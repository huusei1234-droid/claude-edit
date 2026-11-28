# -*- coding: utf-8 -*-
"""
Director V5 Hybrid Assembler & Multi-Episode Renderer for:
  `261122 K4 Bố chồng thu thẻ lương dạy con thương vợ` (An Vượng Pharma `BOJOMI` + `CURCUMILK PHYTO` Edition)

1. Audits & processes the 5 newly shot An Vượng Pharma clips (`w06_av, w07_av, w08_av, w18_av, w19_av`)
   with Demucs vocal/ambience stems, `10_AI_Clip_Harmonizer_Natural.cube` LUT, and exact Act BGM (`acoustic_calm_folk.mp3`
   for `w06_av..w08_av`, `piano_warm_family.mp3` for `w18_av..w19_av`) so they blend seamlessly with the 21 verified
   non-product cuts of `v02_orig_master.mp4`.
2. Builds `QA_V02_AnVuong_9x16.jpg` contact sheet for visual verification of all 26 cuts.
3. Exports Director V5:
   - `261122 K4 Bố chồng thu thẻ lương dạy con thương vợ tập 1 final.mp4` (`<= 90.0s` + Signature Hook + Cliffhanger Outro)
   - `261122 K4 Bố chồng thu thẻ lương dạy con thương vợ tập 2 final.mp4` (`<= 90.0s` + Signature Hook)
   - `261122 K4 Bố chồng thu thẻ lương dạy con thương vợ tập full final.mp4` (`Signature Hook + Full 26-cut Upgraded Story`)
   and removes the old unsplit `261122 K4 Bố chồng thu thẻ lương dạy con thương vợ final.mp4` across all 3 delivery folders!
"""
import json, math, os, re, shutil, subprocess, sys, wave
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_261126 = r"C:\AI\full studio\output\k4-20-reels-261126"
WORK_DIR    = os.path.join(BASE_261126, "v02_anvuong_upgrade")
BGM_DIR     = os.path.join(BASE_261126, "bgm")
LUT_PATH    = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"
ART_DIR     = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
DU_AN_261122 = r"G:\My Drive\AI_Full_Studio\03_Du_An\261122-k4-5-tap-drama-gia-dinh"

K4_DRIVE_DIR     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu"
MASTER_CLOUD_DIR = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR = r"C:\XUẤT CAPCUT\K4 - Mẹ Chồng Nàng Dâu"

sys.path.insert(0, BASE_261126)
from render_20_reels_director_v3 import (
    SR, FPS, SAMPLES_PER_FRAME,
    is_valid_mp4_video, probe_video, detect_letterbox_bars,
    run_demucs_stems, load_wav_48k_stereo, load_mp4_audio_48k_stereo,
    analyze_clip_speech, detect_tight_bounds_48k, fft_bandpass_stereo,
    load_bgm_48k_prepared, get_looped_bgm_slice, slice_exact_samples,
)
from split_10_previous_k4_director_v5 import (
    X264_COMMON, run_ffmpeg_lowmem,
    isolate_vocals_48k_for_cut, extract_highlight_from_master,
    make_black_pause_clip, encode_story_span_video,
    pick_dramatic_cuts, build_hook_and_mix, build_cliff_and_mix, mux_and_deliver,
)

BATCH_CODE = "261122"
BASE_TITLE = "Bố chồng thu thẻ lương dạy con thương vợ"

# Exact verified 26-cut frame boundaries of `v02_orig_master.mp4`
ORIG_26_CUTS = [
    ("w01", 0, 124),
    ("w02", 124, 295),
    ("w03", 295, 433),
    ("w04", 433, 617),
    ("w05", 617, 738),
    ("w06_av", 738, 917),    # REPLACED WITH AN VƯỢNG!
    ("w07_av", 917, 1059),   # REPLACED WITH AN VƯỢNG!
    ("w08_av", 1059, 1120),  # REPLACED WITH AN VƯỢNG!
    ("w09", 1120, 1279),
    ("s03", 1279, 1428),
    ("w10", 1428, 1562),
    ("w11", 1562, 1695),
    ("s04", 1695, 1836),
    ("w12", 1836, 1997),
    ("s05", 1997, 2182),
    ("s06", 2182, 2385),
    ("w13", 2385, 2560),
    ("w14", 2560, 2761),
    ("w15", 2761, 2888),
    ("w16", 2888, 3113),
    ("s07", 3113, 3292),
    ("s08", 3292, 3453),
    ("w17", 3453, 3595),
    ("w18_av", 3595, 3804),  # REPLACED WITH AN VƯỢNG!
    ("w19_av", 3804, 3955),  # REPLACED WITH AN VƯỢNG!
    ("s09", 3955, 4193),
]

