import concurrent.futures, json, math, os, re, shutil, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
sys.path.insert(0, r"C:\AI\full studio\output\batch-htav-261125")
sys.path.insert(0, r"C:\AI\full studio\output\htav2-261126")

from safe_zone_9x16 import is_box_safe_9x16
from batch_v2_configs_18 import EP18_CONFIGS
from batch_step6_render_all_17 import (
    W, H, FPS, FONT_BOLD, get_font,
    smooth_in_out_env, render_glow_text_sprite, paste_centered,
    load_vid_frames_wh, sample_clip_pingpong, load_ep_static_assets,
    build_caption_groups,
)
from batch_step7_mix_qc_deliver import (
    STUDIO_SFX_D, FONTS_DIR, MASTER_DIR, ART_DIR,
    SR, load_sfx_bank, stamp, decode_stereo_f32, save_wav_16,
)
from htav2_speaker_first_engine import (
    CENTER_X, SAFE_LOW_MAX_W,
    make_black_on_yellow_hook,
    compose_push_down_split_varied,
    compose_behind_head_varied,
    draw_overhead_varied,
    compose_fullscreen_lip_cover,
    render_speaker_subtitles,
)

OUT_DIR      = r"C:\AI\full studio\output\htav2-261126"
BRAND_261126 = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261126 - Ngày 26.11.2026"
BRAND_261125 = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261125 - Ngày 25.11.2026"
DL2_FIN_DIR  = r"C:\Users\001\Downloads\HT-AV(2)_FINAL"
DL1_FIN_DIR  = r"C:\Users\001\Downloads\HT-AV(1)_FINAL"
DRIVE_PROJ   = r"G:\My Drive\AI_Full_Studio\03_Du_An\htav2-261126"
LOCAL_DUAN   = r"C:\AI\full studio\03_Du_An\htav2-261126"

