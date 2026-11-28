import json
import math
import os
import subprocess
import time
import wave
import numpy as np

PROJ_DIR = r"C:\AI\full studio\projects\feel_chicken_premiere_120agents_261128"
SFX_DIR  = os.path.join(PROJ_DIR, "assets", "sfx")
FRAMES_DIR = os.path.join(PROJ_DIR, "rendered_frames")
SRC_WAV  = os.path.join(PROJ_DIR, "assets", "fc_source_48k.wav")
MIX_WAV  = os.path.join(PROJ_DIR, "assets", "fc_premiere_master_mix.wav")
FINAL_MP4 = os.path.join(
    PROJ_DIR,
    "261128 Feel Chicken Hệ thống 120 Agent AI dựng Premiere tự động Kiểm tra miệng final.mp4"
)

SR = 48000

def load_sfx_stereo(fname, pitch_semitones=0.0):
    p = os.path.join(SFX_DIR, fname)
    af = f"aresample={SR}"
    if abs(pitch_semitones) > 0.01:
        ratio = 2.0 ** (pitch_semitones / 12.0)
        af = f"asetrate={int(round(SR * ratio))},aresample={SR}"
    cmd = [
        "ffmpeg", "-v", "error", "-i", p,
        "-af", af, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"
    ]
    raw = subprocess.check_output(cmd)
    arr = np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()
    pk = float(np.max(np.abs(arr)))
    if pk > 1e-5:
        arr /= pk
    return arr

