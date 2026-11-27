"""
Thư viện & CLI Python điều khiển trọn bộ Hệ sinh thái ChatGPT Plus qua Infinite Canvas / Full Studio (:18620):
- Suy luận sâu (Thinking), Viết kịch bản & Prompt Flow Dự án K4, Viết bài & Phân tích sản phẩm Dự án HTPM/An Vượng
- Nghiên cứu chuyên sâu đa nguồn (Deep Research)
- Tạo ảnh thương mại song song 3 luồng (kèm khóa mặt mẫu / hộp sản phẩm thật)
- Tạo video điện ảnh / B-Roll qua OpenAI Sora (sora.chatgpt.com)
- Tự động đồng bộ tài liệu mới (.md, nhật ký Zalo An Vượng, bảng SKU) thẳng vào mục Sources của từng Dự án ChatGPT Plus
- Đặt lịch chạy tự động (Scheduled Tasks), gọi OpenAI Codex và mở nhanh mọi mảnh ghép (Library, Connectors, GPTs)
"""
import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

GATEWAY_URL = os.environ.get("CHATGPT_PLUS_GATEWAY", "http://127.0.0.1:18620")

STUDIO_LAUNCH_CANDIDATES = [
    r"C:\AI\full studio\full studido.exe",
    r"d:\AI\full studio\full studido.exe",
]


def _http_json(method: str, path: str, payload: Optional[dict] = None, timeout: int = 600) -> dict:
    url = f"{GATEWAY_URL.rstrip('/')}/{path.lstrip('/')}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ensure_gateway_ready(auto_start: bool = True, wait_seconds: int = 35) -> dict:
    """Kiểm tra cổng :18620; nếu Full Studio chưa bật thì chủ động bật lên ngay."""
    try:
        return _http_json("GET", "/health", timeout=3)
    except Exception:
        if not auto_start:
            raise

    launched = False
    for exe in STUDIO_LAUNCH_CANDIDATES:
        if os.path.exists(exe):
            subprocess.Popen([exe], cwd=os.path.dirname(exe))
            launched = True
            break

    if not launched:
        desktop_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "canvas", "desktop"))
        electron_cmd = os.path.join(desktop_dir, "node_modules", ".bin", "electron.cmd")
        if os.path.exists(electron_cmd):
            env = {k: v for k, v in os.environ.items() if k not in ("ANTIGRAVITY_AGENT", "ELECTRON_RUN_AS_NODE")}
            subprocess.Popen([electron_cmd, "."], cwd=desktop_dir, env=env)

    deadline = time.time() + wait_seconds
    last_err = None
    while time.time() < deadline:
        time.sleep(1.5)
        try:
            return _http_json("GET", "/health", timeout=3)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Không kết nối được cổng ChatGPT Plus Gateway ({GATEWAY_URL}): {last_err}")


def _encode_images(image_paths: Optional[List[str]]) -> list:
    out = []
    for p in image_paths or []:
        if not p or not os.path.exists(p):
            raise FileNotFoundError(f"Không tìm thấy ảnh tham chiếu: {p}")
        mime, _ = mimetypes.guess_type(p)
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        out.append({
            "name": os.path.basename(p),
            "mime": mime or "image/png",
            "base64": b64,
        })
    return out


def ask_plus(
    prompt: str,
    model: str = "chatgpt-plus-thinking",
    project: str = "auto",
    mode: str = "auto",
    image_paths: Optional[List[str]] = None,
    file_paths: Optional[List[str]] = None,
    keep_chat: bool = False,
    timeout_min: int = 8,
) -> str:
    ensure_gateway_ready()
    res = _http_json(
        "POST",
        "/v1/chat/completions",
        {
            "model": model,
            "prompt": prompt,
            "project": project,
            "mode": mode,
            "images": _encode_images(image_paths),
            "files": [os.path.abspath(f) for f in (file_paths or []) if os.path.exists(f)],
            "keepChat": keep_chat,
            "timeoutMin": timeout_min,
        },
        timeout=timeout_min * 60 + 30,
    )
    return res["choices"][0]["message"]["content"]


