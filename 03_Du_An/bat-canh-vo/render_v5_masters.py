import json, os, shutil, subprocess, sys, wave
import numpy as np

PROJ_DIR   = r"d:\AI\full studio\output\bat-canh-vo"
V5_16X9    = os.path.join(PROJ_DIR, "v5_raw_16x9")
V5_9X16    = os.path.join(PROJ_DIR, "v5_raw_9x16")
DEMUCS_DIR = os.path.join(PROJ_DIR, "v5_demucs")
QC_DIR     = os.path.join(PROJ_DIR, "qc_v5")
BGM_DIR    = os.path.join(PROJ_DIR, "bgm")
ART_DIR    = r"C:\Users\Hang thu\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
DEMUCS_PY  = r"D:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
SMASH_SFX  = os.path.join(PROJ_DIR, "qc", "real_ceramic_smash.mp3")

for d in (DEMUCS_DIR, QC_DIR):
    os.makedirs(d, exist_ok=True)

SHOT_ORDER = [
    ("d01", "voice"),
    ("d02", "smash"),
    ("d03", "voice"),
    ("d04", "voice"),
    ("d05", "voice"),
    ("d06", "voice"),
    ("d07", "voice"),
    ("d08", "voice"),
    ("d09", "voice"),
    ("d10", "smirk"),
    ("d11", "voice"),
]

def probe_video(p):
    j = json.loads(subprocess.check_output([
        "ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=width,height:format=duration","-of","json",p
    ]).decode())
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])

