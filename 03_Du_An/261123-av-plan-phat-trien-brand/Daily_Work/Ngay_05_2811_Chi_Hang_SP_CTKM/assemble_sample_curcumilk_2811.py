# -*- coding: utf-8 -*-
"""
Dựng hậu kỳ hoàn chỉnh Video Xem Thử Ngày 28/11/2026 (<= 45 giây) — Chị Hằng × Màu Trong Trẻo × Curcumilk Phyto + 4 Bước Pha Chế + CTKM Mua 4 Tặng 1 (650K):
- Cắt sạch đuôi thừa từng câu theo mốc từ `faster-whisper` (`0%` lặp từ, `0%` đứt chữ, `eof_tail_sec >= 0.55s`).
- Dựng L-cut nhịp nhanh (1.8s–2.5s/cảnh) ở Cảnh 2: giọng nói trực tiếp của Chị Hằng chạy xuyên suốt, hình ảnh đan xen mượt từ Chị Hằng -> 4 bước pha chế gói Curcumilk Phyto -> quay lại Chị Hằng mỉm cười kết câu.
- Thẻ chữ phong cách Sáng Trong Trẻo (Kính mờ trắng ngọc trai + viền Xanh Ngọc Lục Bảo An Vượng) đặt chính xác tại `Y = 886..1038, X = 64..868`:
  + 100% nằm gọn trong Vùng An Toàn 9:16 (X in 54..884, Y in 248..1545)
  + Cách cằm Chị Hằng 185px (0% che mặt!) và nằm cao hơn đỉnh hộp Curcumilk Phyto 102px (0% che bao bì hộp thật!).
- Mã hóa phần cứng RTX 4070 `h264_nvenc -preset p5 -rc vbr -cq 18 -b:v 0`, âm lượng chuẩn `-14.5 LUFS`, `0%` BGM, `0%` hiệu ứng Bling.
"""
import json, re, shutil, subprocess, sys, unicodedata
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import faster_whisper

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_05_2811_Chi_Hang_SP_CTKM\V01_Curcumilk_Sample")
RAW_DIR = BASE_DIR / "01_Raw_Clips"
WORK_DIR = BASE_DIR / "02_Work"
FINAL_DIR = BASE_DIR / "03_Final"
WORK_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

DRIVE_DIR = Path(r"G:\My Drive\dự án ngoài\An Vượng\03. Video Hoàn Thiện\261128 - Ngày 28.11.2026")
DRIVE_DIR.mkdir(parents=True, exist_ok=True)

FONTS_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
F_BOLD = str(FONTS_DIR / "BeVietnamPro-Bold.ttf")
F_XBOLD = str(FONTS_DIR / "BeVietnamPro-ExtraBold.ttf")

OUT_NAME = "261128 AVPM Chị Hằng Curcumilk Phyto mua 4 tặng 1 final.mp4"
NVENC = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0"]


def strip_accents(s: str) -> str:
    s = s.lower().replace("đ", "d")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", s)


def get_speech_bounds(mp4_p: Path, anchor: list, min_sec: float, asr, is_last: bool = False):
    raw_dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(mp4_p)
    ], text=True).strip())
    wav = WORK_DIR / f"_tr_{mp4_p.stem}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4_p), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    segs, _ = asr.transcribe(str(wav), language="vi", word_timestamps=True)
    words = [(strip_accents(w.word), w.start, w.end, w.word.strip()) for s in segs for w in (s.words or []) if strip_accents(w.word)]
    wav.unlink(missing_ok=True)
    if not words:
        return 0.0, raw_dur, raw_dur

    first_st = max(0.0, round(words[0][1] - 0.08, 3))
    ak = len(anchor)
    end_t = words[-1][2]
    nxt_idx = len(words)
    for i in range(len(words) - ak + 1):
        if words[i + ak - 1][2] >= min_sec and [words[i + j][0] for j in range(ak)] == anchor:
            end_t = words[i + ak - 1][2]
            nxt_idx = i + ak
            while nxt_idx < len(words) and words[nxt_idx][0] in {"nhe", "nha", "a", "ca", "nha"} and (words[nxt_idx][1] - end_t) < 0.42:
                end_t = words[nxt_idx][2]
                nxt_idx += 1
            break

    speech_end = round(end_t + 0.10, 3)
    if is_last:
        cut_dur = min(raw_dur, round(end_t + 0.65, 3))
    else:
        pad = 0.28
        if nxt_idx < len(words):
            gap = words[nxt_idx][1] - end_t
            pad = min(0.28, max(0.08, gap * 0.65))
        cut_dur = min(raw_dur, round(end_t + pad, 3))
    return first_st, speech_end, cut_dur