AV_NEW_SPECS = {
    "w06_av": ("voice", "acoustic_calm_folk.mp3", 25.0, 0.92, "Cái đám con cái này ngày nào cũng để người già phải lo để xem quầy An Vượng có bộ dinh dưỡng nào tốt cho bà thông gia nào"),
    "w07_av": ("voice", "acoustic_calm_folk.mp3", 31.0, 0.92, "Bộ đôi Bojomi canxi tảo biển đỏ với nghệ Curcumilk Phyto An Vượng này dễ uống êm bụng biếu người lớn tuổi ở quê là chuẩn nhất rồi"),
    "w08_av": ("visual", "acoustic_calm_folk.mp3", 36.5, 0.92, ""),
    "w18_av": ("voice", "piano_warm_family.mp3", 12.0, 1.05, "Mấy hộp Bojomi canxi với nghệ Curcumilk Phyto của An Vượng ba chọn kỹ lắm hai đứa mang về biếu mẹ hết kèm phong bì này mua áo mới nha"),
    "w19_av": ("voice", "piano_warm_family.mp3", 19.0, 1.05, "Lên đường thượng lộ bình an nha hai đứa về dưới quê nhớ pha ấm mỗi sáng cho mẹ dễ uống ở lại chơi vài hôm chăm mẹ cho trọn vẹn nghe con"),
}

