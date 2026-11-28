# -*- coding: utf-8 -*-
"""
Hậu kỳ gọn sạch, chuẩn chỉnh 100% cho 6 Video nói trực tiếp của Chị Hậu (Video 1, 2, 4, 5, 6, 7):
- Giữ 100% tiếng nói gốc có khẩu hình (lip-sync) của Chị Hậu từ 3 Cảnh (chuẩn hóa -15 LUFS + micro-fade êm, 0% Voiceover rời, 0% khung quảng cáo USP)
- Chèn đúng Chữ mở đầu (3.2s đầu) + đúng các dòng chữ / đồ họa kiến thức được chỉ định trong từng kịch bản (nằm gọn trong Vùng An Toàn 9:16, không che mặt Chị Hậu)
- Xuất bảng kiểm QC từng cảnh + kiểm âm faster-whisper + đồng bộ thẳng lên Google Drive An Vượng ngày 27/11/2026!
"""
import json, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import faster_whisper

SERIES_DIR = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Series_7_Video_Kien_Thuc_Chi_Hau")
FINAL_ALL_DIR = SERIES_DIR / "Final_All_7_Videos_MP4"
FINAL_ALL_DIR.mkdir(parents=True, exist_ok=True)
DRIVE_DIR = Path(r"G:\My Drive\dự án ngoài\An Vượng\03. Video Hoàn Thiện\261127 - Ngày 27.11.2026")
DRIVE_DIR.mkdir(parents=True, exist_ok=True)

FONTS_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
F_BOLD = str(FONTS_DIR / "BeVietnamPro-Bold.ttf")
F_XBOLD = str(FONTS_DIR / "BeVietnamPro-ExtraBold.ttf")

CONFIGS = [
    {
        "vid": "V01_An_Du_Dam_Giam_Can",
        "out_name": "261127 AVPM Chi Hau 01 - An Du Dam Giup Giam Can De Hon final.mp4",
        "open_l1": "ĂN ÍT ĐI",
        "open_l2": "MÀ CỨ NHANH ĐÓI?",
        # Cận cảnh bữa sáng với chữ “Bữa này có món gì giàu đạm?” ở Cảnh 3
        "scene_cards": [
            (3, "Bữa này có món gì giàu đạm?", None),
        ],
    },
    {
        "vid": "V02_Giam_2_Ky_Thay_Doi_Gi",
        "out_name": "261127 AVPM Chi Hau 02 - Giam 2 Ky Minh Da Giam Gi final.mp4",
        "open_l1": "GIẢM 2 KÝ,",
        "open_l2": "MÌNH ĐÃ GIẢM GÌ?",
        "scene_cards": [],
    },
    {
        "vid": "V04_It_Uong_Sua_Tim_Canxi",
        "out_name": "261127 AVPM Chi Hau 04 - It Uong Sua Tim Canxi O Dau final.mp4",
        "open_l1": "CANXI TRONG BỮA CƠM",
        "open_l2": "CÓ Ở ĐÂU?",
        # Cảnh 2: Chèn chữ “Canxi · mg mỗi khẩu phần”
        "scene_cards": [
            (2, "Canxi · mg mỗi khẩu phần", None),
        ],
    },
    {
        "vid": "V05_Mot_Goi_1000mg_La_Gi",
        "out_name": "261127 AVPM Chi Hau 05 - Thay 1000mg Hay Doc Them 1 Dong final.mp4",
        "open_l1": "THẤY 1.000 MG,",
        "open_l2": "HÃY ĐỌC THÊM 1 DÒNG",
        # Cảnh 2: Đồ họa “1.000 mg canxi carbonat → khoảng 400 mg canxi nguyên tố” | Cảnh 3: “Kiểm tra khẩu phần”
        "scene_cards": [
            (2, "1.000 mg canxi carbonat", "→ khoảng 400 mg canxi nguyên tố"),
            (3, "Kiểm tra khẩu phần", None),
        ],
    },
    {
        "vid": "V06_Collagen_Va_Vitamin_C",
        "out_name": "261127 AVPM Chi Hau 06 - Qua Oi Lien Quan Gi Den Collagen final.mp4",
        "open_l1": "QUẢ ỔI LIÊN QUAN GÌ",
        "open_l2": "ĐẾN COLLAGEN?",
        # Chèn chữ “Vitamin C tham gia tạo collagen”
        "scene_cards": [
            (2, "Vitamin C tham gia tạo collagen", None),
        ],
    },
    {
        "vid": "V07_Bot_Nghe_Va_Curcumin",
        "out_name": "261127 AVPM Chi Hau 07 - Cung Ghi Nghe Con So Noi Ve Gi final.mp4",
        "open_l1": "CÙNG GHI “NGHỆ”,",
        "open_l2": "CON SỐ ĐANG NÓI VỀ GÌ?",
        # Cảnh 2: Hai bảng chữ “Bột nghệ” và “Chiết xuất nghệ” | Cảnh 3: “Tên nguyên liệu · Hàm lượng · Khẩu phần”
        "scene_cards": [
            (2, "Bột nghệ   |   Chiết xuất nghệ", "Cùng 500 mg nhưng khác nguyên liệu"),
            (3, "Tên nguyên liệu · Hàm lượng · Khẩu phần", None),
        ],
    },
]


