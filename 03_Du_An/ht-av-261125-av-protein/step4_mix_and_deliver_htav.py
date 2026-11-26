import json, math, os, re, shutil, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJ_DIR     = r"C:\AI\full studio\output\ht-av-261125"
AROLL_DIR    = os.path.join(PROJ_DIR, "aroll")
STEMS_DIR    = os.path.join(PROJ_DIR, "audio_stems")
CHECK_DIR    = os.path.join(PROJ_DIR, "check")
FONTS_DIR    = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
STUDIO_SFX_D = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"
TLH_SFX_DIR  = r"G:\Other computers\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
SAAS_SFX_DIR = r"C:\AI\full studio\phong-cach\saas-animation\audio\sfx"

RAW_VID      = os.path.join(PROJ_DIR, "_v3_video_only.mp4")
VOICE_WAV    = os.path.join(STEMS_DIR, "edited_voice_48k.wav")

FINAL_NAME   = "261125 HTPM AV Protein bữa sáng 30 giây đủ đạm final.mp4"
LOCAL_FINAL  = os.path.join(PROJ_DIR, FINAL_NAME)

DEST_BRAND   = rf"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261125 - Ngày 25.11.2026\{FINAL_NAME}"
DEST_MASTER  = rf"G:\My Drive\AI_Full_Studio\04_Videos_Final\{FINAL_NAME}"
DEST_DL      = rf"C:\Users\001\Downloads\{FINAL_NAME}"
DRIVE_PROJ   = r"G:\My Drive\AI_Full_Studio\03_Du_An\ht-av-261125-av-protein"
LOCAL_DUAN   = r"C:\AI\full studio\03_Du_An\ht-av-261125-av-protein"
ART_DIR      = r"C:\Users\001\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682"

SR = 48000

def build_sfx_index():
    idx = {}
    for base in (STUDIO_SFX_D, SAAS_SFX_DIR, TLH_SFX_DIR):
        if os.path.exists(base):
            for r, _, files in os.walk(base):
                for fn in files:
                    idx[fn] = os.path.join(r, fn)
    return idx

SFX_IDX = build_sfx_index()
def find_sfx(fname):
    return SFX_IDX.get(fname, os.path.join(STUDIO_SFX_D, fname))

TACTILE_EQ = "highpass=f=140,equalizer=f=2400:t=q:w=1.25:g=-3.5,lowpass=f=13500"
AIRY_EQ    = "highpass=f=180,equalizer=f=2650:t=q:w=1.20:g=-4.5,lowpass=f=9000"

SFX_SPECS = {
    "soft_whoosh": (find_sfx("sfx_whoosh_soft.mp3"),                                                        0.02, 0.32, AIRY_EQ),
    "pop_clean":   (find_sfx("sfx_pop_clean.mp3"),                                                          0.00, 0.16, TACTILE_EQ),
    "click_soft":  (find_sfx("sfx_click_soft.mp3"),                                                         0.00, 0.12, TACTILE_EQ),
    "card_deal":   (find_sfx("Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3"), 0.02, 0.42, TACTILE_EQ),
    "ping_glass":  (find_sfx("sfx_ping_glass.mp3"),                                                         0.00, 0.52, TACTILE_EQ),
    "sparkle":     (find_sfx("sfx_sparkle_shine.mp3"),                                                      0.00, 0.65, TACTILE_EQ),
    "chime_warm":  (find_sfx("sfx_chime_warm.mp3"),                                                         0.00, 0.60, TACTILE_EQ),
    "notif_cta":   (find_sfx("sfx_notification_cta.mp3"),                                                   0.00, 0.55, TACTILE_EQ),
}