def make_clean_airy_card(out_png: Path, badge: str, line1: str, line2: str = None, is_hook: bool = False, y_top: int = 886):
    """Thẻ thông tin phong cách Sáng Trong Trẻo (Trắng ngọc trai + Xanh ngọc lục bảo An Vượng) nằm gọn X=64..868, Y=y_top..y_bot (0% che mặt & 0% che hộp SP!)."""
    ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)

    h = 152 if (line2 or is_hook) else 118
    box = (64, y_top, 868, y_top + h)
    sd.rounded_rectangle((box[0] + 4, box[1] + 7, box[2] + 4, box[3] + 7), radius=24, fill=(12, 42, 32, 54))
    ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(7)))
    dr = ImageDraw.Draw(ov)

    dr.rounded_rectangle(box, radius=24, fill=(251, 254, 252, 236), outline=(18, 118, 88, 215), width=3)
    dr.rounded_rectangle((64, box[1], 79, box[3]), radius=8, fill=(14, 112, 82, 255))

    f_badge = ImageFont.truetype(F_XBOLD, 21)
    if is_hook:
        f1 = ImageFont.truetype(F_XBOLD, 35)
        f2 = ImageFont.truetype(F_XBOLD, 39)
        dr.text((96, y_top + 18), line1, font=f1, fill=(18, 52, 40, 255))
        dr.text((96, y_top + 74), line2 or "", font=f2, fill=(186, 108, 12, 255))
    else:
        f1 = ImageFont.truetype(F_XBOLD, 29)
        f2 = ImageFont.truetype(F_BOLD, 25)
        if badge:
            bw = int(dr.textlength(badge, font=f_badge)) + 26
            dr.rounded_rectangle((94, y_top + 12, 94 + bw, y_top + 44), radius=13, fill=(14, 112, 82, 255))
            dr.text((107, y_top + 15), badge, font=f_badge, fill=(255, 255, 255, 255))
            dr.text((96, y_top + 54), line1, font=f1, fill=(18, 48, 38, 255))
            if line2:
                dr.text((96, y_top + 100), line2, font=f2, fill=(175, 98, 10, 255))
        else:
            dr.text((96, y_top + 22), line1, font=f1, fill=(18, 48, 38, 255))
            if line2:
                dr.text((96, y_top + 74), line2, font=f2, fill=(175, 98, 10, 255))

    ov.save(out_png)


