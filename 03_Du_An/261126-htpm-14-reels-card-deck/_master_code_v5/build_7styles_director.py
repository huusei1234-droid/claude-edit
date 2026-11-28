# -*- coding: utf-8 -*-
"""
Master 7-Style Polymorphic HyperFrames Director (#02 -> #14):
Rebuilds #02..#06 AND builds #07..#14 so every single video in the 14-video HTPM series
has a genuinely distinct Talking-Head architecture from the user's studio repertoire!
"""
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
    prepare_presenter_and_rvm,
    transcribe_and_trim,
)
from styles_part1 import (
    build_style2_thv3_dualsplit,
    build_style3_kobe_light_pip,
    build_style4_kobe_dark_cyber,
)
from styles_part2 import (
    build_style5_callaway_split,
    build_style6_minimal_editorial,
    build_style7_medical_bento,
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

STYLE_DISPATCH = {
    2: ("STYLE_2_THV3_DUALSPLIT", build_style2_thv3_dualsplit, True),
    3: ("STYLE_3_KOBE_LIGHT_PIP", build_style3_kobe_light_pip, False),
    4: ("STYLE_4_KOBE_DARK_CYBER", build_style4_kobe_dark_cyber, True),
    5: ("STYLE_5_CALLAWAY_SPLIT", build_style5_callaway_split, True),
    6: ("STYLE_6_MINIMAL_EDITORIAL", build_style6_minimal_editorial, True),
    7: ("STYLE_7_MEDICAL_BENTO", build_style7_medical_bento, False),
    8: ("STYLE_7_MEDICAL_BENTO", build_style7_medical_bento, False),
    9: ("STYLE_6_MINIMAL_EDITORIAL", build_style6_minimal_editorial, True),
    10: ("STYLE_2_THV3_DUALSPLIT", build_style2_thv3_dualsplit, True),
    11: ("STYLE_7_MEDICAL_BENTO", build_style7_medical_bento, False),
    12: ("STYLE_4_KOBE_DARK_CYBER", build_style4_kobe_dark_cyber, True),
    13: ("STYLE_3_KOBE_LIGHT_PIP", build_style3_kobe_light_pip, False),
    14: ("STYLE_5_CALLAWAY_SPLIT", build_style5_callaway_split, True),
}


def prepare_presenter_only(raw_mp4: str, clean_dur: float, hf_dir: str):
    vid_dir = os.path.join(hf_dir, "assets", "videos")
    os.makedirs(vid_dir, exist_ok=True)
    pres_mp4 = os.path.join(vid_dir, "presenter.mp4")
    if not os.path.exists(pres_mp4) or os.path.getsize(pres_mp4) < 50000:
        vf = (
            "scale=1080:1920:flags=lanczos,format=rgb24,"
            "split[main][top];"
            "[top]crop=1080:64:0:0,vflip,gblur=sigma=8[topfill];"
            "[main]crop=1080:1856:0:0[body];"
            "[topfill][body]vstack=inputs=2,fps=30,format=yuv420p"
        )
        fade_out_st = max(0.5, round(clean_dur - 0.16, 2))
        af = f"afade=t=in:st=0:d=0.05,afade=t=out:st={fade_out_st}:d=0.15"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", raw_mp4, "-t", f"{clean_dur:.2f}",
                "-filter_complex", vf, "-af", af,
                "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-g", "30",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                pres_mp4,
            ],
            check=True, capture_output=True
        )


def stage_fonts_and_audio(hf_dir: str, bgm_file: str, sfx_cues: list):
    fdir = os.path.join(hf_dir, "assets", "fonts")
    adir = os.path.join(hf_dir, "assets", "audio")
    os.makedirs(fdir, exist_ok=True)
    os.makedirs(adir, exist_ok=True)

    # Copy Montserrat-Black from v01 + extra TVC fonts
    shutil.copy2(os.path.join(V01_HF, "assets", "fonts", "Montserrat-Black.ttf"), os.path.join(fdir, "Montserrat-Black.ttf"))
    for fn in NEEDED_FONTS:
        src = os.path.join(FONTS_SRC, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(fdir, fn))

    shutil.copy2(os.path.join(AUDIO_SRC, bgm_file), os.path.join(adir, bgm_file))
    shutil.copy2(os.path.join(V01_HF, "assets", "audio", "sfx_hook_pop.mp3"), os.path.join(adir, "sfx_hook_pop.mp3"))
    for sfx_fn, _, _ in sfx_cues:
        s_path = os.path.join(AUDIO_SRC, sfx_fn)
        if os.path.exists(s_path):
            shutil.copy2(s_path, os.path.join(adir, sfx_fn))


