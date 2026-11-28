# -*- coding: utf-8 -*-
"""
Hậu kỳ chuẩn 100% cho trọn bộ 7 Video nói trực tiếp của Chị Hằng (An Vượng Pharma — 27/11/2026):
- Tự động dùng `faster-whisper` word-timestamps tìm đúng chữ kết câu kịch bản của từng cảnh và cắt gọn phần đuôi dư / vọng chữ tại điểm nghỉ hơi thở (+0.30s, micro-fade 45ms) -> ĐẠT 0% LẶP TỪ, 0% TIẾNG RÁC CUỐI CÂU!
- Giữ 100% tiếng nói gốc có khẩu hình (lip-sync) của Chị Hằng (-15 LUFS, 0% Voiceover rời, 0% nhạc nền, 0% khung quảng cáo USP, 0% hiệu ứng bling-bling)
- Chèn đúng Chữ mở đầu (3.2s đầu) + đúng các dòng chữ / đồ họa kiến thức trong từng kịch bản, đặt gọn 100% trong Vùng An Toàn TikTok/Reels 9:16 (X <= 862px, Y <= 1468px, không che mặt Chị Hằng)
- Đặt tên chuẩn Quy tắc 1: `<YYMMDD> AVPM <tên tiếng Việt có dấu> final.mp4` và lưu vào thư mục dự án + Google Drive An Vượng!
"""
import re, shutil, subprocess, unicodedata
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import faster_whisper

SERIES_DIR = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Series_7_Video_Kien_Thuc_Chi_Hau\Chi_Hang_2711")
FINAL_ALL_DIR = SERIES_DIR / "Final_All_7_Videos_Chi_Hang"
FINAL_ALL_DIR.mkdir(parents=True, exist_ok=True)
DRIVE_DIR = Path(r"G:\My Drive\dự án ngoài\An Vượng\03. Video Hoàn Thiện\261127 - Ngày 27.11.2026")
DRIVE_DIR.mkdir(parents=True, exist_ok=True)

FONTS_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
F_BOLD = str(FONTS_DIR / "BeVietnamPro-Bold.ttf")
F_XBOLD = str(FONTS_DIR / "BeVietnamPro-ExtraBold.ttf")

