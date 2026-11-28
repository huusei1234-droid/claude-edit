# -*- coding: utf-8 -*-
"""
Trình Tự Động Tiến Hóa Mỗi Ngày Bằng OpenAI Codex (`codex_daily_self_evolver.py`)
----------------------------------------------------------------------------------
Mục tiêu:
- Tận dụng hạn mức reset hàng ngày của gói OpenAI Codex (`gpt-6.2-sol`, `reasoning="xhigh"`)
  để tự động rà soát, tối ưu hóa hiệu năng, bổ sung test-case, thêm preset đồ họa/âm thanh
  và nâng cấp dần toàn bộ 43+ Siêu Kỹ Năng trong `.agents/skills/` & `edit/canvas-tools/`.
- Cơ chế An Toàn Tuyệt Đối (Zero-Regression Gate):
  1. Mọi tác vụ chạy trong vùng đệm `skills_evolution_staging/` ở mức ưu tiên CPU thấp (`BELOW_NORMAL_PRIORITY_CLASS`) để 0% gây lag máy.
  2. Bắt buộc vượt qua cổng kiểm định tự động (`py_compile` + `--self-test`) mới được cập nhật vào `.agents/skills/`.
  3. Tự động phát hiện khi chạm trần hạn mức ngày/phiên của Codex (`usage limit` / `rate limit`) và dừng êm ngay lập tức.
  4. Ghi nhật ký chi tiết vào `.agents/skills/CODEX_DAILY_EVOLUTION_LOG.md`.
"""
import argparse
import datetime
import glob
import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = r"C:\AI\full studio" if os.path.exists(r"C:\AI\full studio\.agents\skills") else r"D:\AI\full studio"
SKILLS_DIR = os.path.join(REPO, ".agents", "skills")
STATE_FILE = os.path.join(SKILLS_DIR, "codex_evolution_state.json")
LOG_FILE = os.path.join(SKILLS_DIR, "CODEX_DAILY_EVOLUTION_LOG.md")
STAGING_DIR = os.path.join(REPO, "skills_evolution_staging")

QUOTA_KEYWORDS = (
    "usage limit",
    "rate limit",
    "quota",
    "too many requests",
    "try again later",
    "exceeded your",
    "upgrade to pro",
)