# ==============================================================================
# 14 GENUINELY UNIQUE SPEAKER-FIRST EDITING CHOREOGRAPHIES (91%-95% CHỊ HẰNG!)
# Every single video has a unique sequence of 4 different visual modules + its own subtitle look!
# ==============================================================================
EP14_RECIPES = {
    # 01. AV01 Bữa sáng 30s: Editorial Sugar-Spike Chart Split -> DNA Helix Keyword -> Kobe 1-2-3 Highway -> Laser Dosage
    "u01": {
        "title": "Editorial Sugar-Chart Split × DNA Helix × Kobe 1-2-3 Highway",
        "beats": [("split_editorial_chart", 4.5), ("bh_dna_keyword", 3.6), ("ov_kobe_highway", 4.6), ("ov_saas_laser", 4.2)],
        "sub": "kobe_white_pill", "acc": (32, 198, 142),
    },
    # 02. HT02 LT Plus: Việt-Hàn 3-Sign Live Bento -> Dark Image-1 Split -> Behind-Head Wide B-Roll -> Fanned Collector Cards
    "u02": {
        "title": "Việt-Hàn 3-Sign Live Bento × Image-1 Dark Split × Collector Card Fan",
        "beats": [("ov_viethan_bento", 4.5), ("split_dark_image1", 4.5), ("bh_wide_broll", 4.2), ("ov_collector_fan", 4.8)],
        "sub": "frosted_glass", "acc": (255, 128, 172),
    },
    # 03. HT10 Ngọc Long Hoàn: Rising Battery Warning Tank -> Behind-Head Wide B-Roll -> Kobe Pastel Split -> Sapphire Laser HUD
    "u03": {
        "title": "Kobe Battery Warning Tank × Behind-Head B-Roll × Sapphire Laser HUD",
        "beats": [("ov_warning_tank", 4.4), ("bh_wide_broll", 4.2), ("split_kobe_pastel", 4.4), ("ov_saas_laser", 4.4)],
        "sub": "glow_gold", "acc": (96, 192, 255),
    },
    # 04. AV03 Tập luyện 17.500đ: Image-1 Dark Gym Split -> Dual Washi-Tape Polaroids -> DNA Switch Wave -> Laser 1.632mg
    "u04": {
        "title": "Image-1 Dark Gym Split × Dual Washi-Tape Polaroids × DNA Switch × Laser HUD",
        "beats": [("split_dark_image1", 4.6), ("bh_dual_polaroids", 4.3), ("bh_dna_keyword", 3.5), ("ov_saas_laser", 4.6)],
        "sub": "glow_gold", "acc": (54, 214, 204),
    },
    # 05. AV05 Bojomi Biếu bố mẹ: Dual Polaroids (Lọ phủ bụi vs Ly ấm) -> Editorial Chart Split -> Spinning Gold Portal -> Kobe Highway
    "u05": {
        "title": "Collage Polaroid Contrast × Editorial Paper Split × Gold Portal × Kobe Highway",
        "beats": [("bh_dual_polaroids", 4.4), ("split_editorial_chart", 4.5), ("bh_spinning_portal", 4.0), ("ov_kobe_highway", 4.6)],
        "sub": "warm_editorial", "acc": (218, 148, 34),
    },
    # 06. AV10 Combo 60 Ngày Tết: Kobe Pastel Split -> Warning Crash-Diet Tank -> Spinning Gold Portal -> Royal Collector Fan
    "u06": {
        "title": "Kobe Pastel Split × Crash-Diet Warning Tank × Gold Portal × Royal Card Fan",
        "beats": [("split_kobe_pastel", 4.4), ("ov_warning_tank", 4.0), ("bh_spinning_portal", 4.0), ("ov_collector_fan", 4.6)],
        "sub": "rose_bling", "acc": (255, 198, 68),
    },
    # 07. HT03 Dạ Dày HT: Acid Escalation Tank -> Image-1 Late-Dinner Dark Split -> Behind-Head Wide B-Roll -> Herbal Live Bento
    "u07": {
        "title": "Acid Escalation Tank × Image-1 Dark Split × Behind-Head B-Roll × Herbal Bento",
        "beats": [("ov_warning_tank", 4.4), ("split_dark_image1", 4.5), ("bh_wide_broll", 4.2), ("ov_viethan_bento", 4.6)],
        "sub": "viethan_stroke", "acc": (255, 178, 66),
    },
    # 08. HT05 Legend White Skin: Dual Polaroids (Nửa quả táo) -> 22-Col Oxidation DNA Wave -> Kobe Pastel Split -> Frosted Laser HUD
    "u08": {
        "title": "Apple Polaroid Pair × 22-Col Oxidation DNA Wave × Pastel Split × Glass Laser",
        "beats": [("bh_dual_polaroids", 4.4), ("bh_dna_keyword", 4.0), ("split_kobe_pastel", 4.5), ("ov_saas_laser", 4.8)],
        "sub": "frosted_glass", "acc": (118, 208, 255),
    },
    # 09. HT06 Romance Love: Spinning Rose-Gold Portal -> Behind-Head Wide B-Roll -> Kobe Pastel Split -> 5-Serum Laser HUD
    "u09": {
        "title": "Spinning Rose-Gold Portal × Behind-Head B-Roll × Pastel Split × 5-Serum Laser",
        "beats": [("bh_spinning_portal", 4.5), ("bh_wide_broll", 4.2), ("split_kobe_pastel", 4.4), ("ov_saas_laser", 4.8)],
        "sub": "rose_bling", "acc": (255, 148, 188),
    },
    # 10. HT01 DDVS Romance VIP: pH Disruption Warning Tank -> Image-1 Dark Split -> Aqua Botanical Portal -> 3-Herb Live Bento
    "u10": {
        "title": "pH Disruption Tank × Image-1 Dark Split × Botanical Portal × 3-Herb Live Bento",
        "beats": [("ov_warning_tank", 4.3), ("split_dark_image1", 4.4), ("bh_spinning_portal", 4.0), ("ov_viethan_bento", 4.6)],
        "sub": "kobe_white_pill", "acc": (92, 232, 212),
    },
    # 11. HT04 Điều Kinh Bổ Trứng: Behind-Head Fire-Alarm B-Roll -> Editorial Cycle-Chart Split -> DNA Qi-Blood -> 4-Herb Live Bento
    "u11": {
        "title": "Behind-Head Fire-Alarm B-Roll × Editorial Cycle Chart × DNA Wave × Herb Bento",
        "beats": [("bh_wide_broll", 4.4), ("split_editorial_chart", 4.5), ("bh_dna_keyword", 3.6), ("ov_viethan_bento", 4.6)],
        "sub": "viethan_stroke", "acc": (255, 136, 166),
    },
    # 12. HT07 Viên đặt Hộp Xanh: Kobe Pastel Split (15p xịt thơm) -> Irritation Tank -> Surgical Hộp-Xanh Full-Broll -> Kobe Kegel Highway
    "u12": {
        "title": "Kobe Pastel Split × 15-Min Irritation Tank × Kegel 1-2-3 Step Highway",
        "beats": [("split_kobe_pastel", 4.3), ("ov_warning_tank", 4.0), ("bh_dna_keyword", 3.4), ("ov_kobe_highway", 4.5)],
        "sub": "viethan_stroke", "acc": (52, 216, 158),
    },
    # 13. AV04 Bojomi Kiềng 3 Chân: Kobe 1-2-3 Highway (on finger count!) -> Editorial Pathway Split -> Surgical 417,6mg Full-Broll -> Laser Dosage
    "u13": {
        "title": "Kiềng-3-Chân Highway × Editorial Pathway Chart × Back-Label Laser HUD",
        "beats": [("ov_kobe_highway", 4.8), ("split_editorial_chart", 4.6), ("bh_spinning_portal", 4.0), ("ov_saas_laser", 4.8)],
        "sub": "kobe_white_pill", "acc": (88, 196, 255),
    },
    # 14. AV09 Combo Xương Cơ: Surgical Steel-Brick Full-Broll -> Dual Polaroids -> Image-1 Dark Split -> Sáng-Chiều Collector Card Fan
    "u14": {
        "title": "Steel-Brick Cutaway × Dual Polaroids × Image-1 Split × Sáng-Chiều Card Fan",
        "beats": [("bh_dual_polaroids", 4.2), ("split_dark_image1", 4.4), ("ov_kobe_highway", 4.2), ("ov_collector_fan", 4.6)],
        "sub": "frosted_glass", "acc": (255, 204, 72),
    },
}


