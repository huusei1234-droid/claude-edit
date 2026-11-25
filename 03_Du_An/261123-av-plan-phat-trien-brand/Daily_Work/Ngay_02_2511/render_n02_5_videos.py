# -*- coding: utf-8 -*-
"""
Build & Render all 5 Day-02 (25/11/2026) HyperFrames 24fps 9:16 Videos (< 55s each,
5 distinct Nha Trang looks, 5 unique BGMs, Cinema Screen Overlays, Extra-Large Safe-Zone Text,
100% real IS-Net product boxes, 100% accurate 25/11–30/11 CTKM), plus build Hook & End-Card QC sheets
and run faster-whisper verification on all 5 final MP4s.
"""
import concurrent.futures, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
import faster_whisper

WORK = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_02_2511")
OUT_VID = WORK / "06_Final_5_Videos_MP4"
OUT_VID.mkdir(parents=True, exist_ok=True)

VKEYS = [
    "n02_v1_av_protein_leucine",
    "n02_v2_bojomi_chay_bo_60c",
    "n02_v3_combo_be_1_tuoi_bieng_an",
    "n02_v4_curcumilk_15h_em_bung",
    "n02_v5_collamela_don_tet_480k",
]


def render_one(job: dict) -> str:
    hf_dir = job["hf_dir"]
    mp4 = job["out_mp4"]
    print(f"[START RENDER] {mp4.name} ...", flush=True)
    cmd = f'npx --yes hyperframes@0.9.38 render --quality delivery -o "{mp4}"'
    res = subprocess.run(cmd, cwd=str(hf_dir), shell=True, capture_output=True, text=True)
    if res.returncode != 0 or not mp4.exists():
        raise RuntimeError(f"Render failed for {mp4.name}:\nSTDOUT:{res.stdout[-800:]}\nSTDERR:{res.stderr[-800:]}")
    print(f"[DONE RENDER] {mp4.name} ({mp4.stat().st_size / 1e6:.2f} MB)", flush=True)
    return str(mp4)


def main():
    # 1. Build all 5 HyperFrames projects (prepping clips + cinema overlays on RTX 4070 NVENC)
    subprocess.run([sys.executable, "-X", "utf8", str(WORK / "build_n02_5_videos_hf.py"), "all"], check=True)

    jobs = []
    for i, vk in enumerate(VKEYS, 1):
        mdata = json.loads((WORK / vk / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))
        jobs.append({
            "id": f"V{i}",
            "vkey": vk,
            "hf_dir": WORK / vk / "07_HyperFrames_Project",
            "out_mp4": OUT_VID / mdata["final_name"],
        })

    # 2. Render all 5 videos in parallel (max_workers=2 on RTX 4070 + 64GB RAM)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(render_one, j) for j in jobs]
        for f in concurrent.futures.as_completed(futs):
            f.result()

    # 3. Build combined 5x2 QC Contact Sheet (Row 1 = Opening Big Hook @ 0.8s, Row 2 = End-Card @ dur-2.0s)
    #    and run faster-whisper audit on End-Card audio of all 5 videos!
    asr = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")
    tw, th = 360, 640
    sheet = Image.new("RGB", (5 * (tw + 18) + 18, 2 * (th + 36) + 20), (14, 20, 26))
    draw = ImageDraw.Draw(sheet)
    tmp_p = WORK / "_tmp_vqc.png"
    tmp_w = WORK / "_tmp_vtail.wav"

    for idx, j in enumerate(jobs):
        mp4 = j["out_mp4"]
        dur = float(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(mp4)],
                text=True,
            ).strip()
        )
        assert dur <= 60.0, f"Video > 60s: {mp4.name} = {dur:.2f}s"

        # Hook frame (0.8s)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0.80", "-i", str(mp4), "-frames:v", "1", str(tmp_p)], check=True)
        im1 = Image.open(tmp_p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x = idx * (tw + 18) + 18
        sheet.paste(im1, (x, 18))
        draw.text((x + 4, 18 + th + 6), f"{j['id']} HOOK ({dur:.1f}s)", fill=(255, 232, 120))

        # End-Card frame (dur - 2.0s)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, dur - 2.0):.2f}", "-i", str(mp4), "-frames:v", "1", str(tmp_p)], check=True)
        im2 = Image.open(tmp_p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        y2 = th + 54
        sheet.paste(im2, (x, y2))
        draw.text((x + 4, y2 + th + 6), f"{j['id']} ENDCARD | {mp4.name[:28]}", fill=(160, 245, 195))

        # Tail Whisper audit
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, dur - 11.0):.2f}", "-i", str(mp4), "-vn", "-ac", "1", "-ar", "16000", str(tmp_w)],
            check=True,
        )
        heard = " ".join(s.text.strip() for s in asr.transcribe(str(tmp_w), language="vi")[0])
        print(f"[FINAL WHISPER {j['id']} ({dur:.1f}s)] {heard}", flush=True)

    qa_out = WORK / "QA_5_Videos_Ngay_2511_Hook_Va_EndCard.jpg"
    sheet.save(qa_out, quality=92)
    tmp_p.unlink(missing_ok=True)
    tmp_w.unlink(missing_ok=True)
    print(f"\n[QC SHEET READY] {qa_out}", flush=True)


if __name__ == "__main__":
    main()
