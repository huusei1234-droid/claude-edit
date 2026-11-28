# -*- coding: utf-8 -*-
import os, sys, json, wave, struct, math, random, shutil, subprocess
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PROJ = r"C:\AI\full studio\projects\htpm_ai_swarm_auto_edit_261127"
FRAMES_DIR = os.path.join(PROJ, "assets", "preview_frames")
THUMBS_DIR = os.path.join(PROJ, "assets", "thumbs")
AUDIO_DIR = os.path.join(PROJ, "assets", "audio")
RENDERED_DIR = os.path.join(PROJ, "rendered_frames")
SFX_BUNDLE = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"

def prepare_real_chihang_source(src_video: str, start_sec: float = 0.0):
    print(f"=== 1. Extracting 18.0s @ 60fps from REAL Chi Hang video: {os.path.basename(src_video)} ===")
    os.makedirs(FRAMES_DIR, exist_ok=True)
    os.makedirs(THUMBS_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)

    # Extract 1080 60fps preview frames
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{start_sec:.2f}", "-t", "18.0", "-i", src_video,
        "-vf", "fps=60,scale=360:640:force_original_aspect_ratio=increase:flags=lanczos,crop=360:640",
        "-q:v", "3", os.path.join(FRAMES_DIR, "f_%04d.jpg")
    ], check=True)

    # Update 18 timeline filmstrip mini-thumbnails to match 100%
    for sec in range(18):
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{start_sec + sec + 0.35:.2f}", "-i", src_video,
            "-vf", "scale=90:56:force_original_aspect_ratio=increase,crop=90:56",
            "-frames:v", "1", os.path.join(THUMBS_DIR, f"strip_{sec:02d}.jpg")
        ], check=True)

    # Extract 18.0s 48kHz stereo wav
    vo_wav = os.path.join(AUDIO_DIR, "chihang_18s.wav")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{start_sec:.2f}", "-t", "18.0", "-i", src_video,
        "-ac", "2", "-ar", "48000", vo_wav
    ], check=True)

    # Compute 60fps L/R VU meter envelope + 220-bar waveform
    with wave.open(vo_wav, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        total_samples = wf.getnframes()
        raw_bytes = wf.readframes(total_samples)

    samples = struct.unpack(f"<{total_samples * nch}h", raw_bytes)
    env_l, env_r = [], []
    spf = sr // 60
    for f in range(1080):
        s0 = f * spf * nch
        s1 = min(len(samples), (f + 1) * spf * nch)
        if s1 <= s0:
            env_l.append(0.05); env_r.append(0.05)
            continue
        sl = samples[s0:s1:2]
        sr_ch = samples[s0+1:s1:2]
        rmsl = math.sqrt(sum(x*x for x in sl) / max(1, len(sl))) / 32768.0
        rmsr = math.sqrt(sum(x*x for x in sr_ch) / max(1, len(sr_ch))) / 32768.0
        env_l.append(round(min(1.0, rmsl * 3.8), 4))
        env_r.append(round(min(1.0, rmsr * 3.8), 4))

    waveform = []
    spb = max(1, (total_samples // 220) * nch)
    for b in range(220):
        s0 = b * spb
        s1 = min(len(samples), (b + 1) * spb)
        chunk = samples[s0:s1:4]
        pk = max((abs(x) for x in chunk), default=0) / 32768.0
        waveform.append(round(min(1.0, pk * 1.35), 3))

    data_obj = {"env_l": env_l, "env_r": env_r, "waveform": waveform}
    with open(os.path.join(PROJ, "assets", "audio_data.json"), "w", encoding="utf-8") as fp:
        json.dump(data_obj, fp)
    with open(os.path.join(PROJ, "assets", "audio_data_inline.js"), "w", encoding="utf-8") as fp:
        fp.write("window.AUDIO_DATA = " + json.dumps(data_obj) + ";\n")

    return vo_wav

def build_tactile_swarm_bed(out_bed_wav: str, duration_sec: float = 18.0):
    """Synthesize crisp, subtle stereo tactile mouse-clicks & mechanical keystroke micro-ticks across stereo field."""
    sr = 48000
    n_samples = int(sr * duration_sec)
    buf_l = [0.0] * n_samples
    buf_r = [0.0] * n_samples
    rng = random.Random(261127)

    # ~11 subtle tactile clicks/ticks per second panned naturally across L/R
    t = 0.08
    while t < duration_sec - 0.1:
        idx0 = int(t * sr)
        pan = rng.uniform(0.25, 0.75)
        amp = rng.uniform(0.035, 0.085)
        freq = rng.choice([1850.0, 2350.0, 2900.0, 3400.0, 1450.0])
        decay = rng.uniform(220.0, 420.0)
        click_len = min(int(0.018 * sr), n_samples - idx0)
        for k in range(click_len):
            dt = k / sr
            val = amp * math.exp(-dt * decay) * (
                0.7 * math.sin(2 * math.pi * freq * dt) +
                0.3 * math.sin(2 * math.pi * (freq * 1.9) * dt)
            )
            buf_l[idx0 + k] += val * (1.0 - pan * 0.5)
            buf_r[idx0 + k] += val * (0.5 + pan * 0.5)
        t += rng.uniform(0.055, 0.145)

    pcm = bytearray(n_samples * 4)
    for i in range(n_samples):
        vl = max(-32767, min(32767, int(buf_l[i] * 32767)))
        vr = max(-32767, min(32767, int(buf_r[i] * 32767)))
        struct.pack_into("<hh", pcm, i * 4, vl, vr)

    with wave.open(out_bed_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm)

def mix_master_audio(vo_wav: str) -> str:
    print("=== 2. Mixing Real Chi Hang Voiceover + Tactile Multi-Agent Micro-SFX (-14.0 LUFS) ===")
    bed_wav = os.path.join(AUDIO_DIR, "tactile_swarm_bed.wav")
    build_tactile_swarm_bed(bed_wav, 18.0)

    click_sfx = os.path.join(SFX_BUNDLE, "sfx_click_soft.mp3")
    pop_sfx = os.path.join(SFX_BUNDLE, "sfx_pop_clean.mp3")
    whoosh_sfx = os.path.join(SFX_BUNDLE, "sfx_whoosh_soft.mp3")

    master_wav = os.path.join(AUDIO_DIR, "master_18s_lufs14.wav")
    if all(os.path.exists(x) for x in [click_sfx, pop_sfx, whoosh_sfx]):
        flt = (
            "[0:a]volume=1.05[vo];"
            "[1:a]volume=0.42[bed];"
            "[2:a]adelay=150|150,volume=0.22[w1];"
            "[3:a]adelay=4200|4200,volume=0.20[p1];"
            "[2:a]adelay=8000|8000,volume=0.20[w2];"
            "[3:a]adelay=11300|11300,volume=0.20[p2];"
            "[2:a]adelay=14500|14500,volume=0.20[w3];"
            "[vo][bed][w1][p1][w2][p2][w3]amix=inputs=7:normalize=0,"
            "highpass=f=65,loudnorm=I=-14.0:TP=-1.2:LRA=11,"
            "afade=t=in:st=0:d=0.12,afade=t=out:st=17.65:d=0.35[outa]"
        )
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", vo_wav, "-i", bed_wav, "-i", whoosh_sfx, "-i", pop_sfx,
            "-filter_complex", flt, "-map", "[outa]", "-t", "18.0",
            "-ar", "48000", "-ac", "2", master_wav
        ], check=True)
    else:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", vo_wav, "-i", bed_wav,
            "-filter_complex", "[0:a]volume=1.05[vo];[1:a]volume=0.42[bed];[vo][bed]amix=inputs=2:normalize=0,loudnorm=I=-14.0:TP=-1.2:LRA=11[outa]",
            "-map", "[outa]", "-t", "18.0", master_wav
        ], check=True)
    return master_wav

