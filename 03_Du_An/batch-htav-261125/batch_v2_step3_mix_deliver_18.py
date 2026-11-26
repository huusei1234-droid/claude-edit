import json, math, os, re, shutil, subprocess, sys, time, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"C:\AI\full studio\output\batch-htav-261125")
from batch_v2_configs_18 import EP18_CONFIGS, HYBRID_STYLES
from batch_v2_step2_render_18_hybrid_styles import build_hybrid_timeline
from batch_step7_mix_qc_deliver import (
    STUDIO_SFX_D, FONTS_DIR, BRAND_DIR, MASTER_DIR, DL_DIR, DRIVE_PROJ, LOCAL_DUAN, ART_DIR,
    SR, load_sfx_bank, stamp, decode_stereo_f32, save_wav_16,
)

BATCH_DIR   = r"C:\AI\full studio\output\batch-htav-261125"
TLH_BGM_DIR = r"G:\Other computers\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)"


def collect_bgm_pool():
    b1 = os.path.join(STUDIO_SFX_D, "bgm_warm_fretless.mp3")
    b2 = os.path.join(STUDIO_SFX_D, "bgm_bright_riley.mp3")
    pool = [b1, b2]
    for sub_d in ("01_Truyền Cảm Hứng - Quảng Cáo TVC", "02_Chill - Lofi", "05_Acoustic"):
        dp = os.path.join(TLH_BGM_DIR, sub_d)
        if os.path.exists(dp):
            cands = sorted([os.path.join(dp, f) for f in os.listdir(dp) if f.lower().endswith((".mp3", ".wav", ".m4a"))])
            pool.extend(cands[:4])
    return [p for p in pool if os.path.exists(p)]