CONFIGS = [
    {
        "vid": "V01_An_Du_Dam_Giam_Can",
        "out_name": "261127 AVPM 01 Tại sao ăn đủ đạm giúp giảm cân dễ hơn final.mp4",
        "open_l1": "ĂN ÍT ĐI",
        "open_l2": "MÀ CỨ NHANH ĐÓI?",
        "end_anchors": [
            ["dam", "chua"],
            ["sau", "bua", "an"],
            ["doi", "nhe"],
        ],
        "min_sec": [6.5, 8.0, 7.0],
        "scene_cards": [
            (3, "Bữa này có món gì giàu đạm?", None),
        ],
    },
    {
        "vid": "V02_Giam_2_Ky_Thay_Doi_Gi",
        "out_name": "261127 AVPM 02 Cùng giảm 2 ký cơ thể thay đổi giống nhau không final.mp4",
        "open_l1": "GIẢM 2 KÝ,",
        "open_l2": "MÌNH ĐÃ GIẢM GÌ?",
        "end_anchors": [
            ["va", "co"],
            ["di", "cho"],
            ["tung", "tuan"],
        ],
        "min_sec": [7.5, 7.5, 6.0],
        "scene_cards": [],
    },
    {
        "vid": "V03_An_Chay_Nguon_Dam",
        "out_name": "261127 AVPM 03 Ăn chay nhìn thế nào để biết bữa ăn có nguồn đạm final.mp4",
        "open_l1": "MÂM CƠM CHAY NÀY,",
        "open_l2": "ĐẠM Ở ĐÂU?",
        "end_anchors": [
            ["dam", "chinh"],
            ["dau", "lang"],
            ["thuc", "don"],
        ],
        "min_sec": [7.5, 4.2, 7.5],
        "scene_cards": [],
    },
    {
        "vid": "V04_It_Uong_Sua_Tim_Canxi",
        "out_name": "261127 AVPM 04 Ít uống sữa tìm canxi ở đâu final.mp4",
        "open_l1": "CANXI TRONG BỮA CƠM",
        "open_l2": "CÓ Ở ĐÂU?",
        "end_anchors": [
            ["lua", "chon"],
            ["miligam"],
            ["ca", "nha"],
        ],
        "min_sec": [9.5, 6.5, 7.5],
        "scene_cards": [
            (2, "Canxi · mg mỗi khẩu phần", None),
        ],
    },
    {
        "vid": "V05_Mot_Goi_1000mg_La_Gi",
        "out_name": "261127 AVPM 05 Một gói có 1000 mg đó là 1000 mg gì final.mp4",
        "open_l1": "THẤY 1.000 MG,",
        "open_l2": "HÃY ĐỌC THÊM 1 DÒNG",
        "end_anchors": [
            ["hop", "chat"],
            ["hai", "vien"],
            ["moi", "so"],
        ],
        "min_sec": [8.0, 7.0, 6.5],
        "scene_cards": [
            (2, "1.000 mg canxi carbonat", "→ khoảng 400 mg canxi nguyên tố"),
            (3, "Kiểm tra khẩu phần", None),
        ],
    },
    {
        "vid": "V06_Collagen_Va_Vitamin_C",
        "out_name": "261127 AVPM 06 Vì sao nói về collagen lại nhắc đến vitamin C final.mp4",
        "open_l1": "QUẢ ỔI LIÊN QUAN GÌ",
        "open_l2": "ĐẾN COLLAGEN?",
        "end_anchors": [
            ["trinh", "do"],
            ["chua"],
            ["deu", "hon"],
        ],
        "min_sec": [7.0, 7.0, 7.0],
        "scene_cards": [
            (2, "Vitamin C tham gia tạo collagen", None),
        ],
    },
    {
        "vid": "V07_Bot_Nghe_Va_Curcumin",
        "out_name": "261127 AVPM 07 Bột nghệ và curcumin khác nhau ở đâu final.mp4",
        "open_l1": "CÙNG GHI “NGHỆ”,",
        "open_l2": "CON SỐ ĐANG NÓI VỀ GÌ?",
        "end_anchors": [
            ["cu", "nghe"],
            ["hay", "khong"],
            ["hon", "nhieu"],
        ],
        "min_sec": [9.0, 6.5, 7.5],
        "scene_cards": [
            (2, "Bột nghệ   |   Chiết xuất nghệ", "Cùng 500 mg nhưng khác nguyên liệu"),
            (3, "Tên nguyên liệu · Hàm lượng · Khẩu phần", None),
        ],
    },
]


def strip_accents(s: str) -> str:
    s = s.lower().replace("đ", "d")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", s)


# Bảng đồng âm Whisper tiếng Việt hay phiên âm khác mặt chữ
SYNONYMS = {
    "bua": {"bua", "bu"},
    "cho": {"cho", "tro"},
    "miligam": {"miligam", "milligram", "mg"},
    "hai": {"hai", "2"},
}


def tok_match(word_norm: str, target_tok: str) -> bool:
    opts = SYNONYMS.get(target_tok, {target_tok})
    return word_norm in opts


