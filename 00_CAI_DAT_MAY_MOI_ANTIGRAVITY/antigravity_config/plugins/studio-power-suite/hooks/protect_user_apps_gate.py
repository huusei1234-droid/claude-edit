# -*- coding: utf-8 -*-
"""
PreToolUse Hook bảo vệ tuyệt đối các phần mềm sáng tạo đang mở của người dùng:
Tự động chặn mọi lệnh `taskkill` hoặc `Stop-Process` nhắm vào CapCut, Premiere Pro, Photoshop, After Effects hoặc Brave.
"""
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROTECTED_PATTERNS = [
    r"\bcapcut(\.exe)?\b",
    r"\bvedesktop(\.exe)?\b",
    r"\bphotoshop(\.exe)?\b",
    r"adobe\s+premiere",
    r"\bafterfx(\.exe)?\b",
    r"\bbrave(\.exe)?\b",
]
KILL_VERBS = re.compile(r"\b(taskkill|stop-process|tskill|wmic\s+process.*delete)\b", re.IGNORECASE)


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tc = payload.get("toolCall") or {}
    args = tc.get("args") or {}
    cmd_line = str(args.get("CommandLine") or "")

    if KILL_VERBS.search(cmd_line):
        for pat in PROTECTED_PATTERNS:
            if re.search(pat, cmd_line, re.IGNORECASE):
                print(
                    json.dumps(
                        {
                            "decision": "block",
                            "reason": (
                                f"[Safety Guard] Đã chặn lệnh tắt tiến trình bảo vệ ({pat}). "
                                "Quy tắc bắt buộc: Không được tự ý đóng CapCut, Premiere, Photoshop, After Effects hoặc Brave của người dùng khi chưa được cho phép rõ ràng."
                            ),
                        },
                        ensure_ascii=False,
                    )
                )
                return

    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
