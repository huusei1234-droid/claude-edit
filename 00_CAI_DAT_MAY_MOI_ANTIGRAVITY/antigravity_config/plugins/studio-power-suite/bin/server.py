# -*- coding: utf-8 -*-
"""
FastMCP Server `studio-ai-hub` cho Google Antigravity & OpenAI Codex:
- Thực thi trực tiếp OpenAI Codex (gpt-6.2-sol / gpt-reserve, JSON Schema, chạy song song 4-6 luồng)
- Điều khiển Adobe After Effects 2027 (chạy ExtendScript .jsx & kết xuất aerender.exe)
- Tổng hợp giọng đọc tiếng Việt thần kinh (Studio TTS HoaiMyNeural / NamMinhNeural)
- Kiểm tra Vùng An Toàn Video Dọc 9:16 (TikTok x Reels 5 vùng đen cấm)
"""
import json
import os
import subprocess
import sys
import tempfile
from typing import List
from mcp.server.fastmcp import FastMCP

STUDIO_TOOLS_DIR = r"C:\AI\full studio\edit\canvas-tools"
if STUDIO_TOOLS_DIR not in sys.path:
    sys.path.insert(0, STUDIO_TOOLS_DIR)

AE_SUPPORT_DIR = r"C:\Program Files\Adobe\Adobe After Effects 2027\Support Files"
AFTERFX_EXE = os.path.join(AE_SUPPORT_DIR, "AfterFX.exe")
AERENDER_EXE = os.path.join(AE_SUPPORT_DIR, "aerender.exe")

mcp = FastMCP("studio-ai-hub")


@mcp.tool()
def codex_ask(
    prompt: str,
    model: str = "gpt-6.2-sol",
    reasoning: str = "medium",
    project: str = "auto",
    image_paths: List[str] = [],
) -> str:
    """Gọi trực tiếp OpenAI Codex cục bộ (gpt-6.2-sol hoặc gpt-reserve) bằng gói ChatGPT Plus, phản hồi 2-6s không mở trình duyệt."""
    import chatgpt_plus as cp

    return cp.ask_codex(
        prompt=prompt,
        model=model,
        reasoning=reasoning,
        project=project,
        image_paths=image_paths,
    )


@mcp.tool()
def codex_structured_json(
    prompt: str,
    schema_json: str,
    model: str = "gpt-6.2-sol",
    reasoning: str = "medium",
    project: str = "auto",
) -> str:
    """Ép OpenAI Codex trả về JSON hợp lệ 100% đúng theo JSON Schema (dùng cho bảng phân cảnh K4/TVC, Asset Board, CapCut JSON)."""
    import chatgpt_plus as cp

    schema = json.loads(schema_json) if isinstance(schema_json, str) else schema_json
    out = cp.ask_codex_json(prompt=prompt, schema=schema, model=model, reasoning=reasoning, project=project)
    return json.dumps(out, ensure_ascii=False, indent=2)


@mcp.tool()
def codex_parallel_batch(
    prompts: List[str],
    max_workers: int = 4,
    model: str = "gpt-reserve",
    project: str = "auto",
) -> str:
    """Chạy song song 4-6 luồng Codex cùng lúc (mặc định gpt-reserve siêu tốc tiết kiệm 4x hạn mức Plus)."""
    import chatgpt_plus as cp

    results = cp.codex_parallel(prompts=prompts, max_workers=max_workers, model=model, project=project)
    return json.dumps({"count": len(results), "results": results}, ensure_ascii=False, indent=2)


@mcp.tool()
def after_effects_run_jsx(jsx_script_or_path: str) -> str:
    """Thực thi mã ExtendScript (.jsx) trực tiếp trên Adobe After Effects 2027 (hỗ trợ thư viện ae-3d-effects.jsx)."""
    if not os.path.exists(AFTERFX_EXE):
        return json.dumps({"ok": False, "error": f"Không tìm thấy AfterFX.exe tại {AFTERFX_EXE}"}, ensure_ascii=False)

    if os.path.exists(jsx_script_or_path) and jsx_script_or_path.lower().endswith(".jsx"):
        jsx_path = os.path.abspath(jsx_script_or_path)
        cleanup = False
    else:
        fd, jsx_path = tempfile.mkstemp(prefix="studio_ae_", suffix=".jsx")
        os.close(fd)
        with open(jsx_path, "w", encoding="utf-8") as f:
            f.write(jsx_script_or_path)
        cleanup = True

    subprocess.Popen([AFTERFX_EXE, "-r", jsx_path])
    return json.dumps({"ok": True, "launched_jsx": jsx_path, "temp_file": cleanup}, ensure_ascii=False)


@mcp.tool()
def after_effects_render_comp(
    aep_path: str,
    comp_name: str,
    output_path: str,
    om_template: str = "",
) -> str:
    """Kết xuất không giao diện (headless) một Composition của Adobe After Effects 2027 bằng aerender.exe."""
    if not os.path.exists(AERENDER_EXE):
        return json.dumps({"ok": False, "error": f"Không tìm thấy aerender.exe tại {AERENDER_EXE}"}, ensure_ascii=False)
    if not os.path.exists(aep_path):
        return json.dumps({"ok": False, "error": f"Không tìm thấy tệp dự án .aep: {aep_path}"}, ensure_ascii=False)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cmd = [
        AERENDER_EXE,
        "-project", os.path.abspath(aep_path),
        "-comp", comp_name,
        "-output", os.path.abspath(output_path),
    ]
    if om_template:
        cmd.extend(["-OMtemplate", om_template])

    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    return json.dumps(
        {
            "ok": proc.returncode == 0 and os.path.exists(output_path),
            "returncode": proc.returncode,
            "output_path": os.path.abspath(output_path),
            "log_tail": (proc.stdout + "\n" + proc.stderr)[-1200:],
        },
        ensure_ascii=False,
    )


@mcp.tool()
def studio_tts_vietnamese(
    text: str,
    output_path: str,
    voice: str = "female",
    speed: float = 1.0,
) -> str:
    """Tạo tệp âm thanh giọng đọc tiếng Việt thần kinh (Nữ HoaiMyNeural / Nam NamMinhNeural) chuẩn TVC."""
    import chatgpt_plus as cp

    out = cp.tts_vietnamese(text=text, out_path=output_path, voice=voice, speed=speed)
    return json.dumps({"ok": True, "path": out, "bytes": os.path.getsize(out)}, ensure_ascii=False)


@mcp.tool()
def audit_safe_zone_9x16(media_path: str) -> str:
    """Kiểm tra tệp ảnh/video dọc 9:16 (1080x1920) có vi phạm 5 vùng đen cấm của TikTok x Reels hay không."""
    sz_py = os.path.join(STUDIO_TOOLS_DIR, "safe_zone_9x16.py")
    if not os.path.exists(sz_py):
        return json.dumps({"ok": False, "error": "Không tìm thấy safe_zone_9x16.py"}, ensure_ascii=False)
    proc = subprocess.run(
        [sys.executable, sz_py, media_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    return json.dumps(
        {"ok": proc.returncode == 0, "returncode": proc.returncode, "report": (proc.stdout + "\n" + proc.stderr).strip()},
        ensure_ascii=False,
    )


if __name__ == "__main__":
    mcp.run()
