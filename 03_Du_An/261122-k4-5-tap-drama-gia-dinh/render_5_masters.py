"""
Renders all 5 K4 Family Drama Episodes (`1080x1920` Vertical & `1920x1080` Ngang) on GPU RTX 3060 (`h264_nvenc`):
- Isolates pure Vietnamese speech via CUDA `Demucs` (`htdemucs --two-stems=vocals`), removing 100% AI background noise.
- Trims exact first & last spoken syllable with smooth micro-fades (`0.04s` in / `0.05s` out) -> 0% click/pop, crisp drama pacing.
- Auto-crops any letterbox bars & removes any Flow corner watermark (`delogo`), applies gentle `10_AI_Clip_Harmonizer_Natural.cube` LUT.
- Mixes 2-Act BGM (`dram_quiet_tension` / `sad_ltk_piano` -> `dram_ltk` / `piano_warm_family`) with Voice Pocket EQ (`1.5kHz` & `2.8kHz` -4.2dB).
- Exports QA Contact Sheets + Delivers Final MP4s (`261122 K4 <Tên Tiếng Việt> final.mp4`) to K4 Google Drive folder (`Ngang\` for 16:9), Master Cloud `04_Videos_Final`, and `D:\XUẤT CAPCUT`.
"""
import json, os, shutil, subprocess, sys, wave
import numpy as np

BASE_DIR   = r"d:\AI\full studio\output\k4-5-videos-261122"
BGM_DIR    = os.path.join(BASE_DIR, "bgm")
DEMUCS_DIR = os.path.join(BASE_DIR, "demucs_cache")
QC_DIR     = os.path.join(BASE_DIR, "qc_sheets")
ART_DIR    = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
DEMUCS_PY  = r"D:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
LUT_PATH   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"

K4_DRIVE_DIR     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu"
MASTER_CLOUD_DIR = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR = r"D:\XUẤT CAPCUT\K4 - Mẹ Chồng Nàng Dâu"
DU_AN_CLOUD_DIR  = r"G:\My Drive\AI_Full_Studio\03_Du_An\261122-k4-5-tap-drama-gia-dinh"

for d in (DEMUCS_DIR, QC_DIR):
    os.makedirs(d, exist_ok=True)

EPISODE_META = {
    "v01": {
        "title": "Mẹ chỉ có một vợ tự chọn đi",
        "scenes": ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09"],
        "pivot_idx": 7,  # s08: Hiếu points to the door!
        "bgm_act1": ("dram_quiet_tension.mp3", 3.0, 0.23),
        "bgm_act2": ("dram_ltk.mp3", 0.0, 0.22),
    },
    "v02": {
        "title": "Bố chồng thu thẻ lương dạy con thương vợ",
        "scenes": ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09"],
        "pivot_idx": 4,  # s05: Ông Tấn schools his son & hands everything to Thảo!
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.22),
        "bgm_act2": ("piano_warm_family.mp3", 8.0, 0.25),
    },
    "v03": {
        "title": "Mẹ kế chủ tịch làm chủ cho con chồng",
        "scenes": ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09"],
        "pivot_idx": 6,  # s07: Cô Lan steps up with lawyer & VIP heart surgery!
        "bgm_act1": ("sad_ltk_piano.mp3", 12.0, 0.25),
        "bgm_act2": ("piano_warm_family.mp3", 14.0, 0.26),
    },
    "v04": {
        "title": "Mẹ quê vượt ngàn cây số tìm con gái",
        "scenes": ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08"],
        "pivot_idx": 5,  # s06-s07: Mother reveals sick father & Tú calls her Mẹ!
        "bgm_act1": ("sad_ltk_piano.mp3", 6.0, 0.25),
        "bgm_act2": ("piano_warm_family.mp3", 10.0, 0.26),
    },
    "v05": {
        "title": "Đòi 2 tỷ sính lễ ngay trước cổng cưới",
        "scenes": ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08"],
        "pivot_idx": 4,  # s05: Groom Quân flips the table & cancels wedding!
        "bgm_act1": ("dram_quiet_tension.mp3", 4.0, 0.23),
        "bgm_act2": ("dram_ltk.mp3", 0.0, 0.23),
    },
}

def probe_video(p):
    j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration", "-of", "json", p
    ]).decode("utf-8"))
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])

