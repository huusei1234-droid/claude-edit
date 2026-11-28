# -*- coding: utf-8 -*-
"""
Master V3 Behind-Subject 14-Video HyperFrames Director (#01 -> #14):
- 0% Speech Repetition (loads verified `vXX_clean_words.json`).
- 0px Presenter Vertical/Horizontal Shift ("đừng có kéo mẫu lên xuống nữa").
- 0% B-Roll Covering Chị Hằng ("không được để broll che mất chị mẫu" — 100% behind RVM `vid-fg` at z-index 20!).
- 0% Background Music ("không cần nhạc nền luôn" — pure crisp -14.0 LUFS studio voice + subtle tactile micro-SFX).
- 14 Unique Behind-Subject Visual Architectures (modeled directly on hanh.sung.suong reel_01..14 + Talking-Head FX).
"""
import glob
import html
import json
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_14_master_spec import VIDEOS_SPEC
from build_and_render_wave import (
    BASE_DIR,
    DEST_HTPM_DIR,
    DEST_LOCAL_DIR,
    DEST_MASTER_DIR,
    DU_AN_ROOT,
    HF_BIN,
    V01_HF,
    plan_timings,
)
from behind_styles_01_07 import (
    build_v01,
    build_v02,
    build_v03,
    build_v04,
    build_v05,
    build_v06,
    build_v07,
)
from behind_styles_08_14 import (
    build_v08,
    build_v09,
    build_v10,
    build_v11,
    build_v12,
    build_v13,
    build_v14,
)

FONTS_SRC = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
AUDIO_SRC = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"

NEEDED_FONTS = [
    "Anton-Regular.ttf",
    "AsapCondensed-Black.ttf",
    "AsapCondensed-ExtraBold.ttf",
    "BarlowCondensed-BlackItalic.ttf",
    "BeVietnamPro-Bold.ttf",
    "BeVietnamPro-ExtraBold.ttf",
]

V01_SPEC = {
    "idx": 1,
    "slug": "v01_cat_bao_quy_dau",
    "final_name": "261126 HTPM cắt bao quy đầu có giúp kéo dài cuộc yêu không final.mp4",
    "hook_lines": ["CẮT BAO QUY ĐẦU", "CÓ GIÚP KÉO DÀI", "CUỘC YÊU KHÔNG?"],
    "spoken_script": (
        "Chỉ được 1–2 phút nên các anh định cắt bao quy đầu để lâu hơn hả? "
        "Cắt bao quy đầu không phải cách điều trị chuẩn cho xuất tinh sớm đâu. "
        "Nếu được đề nghị cắt, hãy hỏi rõ mình có bệnh lý gì cần xử lý. "
        "Đừng vội phẫu thuật chỉ vì lời hứa kéo dài cuộc yêu nha các anh!"
    ),
    "behind_kw_anchor": ["không", "phải", "cách"],
    "behind_kw_lines": ["KHÔNG PHẢI CÁCH", "TRỊ XUẤT SỚM!"],
    "broll_cards": [
        {"tag": "✕ SAI MỤC ĐÍCH", "head": "CẮT BAO QUY ĐẦU", "desc": "Không trị xuất tinh sớm"},
        {"tag": "✔ KHÁM ĐÚNG", "head": "HỎI RÕ BÁC SĨ", "desc": "Tìm đúng nguyên nhân"},
    ],
}

BUILDERS = {
    1: ("V01_AR_HOURGLASS_FAN", build_v01),
    2: ("V02_DROPLET_SCALE_SHIELD", build_v02),
    3: ("V03_KOBE_STEPS_OVUM_FLIP", build_v03),
    4: ("V04_DNA_HELIX_ARC", build_v04),
    5: ("V05_TIMER_REPEAT_RING", build_v05),
    6: ("V06_HEART_CRYSTAL_TWIN", build_v06),
    7: ("V07_VESSEL_FLOW_COMPARE", build_v07),
    8: ("V08_ORBIT_WELLNESS_SHIELD", build_v08),
    9: ("V09_ECG_WAVE_DIALOGUE", build_v09),
    10: ("V10_THV3_RECOVERY_MONITOR", build_v10),
    11: ("V11_CLOCK_ICE_THERMO", build_v11),
    12: ("V12_BEER_STAMINA_TANK", build_v12),
    13: ("V13_CURVED_5CARD_CAROUSEL", build_v13),
    14: ("V14_5HABITS_FLYING_DECK", build_v14),
}


