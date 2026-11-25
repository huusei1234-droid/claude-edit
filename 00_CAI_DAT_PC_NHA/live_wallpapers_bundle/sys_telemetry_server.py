"""
Hữu Seiz Studio — Windows Telemetry, Weather, Media & Quick Launch Daemon for Lively Wallpaper.
- Listens on http://127.0.0.1:18625/stats.json (CORS enabled, <0.1% CPU)
- Clickable actions:
  /open?target=taskmgr|resmon|capcut|photoshop|htpm|finals|disk_d|disk_z|network
  /action?cmd=media_prev|media_play|media_next|trim_ram
- Also writes live_stats.js directly into Lively wallpaper folder for zero-CORS fallback.
"""
import ctypes
import json
import os
import subprocess
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import psutil

HOST = "127.0.0.1"
PORT = 18625
POLL_INTERVAL = 2.0

LIVELY_JS_PATHS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Lively Wallpaper\Library\wallpapers\Fresh_Muses_4K_Live\live_stats.js"),
    os.path.expandvars(r"%LOCALAPPDATA%\Lively Wallpaper\Library\wallpapers\fresh_muses_4k.agy\live_stats.js"),
    r"d:\AI\full studio\live-wallpapers\Fresh_Muses_4K_Live\live_stats.js",
]

GIF_1X1 = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
    b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)

CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

_lock = threading.Lock()
_stats = {
    "cpu": 0.0,
    "ram_pct": 0.0,
    "ram_used_gb": 0.0,
    "ram_total_gb": 64,
    "gpu": 0,
    "gpu_temp": 0,
    "gpu_power": 0,
    "vram_used_gb": 0.0,
    "vram_total_gb": 12.0,
    "vram_pct": 0.0,
    "net_down_mbps": 0.0,
    "net_up_mbps": 0.0,
    "disk_d_pct": 0.0,
    "disk_d_free_gb": 0,
    "disk_c_free_gb": 0,
    "disk_z_free_gb": 0,
    "procs": 0,
    "top_ram": [],
    "weather": {"temp": None, "icon": "☀️", "desc": "", "city": "", "humidity": None},
    "media": {"title": "", "source": ""},
    "ts": 0,
}


def _read_gpu():
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total,power.draw",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.DEVNULL,
            timeout=2.5,
            creationflags=CREATE_NO_WINDOW,
        ).decode("utf-8", errors="ignore").strip()
        if out:
            first_line = out.splitlines()[0]
            parts = [p.strip() for p in first_line.split(",")]
            if len(parts) >= 4:
                util = int(float(parts[0]))
                temp = int(float(parts[1]))
                mem_used_mb = float(parts[2])
                mem_total_mb = max(float(parts[3]), 1.0)
                power = int(float(parts[4])) if len(parts) >= 5 and parts[4] not in ("", "[N/A]", "N/A") else 0
                return (
                    util,
                    temp,
                    round(mem_used_mb / 1024.0, 1),
                    round(mem_total_mb / 1024.0, 1),
                    round((mem_used_mb / mem_total_mb) * 100.0, 1),
                    power,
                )
    except Exception:
        pass
    return 0, 0, 0.0, 12.0, 0.0, 0


def _read_top_ram(limit=5):
    groups = {}
    try:
        for p in psutil.process_iter(["name", "memory_info"]):
            try:
                name = p.info.get("name") or ""
                mi = p.info.get("memory_info")
                if not name or not mi:
                    continue
                clean = name[:-4] if name.lower().endswith(".exe") else name
                groups[clean] = groups.get(clean, 0) + mi.rss
            except Exception:
                continue
        ranked = sorted(groups.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{"name": k, "gb": round(v / (1024 ** 3), 2)} for k, v in ranked]
    except Exception:
        return []


def _weather_icon(code: int) -> str:
    if code in (113,):
        return "☀️"
    if code in (116,):
        return "⛅"
    if code in (119, 122):
        return "☁️"
    if code in (143, 248, 260):
        return "🌫️"
    if code in (200, 386, 389, 392, 395):
        return "⛈️"
    if code >= 176:
        return "🌧️"
    return "🌤️"


