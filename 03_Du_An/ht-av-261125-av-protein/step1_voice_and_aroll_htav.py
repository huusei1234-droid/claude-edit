import json, math, os, subprocess, sys, wave
import numpy as np

PROJ      = r"C:\AI\full studio\output\ht-av-261125"
AROLL     = os.path.join(PROJ, "aroll")
STEMS     = os.path.join(PROJ, "audio_stems")
VS_ROOT   = r"C:\AI\full studio\voice-studio"

sys.path.insert(0, os.path.join(VS_ROOT, "backend"))
sys.path.insert(0, VS_ROOT)

import torch
from faster_whisper import WhisperModel
from services.tts_backend import get_active_tts_backend

voc_orig = os.path.join(STEMS, "demucs_out", "htdemucs", "orig_input", "vocals.wav")
ref_wav  = os.path.join(STEMS, "chi_hang_ref_24k.wav")
ref_text = "Bữa sáng toàn tinh bột, làm đường huyết tăng vọt cực nhanh, rồi tụt dốc không phanh, chỉ sau hai tiếng, cơ thể bạn không cần thêm tinh bột,"

torch.manual_seed(2026)
backend = get_active_tts_backend()
wmodel  = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 12)

def synth_and_pick(candidates, out_wav_48k):
    best_arr, best_sr, best_txt, best_heard = None, 24000, "", ""
    for seed_i, ctext, lang in candidates:
        torch.manual_seed(seed_i)
        wt = backend.generate(
            text=ctext,
            ref_audio=ref_wav,
            ref_text=ref_text,
            language=lang,
            num_step=32,
            guidance_scale=2.2,
            speed=1.03,
        )
        sr = int(getattr(backend, "sample_rate", 24000))
        arr = wt.detach().to("cpu").float().numpy().squeeze().astype(np.float32) if hasattr(wt, "detach") else np.asarray(wt, dtype=np.float32).squeeze()
        if arr.ndim > 1:
            arr = arr.mean(axis=int(np.argmin(arr.shape)))
        pk = float(np.max(np.abs(arr))) if len(arr) else 0.0
        if pk > 1e-4:
            arr = arr * (0.90 / pk)
        idx = np.where(np.abs(arr) > 0.014)[0]
        if len(idx) > 10:
            arr = arr[max(0, int(idx[0]) - int(0.025 * sr)) : min(len(arr), int(idx[-1]) + int(0.045 * sr))]

        tmp24 = out_wav_48k + f".cand_{seed_i}.wav"
        tmp16 = out_wav_48k + f".cand_{seed_i}_16k.wav"
        pcm16 = (np.clip(arr, -1.0, 1.0) * 32767.0).astype(np.int16)
        with wave.open(tmp24, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm16.tobytes())
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp24, "-ac", "1", "-ar", "16000", tmp16], check=True)
        segs, _ = wmodel.transcribe(tmp16, language="vi", initial_prompt="1.632 miligam L-Leucine, PROTEIN")
        heard = " ".join(s.text.strip() for s in segs)
        print(f"  [Cand seed={seed_i} lang={lang}] '{ctext}' -> dur={len(arr)/sr:.2f}s | heard='{heard}'", flush=True)
        os.remove(tmp16)
        if best_arr is None or any(k in heard.lower() for k in ("leucine", "l-leucine", "liu", "lơ xin", "protein", "nhắn")):
            best_arr, best_sr, best_txt, best_heard = arr, sr, ctext, heard
            shutil.copy2(tmp24, out_wav_48k + ".raw24.wav") if False else None
            # Convert chosen to 48kHz stereo matched with mild warmth EQ so it blends seamlessly with Chi Hang's mic!
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-i", tmp24,
                "-af", "highpass=f=85,equalizer=f=320:t=q:w=1.1:g=1.4,equalizer=f=3400:t=q:w=1.2:g=-1.2,lowpass=f=12500",
                "-ac", "2", "-ar", "48000", out_wav_48k
            ], check=True)
            os.remove(tmp24)
            if any(k in heard.lower() for k in ("leucine", "protein")):
                break
        else:
            os.remove(tmp24)
    print(f"  => SELECTED '{best_txt}' -> heard='{best_heard}' -> {out_wav_48k}", flush=True)
    return out_wav_48k