def get_adjusted_specs():
    specs = [V01_SPEC] + [dict(s) for s in VIDEOS_SPEC]
    for s in specs:
        if s["idx"] == 2:
            # Exact spoken words after trimming trailing repetition at 13.36s!
            s["spoken_script"] = (
                "Quan hệ nhiều có làm cạn tinh trùng không các anh? "
                "Lượng tinh dịch và số lượng tinh trùng là hai chỉ số hoàn toàn khác nhau. "
                "Xuất tinh thường xuyên không đồng nghĩa chắc chắn bị vô sinh đâu. "
                "Đừng tự đoán qua mắt thường!"
            )
        elif s["idx"] == 6:
            s["spoken_script"] = (
                "Rất muốn gần vợ mà cơ thể lại không nghe lời phải làm sao? "
                "Các anh tách riêng hai chuyện nhé: ham muốn thương, còn cương là phản ứng mạch máu của cơ thể. "
                "Đừng để một lần trục trặc thành hiểu lầm hết yêu, hãy chia sẻ thật với vợ và khám sức khỏe nhé!"
            )
        elif s["idx"] == 11:
            s["spoken_script"] = (
                "Xem phim nhạy cảm quá nhiều gây ra bốn tác hại gì cho nam giới? "
                "Một là tốn thời gian thức khuya. Dễ rối loạn cương cứng. "
                "Ba là bị trơ khi gần gũi thật. Bốn là khó xuất hoặc xuất muộn bất thường. "
                "Anh nào đang xem quá nhiều hãy điều chỉnh ngay nhé!"
            )
    return specs


def stage_fonts_and_sfx(hf_dir: str, sfx_cues: list):
    fdir = os.path.join(hf_dir, "assets", "fonts")
    adir = os.path.join(hf_dir, "assets", "audio")
    os.makedirs(fdir, exist_ok=True)
    os.makedirs(adir, exist_ok=True)

    # Copy Montserrat-Black into a temp buffer first if hf_dir == V01_HF
    v01_mont = os.path.join(V01_HF, "assets", "fonts", "Montserrat-Black.ttf")
    dst_mont = os.path.join(fdir, "Montserrat-Black.ttf")
    if os.path.abspath(v01_mont) != os.path.abspath(dst_mont):
        shutil.copy2(v01_mont, dst_mont)

    for fn in NEEDED_FONTS:
        src = os.path.join(FONTS_SRC, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(fdir, fn))

    v01_pop = os.path.join(V01_HF, "assets", "audio", "sfx_hook_pop.mp3")
    dst_pop = os.path.join(adir, "sfx_hook_pop.mp3")
    if os.path.abspath(v01_pop) != os.path.abspath(dst_pop):
        shutil.copy2(v01_pop, dst_pop)

    for sfx_fn, _, _ in sfx_cues:
        s_path = os.path.join(AUDIO_SRC, sfx_fn)
        if os.path.exists(s_path):
            shutil.copy2(s_path, os.path.join(adir, sfx_fn))


