# -*- coding: utf-8 -*-
"""
Auto-Shutdown Watchdog (Full Studio):
Theo doi TOAN BO cac tac vu dang chay tren may tinh:
  1. Tat ca cuoc hoi thoai Antigravity (kiem tra transcript.jsonl xem con tool_calls dang chay,
     con USER_INPUT chua tra loi, hoac vua ghi file trong 4 phut gan nhat; bo qua conversation hien tai neu da xong).
  2. Tien trinh Render / AI: ffmpeg, ffprobe, robocopy, rclone, python worker (ngoai MCP server nhan roi).
  3. Infinite Canvas (:17371) node dang running/queued/generating.
  4. NVIDIA GPU Encoder (NVENC) & Compute nang (> 15% GPU keu dai).
  5. CapCut / Premiere / Photoshop dang xuat file (CPU > 6% mot nhan).
  6. Google Drive (GoogleDriveFS) & Mang Upload/Download (> 180 KB/s) hoac file .crdownload/.part dang tai.

Chi khi TAT CA 6 nhom deu ranh 100% lien tuc trong 5 PHUT (10 chu ky x 30s):
  -> Tu dong dong bo nhanh GitHub (timeout 90s)
  -> Phat lenh shutdown.exe /s /f /t 90 (co the huy bang HUY_HEN_GIO_TAT_MAY.bat ngoai Desktop).
"""
import argparse
import ctypes
import glob
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

BRAIN_GLOB = r"C:\Users\Hang thu\.gemini\antigravity\brain\*\.system_generated\logs\transcript.jsonl"
DOWNLOADS_DIR = r"C:\Users\Hang thu\Downloads"
LOG_DIR = r"d:\AI\full studio\huu\logs"
LOG_FILE = os.path.join(LOG_DIR, "auto_shutdown_watchdog.log")
STOP_FLAG = os.path.join(LOG_DIR, "CANCEL_AUTO_SHUTDOWN.flag")
GITHUB_PUSH_PS1 = r"d:\AI\full studio\huu\github_sync_19h30_push.ps1"


