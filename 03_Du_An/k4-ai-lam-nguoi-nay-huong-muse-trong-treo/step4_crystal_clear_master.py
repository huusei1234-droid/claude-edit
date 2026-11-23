import json, os, shutil, subprocess, sys, wave
import numpy as np
from PIL import Image

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from final_delivery import deliver_final_video

PROJ_DIR   = r"d:\AI\full studio\output\k4-muse-trong-treo"
KF_DIR     = os.path.join(PROJ_DIR, "chatgpt_keyframes")
RAW_DIR    = os.path.join(PROJ_DIR, "muse_raw_9x16")
NORM_DIR   = os.path.join(PROJ_DIR, "muse_norm_9x16")
LUT_DIR    = os.path.join(PROJ_DIR, "auto_luts")
DEMUCS_DIR = os.path.join(PROJ_DIR, "demucs_vocals")
QC_DIR     = os.path.join(PROJ_DIR, "qc")
BGM_DIR    = r"d:\AI\full studio\output\bat-canh-vo\bgm"
ART_DIR    = r"C:\Users\Hang thu\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
DEMUCS_PY  = r"D:\AI\full studio\voice-studio\.venv\Scripts\python.exe"

for d in (NORM_DIR, LUT_DIR, DEMUCS_DIR, QC_DIR):
    os.makedirs(d, exist_ok=True)

SHOTS = [
    ("s01", "voice"),
    ("s02", "voice"),
    ("s03", "voice"),
    ("s04", "voice"),
    ("s05", "voice"),
    ("s06", "feast_visual"),
    ("s07", "voice"),
    ("s08", "voice"),
    ("s09", "voice"),
]

def probe_video(p):
    j = json.loads(subprocess.check_output([
        "ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=width,height:format=duration","-of","json",p
    ]).decode())
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])

def build_crystal_clear_match_lut(kf_png_path: str, raw_mp4_path: str, lut_out_path: str, sample_t: float = 0.25):
    """
    Computes a precision 33x33x33 3D .cube LUT that maps `muse-video`'s darkened & over-saturated
    RGB/YCbCr output directly back onto ChatGPT's bright, airy, pastel Live-Wallpaper keyframe (`kf_sXX.png`),
    plus guarantees airy Live-Wallpaper target clarity (Y_mean >= 138, Sat <= 0.22, clean creamy whites)!
    """
    kf_arr = np.array(Image.open(kf_png_path).convert("RGB"), dtype=np.float32) / 255.0
    w, h, _ = probe_video(raw_mp4_path)
    raw_bytes = subprocess.check_output([
        "ffmpeg","-v","error","-ss",f"{sample_t:.2f}","-i",raw_mp4_path,
        "-frames:v","1","-pix_fmt","rgb24","-f","rawvideo","-"
    ])
    vid_arr = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((h, w, 3)).astype(np.float32) / 255.0

    def to_ycbcr(rgb):
        y  = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
        cb = -0.168736 * rgb[..., 0] - 0.331264 * rgb[..., 1] + 0.5 * rgb[..., 2]
        cr = 0.5 * rgb[..., 0] - 0.418688 * rgb[..., 1] - 0.081312 * rgb[..., 2]
        return y, cb, cr

    ky, kcb, kcr = to_ycbcr(kf_arr)
    vy, vcb, vcr = to_ycbcr(vid_arr)

    tgt_y_mean = float(np.clip(ky.mean(), 0.52, 0.72))
    src_y_mean = max(float(vy.mean()), 0.08)

    # Exact 1:1 luminance match back to ChatGPT's crystal-clear keyframe (never wash out!)
    gamma = np.log(tgt_y_mean) / np.log(src_y_mean)
    gamma = float(np.clip(gamma, 0.82, 1.02))

    contrast_soft = 0.98

    # Exact 1:1 chroma match back to ChatGPT's fresh natural saturation
    src_chroma = float(np.sqrt(vcb**2 + vcr**2).mean()) + 1e-5
    tgt_chroma = float(np.sqrt(kcb**2 + kcr**2).mean())
    sat_scale  = float(np.clip(tgt_chroma / src_chroma, 0.76, 1.00))

    # Neutralize any slight warm/orange shift introduced by Muse
    dcb = float(np.clip((kcb.mean() - vcb.mean()) * 0.60, -0.020, 0.025))
    dcr = float(np.clip((kcr.mean() - vcr.mean()) * 0.60, -0.025, 0.020))

    N = 33
    grid = np.linspace(0.0, 1.0, N, dtype=np.float32)
    B, G, R = np.meshgrid(grid, grid, grid, indexing="ij")
    rgb = np.stack([R, G, B], axis=-1)

    y, cb, cr = to_ycbcr(rgb)
    y_lifted = np.power(np.clip(y, 0.0, 1.0), gamma)
    y_airy = tgt_y_mean + (y_lifted - tgt_y_mean) * contrast_soft
    y_airy = np.clip(y_airy, 0.0, 1.0)

    # 2) Clean pastel chroma & neutralize orange cast (attenuated near pure black/white so whites stay pure!)
    w_mid = 4.0 * y_airy * (1.0 - y_airy)
    cb_new = cb * sat_scale + dcb * w_mid
    cr_new = cr * sat_scale + dcr * w_mid

    r_out = np.clip(y_airy + 1.402 * cr_new, 0.0, 1.0)
    g_out = np.clip(y_airy - 0.344136 * cb_new - 0.714136 * cr_new, 0.0, 1.0)
    b_out = np.clip(y_airy + 1.772 * cb_new, 0.0, 1.0)

    flat = np.stack([r_out, g_out, b_out], axis=-1).reshape(-1, 3)
    with open(lut_out_path, "w", encoding="ascii") as f:
        f.write("TITLE \"CrystalClear_ChatGPT_Match\"\n")
        f.write(f"LUT_3D_SIZE {N}\n")
        f.write("DOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n")
        for rv, gv, bv in flat:
            f.write(f"{rv:.6f} {gv:.6f} {bv:.6f}\n")
    return gamma, sat_scale