# Lộ trình tiến hóa liên tục xoay vòng (khi hoàn tất hết 1 vòng sẽ tự động sang vòng nâng cấp sâu tiếp theo: V6.1 -> V6.2 -> V7...)
EVOLUTION_CURRICULUM = [
    {
        "id": "evo_01_remotion_3d_pack",
        "skill": "remotion-best-practices",
        "title": "Rèn bộ công cụ sinh Component Remotion 9:16 Safe-Zone & 3D Camera Presets",
        "prompt": r"""Đọc `skills_evolution_staging/remotion-best-practices/SKILL.md` và tạo mới công cụ `skills_evolution_staging/remotion-best-practices/scripts/remotion_safezone_scaffold.py` (Python 3.11 UTF-8, có `--self-test` in `SELF_TEST_OK`):
- Tự động sinh khung component `.tsx` chuẩn `1080x1920 @ 30fps` có khóa cứng 5 Vùng Đen Cấm TikTok/Reels, hiệu ứng `spring()` đàn hồi mượt và preset phụ đề giữ màu.
- Cập nhật `SKILL.md` bổ sung hướng dẫn CLI.""",
    },
    {
        "id": "evo_02_ps_uxp_ai_recipes",
        "skill": "ps",
        "title": "Rèn bộ công thức Batch Recipe JSON cho Photoshop MCP (Harmonize & Select Subject)",
        "prompt": r"""Đọc `skills_evolution_staging/ps/SKILL.md` và tạo mới công cụ `skills_evolution_staging/ps/scripts/ps_mcp_recipe_generator.py` (Python 3.11 UTF-8, có `--self-test` in `SELF_TEST_OK`):
- Sinh chuỗi payload JSON chuẩn cho `ps_batch` / `ps_recipe` để tách chủ thể hàng loạt, cân bằng ánh sáng Harmonize, gắn sRGB và lưu `.PSD` không khóa cửa sổ người dùng.
- Cập nhật `SKILL.md` tích hợp công cụ.""",
    },
    {
        "id": "evo_03_hyperframes_registry_search",
        "skill": "hyperframes-registry",
        "title": "Rèn bộ máy tìm kiếm Offline 448 hiệu ứng Final Cut / Liquid Glass / Shaders",
        "prompt": r"""Đọc `skills_evolution_staging/hyperframes-registry/SKILL.md` và tạo công cụ `skills_evolution_staging/hyperframes-registry/scripts/offline_pack_finder.py` (Python 3.11 UTF-8, có `--query`, `--category`, `--self-test` in `SELF_TEST_OK`):
- Quét kho `BO_KIEN_THUC_TVC_AI_PORTABLE/03_TAI_NGUYEN_DUNG_CHUNG/fcp_hyperframes_pack` (nếu có trên đĩa) hoặc danh mục chỉ mục để gợi ý nhanh Top 5 hiệu ứng chuyển cảnh, chữ 3D, Liquid Glass khớp tâm trạng kịch bản!
- Cập nhật `SKILL.md`.""",
    },
    {
        "id": "evo_04_figma_brand_token_extractor",
        "skill": "figma",
        "title": "Rèn trình chuyển đổi Figma Design Tokens sang CSS Variables & Brand Guidelines JSON",
        "prompt": r"""Đọc `skills_evolution_staging/figma/SKILL.md` và tạo công cụ `skills_evolution_staging/figma/scripts/figma_tokens_to_brandkit.py` (Python 3.11 UTF-8, có `--self-test` in `SELF_TEST_OK`):
- Chuyển đổi file JSON biến màu/font từ Figma sang `brand_guidelines.json` + `brand-tokens.css` (tự sinh thêm các dải 5-stop Gradient sang trọng cho tiêu đề TVC).
- Cập nhật `SKILL.md`.""",
    },
    {
        "id": "evo_05_slideshow_interactive_deck",
        "skill": "slideshow",
        "title": "Rèn trình đóng gói Bài Thuyết Trình Pitching Khách Hàng Tương Tác (Live HTML Deck)",
        "prompt": r"""Đọc `skills_evolution_staging/slideshow/SKILL.md` và tạo công cụ `skills_evolution_staging/slideshow/scripts/agency_pitch_deck_builder.py` (Python 3.11 UTF-8, có `--self-test` in `SELF_TEST_OK`):
- Sinh bộ slide HTML thuyết trình chiến dịch TVC / Phim AI có phím tắt chuyển trang, ghi chú diễn giả (Speaker Notes) và khung nhúng xem thử video trực tiếp.
- Cập nhật `SKILL.md`.""",
    },
    {
        "id": "evo_06_docx_xlsx_pdf_qa_suite",
        "skill": "agency-client-deliverables",
        "title": "Nâng cấp sâu bộ kiểm định Báo cáo Nghiệm thu PDF/DOCX/XLSX đa nhãn hàng",
        "prompt": r"""Đọc `skills_evolution_staging/agency-client-deliverables/SKILL.md` và `scripts/build_agency_pack.py`, nâng cấp thêm chế độ `--export-executive-summary` xuất bảng tổng kết KPI & ngân sách đa kênh siêu gọn đẹp cho Chủ tịch/Giám đốc duyệt nhanh trên điện thoại, giữ nguyên và mở rộng `--self-test` in `SELF_TEST_OK`.""",
    },
    {
        "id": "evo_07_cross_skill_deep_optimizer",
        "skill": "video-qc-auditor",
        "title": "Kiểm toán chéo & tối ưu tốc độ toàn bộ Script Python trong kho Siêu Kỹ Năng",
        "prompt": r"""Đọc `skills_evolution_staging/video-qc-auditor/scripts/forensic_qc_analyzer.py` và tối ưu thêm chế độ `--fast-sample` (chỉ lấy mẫu frame thông minh giúp tăng tốc kiểm tra video dài gấp 3 lần mà vẫn bắt chính xác 100% viền đen, lệch tiếng và vùng an toàn `9:16`), đảm bảo `--self-test` in `SELF_TEST_OK`.""",
    },
]