def write_v3_project(sp: dict, plan: dict, hf_dir: str):
    style_name, builder_fn = BUILDERS[sp["idx"]]
    scene_html, sfx_cues = builder_fn(sp, plan)

    comp_dir = os.path.join(hf_dir, "compositions")
    os.makedirs(comp_dir, exist_ok=True)
    for old_f in os.listdir(comp_dir):
        if old_f != "presenter-stage.html":
            try:
                os.remove(os.path.join(comp_dir, old_f))
            except Exception:
                pass

    src_hf_json = os.path.join(V01_HF, "hyperframes.json")
    dst_hf_json = os.path.join(hf_dir, "hyperframes.json")
    if os.path.abspath(src_hf_json) != os.path.abspath(dst_hf_json):
        shutil.copy2(src_hf_json, dst_hf_json)

    stage_fonts_and_sfx(hf_dir, sfx_cues)
    with open(os.path.join(comp_dir, "presenter-stage.html"), "w", encoding="utf-8") as f:
        f.write(scene_html)

    dur = plan["dur"]
    # ZERO BGM! Only subtle hook pop + tactile micro-SFX cues!
    sfx_tags = [
        '      <audio id="sfx-hook-0" class="clip" src="assets/audio/sfx_hook_pop.mp3" data-start="0.04" data-duration="0.14" data-track-index="2" data-volume="0.18"></audio>'
    ]
    for i, (sfx_fn, st, vol) in enumerate(sfx_cues, 1):
        st_clamped = max(0.06, min(round(dur - 0.35, 2), round(st, 2)))
        tr_idx = 2 + (i % 2)
        sfx_tags.append(
            f'      <audio id="sfx-v3-{i}" class="clip" src="assets/audio/{sfx_fn}" '
            f'data-start="{st_clamped:.2f}" data-duration="0.26" data-track-index="{tr_idx}" data-volume="{vol:.2f}" data-fade-out="0.08"></audio>'
        )

    idx_html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{html.escape(sp['final_name'])} [{style_name}]</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body, #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #f5f2eb; }}
      .scene-host {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.2f}" data-width="1080" data-height="1920" data-fps="30">
      <div id="presenter-stage" class="scene-host" data-composition-id="presenter-stage" data-composition-src="compositions/presenter-stage.html" data-start="0" data-duration="{dur:.2f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
{chr(10).join(sfx_tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    with open(os.path.join(hf_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx_html)
    return style_name


def render_and_deliver_v3(sp: dict, plan: dict, hf_dir: str, style_name: str):
    chk = subprocess.run([HF_BIN, "check", "--json"], cwd=hf_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
    j_start = chk.stdout.find("{")
    if j_start >= 0:
        d = json.loads(chk.stdout[j_start:])
        errs = [x for x in d.get("diagnostics", []) if x.get("severity") == "error"]
        if errs:
            raise RuntimeError(f"Lint errors on #{sp['idx']} ({style_name}): {errs}")

    raw_render = os.path.join(hf_dir, "_v3_raw.mp4")
    last_err = ""
    for _ in range(2):
        ren = subprocess.run(
            [HF_BIN, "render", "--output", raw_render, "--fps", "30", "--low-memory-mode", "--frames-cache-dir=off"],
            cwd=hf_dir, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if ren.returncode == 0 and os.path.exists(raw_render) and os.path.getsize(raw_render) > 200000:
            break
        last_err = ren.stdout[-400:] + "\n" + ren.stderr[-700:]
    else:
        raise RuntimeError(f"Render failed on #{sp['idx']} ({style_name}): {last_err}")

    master_mp4 = os.path.join(hf_dir, "_v3_14lufs.mp4")
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_render,
            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", "30", "-g", "30",
            "-af", "highpass=f=70,loudnorm=I=-14:TP=-1.2:LRA=11",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart",
            master_mp4,
        ],
        check=True, capture_output=True
    )

    qc_dir = os.path.join(BASE_DIR, "_qc_14_styles")
    os.makedirs(qc_dir, exist_ok=True)
    # Capture Hook EdgeSweep frame + Finale/Hologram frame for visual QC!
    fin_t = round(max(4.8, plan["dur"] - 1.45), 2)
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "0.55", "-i", master_mp4, "-frames:v", "1", "-q:v", "3", os.path.join(qc_dir, f"v4_hook_{sp['idx']:02d}.jpg")],
        capture_output=True
    )
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{fin_t:.2f}", "-i", master_mp4, "-frames:v", "1", "-q:v", "3", os.path.join(qc_dir, f"v3_{sp['idx']:02d}.jpg")],
        capture_output=True
    )

    final_name = sp["final_name"]
    for folder in [DEST_HTPM_DIR, DEST_LOCAL_DIR, DEST_MASTER_DIR]:
        os.makedirs(folder, exist_ok=True)
        shutil.copy2(master_mp4, os.path.join(folder, final_name))

    du_an_v = os.path.join(DU_AN_ROOT, sp["slug"])
    os.makedirs(os.path.join(du_an_v, "compositions"), exist_ok=True)
    shutil.copy2(os.path.join(hf_dir, "index.html"), os.path.join(du_an_v, "index.html"))
    shutil.copy2(os.path.join(hf_dir, "compositions", "presenter-stage.html"), os.path.join(du_an_v, "compositions", "presenter-stage.html"))

    mb = round(os.path.getsize(os.path.join(DEST_HTPM_DIR, final_name)) / (1024 * 1024), 2)
    for tmp_f in [raw_render, master_mp4]:
        if os.path.exists(tmp_f):
            try:
                os.remove(tmp_f)
            except Exception:
                pass
    print(f"[V3 DELIVERED #{sp['idx']:02d}] [{style_name}] (0% BGM, 0px shift, 0% occlusion) -> {final_name} ({mb} MB)", flush=True)


def build_qc_showcase():
    import cv2
    import numpy as np
    qc_dir = os.path.join(BASE_DIR, "_qc_14_styles")
    thumbs = []
    for i in range(1, 15):
        p = os.path.join(qc_dir, f"v3_{i:02d}.jpg")
        if os.path.exists(p):
            im = cv2.imread(p)
            im = cv2.resize(im, (270, 480))
            cv2.putText(im, f"#{i:02d}", (12, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)
            thumbs.append(im)
    if len(thumbs) == 14:
        grid = np.vstack([np.hstack(thumbs[:7]), np.hstack(thumbs[7:])])
        out_p = os.path.join(qc_dir, "14_videos_v3_behind_qc.jpg")
        cv2.imwrite(out_p, grid, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        print("Saved QC showcase:", out_p, flush=True)


def main():
    wanted = [int(x) for x in sys.argv[1:] if x.isdigit()]
    all_specs = get_adjusted_specs()
    targets = [s for s in all_specs if (not wanted or s["idx"] in wanted)]

    for sp in targets:
        vdir = os.path.join(BASE_DIR, sp["slug"])
        clean_json = os.path.join(vdir, "raw_assets", f"v{sp['idx']:02d}_clean_words.json")
        hf_dir = os.path.join(vdir, "hf_project")
        with open(clean_json, "r", encoding="utf-8") as f:
            wdata = json.load(f)

        plan = plan_timings(sp, wdata)
        plan["head_top_y"] = wdata.get("head_top_y", 360)
        style_name = write_v3_project(sp, plan, hf_dir)
        render_and_deliver_v3(sp, plan, hf_dir, style_name)

    build_qc_showcase()


if __name__ == "__main__":
    main()