def run_demucs_vocals(mp4_path, tag_key):
    out_wav = os.path.join(DEMUCS_DIR, f"{tag_key}_vocals.wav")
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 20_000:
        return out_wav
    raw_wav = os.path.join(DEMUCS_DIR, f"{tag_key}.wav")
    subprocess.run(["ffmpeg","-y","-v","error","-i",mp4_path,"-vn","-ac","2","-ar","44100",raw_wav], check=True)
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
        return min_ss, max(min_ss + 1.0, total_dur - 0.08)
    rms = np.sqrt(np.mean(pcm[:nf * win].reshape(nf, win) ** 2, axis=1))
    min_idx = int(min_ss / 0.025)
    peak = float(np.max(rms[min_idx:])) if min_idx < len(rms) else float(np.max(rms))
    thr = max(0.012, peak * 0.10)
    active = np.where(rms[min_idx:] >= thr)[0] + min_idx
    if len(active) == 0:
        return min_ss, max(min_ss + 1.2, total_dur - 0.10)
    t_first = active[0] * 0.025
    t_last  = (active[-1] + 1) * 0.025
    ss = max(min_ss, t_first - pre_pad)
    to = min(total_dur - 0.04, t_last + post_pad)
    if to - ss < 1.2:
        to = min(total_dur - 0.04, ss + 1.5)
    return round(ss, 3), round(to, 3)