def detect_letterbox_bars_asymmetric(mp4_path, w, h, t_mid):
    """Independently detect top and bottom black bars so asymmetric letterboxes crop 100% cleanly."""
    raw = subprocess.check_output([
        "ffmpeg","-v","error","-ss",f"{t_mid:.2f}","-i",mp4_path,
        "-frames:v","1","-pix_fmt","gray","-f","rawvideo","-"
    ])
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w))
    row_means = arr.mean(axis=1)
    top_b = 0
    while top_b < h // 4 and row_means[top_b] < 16.0:
        top_b += 1
    bot_b = 0
    while bot_b < h // 4 and row_means[h - 1 - bot_b] < 16.0:
        bot_b += 1
    top_b = ((top_b + 1) // 2) * 2 if top_b >= 4 else 0
    bot_b = ((bot_b + 1) // 2) * 2 if bot_b >= 4 else 0
    return top_b, bot_b

def run_demucs_vocals(mp4_path, tag_key):
    """Isolate 100% pure human vocals on RTX 3060 GPU using Demucs htdemucs --two-stems=vocals."""
    out_wav = os.path.join(DEMUCS_DIR, f"{tag_key}_vocals.wav")
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 20_000:
        return out_wav
    raw_wav = os.path.join(DEMUCS_DIR, f"{tag_key}.wav")
    subprocess.run([
        "ffmpeg","-y","-v","error","-i",mp4_path,"-vn","-ac","2","-ar","44100",raw_wav
    ], check=True)
    subprocess.run([
        DEMUCS_PY, "-m", "demucs.separate",
        "-n", "htdemucs", "--two-stems=vocals", "-d", "cuda",
        "-o", DEMUCS_DIR, raw_wav
    ], check=True)
    sep_voc = os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "vocals.wav")
    assert os.path.exists(sep_voc), f"Demucs vocals missing: {sep_voc}"
    shutil.copy2(sep_voc, out_wav)
    return out_wav

def detect_speech_bounds(vocals_wav, total_dur, min_ss=0.06, pre_pad=0.14, post_pad=0.22):
    """Find exact first & last spoken syllable on isolated Demucs vocal stem."""
    with wave.open(vocals_wav, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        pcm = pcm.reshape(-1, nch).mean(axis=1)
    win = int(sr * 0.025)
    n_frames = len(pcm) // win
    if n_frames < 4:
        return min_ss, max(min_ss + 0.8, total_dur - 0.08)
    rms = np.sqrt(np.mean(pcm[:n_frames * win].reshape(n_frames, win) ** 2, axis=1))
    min_idx = int(min_ss / 0.025)
    peak_rms = float(np.max(rms[min_idx:])) if min_idx < len(rms) else float(np.max(rms))
    thr = max(0.012, peak_rms * 0.10)
    active = np.where(rms[min_idx:] >= thr)[0] + min_idx
    if len(active) == 0:
        return min_ss, max(min_ss + 1.0, total_dur - 0.10)
    t_first = active[0] * 0.025
    t_last  = (active[-1] + 1) * 0.025
    ss = max(min_ss, t_first - pre_pad)
    to = min(total_dur - 0.04, t_last + post_pad)
    if to - ss < 1.2:
        to = min(total_dur - 0.04, ss + 1.5)
    return round(ss, 3), round(to, 3)

def render_ratio_master(ratio: str):
    is_16 = (ratio == "16:9")
    raw_dir  = V5_16X9 if is_16 else V5_9X16
    norm_dir = os.path.join(PROJ_DIR, "v5_norm_16x9" if is_16 else "v5_norm_9x16")
    os.makedirs(norm_dir, exist_ok=True)
    out_w, out_h = (1920, 1080) if is_16 else (1080, 1920)
    rtag = "16x9" if is_16 else "9x16"

    print(f"\n==================== BUILDING V5 MASTER ({ratio} -> {out_w}x{out_h}) ====================", flush=True)
    norm_files = []
    timeline_log = []
    cum_t = 0.0

    for idx, (sid, mode) in enumerate(SHOT_ORDER, 1):
        src = os.path.join(raw_dir, f"{sid}.mp4")
        assert os.path.exists(src), f"Missing {src}"
        w, h, total_dur = probe_video(src)
        dst = os.path.join(norm_dir, f"{idx:02d}_{sid}.mp4")

        if mode == "voice":
            voc_wav = run_demucs_vocals(src, f"{rtag}_{sid}")
            # On 9:16 d03, skip pre-speech noise before 0.92s; on d06 keep 0.55s pre-pad so worry->shock eye-widening plays cleanly!
            min_ss = 0.92 if (not is_16 and sid == "d03") else 0.06
            pre_p  = 0.60 if sid == "d06" else 0.14
            ss, to = detect_speech_bounds(voc_wav, total_dur, min_ss=min_ss, pre_pad=pre_p, post_pad=0.22)
            # For d06, ensure we start from ~0.12s so the full silent facial shift (worry -> stunned wide eyes) is shown!
            if sid == "d06":
                ss = min(ss, 0.15)
        elif mode == "smash":
            if is_16:
                # 16:9 Muse d02_alt.mp4 (5.0s): 0.08s -> 2.78s at 1.18x speed -> 2.29s snappy shove + mid-air drop + crown shatter!
                ss, to, spd, imp_raw = 0.08, 2.78, 1.18, 1.98
            else:
                # 9:16 Muse d02.mp4 (10.0s): 1.35s -> 5.05s at 1.55x speed -> 2.39s snappy shove + vertical drop + shatter!
                ss, to, spd, imp_raw = 1.35, 5.05, 1.55, 3.92
        elif mode == "smirk":
            if is_16:
                ss, to = 1.15, 3.85
            else:
                ss, to = 0.85, 3.65

        dur = round(to - ss, 3)

        vf_parts = []
        if mode != "smash":
            if is_16 and w == 1280 and h == 720:
                vf_parts.append("delogo=x=1130:y=568:w=64:h=64,delogo=x=1130:y=520:w=64:h=56")
                top_b, bot_b = detect_letterbox_bars_asymmetric(src, w, h, (ss + to) * 0.5)
                if sid == "d05":
                    # Cleanly crop out bottom-right VTVgo mark (y=666..698) without any blur!
                    bot_b = max(bot_b, 58)
                if top_b > 0 or bot_b > 0:
                    ch = h - top_b - bot_b
                    cw = int(round(ch * 16.0 / 9.0 / 2) * 2)
                    cx = (w - cw) // 2
                    vf_parts.append(f"crop={cw}:{ch}:{cx}:{top_b}")
            elif (not is_16) and w == 720 and h == 1280:
                vf_parts.append("delogo=x=570:y=1130:w=62:h=62")
        else:
            target_ar = 16.0 / 9.0 if is_16 else 9.0 / 16.0
            cur_ar = w / float(h)
            if abs(cur_ar - target_ar) > 0.015:
                if cur_ar > target_ar:
                    cw = int(round(h * target_ar / 2) * 2)
                    vf_parts.append(f"crop={cw}:{h}:{(w-cw)//2}:0")
                else:
                    ch = int(round(w / target_ar / 2) * 2)
                    vf_parts.append(f"crop={w}:{ch}:0:{(h-ch)//2}")
            vf_parts.append(f"setpts=PTS/{spd:.3f}")

        vf_parts += [
            f"scale={out_w}:{out_h}:flags=lanczos",
            "eq=contrast=1.03:saturation=1.05",
            "fps=30",
            "format=yuv420p",
        ]
        vf = ",".join(vf_parts)

        if mode == "voice":
            voc_wav = run_demucs_vocals(src, f"{rtag}_{sid}")
            fo_st = max(0.05, dur - 0.05)
            af = (
                f"highpass=f=85,lowpass=f=13500,"
                f"loudnorm=I=-14.5:TP=-1.2:LRA=7,"
                f"afade=t=in:st=0:d=0.04,afade=t=out:st={fo_st:.3f}:d=0.05"
            )
            subprocess.run([
                "ffmpeg","-y","-v","error",
                "-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",src,
                "-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",voc_wav,
                "-vf",vf,"-af",af,"-map","0:v:0","-map","1:a:0",
                "-c:v","h264_nvenc","-preset","p5","-rc","vbr","-cq","18","-b:v","0",
                "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst
            ], check=True)
        elif mode == "smirk":
            if not is_16:
                # Keep Mẹ Tuấn's subtle sinister chuckle on 9:16 isolated via Demucs!
                voc_wav = run_demucs_vocals(src, f"{rtag}_{sid}")
                fo_st = max(0.05, dur - 0.08)
                af = f"highpass=f=100,lowpass=f=11000,volume=0.85,afade=t=in:st=0:d=0.08,afade=t=out:st={fo_st:.3f}:d=0.10"
                subprocess.run([
                    "ffmpeg","-y","-v","error",
                    "-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",src,
                    "-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",voc_wav,
                    "-vf",vf,"-af",af,"-map","0:v:0","-map","1:a:0",
                    "-c:v","h264_nvenc","-preset","p5","-rc","vbr","-cq","18","-b:v","0",
                    "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst
                ], check=True)
            else:
                subprocess.run([
                    "ffmpeg","-y","-v","error",
                    "-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",src,
                    "-f","lavfi","-t",f"{dur:.3f}","-i","anullsrc=r=48000:cl=stereo",
                    "-vf",vf,"-map","0:v:0","-map","1:a:0",
                    "-c:v","h264_nvenc","-preset","p5","-rc","vbr","-cq","18","-b:v","0",
                    "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst
                ], check=True)
        elif mode == "smash":
            out_dur = dur / spd
            imp_rel = (imp_raw - ss) / spd
            delay_ms = max(0, int(round((imp_rel - 0.04) * 1000)))
            fc_sm = (
                f"[0:a]atempo={spd:.3f},volume=0.70,afade=t=in:st=0:d=0.04,afade=t=out:st={max(0.1, out_dur-0.16):.3f}:d=0.15[ma];"
                f"[1:a]atrim=0.24:1.35,asetpts=PTS-STARTPTS,volume=1.15,afade=t=out:st=0.80:d=0.25,adelay={delay_ms}|{delay_ms}[sa];"
                f"[ma][sa]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
            )
            subprocess.run([
                "ffmpeg","-y","-v","error",
                "-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",src,
                "-i",SMASH_SFX,
                "-vf",vf,"-filter_complex",fc_sm,"-map","0:v:0","-map","[aout]",
                "-c:v","h264_nvenc","-preset","p5","-rc","vbr","-cq","18","-b:v","0",
                "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst
            ], check=True)

        _, _, real_d = probe_video(dst)
        timeline_log.append((sid, cum_t, cum_t + real_d, real_d, ss, to))
        print(f"  [{idx:02d}_{sid}] raw({ss:.2f}->{to:.2f}s) | timeline {cum_t:5.2f}s -> {cum_t+real_d:5.2f}s ({real_d:.2f}s)", flush=True)
        cum_t += real_d
        norm_files.append(dst)

    concat_txt = os.path.join(PROJ_DIR, f"v5_concat_{rtag}.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for nf in norm_files:
            cf.write(f"file '{nf}'\n")

    vo_master = os.path.join(PROJ_DIR, f"v5_vo_track_{rtag}.mp4")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",concat_txt,"-c","copy",vo_master], check=True)
    _, _, vid_total = probe_video(vo_master)

    # Pivot at start of d08 (index 7: Thảo bursts into tears defending herself!)
    pivot_t = timeline_log[7][1]
    outro_fo = max(1.0, vid_total - 2.0)

    BGM_TENSION = os.path.join(BGM_DIR, "dram_quiet_tension.mp3")
    BGM_PIANO   = os.path.join(BGM_DIR, "sad_ltk_piano.mp3")

    b1_len = min(41.5, pivot_t + 1.0)
    b2_start_timeline = max(0.0, pivot_t - 0.5)
    b2_delay_ms = int(round(b2_start_timeline * 1000))
    b2_len = min(29.0, vid_total - b2_start_timeline + 0.5)

    fc_bgm = (
        f"[1:a]atrim=3.0:{3.0 + b1_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume=0.25,afade=t=in:st=0:d=0.5,afade=t=out:st={max(0.5, b1_len - 1.6):.3f}:d=1.6[b1];"
        f"[2:a]atrim=15.5:{15.5 + b2_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume=0.27,afade=t=in:st=0:d=1.4,adelay={b2_delay_ms}|{b2_delay_ms}[b2];"
        f"[b1][b2]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"
        f"atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,"
        f"highpass=f=95,lowpass=f=9500,"
        f"equalizer=f=1500:t=q:w=1.2:g=-4.0,equalizer=f=2800:t=q:w=1.2:g=-4.0,"
        f"afade=t=out:st={outro_fo:.3f}:d=1.9[bgm_clean];"
        f"[0:a][bgm_clean]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.93[aout]"
    )

    final_local = os.path.join(PROJ_DIR, f"261120 K4 Bát canh vỡ {rtag} v5 final.mp4")
    subprocess.run([
        "ffmpeg","-y","-v","error",
        "-i",vo_master,
        "-i",BGM_TENSION,
        "-i",BGM_PIANO,
        "-filter_complex",fc_bgm,"-map","0:v:0","-map","[aout]",
        "-c:v","copy","-c:a","aac","-b:a","224k","-ar","48000","-ac","2","-movflags","+faststart",final_local
    ], check=True)

    tw, th = (384, 216) if is_16 else (216, 384)
    thumbs = []
    for i, nf in enumerate(norm_files, 1):
        _, _, d = probe_video(nf)
        t = os.path.join(QC_DIR, f"{rtag}_s{i:02d}.jpg")
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{d*0.52:.2f}","-i",nf,"-vf",f"scale={tw}:{th}","-frames:v","1",t], check=True)
        thumbs.append(t)
    pad_t = os.path.join(QC_DIR, f"{rtag}_pad.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-f","lavfi","-i",f"color=c=0x111111:s={tw}x{th}","-frames:v","1",pad_t], check=True)
    thumbs.append(pad_t)
    cols = 3 if is_16 else 4
    inp = []
    for t in thumbs: inp += ["-i", t]
    layout = "|".join(f"{(i%cols)*tw}_{(i//cols)*th}" for i in range(12))
    qa_sheet = os.path.join(QC_DIR, f"qa_v5_{rtag}.jpg")
    subprocess.run(["ffmpeg","-y","-v","error"] + inp + ["-filter_complex",f"xstack=inputs=12:layout={layout}","-frames:v","1",qa_sheet], check=True)
    shutil.copy2(qa_sheet, os.path.join(ART_DIR, f"qa_v5_{rtag}.jpg"))

    pw, ph = (512, 288) if is_16 else (288, 512)
    prev_mp4 = os.path.join(QC_DIR, f"preview_v5_{rtag}.mp4")
    subprocess.run([
        "ffmpeg","-y","-v","error","-i",final_local,
        "-vf",f"scale={pw}:{ph}","-c:v","h264_nvenc","-cq","27","-c:a","aac","-b:a","128k",prev_mp4
    ], check=True)

    print(f"[MASTER {ratio} READY] {final_local} ({vid_total:.2f}s) | Preview: {prev_mp4}", flush=True)
    return final_local, prev_mp4, qa_sheet, timeline_log

if __name__ == "__main__":
    ratios = sys.argv[1:] if len(sys.argv) > 1 else ["16:9", "9:16"]
    for r in ratios:
        render_ratio_master(r)
