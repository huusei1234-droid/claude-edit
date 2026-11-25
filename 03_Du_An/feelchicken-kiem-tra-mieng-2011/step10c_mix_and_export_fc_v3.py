import json, math, os, shutil, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")

SKILL_AUDIO_DIR = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"
TLH_BGM_DIR     = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)"
TLH_SFX_DIR     = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
TLH_MEME_DIR    = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\03_Video Meme & Chèn Cảnh"

RAW_VID      = os.path.join(PROJ_DIR, "_fc_kute_v3_video_only.mp4")
VO_MASTER    = os.path.join(STEMS_DIR, "01_Voice_Master_V3.wav")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4")
DRIVE_FINAL  = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
FC_FINAL_DIR = r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-kiem-tra-mieng-2011"

SR = 48000

def build_tlh_index():
    idx = {}
    for base in (TLH_SFX_DIR, TLH_MEME_DIR):
        if os.path.exists(base):
            for r, _, files in os.walk(base):
                for fn in files:
                    idx[fn] = os.path.join(r, fn)
    return idx

TLH_INDEX = build_tlh_index()
def tlh_path(fname):
    return TLH_INDEX.get(fname, os.path.join(TLH_SFX_DIR, fname))

SFX_SPECS = {
    "tlh_star_open": (tlh_path("Mở cảnh - Tiếng chuông sao lung linh.mp3"), 0.00, 1.80, None),
    "tlh_slap_crisp":(tlh_path("Đánh tát - Tiếng tát bốp rõ kêu (Slap).mp3"), 0.00, 0.55, "highpass=f=90"),
    "tlh_thud_wood": (tlh_path("Vật lý - Tiếng va đập trầm (Thud).mp3"), 0.00, 0.60, "lowpass=f=3200"),
    "tlh_vine_boom": (tlh_path("Impact - Tiếng Vine Boom trầm meme.mp3"), 0.00, 1.10, "highpass=f=55,lowpass=f=4500"),
    "tlh_crickets":  (os.path.join(TLH_BGM_DIR, "12_Nhạc Tình Huống Ngắn & Đa Dụng", "AFX_CRICKETS_1_DFMG (6s).mp3"), 0.10, 1.45, "highpass=f=1200"),
    "tlh_whip_turn": (tlh_path("Clip Hiệu Ứng - Tiếng xoẹt quay đầu ngạc nhiên.mov"), 0.00, 0.85, "highpass=f=120"),
    "tlh_yay_kids":  (tlh_path("Tiếng Cười & Vỗ Tay - Yay! Energetic children(1011045) (2s).mp3"), 0.00, 2.10, "highpass=f=150"),
    "tlh_yeah_cheer":(tlh_path("Reo hò - Tiếng hô Yeah phấn khích.mp3"), 0.00, 1.80, "highpass=f=150"),
    "tlh_wow_anime": (tlh_path("Ngạc nhiên - Tiếng Wow trầm trồ anime.mp3"), 0.00, 1.50, "highpass=f=150"),
    "tlh_fireworks": (tlh_path("Đời Thường & ASMR - Fireworks (14s).mp3"), 0.20, 2.80, "highpass=f=180,lowpass=f=9000"),
    "tlh_pop1":      (tlh_path("Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3"), 0.00, 0.38, None),
    "tlh_pop2":      (tlh_path("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"), 0.00, 0.32, None),
    "tlh_boing":     (tlh_path("Hoạt hình - Lò xo nảy Boing Boing.mp3"), 0.00, 0.55, "lowpass=f=3800"),
    "tlh_ting":      (tlh_path("Ting - Chuông Ting nảy ý tưởng.mp3"), 0.00, 1.25, None),
    "tlh_notif":     (tlh_path("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"), 0.00, 0.55, None),
    "tlh_swoosh":    (tlh_path("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"), 0.02, 0.42, None),
    "tlh_whoosh_tvc":(tlh_path("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"), 0.02, 0.55, None),
    "tlh_plip":      (tlh_path("UI - Tiếng chạm màn hình cảm ứng Plip Plip.mp3"), 0.02, 0.45, None),
    "sk_sparkle":    (os.path.join(SKILL_AUDIO_DIR, "sfx_sparkle_shine.mp3"), 0.00, 1.50, None),
    "sk_shimmer":    (os.path.join(SKILL_AUDIO_DIR, "sfx_crystal_shimmer.mp3"), 0.00, 1.60, None),
    "sk_whoosh":     (os.path.join(SKILL_AUDIO_DIR, "sfx_whoosh_soft.mp3"), 0.00, 0.55, None),
}

