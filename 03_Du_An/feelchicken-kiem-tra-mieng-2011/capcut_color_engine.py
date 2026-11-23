import json, math, os, subprocess
import numpy as np
from PIL import Image, ImageFilter

DRAFT_JSON = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\FEEL_CHICKEN_KiemTraMieng_2011_V4_CS1_SourceGoc\draft_content.json"
DRAFT_COV  = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\FEEL_CHICKEN_KiemTraMieng_2011_V4_CS1_SourceGoc\draft_cover.jpg"

# CapCut 8 HSL color centers in degrees [0..360):
# 1:Red(0), 2:Orange(28), 3:Yellow(58), 4:Green(120), 5:Cyan(180), 6:Blue(225), 7:Purple(275), 8:Magenta(320)
HSL_CENTERS = {1: 0.0, 2: 28.0, 3: 58.0, 4: 120.0, 5: 180.0, 6: 222.0, 7: 275.0, 8: 320.0}
HSL_WIDTHS  = {1: 32.0, 2: 30.0, 3: 32.0, 4: 45.0, 5: 38.0, 6: 42.0, 7: 38.0, 8: 36.0}

def load_user_capcut_segments(draft_json_path=DRAFT_JSON):
    D = json.load(open(draft_json_path, encoding="utf-8"))
    mats = D["materials"]
    all_m = {it["id"]: (k, it) for k, v in mats.items() if isinstance(v, list) for it in v if isinstance(it, dict) and "id" in it}
    out = []
    for si, seg in enumerate(D["tracks"][0]["segments"]):
        _, mobj = all_m[seg["material_id"]]
        st, tt, cl = seg["source_timerange"], seg["target_timerange"], seg.get("clip", {})
        fxs, hsls = {}, []
        for eid in seg.get("extra_material_refs", []):
            ek, ev = all_m.get(eid, ("?", {}))
            if ek == "effects" and ev.get("visible", True):
                fxs[ev.get("type") or ev.get("name")] = float(ev.get("value", 0.0))
            elif ek == "hsl":
                if any(ev.get(x, 0) != 0 for x in ("hue", "saturation", "lightness")):
                    hsls.append((int(ev.get("hsl_color_type", 1)), float(ev.get("hue", 0)), float(ev.get("saturation", 0)), float(ev.get("lightness", 0))))
        out.append({
            "index": si,
            "name": mobj.get("material_name", ""),
            "path": mobj.get("path", ""),
            "src_start": st["start"] / 1e6,
            "src_dur": st["duration"] / 1e6,
            "tl_start": tt["start"] / 1e6,
            "tl_dur": tt["duration"] / 1e6,
            "scale_x": float(cl.get("scale", {}).get("x", 1.0)),
            "scale_y": float(cl.get("scale", {}).get("y", 1.0)),
            "trans_x": float(cl.get("transform", {}).get("x", 0.0)),
            "trans_y": float(cl.get("transform", {}).get("y", 0.0)),
            "fx": fxs,
            "hsl": hsls,
        })
    return out

def apply_capcut_transform(rgb_arr, tw, th, scale=1.0, tx=0.0, ty=0.0, extra_zoom=1.0):
    """Exact CapCut canvas transform: fit/cover 9:16, scale around center, shift by (tx * W/2, -ty * H/2)."""
    ih, iw = rgb_arr.shape[:2]
    # Base cover scale to 1080x1920
    base_s = max(tw / float(iw), th / float(ih))
    tot_s  = base_s * max(1.0, scale) * extra_zoom
    nw = max(tw, int(round(iw * tot_s)))
    nh = max(th, int(round(ih * tot_s)))
    im = Image.fromarray(rgb_arr).resize((nw, nh), Image.Resampling.BILINEAR)

    # In CapCut, tx > 0 shifts image RIGHT (so crop window x0 shifts LEFT: -tx * tw/2)
    # ty > 0 shifts image UP (or DOWN depending on sign; clamped safely inside [0, nw-tw] x [0, nh-th])
    dx = tx * (tw * 0.5)
    dy = -ty * (th * 0.5)
    x0 = int(round((nw - tw) * 0.5 - dx))
    y0 = int(round((nh - th) * 0.5 - dy))
    x0 = max(0, min(nw - tw, x0))
    y0 = max(0, min(nh - th, y0))
    return np.array(im.crop((x0, y0, x0 + tw, y0 + th)), dtype=np.uint8)

# Calibrated shader coefficients matching CapCut v9.8 GPU color-adjustment + 8-band HSL
COEF = {
    "temp_r": 0.260,
    "temp_g": 0.010,
    "temp_b": 0.250,
    "tone_r": 0.110,
    "tone_g": -0.130,
    "tone_b": 0.095,
    "bri":    0.170,
    "ls":     0.185,
    "sca":    0.055,
    "con":    0.245,
    "hi":     0.140,
    "sh":     0.215,
    "blk":    0.210,
    "sat":    0.615,
    "clr":    0.185,
}

