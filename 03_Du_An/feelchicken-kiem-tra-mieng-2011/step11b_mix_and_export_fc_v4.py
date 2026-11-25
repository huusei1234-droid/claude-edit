import json, math, os, shutil, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")

TLH_BGM_DIR  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)"
RAW_VID      = os.path.join(PROJ_DIR, "_fc_kute_v4_video_only.mp4")
VO_MASTER    = os.path.join(STEMS_DIR, "01_Voice_Master_V3.wav")
LOCAL_FINAL  = os.path.join(PROJ_DIR, "FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4")
DRIVE_FINAL  = r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
FC_FINAL_DIR = r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
LOCAL_EXPORT = r"D:\XUẤT CAPCUT\FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"
DRIVE_PROJ   = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-kiem-tra-mieng-2011"

SR = 48000

import sys
sys.path.insert(0, PROJ_DIR)
from step10c_mix_and_export_fc_v3 import decode_stereo_f32, save_wav_16, load_sfx_bank, stamp

def main():
    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v3.json"), encoding="utf-8"))
    segs = {s["id"]: s for s in tm["segments"]}
    vid_dur = float(tm["total_dur"])
    N = int(round(vid_dur * SR))

    vo = decode_stereo_f32(VO_MASTER, dur_limit=vid_dur, af="loudnorm=I=-14:TP=-1.2:LRA=9")
    vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

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
    gain_hop = 0.55 * (1.0 - sp_sm) + 0.29 * sp_sm
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

        # Scene 2: POV Praying ("RUNG CẦM CẬP!!") + Emotional Vietnamese Students Nostalgia ("BỒI HỒI")
        ("tlh_whoosh_tvc",s2_0,        -13.0, 0.00, True),
        ("tlh_whip_turn", s2_0 + 1.53, -10.8, 0.00, True),
        ("tlh_pop1",      s2_0 + 3.48, -10.8, 0.00, True),
        ("tlh_boing",     s2_0 + 4.20, -11.0,+0.10, True),
        ("sk_whoosh",     s2_0 + 4.91, -13.0, 0.00, True),
        ("sk_shimmer",    s2_0 + 6.95, -12.2, 0.00, False),  # Warm emotional shimmer as VN students appear!
        ("tlh_pop1",      s2_0 + 6.90, -11.8, 0.00, True),

        # Scene 3: 3 CS1 Shots + Fireworks Chalkboard + Yay!/Wow!
        ("tlh_star_open", s3_0 + 0.05, -13.0, 0.00, False),
        ("tlh_swoosh",    s3_0 + 1.56, -13.5, 0.00, True),
        ("tlh_swoosh",    s3_0 + 3.12, -13.5, 0.00, True),
        ("tlh_whoosh_tvc",s3_0 + 4.68, -11.2, 0.00, True),
        ("tlh_fireworks", s3_0 + 4.72, -11.8, 0.00, False),
        ("tlh_yay_kids",  s3_0 + 4.82,  -9.8,-0.10, False),
        ("tlh_wow_anime", s3_0 + 6.15, -11.2,+0.15, False),
        ("sk_sparkle",    s3_0 + 4.78, -12.5, 0.00, False),

        # Scene 4: 2 Uploaded Question-Jar Sources + 6 Rapid Quiz Cards Bursting Out!
        ("sk_whoosh",     s4_0 + 0.04, -13.0, 0.00, True),
        ("tlh_swoosh",    s4_0 + 2.15, -12.5, 0.00, True),
        ("tlh_pop1",      s4_0 + 3.32, -11.2,-0.20, True),
        ("tlh_pop2",      s4_0 + 3.70, -11.2,+0.20, True),
        ("tlh_pop1",      s4_0 + 4.08, -11.2,-0.15, True),
        ("tlh_notif",     s4_0 + 4.46, -11.2,+0.15, True),
        ("tlh_pop2",      s4_0 + 4.84, -11.0,-0.10, True),
        ("tlh_boing",     s4_0 + 5.22, -10.5, 0.00, True),

        # Scene 5: Centered Khang + Standalone "CÓ QUÀ!!" + 3 CS1 Close-up Food Shots + Behind-Head Animated Text!
        ("tlh_whoosh_tvc",s5_0 + 0.04, -13.0, 0.00, True),
        ("tlh_ting",      s5_0 + 0.88, -10.2, 0.00, True),
        ("tlh_yeah_cheer",s5_0 + 0.92, -12.5,+0.10, False),
        ("sk_whoosh",     s5_0 + 1.56, -12.8, 0.00, True),
        ("tlh_pop1",      s5_0 + 1.62, -12.2,-0.10, True),
        ("tlh_swoosh",    s5_0 + 2.68, -13.2,+0.10, True),
        ("tlh_pop2",      s5_0 + 2.74, -12.2,+0.10, True),
        ("tlh_swoosh",    s5_0 + 3.80, -13.2,-0.10, True),
        ("tlh_pop1",      s5_0 + 3.86, -12.2,-0.10, True),
        ("sk_whoosh",     s5_0 + 4.92, -12.8, 0.00, True),
        ("sk_sparkle",    s5_0 + 4.98, -13.5, 0.00, False),
        ("tlh_ting",      s5_0 + 7.72, -11.0, 0.00, True),

        # Scene 6A, 6B, 6C: Zero-Zoom Crowded CS1 -> Energetic Bouncing Texts on Crispy Bite -> CS1 Storefront!
        ("tlh_whoosh_tvc",s6a_0 + 0.04, -13.0, 0.00, True),
        ("sk_shimmer",    s6a_0 + 0.16, -13.5, 0.00, False),
        ("tlh_swoosh",    s6a_0 + 2.72, -12.8, 0.00, True),
        ("tlh_pop1",      s6a_0 + 2.78, -11.5,-0.15, True),
        ("tlh_pop2",      s6a_0 + 3.24, -11.8,+0.15, True),
        ("tlh_swoosh",    s6a_0 + 4.32, -12.5, 0.00, True),
        ("tlh_boing",     s6a_0 + 4.38, -10.8, 0.00, True),
        ("tlh_wow_anime", s6a_0 + 4.55, -11.8,+0.15, False),
        ("tlh_pop1",      s6b_0 + 0.04, -12.5, 0.00, True),
        ("tlh_whoosh_tvc",s6c_0 + 0.02, -11.8, 0.00, True),
        ("tlh_star_open", s6c_0 + 0.08, -12.0, 0.00, False),
        ("tlh_yay_kids",  s6c_0 + 0.18, -12.2, 0.00, False),
    ]
    for k, ts, db, pan, ap in cues:
        stamp(sfx, bank, k, ts, db, pan=pan, align_peak=ap)

    raw_mix = vo * 1.02 + bgm_ducked + sfx
    raw_mix_p = os.path.join(STEMS_DIR, "_raw_mix_v4.wav")
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
    master_wav = os.path.join(STEMS_DIR, "04_Final_Broadcast_Master_V4.wav")
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
    print(f"Final V4 Mastered Video -> {LOCAL_FINAL} | I={j2['input_i']} LUFS | TP={j2['input_tp']} dBTP", flush=True)

    for dst in (DRIVE_FINAL, FC_FINAL_DIR, LOCAL_EXPORT):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(LOCAL_FINAL, dst)
        print("Synced V4 Final MP4 ->", dst, flush=True)

    os.makedirs(DRIVE_PROJ, exist_ok=True)
    for pyf in ("step11a_render_fc_v4_master.py", "step11b_mix_and_export_fc_v4.py"):
        sp = os.path.join(PROJ_DIR, pyf)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(DRIVE_PROJ, pyf))

    thumbs = []
    for ts in [5.30, 12.75, 15.80, 19.60, 23.00, 24.85, 27.45, 30.05, 34.40, 38.10, 41.80, 45.80]:
        fp = os.path.join(CHECK_DIR, "_fcs4.png")
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
    cs_out = os.path.join(CHECK_DIR, "final_v4_contact_sheet.jpg")
    grid.save(cs_out, quality=92)
    shutil.copy2(cs_out, os.path.join(DRIVE_PROJ, "final_v4_contact_sheet.jpg"))
    print("Saved Final V4 Contact Sheet:", cs_out, flush=True)

if __name__ == "__main__":
    main()