def decode_stereo_f32(path, dur_limit=None, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if dur_limit:
        cmd += ["-t", f"{dur_limit:.3f}"]
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

def load_sfx_bank():
    bank = {}
    for key, (path, t0, t1, extra_af) in SFX_SPECS.items():
        if not os.path.exists(path):
            print("WARNING missing SFX:", key, path, flush=True)
            continue
        af_parts = [f"atrim={t0:.3f}:{t1:.3f}", "asetpts=PTS-STARTPTS"]
        if extra_af:
            af_parts.append(extra_af)
        arr = decode_stereo_f32(path, af=",".join(af_parts))
        if len(arr) < 64:
            continue
        n_in = min(len(arr) // 4, int(0.005 * SR))
        n_out = min(len(arr) // 3, int(0.035 * SR))
        if n_in > 2:
            arr[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
        if n_out > 2:
            arr[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
        pk = float(np.max(np.abs(arr)))
        if pk > 1e-5:
            arr /= pk
        pk_idx = int(np.argmax(np.max(np.abs(arr), axis=1)))
        bank[key] = (arr, pk_idx)
    return bank

def stamp(bus, bank, key, target_sec, db, pan=0.0, align_peak=True):
    if key not in bank:
        return 0
    clip, pk_idx = bank[key]
    gain = 10.0 ** (db / 20.0)
    ang = (max(-1.0, min(1.0, pan)) + 1.0) * (math.pi / 4.0)
    g_l = gain * math.cos(ang) * 1.4142
    g_r = gain * math.sin(ang) * 1.4142
    s_idx = int(round(target_sec * SR)) - (pk_idx if align_peak else 0)
    e_idx = s_idx + len(clip)
    bs, be = max(0, s_idx), min(len(bus), e_idx)
    if be <= bs:
        return 0
    cs = bs - s_idx
    seg = clip[cs:cs + (be - bs)]
    bus[bs:be, 0] += seg[:, 0] * g_l
    bus[bs:be, 1] += seg[:, 1] * g_r
    return 1

def main():
    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v3.json"), encoding="utf-8"))
    segs = {s["id"]: s for s in tm["segments"]}
    vid_dur = float(tm["total_dur"])
    N = int(round(vid_dur * SR))

    vo = decode_stereo_f32(VO_MASTER, dur_limit=vid_dur, af="loudnorm=I=-14:TP=-1.2:LRA=9")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

    # User-requested BGM: Food Funk02 (1p49s).mp3!
    bgm_eq = "highpass=f=70,equalizer=f=2150:t=q:w=1.25:g=-4.5,equalizer=f=9500:t=q:w=1.2:g=1.4,lowpass=f=14800,loudnorm=I=-14:TP=-1.5:LRA=9"
    bgm_path = os.path.join(TLH_BGM_DIR, "08_Hip-Hop - Rap - Beat Ngầu Hiện Đại", "Food Funk02 (1p49s).mp3")
    b_raw = decode_stereo_f32(bgm_path, af="atrim=start=0.26,asetpts=PTS-STARTPTS," + bgm_eq)
    bgm = np.tile(b_raw, ((N // len(b_raw)) + 2, 1))[:N]
    t_axis = np.arange(N, dtype=np.float32) / SR
    fade_out_tail = np.clip((vid_dur - t_axis) / 0.85, 0.0, 1.0)
    bgm = bgm * fade_out_tail[:, None]

    hop = 480
    n_hops = (N + hop - 1) // hop
    vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
    vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
    speaking = (vo_rms > 0.020).astype(np.float32)
    sp_dil = np.zeros_like(speaking)
    for i_h in range(n_hops):
        if speaking[i_h] > 0.5:
            sp_dil[max(0, i_h - 16):min(n_hops, i_h + 24)] = 1.0
    win_sm = np.hanning(31).astype(np.float32); win_sm /= np.sum(win_sm)
    sp_sm = np.convolve(np.pad(sp_dil, (15, 15), mode="edge"), win_sm, mode="valid")[:n_hops]
    # Boost BGM during the real storefront outro (s6c_storefront) when voice finishes!
    gain_hop = 0.54 * (1.0 - sp_sm) + 0.29 * sp_sm
    bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, gain_hop).astype(np.float32)

    s1_end = segs["s1_skit"]["t1"]
    pause_mask = 1.0 - (
        np.clip((t_axis - 3.02) / 0.06, 0.0, 1.0) * np.clip(((s1_end - 0.04) - t_axis) / 0.08, 0.0, 1.0) * 0.90
    )
    bgm_ducked = bgm * (bgm_env * pause_mask)[:, None]

    bank = load_sfx_bank()
    sfx = np.zeros((N, 2), dtype=np.float32)

    s2_0  = segs["s2_table"]["t0"]
    s3_0  = segs["s3_program"]["t0"]
    s4_0  = segs["s4_questions"]["t0"]
    s5_0  = segs["s5_gifts"]["t0"]
    s6a_0 = segs["s6a_outro"]["t0"]
    s6b_0 = segs["s6b_thumbs"]["t0"]
    s6c_0 = segs["s6c_storefront"]["t0"]

    cues = [
        # Scene 1: Table slap + Thành clueless zoom
        ("tlh_star_open", 0.12, -14.5, 0.00, False),
        ("tlh_slap_crisp",1.41,  -7.2, +0.10, True),
        ("tlh_thud_wood", 1.41,  -7.8, +0.08, True),
        ("tlh_whip_turn", 3.06,  -9.5, +0.15, True),
        ("tlh_vine_boom", 3.10, -11.5,  0.00, True),
        ("tlh_crickets",  3.18, -15.0,  0.00, False),
        ("tlh_plip",      3.16, -12.5, -0.20, True),
        ("tlh_plip",      3.28, -12.0,  0.00, True),
        ("tlh_boing",     3.40, -11.5, +0.20, True),

        # Scene 2: POV Praying ("RUNG CẦM CẬP!!") + Fond Nostalgia ("BỒI HỒI")
        ("tlh_whoosh_tvc",s2_0,        -13.0, 0.00, True),
        ("tlh_whip_turn", s2_0 + 1.53, -10.8, 0.00, True),
        ("tlh_pop1",      s2_0 + 3.48, -10.8, 0.00, True),
        ("tlh_boing",     s2_0 + 4.20, -11.0,+0.10, True),
        ("sk_whoosh",     s2_0 + 4.91, -13.0, 0.00, True),
        ("tlh_pop1",      s2_0 + 6.90, -11.5, 0.00, True),
        ("sk_shimmer",    s2_0 + 7.68, -13.5, 0.00, False),

        # Scene 3: 20/11 Header + CELEBRATORY FIREWORKS & CAPCUT "YAY! / WOW!" ON CHALKBOARD (Image 3)!
        ("tlh_star_open", s3_0 + 0.05, -13.0, 0.00, False),
        ("tlh_swoosh",    s3_0 + 2.34, -13.5, 0.00, True),
        ("tlh_whoosh_tvc",s3_0 + 4.68, -11.2, 0.00, True),
        ("tlh_fireworks", s3_0 + 4.72, -11.8, 0.00, False),
        ("tlh_yay_kids",  s3_0 + 4.82,  -9.8,-0.10, False),  # Joyful CapCut Yay!!
        ("tlh_wow_anime", s3_0 + 6.15, -11.2,+0.15, False),  # Fun Wow! accent on NHẬN QUÀ NGAY!
        ("sk_sparkle",    s3_0 + 4.78, -12.5, 0.00, False),

        # Scene 4: 6 Quiz Cards jumping up rapidly & stacking across screen!
        ("sk_whoosh",     s4_0 + 0.04, -13.5, 0.00, True),
        ("tlh_pop1",      s4_0 + 0.65, -11.5,-0.20, True),
        ("tlh_pop2",      s4_0 + 1.32, -11.5,+0.20, True),
        ("tlh_pop1",      s4_0 + 1.98, -11.2,-0.15, True),
        ("tlh_notif",     s4_0 + 2.64, -11.5,+0.15, True),
        ("tlh_pop2",      s4_0 + 3.30, -11.2,-0.10, True),
        ("tlh_boing",     s4_0 + 3.98, -10.5, 0.00, True),

        # Scene 5: Standalone "CÓ QUÀ!!" + Real Food Cutaways + Full "20/11"!
        ("tlh_whoosh_tvc",s5_0 + 0.04, -13.0, 0.00, True),
        ("tlh_ting",      s5_0 + 0.88, -10.2, 0.00, True),   # Emphasis chime on standalone "CÓ QUÀ!!"
        ("tlh_yeah_cheer",s5_0 + 0.92, -12.5,+0.10, False),
        ("sk_whoosh",     s5_0 + 1.56, -13.0, 0.00, True),
        ("tlh_swoosh",    s5_0 + 3.11, -13.5, 0.00, True),
        ("sk_whoosh",     s5_0 + 4.67, -13.5, 0.00, True),
        ("tlh_pop1",      s5_0 + 7.92, -11.5, 0.00, True),

        # Scene 6A, 6B, 6C: Wide Students -> Crispy Chicken Bites -> Khang -> Real Storefront Fireworks!
        ("tlh_whoosh_tvc",s6a_0 + 0.04, -13.0, 0.00, True),
        ("sk_shimmer",    s6a_0 + 0.16, -13.5, 0.00, False),
        ("tlh_swoosh",    s6a_0 + 2.45, -13.5, 0.00, True),
        ("tlh_swoosh",    s6a_0 + 4.20, -13.5, 0.00, True),
        ("tlh_pop1",      s6b_0 + 0.04, -12.5, 0.00, True),
        ("tlh_whoosh_tvc",s6c_0 + 0.02, -11.8, 0.00, True),
        ("tlh_star_open", s6c_0 + 0.08, -12.0, 0.00, False),
        ("tlh_yay_kids",  s6c_0 + 0.18, -12.2, 0.00, False),
    ]
    for k, ts, db, pan, ap in cues:
        stamp(sfx, bank, k, ts, db, pan=pan, align_peak=ap)

    raw_mix = vo * 1.02 + bgm_ducked + sfx
    raw_mix_p = os.path.join(STEMS_DIR, "_raw_mix_v3.wav")
    save_wav_16(raw_mix_p, raw_mix)

    p1 = subprocess.run([
        "ffmpeg", "-v", "info", "-i", raw_mix_p,
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=9.0:print_format=json",
        "-f", "null", "-"
    ], capture_output=True, text=True)
    ln = json.loads(p1.stderr[p1.stderr.rfind("{"):p1.stderr.rfind("}") + 1])
    af_p2 = (
        f"loudnorm=I=-14.0:TP=-1.0:LRA=9.0:measured_I={ln['input_i']}:"
        f"measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:"
        f"measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true"
    )
    master_wav = os.path.join(STEMS_DIR, "04_Final_Broadcast_Master_V3.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_mix_p, "-af", af_p2, "-ar", "48000", "-ac", "2", master_wav], check=True)

    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", RAW_VID, "-i", master_wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-movflags", "+faststart", LOCAL_FINAL
    ], check=True)

    p_chk = subprocess.run([
        "ffmpeg", "-v", "info", "-i", LOCAL_FINAL,
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=9.0:print_format=json",
        "-f", "null", "-"
    ], capture_output=True, text=True)
    j2 = json.loads(p_chk.stderr[p_chk.stderr.rfind("{"):p_chk.stderr.rfind("}") + 1])
    print(f"Final V3 Mastered Video -> {LOCAL_FINAL} | I={j2['input_i']} LUFS | TP={j2['input_tp']} dBTP", flush=True)

    for dst in (DRIVE_FINAL, FC_FINAL_DIR, LOCAL_EXPORT):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(LOCAL_FINAL, dst)
        print("Synced V3 Final MP4 ->", dst, flush=True)

    os.makedirs(DRIVE_PROJ, exist_ok=True)
    for pyf in ("step10a_prep_v3_timeline_and_clips.py", "step10b_render_fc_v3.py", "step10c_mix_and_export_fc_v3.py"):
        sp = os.path.join(PROJ_DIR, pyf)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(DRIVE_PROJ, pyf))

    thumbs = []
    for ts in [1.46, 8.85, 12.80, 15.00, 19.60, 26.60, 29.15, 31.40, 36.20, 38.00, 41.50, 45.60]:
        fp = os.path.join(CHECK_DIR, "_fcs3.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", LOCAL_FINAL, "-vf", "scale=270:480", "-frames:v", "1", fp], check=True)
        im = Image.open(fp).convert("RGB")
        dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, 110, 26], fill=(0, 0, 0))
        dr.text((8, 6), f"t={ts:.2f}s", fill=(255, 235, 90))
        thumbs.append(im)
        os.remove(fp)

    grid = Image.new("RGB", (270 * 6, 480 * 2))
    for i, im in enumerate(thumbs):
        grid.paste(im, ((i % 6) * 270, (i // 6) * 480))
    cs_out = os.path.join(CHECK_DIR, "final_v3_contact_sheet.jpg")
    grid.save(cs_out, quality=92)
    shutil.copy2(cs_out, os.path.join(DRIVE_PROJ, "final_v3_contact_sheet.jpg"))
    print("Saved Final V3 Contact Sheet:", cs_out, flush=True)

if __name__ == "__main__":
    main()