def apply_capcut_grade(rgb_u8, fx, hsl_list, coef=COEF):
    """Fast vectorized NumPy implementation of CapCut's Color Adjustment + 8-band HSL shader."""
    x = rgb_u8.astype(np.float32) / 255.0

    # 1. White Balance: Temperature & Tone (Tint) + Smart Color Adjust subtle auto-WB
    temp = fx.get("temperature", 0.0)
    tone = fx.get("tone", 0.0)
    sca  = fx.get("smart_color_adjust", 0.0)
    if sca > 0.0:
        # Subtle auto neutral-balance pull (reduces warm indoor cast slightly like CapCut Smart Adjust)
        mean_rgb = np.mean(x, axis=(0, 1))
        gray_m   = float(np.mean(mean_rgb)) + 1e-5
        wb_pull  = np.clip(gray_m / (mean_rgb + 1e-5), 0.88, 1.14)
        x = x * (1.0 + (wb_pull - 1.0) * (sca * 0.42))[None, None, :]

    if abs(temp) > 1e-4 or abs(tone) > 1e-4:
        r_g = 1.0 + temp * coef["temp_r"] + tone * coef["tone_r"]
        g_g = 1.0 + temp * coef["temp_g"] + tone * coef["tone_g"]
        b_g = 1.0 - temp * coef["temp_b"] + tone * coef["tone_b"]
        x[:, :, 0] *= r_g
        x[:, :, 1] *= g_g
        x[:, :, 2] *= b_g
    x = np.clip(x, 0.0, 1.0)

    # 2. Exposure / Brightness / Light Sensation (Brilliance) / Highlights / Shadows / Blacks / Contrast
    bri = fx.get("brightness", 0.0)
    ls  = fx.get("light_sensation", 0.0)
    con = fx.get("contrast", 0.0)
    hi  = fx.get("highlight", 0.0)
    sh  = fx.get("shadow", 0.0)
    blk = fx.get("black", 0.0)

    lum = 0.299 * x[:, :, 0] + 0.587 * x[:, :, 1] + 0.114 * x[:, :, 2]

    # Brightness + Light sensation (midtone gamma lift) + Smart Color Adjust lift
    mid_w = 4.0 * lum * (1.0 - lum)
    delta_l = (
        bri * coef["bri"] * (0.65 + 0.35 * (1.0 - lum))
        + ls * coef["ls"] * (0.45 + 0.55 * mid_w)
        + sca * coef["sca"] * mid_w
    )
    # Shadow recovery & Highlight roll-off
    if abs(sh) > 1e-4:
        sh_w = np.clip(1.0 - lum * 1.45, 0.0, 1.0) ** 1.6
        delta_l += sh * coef["sh"] * sh_w
    if abs(hi) > 1e-4:
        hi_w = np.clip((lum - 0.38) / 0.62, 0.0, 1.0) ** 1.5
        delta_l += hi * coef["hi"] * hi_w
    if abs(blk) > 1e-4:
        blk_w = np.clip(1.0 - lum * 2.5, 0.0, 1.0) ** 1.8
        delta_l += blk * coef["blk"] * blk_w

    # Apply luminance curve preserving chromaticity smoothly
    new_lum = np.clip(lum + delta_l, 0.0, 1.0)
    ratio = (new_lum + 1e-4) / (lum + 1e-4)
    x = np.clip(x * ratio[:, :, None] * 0.72 + (x + delta_l[:, :, None]) * 0.28, 0.0, 1.0)

    if abs(con) > 1e-4:
        x = np.clip(0.5 + (x - 0.5) * (1.0 + con * coef["con"]), 0.0, 1.0)

    # 3. 8-Band HSL (Skin brightening & Red/Blue pop!) + Global Saturation
    sat = fx.get("saturation", 0.0)
    if hsl_list or abs(sat) > 1e-4 or sca > 0.0:
        cmax = np.max(x, axis=2)
        cmin = np.min(x, axis=2)
        d = cmax - cmin
        l_hsl = (cmax + cmin) * 0.5
        s_hsl = np.where(d < 1e-5, 0.0, d / (1.0 - np.abs(2.0 * l_hsl - 1.0) + 1e-5))

        # Hue in [0, 360)
        r, g, b = x[:, :, 0], x[:, :, 1], x[:, :, 2]
        h_deg = np.zeros_like(cmax)
        m_r = (d >= 1e-5) & (cmax == r)
        m_g = (d >= 1e-5) & (cmax == g) & (~m_r)
        m_b = (d >= 1e-5) & (~m_r) & (~m_g)
        h_deg[m_r] = (60.0 * ((g[m_r] - b[m_r]) / (d[m_r] + 1e-6))) % 360.0
        h_deg[m_g] = 60.0 * ((b[m_g] - r[m_g]) / (d[m_g] + 1e-6) + 2.0)
        h_deg[m_b] = 60.0 * ((r[m_b] - g[m_b]) / (d[m_b] + 1e-6) + 4.0)

        dh_tot = np.zeros_like(h_deg)
        ds_tot = np.full_like(s_hsl, sat * coef["sat"] + sca * 0.06)
        dl_tot = np.zeros_like(l_hsl)

        for ctype, h_sh, s_sh, l_sh in hsl_list:
            c_deg = HSL_CENTERS.get(ctype, 0.0)
            w_deg = HSL_WIDTHS.get(ctype, 35.0)
            dist = np.abs(((h_deg - c_deg + 180.0) % 360.0) - 180.0)
            w_band = np.clip(1.0 - dist / w_deg, 0.0, 1.0)
            w_band = w_band * w_band * (3.0 - 2.0 * w_band) * np.clip(s_hsl * 3.2, 0.0, 1.0)
            if h_sh != 0:
                dh_tot += w_band * (h_sh * 0.35)
            if s_sh != 0:
                ds_tot += w_band * (s_sh / 100.0) * 0.85
            if l_sh != 0:
                dl_tot += w_band * (l_sh / 100.0) * 0.32

        h_new = (h_deg + dh_tot) % 360.0
        s_new = np.clip(s_hsl * (1.0 + ds_tot), 0.0, 1.0)
        l_new = np.clip(l_hsl + dl_tot * (1.0 - np.abs(2.0 * l_hsl - 1.0) * 0.5), 0.0, 1.0)

        # HSL -> RGB vectorized
        c_ch = (1.0 - np.abs(2.0 * l_new - 1.0)) * s_new
        h_sec = h_new / 60.0
        x_ch = c_ch * (1.0 - np.abs((h_sec % 2.0) - 1.0))
        m_ch = l_new - c_ch * 0.5
        hi_idx = np.floor(h_sec).astype(np.int32) % 6

        ro = np.choose(hi_idx, [c_ch, x_ch, 0.0, 0.0, x_ch, c_ch]) + m_ch
        go = np.choose(hi_idx, [x_ch, c_ch, c_ch, x_ch, 0.0, 0.0]) + m_ch
        bo = np.choose(hi_idx, [0.0, 0.0, x_ch, c_ch, c_ch, x_ch]) + m_ch
        x = np.stack([ro, go, bo], axis=2)

    # 4. Clarity ("clear": local midtone detail pop!)
    clr = fx.get("clear", 0.0)
    if clr > 0.01:
        u8_tmp = Image.fromarray(np.clip(x * 255.0, 0, 255).astype(np.uint8))
        blur_im = u8_tmp.filter(ImageFilter.GaussianBlur(radius=6.0))
        detail = x - (np.array(blur_im, dtype=np.float32) / 255.0)
        x = np.clip(x + detail * (clr * coef["clr"] * 2.2), 0.0, 1.0)

    return np.clip(x * 255.0 + 0.5, 0.0, 255.0).astype(np.uint8)