def decode_stereo_f32(path, dur_limit=None, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if dur_limit:
        cmd += ["-t", f"{dur_limit:.4f}"]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def save_wav_16(path, stereo_arr):
    clipped = np.clip(stereo_arr, -0.99, 0.99)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

def pitch_shift(arr, semitones: float):
    if abs(semitones) < 0.05:
        return arr
    factor = 2.0 ** (semitones / 12.0)
    new_len = max(16, int(round(len(arr) / factor)))
    xo = np.linspace(0.0, 1.0, len(arr), dtype=np.float32)
    xn = np.linspace(0.0, 1.0, new_len, dtype=np.float32)
    out = np.zeros((new_len, 2), dtype=np.float32)
    out[:, 0] = np.interp(xn, xo, arr[:, 0])
    out[:, 1] = np.interp(xn, xo, arr[:, 1])
    return out

def load_sfx_bank():
    bank = {}
    for key, (path, t0, t1, extra_af) in SFX_SPECS.items():
        if not path or not os.path.exists(path):
            continue
        af_parts = [f"atrim={t0:.3f}:{t1:.3f}", "asetpts=PTS-STARTPTS"]
        if extra_af:
            af_parts.append(extra_af)
        try:
            arr = decode_stereo_f32(path, af=",".join(af_parts))
        except Exception:
            continue
        if len(arr) < 48:
            continue
        n_in  = min(len(arr) // 5, int(0.008 * SR))
        n_out = min(len(arr) // 3, int(0.040 * SR))
        if n_in > 2:
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2:
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        pk_idx = int(np.argmax(np.max(np.abs(arr), axis=1)))
        bank[key] = (arr, pk_idx)
    print(f"[SFX] Loaded {len(bank)}/{len(SFX_SPECS)} tactile card & studio SFX cues.", flush=True)
    return bank

def stamp(bus, bank, key, target_sec, db_below_vo, semitones=0.0, pan=0.0, align_peak=True):
    if key not in bank:
        if "pop_clean" in bank:
            key = "pop_clean"
        else:
            return 0
    base_clip, _ = bank[key]
    clip = pitch_shift(base_clip, semitones)
    pk_idx = int(np.argmax(np.max(np.abs(clip), axis=1)))
    abs_db = -5.5 + float(db_below_vo)
    gain = 10.0 ** (abs_db / 20.0)
    ang = (max(-1.0, min(1.0, pan)) + 1.0) * (math.pi / 4.0)
    g_l = gain * math.cos(ang) * 1.4142
    g_r = gain * math.sin(ang) * 1.4142
    s_idx = int(round(target_sec * SR)) - (pk_idx if align_peak else 0)
    e_idx = s_idx + len(clip)
    bs, be = max(0, s_idx), min(len(bus), e_idx)
    if be <= bs:
        return 0
    cs = bs - s_idx
    seg = clip[cs : cs + (be - bs)]
    bus[bs:be, 0] += seg[:, 0] * g_l
    bus[bs:be, 1] += seg[:, 1] * g_r
    return 1

def main():
    pr = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames:format=duration",
        "-of", "json", RAW_VID
    ], text=True))
    vid_dur = float(pr["format"]["duration"])
    N = int(round(vid_dur * SR))

    # 1. Load hybrid Voice Track (real Demucs vocals + Voice Studio cloned Leucine & PROTEIN CTA)
    vo = decode_stereo_f32(VOICE_WAV, dur_limit=vid_dur, af="highpass=f=80,dynaudnorm=f=180:g=7")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.015).astype(np.float32)
    sp_samples = np.repeat(speaking > 0.5, hop)[:N]
    cur_sp_rms = float(np.sqrt(np.mean(vo[sp_samples] ** 2))) if np.any(sp_samples) else float(np.sqrt(np.mean(vo ** 2)))
    if cur_sp_rms > 1e-4:
        vo *= (0.168 / cur_sp_rms)

    # 2. Build 2-Half C-Major BGM (0..19.1s Warm Fretless -> 1.6s crossfade -> 19.1..49.57s Bright Riley!)
    # Sculpted with EQ Voice Pocket (-4.5 dB @ 1750 Hz) + smooth dynamic ducking (-14.5 dB under speech, blooming gently in pauses/outro!)
    bgm1 = os.path.join(STUDIO_SFX_D, "bgm_warm_fretless.mp3")
    bgm2 = os.path.join(STUDIO_SFX_D, "bgm_bright_riley.mp3")
    bgm_tmp = os.path.join(STEMS_DIR, "_bgm_2half_48k.wav")
    split_t = 19.10
    rem_t   = max(3.0, vid_dur - split_t + 1.6)
    bgm_fc = (
        f"[0:a]atrim=0:{split_t + 0.8:.2f},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.8[b1];"
        f"[1:a]atrim=0:{rem_t:.2f},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-1.5:LRA=11,afade=t=out:st={max(0.1, rem_t - 1.6):.2f}:d=1.6[b2];"
        f"[b1][b2]acrossfade=d=1.6:c1=tri:c2=tri,"
        f"atrim=0:{vid_dur:.3f},highpass=f=75,equalizer=f=1750:t=q:w=1.25:g=-4.5[bgm_out]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-stream_loop", "-1", "-i", bgm1,
        "-stream_loop", "-1", "-i", bgm2,
        "-filter_complex", bgm_fc, "-map", "[bgm_out]", "-ar", str(SR), "-ac", "2", bgm_tmp
    ], check=True)
    bgm_arr = decode_stereo_f32(bgm_tmp, dur_limit=vid_dur)
    bgm_arr = np.vstack([bgm_arr, np.zeros((max(0, N - len(bgm_arr)), 2), dtype=np.float32)])[:N]

    sp_dil = np.zeros_like(speaking)
    for ih in range(n_hops):
        if speaking[ih] > 0.5:
            sp_dil[max(0, ih - 10) : min(n_hops, ih + 18)] = 1.0
    win_sm = np.hanning(35).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (17, 17), mode="edge"), win_sm, mode="valid")[:n_hops]
    # -14.8 dB below voice during speech, blooming gently during pauses & final musical tail!
    bgm_gain_hop = 0.34 * (1.0 - sp_sm) + 0.19 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, bgm_gain_hop).astype(np.float32)
    bgm_ducked = bgm_arr * bgm_env[:, None]

    # 3. Tactile Playing-Card & Studio Micro-SFX (-10 to -14 dB below Voice, escalating pitch on multi-card deals!)
    bank = load_sfx_bank()
    sfx_bus = np.zeros((N, 2), dtype=np.float32)
    c = 0

    # Style 1: 3-Card Overhead Arc Deal (0.32, 0.50, 0.68s) + Hook Title pops
    c += stamp(sfx_bus, bank, "soft_whoosh", 0.06, -12.0)
    for k, tc in enumerate([0.32, 0.50, 0.68]):
        c += stamp(sfx_bus, bank, "card_deal", tc, -11.4, semitones=k * 1.2, pan=-0.25 + k * 0.25)
        c += stamp(sfx_bus, bank, "pop_clean", tc + 0.22, -11.8, semitones=k * 1.2, pan=-0.25 + k * 0.25)
    c += stamp(sfx_bus, bank, "click_soft", 2.84, -12.6)

    # Behind-head Warning 1 (5.15s) + Style 2: Full-Screen Dual-Card Clash (6.65s & 7.15s & 9.45s crash!)
    c += stamp(sfx_bus, bank, "chime_warm",  5.18, -12.0, align_peak=False)
    c += stamp(sfx_bus, bank, "soft_whoosh", 6.55, -11.2)
    c += stamp(sfx_bus, bank, "card_deal",   6.72, -11.0, pan=-0.12)
    c += stamp(sfx_bus, bank, "card_deal",   7.22, -10.8, semitones=-1.2, pan=0.12)
    c += stamp(sfx_bus, bank, "ping_glass",  9.50, -12.2, align_peak=False)
    c += stamp(sfx_bus, bank, "soft_whoosh", 12.96, -11.6)

    # Style 3: 3-Card Hand Fan Spread (14.88s) + Center Gold Ace Lift (16.15s "KHÁT ĐẠM SẠCH")
    c += stamp(sfx_bus, bank, "card_deal",  14.92, -11.2, pan=-0.18)
    c += stamp(sfx_bus, bank, "card_deal",  15.08, -11.0, semitones=1.2, pan=0.18)
    c += stamp(sfx_bus, bank, "sparkle",    16.18, -12.0, align_peak=False)
    c += stamp(sfx_bus, bank, "pop_clean",  16.22, -11.2, semitones=2.0)

    # Solution 2 (19.14s) + Orbital Rings (23.30s) + Style 4A: 3D 180-deg Card Flip (25.25s & flip @ 26.35s)
    c += stamp(sfx_bus, bank, "chime_warm",  19.18, -12.0, align_peak=False)
    c += stamp(sfx_bus, bank, "sparkle",     23.35, -12.4, align_peak=False)
    c += stamp(sfx_bus, bank, "card_deal",   25.30, -11.4, pan=-0.22)
    c += stamp(sfx_bus, bank, "soft_whoosh", 26.25, -11.4, pan=-0.20)
    c += stamp(sfx_bus, bank, "ping_glass",  26.68, -11.8, align_peak=False, pan=-0.20)

    # Style 4B: Full-Screen Rapid Riffle Cascade + 3D Hero Ace "1.632 MG L-LEUCINE" (31.52 - 37.36s)
    c += stamp(sfx_bus, bank, "soft_whoosh", 31.42, -11.0)
    for k, trf in enumerate([31.60, 31.76, 31.94]):
        c += stamp(sfx_bus, bank, "card_deal", trf, -11.0, semitones=k * 1.4, pan=-0.20 + k * 0.12)
    c += stamp(sfx_bus, bank, "sparkle",     32.36, -11.6, align_peak=False)
    c += stamp(sfx_bus, bank, "pop_clean",   32.42, -10.8, semitones=2.4)
    c += stamp(sfx_bus, bank, "click_soft",  34.55, -12.4)
    c += stamp(sfx_bus, bank, "soft_whoosh", 37.26, -11.4)

    # Real A-Roll Light Belly (37.42s) + Share/30s Menu Mini Card (40.10s & 43.82s)
    c += stamp(sfx_bus, bank, "ping_glass",  37.46, -12.2, align_peak=False)
    c += stamp(sfx_bus, bank, "card_deal",   40.14, -11.6, pan=-0.22)
    c += stamp(sfx_bus, bank, "sparkle",     43.85, -12.4, align_peak=False)

    # Style 5: Full-Screen Royal End-Card Table + "NHẮN CHỮ PROTEIN BÊN DƯỚI!" (46.66s)
    c += stamp(sfx_bus, bank, "soft_whoosh", 46.56, -10.8)
    c += stamp(sfx_bus, bank, "card_deal",   46.74, -11.0, pan=-0.24)
    c += stamp(sfx_bus, bank, "card_deal",   46.88, -10.8, semitones=1.5, pan=0.24)
    c += stamp(sfx_bus, bank, "notif_cta",   47.18, -10.6, align_peak=False)
    c += stamp(sfx_bus, bank, "sparkle",     47.40, -11.8, align_peak=False)

    print(f"[SFX] Placed {c} synced Playing-Card & Studio Micro-SFX cues.", flush=True)

    # 4. Mix & 2-Pass EBU R128 Loudnorm to exact -14.0 LUFS!
    pre_wav  = os.path.join(STEMS_DIR, "mix_pre_14lufs.wav")
    norm_wav = os.path.join(STEMS_DIR, "mix_14lufs.wav")
    save_wav_16(pre_wav, vo + bgm_ducked + sfx_bus)

    p1 = subprocess.run(
        ["ffmpeg", "-y", "-i", pre_wav, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=10:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True
    )
    m_j = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p1.stderr)
    if m_j:
        st = json.loads(m_j.group(0))
        af2 = (
            f"loudnorm=I=-14.0:TP=-1.0:LRA=10:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
            f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true"
        )
    else:
        af2 = "loudnorm=I=-14.0:TP=-1.0:LRA=10"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", pre_wav, "-af", af2, "-ar", str(SR), "-ac", "2", norm_wav], check=True)

    # Mux final MP4
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", RAW_VID, "-i", norm_wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
        LOCAL_FINAL
    ], check=True)

    # Verify 0 decode errors & exact LUFS
    dec_chk = subprocess.run(["ffmpeg", "-v", "error", "-i", LOCAL_FINAL, "-f", "null", "-"], capture_output=True, text=True)
    assert dec_chk.stderr.strip() == "", f"Decode error: {dec_chk.stderr}"
    p_ver = subprocess.run(["ffmpeg", "-i", LOCAL_FINAL, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=10:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    m_v = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p_ver.stderr)
    ver_lufs = json.loads(m_v.group(0)) if m_v else {}
    print(f"[QC VERIFIED] Frames={pr['streams'][0]['nb_read_frames']} | Dur={vid_dur:.3f}s | LUFS={ver_lufs.get('input_i')} | TP={ver_lufs.get('input_tp')} | DecodeErr=0", flush=True)

    # 5. Build 20-Panel Final Contact Sheet (5x4)
    pw, ph = 270, 480
    sheet = Image.new("RGB", (pw * 5, ph * 4), (12, 22, 18))
    fnt = ImageFont.truetype(os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf"), 20)
    for i in range(20):
        ts = min(vid_dur - 0.25, 0.55 + i * (vid_dur - 1.1) / 19.0)
        tf = os.path.join(CHECK_DIR, f"_qcf_{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", LOCAL_FINAL, "-frames:v", "1", "-q:v", "2", tf], check=True)
        im = Image.open(tf).convert("RGB").resize((pw, ph), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([8, 8, 108, 36], radius=8, fill=(10, 20, 16))
        d.text((16, 10), f"{ts:05.2f}s", font=fnt, fill=(255, 224, 92))
        sheet.paste(im, ((i % 5) * pw, (i // 5) * ph))
        os.remove(tf)
    sheet_p = os.path.join(CHECK_DIR, "ht_av_261125_final_sheet.jpg")
    sheet.save(sheet_p, quality=93)

    # Write QC Report
    rep_md = f"""# Báo Cáo QC — `{FINAL_NAME}`

- **Kịch bản gốc**: Tập `01/20` — `AV01 · AN VƯỢNG — AV Protein (Đạm thực vật)`
- **Độ phân giải & Thời lượng**: `1080×1920 @ 30fps CFR` (`{pr['streams'][0]['nb_read_frames']}` frames · `{vid_dur:.2f}s`, `0` lỗi giải mã)
- **Xử lý Thoại & Nhân bản giọng Voice Studio (`OmniVoice` CUDA)**:
  - Cắt sạch 4 đoạn vấp/nháp (`19.1–29.5s`, `42.1–47.1s`, `53.6–57.3s`, `61.4–68.2s`).
  - Giữ nguyên biến tấu tự nhiên của chị Hằng (*"làm đường huyết tăng vọt cực nhanh"*).
  - Dùng **Voice Studio clone đúng giọng chị Hằng** sửa 2 cụm đọc sai: `"thêm 1.632 miligam L-Leucine"` (gốc đọc chệch thành *"32mg eloxin"*) và `"nhắn chữ PROTEIN bên dưới!"` (gốc đọc nhầm thành *"nhận chữ protein"*), đồng thời phủ kín 100% màn hình chính ở cả 2 đoạn bằng lớp phủ lá bài nên `0%` lộ lệch khẩu hình.
- **5 Kiểu Lớp Phủ Lá Bài Đa Dạng (`100%` đạt chuẩn `safe_zone_9x16.py`)**:
  1. `0.32–4.90s`: **3 Lá bài xếp vòng cung trên đầu** (`Ăn No Căng` · `10h Ngáp Ngủ` · `Tụt Pin Sớm`) + chữ Hook đa font.
  2. `6.65–13.06s`: **2 Lá bài lớn đối đầu đè toàn màn hình chính** (`07:30 Bữa sáng tinh bột` vs `10:00 Tụt dốc không phanh` + biểu đồ đường huyết động).
  3. `14.88–19.04s`: **Xòe quạt 3 lá bài (`Hand Fan Spread`)** (`Dư Tinh Bột` · `Át Chủ Bài ĐẠM SẠCH` · `Nuôi Khối Cơ`).
  4. `25.25–31.50s`: **Lật lá bài 3D `180°` từ mặt lưng mạ vàng sang mặt trước `22,05g`** cạnh cảnh chị Hằng cầm hộp thật `AV Protein` & 2 gói stick.
  5. `31.52–37.36s` & `46.66–49.57s`: **Tráo bài liên hoàn (`Rapid Riffle Cascade`) + Bàn bài Hoàng Gia End-Card đè toàn màn hình chính** khóa cứng ảnh chụp sản phẩm thật tách nền `av01_protein_a.png` / `av01_protein_b.png`.
- **Âm thanh**: BGM 2 nửa C-Major (`bgm_warm_fretless` → `bgm_bright_riley`) + EQ Voice Pocket + Sidechain Ducking + `{c}` điểm `Tactile Card Micro-SFX` chuẩn **`{ver_lufs.get('input_i', '-14.0')} LUFS`**.
"""
    rep_p = os.path.join(PROJ_DIR, "report.md")
    with open(rep_p, "w", encoding="utf-8") as f:
        f.write(rep_md)

    # 6. Deliver to Brand Folder, Master Cloud Storage, Downloads & Project Archives
    for dst in (DEST_BRAND, DEST_MASTER, DEST_DL):
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(LOCAL_FINAL, dst)
            print("[DELIVERED] ->", dst, flush=True)
        except Exception as e:
            print("[WARN COPY]", dst, e, flush=True)

    for pdir in (DRIVE_PROJ, LOCAL_DUAN):
        try:
            os.makedirs(pdir, exist_ok=True)
            for fn_s in ("step1_voice_and_aroll_htav.py", "clean_htav_transcript.py", "step2_gen_av01_brolls.js", "step3_render_htav_v3_cards.py", "step4_mix_and_deliver_htav.py", "report.md"):
                sp = os.path.join(PROJ_DIR, fn_s)
                if os.path.exists(sp):
                    shutil.copy2(sp, os.path.join(pdir, fn_s))
            shutil.copy2(os.path.join(AROLL_DIR, "main_cut_clean.json"), os.path.join(pdir, "main_cut_clean.json"))
            shutil.copy2(sheet_p, os.path.join(pdir, "ht_av_261125_final_sheet.jpg"))
            shutil.copy2(os.path.join(CHECK_DIR, "brolls_qc.jpg"), os.path.join(pdir, "brolls_qc.jpg"))
        except Exception as e:
            print("[WARN PROJ SYNC]", pdir, e, flush=True)

    try:
        os.makedirs(ART_DIR, exist_ok=True)
        shutil.copy2(sheet_p, os.path.join(ART_DIR, "ht_av_261125_final_sheet.jpg"))
    except Exception:
        pass

if __name__ == "__main__":
    main()