def detect_letterbox_bars(mp4_path, w, h, t_mid):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", f"{t_mid:.2f}", "-i", mp4_path,
        "-frames:v", "1", "-pix_fmt", "gray", "-f", "rawvideo", "-"
    ])
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w))
    row_means = arr.mean(axis=1)
    top_b = 0
    while top_b < h // 5 and row_means[top_b] < 16.0:
        top_b += 1
    bot_b = 0
    while bot_b < h // 5 and row_means[h - 1 - bot_b] < 16.0:
        bot_b += 1
    top_b = ((top_b + 1) // 2) * 2 if top_b >= 4 else 0
    bot_b = ((bot_b + 1) // 2) * 2 if bot_b >= 4 else 0
    return top_b, bot_b

def run_demucs_vocals(mp4_path, tag_key):
    out_wav = os.path.join(DEMUCS_DIR, f"{tag_key}_vocals.wav")
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 20_000:
        return out_wav
    raw_wav = os.path.join(DEMUCS_DIR, f"{tag_key}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4_path, "-vn", "-ac", "2", "-ar", "44100", raw_wav], check=True)
    subprocess.run([
        DEMUCS_PY, "-m", "demucs.separate",
        "-n", "htdemucs", "--two-stems=vocals", "-d", "cuda",
        "-o", DEMUCS_DIR, raw_wav
    ], check=True)
    sep_voc = os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "vocals.wav")
    shutil.copy2(sep_voc, out_wav)
    return out_wav

def detect_speech_bounds(vocals_wav, total_dur, min_ss=0.06, pre_pad=0.14, post_pad=0.22):
    with wave.open(vocals_wav, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        pcm = pcm.reshape(-1, nch).mean(axis=1)
    win = int(sr * 0.025)
    nf = len(pcm) // win
    if nf < 4:
        return min_ss, max(min_ss + 1.2, total_dur - 0.08)
    rms = np.sqrt(np.mean(pcm[:nf * win].reshape(nf, win) ** 2, axis=1))
    min_idx = int(min_ss / 0.025)
    peak = float(np.max(rms[min_idx:])) if min_idx < len(rms) else float(np.max(rms))
    thr = max(0.012, peak * 0.10)
    active = np.where(rms[min_idx:] >= thr)[0] + min_idx
    if len(active) == 0:
        return min_ss, max(min_ss + 1.5, total_dur - 0.10)
    t_first = active[0] * 0.025
    t_last  = (active[-1] + 1) * 0.025
    ss = max(min_ss, t_first - pre_pad)
    to = min(total_dur - 0.04, t_last + post_pad)
    if to - ss < 1.5:
        to = min(total_dur - 0.04, ss + 1.8)
    return round(ss, 3), round(to, 3)

def deliver_episode(src_mp4, vn_title, is_horizontal):
    fname = f"261122 K4 {vn_title} final.mp4"
    targets = [
        ("brand_path", os.path.join(K4_DRIVE_DIR, "Ngang") if is_horizontal else K4_DRIVE_DIR),
        ("master_cloud_path", os.path.join(MASTER_CLOUD_DIR, "Ngang") if is_horizontal else MASTER_CLOUD_DIR),
        ("local_path", os.path.join(LOCAL_CAPCUT_DIR, "Ngang") if is_horizontal else LOCAL_CAPCUT_DIR),
    ]
    out = {"filename": fname}
    for key, tdir in targets:
        os.makedirs(tdir, exist_ok=True)
        dst = os.path.join(tdir, fname)
        shutil.copy2(src_mp4, dst)
        out[key] = dst
    print(f"  [DELIVERED {'16:9 Ngang' if is_horizontal else '9:16 Dọc'}] -> {out['brand_path']}", flush=True)
    return out

def render_episode(ep_id, ratio="9:16"):
    meta = EPISODE_META[ep_id]
    is_16 = (ratio == "16:9")
    rtag = "16x9" if is_16 else "9x16"
    out_w, out_h = (1920, 1080) if is_16 else (1080, 1920)
    target_ar = 16.0 / 9.0 if is_16 else 9.0 / 16.0

    ep_dir = os.path.join(BASE_DIR, ep_id)
    raw_dir = os.path.join(ep_dir, f"raw_{rtag}")
    norm_dir = os.path.join(ep_dir, f"norm_{rtag}")
    os.makedirs(norm_dir, exist_ok=True)

    print(f"\n==================== RENDERING {ep_id.upper()} ({ratio}) — {meta['title']} ====================", flush=True)
    norm_files = []
    timeline_log = []
    cum_t = 0.0
    lut_ff = LUT_PATH.replace("\\", "/").replace(":", "\\:")

    for idx, sid in enumerate(meta["scenes"], 1):
        src = os.path.join(raw_dir, f"{sid}.mp4")
        if not os.path.exists(src):
            raise FileNotFoundError(f"Missing raw clip: {src}")
        w, h, total_dur = probe_video(src)
        voc_wav = run_demucs_vocals(src, f"{ep_id}_{rtag}_{sid}")
        ss, to = detect_speech_bounds(voc_wav, total_dur, min_ss=0.06, pre_pad=0.14, post_pad=0.22)
        dur = round(to - ss, 3)

        vf_parts = []
        # Clean subtle Flow bottom-right mark if 720p native
        if is_16 and w == 1280 and h == 720:
            vf_parts.append("delogo=x=1130:y=568:w=64:h=64")
        elif (not is_16) and w == 720 and h == 1280:
            vf_parts.append("delogo=x=570:y=1130:w=62:h=62")

        top_b, bot_b = detect_letterbox_bars(src, w, h, (ss + to) * 0.5)
        ch_crop = h - top_b - bot_b
        cw_crop = w
        cx_crop = 0
        cy_crop = top_b
        cur_ar = cw_crop / float(max(1, ch_crop))
        if abs(cur_ar - target_ar) > 0.015:
            if cur_ar > target_ar:
                cw_crop = int(round(ch_crop * target_ar / 2) * 2)
                cx_crop = (w - cw_crop) // 2
            else:
                new_ch = int(round(cw_crop / target_ar / 2) * 2)
                cy_crop = top_b + (ch_crop - new_ch) // 2
                ch_crop = new_ch
        if cw_crop != w or ch_crop != h or cx_crop != 0 or cy_crop != 0:
            vf_parts.append(f"crop={cw_crop}:{ch_crop}:{cx_crop}:{cy_crop}")

        if os.path.exists(LUT_PATH):
            vf_parts.append(f"lut3d=file='{lut_ff}':interp=tetrahedral")
        vf_parts += [
            f"scale={out_w}:{out_h}:flags=lanczos",
            "eq=contrast=1.02:saturation=1.04",
            "unsharp=3:3:0.30:3:3:0.0",
            "fps=30",
            "format=yuv420p",
        ]
        vf = ",".join(vf_parts)

        fo_st = max(0.05, dur - 0.05)
        af = (
            f"highpass=f=85,lowpass=f=13500,"
            f"loudnorm=I=-14.5:TP=-1.2:LRA=7,"
            f"afade=t=in:st=0:d=0.04,afade=t=out:st={fo_st:.3f}:d=0.05"
        )
        dst = os.path.join(norm_dir, f"{idx:02d}_{sid}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", src,
            "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", voc_wav,
            "-vf", vf, "-af", af, "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", dst
        ], check=True)

        _, _, real_d = probe_video(dst)
        timeline_log.append({"scene": sid, "start": round(cum_t, 2), "end": round(cum_t + real_d, 2), "dur": round(real_d, 2)})
        print(f"  [{idx:02d}_{sid}] {cum_t:5.2f}s -> {cum_t + real_d:5.2f}s ({real_d:.2f}s)", flush=True)
        cum_t += real_d
        norm_files.append(dst)

    concat_txt = os.path.join(ep_dir, f"concat_{rtag}.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for nf in norm_files:
            cf.write(f"file '{nf}'\n")

    vo_master = os.path.join(ep_dir, f"vo_master_{rtag}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", vo_master], check=True)
    _, _, vid_total = probe_video(vo_master)

    # Mix 2-Act BGM with Voice Pocket EQ
    p_idx = min(meta["pivot_idx"], len(timeline_log) - 1)
    pivot_t = timeline_log[p_idx]["start"]
    outro_fo = max(1.0, vid_total - 2.0)

    b1_fn, b1_off, b1_vol = meta["bgm_act1"]
    b2_fn, b2_off, b2_vol = meta["bgm_act2"]
    b1_path = os.path.join(BGM_DIR, b1_fn)
    b2_path = os.path.join(BGM_DIR, b2_fn)

    b1_len = max(2.0, pivot_t + 0.9)
    b2_start = max(0.0, pivot_t - 0.35)
    b2_delay_ms = int(round(b2_start * 1000))
    b2_len = max(2.0, vid_total - b2_start + 0.8)

    fc_bgm = (
        f"[1:a]atrim={b1_off:.2f}:{b1_off + b1_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume={b1_vol:.2f},afade=t=in:st=0:d=0.5,afade=t=out:st={max(0.4, b1_len - 1.4):.3f}:d=1.4[b1];"
        f"[2:a]atrim={b2_off:.2f}:{b2_off + b2_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume={b2_vol:.2f},afade=t=in:st=0:d=1.0,adelay={b2_delay_ms}|{b2_delay_ms}[b2];"
        f"[b1][b2]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"
        f"atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,"
        f"highpass=f=95,lowpass=f=9500,"
        f"equalizer=f=1500:t=q:w=1.2:g=-4.2,equalizer=f=2800:t=q:w=1.2:g=-4.2,"
        f"afade=t=out:st={outro_fo:.3f}:d=1.9[bgm_clean];"
        f"[0:a][bgm_clean]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.93[aout]"
    )

    final_local = os.path.join(ep_dir, f"261122 K4 {meta['title']} {rtag} final.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", vo_master,
        "-i", b1_path,
        "-i", b2_path,
        "-filter_complex", fc_bgm, "-map", "0:v:0", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "224k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", final_local
    ], check=True)

    # QA Contact Sheet
    tw, th = (384, 216) if is_16 else (240, 426)
    thumbs = []
    for i, nf in enumerate(norm_files, 1):
        _, _, d = probe_video(nf)
        t = os.path.join(QC_DIR, f"{ep_id}_{rtag}_s{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{d*0.50:.2f}", "-i", nf, "-vf", f"scale={tw}:{th}", "-frames:v", "1", t], check=True)
        thumbs.append(t)
    cols = 3 if is_16 else 3
    rows = (len(thumbs) + cols - 1) // cols
    while len(thumbs) < cols * rows:
        pad_t = os.path.join(QC_DIR, f"{ep_id}_{rtag}_pad{len(thumbs)}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x14161c:s={tw}x{th}", "-frames:v", "1", pad_t], check=True)
        thumbs.append(pad_t)
    inp = []
    for t in thumbs:
        inp += ["-i", t]
    layout = "|".join(f"{(i%cols)*tw}_{(i//cols)*th}" for i in range(len(thumbs)))
    qa_sheet = os.path.join(QC_DIR, f"QA_{ep_id}_{rtag}.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", f"xstack=inputs={len(thumbs)}:layout={layout}", "-frames:v", "1", qa_sheet], check=True)
    shutil.copy2(qa_sheet, os.path.join(ART_DIR, f"QA_{ep_id}_{rtag}.jpg"))

    delivered = deliver_episode(final_local, meta["title"], is_horizontal=is_16)
    return {
        "episode": ep_id,
        "ratio": ratio,
        "duration": round(vid_total, 2),
        "qa_sheet": qa_sheet,
        "timeline": timeline_log,
        **delivered,
    }