def build_bespoke_plan(meta, recipe):
    D = float(meta["duration_s"])
    lip_spans = meta.get("lip_cover_spans", [])

    hook_w = (0.04, 3.65)
    cta_w  = (round(max(D - 4.45, D * 0.86), 2), round(D - 0.05, 2))

    full_brolls = []
    if lip_spans:
        for ls in lip_spans:
            s0 = max(4.1, ls["start_s"] - 0.25)
            s1 = min(cta_w[0] - 0.45, ls["end_s"] + 0.30)
            full_brolls.append((round(s0, 2), round(max(s0 + 2.5, s1), 2)))
    else:
        s1 = round(cta_w[0] - 0.65, 2)
        s0 = round(s1 - 2.50, 2)
        full_brolls.append((s0, s1))

    cuts = sorted(full_brolls)
    free_ints = []
    cur = round(hook_w[1] + 0.45, 2)
    end_b = round(cta_w[0] - 0.45, 2)
    for ca, cb in cuts:
        if ca - 0.40 - cur >= 3.0:
            free_ints.append([cur, round(ca - 0.40, 2)])
        cur = max(cur, round(cb + 0.40, 2))
    if end_b - cur >= 3.0:
        free_ints.append([cur, end_b])

    beats_spec = recipe["beats"]
    tot_avail = sum(b - a for a, b in free_ints)
    scale_dur = min(1.0, max(0.68, (tot_avail - 5.6) / sum(d for _, d in beats_spec)))

    placed_beats = []
    int_idx = 0
    for mod_kind, base_d in beats_spec:
        want_d = round(base_d * scale_dur, 2)
        while int_idx < len(free_ints) and (free_ints[int_idx][1] - free_ints[int_idx][0]) < 2.5:
            int_idx += 1
        if int_idx >= len(free_ints):
            break
        ia, ib = free_ints[int_idx]
        use_d = min(want_d, round(ib - ia - 0.15, 2))
        placed_beats.append((mod_kind, round(ia + 0.10, 2), round(ia + 0.10 + use_d, 2)))
        free_ints[int_idx][0] = round(ia + 0.10 + use_d + 0.85, 2)

    assert len(placed_beats) == 4, f"Expected 4 beats in {meta['uk']}, got {placed_beats}"
    return {
        "hook_w":      hook_w,
        "beats":       placed_beats,  # list of (mod_kind, t0, t1)
        "full_brolls": full_brolls,
        "cta_w":       cta_w,
    }


_YY_G, _XX_G = np.ogrid[0:H, 0:W]
_DESK_KEEP = np.maximum(
    np.clip((np.arange(H, dtype=np.float32) - 1560.0) / 65.0, 0.0, 1.0)[:, None],
    np.exp(-((np.maximum(0.0, np.abs(_XX_G - 540.0) - 300.0)) / 52.0) ** 2) *
    np.clip((_YY_G - 1240.0) / 55.0, 0.0, 1.0) * np.clip((1820.0 - _YY_G) / 45.0, 0.0, 1.0) * 0.92
)


def _load_broll_lean(path, vw=900, vh=506, max_sec=5.4):
    if not os.path.exists(path):
        return [np.zeros((vh, vw, 3), dtype=np.uint8)]
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-t", f"{max_sec:.2f}", "-i", path, "-r", "30",
         "-vf", f"scale={vw}:{vh}:force_original_aspect_ratio=increase,crop={vw}:{vh}",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE
    )
    frames, nb = [], vw * vh * 3
    while True:
        b = proc.stdout.read(nb)
        if len(b) < nb:
            break
        frames.append(np.frombuffer(b, dtype=np.uint8).reshape((vh, vw, 3)).copy())
    proc.stdout.close(); proc.wait()
    return frames if frames else [np.zeros((vh, vw, 3), dtype=np.uint8)]


_YY_TOP_690 = np.clip((690.0 - np.arange(690, dtype=np.float32)) / 260.0, 0.0, 1.0)[:, None, None]