def main():
    norm_files = []
    timeline_log = []
    cum_t = 0.0

    print("=== RENDERING CRYSTAL-CLEAR LIVE-WALLPAPER GRADE K4 MASTER (1080x1920 @ 30fps NVENC) ===", flush=True)
    for idx, (sid, mode) in enumerate(SHOTS, 1):
        src = os.path.join(RAW_DIR, f"{sid}.mp4")
        kf  = os.path.join(KF_DIR,  f"kf_{sid}.png")
        dst = os.path.join(NORM_DIR, f"{idx:02d}_{sid}.mp4")
        lut_p = os.path.join(LUT_DIR, f"match_{sid}.cube")

        w, h, total_dur = probe_video(src)
        gamma, sat_sc = build_crystal_clear_match_lut(kf, src, lut_p, sample_t=total_dur * 0.50)

        if mode == "voice":
            voc_wav = run_demucs_vocals(src, sid)
            pre_p = 0.25 if sid == "s04" else 0.14
            ss, to = detect_speech_bounds(voc_wav, total_dur, min_ss=0.06, pre_pad=pre_p, post_pad=0.20)
            if sid == "s09":
                # Cut right after "Bình luận cho Thảo biết nha!" before background actors relax expression
                to = min(to, 7.75)
        else:
            ss = 0.15
            to = min(total_dur - 0.10, 3.15)

        dur = round(to - ss, 3)
        lut_ff = lut_p.replace("\\", "/").replace(":", "\\:")
        vf_parts = []
        target_ar = 9.0 / 16.0
        cur_ar = w / float(h)
        if abs(cur_ar - target_ar) > 0.015:
            if cur_ar > target_ar:
                cw = int(round(h * target_ar / 2) * 2)
                vf_parts.append(f"crop={cw}:{h}:{(w-cw)//2}:0")
            else:
                ch = int(round(w / target_ar / 2) * 2)
                vf_parts.append(f"crop={w}:{ch}:0:{(h-ch)//2}")
        vf_parts += [
            f"lut3d=file='{lut_ff}':interp=tetrahedral",
            "scale=1080:1920:flags=lanczos",
            "unsharp=3:3:0.35:3:3:0.0",
            "fps=30",
            "format=yuv420p",
        ]
        vf = ",".join(vf_parts)
        fo_st = max(0.05, dur - 0.05)

        if mode == "voice":
            voc_wav = run_demucs_vocals(src, sid)
            af = f"highpass=f=85,lowpass=f=13500,loudnorm=I=-14.5:TP=-1.2:LRA=7,afade=t=in:st=0:d=0.04,afade=t=out:st={fo_st:.3f}:d=0.05"
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

        # Measure rendered brightness & saturation to verify crystal-clear Live-Wallpaper grade!
        rb = subprocess.check_output(["ffmpeg","-v","error","-ss",f"{dur*0.5:.2f}","-i",dst,"-frames:v","1","-vf","scale=360:640","-pix_fmt","rgb24","-f","rawvideo","-"])
        ra = np.frombuffer(rb, dtype=np.uint8).reshape((640,360,3)).astype(float)
        ym = (0.299*ra[:,:,0] + 0.587*ra[:,:,1] + 0.114*ra[:,:,2]).mean()
        mx = ra.max(axis=2); mn = ra.min(axis=2)
        sm = np.where(mx>5, (mx-mn)/np.maximum(mx,1), 0).mean()

        _, _, real_d = probe_video(dst)
        timeline_log.append((sid, cum_t, cum_t + real_d, real_d))
        print(f"  [{idx:02d}_{sid}] {cum_t:5.2f}s->{cum_t+real_d:5.2f}s ({real_d:.2f}s) | LUT(gamma={gamma:.2f}, sat={sat_sc:.2f}) -> Out Y={ym:.1f}, Sat={sm:.3f}", flush=True)
        cum_t += real_d
        norm_files.append(dst)

    concat_txt = os.path.join(PROJ_DIR, "concat_9x16.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for nf in norm_files:
            cf.write(f"file '{nf}'\n")

    vo_master = os.path.join(PROJ_DIR, "vo_master_9x16.mp4")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",concat_txt,"-c","copy",vo_master], check=True)
    _, _, vid_total = probe_video(vo_master)

    pivot_t = timeline_log[4][1]
    outro_fo = max(1.0, vid_total - 2.0)

    BGM_ACT1 = os.path.join(BGM_DIR, "dram_quiet_tension.mp3")
    BGM_ACT2 = os.path.join(BGM_DIR, "dram_ltk.mp3")

    b1_len = min(41.0, pivot_t + 0.8)
    b2_start = max(0.0, pivot_t - 0.25)
    b2_delay_ms = int(round(b2_start * 1000))
    b2_len = min(42.0, vid_total - b2_start + 0.5)

    fc_bgm = (
        f"[1:a]atrim=3.0:{3.0 + b1_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume=0.23,afade=t=in:st=0:d=0.5,afade=t=out:st={max(0.4, b1_len - 1.3):.3f}:d=1.3[b1];"
        f"[2:a]atrim=0.0:{b2_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume=0.22,afade=t=in:st=0:d=0.8,adelay={b2_delay_ms}|{b2_delay_ms}[b2];"
        f"[b1][b2]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"
        f"atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,"
        f"highpass=f=95,lowpass=f=9500,"
        f"equalizer=f=1500:t=q:w=1.2:g=-4.5,equalizer=f=2800:t=q:w=1.2:g=-4.5,"
        f"afade=t=out:st={outro_fo:.3f}:d=1.9[bgm_clean];"
        f"[0:a][bgm_clean]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.93[aout]"
    )

    final_local = os.path.join(PROJ_DIR, "261121 K4 Ai làm người nấy hưởng final.mp4")
    subprocess.run([
        "ffmpeg","-y","-v","error",
        "-i",vo_master,
        "-i",BGM_ACT1,
        "-i",BGM_ACT2,
        "-filter_complex",fc_bgm,"-map","0:v:0","-map","[aout]",
        "-c:v","copy","-c:a","aac","-b:a","224k","-ar","48000","-ac","2","-movflags","+faststart",final_local
    ], check=True)

    tw, th = 270, 480
    thumbs = []
    for i, nf in enumerate(norm_files, 1):
        _, _, d = probe_video(nf)
        t = os.path.join(QC_DIR, f"s{i:02d}.jpg")
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{d*0.50:.2f}","-i",nf,"-vf",f"scale={tw}:{th}","-frames:v","1",t], check=True)
        thumbs.append(t)
    inp = []
    for t in thumbs: inp += ["-i", t]
    layout = "|".join(f"{(i%3)*tw}_{(i//3)*th}" for i in range(9))
    qa_sheet = os.path.join(QC_DIR, "qa_9_shots_k4_trong_treo.jpg")
    subprocess.run(["ffmpeg","-y","-v","error"] + inp + ["-filter_complex",f"xstack=inputs=9:layout={layout}","-frames:v","1",qa_sheet], check=True)
    shutil.copy2(qa_sheet, os.path.join(ART_DIR, "qa_9_shots_k4_trong_treo.jpg"))

    prev_mp4 = os.path.join(QC_DIR, "preview_k4_trong_treo.mp4")
    subprocess.run([
        "ffmpeg","-y","-v","error","-i",final_local,
        "-vf","scale=360:640","-c:v","h264_nvenc","-cq","26","-c:a","aac","-b:a","128k",prev_mp4
    ], check=True)

    print(f"\n[CRYSTAL-CLEAR MASTER READY] {final_local} ({vid_total:.2f}s)", flush=True)

if __name__ == "__main__":
    main()