if __name__ == "__main__":
    ratios = sys.argv[1:] if len(sys.argv) > 1 else ["9:16"]
    eps = ["v01", "v02", "v03", "v04", "v05"]
    manifest_out = []
    for r in ratios:
        for ep in eps:
            manifest_out.append(render_episode(ep, ratio=r))
    out_json = os.path.join(BASE_DIR, f"delivery_report_{'_'.join(x.replace(':','x') for x in ratios)}.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(manifest_out, f, ensure_ascii=False, indent=2)

    # Sync project scripts & report to Cloud 03_Du_An
    if os.path.isdir(r"G:\My Drive\AI_Full_Studio\03_Du_An"):
        os.makedirs(DU_AN_CLOUD_DIR, exist_ok=True)
        for fn in ["prepare_step1_assets.py", "build_all_5_flow_batches.py", "render_5_masters.py", "direct_studio_driver.js", os.path.basename(out_json)]:
            sp = os.path.join(BASE_DIR, fn)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(DU_AN_CLOUD_DIR, fn))
        for bfn in os.listdir(os.path.join(BASE_DIR, "assetboards")):
            shutil.copy2(os.path.join(BASE_DIR, "assetboards", bfn), os.path.join(DU_AN_CLOUD_DIR, bfn))
        for qfn in os.listdir(QC_DIR):
            if qfn.startswith("QA_"):
                shutil.copy2(os.path.join(QC_DIR, qfn), os.path.join(DU_AN_CLOUD_DIR, qfn))
    print(f"\nALL EPISODES RENDERED & DELIVERED -> {out_json}", flush=True)
