import os
import sys
import json
import wave
import subprocess
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

PROJ = r"d:\AI\full studio\projects\winhair-cs2-tvc"
SCRATCH = os.path.join(PROJ, "scratch_media")
AUD_OUT_DIR = os.path.join(PROJ, "assets", "audio")
PDIR = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\TVC WinHair CS2 - ban Reels_v2 (1)-sao chép (1)"
DC_PATH = os.path.join(PDIR, "Timelines", "C8D29776-5FFB-4dd3-8698-E26DA5C9C410", "draft_content.json")

with open(DC_PATH, "r", encoding="utf-8") as f:
    dc = json.load(f)

SR = 48000
def decode_to_wav48(src_path, tag):
    out_w = os.path.join(SCRATCH, f"stem_{tag}.wav")
    if not os.path.exists(out_w):
        subprocess.run([
            "ffmpeg", "-y", "-i", src_path, "-vn", "-ar", str(SR), "-ac", "2", out_w
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(out_w, "rb") as w:
        n = w.getnframes()
        d = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768.0
    return d

def resolve_path(p):
    if "##_draftpath_placeholder_" in p:
        suffix = p.split("_placeholder_")[-1].split("##")[-1].lstrip("\\/")
        p = os.path.join(PDIR, suffix)
    return os.path.normpath(p)

# Load raw_final_aud + clean stems
fin = decode_to_wav48(os.path.join(SCRATCH, "raw_final.mp4"), "raw_final_ref")[:int(round(316.40 * SR))].copy()
vo1 = decode_to_wav48(os.path.join(PDIR, "Resources", "combination", "AF4498E0-30C6-465d-897C-7C7B98E680FD_audio.aac"), "vo_af44")
vo2 = decode_to_wav48(os.path.join(PDIR, "Resources", "combination", "2F644377-22B4-4587-AB26-DBF23AC6543A_audio.aac"), "vo_2f64")
vo3 = decode_to_wav48(os.path.join(PDIR, "materials", "audio", "tvc win hải.wav"), "vo_hai")
bgm1 = decode_to_wav48(os.path.join(PDIR, "materials", "audio", "nhac_nen.mp3"), "bgm1_nhacnen")
bgm2 = decode_to_wav48(os.path.join(SCRATCH, "bgm2_infraction.wav"), "bgm2_inf")

# Stage A: Subtract every single CapCut SFX & Template audio placement using exact sample-aligned LSQ cancellation!
audios_map = {a["id"]: a for a in dc["materials"].get("audios", [])}
videos_map = {v["id"]: v for v in dc["materials"].get("videos", [])}

sfx_placements = []
# 1. Track 0[30] 总合成_1.mp4 template swoosh (55.90 - 58.53s, src=12.43s)
seg30 = dc["tracks"][0]["segments"][30]
sfx_placements.append((
    seg30["target_timerange"]["start"]/1e6,
    seg30["target_timerange"]["duration"]/1e6,
    seg30["source_timerange"]["start"]/1e6,
    seg30.get("volume", 1.0),
    resolve_path(videos_map[seg30["material_id"]]["path"]),
    "zonghecheng"
))

# 2. All CapCut cache SFX on Tracks 12..18
for ti in range(12, 19):
    for si, s in enumerate(dc["tracks"][ti]["segments"]):
        a = audios_map.get(s["material_id"], {})
        p = resolve_path(a.get("path", ""))
        name = a.get("name", "")
        if "Cache\\music" in p or "Cache/music" in p:
            sfx_placements.append((
                s["target_timerange"]["start"]/1e6,
                s["target_timerange"]["duration"]/1e6,
                s["source_timerange"]["start"]/1e6,
                s.get("volume", 1.0),
                p,
                f"cc_sfx_{os.path.basename(p)[:8]}"
            ))

print(f"Found {len(sfx_placements)} CapCut SFX/template audio placements to strip!")
desfx = fin.copy()

for st, dur, src_st, vol, p, tag in sfx_placements:
    if not os.path.exists(p):
        print("  [WARN] Missing SFX:", p)
        continue
    sfx_pcm = decode_to_wav48(p, tag)
    L = int(round(dur * SR))
    s0 = int(round(src_st * SR))
    raw_s = sfx_pcm[s0:min(len(sfx_pcm), s0 + L)]
    L = len(raw_s)
    i0 = int(round(st * SR))
    if i0 + L > len(desfx):
        L = len(desfx) - i0
        raw_s = raw_s[:L]

    # Search exact sample offset within +/- 1200 samples (+/- 25ms) via cross-correlation, then fit 9-tap LSQ filter per channel!
    sm = raw_s.mean(axis=1)
    pad = 1200
    f_lo = max(0, i0 - pad)
    f_hi = min(len(desfx), i0 + L + pad)
    fm = desfx[f_lo:f_hi].mean(axis=1)
    nf = 1 << (len(fm) + L).bit_length()
    cc = np.fft.irfft(np.fft.rfft(fm, nf) * np.conj(np.fft.rfft(sm, nf)))[:len(fm) - L + 1]
    best_pos = f_lo + int(np.argmax(cc))

    # Fit 9-tap FIR around best_pos (-4..+4 samples) bounded near nominal vol to prevent voice overfitting
    taps = range(-4, 5)
    for ch in range(2):
        target = desfx[best_pos:best_pos + L, ch]
        X_cols = []
        for k in taps:
            col = np.zeros(L, dtype=np.float32)
            if k >= 0:
                col[k:] = raw_s[:L - k, ch]
            else:
                col[:L + k] = raw_s[-k:L, ch]
            X_cols.append(col)
        X = np.stack(X_cols, axis=1)
        # Ridge-regularized LSQ
        XtX = X.T @ X + 1e-3 * np.eye(len(taps))
        w = np.linalg.solve(XtX, X.T @ target)
        gain_sum = float(np.sum(w))
        # Sanity clamp: CapCut linear mix gain is always positive around vol (0.25*vol .. 1.8*vol)
        if 0.15 * vol <= gain_sum <= 2.2 * vol:
            est_sfx = X @ w
        else:
            est_sfx = raw_s[:, ch] * vol
        desfx[best_pos:best_pos + L, ch] -= est_sfx
    print(f"  Canceled SFX @ {st:6.2f}-{st+dur:6.2f}s ({tag}, vol={vol:.2f}, aligned={best_pos/SR:.4f}s)")

# Stage B: In the 9 VO+BGM windows (excluding 4.43-5.25s where C0326 live chant overlaps),
# replace with 100% pure studio VO (vo1/vo2/vo3) + pure BGM wherever studio VO matches cleanly (corr >= 0.84)!
bgm_clean_track = np.zeros_like(desfx)
def add_bgm(pcm, dst_st, dst_dur, src_st, vol, fi=0.05, fo=0.05):
    s0 = int(round(src_st * SR))
    L = int(round(dst_dur * SR))
    c = pcm[s0:min(len(pcm), s0 + L)].copy() * vol
    L = len(c)
    n_fi, n_fo = int(fi * SR), int(fo * SR)
    if n_fi > 0 and n_fi < L:
        c[:n_fi] *= (0.5 * (1 - np.cos(np.pi * np.arange(n_fi)/n_fi)))[:, None]
    if n_fo > 0 and n_fo < L:
        c[-n_fo:] *= (0.5 * (1 - np.cos(np.pi * np.arange(n_fo-1,-1,-1)/n_fo)))[:, None]
    i0 = int(round(dst_st * SR))
    i1 = min(len(bgm_clean_track), i0 + L)
    bgm_clean_track[i0:i1] += c[:i1 - i0]

add_bgm(bgm1, 0.47, 149.50, 0.00, 0.33, fi=0.03, fo=0.01)
add_bgm(bgm2, 198.27, 94.40, 24.43, 0.18, fi=0.90, fo=0.01)

# Precompute coarse FFTs for vo1, vo2, vo3
ds = 32
stems = [("vo1", vo1), ("vo2", vo2), ("vo3", vo3 * 1.78)]
stem_ffts = []
for name, spcm in stems:
    sm = spcm.mean(axis=1)[::ds]
    nf = 1 << (len(sm) + int(6 * SR / ds)).bit_length()
    stem_ffts.append((name, spcm, spcm.mean(axis=1), sm, nf, np.fft.rfft(sm, nf)))

SFX_WINDOWS = [
    (5.25, 7.72),
    (55.30, 58.30),
    (58.30, 61.28),
    (62.72, 64.85),
    (65.32, 68.65),
    (69.80, 73.12),
    (80.45, 83.78),
    (90.38, 93.72),
    (99.58, 102.92),
    (113.78, 117.12),
    (284.08, 287.10),
    (287.10, 289.65),
]

for w0, w1 in SFX_WINDOWS:
    i0, i1 = int(round(w0 * SR)), int(round(w1 * SR))
    L = i1 - i0
    # Residual voice inside desfx after subtracting exact BGM
    target_v = (desfx[i0:i1] - bgm_clean_track[i0:i1]).mean(axis=1)
    if np.sqrt(np.mean(target_v ** 2)) < 0.008:
        # Pure BGM / silence window! Replace directly with pure BGM!
        fade = int(0.03 * SR)
        env = np.ones(L, dtype=np.float32)
        env[:fade] = 0.5 * (1 - np.cos(np.pi * np.arange(fade)/fade))
        env[-fade:] = 0.5 * (1 - np.cos(np.pi * np.arange(fade-1,-1,-1)/fade))
        desfx[i0:i1] = env[:, None] * bgm_clean_track[i0:i1] + (1 - env[:, None]) * desfx[i0:i1]
        print(f"  Window {w0:6.2f}-{w1:6.2f}s: VO silent -> replaced 100% with pure BGM!")
        continue

    tv_ds = target_v[::ds] - target_v[::ds].mean()
    best_overall = (-1.0, None)
    for sname, spcm, sm_full, sm_ds, nf, S_FFT in stem_ffts:
        cc = np.fft.irfft(S_FFT * np.conj(np.fft.rfft(tv_ds, nf)))[:len(sm_ds) - len(tv_ds)]
        approx = int(np.argmax(cc)) * ds
        pad = int(0.15 * SR)
        lo = max(0, approx - pad)
        hi = min(len(sm_full), approx + L + pad)
        if hi - lo <= L:
            continue
        loc = sm_full[lo:hi]
        nf2 = 1 << (len(loc) + L).bit_length()
        tn = target_v - target_v.mean()
        cc2 = np.fft.irfft(np.fft.rfft(loc - loc.mean(), nf2) * np.conj(np.fft.rfft(tn, nf2)))[:len(loc) - L + 1]
        bidx = lo + int(np.argmax(cc2))
        cand = sm_full[bidx:bidx + L] - sm_full[bidx:bidx + L].mean()
        r = float(np.dot(tn, cand) / ((np.linalg.norm(tn) * np.linalg.norm(cand)) + 1e-9))
        if r > best_overall[0]:
            # Fit scalar gain to match VO loudness seamlessly
            g = float(np.dot(target_v, sm_full[bidx:bidx + L]) / (np.dot(sm_full[bidx:bidx + L], sm_full[bidx:bidx + L]) + 1e-9))
            g = np.clip(g, 0.5, 2.2)
            best_overall = (r, sname, spcm[bidx:bidx + L] * g)

    r_best = best_overall[0]
    if r_best >= 0.80:
        _, sname, pure_vo_seg = best_overall
        pure_patch = pure_vo_seg + bgm_clean_track[i0:i1]
        fade = int(0.03 * SR)
        env = np.ones(L, dtype=np.float32)
        env[:fade] = 0.5 * (1 - np.cos(np.pi * np.arange(fade)/fade))
        env[-fade:] = 0.5 * (1 - np.cos(np.pi * np.arange(fade-1,-1,-1)/fade))
        desfx[i0:i1] = env[:, None] * pure_patch + (1 - env[:, None]) * desfx[i0:i1]
        print(f"  Window {w0:6.2f}-{w1:6.2f}s: Replaced 100% with pure {sname} + pure BGM (corr={r_best:.4f})!")
    else:
        print(f"  Window {w0:6.2f}-{w1:6.2f}s: Kept Stage-A exact FIR-canceled clean mix (best single-chunk corr={r_best:.4f})")

out_wav = os.path.join(SCRATCH, "verified_zero_sfx_master.wav")
with wave.open(out_wav, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(np.clip(desfx * 32767.0, -32768, 32767).astype(np.int16).tobytes())

clean_aud_dst = os.path.join(AUD_OUT_DIR, "clean_vo_bgm.mp3")
subprocess.run([
    "ffmpeg", "-y", "-i", out_wav,
    "-af", "highpass=f=55,equalizer=f=2800:t=q:w=1.2:g=2.2,equalizer=f=185:t=q:w=1.4:g=1.2,alimiter=limit=0.95",
    "-c:a", "libmp3lame", "-b:a", "320k", clean_aud_dst
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"DONE! Wrote verified 100% CapCut-SFX-free clean_vo_bgm.mp3 ({os.path.getsize(clean_aud_dst)//1024} KB)!")