def make_overlay_png(out_png: Path, line1: str, line2: str = None, is_opening: bool = False):
    ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    dr = ImageDraw.Draw(ov)

    if is_opening:
        f1 = ImageFont.truetype(F_XBOLD, 46)
        f2 = ImageFont.truetype(F_XBOLD, 52)
        box = (58, 1260, 862, 1438)
        sd.rounded_rectangle(box, radius=26, fill=(20, 30, 24, 184))
        ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(1.5)))
        dr = ImageDraw.Draw(ov)
        dr.rounded_rectangle(box, radius=26, outline=(255, 248, 230, 95), width=2)
        dr.text((86, 1280), line1, font=f1, fill=(255, 255, 255, 255))
        dr.text((86, 1346), line2 or "", font=f2, fill=(255, 228, 132, 255))
    else:
        f1 = ImageFont.truetype(F_XBOLD, 34)
        f2 = ImageFont.truetype(F_BOLD, 30)
        box = (58, 1320, 862, 1468 if line2 else 1418)
        sd.rounded_rectangle(box, radius=22, fill=(20, 30, 24, 186))
        ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(1.5)))
        dr = ImageDraw.Draw(ov)
        dr.rounded_rectangle(box, radius=22, outline=(255, 232, 150, 110), width=2)
        dr.text((84, 1342), line1, font=f1, fill=(255, 234, 148, 255))
        if line2:
            dr.text((84, 1396), line2, font=f2, fill=(255, 255, 255, 255))

    ov.save(out_png)


