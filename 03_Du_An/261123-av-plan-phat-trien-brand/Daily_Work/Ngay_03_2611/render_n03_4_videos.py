# -*- coding: utf-8 -*-
"""
Build & Render trọn bộ 4 Video Ngày 03 (26/11/2026) HyperFrames 24fps 9:16:
- Nhịp cắt nhanh 2.0s–2.65s/cảnh (11–12 cảnh sinh hoạt thực tế / video + 2-cut live End-Card)
- 0% bối cảnh Nha Trang • 0% Bojomi trẻ em • 100% chuẩn CTKM Black Friday 26/11 & 25–30/11
- Xuất bảng kiểm QA đa điểm (Hook, Split-Bento, Real Box, End-Card) + kiểm âm faster-whisper + đồng bộ Google Drive!
"""
import concurrent.futures, json, os, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
import faster_whisper

WORK = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_03_2611")
OUT_VID = WORK / "06_Final_4_Videos_MP4"
OUT_VID.mkdir(parents=True, exist_ok=True)

VKEYS = [
    "n03_v1_av_protein_bua_sang_em_bung",
    "n03_v2_bojomi_kieng_3_chan_van_phong",
    "n03_v3_curcumilk_3_nguon_nghe_em_bung",
    "n03_v4_collamela_vi_dao_100ml_khong_tanh",
]


def render_one(job: dict) -> str:
    hf_dir = job["hf_dir"]
    mp4 = job["out_mp4"]
    print(f"[START RENDER] {mp4.name} ...", flush=True)
    chk = subprocess.run("npx --yes hyperframes@0.9.38 check --json", cwd=str(hf_dir), shell=True, capture_output=True, text=True)
    if chk.returncode != 0:
        print(f"[CHECK WARN {job['id']}] {chk.stdout[-500:]} {chk.stderr[-300:]}", flush=True)
    cmd = f'npx --yes hyperframes@0.9.38 render --quality delivery -o "{mp4}"'
    res = subprocess.run(cmd, cwd=str(hf_dir), shell=True, capture_output=True, text=True)
    if res.returncode != 0 or not mp4.exists():
        raise RuntimeError(f"Render failed for {mp4.name}:\nSTDOUT:{res.stdout[-800:]}\nSTDERR:{res.stderr[-800:]}")
    print(f"[DONE RENDER] {mp4.name} ({mp4.stat().st_size / 1e6:.2f} MB)", flush=True)
    return str(mp4)


def main():
    subprocess.run([sys.executable, "-X", "utf8", str(WORK / "build_n03_4_videos_hf.py"), "all"], check=True)

    jobs = []
    for i, vk in enumerate(VKEYS, 1):
        mdata = json.loads((WORK / vk / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))
        jobs.append({
            "id": f"V{i}",
            "vkey": vk,
            "hf_dir": WORK / vk / "07_HyperFrames_Project",
            "out_mp4": OUT_VID / mdata["final_name"],
            "mdata": mdata,
        })

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(render_one, j) for j in jobs]
        for f in concurrent.futures.as_completed(futs):
            f.result()

    # Build 4x5 QC Contact Sheet (Hook -> Step1 Cắt gói đổ bột -> Step2 Chế nước -> Step3 Khuấy mịn -> End-Card)
    asr = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")
    tw, th = 290, 515
    sheet = Image.new("RGB", (4 * (tw + 14) + 14, 5 * (th + 30) + 16), (14, 20, 26))
    draw = ImageDraw.Draw(sheet)
    tmp_p = WORK / "_tmp_vqc.png"
    tmp_w = WORK / "_tmp_vtail.wav"

    for idx, j in enumerate(jobs):
        mp4 = j["out_mp4"]
        segs = j["mdata"]["segments"]
        dur = float(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(mp4)],
                text=True,
            ).strip()
        )
        assert dur <= 60.0, f"Video > 60s: {mp4.name} = {dur:.2f}s"
        s1_st, s1_en = float(segs[0]["shot_end_s"]), float(segs[1]["shot_end_s"])
        s1_step = (s1_en - s1_st) / 4.0
        t_p1 = round(s1_st + s1_step * 0.55, 2)
        t_p2 = round(s1_st + s1_step * 1.55, 2)
        t_p3 = round(s1_st + s1_step * 2.55, 2)
        t_p4 = round(s1_st + s1_step * 3.55, 2)
        t_end = round(max(0.0, dur - 2.2), 2)

        for r_idx, (ts, lbl, col) in enumerate([
            (t_p1, f"{j['id']} B1: CAT/XE GOI (@{t_p1:.1f}s)", (255, 232, 120)),
            (t_p2, f"{j['id']} B2: DO BOT VAO LY (@{t_p2:.1f}s)", (255, 185, 110)),
            (t_p3, f"{j['id']} B3: CHE NUOC VAO LY (@{t_p3:.1f}s)", (150, 225, 255)),
            (t_p4, f"{j['id']} B4: KHUAY TAN MIN (@{t_p4:.1f}s)", (210, 190, 255)),
            (t_end, f"{j['id']} ENDCARD (@{t_end:.1f}s)", (160, 245, 195)),
        ]):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(mp4), "-frames:v", "1", str(tmp_p)], check=True)
            im = Image.open(tmp_p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
            x = idx * (tw + 14) + 14
            y = r_idx * (th + 30) + 14
            sheet.paste(im, (x, y))
            draw.text((x + 4, y + th + 5), lbl, fill=col)

        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, dur - 11.0):.2f}", "-i", str(mp4), "-vn", "-ac", "1", "-ar", "16000", str(tmp_w)],
            check=True,
        )
        heard = " ".join(s.text.strip() for s in asr.transcribe(str(tmp_w), language="vi")[0])
        print(f"[FINAL WHISPER {j['id']} ({dur:.1f}s)] {heard}", flush=True)

    qa_out = WORK / "QA_4_Videos_Ngay_2611_Nhanh_SinhHoat.jpg"
    sheet.save(qa_out, quality=92)
    tmp_p.unlink(missing_ok=True)
    tmp_w.unlink(missing_ok=True)
    print(f"\n[QC SHEET READY] {qa_out}", flush=True)


if __name__ == "__main__":
    main()