def place_sfx(buf, clip, t_sec, gain_db=-14.0, pan=0.0, max_dur_s=0.45):
    i0 = int(round(max(0.0, t_sec) * SR))
    if i0 >= len(buf):
        return
    max_len = min(len(clip), int(round(max_dur_s * SR)), len(buf) - i0)
    if max_len <= 16:
        return
    seg = clip[:max_len].copy()
    fade_n = min(max_len // 4, int(0.03 * SR))
    if fade_n > 4:
        seg[-fade_n:] *= np.linspace(1.0, 0.0, fade_n, dtype=np.float32)[:, None]
    amp = 10.0 ** (gain_db / 20.0)
    gl = amp * math.sqrt(0.5 * (1.0 - max(-0.85, min(0.85, pan)))) * 1.414
    gr = amp * math.sqrt(0.5 * (1.0 + max(-0.85, min(0.85, pan)))) * 1.414
    buf[i0:i0 + max_len, 0] += seg[:, 0] * gl
    buf[i0:i0 + max_len, 1] += seg[:, 1] * gr

def main():
    t0 = time.time()
    print("1. Loading original Feel Chicken 48kHz master audio (Voice + Conan BGM)...", flush=True)
    with wave.open(SRC_WAV, "rb") as wf:
        n_frames = wf.getnframes()
        pcm16 = np.frombuffer(wf.readframes(n_frames), dtype=np.int16).reshape((-1, 2))
    base = pcm16.astype(np.float32) / 32768.0
    sfx_bus = np.zeros_like(base)

    # Preload clean studio Tactile Source-Gen & Throw/Import SFX (ZERO mouse-click spam!)
    shimmer  = load_sfx_stereo("sfx_crystal_shimmer.mp3")
    ping_gl  = load_sfx_stereo("sfx_ping_glass.mp3")
    whoosh_s = load_sfx_stereo("sfx_whoosh_soft.mp3")
    swoosh_a = load_sfx_stereo("swoosh_up_a.wav")
    swoosh_b = load_sfx_stereo("swoosh_up_b.wav")
    pop_cln  = load_sfx_stereo("sfx_pop_clean.mp3")
    pop_a    = load_sfx_stereo("pop_a.wav")
    pop_b    = load_sfx_stereo("pop_b.wav")
    chime_ok = load_sfx_stereo("sfx_chime_warm.mp3")

    # 1A. 6 Progressive Premiere Bin Imports (Source-Gen shimmer -> Airy Throw -> Clean Bin Drop)
    bin_imports = [
        (0.85,  1.25, -0.35),
        (5.55,  5.95, -0.35),
        (17.55, 17.98, -0.35),
        (24.65, 25.10, -0.35),
        (28.95, 29.35, -0.35),
        (44.00, 44.42, -0.35),
    ]
    for idx, (ts0, t_imp, pan) in enumerate(bin_imports):
        place_sfx(sfx_bus, shimmer if idx % 2 == 0 else ping_gl, ts0 - 0.08, gain_db=-19.5, pan=pan * 0.5, max_dur_s=0.35)
        place_sfx(sfx_bus, whoosh_s, t_imp - 0.11, gain_db=-18.5, pan=pan, max_dur_s=0.28)
        place_sfx(sfx_bus, pop_cln,  t_imp,        gain_db=-17.5, pan=pan, max_dur_s=0.16)

    # 1B. Major Curved-Arc Throws into Premiere `Program` Monitor (Whoosh at -110ms + Pop at 0ms!)
    major_throws = [
        (0.14,  0.20), (1.40, -0.20), (3.72,  0.22),
        (6.10, -0.25), (8.05,  0.20), (8.77,  0.25), (11.52, -0.20), (12.25, 0.22),
        (13.47,-0.22), (15.81, 0.22), (18.15,-0.20),
        (21.97, 0.20),
        (27.94, 0.22), (28.81,-0.18), (29.49,-0.22), (30.65, 0.20), (31.77,-0.18), (32.85, 0.22), (35.65, 0.22),
        (36.86,-0.20), (39.61,-0.22), (39.97, 0.24), (41.15, 0.18), (44.56,-0.15)
    ]
    for idx, (tland, pan) in enumerate(major_throws):
        wh = swoosh_a if idx % 2 == 0 else swoosh_b
        pp = pop_a if idx % 2 == 0 else pop_b
        place_sfx(sfx_bus, wh, tland - 0.11, gain_db=-18.0, pan=pan, max_dur_s=0.26)
        place_sfx(sfx_bus, pp, tland,        gain_db=-17.0, pan=pan * 0.4, max_dur_s=0.14)

    # 1C. SIGNATURE 6-CARD QUIZ VOLLEY (25.29s .. 27.19s): Ascending +1 Semitone per Card + Chime!
    quiz_lands = [25.29, 25.67, 26.05, 26.43, 26.81, 27.19]
    for qi, qt in enumerate(quiz_lands):
        pan = -0.28 if qi % 2 == 0 else 0.28
        pitched_pop = load_sfx_stereo("sfx_pop_clean.mp3", pitch_semitones=qi * 1.15)
        pitched_wh  = load_sfx_stereo("whoosh_fast_a.wav", pitch_semitones=qi * 0.8)
        place_sfx(sfx_bus, pitched_wh,  qt - 0.10, gain_db=-16.5, pan=pan, max_dur_s=0.22)
        place_sfx(sfx_bus, pitched_pop, qt,        gain_db=-15.2, pan=pan * 0.4, max_dur_s=0.16)
    place_sfx(sfx_bus, ping_gl, 27.22, gain_db=-16.0, pan=0.0, max_dur_s=0.38)

    # 1D. Premiere Quick Export Done Warm Chime (47.92s)
    place_sfx(sfx_bus, chime_ok, 47.92, gain_db=-15.5, pan=0.15, max_dur_s=0.52)

    mixed = np.clip(base + sfx_bus, -0.98, 0.98)
    raw_mix_wav = os.path.join(PROJ_DIR, "assets", "_tmp_unnorm_mix.wav")
    with wave.open(raw_mix_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mixed * 32767.0).astype(np.int16).tobytes())

    print("2. Normalizing final broadcast audio to -14.0 LUFS (-1.1 dBTP)...", flush=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", raw_mix_wav,
        "-af", "loudnorm=I=-14.0:TP=-1.1:LRA=11.0",
        "-ar", str(SR), "-ac", "2", MIX_WAV
    ], check=True)
    if os.path.exists(raw_mix_wav):
        os.remove(raw_mix_wav)

    # Verify all 2,908 rendered frames exist
    n_rendered = len([x for x in os.listdir(FRAMES_DIR) if x.startswith("frame_") and x.endswith(".jpg")])
    print(f"3. Encoding {n_rendered} frames @ 60fps via RTX 4070 h264_nvenc -> {os.path.basename(FINAL_MP4)}...", flush=True)
    if n_rendered < 2908:
        raise RuntimeError(f"Expected 2908 frames in {FRAMES_DIR}, found {n_rendered}!")

    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-framerate", "60",
        "-i", os.path.join(FRAMES_DIR, "frame_%04d.jpg"),
        "-i", MIX_WAV,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
        "-pix_fmt", "yuv420p", "-r", "60",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart",
        FINAL_MP4
    ], check=True)

    sz_mb = os.path.getsize(FINAL_MP4) / (1024 * 1024)
    print(f"DONE Master MP4 ({sz_mb:.2f} MB) in {time.time() - t0:.1f}s: {FINAL_MP4}", flush=True)

if __name__ == "__main__":
    main()