def _fetch_weather():
    try:
        req = urllib.request.Request(
            "https://wttr.in/?format=j1",
            headers={"User-Agent": "curl/8.0"},
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        cur = (data.get("current_condition") or [{}])[0]
        area = (data.get("nearest_area") or [{}])[0]
        temp = int(float(cur.get("temp_C", 0)))
        hum = int(float(cur.get("humidity", 0)))
        code = int(cur.get("weatherCode", 116))
        desc = ((cur.get("weatherDesc") or [{}])[0]).get("value", "")
        city = ((area.get("areaName") or [{}])[0]).get("value", "")
        return {
            "temp": temp,
            "icon": _weather_icon(code),
            "desc": desc,
            "city": city,
            "humidity": hum,
        }
    except Exception:
        return None


def _detect_media_window():
    """Fast <1ms detection of Spotify / YouTube / Music window titles."""
    found = {"title": "", "source": ""}
    try:
        user32 = ctypes.windll.user32
        titles = []

        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def enum_cb(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if 2 < length < 220:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    titles.append(buf.value)
            return True

        user32.EnumWindows(enum_cb, 0)
        for t in titles:
            tl = t.lower()
            if " - youtube" in tl:
                clean = t.split(" - YouTube")[0].strip()
                if clean and clean.lower() != "youtube":
                    return {"title": clean[:48], "source": "YouTube"}
            if "youtube music" in tl and " - " in t:
                clean = t.split(" - YouTube Music")[0].strip()
                return {"title": clean[:48], "source": "YT Music"}
            if "spotify" in tl and " - " in t and not tl.startswith("spotify"):
                return {"title": t.replace(" - Spotify", "").strip()[:48], "source": "Spotify"}
            if "zing mp3" in tl or "nhaccuatui" in tl:
                return {"title": t.split(" - ")[0].strip()[:48], "source": "Music"}
    except Exception:
        pass
    return found


def _send_media_key(vk_code: int):
    try:
        user32 = ctypes.windll.user32
        user32.keybd_event(vk_code, 0, 0, 0)
        user32.keybd_event(vk_code, 0, 2, 0)
    except Exception:
        pass


def _trim_ram():
    try:
        psapi = ctypes.windll.psapi
        kernel32 = ctypes.windll.kernel32
        PROCESS_SET_QUOTA = 0x0100
        PROCESS_QUERY_INFORMATION = 0x0400
        for p in psutil.process_iter(["pid"]):
            pid = p.info.get("pid")
            if not pid or pid < 100:
                continue
            h = kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid)
            if h:
                try:
                    psapi.EmptyWorkingSet(h)
                finally:
                    kernel32.CloseHandle(h)
    except Exception:
        pass


def _write_fallback_js(payload_json: str):
    js_body = f"window.__AGY_STATS = {payload_json};\n"
    for path in LIVELY_JS_PATHS:
        try:
            parent = os.path.dirname(path)
            if not os.path.isdir(parent):
                continue
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(js_body)
            os.replace(tmp, path)
        except Exception:
            pass


def _launch_target(target: str):
    try:
        if target == "taskmgr":
            subprocess.Popen(["taskmgr.exe"], shell=False)
        elif target == "resmon":
            subprocess.Popen(["perfmon.exe", "/res"], shell=False)
        elif target == "capcut":
            for p in (
                os.path.expandvars(r"%LOCALAPPDATA%\CapCut\Apps\CapCut.exe"),
                r"C:\Program Files\CapCut\CapCut.exe",
                r"C:\Users\Hang thu\AppData\Local\CapCut\Apps\CapCut.exe",
            ):
                if os.path.exists(p):
                    subprocess.Popen([p], shell=False)
                    break
        elif target == "photoshop":
            for p in (
                r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe",
                r"C:\Program Files\Adobe\Adobe Photoshop 2025\Photoshop.exe",
            ):
                if os.path.exists(p):
                    subprocess.Popen([p], shell=False)
                    break
        elif target == "htpm":
            for p in (
                r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma",
                r"G:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma",
                r"G:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma",
                r"D:\XUẤT CAPCUT\hằng thu pharma",
            ):
                if os.path.exists(p):
                    os.startfile(p)
                    break
        elif target == "finals":
            for p in (
                r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final",
                r"G:\Drive của tôi\AI_Full_Studio\04_Videos_Final",
                r"G:\My Drive\AI_Full_Studio\04_Videos_Final",
                r"D:\XUẤT CAPCUT",
            ):
                if os.path.exists(p):
                    os.startfile(p)
                    break
        elif target == "disk_d":
            os.startfile("D:\\")
        elif target == "disk_c":
            os.startfile("C:\\")
        elif target == "disk_z":
            for p in (
                r"Z:\Drive của tôi\AI_Full_Studio",
                r"G:\Drive của tôi\AI_Full_Studio",
                r"G:\My Drive\AI_Full_Studio",
                "Z:\\",
                "G:\\",
            ):
                if os.path.exists(p):
                    os.startfile(p)
                    break
        elif target == "network":
            os.startfile("ms-settings:network")
    except Exception:
        pass


def _run_action(cmd: str):
    if cmd == "media_prev":
        _send_media_key(0xB1)
    elif cmd == "media_play":
        _send_media_key(0xB3)
    elif cmd == "media_next":
        _send_media_key(0xB0)
    elif cmd == "trim_ram":
        _trim_ram()


def _weather_loop():
    while True:
        w = _fetch_weather()
        if w:
            with _lock:
                _stats["weather"] = w
            time.sleep(900)  # 15 mins
        else:
            time.sleep(45)


def _poll_loop():
    psutil.cpu_percent(interval=None)
    prev_net = psutil.net_io_counters()
    prev_t = time.monotonic()
    tick_i = 0
    disk_d_pct = 0.0
    disk_d_free = 0
    disk_c_free = 0
    disk_z_free = 0
    top_ram = []
    media = {"title": "", "source": ""}

    while True:
        try:
            cpu = round(psutil.cpu_percent(interval=None), 1)
            mem = psutil.virtual_memory()
            ram_pct = round(mem.percent, 1)
            ram_used_gb = round(mem.used / (1024 ** 3), 1)
            ram_total_gb = int(round(mem.total / (1024 ** 3), 0))

            now_t = time.monotonic()
            dt = max(now_t - prev_t, 0.25)
            cur_net = psutil.net_io_counters()
            down_mbps = round(((cur_net.bytes_recv - prev_net.bytes_recv) * 8.0) / (dt * 1_000_000.0), 2)
            up_mbps = round(((cur_net.bytes_sent - prev_net.bytes_sent) * 8.0) / (dt * 1_000_000.0), 2)
            prev_net = cur_net
            prev_t = now_t

            gpu, gpu_temp, vram_used, vram_total, vram_pct, gpu_power = _read_gpu()

            if tick_i % 15 == 0:
                try:
                    dd = psutil.disk_usage("D:\\")
                    disk_d_pct = round(dd.percent, 1)
                    disk_d_free = int(dd.free / (1024 ** 3))
                except Exception:
                    pass
                try:
                    dc = psutil.disk_usage("C:\\")
                    disk_c_free = int(dc.free / (1024 ** 3))
                except Exception:
                    pass
                for drv in ("Z:\\", "G:\\", "H:\\"):
                    if os.path.exists(drv):
                        try:
                            dz = psutil.disk_usage(drv)
                            disk_z_free = int(dz.free / (1024 ** 3))
                            break
                        except Exception:
                            pass

            if tick_i % 2 == 0:
                media = _detect_media_window()

            if tick_i % 3 == 0:
                top_ram = _read_top_ram(5)
                procs = len(psutil.pids())
            else:
                procs = _stats["procs"]

            tick_i += 1

            with _lock:
                _stats.update({
                    "cpu": cpu,
                    "ram_pct": ram_pct,
                    "ram_used_gb": ram_used_gb,
                    "ram_total_gb": ram_total_gb,
                    "gpu": gpu,
                    "gpu_temp": gpu_temp,
                    "gpu_power": gpu_power,
                    "vram_used_gb": vram_used,
                    "vram_total_gb": vram_total,
                    "vram_pct": vram_pct,
                    "net_down_mbps": max(0.0, down_mbps),
                    "net_up_mbps": max(0.0, up_mbps),
                    "disk_d_pct": disk_d_pct,
                    "disk_d_free_gb": disk_d_free,
                    "disk_c_free_gb": disk_c_free,
                    "disk_z_free_gb": disk_z_free,
                    "procs": procs,
                    "top_ram": top_ram,
                    "media": media,
                    "ts": int(time.time()),
                })
                snap = json.dumps(_stats, ensure_ascii=False)

            _write_fallback_js(snap)
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send_gif(self):
        self.send_response(200)
        self.send_header("Content-Type", "image/gif")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(GIF_1X1)))
        self.end_headers()
        self.wfile.write(GIF_1X1)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/stats"):
            with _lock:
                body = json.dumps(_stats, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/open":
            qs = parse_qs(parsed.query)
            target = (qs.get("target") or ["taskmgr"])[0]
            threading.Thread(target=_launch_target, args=(target,), daemon=True).start()
            self._send_gif()
        elif parsed.path == "/action":
            qs = parse_qs(parsed.query)
            cmd = (qs.get("cmd") or [""])[0]
            threading.Thread(target=_run_action, args=(cmd,), daemon=True).start()
            self._send_gif()
        else:
            self.send_response(404)
            self.end_headers()


def main():
    threading.Thread(target=_poll_loop, daemon=True).start()
    threading.Thread(target=_weather_loop, daemon=True).start()
    time.sleep(0.4)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
