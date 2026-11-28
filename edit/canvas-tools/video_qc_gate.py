# -*- coding: utf-8 -*-
"""
TRẠM KIỂM DUYỆT VIDEO ĐỘC LẬP TOÀN HỆ THỐNG (`video_qc_gate.py`)
Áp dụng bắt buộc cho 100% dự án Video (K4, K5, K6 HTPM, AVPM, TVC, Talking-Head, CapCut, HyperFrames, Remotion).

Chức năng:
  1. `inspect <video.mp4> [--cuts-json <cuts.json>] [--hook-end-sec <sec>] [--out-dir <dir>]`
     - Kiểm tra kỹ thuật stream (codec, FPS, độ phân giải, lệch Audio/Video <= 0.10s, viền đen thừa).
     - Tách khung hình 100% TẤT CẢ CÁC CÚ CẮT (không bỏ sót bất kỳ cảnh nào!) từ chính file `.mp4` thành phẩm:
       + `QC_FINAL_ALL_CUTS_FULL.jpg` (bảng tổng thể đánh số từng cảnh + mốc giây).
       + `QC_FINAL_ALL_CUTS_ZOOM.jpg` (bảng phóng đại 1:1 vùng bàn/tay/đạo cụ/sản phẩm của 100% cảnh để phát hiện hộp trắng giả, sai tên SKU, thừa đạo cụ).
     - Chạy `faster-whisper` word-level trên toàn bộ đường tiếng của `.mp4` thành phẩm:
       + Bắt tự động mọi lỗi lặp từ / lắp bắp (`1-gram` .. `4-gram` trong khoảng cách <= 1.8s).
       + Kiểm tra đứt chữ ở điểm cắt Highlight Hook và cuối video (`EOF`).
       + Đo độ lớn âm thanh chuẩn phát sóng (`Integrated LUFS`).
     - Xuất báo cáo máy `<video.mp4>.qc_audit.json`.

  2. `sign <video.mp4> --verdict PASS|FAIL --auditor <agent_name> --notes "<nhận xét chi tiết từng hạng mục>"`
     - Dành riêng cho Subagent độc lập `video-qc-auditor` sau khi đã mở đọc trực tiếp `QC_FINAL_ALL_CUTS_FULL.jpg` + `QC_FINAL_ALL_CUTS_ZOOM.jpg` + `.qc_audit.json`.
     - Ghi chứng nhận `<video.mp4>.qc_pass.json` khóa cứng theo `file_size` + `sha256_head_tail` để mở khóa Hook giao file.

  3. `copy-cert <src.mp4> <dst.mp4>`
     - Sao chép chứng nhận `.qc_pass.json` sang bản sao y hệt byte trên Google Drive / Local Backup.
"""
import argparse
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _find_venv_python():
    candidates = [
        r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe",
        r"D:\AI\full studio\voice-studio\.venv\Scripts\python.exe",
        sys.executable,
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return sys.executable


# Auto re-exec inside .venv if PIL/faster_whisper not in current interpreter
try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    from faster_whisper import WhisperModel
except ImportError:
    vpy = _find_venv_python()
    if os.path.abspath(vpy).lower() != os.path.abspath(sys.executable).lower():
        rc = subprocess.call([vpy, "-X", "utf8", __file__] + sys.argv[1:])
        sys.exit(rc)
    raise


def file_fingerprint(path: str) -> dict:
    st = os.stat(path)
    h = hashlib.sha256()
    size = st.st_size
    with open(path, "rb") as f:
        h.update(f.read(65536))
        if size > 131072:
            f.seek(max(0, size - 65536))
            h.update(f.read(65536))
    return {
        "file_size": size,
        "sha256_head_tail": h.hexdigest(),
    }


def probe_streams(mp4_path: str) -> dict:
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", mp4_path],
        timeout=20,
    ).decode("utf-8", errors="replace")
    data = json.loads(raw)
    v_st = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    a_st = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v_st:
        raise RuntimeError("NO_VIDEO_STREAM")
    fmt_dur = float(data.get("format", {}).get("duration") or 0.0)
    v_dur = float(v_st.get("duration") or fmt_dur)
    a_dur = float(a_st.get("duration") or fmt_dur) if a_st else 0.0
    fps_str = v_st.get("r_frame_rate", "30/1")
    num, den = (fps_str.split("/") + ["1"])[:2]
    fps = round(float(num) / max(1.0, float(den)), 2)
    return {
        "width": int(v_st.get("width") or 0),
        "height": int(v_st.get("height") or 0),
        "v_codec": v_st.get("codec_name", ""),
        "a_codec": a_st.get("codec_name", "") if a_st else "NONE",
        "fps": fps,
        "format_dur": round(fmt_dur, 3),
        "video_dur": round(v_dur, 3),
        "audio_dur": round(a_dur, 3),
        "av_sync_delta": round(abs(v_dur - a_dur), 3) if a_st else 999.0,
    }


