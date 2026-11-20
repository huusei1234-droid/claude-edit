import ctypes
import json
import os
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 17379
ALLOWED_PREFIXES = ("C:\\", "D:\\", "E:\\", "F:\\", "Z:\\")


def reveal_in_explorer(raw_path: str) -> tuple[bool, str]:
    if not raw_path:
        return False, "Missing path"
    p = os.path.normpath(raw_path.strip().strip('"'))
    if not any(p.upper().startswith(pref) for pref in ALLOWED_PREFIXES):
        return False, f"Disallowed drive: {p}"
    if not os.path.exists(p):
        parent = os.path.dirname(p)
        if parent and os.path.isdir(parent):
            p = parent
        else:
            return False, f"Path not found: {p}"

    def _open_bg():
        time.sleep(0.12)
        try:
            user32 = ctypes.windll.user32
            # Allow Explorer to take foreground cleanly on Windows 11
            user32.keybd_event(0, 0, 0, 0)
        except Exception:
            pass
        if os.path.isfile(p):
            subprocess.Popen(["explorer.exe", f"/select,{p}"])
            folder_name = os.path.basename(os.path.dirname(p))
        else:
            subprocess.Popen(["explorer.exe", p])
            folder_name = os.path.basename(p) or p

        # Bring matching Explorer window to front after it spawns
        for _ in range(12):
            time.sleep(0.12)
            try:
                user32 = ctypes.windll.user32
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
                found = []

                def enum_cb(hwnd, _):
                    if user32.IsWindowVisible(hwnd):
                        cls_buf = ctypes.create_unicode_buffer(64)
                        user32.GetClassNameW(hwnd, cls_buf, 64)
                        if cls_buf.value in ("CabinetWClass", "ExploreWClass"):
                            ln = user32.GetWindowTextLengthW(hwnd)
                            tbuf = ctypes.create_unicode_buffer(ln + 2)
                            user32.GetWindowTextW(hwnd, tbuf, ln + 2)
                            if not folder_name or folder_name.lower() in tbuf.value.lower():
                                found.append(hwnd)
                    return True

                user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
                if found:
                    hwnd = found[0]
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    user32.keybd_event(0, 0, 0, 0)
                    user32.SetForegroundWindow(hwnd)
                    break
            except Exception:
                pass

    threading.Thread(target=_open_bg, daemon=True).start()
    return True, p


class RevealHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/health":
            body = json.dumps({"ok": True, "service": "full-studio-reveal", "port": PORT}).encode("utf-8")
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/reveal":
            target = (qs.get("path") or qs.get("file") or [""])[0]
            mode = (qs.get("mode") or ["html"])[0]
            ok, msg = reveal_in_explorer(target)

            if mode == "json":
                body = json.dumps({"ok": ok, "target": msg}, ensure_ascii=False).encode("utf-8")
                self.send_response(200 if ok else 400)
                self._send_cors()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            # Auto-close tab immediately when clicked as a Markdown link!
            html = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>Đang mở thư mục...</title>
<style>body{{font-family:system-ui,sans-serif;background:#f4f6fc;color:#141418;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}}
.box{{background:#fff;padding:24px 32px;border-radius:18px;box-shadow:0 12px 32px rgba(20,28,70,.12);text-align:center}}</style>
</head><body><div class="box"><h3>📂 Đã mở vị trí tệp trong Windows Explorer</h3><p>{msg}</p></div>
<script>window.close();setTimeout(function(){{window.close();}},120);</script></body></html>""".encode("utf-8")
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        self.send_response(404)
        self._send_cors()
        self.end_headers()


def main():
    srv = ThreadingHTTPServer((HOST, PORT), RevealHandler)
    srv.serve_forever()


if __name__ == "__main__":
    main()