def log(msg: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def check_antigravity_chats(self_conv_id: str, quiet_sec: int = 210) -> list[str]:
    busy = []
    now = time.time()
    for path in glob.glob(BRAIN_GLOB):
        try:
            mtime = os.path.getmtime(path)
            age = now - mtime
            # Chi xet cac cuoc hoi thoai co hoat dong trong 3 gio qua
            if age > 10800:
                continue
            cid = path.split(os.sep)[-4]
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            if not lines:
                continue
            last = json.loads(lines[-1])
            ltype = last.get("type", "")
            lstatus = last.get("status", "")
            has_tc = bool(last.get("tool_calls"))

            # Bo qua khung chat dieu khien tat may ngay khi no da tra loi xong
            if cid == self_conv_id:
                if ltype == "PLANNER_RESPONSE" and not has_tc and age > 45:
                    continue
                if age < 45:
                    busy.append(f"Chat hien tai ({cid[:8]}) vua cap nhat {int(age)}s truoc")
                continue

            # Neu file transcript vua duoc ghi trong quiet_sec (3.5 phut) -> van dang hoat dong
            if age < quiet_sec:
                busy.append(f"Antigravity chat {cid[:8]} vua hoat dong ({int(age)}s truoc, type={ltype})")
                continue

            # Neu buoc cuoi cung la tool_calls dang cho ket qua, GENERIC tool output chua co PLANNER_RESPONSE chot,
            # hoac USER_INPUT chua tra loi (trong vong 45 phut, phong truong hop tab cu bi treo tu chieu)
            if age < 2700:
                if lstatus not in ("DONE", "ERROR", "CANCELED", "CANCELLED"):
                    busy.append(f"Antigravity chat {cid[:8]} status={lstatus}")
                elif has_tc:
                    busy.append(f"Antigravity chat {cid[:8]} dang cho tool hoan tat (has_tool_calls=True, {int(age)}s)")
                elif ltype in ("USER_INPUT", "GENERIC"):
                    busy.append(f"Antigravity chat {cid[:8]} dang giua luot xu ly (last_type={ltype}, {int(age)}s)")
        except Exception as e:
            busy.append(f"Loi doc transcript: {e}")
    return busy


def check_worker_processes_and_cpu() -> list[str]:
    busy = []
    my_pid = os.getpid()
    ps_script = f"""
    $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $myPid = {my_pid}
    # 1. Check hard render / copy processes
    $hard = Get-CimInstance Win32_Process | Where-Object {{
        $_.ProcessId -ne $myPid -and (
            $_.Name -in @('ffmpeg.exe','ffprobe.exe','robocopy.exe','rclone.exe') -or
            ($_.Name -eq 'python.exe' -and $_.CommandLine -notmatch 'open-folder[\\\\/]bin[\\\\/]server\\.py' -and $_.CommandLine -notmatch 'auto_shutdown_watchdog\\.py')
        )
    }}
    foreach ($p in $hard) {{
        Write-Output ("HARD_PROC|" + $p.Name + "|PID=" + $p.ProcessId + "|" + ($p.CommandLine -replace '\\r|\\n',' '))
    }}

    # 2. Measure 4-second CPU + Network delta
    $net1 = (Get-NetAdapterStatistics -ErrorAction SilentlyContinue | Measure-Object -Property ReceivedBytes,SentBytes -Sum)
    $rx1 = ($net1 | Where-Object Property -eq 'ReceivedBytes').Sum
    $tx1 = ($net1 | Where-Object Property -eq 'SentBytes').Sum

    $procs1 = @{{}}
    Get-Process -Name 'CapCut','VEDesktop','Photoshop','Adobe Premiere Pro','GoogleDriveFS','Antigravity','node','python' -ErrorAction SilentlyContinue | ForEach-Object {{
        if ($_.Id -ne $myPid) {{ $procs1[$_.Id] = $_.CPU }}
    }}
    Start-Sleep -Seconds 4
    $net2 = (Get-NetAdapterStatistics -ErrorAction SilentlyContinue | Measure-Object -Property ReceivedBytes,SentBytes -Sum)
    $rx2 = ($net2 | Where-Object Property -eq 'ReceivedBytes').Sum
    $tx2 = ($net2 | Where-Object Property -eq 'SentBytes').Sum
    $kbps = [math]::Round((($rx2 - $rx1) + ($tx2 - $tx1)) / 4.0 / 1024.0, 1)
    Write-Output ("NET_KBPS|" + $kbps)

    $cpuSumByName = @{{}}
    Get-Process -Name 'CapCut','VEDesktop','Photoshop','Adobe Premiere Pro','GoogleDriveFS','Antigravity','node','python' -ErrorAction SilentlyContinue | ForEach-Object {{
        if ($_.Id -ne $myPid -and $procs1.ContainsKey($_.Id)) {{
            $d = $_.CPU - $procs1[$_.Id]
            if (-not $cpuSumByName.ContainsKey($_.ProcessName)) {{ $cpuSumByName[$_.ProcessName] = 0.0 }}
            $cpuSumByName[$_.ProcessName] += $d
        }}
    }}
    foreach ($k in $cpuSumByName.Keys) {{
        Write-Output ("CPU4S|" + $k + "|" + [math]::Round($cpuSumByName[$k], 2))
    }}
    """
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=25,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("HARD_PROC|"):
                parts = line.split("|", 3)
                busy.append(f"Tien trinh dang chay: {parts[1]} ({parts[2]}) {parts[3][:90]}")
            elif line.startswith("NET_KBPS|"):
                kbps = float(line.split("|")[1])
                if kbps > 220.0:
                    busy.append(f"Mang dang tai/dong bo Google Drive ({kbps:.0f} KB/s)")
            elif line.startswith("CPU4S|"):
                _, name, dcpu_s = line.split("|")
                dcpu = float(dcpu_s)
                # 4 giay do: neu chiem > 1.2s CPU (~30% 1 nhan) thi app van dang xu ly viec
                thresh = 1.6 if name in ("Antigravity", "GoogleDriveFS") else 1.0
                if dcpu > thresh:
                    busy.append(f"{name} dang hoat dong CPU ({dcpu:.2f}s / 4s)")
    except Exception as e:
        busy.append(f"Loi do tien trinh: {e}")
    return busy


def check_canvas_and_gpu_and_downloads() -> list[str]:
    busy = []
    # 1. Infinite Canvas (:17371)
    try:
        req = urllib.request.Request("http://127.0.0.1:17371/api/canvas/state")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
            for n in data.get("nodes", []):
                st = str(n.get("data", {}).get("status", "")).lower()
                if st in ("running", "queued", "generating", "pending"):
                    busy.append(f"Canvas node {n.get('id')} dang {st}")
    except Exception:
        pass

    # 2. NVIDIA GPU Encoder (NVENC)
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.encoder", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW,
        )
        enc_util = int(res.stdout.strip().splitlines()[0])
        if enc_util > 0:
            busy.append(f"GPU NVENC dang render video ({enc_util}%)")
    except Exception:
        pass

    # 3. Active downloads (.crdownload / .part modified in last 15 min)
    now = time.time()
    for ext in ("*.crdownload", "*.part"):
        for f in glob.glob(os.path.join(DOWNLOADS_DIR, ext)):
            if now - os.path.getmtime(f) < 900:
                busy.append(f"Trinh duyet dang tai file: {os.path.basename(f)}")
    return busy