def assemble_one(cfg: dict, asr):
    vdir = SERIES_DIR / cfg["vid"]
    raw_dir = vdir / "01_Raw_Scenes"
    work_dir = vdir / "02_Work"
    work_dir.mkdir(parents=True, exist_ok=True)

    norm_parts, durs = [], []
    for i in (1, 2, 3):
        sp = raw_dir / f"scene_0{i}.mp4"
        assert sp.exists(), f"Missing {sp}"
        dur = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(sp)
        ], text=True).strip())
        durs.append(dur)
        np_out = work_dir / f"norm_0{i}.mp4"
        af = f"highpass=f=80,loudnorm=I=-15:TP=-1.5:LRA=9,afade=t=in:st=0:d=0.04,afade=t=out:st={max(0.1, dur-0.06):.3f}:d=0.06"
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,format=yuv420p"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(sp),
            "-vf", vf, "-af", af,
            "-c:v", "libx264", "-crf", "17", "-preset", "fast",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
            str(np_out)
        ], check=True)
        norm_parts.append(np_out)

    concat_txt = work_dir / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.name}'" for p in norm_parts), encoding="utf-8")
    joined = work_dir / "joined.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(joined)], check=True)

    # Build overlay PNGs (Opening title + optional script-specified scene cards)
    open_png = work_dir / "ov_open.png"
    make_overlay_png(open_png, cfg["open_l1"], cfg["open_l2"], is_opening=True)

    overlays = [(open_png, 0.12, 3.35)]
    sc_starts = [0.0, durs[0], durs[0] + durs[1]]
    for idx_c, (sc_no, l1, l2) in enumerate(cfg["scene_cards"], 1):
        c_png = work_dir / f"ov_card_{idx_c}.png"
        make_overlay_png(c_png, l1, l2, is_opening=False)
        st = round(sc_starts[sc_no - 1] + 0.65, 2)
        en = round(sc_starts[sc_no - 1] + durs[sc_no - 1] - 0.55, 2)
        overlays.append((c_png, st, en))

    inputs = ["-i", str(joined)]
    fc_parts = []
    prev_lbl = "0:v"
    for k, (png_p, st, en) in enumerate(overlays, 1):
        du = round(en - st, 2)
        inputs += ["-loop", "1", "-t", f"{en + 0.3:.2f}", "-i", str(png_p)]
        ov_lbl = f"ov{k}"
        nxt_lbl = f"v{k}"
        fc_parts.append(
            f"[{k}:v]format=rgba,fade=t=in:st={st:.2f}:d=0.25:alpha=1,fade=t=out:st={max(st+0.3, en-0.30):.2f}:d=0.30:alpha=1[{ov_lbl}];"
            f"[{prev_lbl}][{ov_lbl}]overlay=0:0:enable='between(t,{st:.2f},{en:.2f})':eof_action=pass[{nxt_lbl}]"
        )
        prev_lbl = nxt_lbl

    fc_str = ";".join(fc_parts) + f";[{prev_lbl}]format=yuv420p[vout]"
    out_mp4 = FINAL_ALL_DIR / cfg["out_name"]
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex", fc_str,
        "-map", "[vout]", "-map", "0:a",
        "-c:v", "libx264", "-crf", "17", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(out_mp4)
    ], check=True)

    shutil.copy2(out_mp4, DRIVE_DIR / out_mp4.name)

    tmp_w = work_dir / "_asr.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out_mp4), "-vn", "-ac", "1", "-ar", "16000", str(tmp_w)], check=True)
    heard = " ".join(s.text.strip() for s in asr.transcribe(str(tmp_w), language="vi")[0])
    tmp_w.unlink(missing_ok=True)
    tot = sum(durs)
    print(f"[DONE {cfg['vid']}] {tot:.1f}s -> {out_mp4.name}\n  WHISPER: {heard}\n", flush=True)
    return out_mp4, durs


def main():
    asr = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")
    # Also copy Video 3 into DRIVE_DIR (27/11) so all 7 videos sit together cleanly!
    v3_src = SERIES_DIR / "V03_An_Chay_Nguon_Dam" / "05_Final_Video" / "261126 AVPM Chi Hau 03 - Mam Com Chay Nay Dam O Dau final.mp4"
    if v3_src.exists():
        v3_dst_name = "261127 AVPM Chi Hau 03 - Mam Com Chay Nay Dam O Dau final.mp4"
        shutil.copy2(v3_src, FINAL_ALL_DIR / v3_dst_name)
        shutil.copy2(v3_src, DRIVE_DIR / v3_dst_name)

    qc_rows = []
    for cfg in CONFIGS:
        mp4, durs = assemble_one(cfg, asr)
        qc_rows.append((cfg["vid"], mp4, durs))

    # Build Master 6x3 QC Contact Sheet (all 18 scenes across the 6 new videos!)
    tw, th = 250, 444
    sheet = Image.new("RGB", (6 * (tw + 10) + 10, 3 * (th + 28) + 10), (18, 22, 18))
    dr = ImageDraw.Draw(sheet)
    tmp_f = SERIES_DIR / "_tmp_qcf.png"
    for col_i, (vid, mp4, durs) in enumerate(qc_rows):
        t_points = [1.2, round(durs[0] + 1.8, 1), round(durs[0] + durs[1] + 1.8, 1)]
        for row_i, ts in enumerate(t_points):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(mp4), "-frames:v", "1", str(tmp_f)], check=True)
            im = Image.open(tmp_f).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
            x, y = 10 + col_i * (tw + 10), 10 + row_i * (th + 28)
            sheet.paste(im, (x, y))
            dr.text((x + 4, y + th + 5), f"{vid[:3]} C{row_i+1} @{ts}s", fill=(175, 255, 195))
    tmp_f.unlink(missing_ok=True)
    qc_out = FINAL_ALL_DIR / "QC_6_Videos_Chi_Hau_18_Scenes.jpg"
    sheet.save(qc_out, quality=92)
    shutil.copy2(qc_out, DRIVE_DIR / qc_out.name)
    print("[MASTER QC READY]", qc_out)


if __name__ == "__main__":
    main()
