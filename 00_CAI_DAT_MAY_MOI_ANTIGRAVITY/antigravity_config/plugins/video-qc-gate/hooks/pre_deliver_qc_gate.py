# -*- coding: utf-8 -*-
"""
PreToolUse Lifecycle Hook cho `call_mcp_tool` (`show_file_location_card`):
Tự động chặn mọi thao tác bàn giao video (`.mp4`, `.mov`, `.webm`) nếu tệp đó chưa có
chứng nhận `.qc_pass.json` hợp lệ (khớp đúng `file_size` + `sha256_head_tail` và `verdict == "PASS"`)
do Agent kiểm duyệt độc lập `video-qc-auditor` ký xác nhận.
"""
import hashlib
import json
import os
import sys


def fingerprint(path: str) -> dict:
    st = os.stat(path)
    h = hashlib.sha256()
    size = st.st_size
    with open(path, "rb") as f:
        h.update(f.read(65536))
        if size > 131072:
            f.seek(max(0, size - 65536))
            h.update(f.read(65536))
    return {"file_size": size, "sha256_head_tail": h.hexdigest()}


def _emit(obj: dict):
    sys.stdout.buffer.write((json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def main():
    try:
        raw_bytes = sys.stdin.buffer.read()
        payload = json.loads(raw_bytes.decode("utf-8", errors="replace") or "{}")
    except Exception:
        _emit({"decision": "allow"})
        return

    tc = payload.get("toolCall") or {}
    if tc.get("name") != "call_mcp_tool":
        _emit({"decision": "allow"})
        return

    args = tc.get("args") or {}
    if args.get("ToolName") != "show_file_location_card":
        _emit({"decision": "allow"})
        return

    mcp_args = args.get("Arguments") or {}
    file_path = (mcp_args.get("file_path") or "").strip()
    if not file_path or not file_path.lower().endswith((".mp4", ".mov", ".webm")):
        _emit({"decision": "allow"})
        return

    if not os.path.exists(file_path):
        _emit({
            "decision": "deny",
            "reason": f"⛔ VIDEO QC GATE: Tệp video đích không tồn tại tại '{file_path}'."
        })
        return

    cert_path = file_path + ".qc_pass.json"
    if not os.path.exists(cert_path):
        _emit({
            "decision": "deny",
            "reason": (
                f"⛔ BỊ CHẶN BỞI TRẠM KIỂM DUYỆT VIDEO (video-qc-gate): Tệp '{os.path.basename(file_path)}' "
                "chưa có chứng nhận kiểm duyệt (.qc_pass.json)! Bắt buộc chạy `video_qc_gate.py inspect` "
                "và gọi subagent độc lập `video-qc-auditor` đọc bảng 100% cuts + bảng zoom đạo cụ + transcript Whisper "
                "rồi ký `sign --verdict PASS` trước khi giao khách!"
            )
        })
        return

    try:
        cert = json.load(open(cert_path, encoding="utf-8"))
        cur_fp = fingerprint(file_path)
    except Exception as exc:
        _emit({
            "decision": "deny",
            "reason": f"⛔ VIDEO QC GATE: Lỗi đọc chứng nhận .qc_pass.json ({exc})."
        })
        return

    if cert.get("verdict") != "PASS" or not cert.get("auditor_verified"):
        _emit({
            "decision": "deny",
            "reason": f"⛔ VIDEO QC GATE: Chứng nhận hiện tại có verdict={cert.get('verdict')} (chưa PASS)!"
        })
        return

    if cert.get("file_size") != cur_fp["file_size"] or cert.get("sha256_head_tail") != cur_fp["sha256_head_tail"]:
        _emit({
            "decision": "deny",
            "reason": "⛔ VIDEO QC GATE: Tệp MP4 đã bị ghi đè/thay đổi sau lần kiểm duyệt trước! Bắt buộc kiểm duyệt lại."
        })
        return

    _emit({"decision": "allow"})


if __name__ == "__main__":
    main()