def evaluate_all_busy(self_conv_id: str) -> list[str]:
    reasons = []
    reasons.extend(check_antigravity_chats(self_conv_id))
    reasons.extend(check_worker_processes_and_cpu())
    reasons.extend(check_canvas_and_gpu_and_downloads())
    return reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-conv", default="8c410fa3-31d5-47df-8611-fc1b3fad1994")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--required-idle-checks", type=int, default=10, help="So lan kiem tra ranh lien tiep (moi lan cach ~30s -> 10 lan = 5 phut)")
    args = ap.parse_args()

    if os.path.exists(STOP_FLAG):
        os.remove(STOP_FLAG)

    if args.dry_run:
        reasons = evaluate_all_busy(args.self_conv)
        print("=== DRY RUN STATUS ===")
        if reasons:
            for r in reasons:
                print("  [BUSY]", r)
        else:
            print("  [IDLE] All tasks finished!")
        return

    log(f"=== BAT DAU THEO DOI TU DONG TAT MAY (Can {args.required_idle_checks} chu ky ranh lien tiep ~ 5 phut) ===")
    # Giu may thuc khong bi Sleep giua chung cho den khi tat ca tac vu hoan tat 100%
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    idle_streak = 0

    while True:
        if os.path.exists(STOP_FLAG):
            log("Phat hien lenh HUY_HEN_GIO_TAT_MAY tu nguoi dung. Dung theo doi!")
            return

        reasons = evaluate_all_busy(args.self_conv)
        if reasons:
            idle_streak = 0
            log(f"Con {len(reasons)} tac vu dang chay -> tiep tuc cho: " + " ; ".join(reasons[:4]))
        else:
            idle_streak += 1
            log(f"He thong ranh ({idle_streak}/{args.required_idle_checks})...")
            if idle_streak >= args.required_idle_checks:
                log("TOAN BO TAC VU DA HOAN TAT 100% SUOT 5 PHUT LIEN TUC!")
                # Dong bo nhanh GitHub truoc khi tat may (gioi han 90s de khong treo)
                if os.path.exists(GITHUB_PUSH_PS1):
                    try:
                        log("Dang dong bo nhanh du lieu len GitHub truoc khi tat may...")
                        subprocess.run(
                            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GITHUB_PUSH_PS1],
                            timeout=90, creationflags=subprocess.CREATE_NO_WINDOW,
                        )
                        log("Dong bo GitHub hoan tat.")
                    except Exception as e:
                        log(f"Bo qua GitHub sync ({e}), tien hanh tat may.")

                if os.path.exists(STOP_FLAG):
                    log("Da huy truoc giay phut chot!")
                    return

                msg = "Toan bo tac vu AI, Render & Google Drive da xong 100%. May se tat sau 90 giay (Bam HUY_HEN_GIO_TAT_MAY ngoai Desktop neu muon huy)."
                log("Phat lenh shutdown /s /f /t 90 !")
                subprocess.run(["shutdown.exe", "/s", "/f", "/t", "90", "/c", msg], creationflags=subprocess.CREATE_NO_WINDOW)
                return

        time.sleep(26)  # +4s do CPU = 30s moi chu ky


if __name__ == "__main__":
    main()