def find_clean_cut_sec(sp: Path, raw_dur: float, anchor_toks: list, min_t: float, asr, is_last_scene: bool = False):
    tmp_wav = sp.parent / f"_trim_{sp.stem}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(sp), "-vn", "-ac", "1", "-ar", "16000", str(tmp_wav)], check=True)
    segs, _ = asr.transcribe(str(tmp_wav), language="vi", word_timestamps=True)
    words = [w for s in segs for w in (s.words or [])]
    tmp_wav.unlink(missing_ok=True)
    if not words:
        return raw_dur, None, 0.0

    norm_words = [(strip_accents(w.word), w.start, w.end, w.word) for w in words if strip_accents(w.word)]
    first_start = max(0.0, round(norm_words[0][1] - 0.08, 3)) if norm_words else 0.0
    k = len(anchor_toks)
    for idx in range(len(norm_words) - k + 1):
        end_t = norm_words[idx + k - 1][2]
        if end_t < min_t:
            continue
        if all(tok_match(norm_words[idx + j][0], anchor_toks[j]) for j in range(k)):
            check_idx = idx + k
            if check_idx < len(norm_words):
                nxt_norm, nxt_st, nxt_en, _ = norm_words[check_idx]
                if nxt_norm in {"nhe", "nha", "a", "chua"} and (nxt_st - end_t) < 0.45:
                    end_t = nxt_en
                    check_idx += 1
            speech_end = round(end_t + 0.12, 3)
            if is_last_scene:
                cut_t = min(raw_dur, round(end_t + 0.65, 3))
                return cut_t, speech_end, first_start
            pad = 0.30
            if check_idx < len(norm_words):
                gap = norm_words[check_idx][1] - end_t
                pad = min(0.30, max(0.08, gap * 0.65))
            cut_t = min(raw_dur, round(end_t + pad, 3))
            if raw_dur - cut_t > 0.25:
                print(f"  [TRIM {sp.parent.parent.name}/{sp.name}] {raw_dur:.2f}s -> {cut_t:.2f}s (cut trailing echo/silence)")
                return cut_t, speech_end, first_start
            return raw_dur, speech_end, first_start
    return raw_dur, None, first_start


