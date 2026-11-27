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


def _find_codex_exe() -> str:
    import glob
    local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    candidates = sorted(
        glob.glob(os.path.join(local_app, "OpenAI", "Codex", "bin", "*", "codex.exe")),
        key=os.path.getmtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    npm_shim = os.path.join(os.environ.get("APPDATA", ""), "npm", "codex.cmd")
    return npm_shim if os.path.exists(npm_shim) else "codex"


def ask_codex(
    prompt: str,
    model: str = "gpt-6.2-sol",
    reasoning: str = "medium",
    project: str = "auto",
    image_paths: Optional[List[str]] = None,
    sandbox: str = "read-only",
    cwd: Optional[str] = None,
    ephemeral: bool = True,
    timeout: int = 360,
) -> str:
    """
    Gọi trực tiếp OpenAI Codex cục bộ (gpt-6.2-sol / gpt-6.2-astra) qua gói ChatGPT Plus:
    chạy ngầm 100%, tốc độ 2-5 giây, không cần mở bất kỳ tab trình duyệt nào!
    """
    import tempfile

    mig_base = r"C:\AI\full studio\huu\chatgpt_migration_huusei1234\02_PROJECTS"
    proj_up = (project or "auto").upper()
    if proj_up == "AUTO":
        if any(k in prompt for k in ("CHỐT KHÔNG GIAN", "IMAGE XUẤT HIỆN", "ASSET BOARD", "K4", "prompt flow")):
            proj_up = "K4"
        elif any(k in prompt for k in ("AVPM", "An Vượng", "Chị Hậu", "AV Protein", "Bojomi", "Curcumilk", "Collamela")):
            proj_up = "AVPM"
        elif any(k in prompt for k in ("HTPM", "Hằng Thu", "Feel Chicken")):
            proj_up = "HTPM"

    full_prompt = prompt
    if proj_up == "K4":
        inst_p = os.path.join(mig_base, "K4_Phim_Chuyen_Trong_Nha", "INSTRUCTIONS.txt")
        if os.path.exists(inst_p):
            full_prompt = f"[QUY CHUẨN DỰ ÁN K4]\n{open(inst_p, encoding='utf-8').read().strip()}\n\n[YÊU CẦU]\n{prompt}"
    elif proj_up == "AVPM":
        inst_p = os.path.join(mig_base, "AVPM", "INSTRUCTIONS.txt")
        av_log = r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\NHAT_KY_CAP_NHAT_KIEN_THUC_ZALO.md"
        extra = f"\n\n[CẬP NHẬT ZALO/FB AN VƯỢNG]\n{open(av_log, encoding='utf-8').read()[-3500:]}" if os.path.exists(av_log) else ""
        if os.path.exists(inst_p):
            full_prompt = f"[QUY CHUẨN DỰ ÁN AN VƯỢNG PHARMA]\n{open(inst_p, encoding='utf-8').read().strip()}{extra}\n\n[YÊU CẦU]\n{prompt}"
    elif proj_up == "HTPM":
        inst_p = os.path.join(mig_base, "HTPM", "INSTRUCTIONS.txt")
        if os.path.exists(inst_p):
            full_prompt = f"[QUY CHUẨN DỰ ÁN HTPM]\n{open(inst_p, encoding='utf-8').read().strip()}\n\n[YÊU CẦU]\n{prompt}"

    exe = _find_codex_exe()
    work_dir = cwd or (r"C:\AI\full studio" if os.path.exists(r"C:\AI\full studio") else os.getcwd())
    with tempfile.TemporaryDirectory(prefix="codex_py_") as tmp_d:
        out_msg = os.path.join(tmp_d, "reply.txt")
        cmd = [exe, "exec", "--skip-git-repo-check", "-C", work_dir, "-s", sandbox, "-m", model, "-o", out_msg]
        if ephemeral and sandbox == "read-only":
            cmd.append("--ephemeral")
        if reasoning in ("low", "medium", "high", "xhigh"):
            cmd.extend(["-c", f'model_reasoning_effort="{reasoning}"'])
        for ip in image_paths or []:
            if ip and os.path.exists(ip):
                cmd.extend(["-i", os.path.abspath(ip)])
        cmd.append("-")

        proc = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=work_dir,
            shell=exe.lower().endswith(".cmd"),
            timeout=timeout,
        )
        if os.path.exists(out_msg):
            ans = open(out_msg, encoding="utf-8", errors="replace").read().strip()
            if ans:
                return ans
        if proc.returncode != 0:
            raise RuntimeError(f"Codex lỗi (rc={proc.returncode}): {proc.stderr[-500:]}")
        return proc.stdout.strip()