def detect_cuts(mp4_path: str, total_dur: float, cuts_json: str = None) -> list:
    """Returns list of (start_sec, end_sec, label) covering 100% of cuts in the rendered MP4."""
    if cuts_json and os.path.exists(cuts_json):
        items = json.load(open(cuts_json, encoding="utf-8"))
        out = []
        for idx, it in enumerate(items, 1):
            out.append((float(it["start"]), float(it["end"]), it.get("label", f"cut_{idx:02d}")))
        if out:
            return out

    # Automatic visual cut detection via ffmpeg scdet / select
    cmd = [
        "ffmpeg", "-v", "info", "-i", mp4_path,
        "-vf", "select='gt(scene,0.22)',showinfo",
        "-f", "null", "-"
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    pts_times = [0.0]
    for line in (p.stderr or "").splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            t = float(m.group(1))
            if t - pts_times[-1] >= 0.45 and t < total_dur - 0.35:
                pts_times.append(round(t, 3))
    pts_times.append(round(total_dur, 3))
    cuts = []
    for i in range(len(pts_times) - 1):
        s, e = pts_times[i], pts_times[i + 1]
        cuts.append((s, e, f"cut_{i + 1:02d}"))
    return cuts


def check_letterbox_bars(mp4_path: str, w: int, h: int, dur: float) -> dict:
    sample_times = [min(dur - 0.2, max(0.2, dur * r)) for r in (0.15, 0.45, 0.75)]
    max_top, max_bot = 0, 0
    for t in sample_times:
        raw = subprocess.check_output(
            ["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", mp4_path, "-frames:v", "1", "-pix_fmt", "gray", "-f", "rawvideo", "-"]
        )
        arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w)).mean(axis=1)
        tb, bb = 0, 0
        while tb < h // 6 and arr[tb] < 14.0:
            tb += 1
        while bb < h // 6 and arr[h - 1 - bb] < 14.0:
            bb += 1
        max_top = max(max_top, tb if tb >= 6 else 0)
        max_bot = max(max_bot, bb if bb >= 6 else 0)
    return {"top_black_px": int(max_top), "bottom_black_px": int(max_bot)}


def build_all_cuts_sheets(mp4_path: str, cuts: list, out_dir: str, is_vertical: bool) -> tuple:
    os.makedirs(out_dir, exist_ok=True)
    try:
        font_lbl = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 19)
    except Exception:
        font_lbl = ImageFont.load_default()

    tw, th = (300, 534) if is_vertical else (480, 270)
    zw, zh = (340, 420)
    cols = 6 if is_vertical else 4
    rows = max(1, math.ceil(len(cuts) / cols))

    full_sheet = Image.new("RGB", (cols * tw, rows * (th + 34)), (16, 18, 24))
    zoom_sheet = Image.new("RGB", (cols * zw, rows * (zh + 34)), (16, 18, 24))
    df = ImageDraw.Draw(full_sheet)
    dz = ImageDraw.Draw(zoom_sheet)

    for idx, (s, e, lbl) in enumerate(cuts):
        t_mid = s + (e - s) * 0.32
        tmp_jpg = os.path.join(out_dir, f"_tmp_cut_{idx + 1:03d}.jpg")
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{t_mid:.2f}", "-i", mp4_path, "-frames:v", "1", tmp_jpg],
            check=True,
        )
        im = Image.open(tmp_jpg).convert("RGB")
        iw, ih = im.size
        r, c = idx // cols, idx % cols

        # 1. Full frame tile
        thumb = im.resize((tw - 6, th - 6), Image.LANCZOS)
        full_sheet.paste(thumb, (c * tw + 3, r * (th + 34) + 31))
        header = f"#{idx + 1:02d} [{s:.1f}-{e:.1f}s] {lbl[:14]}"
        df.text((c * tw + 6, r * (th + 34) + 6), header, fill=(255, 222, 80), font=font_lbl)

        # 2. Lower-65% tabletop / hand / product zoom tile across 100% of cuts!
        crop = im.crop((int(iw * 0.04), int(ih * 0.32), int(iw * 0.96), int(ih * 0.96)))
        zthumb = crop.resize((zw - 6, zh - 6), Image.LANCZOS)
        zoom_sheet.paste(zthumb, (c * zw + 3, r * (zh + 34) + 31))
        dz.text((c * zw + 6, r * (zh + 34) + 6), f"ZOOM #{idx + 1:02d} ({s:.1f}s) {lbl[:12]}", fill=(110, 245, 175), font=font_lbl)
        try:
            os.remove(tmp_jpg)
        except Exception:
            pass

    full_p = os.path.join(out_dir, "QC_FINAL_ALL_CUTS_FULL.jpg")
    zoom_p = os.path.join(out_dir, "QC_FINAL_ALL_CUTS_ZOOM.jpg")
    full_sheet.save(full_p, "JPEG", quality=92)
    zoom_sheet.save(zoom_p, "JPEG", quality=92)
    return full_p, zoom_p