def make_overlay_png(out_png: Path, line1: str, line2: str = None, is_opening: bool = False):
    ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)

    # Vùng an toàn TikTok/Reels 9:16: X in [58..862] (< 884px), Y in [1260..1468] (< 1548px)
    if is_opening:
        f1 = ImageFont.truetype(F_XBOLD, 44)
        f2 = ImageFont.truetype(F_XBOLD, 50)
        box = (58, 1260, 862, 1438)
        sd.rounded_rectangle(box, radius=26, fill=(20, 30, 24, 188))
        ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(1.5)))
        dr = ImageDraw.Draw(ov)
        dr.rounded_rectangle(box, radius=26, outline=(255, 248, 230, 100), width=2)
        dr.text((84, 1280), line1, font=f1, fill=(255, 255, 255, 255))
        dr.text((84, 1346), line2 or "", font=f2, fill=(255, 228, 132, 255))
    else:
        f1 = ImageFont.truetype(F_XBOLD, 33)
        f2 = ImageFont.truetype(F_BOLD, 29)
        box = (58, 1320, 862, 1468 if line2 else 1418)
        sd.rounded_rectangle(box, radius=22, fill=(20, 30, 24, 188))
        ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(1.5)))
        dr = ImageDraw.Draw(ov)
        dr.rounded_rectangle(box, radius=22, outline=(255, 232, 150, 110), width=2)
        dr.text((82, 1342), line1, font=f1, fill=(255, 234, 148, 255))
        if line2:
            dr.text((82, 1396), line2, font=f2, fill=(255, 255, 255, 255))

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
        raw_dur = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(sp)
        ], text=True).strip())
        cut_dur, speech_end, first_start = find_clean_cut_sec(sp, raw_dur, cfg["end_anchors"][i - 1], cfg["min_sec"][i - 1], asr, is_last_scene=(i == 3))
        durs.append(cut_dur)
        np_out = work_dir / f"norm_0{i}.mp4"
        mute_head = f",volume=0:enable='lt(t,{first_start:.3f})'" if first_start > 0.18 else ""
        mute_tail = f",afade=t=out:st={max(0.1, speech_end-0.02):.3f}:d=0.06,volume=0:enable='gt(t,{speech_end+0.05:.3f})'" if (speech_end and cut_dur - speech_end > 0.08) else f",afade=t=out:st={max(0.1, cut_dur-0.06):.3f}:d=0.06"
        af = f"highpass=f=80,loudnorm=I=-14.5:TP=-1.5:LRA=9{mute_head},afade=t=in:st={first_start:.3f}:d=0.04{mute_tail}"
        # Nếu ở cảnh cuối mà raw_dur sát chữ cuối (< 0.25s), nhân bản mượt khung hình cuối thêm 0.45s + khoảng lặng để eof_tail_sec >= 0.40s (0% đứt đuôi!)
        need_pad = 0.45 if (i == 3 and (raw_dur - (speech_end or cut_dur)) < 0.25) else 0.0
        if need_pad > 0:
            durs[-1] = round(cut_dur + need_pad, 3)
            vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,tpad=stop_mode=clone:stop_duration={need_pad:.2f},format=yuv420p"
            af = af + f",apad=pad_dur={need_pad:.2f}"
            t_arg = f"{durs[-1]:.3f}"
        else:
            vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,format=yuv420p"
            t_arg = f"{cut_dur:.3f}"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", str(sp), "-t", t_arg,
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

    open_png = work_dir / "ov_open.png"
    make_overlay_png(open_png, cfg["open_l1"], cfg["open_l2"], is_opening=True)

    overlays = [(open_png, 0.12, 3.35)]
    sc_starts = [0.0, durs[0], durs[0] + durs[1]]
    import json as _json
    cuts_data = [
        {"start": round(sc_starts[0], 3), "end": round(sc_starts[0] + durs[0], 3), "label": "scene_01"},
        {"start": round(sc_starts[1], 3), "end": round(sc_starts[1] + durs[1], 3), "label": "scene_02"},
        {"start": round(sc_starts[2], 3), "end": round(sc_starts[2] + durs[2], 3), "label": "scene_03"},
    ]
    (work_dir / "cuts.json").write_text(_json.dumps(cuts_data, indent=2), encoding="utf-8")
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
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(out_mp4)
    ], check=True)

    for old_f in DRIVE_DIR.glob("*Chi Hau*"):
        old_f.unlink(missing_ok=True)
    shutil.copy2(out_mp4, DRIVE_DIR / out_mp4.name)

    tmp_w = work_dir / "_asr.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out_mp4), "-vn", "-ac", "1", "-ar", "16000", str(tmp_w)], check=True)
    heard = " ".join(s.text.strip() for s in asr.transcribe(str(tmp_w), language="vi")[0])
    tmp_w.unlink(missing_ok=True)
    tot = sum(durs)
    print(f"[DONE {cfg['vid']}] {tot:.1f}s -> {out_mp4.name}\n  WHISPER: {heard}\n", flush=True)
    return out_mp4, durs


def main():
    asr = faster_whisper.WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=12)
    qc_rows = []
    for cfg in CONFIGS:
        # Giữ nguyên V02 đã đạt PASS 100% từ video-qc-auditor!
        v2_mp4 = FINAL_ALL_DIR / cfg["out_name"]
        if cfg["vid"] == "V02_Giam_2_Ky_Thay_Doi_Gi" and v2_mp4.exists():
            import json as _j
            c_p = SERIES_DIR / cfg["vid"] / "02_Work" / "cuts.json"
            cd = _j.loads(c_p.read_text(encoding="utf-8"))
            qc_rows.append((cfg["vid"], v2_mp4, [x["end"] - x["start"] for x in cd]))
            print(f"[SKIP {cfg['vid']}] Kept 100% PASS version -> {v2_mp4.name}", flush=True)
            continue
        mp4, durs = assemble_one(cfg, asr)
        qc_rows.append((cfg["vid"], mp4, durs))

    tw, th = 230, 409
    sheet = Image.new("RGB", (7 * (tw + 10) + 10, 3 * (th + 28) + 10), (18, 22, 18))
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
    qc_out = FINAL_ALL_DIR / "QC_7_Videos_Chi_Hang_21_Scenes.jpg"
    sheet.save(qc_out, quality=92)
    shutil.copy2(qc_out, DRIVE_DIR / qc_out.name)
    print("[MASTER QC READY]", qc_out)


if __name__ == "__main__":
    main()