def write_k4_flow_prompts(
    script_or_brief: str,
    image_paths: Optional[List[str]] = None,
    keep_chat: bool = True,
) -> str:
    """Gửi thẳng vào Dự án K4 Phim Chuyện Trong Nhà (tự động áp dụng Sources 48.9KB + quy chuẩn CHỐT KHÔNG GIAN)."""
    return ask_plus(
        prompt=script_or_brief,
        model="chatgpt-k4-flow",
        project="K4",
        mode="thinking",
        image_paths=image_paths,
        keep_chat=keep_chat,
        timeout_min=10,
    )


def write_htpm_brand(
    brief: str,
    image_paths: Optional[List[str]] = None,
    file_paths: Optional[List[str]] = None,
    keep_chat: bool = False,
) -> str:
    """Gửi thẳng vào Dự án HTPM (Hằng Thu Pharma / An Vượng Pharma / Feel Chicken)."""
    return ask_plus(
        prompt=brief,
        model="chatgpt-htpm-brand",
        project="HTPM",
        mode="thinking",
        image_paths=image_paths,
        file_paths=file_paths,
        keep_chat=keep_chat,
        timeout_min=8,
    )


def deep_research(topic: str, project: str = "none", keep_chat: bool = True) -> str:
    """Chạy Deep Research nghiên cứu đa nguồn web trên ChatGPT Plus."""
    return ask_plus(
        prompt=topic,
        model="chatgpt-deep-research",
        project=project,
        mode="deep-research",
        keep_chat=keep_chat,
        timeout_min=20,
    )


def generate_image(
    prompt: str,
    out_path: str,
    ratio: str = "9:16",
    image_paths: Optional[List[str]] = None,
    keep_chat: bool = False,
) -> str:
    """Tạo ảnh thương mại qua ChatGPT Plus (3 luồng song song, tự xóa chat nháp)."""
    ensure_gateway_ready()
    res = _http_json(
        "POST",
        "/v1/images/generations",
        {
            "prompt": prompt,
            "ratio": ratio,
            "n": 1,
            "images": _encode_images(image_paths),
            "keepChat": keep_chat,
        },
        timeout=420,
    )
    items = res.get("data") or []
    if not items:
        raise RuntimeError("ChatGPT Plus không trả về dữ liệu ảnh.")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(items[0]["b64_json"]))
    return os.path.abspath(out_path)


def generate_sora_video(
    prompt: str,
    out_path: str,
    ratio: str = "9:16",
    seconds: int = 10,
    image_paths: Optional[List[str]] = None,
) -> str:
    """Tạo video B-Roll / Điện ảnh qua OpenAI Sora (gói ChatGPT Plus)."""
    ensure_gateway_ready()
    res = _http_json(
        "POST",
        "/v1/videos/sora",
        {
            "prompt": prompt,
            "ratio": ratio,
            "seconds": seconds,
            "images": _encode_images(image_paths),
            "outPath": os.path.abspath(out_path),
        },
        timeout=540,
    )
    if not res.get("ok"):
        raise RuntimeError(res.get("error") or "Sora không tạo được video.")
    return res["outPath"]


def sync_project_knowledge(
    name: str,
    instructions: Optional[str] = None,
    source_files: Optional[List[str]] = None,
) -> dict:
    """Tạo hoặc cập nhật Dự án trên ChatGPT Plus (Instructions + tải tệp mới vào mục Sources)."""
    ensure_gateway_ready()
    payload = {"name": name}
    if instructions is not None:
        payload["instructions"] = instructions
    if source_files:
        payload["sourceFiles"] = [os.path.abspath(p) for p in source_files if os.path.exists(p)]
    return _http_json("POST", "/v1/projects/sync", payload, timeout=180)


def schedule_task(prompt: str, when: str = "every day at 8:00 AM", project: str = "none") -> dict:
    ensure_gateway_ready()
    return _http_json("POST", "/v1/tasks/schedule", {"prompt": prompt, "when": when, "project": project}, timeout=180)