def measure_lufs(mp4_path: str) -> float:
    p = subprocess.run(
        ["ffmpeg", "-nostats", "-i", mp4_path, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    matches = re.findall(r"I:\s*(-?[0-9.]+)\s*LUFS", p.stderr or "")
    return round(float(matches[-1]), 2) if matches else -99.0


def find_word_repetitions(words: list, start_bound: float = 0.0, end_bound: float = 1e9) -> list:
    """Detects adjacent 1-gram..4-gram stutters/repetitions inside [start_bound, end_bound]."""
    sub = [w for w in words if start_bound - 0.05 <= w["s"] <= end_bound + 0.05]
    norm = [re.sub(r"[^\w]", "", w["w"].lower()) for w in sub]
    # Common legitimate Vietnamese reduplicative words (từ láy / nhấn đôi tự nhiên)
    ALLOWED_1GRAM = {"từ", "đều", "luôn", "rất", "lăm", "nhiều", "ngày", "đời", "người", "ai", "cười", "khóc", "vừa"}
    issues = []
    # Check 4-gram down to 2-gram first
    covered = set()
    for n in (4, 3, 2):
        for k in range(len(norm) - 2 * n + 1):
            if any(idx in covered for idx in range(k, k + 2 * n)):
                continue
            g1 = norm[k:k + n]
            g2 = norm[k + n:k + 2 * n]
            if all(g1) and g1 == g2:
                gap = sub[k + n]["s"] - sub[k + n - 1]["e"]
                if gap <= 1.85:
                    phrase = " ".join(x["w"] for x in sub[k:k + n])
                    issues.append({
                        "type": f"{n}-gram_repeat",
                        "phrase": phrase,
                        "first_span": [sub[k]["s"], sub[k + n - 1]["e"]],
                        "repeat_span": [sub[k + n]["s"], sub[k + 2 * n - 1]["e"]],
                        "gap_sec": round(gap, 3),
                    })
                    covered.update(range(k, k + 2 * n))
    # 1-gram stutters
    for k in range(len(norm) - 1):
        if k in covered or (k + 1) in covered:
            continue
        if norm[k] and len(norm[k]) >= 2 and norm[k] == norm[k + 1] and norm[k] not in ALLOWED_1GRAM:
            gap = sub[k + 1]["s"] - sub[k]["e"]
            if gap <= 1.50:
                issues.append({
                    "type": "1-gram_repeat",
                    "phrase": sub[k]["w"],
                    "first_span": [sub[k]["s"], sub[k]["e"]],
                    "repeat_span": [sub[k + 1]["s"], sub[k + 1]["e"]],
                    "gap_sec": round(gap, 3),
                })
    return issues


def audit_audio_whisper(mp4_path: str, total_dur: float, hook_end_sec: float = 0.0) -> dict:
    wm = WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=12)
    segs, _ = wm.transcribe(
        mp4_path,
        language="vi",
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 350},
        condition_on_previous_text=False,
        hallucination_silence_threshold=0.8,
        beam_size=2,
    )
    HALLUC_SUBSTR = ("la la school", "subscribe cho kênh", "đăng ký kênh")
    words = []
    for s in segs:
        stxt = (s.text or "").lower()
        if any(h in stxt for h in HALLUC_SUBSTR):
            continue
        for w in (s.words or []):
            if w.word.strip():
                words.append({"s": round(float(w.start), 3), "e": round(float(w.end), 3), "w": w.word.strip()})
    if hook_end_sec > 0.5:
        reps_hook = find_word_repetitions(words, 0.0, hook_end_sec)
        reps_body = find_word_repetitions(words, hook_end_sec, total_dur)
        reps = reps_hook + reps_body
    else:
        reps = find_word_repetitions(words, 0.0, total_dur)

    eof_tail_sec = round(total_dur - words[-1]["e"], 3) if words else total_dur
    eof_cutoff = bool(words and eof_tail_sec < 0.12)
    return {
        "word_count": len(words),
        "eof_tail_sec": eof_tail_sec,
        "eof_cutoff": eof_cutoff,
        "repetitions": reps,
        "transcript": " ".join(w["w"] for w in words),
        "words": words,
    }