def render_one_new_av_segment(cid, seg_dir):
    mode, bgm_fn, bgm_off, bgm_gain, exp_dlg = AV_NEW_SPECS[cid]
    raw_mp4 = os.path.join(WORK_DIR, "raw_9x16", f"{cid}.mp4")
    assert is_valid_mp4_video(raw_mp4), f"Missing/invalid raw clip: {raw_mp4}"
    w, h, total_dur = probe_video(raw_mp4)
    tag_key = f"v02_9x16_{cid}"
    voc_wav, nov_wav = run_demucs_stems(raw_mp4, tag_key)
    voc_st = load_wav_48k_stereo(voc_wav)
    nov_st = load_wav_48k_stereo(nov_wav)

    if mode == "visual":
        ss = 0.65
        to = min(total_dur - 0.10, ss + 2.15)
        n_frames = max(48, int(round((to - ss) * FPS)))
        n_samples = n_frames * SAMPLES_PER_FRAME
        s_samp = int(round(ss * SR))
        amb = fft_bandpass_stereo(slice_exact_samples(nov_st, s_samp, n_samples), 120.0, 6500.0) * 0.16
        dlg_seg = amb
        duck_factor = 1.25
    else:
        audit_info = analyze_clip_speech(raw_mp4, tag_key, exp_dlg)
        ss, to, sp_s, sp_e, sp_rms = detect_tight_bounds_48k(voc_st, total_dur, audit_info=audit_info, is_wide=True, is_cta=False)
        n_frames = max(54, int(round((to - ss) * FPS)))
        n_samples = n_frames * SAMPLES_PER_FRAME
        s_samp = int(round(ss * SR))
        v_sl = fft_bandpass_stereo(slice_exact_samples(voc_st, s_samp, n_samples), 85.0, 13200.0)
        a_sl = fft_bandpass_stereo(slice_exact_samples(nov_st, s_samp, n_samples), 110.0, 7200.0) * 0.14
        target_rms = 0.082
        gain_v = min(2.4, max(0.75, target_rms / max(sp_rms, 0.020)))
        dlg_seg = v_sl * gain_v + a_sl
        fi = min(960, n_samples // 6)
        fo = min(1440, n_samples // 6)
        dlg_seg[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
        dlg_seg[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
        duck_factor = 0.72

    bgm_arr = load_bgm_48k_prepared(bgm_fn)
    bgm_sl = get_looped_bgm_slice(bgm_arr, bgm_off, n_samples) * float(bgm_gain) * duck_factor
    bfi = min(1600, n_samples // 5)
    bfo = min(1600, n_samples // 5)
    bgm_sl[:bfi] *= np.linspace(0.0, 1.0, bfi, dtype=np.float32)[:, None]
    bgm_sl[-bfo:] *= np.linspace(1.0, 0.0, bfo, dtype=np.float32)[:, None]

    mix_seg = np.clip(np.tanh((dlg_seg + bgm_sl) * 1.04) / 1.04, -0.94, 0.94)

    top_b, bot_b = detect_letterbox_bars(raw_mp4, w, h, (ss + to) * 0.5)
    vf = []
    if top_b + bot_b > 0:
        vf.append(f"crop={w}:{h - top_b - bot_b}:0:{top_b}")
    vf.append("scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos")
    vf.append("crop=1080:1920")
    if os.path.exists(LUT_PATH):
        lut_esc = LUT_PATH.replace("\\", "/").replace(":", "\\:")
        vf.append(f"lut3d=file='{lut_esc}':interp=tetrahedral")
    vf.append("eq=contrast=1.02:saturation=1.03")

    out_v = os.path.join(seg_dir, f"seg_{cid}.mp4")
    run_ffmpeg_lowmem([
        "ffmpeg", "-y", "-v", "error", "-threads", "2",
        "-ss", f"{ss:.4f}", "-t", f"{(n_frames / float(FPS)) + 0.08:.4f}", "-i", raw_mp4,
        "-vf", ",".join(vf), "-an", "-r", str(FPS), "-frames:v", str(n_frames),
        *X264_COMMON, out_v
    ])
    return out_v, mix_seg, n_frames

def build_upgraded_v02_master():
    orig_mp4 = os.path.join(WORK_DIR, "v02_orig_master.mp4")
    assert os.path.exists(orig_mp4), f"Missing {orig_mp4}"
    orig_pcm = load_mp4_audio_48k_stereo(orig_mp4)
    seg_dir = os.path.join(WORK_DIR, "segs_26")
    os.makedirs(seg_dir, exist_ok=True)

    seg_vids = []
    seg_pcms = []
    segs_meta = []
    cur_f = 0

    for idx, (cid, f0, f1) in enumerate(ORIG_26_CUTS):
        if cid in AV_NEW_SPECS:
            sv, spcm, nf = render_one_new_av_segment(cid, seg_dir)
            print(f"  [NEW AV SHOT #{idx+1:02d} {cid}] {nf/30.0:.2f}s rendered!", flush=True)
        else:
            nf = f1 - f0
            sv = os.path.join(seg_dir, f"seg_{idx+1:02d}_{cid}.mp4")
            if not os.path.exists(sv):
                encode_story_span_video(orig_mp4, f0, f1, sv, fade_in=False, fade_out_black=False)
            spcm = orig_pcm[f0 * SAMPLES_PER_FRAME : f1 * SAMPLES_PER_FRAME].copy()
            if len(spcm) < nf * SAMPLES_PER_FRAME:
                spcm = np.vstack([spcm, np.zeros((nf * SAMPLES_PER_FRAME - len(spcm), 2), dtype=np.float32)])
            # Tiny 12ms micro-fade at splice points around replaced shots to prevent any sample click
            fi = min(576, len(spcm) // 8)
            spcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
            spcm[-fi:] *= np.linspace(1.0, 0.0, fi, dtype=np.float32)[:, None]

        seg_vids.append(sv)
        seg_pcms.append(spcm)
        segs_meta.append({
            "idx": idx, "cid": cid, "f0": cur_f, "f1": cur_f + nf,
            "n_frames": nf, "start": round(cur_f / 30.0, 3), "end": round((cur_f + nf) / 30.0, 3),
            "dur": round(nf / 30.0, 3),
        })
        cur_f += nf

    # Mux clean story-only upgraded master `v02_anvuong_story_master.mp4` for unified Hook/Split/QA extraction!
    story_master_pcm = np.concatenate(seg_pcms, axis=0)
    story_wav = os.path.join(WORK_DIR, "v02_av_story.wav")
    with wave.open(story_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(story_master_pcm, -0.96, 0.96) * 32767.0).astype(np.int16).tobytes())
    cat_txt = os.path.join(WORK_DIR, "v02_av_story_concat.txt")
    with open(cat_txt, "w", encoding="utf-8") as cf:
        for sv in seg_vids:
            cf.write(f"file '{sv}'\n")
    story_master_mp4 = os.path.join(WORK_DIR, "v02_anvuong_story_master.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", cat_txt, "-i", story_wav,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "224k", "-ar", str(SR), "-ac", "2",
        story_master_mp4
    ], check=True)
    os.remove(story_wav)

    # Build 26-cut QA Contact Sheet (`QA_V02_AnVuong_9x16.jpg`)
    cols = 5
    rows = math.ceil(len(segs_meta) / cols)
    tw, th = 216, 384
    sheet = Image.new("RGB", (cols * tw, 54 + rows * th), (14, 18, 16))
    dr = ImageDraw.Draw(sheet)
    try:
        fh = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
        fs = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 14)
    except Exception:
        fh = fs = None
    dr.text((14, 15), f"QA V5 AN VƯỢNG UPGRADE — 261122 {BASE_TITLE} (26 CUTS)", fill=(120, 250, 175), font=fh)
    for m in segs_meta:
        i = m["idx"]
        t_mid = (m["start"] + m["end"]) * 0.5
        raw_rgb = subprocess.check_output([
            "ffmpeg", "-v", "error", "-ss", f"{t_mid:.2f}", "-i", story_master_mp4,
            "-frames:v", "1", "-vf", f"scale={tw}:{th}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"
        ])
        im = Image.frombytes("RGB", (tw, th), raw_rgb)
        r, c = i // cols, i % cols
        x0, y0 = c * tw, 54 + r * th
        sheet.paste(im, (x0, y0))
        col_lbl = (110, 255, 160) if m["cid"].endswith("_av") else (255, 230, 120)
        dr.rectangle([x0 + 4, y0 + 4, x0 + 132, y0 + 24], fill=(0, 0, 0))
        dr.text((x0 + 7, y0 + 5), f"#{i+1:02d} {m['cid']}", fill=col_lbl, font=fs)
    qa_out = os.path.join(WORK_DIR, "QA_V02_AnVuong_9x16.jpg")
    sheet.save(qa_out, "JPEG", quality=92)
    shutil.copy2(qa_out, os.path.join(ART_DIR, "QA_V02_AnVuong_9x16.jpg"))
    if os.path.exists(DU_AN_261122):
        shutil.copy2(qa_out, os.path.join(DU_AN_261122, "QA_V02_AnVuong_9x16.jpg"))

    # Split into Tập 1 (cuts 0..14 -> ends on Ông Tấn's fierce "Ba má vợ có bán đứt con gái cho mày đâu!" ~68s)
    # & Tập 2 (cuts 15..26 -> salary card confiscation + An Vượng gift handover! ~67s) + Tập Full!
    split_cut = 15  # Cuts [0..15) = 15 cuts (~67s), Cuts [15..26) = 11 cuts (~67s)
    if segs_meta[split_cut - 1]["end"] > 70.0:
        split_cut = 14
    ranges = [(0, split_cut), (split_cut, len(segs_meta))]
    total_frames = segs_meta[-1]["f1"]

    hook_dir = os.path.join(WORK_DIR, "hooks_v5")
    os.makedirs(hook_dir, exist_ok=True)
    results = []

    for p_idx, (i0, i1) in enumerate(ranges):
        part_num = p_idx + 1
        has_next = (p_idx < len(ranges) - 1)
        cand_h = list(range(i0, i1))
        # Ensure our An Vượng showcase shot `w07_av` (idx 6) is featured in Tập 1's Highlight Hook!
        h_picks = pick_dramatic_cuts(cand_h, segs_meta, story_master_pcm, k_want=4, exclude_first=(p_idx == 0), exclude_last_cta=(not has_next))
        if p_idx == 0 and 6 not in h_picks and len(h_picks) >= 4:
            h_picks[0] = 6
            h_picks = sorted(h_picks)
        h_vids, h_pcm = build_hook_and_mix(hook_dir, f"p{part_num}", h_picks, segs_meta, story_master_mp4, story_master_pcm)

        if has_next:
            nx0, nx1 = ranges[p_idx + 1]
            c_picks = pick_dramatic_cuts(list(range(nx0, nx1)), segs_meta, story_master_pcm, k_want=2, exclude_first=False, exclude_last_cta=True)
            c_vids, c_pcm = build_cliff_and_mix(hook_dir, f"p{part_num}", c_picks, segs_meta, story_master_mp4, story_master_pcm)
        else:
            c_vids, c_pcm = [], np.zeros((0, 2), dtype=np.float32)

        f_s, f_e = segs_meta[i0]["f0"], segs_meta[i1 - 1]["f1"]
        st_vid = os.path.join(hook_dir, f"story_p{part_num}.mp4")
        encode_story_span_video(story_master_mp4, f_s, f_e, st_vid, fade_in=True, fade_out_black=has_next)
        st_pcm = story_master_pcm[f_s * SAMPLES_PER_FRAME : f_e * SAMPLES_PER_FRAME].copy()
        fi = min(int(0.28 * SR), len(st_pcm))
        fo = min(int((0.45 if has_next else 0.20) * SR), len(st_pcm))
        st_pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
        st_pcm[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]

        all_pcm = np.concatenate([h_pcm, st_pcm] + ([c_pcm] if len(c_pcm) else []), axis=0)
        all_vids = list(h_vids) + [st_vid] + list(c_vids)
        results.append(mux_and_deliver(BATCH_CODE, f"{BASE_TITLE} tập {part_num}", all_vids, all_pcm, hook_dir, enforce_90s=True))

    # Render `tập full`
    f_picks = [6, 14, 19, 23]  # w07_av (An Vượng showcase), s05, w16, w18_av!
    fh_vids, fh_pcm = build_hook_and_mix(hook_dir, "full", f_picks, segs_meta, story_master_mp4, story_master_pcm)
    full_st_vid = os.path.join(hook_dir, "story_full.mp4")
    encode_story_span_video(story_master_mp4, 0, total_frames, full_st_vid, fade_in=True, fade_out_black=False)
    full_st_pcm = story_master_pcm.copy()
    fi = min(int(0.28 * SR), len(full_st_pcm))
    full_st_pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    full_all_pcm = np.concatenate([fh_pcm, full_st_pcm], axis=0)
    full_all_vids = list(fh_vids) + [full_st_vid]
    results.append(mux_and_deliver(BATCH_CODE, f"{BASE_TITLE} tập full", full_all_vids, full_all_pcm, hook_dir, enforce_90s=False))

    # Remove old unsplit `261122 K4 Bố chồng thu thẻ lương dạy con thương vợ final.mp4`
    old_fn = f"{BATCH_CODE} K4 {BASE_TITLE} final.mp4"
    for tdir in (K4_DRIVE_DIR, MASTER_CLOUD_DIR, LOCAL_CAPCUT_DIR):
        op = os.path.join(tdir, old_fn)
        if os.path.exists(op):
            try:
                os.remove(op)
                print(f"  [REMOVED OLD GENERIC BOX MP4] {op}", flush=True)
            except Exception:
                pass

    json.dump(results, open(os.path.join(WORK_DIR, "v02_anvuong_delivery.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n=== V02 AN VƯỢNG UPGRADE COMPLETE (TẬP 1 + TẬP 2 + TẬP FULL DELIVERED)! ===", flush=True)

if __name__ == "__main__":
    build_upgraded_v02_master()