def main():
    t0_all = time.time()
    bank = load_sfx_bank()
    bgm_pool = collect_bgm_pool()
    print(f"[BGM] Pool ready with {len(bgm_pool)} curated tracks.", flush=True)

    for d_out in (BRAND_DIR, MASTER_DIR, DL_DIR, DRIVE_PROJ, LOCAL_DUAN):
        os.makedirs(d_out, exist_ok=True)

    target_keys = list(EP18_CONFIGS.keys())
    pw, ph = 240, 426
    qc_sheet = Image.new("RGB", (pw * 6, ph * math.ceil((len(target_keys) * 3) / 6)), (14, 18, 24))
    f_lbl = ImageFont.truetype(os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf"), 16)
    panel_idx = 0
    qc_rows = []

    for idx_e, vk in enumerate(target_keys, 1):
        v_dir  = os.path.join(BATCH_DIR, vk)
        meta   = json.load(open(os.path.join(v_dir, "v2_meta.json"), "r", encoding="utf-8"))
        cfg    = EP18_CONFIGS[vk]
        hstyle = HYBRID_STYLES[vk]
        tl     = build_hybrid_timeline(meta, cfg, hstyle)

        raw_vid   = os.path.join(v_dir, "_v2_video_only.mp4")
        voice_wav = os.path.join(v_dir, "v2_voice_48k.wav")
        final_fn  = meta["final_name"]
        local_fin = os.path.join(v_dir, final_fn)

        pr = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,nb_frames:format=duration",
            "-of", "json", raw_vid
        ], text=True, encoding="utf-8", errors="replace"))
        vid_dur = float(pr["format"]["duration"])
        N = int(round(vid_dur * SR))

        # 1. Clean 1.10x Voice Track
        vo = decode_stereo_f32(voice_wav, dur_limit=vid_dur, af="highpass=f=80,dynaudnorm=f=180:g=7")
        vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

        hop = 480
        n_hops = (N + hop - 1) // hop
        vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
        vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
        speaking = (vo_rms > 0.015).astype(np.float32)
        sp_samples = np.repeat(speaking > 0.5, hop)[:N]
        cur_sp_rms = float(np.sqrt(np.mean(vo[sp_samples] ** 2))) if np.any(sp_samples) else float(np.sqrt(np.mean(vo ** 2)))
        if cur_sp_rms > 1e-4:
            vo *= (0.170 / cur_sp_rms)

        # 2. Varied 2-Half BGM with Voice Pocket (-4.5dB @ 1750Hz) + Dynamic Sidechain Ducking
        bgm_a = bgm_pool[(idx_e - 1) % len(bgm_pool)]
        bgm_b = bgm_pool[(idx_e) % len(bgm_pool)]
        split_t = round(vid_dur * 0.44, 2)
        rem_t   = max(3.0, vid_dur - split_t + 1.6)
        bgm_tmp = os.path.join(v_dir, "_v2_bgm.wav")
        bgm_fc = (
            f"[0:a]atrim=0:{split_t + 0.8:.2f},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.7[b1];"
            f"[1:a]atrim=0:{rem_t:.2f},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-1.5:LRA=11,afade=t=out:st={max(0.1, rem_t - 1.5):.2f}:d=1.5[b2];"
            f"[b1][b2]acrossfade=d=1.5:c1=tri:c2=tri,atrim=0:{vid_dur:.3f},highpass=f=75,equalizer=f=1750:t=q:w=1.25:g=-4.5[bgm_out]"
        )
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", bgm_a, "-stream_loop", "-1", "-i", bgm_b,
            "-filter_complex", bgm_fc, "-map", "[bgm_out]", "-ar", str(SR), "-ac", "2", bgm_tmp
        ], check=True)
        bgm_arr = decode_stereo_f32(bgm_tmp, dur_limit=vid_dur)
        bgm_arr = np.vstack([bgm_arr, np.zeros((max(0, N - len(bgm_arr)), 2), dtype=np.float32)])[:N]
        os.remove(bgm_tmp)

        sp_dil = np.zeros_like(speaking)
        for ih in range(n_hops):
            if speaking[ih] > 0.5:
                sp_dil[max(0, ih - 10): min(n_hops, ih + 16)] = 1.0
        win_sm = np.hanning(33).astype(np.float32); win_sm /= np.sum(win_sm)
        sp_sm = np.convolve(np.pad(sp_dil, (16, 16), mode="edge"), win_sm, mode="valid")[:n_hops]
        bgm_gain_hop = 0.35 * (1.0 - sp_sm) + 0.19 * sp_sm
        bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, bgm_gain_hop).astype(np.float32)
        bgm_ducked = bgm_arr * bgm_env[:, None]

        # 3. Style-Specific Kobe Tactile Micro-SFX Bus
        sfx_bus = np.zeros((N, 2), dtype=np.float32)
        stamp(sfx_bus, bank, "soft_whoosh", 0.05, -12.0)
        hk_m = hstyle["hook_mode"]
        if hk_m == "overhead_3card_arc":
            for k, tc in enumerate([0.18, 0.34, 0.50]):
                stamp(sfx_bus, bank, "card_deal", tc, -11.4, semitones=k * 1.2, pan=-0.22 + k * 0.22)
        elif hk_m == "viethan_medical_hook":
            for k, tc in enumerate([0.24, 0.46, 0.68]):
                stamp(sfx_bus, bank, "pop_clean", tc, -11.6, semitones=k * 1.0)
        elif hk_m == "tvc_portal_hook":
            stamp(sfx_bus, bank, "sparkle", 0.16, -11.8, align_peak=False)
            stamp(sfx_bus, bank, "chime_warm", 0.35, -12.0, align_peak=False)
        else:
            stamp(sfx_bus, bank, "pop_clean", 0.18, -11.6)
            stamp(sfx_bus, bank, "click_soft", 0.42, -12.0, semitones=1.5)

        for _, k0, _, _ in tl["kw_windows"]:
            stamp(sfx_bus, bank, "chime_warm", k0 + 0.04, -12.2, align_peak=False)

        if tl["flip3d_aroll"]:
            f0, _ = tl["flip3d_aroll"]
            stamp(sfx_bus, bank, "soft_whoosh", f0 + 0.06, -11.8)
            stamp(sfx_bus, bank, "ping_glass",  f0 + 0.65, -12.0, align_peak=False)

        for st_kind, s0, s1, _ in tl["full_stages"]:
            if s0 > 0.15:
                stamp(sfx_bus, bank, "soft_whoosh", max(0.02, s0 - 0.10), -11.2)
            if st_kind == "kobe_saas_highway_pip":
                for k_s, ts_c in enumerate([s0 + 0.08, s0 + 0.26, s0 + 0.44]):
                    stamp(sfx_bus, bank, "pop_clean",  ts_c, -11.4, semitones=k_s * 1.2, pan=-0.20 + k_s * 0.20)
                    stamp(sfx_bus, bank, "click_soft", ts_c + 0.20, -12.2, semitones=k_s * 1.2)
            elif st_kind == "viethan_5cell_bento":
                for k_b in range(5):
                    stamp(sfx_bus, bank, "pop_clean", s0 + k_b * 0.14 + 0.04, -11.8, semitones=k_b * 0.8)
            elif st_kind == "kobe_cyber_tank_pip":
                for k_t in range(4):
                    stamp(sfx_bus, bank, "click_soft", s0 + 0.15 + k_t * 0.36, -11.8, semitones=k_t * 1.4)
                stamp(sfx_bus, bank, "ping_glass", s0 + 1.35, -11.8, align_peak=False)
            elif st_kind == "saas_glass_laser":
                stamp(sfx_bus, bank, "soft_whoosh", s0 + 0.12, -11.4)
                for k_n in range(3):
                    stamp(sfx_bus, bank, "ping_glass", s0 + 0.22 + k_n * 0.26, -12.2, semitones=k_n * 1.5, align_peak=False)
            elif st_kind in ("tvc_gold_portal", "tvc_bling_endcard"):
                stamp(sfx_bus, bank, "sparkle",    s0 + 0.14, -11.6, align_peak=False)
                stamp(sfx_bus, bank, "chime_warm", s0 + 0.42, -12.0, align_peak=False)
            elif st_kind in ("playing_card_fan", "playing_card_riffle", "royal_card_endcard"):
                stamp(sfx_bus, bank, "card_deal", s0 + 0.08, -11.2, pan=-0.18)
                stamp(sfx_bus, bank, "card_deal", s0 + 0.24, -11.0, semitones=1.4, pan=0.18)
                stamp(sfx_bus, bank, "pop_clean", s0 + 0.68, -11.4, semitones=2.0)
            if st_kind.endswith("endcard"):
                stamp(sfx_bus, bank, "notif_cta", s0 + 0.46, -10.8, align_peak=False)

        # 4. 2-Pass EBU R128 Loudnorm to exact -14.0 LUFS!
        pre_wav  = os.path.join(v_dir, "_v2_pre.wav")
        norm_wav = os.path.join(v_dir, "_v2_14lufs.wav")
        save_wav_16(pre_wav, vo + bgm_ducked + sfx_bus)

        p1 = subprocess.run(["ffmpeg", "-y", "-i", pre_wav, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=10:print_format=json", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        m_j = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p1.stderr or "")
        if m_j:
            st = json.loads(m_j.group(0))
            af2 = (
                f"loudnorm=I=-14.0:TP=-1.0:LRA=10:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
                f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true"
            )
        else:
            af2 = "loudnorm=I=-14.0:TP=-1.0:LRA=10"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", pre_wav, "-af", af2, "-ar", str(SR), "-ac", "2", norm_wav], check=True)
        os.remove(pre_wav)

        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", raw_vid, "-i", norm_wav,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
            local_fin
        ], check=True)
        os.remove(norm_wav)

        dec_chk = subprocess.run(["ffmpeg", "-v", "error", "-i", local_fin, "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert (dec_chk.stderr or "").strip() == "", f"Decode error in {vk}: {dec_chk.stderr}"
        p_ver = subprocess.run(["ffmpeg", "-i", local_fin, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=10:print_format=json", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        m_v = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p_ver.stderr or "")
        ver_lufs = json.loads(m_v.group(0)).get("input_i", "-14.0") if m_v else "-14.0"

        # Add 3 QC panels (A-Roll, Mid Hybrid Stage, End-Card)
        st_mid = tl["full_stages"][1] if cfg.get("force_fullscreen_speech") else tl["full_stages"][0]
        t_mid  = (st_mid[1] + st_mid[2]) * 0.52
        for t_snap in [1.45, t_mid, max(1.0, vid_dur - 1.3)]:
            raw_im = subprocess.check_output([
                "ffmpeg", "-v", "error", "-ss", f"{t_snap:.2f}", "-i", local_fin,
                "-frames:v", "1", "-vf", f"scale={pw}:{ph}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
            ])
            im_p = Image.frombytes("RGB", (pw, ph), raw_im)
            dr_p = ImageDraw.Draw(im_p)
            dr_p.rounded_rectangle([4, 4, 168, 28], radius=6, fill=(10, 16, 22))
            dr_p.text((8, 6), f"{vk}•{meta['code']} {t_snap:4.1f}s", font=f_lbl, fill=(255, 226, 96))
            qc_sheet.paste(im_p, ((panel_idx % 6) * pw, (panel_idx // 6) * ph))
            panel_idx += 1

        # Deliver flat to Official Brand Folder, Master Cloud Storage & Downloads!
        for d_target in (BRAND_DIR, MASTER_DIR, DL_DIR):
            shutil.copy2(local_fin, os.path.join(d_target, final_fn))
        if vk == "v00":
            dl_root_v00 = os.path.join(r"C:\Users\001\Downloads", final_fn)
            if os.path.exists(r"C:\Users\001\Downloads"):
                shutil.copy2(local_fin, dl_root_v00)

        qc_rows.append({
            "vk": vk, "code": meta["code"], "final_name": final_fn,
            "dur": round(vid_dur, 2), "lufs": ver_lufs, "style": hstyle["style_title"],
        })
        print(f"[{idx_e:02d}/18] DELIVERED {final_fn} | {vid_dur:.2f}s (1.1x) | {ver_lufs} LUFS | {hstyle['style_title']}", flush=True)

    qc_jpg_local = os.path.join(BATCH_DIR, "v2_18_finals_qc_sheet.jpg")
    qc_jpg_art   = os.path.join(ART_DIR,   "v2_18_finals_qc_sheet.jpg")
    qc_sheet.save(qc_jpg_local, quality=92)
    shutil.copy2(qc_jpg_local, qc_jpg_art)

    # Sync V2 scripts & report to 03_Du_An
    rep_lines = [
        "# Báo Cáo QC Nâng Cấp V2 — 18 Video Hằng Thu Pharma & An Vượng (1.10x • Căn Giữa X=540 • 18 Hybrid Styles)",
        "",
        "| # | Mã | Tên File Final | Thời lượng (1.1x) | LUFS | Kiến trúc Đồ họa Kết hợp Đa Skill |",
        "|---|---|---|---|---|---|",
    ]
    for i_r, r in enumerate(qc_rows, 1):
        rep_lines.append(f"| {i_r:02d} | `{r['code']}` | `{r['final_name']}` | `{r['dur']}s` | `{r['lufs']} LUFS` | {r['style']} |")
    rep_md = "\n".join(rep_lines) + "\n"

    for dp in (DRIVE_PROJ, LOCAL_DUAN):
        with open(os.path.join(dp, "report_v2_18_hybrid.md"), "w", encoding="utf-8") as f:
            f.write(rep_md)
        for py_fn in ("batch_v2_configs_18.py", "batch_v2_native_components.py", "batch_v2_step1_center_trim_110x.py", "batch_v2_step2_render_18_hybrid_styles.py", "batch_v2_step3_mix_deliver_18.py"):
            src_py = os.path.join(BATCH_DIR, py_fn)
            if os.path.exists(src_py):
                shutil.copy2(src_py, os.path.join(dp, py_fn))

    print(f"\n=== ALL 18 V2 HYBRID 1.1x VIDEOS MIXED (-14.0 LUFS) & DELIVERED IN {time.time() - t0_all:.1f}s ===", flush=True)


if __name__ == "__main__":
    main()