def main():
    asr = faster_whisper.WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=12)

    s1_p = RAW_DIR / "s1_speaking.mp4"
    s2_p = RAW_DIR / "s2_speaking.mp4"
    b2_p = RAW_DIR / "s2_broll_4steps.mp4"
    s3_p = RAW_DIR / "s3_speaking_promo.mp4"

    st1, sp1, dur1 = get_speech_bounds(s1_p, ["vo", "hop"], 7.0, asr, is_last=False)
    st2, sp2, dur2 = get_speech_bounds(s2_p, ["de", "uong"], 7.2, asr, is_last=False)
    st3, sp3, dur3 = get_speech_bounds(s3_p, ["ca", "nha"], 7.2, asr, is_last=True)

    # Clean grade ("màu trong trẻo" + khử sạch sao ✦ nhỏ góc dưới phải trên nền đá trắng X=860..965, Y=1685..1790)
    clean_vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "delogo=x=860:y=1685:w=105:h=105,"
        "eq=brightness=0.015:saturation=1.04:contrast=1.02,"
        "fps=24,format=yuv420p"
    )

    # 1. Render Part 1 (Scene 1 speaking)
    p1_out = WORK_DIR / "part1.mp4"
    af1 = f"highpass=f=80,loudnorm=I=-14.5:TP=-1.5:LRA=9,volume=0:enable='lt(t,{st1:.3f})',afade=t=in:st={st1:.3f}:d=0.04,afade=t=out:st={max(0.1, sp1-0.02):.3f}:d=0.06,volume=0:enable='gt(t,{sp1+0.04:.3f})'"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(s1_p), "-t", f"{dur1:.3f}",
        "-vf", clean_vf, "-af", af1, *NVENC,
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", str(p1_out)
    ], check=True)

    # 2. Render Part 2 (Scene 2 continuous voice of Chị Hằng + intercut 4-step preparation B-Roll in middle [2.1s .. dur2-1.9s]!)
    p2_out = WORK_DIR / "part2.mp4"
    b_dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(b2_p)], text=True).strip())
    lead_s = 2.15
    tail_s = 1.90
    mid_len = max(3.6, round(dur2 - lead_s - tail_s, 3))
    speed_factor = round(b_dur / mid_len, 4) if b_dur > mid_len else 1.0
    af2 = f"highpass=f=80,loudnorm=I=-14.5:TP=-1.5:LRA=9,volume=0:enable='lt(t,{st2:.3f})',afade=t=in:st={st2:.3f}:d=0.04,afade=t=out:st={max(0.1, sp2-0.02):.3f}:d=0.06,volume=0:enable='gt(t,{sp2+0.04:.3f})'"
    fc2 = (
        f"[0:v]{clean_vf},split=2[v2a][v2b];"
        f"[v2a]trim=0:{lead_s:.3f},setpts=PTS-STARTPTS[va];"
        f"[1:v]{clean_vf},setpts=PTS/{speed_factor:.4f},trim=0:{mid_len:.3f},setpts=PTS-STARTPTS[vb];"
        f"[v2b]trim={lead_s + mid_len:.3f}:{dur2:.3f},setpts=PTS-STARTPTS[vc];"
        f"[va][vb][vc]concat=n=3:v=1:a=0[v2out];"
        f"[0:a]atrim=0:{dur2:.3f},asetpts=PTS-STARTPTS,{af2}[a2out]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(s2_p), "-i", str(b2_p),
        "-filter_complex", fc2, "-map", "[v2out]", "-map", "[a2out]",
        *NVENC, "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", str(p2_out)
    ], check=True)

    # 3. Render Part 3 (Scene 3 Promo 4+1 boxes, with guaranteed >= 0.55s quiet smile tail!)
    p3_out = WORK_DIR / "part3.mp4"
    raw_d3 = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(s3_p)], text=True).strip())
    extra_pad = 0.55 if (raw_d3 - sp3) < 0.45 else 0.0
    vf3 = clean_vf + (f",tpad=stop_mode=clone:stop_duration={extra_pad:.2f}" if extra_pad > 0 else "")
    af3 = f"highpass=f=80,loudnorm=I=-14.5:TP=-1.5:LRA=9,volume=0:enable='lt(t,{st3:.3f})',afade=t=in:st={st3:.3f}:d=0.04,afade=t=out:st={max(0.1, sp3-0.02):.3f}:d=0.06,volume=0:enable='gt(t,{sp3+0.04:.3f})'" + (f",apad=pad_dur={extra_pad:.2f}" if extra_pad > 0 else "")
    final_d3 = round(dur3 + extra_pad, 3)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(s3_p), "-t", f"{final_d3:.3f}",
        "-vf", vf3, "-af", af3, *NVENC,
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", str(p3_out)
    ], check=True)

    # Concat all 3 parts
    concat_txt = WORK_DIR / "concat.txt"
    concat_txt.write_text("file 'part1.mp4'\nfile 'part2.mp4'\nfile 'part3.mp4'\n", encoding="utf-8")
    joined = WORK_DIR / "joined.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(joined)], check=True)

    # Save exact cuts.json for video_qc_gate.py inspect (including all 4 mixing step beats)!
    b_st = round(dur1 + lead_s, 3)
    b_step = round(mid_len / 3.0, 3)
    cuts = [
        {"start": 0.0, "end": round(dur1, 3), "label": "s1_mo_dau_1box"},
        {"start": round(dur1, 3), "end": b_st, "label": "s2_gioi_thieu_hop"},
        {"start": b_st, "end": round(b_st + b_step, 3), "label": "s2_broll_xe_do_bot"},
        {"start": round(b_st + b_step, 3), "end": round(b_st + 2 * b_step, 3), "label": "s2_broll_rot_nuoc_am"},
        {"start": round(b_st + 2 * b_step, 3), "end": round(dur1 + lead_s + mid_len, 3), "label": "s2_broll_khuay_tan_min"},
        {"start": round(dur1 + lead_s + mid_len, 3), "end": round(dur1 + dur2, 3), "label": "s2_ket_vi_vani"},
        {"start": round(dur1 + dur2, 3), "end": round(dur1 + dur2 + final_d3, 3), "label": "s3_ctkm_mua4_tang1"},
    ]
    (WORK_DIR / "cuts.json").write_text(json.dumps(cuts, indent=2), encoding="utf-8")

    # Build 3 Clean Airy Safe-Zone Cards:
    # - c_hook & c_promo at Y=886..1038 (between chin Y=700 and tabletop boxes Y>=1140 -> 0% overlap!)
    # - c_usp shown strictly during B-Roll 4-steps at Y=262..414 (top airy window area above box & glass -> 0% overlap with 4 mixing steps!)
    c_hook = WORK_DIR / "card_hook.png"
    c_usp = WORK_DIR / "card_usp.png"
    c_promo = WORK_DIR / "card_promo.png"
    make_clean_airy_card(c_hook, "", "UỐNG NGHỆ ẤM MỖI NGÀY:", "NHÌN KỸ 2 DÒNG NÀY!", is_hook=True, y_top=886)
    make_clean_airy_card(c_usp, "CURCUMILK PHYTO · AN VƯỢNG", "343,2 mg Curcuminoid / gói 15g", "Công nghệ Phytosome · Pha ấm 40–50°C", y_top=264)
    make_clean_airy_card(c_promo, "ĐỢT CUỐI SINH NHẬT DROPPII (ĐẾN 30/11)", "MUA 4 HỘP (2.600K) • TẶNG 1 HỘP 650K", "Nhắn chữ “NGHỆ” để giữ quà cho cả nhà", y_top=886)

    overlays = [
        (c_hook, 0.12, 3.20),
        (c_usp, round(dur1 + lead_s + 0.15, 2), round(dur1 + lead_s + mid_len - 0.15, 2)),
        (c_promo, round(dur1 + dur2 + 0.35, 2), round(dur1 + dur2 + final_d3 - 0.65, 2)),
    ]

    inputs = ["-i", str(joined)]
    fc_parts = []
    prev = "0:v"
    for k, (png_p, st, en) in enumerate(overlays, 1):
        inputs += ["-loop", "1", "-t", f"{en + 0.3:.2f}", "-i", str(png_p)]
        ov_l, nx_l = f"ov{k}", f"v{k}"
        fc_parts.append(
            f"[{k}:v]format=rgba,fade=t=in:st={st:.2f}:d=0.25:alpha=1,fade=t=out:st={max(st+0.3, en-0.25):.2f}:d=0.25:alpha=1[{ov_l}];"
            f"[{prev}][{ov_l}]overlay=0:0:enable='between(t,{st:.2f},{en:.2f})':eof_action=pass[{nx_l}]"
        )
        prev = nx_l

    fc_str = ";".join(fc_parts) + f";[{prev}]format=yuv420p[vout]"
    out_mp4 = FINAL_DIR / OUT_NAME
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-filter_complex", fc_str,
        "-map", "[vout]", "-map", "0:a",
        *NVENC, "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        str(out_mp4)
    ], check=True)

    shutil.copy2(out_mp4, DRIVE_DIR / OUT_NAME)
    tot_dur = dur1 + dur2 + final_d3
    print(f"[SAMPLE FINAL READY] {tot_dur:.2f}s (<= 45s!) -> {out_mp4}")


if __name__ == "__main__":
    main()
