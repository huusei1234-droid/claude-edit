# -*- coding: utf-8 -*-
"""
V6 Master Audio Mixer (Synced 1:1 to V6's 25 Direct Curved-Arc Throws + Progressive Bin Imports):
  - Source Generation Shimmers & Glass Pings when ChatGPT / Photoshop / Illustrator craft each B-Roll & KeyText
  - Airy Whooshes + Juicy Clean Pops on every rapid-fire 2-card & 3-card Curved-Arc Volley into CapCut `Tệp phương tiện` & `Trình phát`
  - ZERO dry mouse-click spam! Normalized cleanly to -14.0 LUFS.
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJ_DIR = r"C:\AI\full studio\projects\khach_phu_khoa_capcut_120agents_261128"
ASSETS_DIR = os.path.join(PROJ_DIR, "assets")
SFX_DIR = os.path.join(ASSETS_DIR, "sfx")


def load_sfx_pcm(filename: str, sr: int = 48000, max_dur: float = 1.4, semitones: float = 0.0) -> np.ndarray:
    fp = os.path.join(SFX_DIR, filename)
    if not os.path.exists(fp):
        return np.zeros((100, 2), dtype=np.float32)
    af_chain = []
    if abs(semitones) > 0.05:
        factor = 2.0 ** (semitones / 12.0)
        af_chain.append(f"asetrate={int(sr * factor)},aresample={sr}")
    af_chain.append(f"afade=t=out:st={max(0.05, max_dur - 0.08):.2f}:d=0.08")
    cmd = [
        "ffmpeg", "-v", "error", "-i", fp,
        "-t", f"{max_dur:.2f}",
        "-af", ",".join(af_chain),
        "-f", "s16le", "-acodec", "pcm_s16le", "-ar", str(sr), "-ac", "2", "-"
    ]
    raw = subprocess.check_output(cmd)
    arr = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768.0
    peak = float(np.max(np.abs(arr))) if len(arr) else 1.0
    if peak > 0.01:
        arr = arr / peak
    return arr


def place_panned(mix_buf: np.ndarray, sr: int, sec: float, clip: np.ndarray, gain: float = 0.22, pan: float = 0.0):
    if sec < 0 or len(clip) == 0:
        return
    i0 = int(sec * sr)
    if i0 >= len(mix_buf):
        return
    n = min(len(clip), len(mix_buf) - i0)
    lg = gain * min(1.0, 1.0 - pan * 0.45)
    rg = gain * min(1.0, 1.0 + pan * 0.45)
    mix_buf[i0:i0 + n, 0] += clip[:n, 0] * lg
    mix_buf[i0:i0 + n, 1] += clip[:n, 1] * rg


def build_master_audio(out_wav: str, mode: str):
    voice_wav = os.path.join(ASSETS_DIR, "voice_clean_48k.wav")
    with wave.open(voice_wav, "rb") as wf:
        sr = wf.getframerate()
        n_samples = wf.getnframes()
        voice = np.frombuffer(wf.readframes(n_samples), dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768.0

    with open(os.path.join(ASSETS_DIR, "words_timeline.json"), "r", encoding="utf-8") as f:
        wdata = json.load(f)
    dur = n_samples / float(sr)
    words = wdata.get("words", [])

    def find_t(kws, ratio):
        for kw in kws:
            for w in words:
                if kw in (w.get("n") or w.get("w", "").lower()):
                    return float(w["s"])
        return dur * ratio

    tKi = max(2.3, min(dur * 0.36, find_t(["thủ", "kiềm"], 0.28)))
    tPh = max(tKi + 2.0, min(dur * 0.52, find_t(["mất", "ph"], 0.42)))
    tLk = max(tPh + 1.8, min(dur * 0.66, find_t(["khi", "hàng", "lợi"], 0.52)))
    tDn = max(tLk + 2.2, min(dur * 0.84, find_t(["hãy", "dịu", "chuẩn"], 0.72)))
    tEt = max(tDn + 1.6, min(dur - 1.5, find_t(["êm", "thoáng"], 0.87)))

    shimmers = [
        load_sfx_pcm("shimmer_a.wav", sr, 0.48, 0.0),
        load_sfx_pcm("sparkle_a.wav", sr, 0.46, 2.0),
        load_sfx_pcm("sparkle_b.wav", sr, 0.46, 4.0),
    ]
    riser = load_sfx_pcm("riser_a.wav", sr, 0.28, 3.0)
    pings = [
        load_sfx_pcm("sfx_ping_glass.mp3", sr, 0.42, 0.0),
        load_sfx_pcm("sfx_ping_glass.mp3", sr, 0.42, 2.0),
        load_sfx_pcm("sfx_ping_glass.mp3", sr, 0.42, 4.0),
    ]
    pops = [
        load_sfx_pcm("sfx_pop_clean.mp3", sr, 0.32, 0.0),
        load_sfx_pcm("pop_a.wav", sr, 0.26, 0.0),
        load_sfx_pcm("sfx_pop_clean.mp3", sr, 0.32, 1.5),
        load_sfx_pcm("pop_b.wav", sr, 0.26, 2.5),
        load_sfx_pcm("pop_c.wav", sr, 0.26, 4.0),
    ]
    whooshes = [
        load_sfx_pcm("sfx_whoosh_soft.mp3", sr, 0.30),
        load_sfx_pcm("swoosh_up_a.wav", sr, 0.28),
        load_sfx_pcm("sfx_whoosh_transition.mp3", sr, 0.30),
        load_sfx_pcm("swoosh_up_b.wav", sr, 0.28),
        load_sfx_pcm("whoosh_fast_a.wav", sr, 0.24),
    ]
    chime_warm = load_sfx_pcm("sfx_chime_warm.mp3", sr, 0.95)

    sfx = np.zeros_like(voice)

    if mode == "th":
        for idx, ts in enumerate([0.25, 2.32, tKi, tPh, tLk, tDn, tEt]):
            place_panned(sfx, sr, max(0.02, ts - 0.10), whooshes[0], gain=0.14, pan=0.0)
            place_panned(sfx, sr, ts, pops[idx % len(pops)], gain=0.15, pan=0.0)
    else:
        # 1. Source Generation + Import Bin Drops (BIN_IMPORT_SCHEDULE)
        bin_events = [
            (0.02, 0.24),
            (0.10, 0.34),
            (tKi - 0.65, tKi - 0.14),
            (tLk - 0.62, tLk - 0.10),
            (tDn - 0.62, tDn - 0.10),
        ]
        for idx, (t_src, t_imp) in enumerate(bin_events):
            place_panned(sfx, sr, max(0.01, t_src), riser, gain=0.14, pan=-0.32)
            place_panned(sfx, sr, max(0.02, t_src + 0.08), shimmers[idx % 3], gain=0.22, pan=-0.28)
            place_panned(sfx, sr, max(0.02, t_imp - 0.10), whooshes[idx % 5], gain=0.20, pan=-0.25)
            place_panned(sfx, sr, t_imp, pops[idx % 5], gain=0.28, pan=-0.30)

        # 2. Rapid-Fire Direct Curved-Arc Volleys Into CapCut `Trình phát` (Ascending pitch +1 semitone on 3-card volleys!)
        volley_lands = [
            (0.20, 0), (0.28, 1), (0.38, 2),
            (2.32, 2),
            (tKi - 0.10, 0), (tKi + 0.02, 2), (tKi + 0.14, 4),
            (tPh, 1), (tPh + 0.06, 2), (tPh + 0.16, 3),
            (tLk + 0.02, 1), (tLk + 0.14, 3),
            (tDn - 0.04, 0), (tDn + 0.08, 2), (tDn + 0.20, 4),
            (tEt, 1), (tEt + 0.08, 2), (tEt + 0.18, 4),
        ]
        for idx, (tl, p_idx) in enumerate(volley_lands):
            place_panned(sfx, sr, max(0.02, tl - 0.12), whooshes[idx % 5], gain=0.19, pan=0.18 if idx % 2 == 0 else -0.18)
            place_panned(sfx, sr, tl, pops[p_idx % 5], gain=0.25, pan=0.0)
            if p_idx == 4:
                place_panned(sfx, sr, tl + 0.02, pings[idx % 3], gain=0.17, pan=0.1)

        # 3. Gentle Subtitle Vector Throw Pops in between major volleys
        for idx, st in enumerate([1.35, 3.65, 6.45, 8.55, 11.45, 13.35, 15.25]):
            if st < dur - 0.8:
                place_panned(sfx, sr, st - 0.09, whooshes[0], gain=0.14, pan=0.25)
                place_panned(sfx, sr, st, pops[idx % 5], gain=0.18, pan=0.0)

        # 4. Final `⇥ Xuất` Completion Chime
        place_panned(sfx, sr, max(1.0, dur - 0.54), whooshes[1], gain=0.22, pan=0.35)
        place_panned(sfx, sr, max(1.0, dur - 0.46), chime_warm, gain=0.28, pan=0.0)

    mixed = np.clip(voice + sfx, -0.98, 0.98)
    raw_mix = out_wav.replace(".wav", "_raw.wav")
    pcm16 = (mixed * 32767.0).astype(np.int16)
    with wave.open(raw_mix, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", raw_mix,
            "-af", "loudnorm=I=-14.0:TP=-1.1:LRA=11",
            "-ar", "48000", "-ac", "2", out_wav,
        ],
        check=True,
    )
    if os.path.exists(raw_mix):
        os.remove(raw_mix)


def encode_nvenc_mp4(frames_subdir: str, audio_wav: str, out_mp4: str):
    frames_pattern = os.path.join(PROJ_DIR, frames_subdir, "frame_%04d.jpg")
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-framerate", "60", "-i", frames_pattern,
            "-i", audio_wav,
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
            "-pix_fmt", "yuv420p", "-r", "60",
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            out_mp4,
        ],
        check=True,
    )
    print(f"[Encoded] {out_mp4} ({os.path.getsize(out_mp4) / 1048576:.2f} MB)", flush=True)


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "v2"
    v1_mp4 = os.path.join(PROJ_DIR, "261128 Khách Phụ Khoa Chăm sóc chuẩn độ pH vùng nhạy cảm Talking Head final.mp4")
    v2_mp4 = os.path.join(PROJ_DIR, "261128 Khách Phụ Khoa Hệ thống 120 Agent AI tạo B-Roll Photoshop ném trực tiếp vào CapCut final.mp4")

    if target in ("v1", "both"):
        wav1 = os.path.join(ASSETS_DIR, "master_v1_14lufs.wav")
        build_master_audio(wav1, mode="th")
        encode_nvenc_mp4("th_rendered_frames", wav1, v1_mp4)

    if target in ("v2", "both"):
        wav2 = os.path.join(ASSETS_DIR, "master_v2_14lufs.wav")
        build_master_audio(wav2, mode="capcut120")
        encode_nvenc_mp4("cc_rendered_frames", wav2, v2_mp4)


if __name__ == "__main__":
    main()