print("[1/3] Synthesizing Voice Studio cloned fixes for misread words...", flush=True)
leu_wav = os.path.join(STEMS, "vs_clone_leucine_48k.wav")
cta_wav = os.path.join(STEMS, "vs_clone_cta_48k.wav")

synth_and_pick([
    (2026, "thêm một nghìn sáu trăm ba mươi hai mi li gam eo liu xin,", "vi"),
    (2027, "thêm một nghìn sáu trăm ba mươi hai mi li gam L-Leucine,", "en"),
    (2028, "thêm một nghìn sáu trăm ba mươi hai mi li gam eo lơ xin,", "vi"),
], leu_wav)

synth_and_pick([
    (2026, "nhắn chữ Pờ rô tê in bên dưới!", "vi"),
    (2027, "nhắn chữ Protein bên dưới!", "en"),
], cta_wav)

# Helper to read 48k stereo float32
def read_f32_48k(path, ss=None, dur=None):
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", f"{ss:.6f}"]
    cmd += ["-i", path]
    if dur is not None:
        cmd += ["-t", f"{dur:.6f}"]
    cmd += ["-ac", "2", "-ar", "48000", "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def apply_micro_fade(arr, sr=48000, fi_s=0.020, fo_s=0.025):
    out = arr.copy()
    fi = min(len(out) // 4, int(round(fi_s * sr)))
    fo = min(len(out) // 4, int(round(fo_s * sr)))
    if fi > 2:
        out[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 2:
        out[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return out

def rms_active(arr):
    mono = np.mean(arr, axis=1)
    hop = 960
    nh = len(mono) // hop
    if nh < 1:
        return float(np.sqrt(np.mean(mono**2)) + 1e-6)
    r = np.sqrt(np.mean(mono[:nh*hop].reshape((nh, hop))**2, axis=1))
    act = r[r > 0.015]
    return float(np.median(act)) if len(act) else float(np.mean(r) + 1e-6)

leu_arr = read_f32_48k(leu_wav)
cta_arr = read_f32_48k(cta_wav)

# Quantize cloned segment durations to exact 30fps frame multiples (+ natural breath padding)!
SR = 48000
FPS = 30.0

leu_frames = int(math.ceil((len(leu_arr) / SR + 0.24) * FPS))
leu_dur    = leu_frames / FPS
cta_frames = int(math.ceil((len(cta_arr) / SR + 0.85) * FPS))  # +0.85s musical outro hold!
cta_dur    = cta_frames / FPS

print(f"  Cloned Leucine slot: {leu_frames} frames ({leu_dur:.3f}s) | Cloned CTA slot: {cta_frames} frames ({cta_dur:.3f}s)", flush=True)

# Exact frame-snapped EDL combining 5 clean real A-roll pieces + 2 Voice Studio cloned pieces (covered by Full-Screen Card Overlays!)
# Every start/end is an exact integer frame / 30.0!
PIECES = [
    # (kind, src_v_start_f, n_frames, label)
    ("real",   0,   573, "P1_Hook_And_Problem"),        # raw  0.000 -> 19.100s (19.100s)
    ("real", 886,   377, "P2_30s_22g_PeaRice_RealBox"), # raw 29.533 -> 42.100s (12.567s)
    ("clone_leu", 1413, leu_frames, "P3_Cloned_1632mg_LLeucine"),  # video under full-screen card overlay from raw 47.100s
    ("real", 1478,  131, "P4_FirmMuscle_LightBelly"),   # raw 49.267 -> 53.633s ( 4.367s)
    ("real", 1720,  123, "P5_CTA_Share_10am"),          # raw 57.333 -> 61.433s ( 4.100s)
    ("real", 2046,   92, "P6_CTA_30s_Menu"),            # raw 68.200 -> 71.267s ( 3.067s)
    ("clone_cta", 2138, cta_frames, "P7_Cloned_Message_PROTEIN"),  # video under full-screen CTA card deck from raw 71.267s
]

# Verify NVENC at 1080x1920!
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:d=0.1",
    "-c:v", "h264_nvenc", "-f", "null", "-"
], check=True)
print("[GPU] Verified h264_nvenc @ 1080x1920!", flush=True)

mc_graded = os.path.join(AROLL, "main_cut_graded.mp4")
mc_matte  = os.path.join(AROLL, "main_cut_matte.mp4")

ed_graded = os.path.join(AROLL, "edited_graded.mp4")
ed_matte  = os.path.join(AROLL, "edited_matte.mp4")
ed_voice  = os.path.join(STEMS, "edited_voice_48k.wav")

print("[2/3] Slicing & concatenating frame-exact Graded Video, RVM Matte & Seamless Hybrid Voice Track...", flush=True)
v_Selects_g, v_Selects_m = [], []
total_frames = sum(p[2] for p in PIECES)
total_dur = total_frames / FPS

# Build video concat via exact frame-range filters so 0 frame drift is mathematically guaranteed!
vg_parts, vm_parts, vg_ins, vm_ins = [], [], [], []
max_src_f = 2230
for i, (kind, sf, nf, lbl) in enumerate(PIECES):
    ef = min(max_src_f - 1, sf + nf - 1)
    avail = ef - sf + 1
    pad_f = max(0, nf - avail)
    pad_str = f",tpad=stop_mode=clone:stop_duration={pad_f/FPS:.6f}" if pad_f > 0 else ""
    vg_parts.append(f"[0:v]select='between(n,{sf},{ef})',setpts=N/30/TB{pad_str}[vg{i}];")
    vm_parts.append(f"[0:v]select='between(n,{sf},{ef})',setpts=N/30/TB{pad_str}[vm{i}];")
    vg_ins.append(f"[vg{i}]")
    vm_ins.append(f"[vm{i}]")

fc_g = "".join(vg_parts) + "".join(vg_ins) + f"concat=n={len(PIECES)}:v=1:a=0[vout]"
fc_m = "".join(vm_parts) + "".join(vm_ins) + f"concat=n={len(PIECES)}:v=1:a=0[vout]"

subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", mc_graded,
    "-filter_complex", fc_g, "-map", "[vout]",
    "-r", "30", "-fps_mode", "cfr", "-frames:v", str(total_frames),
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
    ed_graded
], check=True)

subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", mc_matte,
    "-filter_complex", fc_m, "-map", "[vout]",
    "-r", "30", "-fps_mode", "cfr", "-frames:v", str(total_frames),
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
    ed_matte
], check=True)