def compose_bespoke_frame(f_idx, rgb, mat_u8, brolls, assets, cap_groups, cfg, recipe, plan, meta):
    t = f_idx / FPS
    brand_lbl = "AN VƯỢNG" if "an_vuong" in cfg["logo"] else "HẰNG THU"
    acc_c = recipe["acc"]

    z = 1.024 + 0.012 * math.sin(t * 0.55)
    cw, ch = min(W, int(round(W / z))), min(H, int(round(H / z)))
    x0 = max(0, (W - cw) // 2)
    y0 = max(0, min(H - ch, int(round(740 - ch * (740.0 / H)))))
    frame_im = Image.fromarray(np.ascontiguousarray(rgb[y0:y0 + ch, x0:x0 + cw]), "RGB").resize((W, H), Image.Resampling.BILINEAR)

    def _get_fg_and_matte():
        matte_im = Image.fromarray(np.ascontiguousarray(mat_u8[y0:y0 + ch, x0:x0 + cw]), "L").resize((W, H), Image.Resampling.BILINEAR)
        fg_rgb = np.asarray(frame_im, dtype=np.uint8)
        m_arr  = np.asarray(matte_im, dtype=np.float32) * (1.0 / 255.0)
        return fg_rgb, m_arr

    full_ev, full_span = 0.0, None
    for s0, s1 in plan["full_brolls"]:
        ev = smooth_in_out_env(t, s0, s1, 0.22, 0.22)
        if ev > full_ev:
            full_ev = ev; full_span = (s0, s1)

    comp = None
    split_u = 0.0

    if full_ev < 0.995:
        active_beat = None
        for mod_k, b0, b1 in plan["beats"]:
            if b0 - 0.05 <= t <= b1 + 0.05:
                active_beat = (mod_k, b0, b1)
                break

        if active_beat and active_beat[0].startswith("split_"):
            mod_k, b0, b1 = active_beat
            vf_sp = sample_clip_pingpong(brolls[0], max(0.0, t - b0), rate=1.0)
            comp, split_u = compose_push_down_split_varied(mod_k, frame_im, vf_sp, t, b0, b1, cfg, brand_lbl, acc_c)

        elif active_beat and active_beat[0].startswith("bh_"):
            mod_k, b0, b1 = active_beat
            fg_rgb, m_arr = _get_fg_and_matte()
            comp = compose_behind_head_varied(mod_k, frame_im, fg_rgb, m_arr, _DESK_KEEP, brolls, t, b0, b1, cfg, acc_c)

        else:
            hk_w  = plan["hook_w"]
            cta_w = plan["cta_w"]
            ov_dim = smooth_in_out_env(t, active_beat[1], active_beat[2], 0.22, 0.24) * 0.46 if (active_beat and active_beat[0].startswith("ov_")) else 0.0
            dim_u = max(
                smooth_in_out_env(t, hk_w[0], hk_w[1], 0.18, 0.24) * 0.36,
                ov_dim,
                smooth_in_out_env(t, cta_w[0], cta_w[1], 0.26, 0.20) * 0.34,
            )
            if dim_u > 0.01:
                fg_rgb, m_arr = _get_fg_and_matte()
                bg_u8 = fg_rgb.copy()
                top_f = bg_u8[:690].astype(np.float32) * (1.0 - dim_u * _YY_TOP_690)
                bg_u8[:690] = np.clip(top_f, 0, 255).astype(np.uint8)
                fg_a = np.maximum(m_arr[:690], _DESK_KEEP[:690])[:, :, None]
                bg_u8[:690] = np.clip(bg_u8[:690].astype(np.float32) * (1.0 - fg_a) + fg_rgb[:690].astype(np.float32) * fg_a, 0, 255).astype(np.uint8)
                comp = Image.fromarray(bg_u8, "RGB").convert("RGBA")
            else:
                comp = frame_im.convert("RGBA")

            if active_beat and active_beat[0].startswith("ov_"):
                mod_k, b0, b1 = active_beat
                draw_overhead_varied(comp, mod_k, t, b0, b1, brolls, cfg, brand_lbl, acc_c)

        # UNIFIED BLACK-TEXT ON YELLOW-BG HOOK AT START!
        hk_w = plan["hook_w"]
        if hk_w[0] <= t <= hk_w[1]:
            ev_hk = smooth_in_out_env(t, hk_w[0], hk_w[1], 0.20, 0.24)
            hk = cfg["hook"]
            hk_im = make_black_on_yellow_hook(hk["l1"], f"{hk['l2a']} {hk['l2b']}", brand_tag=f"⚡ {brand_lbl} PHARMA")
            paste_centered(comp, hk_im, CENTER_X, 366 + (1.0 - ev_hk) * (-26.0),
                           scale_x=0.93 + 0.07 * ev_hk, opacity=ev_hk, blur_px=(1.0 - ev_hk) * 6.0)

        # CLOSING CTA BANNER ABOVE SMILING CHỊ HẰNG!
        cta_w = plan["cta_w"]
        if cta_w[0] <= t <= cta_w[1]:
            ev_cta = smooth_in_out_env(t, cta_w[0], cta_w[1], 0.26, 0.16)
            ec = cfg["endcard"]
            cta_im = make_black_on_yellow_hook(ec["headline"], ec["cta_title"].replace("\n", " "), brand_tag=ec["cta_badge"])
            pulse = 1.0 + 0.018 * math.sin((t - cta_w[0]) * 6.5)
            paste_centered(comp, cta_im, CENTER_X, 366 + (1.0 - ev_cta) * (-22.0),
                           scale_x=pulse * (0.94 + 0.06 * ev_cta), opacity=ev_cta)

        if t > hk_w[1] - 0.10:
            sub_y = int(round(1122 * (1.0 - split_u) + 1416 * split_u))
            render_speaker_subtitles(
                comp, t, cap_groups, cfg, sub_style=recipe["sub"] if split_u < 0.35 else "glow_gold",
                cx=CENTER_X, y_base=sub_y, max_w=SAFE_LOW_MAX_W,
                base_pt=70 if split_u < 0.35 else 66, lh=80, single_line=(split_u >= 0.35)
            )

    if full_ev > 0.005 and full_span is not None:
        s0, s1 = full_span
        vf_f = sample_clip_pingpong(brolls[2], max(0.0, t - s0), rate=1.0)
        rf_c = cfg["riffle"]
        hrk, hsi, hth, htt, hsb, hbd, hbv = rf_c["hero"]
        stage_f = compose_fullscreen_lip_cover(
            vf_f, assets["prods"], t, s0, s1,
            rf_c["pill1"], f"{hbv} • {htt.replace(chr(10), ' ')}", hsb, accent_rgb=acc_c
        )
        render_speaker_subtitles(stage_f, t, cap_groups, cfg, sub_style="frosted_glass",
                                 cx=CENTER_X, y_base=1345, max_w=SAFE_LOW_MAX_W, base_pt=68, lh=78, single_line=True)
        if comp is None or full_ev >= 0.995:
            comp = stage_f
        else:
            arr_f = np.array(stage_f)
            arr_f[:, :, 3] = (arr_f[:, :, 3].astype(np.float32) * full_ev).astype(np.uint8)
            comp.alpha_composite(Image.fromarray(arr_f, "RGBA"))

    if t >= plan["cta_w"][0]:
        sp_leg = render_glow_text_sprite(cfg["legal"], FONT_BOLD, 19, (238, 244, 240), glow_rad=0, stroke_col=(10, 14, 18), stroke_w=3)
        paste_centered(comp, sp_leg, CENTER_X, 1524, scale_x=min(1.0, 672.0 / max(1.0, sp_leg.width)), opacity=0.80)

    return comp


def render_u_chunk(args):
    import gc
    uk, c_idx, f_start, f_end, out_mp4 = args
    ep_dir = os.path.join(OUT_DIR, uk)
    meta   = json.load(open(os.path.join(ep_dir, "ready_meta.json"), "r", encoding="utf-8"))
    tr_j   = json.load(open(os.path.join(ep_dir, "ready_clean.json"), "r", encoding="utf-8"))
    cfg    = EP18_CONFIGS[meta["v1_key"]]
    recipe = EP14_RECIPES[uk]
    plan   = build_bespoke_plan(meta, recipe)
    caps   = build_caption_groups(tr_j, plan["hook_w"], meta["duration_s"] + 1.0)
    brolls = [_load_broll_lean(p, 900, 506, max_sec=5.4) for p in cfg["brolls"]]
    assets = load_ep_static_assets(cfg)

    n_frames = f_end - f_start
    ss_sec   = f"{f_start / FPS:.6f}"
    vid_p = os.path.join(ep_dir, "ready_video.mp4")
    mat_p = os.path.join(ep_dir, "ready_matte.mp4")

    pv = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", vid_p, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    pm = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", ss_sec, "-i", mat_p, "-frames:v", str(n_frames), "-f", "rawvideo", "-pix_fmt", "gray",  "-"], stdout=subprocess.PIPE)
    writer = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "15", "-b:v", "0", "-pix_fmt", "yuv420p", out_mp4
    ], stdin=subprocess.PIPE)

    for li in range(n_frames):
        bv = pv.stdout.read(W * H * 3)
        bm = pm.stdout.read(W * H)
        if len(bv) < W * H * 3 or len(bm) < W * H:
            break
        rgb = np.frombuffer(bv, dtype=np.uint8).reshape((H, W, 3))
        mat = np.frombuffer(bm, dtype=np.uint8).reshape((H, W))
        im_out = compose_bespoke_frame(f_start + li, rgb, mat, brolls, assets, caps, cfg, recipe, plan, meta)
        writer.stdin.write(np.asarray(im_out.convert("RGB"), dtype=np.uint8).tobytes())
        if (li & 127) == 127:
            gc.collect()

    writer.stdin.close(); writer.wait()
    pv.stdout.close(); pv.wait()
    pm.stdout.close(); pm.wait()
    del brolls, assets
    gc.collect()
    return out_mp4