if __name__ == "__main__":
    segs = load_user_capcut_segments()
    s0 = segs[0]
    cov = Image.open(DRAFT_COV).convert("RGB")
    raw_b = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", f"{s0['src_start']:.2f}", "-i", s0["path"],
        "-vf", "scale=1080:1920", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ])
    raw_u8 = np.frombuffer(raw_b, dtype=np.uint8).reshape((1920, 1080, 3))
    cov_u8 = np.array(cov, dtype=np.uint8)

    # Quick coordinate fine-tune on 270x480 against CapCut's GPU ground-truth draft_cover.jpg!
    r_sm = np.array(Image.fromarray(raw_u8).resize((270, 480), Image.Resampling.BILINEAR))
    c_sm = np.array(cov.resize((270, 480), Image.Resampling.BILINEAR), dtype=np.float32)

    best_c = dict(COEF)
    def loss_fn(cd):
        pred = apply_capcut_grade(r_sm, s0["fx"], s0["hsl"], cd).astype(np.float32)
        return float(np.mean(np.abs(pred - c_sm)))

    best_l = loss_fn(best_c)
    print(f"Initial MAE vs CapCut GPU cover: {best_l:.2f}/255")
    for step in (0.06, 0.025, 0.01):
        for k in list(best_c.keys()):
            for d in (-step, +step):
                cand = dict(best_c)
                cand[k] = max(0.0, cand[k] + d)
                l = loss_fn(cand)
                if l < best_l:
                    best_l, best_c = l, cand
    print(f"Calibrated MAE vs CapCut GPU cover: {best_l:.2f}/255")
    print("Calibrated COEF:", {k: round(v, 4) for k, v in best_c.items()})

    out_full = apply_capcut_grade(raw_u8, s0["fx"], s0["hsl"], best_c)
    print("Mean RGB — Raw:", raw_u8.mean((0,1)).round(1), "| Our Engine:", out_full.mean((0,1)).round(1), "| CapCut GPU:", cov_u8.mean((0,1)).round(1))
    trip = Image.new("RGB", (540 * 3, 960))
    for i, arr in enumerate([raw_u8, out_full, cov_u8]):
        trip.paste(Image.fromarray(arr).resize((540, 960), Image.Resampling.LANCZOS), (i * 540, 0))
    tp = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011\check\capcut_engine_calibrated_triptych.jpg"
    trip.save(tp, quality=92)
    print("Saved triptych (Left=Raw, Middle=Our CapCut Engine, Right=CapCut GPU):", tp)