def render_and_encode(src_video: str, start_sec: float, out_mp4: str):
    vo_wav = prepare_real_chihang_source(src_video, start_sec)
    master_wav = mix_master_audio(vo_wav)

    print("=== 3. Rendering 1080 frames @ 60fps in 4-worker Headless Edge ===")
    if os.path.exists(RENDERED_DIR):
        shutil.rmtree(RENDERED_DIR)
    os.makedirs(RENDERED_DIR, exist_ok=True)
    subprocess.run(["node", "render_60fps.js", "--full"], cwd=PROJ, check=True)

    print("=== 4. Encoding Final 1080x1920 @ 60fps MP4 via GPU h264_nvenc ===")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-framerate", "60", "-i", os.path.join(RENDERED_DIR, "frame_%04d.jpg"),
        "-i", master_wav,
        "-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "17", "-b:v", "0",
        "-pix_fmt", "yuv420p", "-r", "60",
        "-c:a", "aac", "-b:a", "256k",
        "-shortest", "-movflags", "+faststart",
        out_mp4
    ], check=True)
    print(f"DONE: {out_mp4} ({os.path.getsize(out_mp4)/1024/1024:.2f} MB)")

if __name__ == "__main__":
    src = sys.argv[1]
    ss = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    dst = sys.argv[3]
    render_and_encode(src, ss, dst)