def ask_codex_json(
    prompt: str,
    schema: dict,
    model: str = "gpt-6.2-sol",
    reasoning: str = "medium",
    project: str = "auto",
    image_paths: Optional[List[str]] = None,
) -> dict:
    """Ép Codex trả về JSON hợp lệ 100% đúng theo JSON Schema (--output-schema) cho tự động hóa kịch bản & CapCut."""
    import tempfile

    exe = _find_codex_exe()
    work_dir = r"C:\AI\full studio" if os.path.exists(r"C:\AI\full studio") else os.getcwd()
    with tempfile.TemporaryDirectory(prefix="codex_schema_") as tmp_d:
        schema_file = os.path.join(tmp_d, "schema.json")
        out_msg = os.path.join(tmp_d, "out.json")
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False)
        cmd = [
            exe, "exec", "--skip-git-repo-check", "--ephemeral",
            "-C", work_dir, "-s", "read-only", "-m", model,
            "--output-schema", schema_file, "-o", out_msg,
        ]
        if reasoning in ("minimal", "low", "medium", "high", "xhigh", "max", "ultra"):
            cmd.extend(["-c", f'model_reasoning_effort="{reasoning}"'])
        for ip in image_paths or []:
            if ip and os.path.exists(ip):
                cmd.extend(["-i", os.path.abspath(ip)])
        cmd.append("-")

        proc = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=work_dir, shell=exe.lower().endswith(".cmd"), timeout=360
        )
        if not os.path.exists(out_msg):
            raise RuntimeError(f"Codex schema lỗi: {proc.stderr[-400:]}")
        return json.loads(open(out_msg, encoding="utf-8").read().strip())


def codex_parallel(
    prompts: List[str],
    max_workers: int = 4,
    model: str = "gpt-reserve",
    reasoning: str = "medium",
    project: str = "auto",
) -> List[str]:
    """Chạy song song 4–6 luồng Codex cùng lúc (mặc định dùng gpt-reserve siêu tốc để tiết kiệm 4x hạn mức Plus!)."""
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = [
            pool.submit(ask_codex, p, model=model, reasoning=reasoning, project=project)
            for p in prompts
        ]
        return [f.result() for f in futs]


def tts_vietnamese(text: str, out_path: str, voice: str = "female", speed: float = 1.0) -> str:
    """Tạo file giọng đọc tiếng Việt thần kinh chuẩn TVC/Dược sĩ trực tiếp không tốn API key."""
    venv_py = r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
    py_exe = venv_py if os.path.exists(venv_py) else sys.executable
    v_id = "vi-VN-NamMinhNeural" if voice.lower() in ("male", "nam", "onyx", "echo") else "vi-VN-HoaiMyNeural"
    rate_pct = int(round((speed - 1.0) * 100))
    rate_arg = f"{rate_pct:+d}%"
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    subprocess.run(
        [py_exe, "-m", "edge_tts", "--voice", v_id, f"--rate={rate_arg}", "--text", text, "--write-media", out_path],
        check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return os.path.abspath(out_path)


def sync_an_vuong_project() -> dict:
    """Đồng bộ tự động Dự án An Vượng Pharma (Instructions + Nhật ký Zalo/FB mới nhất) lên ChatGPT Plus."""
    inst_p = r"C:\AI\full studio\huu\chatgpt_migration_huusei1234\02_PROJECTS\AVPM\INSTRUCTIONS.txt"
    av_log = r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\NHAT_KY_CAP_NHAT_KIEN_THUC_ZALO.md"
    inst = open(inst_p, encoding="utf-8").read().strip() if os.path.exists(inst_p) else ""
    sources = [av_log] if os.path.exists(av_log) else []
    return sync_project_knowledge("An Vượng Pharma", instructions=inst, source_files=sources)


def run_codex(prompt: str, cwd: Optional[str] = None, sandbox: str = "workspace-write") -> dict:
    text = ask_codex(prompt, sandbox=sandbox, cwd=cwd, ephemeral=False)
    return {"ok": True, "text": text}


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

    p_codex = sub.add_parser("codex", help="Chạy trực tiếp OpenAI Codex (gpt-6.2-sol) siêu tốc 2s không cần mở trình duyệt")
    p_codex.add_argument("prompt")
    p_codex.add_argument("--model", default="gpt-6.2-sol")
    p_codex.add_argument("--reasoning", default="medium", help="low | medium | high | xhigh")
    p_codex.add_argument("--project", default="auto", help="auto | K4 | HTPM | none")
    p_codex.add_argument("--sandbox", default="read-only", help="read-only | workspace-write")
    p_codex.add_argument("--image", action="append", default=[])

    p_hub = sub.add_parser("hub", help="Mở nhanh htpm | k4 | sora | codex | library | connectors | scheduled | gpts")
    p_hub.add_argument("target")

    args = ap.parse_args()
    if args.cmd == "health":
        print(json.dumps(ensure_gateway_ready(), ensure_ascii=False, indent=2))
    elif args.cmd == "codex":
        print(ask_codex(args.prompt, model=args.model, reasoning=args.reasoning, project=args.project, image_paths=args.image, sandbox=args.sandbox))
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