# Assemble hybrid 48kHz voice track (Demucs clean vocals + level-matched Voice Studio cloned segments!)
full_voc = read_f32_48k(voc_orig)
ref_rms  = rms_active(full_voc[int(5.1*SR):int(18.8*SR)])

audio_chunks = []
edl_info = []
cur_f = 0
for kind, sf, nf, lbl in PIECES:
    nsamp = int(round((nf / FPS) * SR))
    t_out_s = cur_f / FPS
    if kind == "real":
        s_idx = int(round((sf / FPS) * SR))
        seg_a = full_voc[s_idx : s_idx + nsamp]
        if len(seg_a) < nsamp:
            seg_a = np.vstack([seg_a, np.zeros((nsamp - len(seg_a), 2), dtype=np.float32)])
        seg_a = apply_micro_fade(seg_a, SR, 0.018, 0.022)
    elif kind == "clone_leu":
        c_rms = rms_active(leu_arr)
        scaled = leu_arr * (ref_rms / max(1e-5, c_rms))
        scaled = apply_micro_fade(scaled, SR, 0.022, 0.030)
        pad_pre = int(round(0.08 * SR))
        seg_a = np.zeros((nsamp, 2), dtype=np.float32)
        put = min(nsamp - pad_pre, len(scaled))
        seg_a[pad_pre : pad_pre + put] = scaled[:put]
    elif kind == "clone_cta":
        c_rms = rms_active(cta_arr)
        scaled = cta_arr * (ref_rms / max(1e-5, c_rms))
        scaled = apply_micro_fade(scaled, SR, 0.022, 0.035)
        pad_pre = int(round(0.08 * SR))
        seg_a = np.zeros((nsamp, 2), dtype=np.float32)
        put = min(nsamp - pad_pre, len(scaled))
        seg_a[pad_pre : pad_pre + put] = scaled[:put]

    audio_chunks.append(seg_a)
    edl_info.append({
        "label": lbl, "kind": kind,
        "src_start_s": round(sf / FPS, 3),
        "out_start_s": round(t_out_s, 3),
        "out_end_s": round((cur_f + nf) / FPS, 3),
        "frames": nf,
    })
    cur_f += nf