def open_hub(target: str = "htpm") -> dict:
    ensure_gateway_ready()
    return _http_json("POST", "/v1/hub/open", {"target": target}, timeout=45)


def run_codex(prompt: str, cwd: Optional[str] = None) -> dict:
    ensure_gateway_ready()
    return _http_json("POST", "/v1/codex/exec", {"prompt": prompt, "cwd": cwd or os.getcwd()}, timeout=330)


def main():
    ap = argparse.ArgumentParser(description="CLI điều khiển Hệ sinh thái ChatGPT Plus qua Full Studio (:18620)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("health", help="Kiểm tra trạng thái cổng :18620 & danh sách Dự án")

    p_ask = sub.add_parser("ask", help="Hỏi / Suy luận với ChatGPT Plus")
    p_ask.add_argument("prompt")
    p_ask.add_argument("--project", default="auto", help="auto | HTPM | K4 | none")
    p_ask.add_argument("--mode", default="thinking", help="thinking | deep-research | search | canvas | auto")
    p_ask.add_argument("--image", action="append", default=[], help="Đường dẫn ảnh đính kèm")
    p_ask.add_argument("--file", action="append", default=[], help="Đường dẫn tệp đính kèm")
    p_ask.add_argument("--keep-chat", action="store_true")

    p_k4 = sub.add_parser("k4", help="Viết kịch bản / Asset Board / Prompt Flow trong Dự án K4")
    p_k4.add_argument("prompt")

    p_htpm = sub.add_parser("htpm", help="Phân tích sản phẩm / Viết bài trong Dự án HTPM")
    p_htpm.add_argument("prompt")
    p_htpm.add_argument("--image", action="append", default=[])

    p_res = sub.add_parser("research", help="Chạy Deep Research trên ChatGPT Plus")
    p_res.add_argument("topic")

    p_img = sub.add_parser("image", help="Tạo ảnh qua ChatGPT Plus")
    p_img.add_argument("prompt")
    p_img.add_argument("-o", "--out", required=True)
    p_img.add_argument("--ratio", default="9:16")
    p_img.add_argument("--image", action="append", default=[])

    p_sora = sub.add_parser("sora", help="Tạo video qua OpenAI Sora")
    p_sora.add_argument("prompt")
    p_sora.add_argument("-o", "--out", required=True)
    p_sora.add_argument("--ratio", default="9:16")
    p_sora.add_argument("--seconds", type=int, default=10)
    p_sora.add_argument("--image", action="append", default=[])

    p_sync = sub.add_parser("sync-project", help="Đồng bộ Instructions & tệp Sources lên Dự án ChatGPT Plus")
    p_sync.add_argument("--name", required=True)
    p_sync.add_argument("--instructions", default=None)
    p_sync.add_argument("--source", action="append", default=[])

    p_hub = sub.add_parser("hub", help="Mở nhanh htpm | k4 | sora | codex | library | connectors | scheduled | gpts")
    p_hub.add_argument("target")

    args = ap.parse_args()
    if args.cmd == "health":
        print(json.dumps(ensure_gateway_ready(), ensure_ascii=False, indent=2))
    elif args.cmd == "ask":
        print(ask_plus(args.prompt, project=args.project, mode=args.mode, image_paths=args.image, file_paths=args.file, keep_chat=args.keep_chat))
    elif args.cmd == "k4":
        print(write_k4_flow_prompts(args.prompt))
    elif args.cmd == "htpm":
        print(write_htpm_brand(args.prompt, image_paths=args.image))
    elif args.cmd == "research":
        print(deep_research(args.topic))
    elif args.cmd == "image":
        print(generate_image(args.prompt, out_path=args.out, ratio=args.ratio, image_paths=args.image))
    elif args.cmd == "sora":
        print(generate_sora_video(args.prompt, out_path=args.out, ratio=args.ratio, seconds=args.seconds, image_paths=args.image))
    elif args.cmd == "sync-project":
        print(json.dumps(sync_project_knowledge(args.name, instructions=args.instructions, source_files=args.source), ensure_ascii=False, indent=2))
    elif args.cmd == "hub":
        print(json.dumps(open_hub(args.target), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