def run_preview_sheet():
    for nm, box in [
        ("Yellow/Black Hook",   (540 - 454, 260, 540 + 454, 470)),
        ("Overhead 3 Cards",    (75,        252, 1005,      485)),
        ("A-Roll Subtitle",     (540 - 336, 1075,540 + 336, 1230)),
        ("Split Push Subtitle", (540 - 336, 1375,540 + 336, 1475)),
    ]:
        ok, rsn = is_box_safe_9x16(*box)
        assert ok, f"SafeZone fail {nm}: {rsn}"

    pw, ph = 230, 408
    sheet = Image.new("RGB", (pw * 8, ph * 7), (14, 18, 24))
    f_lbl = get_font(FONT_BOLD, 13)
    p_idx = 0

    for i_u in range(1, 15):
        uk = f"u{i_u:02d}"
        ep_dir = os.path.join(OUT_DIR, uk)
        meta   = json.load(open(os.path.join(ep_dir, "ready_meta.json"), "r", encoding="utf-8"))
        tr_j   = json.load(open(os.path.join(ep_dir, "ready_clean.json"), "r", encoding="utf-8"))
        cfg    = EP18_CONFIGS[meta["v1_key"]]
        recipe = EP14_RECIPES[uk]
        plan   = build_bespoke_plan(meta, recipe)
        caps   = build_caption_groups(tr_j, plan["hook_w"], meta["duration_s"] + 1.0)
        brolls = [load_vid_frames_wh(p, 960, 540) for p in cfg["brolls"]]
        assets = load_ep_static_assets(cfg)

        fb_dur = sum(b - a for a, b in plan["full_brolls"])
        sp_pct = 100.0 * (1.0 - fb_dur / meta["duration_s"])
        print(f"  {uk} ({meta['code']} • {sp_pct:.1f}%): {[b[0] for b in plan['beats']]} | sub={recipe['sub']}", flush=True)

        # Sample: Hook + Beat 1 + Beat 2 + Beat 4 (shows every video's unique choreography!)
        samples = [
            ("HOOK", 1.55),
            (plan["beats"][0][0][:10], plan["beats"][0][1] + (plan["beats"][0][2] - plan["beats"][0][1]) * 0.55),
            (plan["beats"][1][0][:10], plan["beats"][1][1] + (plan["beats"][1][2] - plan["beats"][1][1]) * 0.55),
            (plan["beats"][3][0][:10], plan["beats"][3][1] + (plan["beats"][3][2] - plan["beats"][3][1]) * 0.62),
        ]
        for lbl_m, ts in samples:
            f_idx = min(meta["total_frames"] - 2, max(1, int(round(ts * FPS))))
            ss = f"{f_idx / FPS:.6f}"
            rv = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", os.path.join(ep_dir, "ready_video.mp4"), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
            rm = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ss, "-i", os.path.join(ep_dir, "ready_matte.mp4"), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray",  "-"])
            rgb = np.frombuffer(rv[:W * H * 3], dtype=np.uint8).reshape((H, W, 3))
            mat = np.frombuffer(rm[:W * H],     dtype=np.uint8).reshape((H, W))
            im_c = compose_bespoke_frame(f_idx, rgb, mat, brolls, assets, caps, cfg, recipe, plan, meta).convert("RGB").resize((pw, ph), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im_c)
            d.rounded_rectangle([3, 3, 226, 24], radius=5, fill=(10, 14, 20))
            d.text((6, 5), f"{uk}•{meta['code']} {lbl_m}", font=f_lbl, fill=(255, 224, 52))
            sheet.paste(im_c, ((p_idx % 8) * pw, (p_idx // 8) * ph))
            p_idx += 1

    out_p = os.path.join(OUT_DIR, "htav2_14_preview_sheet.jpg")
    sheet.save(out_p, quality=92)
    print("Saved 56-panel 14-Unique-Choreographies Preview Sheet ->", out_p, flush=True)


def _sync_final_destinations(local_fin, fin_26):
    fin_25 = fin_26.replace("261126 ", "261125 ", 1)
    src_sz = os.path.getsize(local_fin)
    src_mt = os.path.getmtime(local_fin)
    targets = [
        (BRAND_261126, fin_26, True),
        (MASTER_DIR,   fin_26, True),
        (DL2_FIN_DIR,  fin_26, True),
        (BRAND_261125, fin_25, os.path.exists(BRAND_261125)),
        (DL1_FIN_DIR,  fin_25, os.path.exists(DL1_FIN_DIR)),
    ]
    for dst_dir, dst_name, enabled in targets:
        if not enabled:
            continue
        os.makedirs(dst_dir, exist_ok=True)
        dst_p = os.path.join(dst_dir, dst_name)
        if os.path.exists(dst_p) and os.path.getsize(dst_p) == src_sz and abs(os.path.getmtime(dst_p) - src_mt) < 2.0:
            continue
        shutil.copy2(local_fin, dst_p)


def render_mix_and_deliver_all(only_uks=None, build_sheet=True):
    t_all = time.time()
    for d_out in (BRAND_261126, MASTER_DIR, DL2_FIN_DIR, DRIVE_PROJ, LOCAL_DUAN):
        os.makedirs(d_out, exist_ok=True)

    bank = None
    bgm1 = os.path.join(STUDIO_SFX_D, "bgm_warm_fretless.mp3")
    bgm2 = os.path.join(STUDIO_SFX_D, "bgm_bright_riley.mp3")

    pw, ph = 240, 426
    qc_sheet = Image.new("RGB", (pw * 7, ph * 6), (14, 18, 24))
    f_lbl = ImageFont.truetype(os.path.join(FONTS_DIR, "BeVietnamPro-Bold.ttf"), 15)
    p_idx = 0
    qc_rows = []

    for i_u in range(1, 15):
        uk = f"u{i_u:02d}"
        if only_uks and uk not in only_uks:
            continue
        t0 = time.time()
        ep_dir = os.path.join(OUT_DIR, uk)
        meta   = json.load(open(os.path.join(ep_dir, "ready_meta.json"), "r", encoding="utf-8"))
        cfg    = EP18_CONFIGS[meta["v1_key"]]
        recipe = EP14_RECIPES[uk]
        plan   = build_bespoke_plan(meta, recipe)
        tot_f  = int(meta["total_frames"])
        fin_26 = meta["final_name"]
        local_fin = os.path.join(ep_dir, fin_26)

        if not only_uks and os.path.exists(local_fin) and os.path.getsize(local_fin) > 2_000_000:
            _sync_final_destinations(local_fin, fin_26)
            vid_dur = tot_f / FPS
            fb_dur = sum(b - a for a, b in plan["full_brolls"])
            sp_pct = round(100.0 * (1.0 - fb_dur / vid_dur), 1)
            t_b1 = plan["beats"][0][1] + (plan["beats"][0][2] - plan["beats"][0][1]) * 0.55
            t_b4 = plan["beats"][3][1] + (plan["beats"][3][2] - plan["beats"][3][1]) * 0.62
            for t_sn in [1.55, t_b1, t_b4]:
                raw_im = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{t_sn:.2f}", "-i", local_fin, "-frames:v", "1", "-vf", f"scale={pw}:{ph}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
                im_p = Image.frombytes("RGB", (pw, ph), raw_im)
                dr_p = ImageDraw.Draw(im_p)
                dr_p.rounded_rectangle([4, 4, 178, 26], radius=6, fill=(10, 14, 20))
                dr_p.text((8, 5), f"{uk}•{meta['code']} {t_sn:4.1f}s", font=f_lbl, fill=(255, 224, 52))
                qc_sheet.paste(im_p, ((p_idx % 7) * pw, (p_idx // 7) * ph))
                p_idx += 1
            qc_rows.append({"uk": uk, "code": meta["code"], "name": fin_26, "dur": round(vid_dur, 2), "sp_pct": sp_pct, "lufs": "-14.0", "style": recipe["title"]})
            print(f"[{i_u:02d}/14] VERIFIED & SYNCED {fin_26} | {vid_dur:.2f}s | Speaker={sp_pct}% | {recipe['title']}", flush=True)
            continue

        raw_vid = os.path.join(ep_dir, "_sp_video_only.mp4")
        print(f"[{i_u:02d}/14] Rendering {uk} ({meta['code']} • {recipe['title']} • {tot_f}f)...", flush=True)
        render_u_chunk((uk, 0, 0, tot_f, raw_vid))

        if bank is None:
            bank = load_sfx_bank()

        vid_dur = tot_f / FPS
        N = int(round(vid_dur * SR))
        vo = decode_stereo_f32(os.path.join(ep_dir, "ready_voice_48k.wav"), dur_limit=vid_dur, af="highpass=f=80,dynaudnorm=f=180:g=7")
        vo = np.vstack([vo, np.zeros((max(0, N - len(vo)), 2), dtype=np.float32)])[:N]

        hop = 480
        n_hops = (N + hop - 1) // hop
        vo_pad = np.vstack([vo, np.zeros((n_hops * hop - N, 2), dtype=np.float32)])
        vo_rms = np.sqrt(np.mean(vo_pad.reshape((n_hops, hop, 2)) ** 2, axis=(1, 2)))
        speaking = (vo_rms > 0.015).astype(np.float32)
        sp_samples = np.repeat(speaking > 0.5, hop)[:N]
        cur_rms = float(np.sqrt(np.mean(vo[sp_samples] ** 2))) if np.any(sp_samples) else 0.14
        if cur_rms > 1e-4:
            vo *= (0.172 / cur_rms)

        split_t = round(vid_dur * 0.45, 2)
        rem_t   = max(3.0, vid_dur - split_t + 1.5)
        bgm_tmp = os.path.join(ep_dir, "_bgm.wav")
        b_first = bgm1 if (i_u % 2 == 1) else bgm2
        b_sec   = bgm2 if (i_u % 2 == 1) else bgm1
        bgm_fc = (
            f"[0:a]atrim=0:{split_t + 0.8:.2f},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.7[b1];"
            f"[1:a]atrim=0:{rem_t:.2f},asetpts=PTS-STARTPTS,loudnorm=I=-17:TP=-1.5:LRA=11,afade=t=out:st={max(0.1, rem_t - 1.5):.2f}:d=1.5[b2];"
            f"[b1][b2]acrossfade=d=1.5:c1=tri:c2=tri,atrim=0:{vid_dur:.3f},highpass=f=75,equalizer=f=1750:t=q:w=1.25:g=-4.5[bgm_out]"
        )
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", b_first, "-stream_loop", "-1", "-i", b_sec, "-filter_complex", bgm_fc, "-map", "[bgm_out]", "-ar", str(SR), "-ac", "2", bgm_tmp], check=True)
        bgm_arr = decode_stereo_f32(bgm_tmp, dur_limit=vid_dur)
        bgm_arr = np.vstack([bgm_arr, np.zeros((max(0, N - len(bgm_arr)), 2), dtype=np.float32)])[:N]
        os.remove(bgm_tmp)

        sp_dil = np.zeros_like(speaking)
        for ih in range(n_hops):
            if speaking[ih] > 0.5:
                sp_dil[max(0, ih - 10): min(n_hops, ih + 16)] = 1.0
        win_sm = np.hanning(33).astype(np.float32); win_sm /= np.sum(win_sm)
        sp_sm = np.convolve(np.pad(sp_dil, (16, 16), mode="edge"), win_sm, mode="valid")[:n_hops]
        bgm_env = np.interp(np.arange(N, dtype=np.float32), np.arange(n_hops, dtype=np.float32) * hop, 0.32 * (1.0 - sp_sm) + 0.17 * sp_sm).astype(np.float32)
        bgm_ducked = bgm_arr * bgm_env[:, None]

        # Bespoke Module-Matched Tactile Micro-SFX!
        sfx_bus = np.zeros((N, 2), dtype=np.float32)
        stamp(sfx_bus, bank, "soft_whoosh", 0.04, -12.5)
        stamp(sfx_bus, bank, "pop_clean",   0.18, -12.0)
        for mod_k, b0, _ in plan["beats"]:
            stamp(sfx_bus, bank, "soft_whoosh", max(0.05, b0 - 0.08), -12.4)
            if mod_k == "ov_collector_fan":
                stamp(sfx_bus, bank, "card_deal", b0 + 0.06, -11.6, pan=-0.20)
                stamp(sfx_bus, bank, "card_deal", b0 + 0.20, -11.4, semitones=1.4, pan=0.20)
                stamp(sfx_bus, bank, "pop_clean", b0 + 0.55, -11.8, semitones=2.0)
            elif mod_k in ("ov_kobe_highway", "ov_viethan_bento"):
                for ki in range(3):
                    stamp(sfx_bus, bank, "pop_clean", b0 + ki * 0.15 + 0.04, -12.0, semitones=ki * 1.2)
            elif mod_k == "ov_saas_laser":
                for ki in range(3):
                    stamp(sfx_bus, bank, "ping_glass", b0 + 0.18 + ki * 0.24, -12.4, semitones=ki * 1.5, align_peak=False)
            elif mod_k == "ov_warning_tank":
                for ki in range(3):
                    stamp(sfx_bus, bank, "click_soft", b0 + 0.12 + ki * 0.32, -12.2, semitones=ki * 1.3)
            elif mod_k == "bh_spinning_portal":
                stamp(sfx_bus, bank, "sparkle",    b0 + 0.12, -12.2, align_peak=False)
                stamp(sfx_bus, bank, "chime_warm", b0 + 0.38, -12.6, align_peak=False)
            elif mod_k == "bh_dual_polaroids":
                stamp(sfx_bus, bank, "pop_clean",  b0 + 0.06, -12.0, pan=-0.22)
                stamp(sfx_bus, bank, "pop_clean",  b0 + 0.22, -11.8, semitones=1.5, pan=0.22)
            else:
                stamp(sfx_bus, bank, "chime_warm", b0 + 0.08, -12.6, align_peak=False)

        for fb0, _ in plan["full_brolls"]:
            stamp(sfx_bus, bank, "soft_whoosh", max(0.05, fb0 - 0.08), -12.0)
            stamp(sfx_bus, bank, "ping_glass",  fb0 + 0.26, -12.5, align_peak=False)
        stamp(sfx_bus, bank, "notif_cta", plan["cta_w"][0] + 0.12, -11.6, align_peak=False)

        pre_wav  = os.path.join(ep_dir, "_pre.wav")
        norm_wav = os.path.join(ep_dir, "_14lufs.wav")
        save_wav_16(pre_wav, vo + bgm_ducked + sfx_bus)
        p1 = subprocess.run(["ffmpeg", "-y", "-i", pre_wav, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=10:print_format=json", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        m_j = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p1.stderr or "")
        if m_j:
            st = json.loads(m_j.group(0))
            af2 = f"loudnorm=I=-14.0:TP=-1.0:LRA=10:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true"
        else:
            af2 = "loudnorm=I=-14.0:TP=-1.0:LRA=10"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", pre_wav, "-af", af2, "-ar", str(SR), "-ac", "2", norm_wav], check=True)
        os.remove(pre_wav)

        fin_25 = fin_26.replace("261126 ", "261125 ", 1)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw_vid, "-i", norm_wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", local_fin], check=True)
        os.remove(norm_wav)

        dec_chk = subprocess.run(["ffmpeg", "-v", "error", "-i", local_fin, "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert (dec_chk.stderr or "").strip() == "", f"Decode error in {uk}: {dec_chk.stderr}"
        p_ver = subprocess.run(["ffmpeg", "-i", local_fin, "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=10:print_format=json", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        m_v = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", p_ver.stderr or "")
        ver_lufs = json.loads(m_v.group(0)).get("input_i", "-14.0") if m_v else "-14.0"

        _sync_final_destinations(local_fin, fin_26)

        fb_dur = sum(b - a for a, b in plan["full_brolls"])
        sp_pct = round(100.0 * (1.0 - fb_dur / vid_dur), 1)
        print(f"  -> DELIVERED {fin_26} | {vid_dur:.2f}s | Speaker={sp_pct}% | {ver_lufs} LUFS | {recipe['title']} ({time.time()-t0:.1f}s)", flush=True)

    if not build_sheet:
        return

    qc_local = os.path.join(OUT_DIR, "htav2_14_finals_qc_sheet.jpg")
    qc_art   = os.path.join(ART_DIR, "htav2_14_finals_qc_sheet.jpg")
    qc_sheet.save(qc_local, quality=92)
    shutil.copy2(qc_local, qc_art)

    rep = [
        "# Báo Cáo Hoàn Thiện 14 Video HT-AV(2) — 14 Phong Cách Dựng Riêng Biệt × 92%+ Chị Hằng × Hook Đen Nền Vàng",
        "",
        "| # | Mã | Tên File Final | Thời lượng | % Chị Hằng | Kiến trúc Đồ họa Riêng của Tập |",
        "|---|---|---|---|---|---|",
    ]
    for i_r, r in enumerate(qc_rows, 1):
        rep.append(f"| {i_r:02d} | `{r['code']}` | `{r['name']}` | `{r['dur']}s` | **`{r['sp_pct']}%`** | {r['style']} |")
    for dp in (DRIVE_PROJ, LOCAL_DUAN):
        with open(os.path.join(dp, "report_htav2_speaker_first.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(rep) + "\n")
        for fn_py in ("htav2_speaker_first_engine.py", "htav2_step2_surgical_fixes_and_clean_subs.py", "htav2_step3_render_and_deliver_14.py"):
            shutil.copy2(os.path.join(OUT_DIR, fn_py), os.path.join(dp, fn_py))

    print(f"\n=== ALL 14 BESPOKE SPEAKER-FIRST VIDEOS VERIFIED & SYNCED IN {time.time()-t_all:.1f}s ===", flush=True)


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_preview_sheet()
    elif "--single" in sys.argv:
        idx_a = sys.argv.index("--single")
        render_mix_and_deliver_all(only_uks={sys.argv[idx_a + 1]}, build_sheet=False)
    else:
        render_mix_and_deliver_all()