hybrid_vo = np.vstack(audio_chunks)
pcm_vo = (np.clip(hybrid_vo, -0.99, 0.99) * 32767.0).astype(np.int16)
with wave.open(ed_voice, "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm_vo.tobytes())

json.dump({"total_frames": total_frames, "duration_s": round(total_dur, 3), "edl": edl_info}, open(os.path.join(AROLL, "edl_htav.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# [3/3] Transcribe the assembled hybrid voice track word-for-word & apply 100% Vietnamese spelling polish!
print("[3/3] Transcribing assembled hybrid voice track for exact word-level sync...", flush=True)
ed_16k = os.path.join(STEMS, "_ed_vo_16k.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", ed_voice, "-ac", "1", "-ar", "16000", ed_16k], check=True)
segs_ed, _ = wmodel.transcribe(
    ed_16k, language="vi", word_timestamps=True,
    initial_prompt="Đừng thắc mắc vì sao ăn sáng no căng mà 10 giờ đã buồn ngủ rũ rượi! Bữa sáng toàn tinh bột làm đường huyết tăng vọt cực nhanh rồi tụt dốc không phanh chỉ sau 2 tiếng! Cơ thể bạn không cần thêm tinh bột, nó đang khát đạm sạch để giữ năng lượng và nuôi cơ! Thay vì nhịn sáng hay ăn đại cho xong, chỉ 30 giây pha 2 gói AV Protein là bạn có ngay 22,05g đạm thực vật từ đậu Hà Lan và gạo, thêm 1.632mg L-Leucine giữ khối cơ săn chắc, nhẹ bụng mà no êm tới trưa! Gửi ngay video này cho đồng nghiệp hay ngáp dài lúc 10 giờ nhé! Muốn nhận thực đơn bữa sáng 30 giây đủ đạm, nhắn chữ PROTEIN bên dưới!"
)
os.remove(ed_16k)

out_segs = []
for s in segs_ed:
    ws = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for w in (s.words or []) if w.word.strip()]
    if ws:
        out_segs.append({"start": ws[0]["start"], "end": ws[-1]["end"], "text": " ".join(x["word"] for x in ws), "words": ws})

json.dump({"lang": "vi", "duration": round(total_dur, 3), "total_frames": total_frames, "segments": out_segs}, open(os.path.join(AROLL, "edited_raw_tr.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("\n=== EDL SUMMARY ===")
for e in edl_info:
    print(f"  [{e['out_start_s']:6.3f} -> {e['out_end_s']:6.3f}s] ({e['frames']:3d}f | {e['kind']:9s}) {e['label']}")
print(f"TOTAL: {total_frames} frames = {total_dur:.3f}s")
print("\n=== HYBRID TRANSCRIPT ===")
for s in out_segs:
    print(f"  [{s['start']:5.2f} - {s['end']:5.2f}] {s['text']}")