def write_bespoke_project(sp: dict, plan: dict, hf_dir: str):
    style_name, builder_fn, _ = STYLE_DISPATCH[sp["idx"]]
    scene_html, bgm_file, sfx_cues = builder_fn(sp, plan)

    os.makedirs(os.path.join(hf_dir, "compositions"), exist_ok=True)
    # Remove old unused composition files so hyperframes check stays 100% clean
    for old_f in os.listdir(os.path.join(hf_dir, "compositions")):
        if old_f != "presenter-stage.html":
            try:
                os.remove(os.path.join(hf_dir, "compositions", old_f))
            except Exception:
                pass

    shutil.copy2(os.path.join(V01_HF, "hyperframes.json"), os.path.join(hf_dir, "hyperframes.json"))
    stage_fonts_and_audio(hf_dir, bgm_file, sfx_cues)

    with open(os.path.join(hf_dir, "compositions", "presenter-stage.html"), "w", encoding="utf-8") as f:
        f.write(scene_html)

    dur = plan["dur"]
    sfx_tags = [
        f'      <audio id="sfx-hook-0" class="clip" src="assets/audio/sfx_hook_pop.mp3" data-start="0.04" data-duration="0.14" data-track-index="3" data-volume="0.30"></audio>'
    ]
    for i, (sfx_fn, st, vol) in enumerate(sfx_cues, 1):
        st_clamped = max(0.05, min(round(dur - 0.35, 2), round(st, 2)))
        tr_idx = 3 + (i % 2)
        sfx_tags.append(
            f'      <audio id="sfx-bespoke-{i}" class="clip" src="assets/audio/{sfx_fn}" '
            f'data-start="{st_clamped:.2f}" data-duration="0.28" data-track-index="{tr_idx}" data-volume="{vol:.2f}" data-fade-out="0.08"></audio>'
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
      html, body, #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0b0f17; }}
      .scene-host {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.2f}" data-width="1080" data-height="1920" data-fps="30">
      <div id="presenter-stage" class="scene-host" data-composition-id="presenter-stage" data-composition-src="compositions/presenter-stage.html" data-start="0" data-duration="{dur:.2f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <audio id="bgm-main" class="clip" src="assets/audio/{bgm_file}" data-start="0" data-duration="{dur:.2f}" data-track-index="2" data-volume="0.18" data-fade-in="0.20" data-fade-out="0.60"></audio>
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


def render_bespoke_and_deliver(sp: dict, plan: dict, hf_dir: str, style_name: str):
    chk = subprocess.run([HF_BIN, "check", "--json"], cwd=hf_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
    j_start = chk.stdout.find("{")
    if j_start >= 0:
        d = json.loads(chk.stdout[j_start:])
        errs = [x for x in d.get("diagnostics", []) if x.get("severity") == "error"]
        if errs:
            raise RuntimeError(f"Lint errors on #{sp['idx']} ({style_name}): {errs}")

    raw_render = os.path.join(hf_dir, "_bespoke_raw.mp4")
    last_err = ""
    for attempt in range(1, 3):
        ren = subprocess.run(
            [HF_BIN, "render", "--output", raw_render, "--fps", "30", "--low-memory-mode", "--frames-cache-dir=off"],
            cwd=hf_dir, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if ren.returncode == 0 and os.path.exists(raw_render) and os.path.getsize(raw_render) > 200000:
            break
        last_err = ren.stdout[-400:] + "\n" + ren.stderr[-700:]
    else:
        raise RuntimeError(f"Render failed on #{sp['idx']} ({style_name}): {last_err}")

    master_mp4 = os.path.join(hf_dir, "_bespoke_14lufs.mp4")
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

    # Save a representative mid-video style frame for our 14-video visual QC sheet!
    qc_dir = os.path.join(BASE_DIR, "_qc_14_styles")
    os.makedirs(qc_dir, exist_ok=True)
    mid_t = round(min(plan["dur"] - 1.5, max(5.2, plan["hook_end"] + 2.6)), 2)
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{mid_t:.2f}", "-i", master_mp4, "-frames:v", "1", "-q:v", "3", os.path.join(qc_dir, f"v{sp['idx']:02d}_{style_name}.jpg")],
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
    for tmp_f in [raw_render, master_mp4, os.path.join(hf_dir, "assets", "videos", "_presenter_matte.mp4")]:
        if os.path.exists(tmp_f):
            try:
                os.remove(tmp_f)
            except Exception:
                pass
    print(f"[BESPOKE DELIVERED #{sp['idx']:02d}] [{style_name}] -> {final_name} ({mb} MB)", flush=True)


def main():
    wanted = [int(x) for x in sys.argv[1:] if x.isdigit()]
    targets = [s for s in VIDEOS_SPEC if (not wanted or s["idx"] in wanted)]

    for sp in targets:
        style_name, _, _ = STYLE_DISPATCH[sp["idx"]]
        vdir = os.path.join(BASE_DIR, sp["slug"])
        clean_words_json = os.path.join(vdir, "raw_assets", f"v{sp['idx']:02d}_clean_words.json")
        fallback_words_json = os.path.join(vdir, "raw_assets", f"v{sp['idx']:02d}_words.json")
        hf_dir = os.path.join(vdir, "hf_project")

        print(f"=== DIRECTING #{sp['idx']:02d} [{style_name}]: {sp['slug']} ===", flush=True)
        wpath = clean_words_json if os.path.exists(clean_words_json) else fallback_words_json
        with open(wpath, "r", encoding="utf-8") as f:
            wdata = json.load(f)

        plan = plan_timings(sp, wdata)
        plan["head_top_y"] = wdata.get("head_top_y", 410)
        plan["splice_t"] = wdata.get("splice_t")
        write_bespoke_project(sp, plan, hf_dir)
        render_bespoke_and_deliver(sp, plan, hf_dir, style_name)


if __name__ == "__main__":
    main()