def find_codex_exe() -> str:
    local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    cands = sorted(
        glob.glob(os.path.join(local_app, "OpenAI", "Codex", "bin", "*", "codex.exe")),
        key=os.path.getmtime,
        reverse=True,
    )
    if cands:
        return cands[0]
    return os.path.join(os.environ.get("APPDATA", ""), "npm", "codex.cmd")


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE, encoding="utf-8"))
        except Exception:
            pass
    return {"generation_cycle": 1, "completed_ids": [], "total_runs": 0, "history": []}


def save_state(st: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, ensure_ascii=False)


def is_quota_exhausted(rc: int, stderr_txt: str, stdout_txt: str) -> bool:
    if rc == 0:
        return False
    blob = f"{stderr_txt}\n{stdout_txt}".lower()
    return any(k in blob for k in QUOTA_KEYWORDS)


def verify_staged_skill(skill_dir: str, py_exe: str) -> tuple[bool, str]:
    py_files = []
    for r, _, fs in os.walk(skill_dir):
        for f in fs:
            if f.endswith(".py"):
                fp = os.path.join(r, f)
                py_compile.compile(fp, doraise=True)
                py_files.append(fp)
    tested = []
    for fp in py_files:
        txt = open(fp, encoding="utf-8", errors="replace").read()
        if "--self-test" in txt:
            p = subprocess.run(
                [py_exe, "-X", "utf8", fp, "--self-test"],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
            if p.returncode != 0:
                return False, f"Self-test failed on {os.path.basename(fp)}: {p.stderr[-200:]}"
            tested.append(os.path.basename(fp))
    return True, f"Compiled {len(py_files)} .py files; self-tested: {', '.join(tested) or 'syntax-ok'}"


def run_evolution_batch(max_tasks: int = 3) -> dict:
    codex_exe = find_codex_exe()
    py_exe = r"C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe"
    if not os.path.exists(py_exe):
        py_exe = sys.executable

    state = load_state()
    pending = [item for item in EVOLUTION_CURRICULUM if item["id"] not in state["completed_ids"]]
    if not pending:
        state["generation_cycle"] = int(state.get("generation_cycle", 1)) + 1
        state["completed_ids"] = []
        pending = list(EVOLUTION_CURRICULUM)

    batch = pending[:max_tasks]
    below_normal = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0x00004000)
    results = []
    quota_hit = False

    for item in batch:
        skill_name = item["skill"]
        src_skill = os.path.join(SKILLS_DIR, skill_name)
        stg_skill = os.path.join(STAGING_DIR, skill_name)
        shutil.rmtree(STAGING_DIR, ignore_errors=True)
        os.makedirs(STAGING_DIR, exist_ok=True)
        if os.path.isdir(src_skill):
            shutil.copytree(src_skill, stg_skill, dirs_exist_ok=True)
        else:
            os.makedirs(stg_skill, exist_ok=True)

        cycle = state.get("generation_cycle", 1)
        full_prompt = (
            "QUY TẮC MÔI TRƯỜNG:\n"
            f"- Đọc & ghi trực tiếp trong `skills_evolution_staging/{skill_name}/` (trong tài liệu SKILL.md vẫn ghi `.agents/skills/{skill_name}/`).\n"
            "- Không bật trình duyệt headless Chrome/Edge/Puppeteer; chỉ kiểm thử bằng Python CLI `--self-test`.\n"
            f"- Chu kỳ tiến hóa hiện tại: V6.{cycle}.\n\n"
            + item["prompt"]
        )

        t0 = time.time()
        with tempfile.TemporaryDirectory(prefix="codex_evo_") as td:
            out_f = os.path.join(td, "summary.txt")
            cmd = [
                codex_exe,
                "exec",
                "--skip-git-repo-check",
                "-C",
                REPO,
                "-s",
                "workspace-write",
                "-m",
                "gpt-6.2-sol",
                "-c",
                'model_reasoning_effort="xhigh"',
                "-o",
                out_f,
                "-",
            ]
            try:
                proc = subprocess.run(
                    cmd,
                    input=full_prompt,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=REPO,
                    shell=codex_exe.lower().endswith(".cmd"),
                    creationflags=below_normal if os.name == "nt" else 0,
                    timeout=600,
                )
                rc = proc.returncode
                stderr_t, stdout_t = proc.stderr, proc.stdout
            except subprocess.TimeoutExpired as exc:
                rc, stderr_t, stdout_t = 124, str(exc), ""

            dur = round(time.time() - t0, 1)
            if is_quota_exhausted(rc, stderr_t, stdout_t):
                quota_hit = True
                results.append({"id": item["id"], "skill": skill_name, "status": "QUOTA_REACHED", "seconds": dur})
                break

            if rc == 0 and os.path.isdir(stg_skill):
                ok, msg = verify_staged_skill(stg_skill, py_exe)
                if ok:
                    os.makedirs(src_skill, exist_ok=True)
                    for r, _, fs in os.walk(stg_skill):
                        rel = os.path.relpath(r, stg_skill)
                        td_dst = src_skill if rel == "." else os.path.join(src_skill, rel)
                        os.makedirs(td_dst, exist_ok=True)
                        for f in fs:
                            sf = os.path.join(r, f)
                            df = os.path.join(td_dst, f)
                            shutil.copy2(sf, df)
                            if f.endswith((".md", ".py", ".html", ".jsx", ".json")):
                                txt = open(df, encoding="utf-8", errors="replace").read()
                                fixed = txt.replace("skills_evolution_staging/", ".agents/skills/").replace(
                                    "skills_evolution_staging\\", ".agents\\skills\\"
                                )
                                if fixed != txt:
                                    with open(df, "w", encoding="utf-8") as wf:
                                        wf.write(fixed)
                    state["completed_ids"].append(item["id"])
                    results.append({"id": item["id"], "skill": skill_name, "status": "UPGRADED_PASS", "detail": msg, "seconds": dur})
                else:
                    results.append({"id": item["id"], "skill": skill_name, "status": "REJECTED_BY_GATE", "detail": msg, "seconds": dur})
            else:
                results.append({"id": item["id"], "skill": skill_name, "status": f"ERROR_RC_{rc}", "seconds": dur})

    shutil.rmtree(STAGING_DIR, ignore_errors=True)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["total_runs"] = int(state.get("total_runs", 0)) + 1
    state["last_run_at"] = now_str
    state["history"] = (state.get("history", []) + [{"at": now_str, "quota_hit": quota_hit, "results": results}])[-30:]
    save_state(state)

    # Append to Markdown evolution log
    log_entry = [f"\n## [{now_str}] Chu kỳ V6.{state['generation_cycle']} (Quota chạm trần: `{quota_hit}`)"]
    for r in results:
        log_entry.append(f"- **`{r['skill']}`** (`{r['id']}`): **{r['status']}** trong `{r['seconds']}s` — {r.get('detail', '')}")
    header = "# Nhật Ký Tự Động Bào Điểm OpenAI Codex Nâng Cấp Hệ Thống Hàng Ngày\n"
    old_log = open(LOG_FILE, encoding="utf-8", errors="replace").read() if os.path.exists(LOG_FILE) else header
    with open(LOG_FILE, "w", encoding="utf-8") as lf:
        lf.write(old_log.rstrip() + "\n" + "\n".join(log_entry) + "\n")

    return {"at": now_str, "cycle": state["generation_cycle"], "quota_hit": quota_hit, "results": results}


def main():
    ap = argparse.ArgumentParser(description="Daily OpenAI Codex Self-Evolution Engine")
    ap.add_argument("--max-tasks", type=int, default=3, help="Số lượng nâng cấp mỗi đợt chạy")
    ap.add_argument("--status", action="store_true", help="Xem trạng thái tiến hóa hiện tại")
    args = ap.parse_args()

    if args.status:
        st = load_state()
        print(json.dumps({
            "repo": REPO,
            "codex_exe": find_codex_exe(),
            "cycle": st.get("generation_cycle", 1),
            "completed_in_cycle": f"{len(st.get('completed_ids', []))}/{len(EVOLUTION_CURRICULUM)}",
            "total_runs": st.get("total_runs", 0),
            "last_run_at": st.get("last_run_at", "never"),
        }, ensure_ascii=False, indent=2))
        return

    out = run_evolution_batch(max_tasks=args.max_tasks)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