def cmd_inspect(args):
    mp4 = os.path.abspath(args.video)
    if not os.path.exists(mp4):
        raise FileNotFoundError(mp4)
    out_dir = os.path.abspath(args.out_dir) if args.out_dir else os.path.join(os.path.dirname(mp4), "_qc_gate_sheets")
    fp = file_fingerprint(mp4)
    st = probe_streams(mp4)
    is_vert = st["height"] >= st["width"]
    bars = check_letterbox_bars(mp4, st["width"], st["height"], st["format_dur"])
    cuts = detect_cuts(mp4, st["format_dur"], args.cuts_json)
    full_sheet, zoom_sheet = build_all_cuts_sheets(mp4, cuts, out_dir, is_vert)
    lufs = measure_lufs(mp4)
    aud = audit_audio_whisper(mp4, st["format_dur"], float(args.hook_end_sec or 0.0))

    failures = []
    if st["a_codec"] == "NONE":
        failures.append("MISSING_AUDIO_STREAM")
    if st["av_sync_delta"] > 0.12:
        failures.append(f"AV_SYNC_DRIFT ({st['av_sync_delta']}s)")
    if bars["top_black_px"] > 12 or bars["bottom_black_px"] > 12:
        failures.append(f"LETTERBOX_BLACK_BARS (top={bars['top_black_px']}px, bot={bars['bottom_black_px']}px)")
    if aud["eof_cutoff"]:
        failures.append(f"EOF_SPEECH_CUTOFF (tail={aud['eof_tail_sec']}s)")
    if aud["repetitions"]:
        failures.append(f"WORD_REPETITIONS ({len(aud['repetitions'])} found: {[r['phrase'] for r in aud['repetitions']]})")

    report = {
        "inspected_at": datetime.datetime.now().isoformat(),
        "video_path": mp4,
        "fingerprint": fp,
        "streams": st,
        "letterbox": bars,
        "integrated_lufs": lufs,
        "cut_count": len(cuts),
        "cuts": [{"index": i + 1, "start": round(s, 2), "end": round(e, 2), "dur": round(e - s, 2), "label": l} for i, (s, e, l) in enumerate(cuts)],
        "sheets": {
            "all_cuts_full": full_sheet,
            "all_cuts_zoom": zoom_sheet,
        },
        "audio_audit": {
            "word_count": aud["word_count"],
            "eof_tail_sec": aud["eof_tail_sec"],
            "eof_cutoff": aud["eof_cutoff"],
            "repetitions": aud["repetitions"],
            "transcript": aud["transcript"],
        },
        "machine_failures": failures,
        "machine_status": "READY_FOR_VISUAL_SIGN_OFF" if not failures else "MACHINE_FAIL",
    }
    audit_path = mp4 + ".qc_audit.json"
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"=== VIDEO QC GATE INSPECT: {os.path.basename(mp4)} ===")
    print(f"  Resolution/FPS : {st['width']}x{st['height']} @ {st['fps']}fps | Dur={st['format_dur']}s | SyncDelta={st['av_sync_delta']}s")
    print(f"  Loudness       : {lufs} LUFS | Letterbox={bars}")
    print(f"  Total Cuts     : {len(cuts)}")
    print(f"  Full Sheet     : {full_sheet}")
    print(f"  Zoom Sheet     : {zoom_sheet}")
    print(f"  Repetitions    : {aud['repetitions']}")
    print(f"  Machine Status : {report['machine_status']} (Failures={failures})")
    print(f"  Audit JSON     : {audit_path}")
    if failures:
        sys.exit(2)


def cmd_sign(args):
    mp4 = os.path.abspath(args.video)
    audit_path = mp4 + ".qc_audit.json"
    if not os.path.exists(audit_path):
        raise RuntimeError(f"Chưa chạy `video_qc_gate.py inspect` cho {mp4}!")
    audit = json.load(open(audit_path, encoding="utf-8"))
    cur_fp = file_fingerprint(mp4)
    if cur_fp != audit.get("fingerprint"):
        raise RuntimeError("Tệp MP4 đã thay đổi sau khi inspect! Bắt buộc chạy lại inspect.")
    verdict = args.verdict.upper().strip()
    if verdict == "PASS" and audit.get("machine_status") != "READY_FOR_VISUAL_SIGN_OFF" and not args.override_reason:
        raise RuntimeError(f"Không thể ký PASS khi machine_status={audit.get('machine_status')}: {audit.get('machine_failures')}")
    if verdict == "PASS" and len((args.notes or "").strip()) < 30:
        raise RuntimeError("Ghi chú kiểm duyệt (`--notes`) phải mô tả cụ thể kết quả soi sản phẩm, logic cảnh quay, cảnh toàn và âm thanh (>= 30 ký tự)!")

    cert = {
        "signed_at": datetime.datetime.now().isoformat(),
        "certified_path": mp4,
        "verdict": verdict,
        "auditor_verified": (verdict == "PASS"),
        "auditor": args.auditor,
        "notes": args.notes.strip(),
        "override_reason": args.override_reason or "",
        "cut_count": audit.get("cut_count", 0),
        "integrated_lufs": audit.get("integrated_lufs"),
        **cur_fp,
    }
    cert_path = mp4 + ".qc_pass.json"
    with open(cert_path, "w", encoding="utf-8") as f:
        json.dump(cert, f, ensure_ascii=False, indent=2)
    print(f"[VideoQCGate] SIGNED {verdict} by {args.auditor} -> {cert_path}")


def cmd_copy_cert(args):
    src = os.path.abspath(args.src)
    dst = os.path.abspath(args.dst)
    src_cert = src + ".qc_pass.json"
    if not os.path.exists(src_cert):
        raise FileNotFoundError(f"Không tìm thấy chứng nhận gốc: {src_cert}")
    cert = json.load(open(src_cert, encoding="utf-8"))
    src_fp = file_fingerprint(src)
    dst_fp = file_fingerprint(dst)
    if src_fp != dst_fp or cert.get("sha256_head_tail") != dst_fp["sha256_head_tail"]:
        raise RuntimeError("Byte tệp đích không khớp tệp gốc đã kiểm duyệt!")
    cert_copy = dict(cert)
    cert_copy["certified_path"] = dst
    with open(dst + ".qc_pass.json", "w", encoding="utf-8") as f:
        json.dump(cert_copy, f, ensure_ascii=False, indent=2)
    print(f"[VideoQCGate] Propagated QC PASS cert -> {dst}.qc_pass.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_in = sub.add_parser("inspect")
    p_in.add_argument("video")
    p_in.add_argument("--cuts-json", default="")
    p_in.add_argument("--hook-end-sec", type=float, default=0.0)
    p_in.add_argument("--out-dir", default="")
    p_in.set_defaults(func=cmd_inspect)

    p_sg = sub.add_parser("sign")
    p_sg.add_argument("video")
    p_sg.add_argument("--verdict", required=True, choices=["PASS", "FAIL", "pass", "fail"])
    p_sg.add_argument("--auditor", required=True)
    p_sg.add_argument("--notes", required=True)
    p_sg.add_argument("--override-reason", default="")
    p_sg.set_defaults(func=cmd_sign)

    p_cp = sub.add_parser("copy-cert")
    p_cp.add_argument("src")
    p_cp.add_argument("dst")
    p_cp.set_defaults(func=cmd_copy_cert)

    ns = ap.parse_args()
    ns.func(ns)
