import copy, json, math, os, shutil, subprocess, sys, time, uuid
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT        = Path(r"d:\AI\full studio\output\f20-set-qua-2011")
V5         = OUT / "v5_master"
V7         = OUT / "v7_master"
CLIPS_V7   = V7 / "clips_v7"
TYPOS_V7   = V7 / "typos_v7"
BAK_DIR    = OUT / "capcut_backup"
DRAFTS_DIR = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
RAW_SONY_D = Path(r"Z:\Máy tính khác\My Computer\F20\video gốc\261116\Chi Oanh\dọc")

W, H, FPS = 1080, 1920, 30
DRAFT_RAW_NAME = "F20_SetQua_2011_SourceGoc"

TL_V5 = json.loads((V5 / "timeline_v5_master.json").read_text(encoding="utf-8"))
BMAP  = {b["id"]: b for b in TL_V5["blocks"]}
def bt(bid): return float(BMAP[bid]["start"]), float(BMAP[bid]["end"])

b01_s, b01_e   = bt("b01_open_live")
b02_s, b02_e   = bt("b02_nhatrang_real")
b03_s, b03_e   = bt("b03_ship_104_clean")
b04_s, b04_e   = bt("b04_wide_oanh_104_live")
b05_s, b05_e   = bt("b05_intro_set_live")
b06_s, b06_e   = bt("b06_4items_real_tight")
b07a_s, b07a_e = bt("b07a_yen_giatri_real")
b07b_s, b07b_e = bt("b07b_camnang_live")
b08_s, b08_e   = bt("b08_chungyen_clean")
b09a_s, b09a_e = bt("b09a_giomica_real")
b09b_s, b09b_e = bt("b09b_quai_da_live")
b09c_s, b09c_e = bt("b09c_hoa_no_real")
b10a_s, b10a_e = bt("b10a_sx_live")
b10b_s, b10b_e = bt("b10b_sx_yentam_real")
b11a_s, b11a_e = bt("b11a_cta_live1")
b11b_s, b11b_e = bt("b11b_cta_2011_real")
b11c_s, b11c_e = bt("b11c_cta_inbox_live")
tot_end        = float(TL_V5["total_dur"])

t_24thanh_s = round(b06_e - 5.12, 4)

# ==============================================================================
# 1. V7 MASTER SHOT SCHEDULE
#    - 100% De-Oranged Calm Commercial Color (Zero Glare, Natural Saturation!)
#    - 100% Error-Free Muse Studio Product Shots at Steady 1.00x (ZERO ZOOM!)
# ==============================================================================
SHOTS = [
    {"t0": 0.00,   "t1": 1.30,   "src": CLIPS_V7 / "br_intro1_sunlit_sets.mp4", "ss": 0.0},
    {"t0": 1.30,   "t1": 2.60,   "src": CLIPS_V7 / "br_intro2_long_table.mp4",  "ss": 0.0},
    {"t0": 2.60,   "t1": b01_s,  "src": CLIPS_V7 / "br_intro3_shelf_tower.mp4", "ss": 0.0},

    {"t0": b01_s,  "t1": b01_e,  "src": CLIPS_V7 / "b01_open_live.mp4",         "ss": 0.0},

    {"t0": b02_s,        "t1": b02_s + 2.75, "src": CLIPS_V7 / "br_anh_hau_handover.mp4", "ss": 0.0},
    {"t0": b02_s + 2.75, "t1": b02_s + 6.55, "src": CLIPS_V7 / "br_anh_hau_77sets.mp4",   "ss": 0.0},
    {"t0": b02_s + 6.55, "t1": b02_e,        "src": CLIPS_V7 / "br_phu_huynh_13sets.mp4", "ss": 0.0},

    {"t0": b03_s,        "t1": b03_s + 3.25, "src": CLIPS_V7 / "br_hanoi_carton.mp4",      "ss": 0.0},
    {"t0": b03_s + 3.25, "t1": b03_s + 6.35, "src": CLIPS_V7 / "br_hcmc_suv.mp4",          "ss": 0.0},
    {"t0": b03_s + 6.35, "t1": b03_s + 8.65, "src": CLIPS_V7 / "br_wide_oanh_row_104.mp4", "ss": 0.0},
    {"t0": b03_s + 8.65, "t1": b03_e,        "src": CLIPS_V7 / "br_clean_row_104sets.mp4", "ss": 0.0},

    {"t0": b04_s,  "t1": b04_e,  "src": CLIPS_V7 / "b04_wide_oanh_104_live.mp4","ss": 0.0},
    {"t0": b05_s,  "t1": b05_e,  "src": CLIPS_V7 / "b05_intro_set_live.mp4",    "ss": 0.0},

    # b06: 4 Items Inside Set Qua — 100% Error-Free Muse Studio Visuals at Steady 1.00x (ZERO ZOOM!) + Real Sony C3852!
    {"t0": b06_s,       "t1": 48.10,       "src": CLIPS_V7 / "br_basket_full_hero.mp4",    "ss": 0.0},
    {"t0": 48.10,       "t1": 50.45,       "src": CLIPS_V7 / "muse_skanest_box.mp4",       "ss": 0.0},
    {"t0": 50.45,       "t1": 53.65,       "src": CLIPS_V7 / "prod_to_yen_dedicated1.mp4", "ss": 0.0},
    {"t0": 53.65,       "t1": 56.90,       "src": CLIPS_V7 / "br_inside_basket_clean.mp4", "ss": 0.0},
    {"t0": 56.90,       "t1": 60.25,       "src": CLIPS_V7 / "muse_skanest_box.mp4",       "ss": 1.2},
    {"t0": 60.25,       "t1": 63.48,       "src": CLIPS_V7 / "muse_two_jars.mp4",          "ss": 0.0},
    {"t0": 63.48,       "t1": 65.76,       "src": CLIPS_V7 / "muse_hu_say_gion.mp4",       "ss": 0.0},
    {"t0": 65.76,       "t1": 68.05,       "src": CLIPS_V7 / "muse_hu_say_me.mp4",         "ss": 0.0},
    {"t0": 68.05,       "t1": 72.76,       "src": CLIPS_V7 / "muse_banh_thuyen.mp4",       "ss": 0.0},
    {"t0": 72.76,       "t1": t_24thanh_s, "src": CLIPS_V7 / "muse_kep_hat.mp4",           "ss": 0.0},
    {"t0": t_24thanh_s, "t1": b06_e,       "src": CLIPS_V7 / "b06_24thanh_real_live.mp4",  "ss": 0.0},

    # b07a: Dedicated To Yen Tinh Che Soi Dai + Muse SKA NEST Box (Steady 1.00x!)
    {"t0": b07a_s,        "t1": b07a_s + 3.45, "src": CLIPS_V7 / "prod_to_yen_soi_dai2.mp4", "ss": 0.0},
    {"t0": b07a_s + 3.45, "t1": b07a_e,        "src": CLIPS_V7 / "muse_skanest_box.mp4",     "ss": 0.6},

    {"t0": b07b_s, "t1": b07b_e, "src": CLIPS_V7 / "b07b_camnang_live.mp4",     "ss": 0.0},
    {"t0": b08_s,  "t1": b08_e,  "src": CLIPS_V7 / "prod_chung_yen.mp4",        "ss": 0.0},

    {"t0": b09a_s, "t1": b09a_e, "src": CLIPS_V7 / "br_basket_full_hero.mp4",   "ss": 1.5},
    {"t0": b09b_s, "t1": b09b_e, "src": CLIPS_V7 / "b09b_quai_da_live.mp4",     "ss": 0.0},
    {"t0": b09c_s,        "t1": b09c_s + 2.65, "src": CLIPS_V7 / "br_basket_flower_bow.mp4", "ss": 0.0},
    {"t0": b09c_s + 2.65, "t1": b09c_e,        "src": CLIPS_V7 / "br_basket_row_bow.mp4",    "ss": 0.0},

    {"t0": b10a_s, "t1": b10a_e, "src": CLIPS_V7 / "b10a_sx_live.mp4",          "ss": 0.0},
    {"t0": b10b_s, "t1": b10b_e, "src": CLIPS_V7 / "br_factory_pack1.mp4",      "ss": 0.0},
    {"t0": b11a_s, "t1": b11a_e, "src": CLIPS_V7 / "b11a_cta_live1.mp4",        "ss": 0.0},
    {"t0": b11b_s, "t1": b11b_e, "src": CLIPS_V7 / "br_wide_oanh_arms_104.mp4", "ss": 0.2},
    {"t0": b11c_s, "t1": b11c_e, "src": CLIPS_V7 / "b11c_cta_inbox_live.mp4",   "ss": 0.0},
    {"t0": b11c_e, "t1": tot_end,"src": "OFFICIAL_ENDCARD_V7",                  "ss": 0.0},
]

FLOATING_OVERLAYS = [
    {"t0": b01_s + 3.80,      "t1": b01_e - 0.35, "src": CLIPS_V7 / "br_basket_flower_bow.mp4",   "ss": 0.2, "cx": 228, "cy": 415, "pw": 286, "ph": 368, "crop": (160, 420, 920, 1520), "dir": -1, "pip_idx": 0},
    {"t0": b05_s + 0.95,      "t1": b05_e - 0.30, "src": CLIPS_V7 / "br_inside_basket_clean.mp4", "ss": 0.2, "cx": 228, "cy": 415, "pw": 286, "ph": 368, "crop": (120, 320, 960, 1460), "dir": -1, "pip_idx": 1},
    {"t0": t_24thanh_s + 0.45,"t1": b06_e - 0.25, "src": CLIPS_V7 / "prod_kep_hat_real_bars.mp4", "ss": 0.2, "cx": 228, "cy": 418, "pw": 288, "ph": 372, "crop": (90,  220, 990, 1480), "dir": -1, "pip_idx": 2},
    {"t0": b07b_s + 1.40,     "t1": b07b_e - 0.35,"src": CLIPS_V7 / "prod_chung_yen.mp4",         "ss": 0.2, "cx": 228, "cy": 420, "pw": 286, "ph": 360, "crop": (160, 420, 920, 1460), "dir": -1, "pip_idx": 3},
    {"t0": b10a_s + 1.05,     "t1": b10a_e - 0.28,"src": CLIPS_V7 / "br_factory_pack1.mp4",       "ss": 0.3, "cx": 838, "cy": 415, "pw": 286, "ph": 366, "crop": (160, 360, 920, 1460), "dir": +1, "pip_idx": 4},
    {"t0": b11a_s + 1.20,     "t1": b11a_e - 0.28,"src": CLIPS_V7 / "br_basket_full_hero.mp4",    "ss": 0.5, "cx": 228, "cy": 418, "pw": 286, "ph": 368, "crop": (180, 460, 900, 1520), "dir": -1, "pip_idx": 5},
]

ING_SCHEDULE = [
    (56.95, 60.15, 0, 290, 385),
    (57.45, 60.15, 1, 775, 385),
    (58.15, 60.15, 2, 290, 1345),
    (58.75, 60.15, 3, 775, 1345),
]

# Preload Chrome CSS/SVG Sprites!
SUB_MANIFEST = json.loads((TYPOS_V7 / "subtitles_manifest.json").read_text(encoding="utf-8"))
SUB_SPRITES  = {fn: Image.open(TYPOS_V7 / fn).convert("RGBA") for it in SUB_MANIFEST for fn in it["lines"]}
HOOK_SPRITE  = Image.open(TYPOS_V7 / "hook_header.png").convert("RGBA")
PIP_SPRITES  = [Image.open(TYPOS_V7 / f"pip_{i}.png").convert("RGBA") for i in range(7)]
ING_SPRITES  = [Image.open(TYPOS_V7 / f"ing_{i}.png").convert("RGBA") for i in range(4)]
ENDCARD_BG   = Image.open(TYPOS_V7 / "endcard_bg.png").convert("RGBA")

# Soft invisible bottom vignette scrim (only bottom 420px, max alpha 96/255 = 37% so white/gold text pops effortlessly without any box!)
SCRIM_ARR = np.zeros((420, W, 4), dtype=np.uint8)
SCRIM_ARR[:, :, 3] = (np.linspace(0.0, 1.0, 420) ** 1.65 * 96.0).astype(np.uint8)[:, None]
BOTTOM_SCRIM = Image.fromarray(SCRIM_ARR)

class StreamingClipReader:
    def __init__(self):
        self._cache = {}
    def get_frame(self, path: Path, t_local: float) -> Image.Image:
        if "--test" in sys.argv:
            tj = V7 / "_fast_test_fr.png"
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, t_local):.3f}", "-i", str(path),
                "-vf", f"scale={W}:{H}", "-frames:v", "1", str(tj)
            ], check=True)
            return Image.open(tj).convert("RGB")
        key = str(path)
        if key not in self._cache:
            raw = subprocess.check_output([
                "ffmpeg", "-v", "error", "-i", key,
                "-vf", f"scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
            ])
            n = len(raw) // (W * H * 3)
            arr = np.frombuffer(raw[:n * W * H * 3], dtype=np.uint8).reshape((n, H, W, 3))
            self._cache[key] = arr
            if len(self._cache) > 10:
                oldest = next(iter(self._cache))
                if oldest != key:
                    del self._cache[oldest]
        arr = self._cache[key]
        idx = max(0, min(len(arr) - 1, int(round(t_local * FPS))))
        return Image.fromarray(arr[idx], mode="RGB")

READER = StreamingClipReader()

def ease_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3

def ease_out_back(x: float) -> float:
    x = max(0.0, min(1.0, x))
    c1 = 1.45; c3 = c1 + 1.0
    return 1.0 + c3 * ((x - 1.0) ** 3) + c1 * ((x - 1.0) ** 2)

def scale_and_fade_rgba(im: Image.Image, scale: float, alpha_mul: float) -> Image.Image:
    if abs(scale - 1.0) > 0.004:
        nw = max(4, int(round(im.width * scale)))
        nh = max(4, int(round(im.height * scale)))
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    if alpha_mul < 0.995:
        arr = np.array(im)
        arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * max(0.0, min(1.0, alpha_mul))).astype(np.uint8)
        im = Image.fromarray(arr)
    return im

def draw_floating_pip(canvas: Image.Image, t: float, ov: dict):
    dt_in  = t - ov["t0"]
    dt_out = ov["t1"] - t
    if dt_in < 0 or dt_out < 0:
        return
    p_in  = ease_out_back(dt_in / 0.34) if dt_in < 0.34 else 1.0
    p_out = ease_out_cubic(dt_out / 0.26) if dt_out < 0.26 else 1.0
    alpha = min(1.0, dt_in / 0.20, dt_out / 0.22)
    slide_x = int(round((1.0 - p_in) * 140 * ov["dir"] + (1.0 - p_out) * 90 * ov["dir"]))
    sc = 0.88 + 0.12 * min(p_in, p_out)

    fr = READER.get_frame(ov["src"], ov["ss"] + dt_in)
    x0, y0, x1, y1 = ov["crop"]
    pw, ph = max(40, int(round(ov["pw"] * sc))), max(40, int(round(ov["ph"] * sc)))
    card_rgb = fr.crop((x0, y0, x1, y1)).resize((pw, ph), Image.Resampling.LANCZOS)

    rad = 28
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=rad, fill=int(255 * alpha))

    pad = 24
    layer = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 8, pad + pw, pad + ph + 8], radius=rad, fill=(0, 0, 0, int(115 * alpha)))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=9))
    layer.alpha_composite(sh)

    c_rgba = card_rgb.convert("RGBA")
    c_rgba.putalpha(mask)
    layer.alpha_composite(c_rgba, (pad, pad))
    ImageDraw.Draw(layer).rounded_rectangle([pad, pad, pad + pw - 1, pad + ph - 1], radius=rad, outline=(250, 222, 148, int(230 * alpha)), width=3)

    px = ov["cx"] - pw // 2 - pad + slide_x
    py = ov["cy"] - ph // 2 - pad
    canvas.alpha_composite(layer, (px, py))

    pill = scale_and_fade_rgba(PIP_SPRITES[ov["pip_idx"]], sc, alpha)
    canvas.alpha_composite(pill, (ov["cx"] + slide_x - pill.width // 2, ov["cy"] + ph // 2 - pill.height // 2 + 4))

def draw_loupe_quai_da(canvas: Image.Image, t: float):
    t0, t1 = b09b_s + 0.55, b09b_e - 0.30
    if not (t0 <= t <= t1):
        return
    dt_in, dt_out = t - t0, t1 - t
    sc = ease_out_back(dt_in / 0.36) if dt_in < 0.36 else (ease_out_cubic(dt_out / 0.25) if dt_out < 0.25 else 1.0)
    alpha = min(1.0, dt_in / 0.20, dt_out / 0.20)
    D = max(60, int(round(306 * sc)))
    cx, cy = 232, 395

    fr = READER.get_frame(CLIPS_V7 / "prod_quai_loupe.mp4", 0.2 + dt_in)
    crop = fr.crop((200, 340, 880, 1020)).resize((D, D), Image.Resampling.LANCZOS)
    mask = Image.new("L", (D, D), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, D - 1, D - 1], fill=int(255 * alpha))

    pad = 26
    lay = Image.new("RGBA", (D + pad * 2, D + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", (D + pad * 2, D + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([pad, pad + 8, pad + D, pad + D + 8], fill=(0, 0, 0, int(125 * alpha)))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))

    c_rgba = crop.convert("RGBA"); c_rgba.putalpha(mask)
    lay.alpha_composite(c_rgba, (pad, pad))
    d = ImageDraw.Draw(lay)
    d.ellipse([pad, pad, pad + D - 1, pad + D - 1], outline=(248, 216, 136, int(245 * alpha)), width=6)
    d.ellipse([pad + 5, pad + 5, pad + D - 6, pad + D - 6], outline=(255, 250, 230, int(150 * alpha)), width=2)
    canvas.alpha_composite(lay, (cx - D // 2 - pad, cy - D // 2 - pad))

    pill = scale_and_fade_rgba(PIP_SPRITES[6], sc, alpha)
    canvas.alpha_composite(pill, (cx - pill.width // 2, cy + D // 2 - 22))

def render_frame_v7(fi: int) -> Image.Image:
    t = fi / FPS
    shot = SHOTS[-1]
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]:
            shot = s
            break

    if shot["src"] == "OFFICIAL_ENDCARD_V7":
        canvas = ENDCARD_BG.copy()
        dt = t - shot["t0"]
        fr = READER.get_frame(CLIPS_V7 / "br_basket_flower_bow.mp4", 0.3 + dt)
        pw, ph = 420, 440
        card = fr.crop((140, 420, 940, 1480)).resize((pw, ph), Image.Resampling.LANCZOS)
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=32, fill=255)
        c_rgba = card.convert("RGBA"); c_rgba.putalpha(mask)
        canvas.alpha_composite(c_rgba, (540 - pw // 2, 345))
        ImageDraw.Draw(canvas).rounded_rectangle([540 - pw // 2, 345, 540 + pw // 2 - 1, 345 + ph - 1], radius=32, outline=(246, 214, 132, 230), width=4)
        return canvas.convert("RGB")

    t_local = float(shot["ss"]) + (t - float(shot["t0"]))
    base_rgb = READER.get_frame(shot["src"], t_local)

    # 8-frame smooth optical cross-dissolve only across non-live B-roll cuts
    if (t - shot["t0"]) < 0.18 and shot["t0"] > 0.05:
        idx_s = SHOTS.index(shot)
        prev_s = SHOTS[idx_s - 1]
        if prev_s["src"] != "OFFICIAL_ENDCARD_V7" and "live" not in Path(shot["src"]).stem and "live" not in Path(prev_s["src"]).stem:
            prev_rgb = READER.get_frame(prev_s["src"], float(prev_s["ss"]) + (shot["t0"] - prev_s["t0"]))
            w_cur = ease_out_cubic((t - shot["t0"]) / 0.18)
            base_rgb = Image.blend(prev_rgb, base_rgb, w_cur)

    canvas = base_rgb.convert("RGBA")

    # Opening Luxury Hook Header (placed cleanly in top negative space y=185, zero overlap with gift baskets!)
    if 0.12 <= t <= 3.75:
        a_in  = ease_out_cubic((t - 0.12) / 0.32)
        a_out = ease_out_cubic((3.75 - t) / 0.28)
        a = min(a_in, a_out)
        y_off = int(round((1.0 - a_in) * 18))
        hk = scale_and_fade_rgba(HOOK_SPRITE, 0.96 + 0.04 * a_in, a)
        canvas.alpha_composite(hk, (540 - hk.width // 2, 185 + y_off))

    # Floating PIP Overlays
    for ov in FLOATING_OVERLAYS:
        if ov["t0"] <= t <= ov["t1"]:
            draw_floating_pip(canvas, t, ov)

    # 3D Gold Loupe on Quai Da Do Do
    draw_loupe_quai_da(canvas, t)

    # 4 Frosted Ingredient Pills (symmetrically above & below SKA NEST box at 56.95-60.15s!)
    for it0, it1, idx_ing, icx, icy in ING_SCHEDULE:
        if it0 <= t <= it1:
            p_in  = ease_out_back((t - it0) / 0.28) if (t - it0) < 0.28 else 1.0
            a_ing = min(1.0, (t - it0) / 0.16, (it1 - t) / 0.20)
            pil_im = scale_and_fade_rgba(ING_SPRITES[idx_ing], 0.88 + 0.12 * p_in, a_ing)
            canvas.alpha_composite(pil_im, (icx - pil_im.width // 2, icy - pil_im.height // 2))

    # Staggered Boxless 3D-Extruded Editorial Subtitles in Lower TikTok Safe Zone (y=1470 / 1528)!
    for sub in SUB_MANIFEST:
        st0, st1 = float(sub["t0"]), float(sub["t1"])
        if st0 <= t <= st1:
            # Whisper-soft bottom scrim faded in/out smoothly with subtitle
            sc_a = min(1.0, (t - st0) / 0.18, (st1 - t) / 0.18)
            canvas.alpha_composite(scale_and_fade_rgba(BOTTOM_SCRIM, 1.0, sc_a), (0, H - 420))
            n_lines = len(sub["lines"])
            base_y = 1502 if n_lines == 1 else 1468
            for li, fn in enumerate(sub["lines"]):
                lt0 = st0 + li * 0.08
                if t < lt0:
                    continue
                dt_l = t - lt0
                p_l  = ease_out_back(dt_l / 0.22) if dt_l < 0.22 else 1.0
                a_l  = min(1.0, dt_l / 0.14, (st1 - t) / 0.15)
                y_glide = int(round((1.0 - min(1.0, dt_l / 0.20)) * 12))
                sp_im = scale_and_fade_rgba(SUB_SPRITES[fn], 0.94 + 0.06 * p_l, a_l)
                canvas.alpha_composite(sp_im, (540 - sp_im.width // 2, base_y + li * 58 + y_glide))
            break

    return canvas.convert("RGB")


# ==============================================================================
# 2. BUILD TRUE 100% ORIGINAL RAW CAMERA SOURCE CAPCUT DRAFT ("source gốc"!)
#    - ZERO re-encoded files, ZERO AI files, ZERO text, ZERO BGM, ZERO SFX!
#    - Every single video material points DIRECTLY to untouched raw Sony .MP4s in:
#      Z:/Máy tính khác/My Computer/F20/video gốc/261116/Chi Oanh/dọc/C3xxx.MP4
# ==============================================================================
def uid(): return str(uuid.uuid4()).upper()
def us(sec): return int(round(float(sec) * 30.0) * 1_000_000 // 30)

RAW_META_CACHE = {}
def raw_sony_info(fn: str):
    p = RAW_SONY_D / fn
    if fn not in RAW_META_CACHE:
        pr = json.loads(subprocess.check_output([
            "ffprobe", "-v", "quiet", "-show_streams", "-show_format", "-of", "json", str(p)
        ]))
        vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
        # Account for rotation tag on vertical Sony MP4s
        rot = 0
        for sd in vs.get("side_data_list", []):
            if "rotation" in sd:
                rot = abs(int(sd["rotation"]))
        rot_tag = int(vs.get("tags", {}).get("rotate", 0))
        if rot in (90, 270) or rot_tag in (90, 270):
            w, h = int(vs["height"]), int(vs["width"])
        else:
            w, h = int(vs["width"]), int(vs["height"])
        dur_us = us(float(pr["format"]["duration"]))
        RAW_META_CACHE[fn] = (str(p).replace("\\", "/"), w, h, dur_us)
    return RAW_META_CACHE[fn]

def build_true_raw_source_capcut_draft():
    orig_dc = json.loads((BAK_DIR / "draft_content.json.orig").read_text(encoding="utf-8"))
    vtrack_tpl = copy.deepcopy(orig_dc["tracks"][0])
    vseg_tpl   = copy.deepcopy(orig_dc["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(orig_dc["materials"]["videos"][0])
    extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl = {k: copy.deepcopy(next(x for x in orig_dc["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in extra_keys}

    # Track 0: 100% Untouched Raw Sony Camera Spine (3-shot product pan intro + surgical stumble-free Chị Oanh A-roll takes!)
    # Every tuple: (raw_filename, in_sec, dur_sec, vol)
    RAW_AROLL_SPINE = [
        # 3-Shot Raw Product Pan Intro (0.00 - 3.90s)
        ("C3909.MP4", 0.40,  1.30, 0.0),
        ("C3910.MP4", 0.50,  1.30, 0.0),
        ("C3875.MP4", 0.50,  1.30, 0.0),
        # C3841: Opening + Nha Trang 77 sets & 13 sets + Ha Noi 10 sets + TP.HCM 4 sets (skips dead air at 19.7s!)
        ("C3841.MP4", 3.95,  15.73, 1.0),
        ("C3841.MP4", 20.12, 16.40, 1.0),
        # C3845: Wide Chị Oanh amidst 104 gift sets
        ("C3845.MP4", 1.55,  4.65,  1.0),
        # C3849: Intro to 1 Set Quà
        ("C3849.MP4", 2.50,  5.05,  1.0),
        # C3852: 4 Items inside Set Quà (skips "Còn..." and all 3 dead pauses cleanly!)
        ("C3852.MP4", 0.44,  9.66,  1.0),
        ("C3852.MP4", 10.52, 14.48, 1.0),
        ("C3852.MP4", 25.68, 4.72,  1.0),
        ("C3852.MP4", 31.88, 9.48,  1.0),
        # C3856: Tổ Yến Tinh Chế Sợi Dài + Cẩm Nang (skips 8.68..10.12s stumble!)
        ("C3856.MP4", 1.94,  6.74,  1.0),
        ("C3856.MP4", 10.12, 12.60, 1.0),
        # C3853: Giỏ Quà Mica + Quai Da Đỏ Đô + Hoa & Nơ Màu Be (skips 6.18..8.88s & 13.70..15.10s pauses!)
        ("C3853.MP4", 0.90,  5.28,  1.0),
        ("C3853.MP4", 8.88,  4.80,  1.0),
        ("C3853.MP4", 15.10, 5.20,  1.0),
        # C3862: Công ty F20 trực tiếp sản xuất (skips "sẵn sẵn" stumble!)
        ("C3862.MP4", 2.55,  4.95,  1.0),
        ("C3862.MP4", 8.35,  3.75,  1.0),
        # C3864: CTA Đặt Quà 20/11 & Nhắn Tin (skips 12.83..13.74s "đặt thang" stumble!)
        ("C3864.MP4", 5.10,  7.73,  1.0),
        ("C3864.MP4", 13.74, 8.18,  1.0),
    ]

    # Track 1: 100% Untouched Raw Sony B-Roll Cutaways placed cleanly above Track 0 (volume = 0.0)!
    # Every tuple: (target_start_sec, raw_filename, in_sec, dur_sec)
    RAW_BROLL_OVERLAYS = [
        (13.10, "C3921.MP4", 0.80, 2.75),   # Anh Hậu handover
        (15.85, "C3932.MP4", 0.60, 3.70),   # Anh Hậu 77 sets
        (19.55, "C3866.MP4", 3.00, 3.85),   # Hội phụ huynh 13 sets
        (23.50, "C3892.MP4", 0.60, 3.25),   # Đóng thùng gửi Hà Nội
        (26.75, "C3901.MP4", 0.50, 3.10),   # Xe giao đi TP.HCM
        (29.85, "C3865.MP4", 5.00, 2.80),   # Toàn cảnh Chị Oanh & dãy 104 set quà
        (32.65, "C3869.MP4", 1.50, 3.30),   # Dãy 104 set quà trên bàn
        (45.80, "C3908.MP4", 0.40, 4.20),   # Cận giỏ quà đầy đặn
        (53.80, "C3873.MP4", 0.15, 2.40),   # Cận bên trong giỏ quà (trước khi lia trần)
        (56.20, "C3874.MP4", 0.50, 4.00),   # Kệ hộp yến sào & hũ rong biển F20 thật
        (85.90, "C3875.MP4", 0.60, 4.20),   # Kệ trưng bày yến sào SKA NEST thật
        (105.2, "C3908.MP4", 2.00, 4.50),   # Giỏ quà mica trong suốt
        (115.2, "C3909.MP4", 1.60, 2.60),   # Bông hoa điểm nhấn (không zoom)
        (117.8, "C3910.MP4", 2.00, 2.60),   # Nơ voan màu be (không zoom)
        (125.4, "C3882.MP4", 0.60, 3.75),   # Nhân viên F20 trực tiếp đóng gói
        (134.8, "C3865.MP4", 1.50, 3.40),   # Toàn cảnh 104 set quà lễ 20/11
    ]

    d_id = uid()
    D = copy.deepcopy(orig_dc)
    D.update({
        "id": d_id, "name": DRAFT_RAW_NAME, "fps": 30.0,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in orig_dc["materials"]}
    })

    mat_by_fn = {}
    def get_or_add_raw_mat(fn: str):
        if fn not in mat_by_fn:
            abs_p, w, h, dur_u = raw_sony_info(fn)
            mid = uid()
            vm = copy.deepcopy(vmat_tpl)
            vm.update({
                "id": mid, "local_material_id": str(uuid.uuid4()), "type": "video",
                "path": abs_p, "material_name": fn,
                "width": w, "height": h, "duration": dur_u, "has_audio": True,
            })
            D["materials"]["videos"].append(vm)
            mat_by_fn[fn] = mid
        return mat_by_fn[fn]

    def make_raw_seg(fn: str, src_in_s: float, dur_s: float, tgt_start_u: int, vol: float, r_idx: int):
        mid = get_or_add_raw_mat(fn)
        du  = us(dur_s)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k in extra_keys:
            em = copy.deepcopy(v_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": us(src_in_s), "duration": du},
            "target_timerange": {"start": tgt_start_u, "duration": du},
            "speed": 1.0, "volume": vol, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": r_idx
        })
        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        seg["clip"]["alpha"] = 1.0
        return seg, du

    # Build Track 0 (Contiguous Raw Sony Spine)
    tr0 = copy.deepcopy(vtrack_tpl); tr0["id"] = uid(); tr0["segments"] = []
    cur_u = 0
    for fn, s_in, dur_s, vol in RAW_AROLL_SPINE:
        seg, du = make_raw_seg(fn, s_in, dur_s, cur_u, vol, 0)
        tr0["segments"].append(seg)
        cur_u += du
    D["tracks"].append(tr0)
    tot_u = cur_u
    D["duration"] = tot_u

    # Build Track 1 (Raw Sony B-Roll Cutaways on top, volume = 0.0)
    tr1 = copy.deepcopy(vtrack_tpl); tr1["id"] = uid(); tr1["segments"] = []
    for t_st, fn, s_in, dur_s in RAW_BROLL_OVERLAYS:
        tgt_u = us(t_st)
        if tgt_u + us(dur_s) <= tot_u:
            seg, _ = make_raw_seg(fn, s_in, dur_s, tgt_u, 0.0, 1)
            tr1["segments"].append(seg)
    D["tracks"].append(tr1)

    stg = V7 / DRAFT_RAW_NAME
    if stg.exists():
        shutil.rmtree(stg)
    stg.mkdir(parents=True, exist_ok=True)

    dc_s = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    for fn in ("draft_content.json", "draft_info.json", "template.tmp", "template-2.tmp"):
        (stg / fn).write_text(dc_s, encoding="utf-8")

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "1.0",
        "-i", str(RAW_SONY_D / "C3909.MP4"), "-frames:v", "1", str(stg / "draft_cover.jpg")
    ], check=True)

    donor_dir = DRAFTS_DIR / "1117"
    dmi = json.loads((donor_dir / "draft_meta_info.json").read_text(encoding="utf-8"))
    now_us = int(time.time() * 1_000_000)
    cap_dst = DRAFTS_DIR / DRAFT_RAW_NAME

    # Populate draft_materials[0].value so CapCut's Media Bin ALSO shows all 20 raw Sony MP4s cleanly!
    bin_vals = []
    for fn, mid in mat_by_fn.items():
        abs_p, w, h, dur_u = raw_sony_info(fn)
        bin_vals.append({
            "create_time": int(time.time()),
            "duration": dur_u,
            "extra_info": fn,
            "file_Path": abs_p,
            "height": h, "width": w,
            "id": str(uuid.uuid4()),
            "import_time": int(time.time()),
            "import_time_ms": int(time.time() * 1000),
            "item_source": 1, "md5": "", "metetype": "video",
            "roughcut_time_range": {"duration": -1, "start": -1},
            "sub_time_range": {"duration": -1, "start": -1},
            "type": 0,
        })

    dmi.update({
        "draft_id": d_id, "draft_name": DRAFT_RAW_NAME,
        "draft_fold_path": str(cap_dst).replace("\\", "/"),
        "draft_root_path": str(DRAFTS_DIR), "draft_cover": "draft_cover.jpg",
        "tm_duration": tot_u, "tm_draft_create": now_us, "tm_draft_modified": now_us,
        "draft_materials": [{"type": 0, "value": bin_vals}] + [{"type": t, "value": []} for t in (1, 2, 3, 6, 7, 8)]
    })
    (stg / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for aux in ("draft_agency_config.json", "draft_biz_config.json", "draft_virtual_store.json", "key_value.json", "performance_opt_info.json"):
        if (donor_dir / aux).exists():
            shutil.copy2(donor_dir / aux, stg / aux)

    # Also write Timelines/<id>/draft_content.json for newer CapCut Desktop versions!
    tl_sub = stg / "Timelines" / d_id
    tl_sub.mkdir(parents=True, exist_ok=True)
    (tl_sub / "draft_content.json").write_text(dc_s, encoding="utf-8")

    for dst_f in [
        str(cap_dst),
        rf"Z:\Máy tính khác\My Computer\Document HT Media\TLH\{DRAFT_RAW_NAME}",
        rf"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011\{DRAFT_RAW_NAME}",
    ]:
        if os.path.exists(dst_f):
            shutil.rmtree(dst_f)
        os.makedirs(os.path.dirname(dst_f), exist_ok=True)
        shutil.copytree(stg, dst_f)
        print("  -> Deployed True Raw-Source CapCut Draft:", dst_f, flush=True)

    # Clean old generated drafts from root_meta_info.json while keeping user's original 1117 & F20 vd 1 untouched!
    rmi_path = DRAFTS_DIR / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8")) if rmi_path.exists() else {"all_draft_store": []}
    old_gen = {"F20_SetQua_2011_SourceOnly", "F20_SetQua_2011_V6_Edit", "F20_SetQua_2011_V5_Clean", DRAFT_RAW_NAME}
    stores = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") not in old_gen]
    ent = copy.deepcopy(stores[0]) if stores else {}
    ent.update({
        "draft_cloud_last_action_download": False,
        "draft_cover": f"{cap_dst}/draft_cover.jpg".replace("\\", "/"),
        "draft_fold_path": str(cap_dst).replace("\\", "/"),
        "draft_id": d_id, "draft_is_invisible": False,
        "draft_json_file": f"{cap_dst}/draft_content.json".replace("\\", "/"),
        "draft_name": DRAFT_RAW_NAME, "draft_root_path": str(DRAFTS_DIR),
        "tm_draft_create": now_us, "tm_draft_modified": now_us + 2000, "tm_duration": tot_u,
    })
    rmi["all_draft_store"] = [ent] + stores
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Registered 100% Pure Raw-Source Draft {DRAFT_RAW_NAME} at #1 in CapCut Desktop!", flush=True)


if __name__ == "__main__":
    total_frames = int(TL_V5["total_frames"])
    total_dur    = float(TL_V5["total_dur"])

    if "--test" in sys.argv:
        test_ts = [
            0.8, 2.0, 9.5, 17.5,
            49.2, 52.0, 55.2, 59.0,
            62.0, 64.5, 70.2, 74.8,
            79.5, 84.0, 110.2, 114.0,
        ]
        grid = Image.new("RGB", (270 * 4, 480 * 4))
        for i, ts in enumerate(test_ts):
            fr = render_frame_v7(int(round(ts * FPS)))
            th = fr.resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(th)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(130, 255, 170))
            grid.paste(th, ((i % 4) * 270, (i // 4) * 480))
        grid.save(V7 / "v7_test_grid_16.jpg", quality=94)
        print("Saved v7_test_grid_16.jpg!")
    else:
        vid_only = V7 / "_v7_video_only.mp4"
        proc = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", str(vid_only)
        ], stdin=subprocess.PIPE)
        for fi in range(total_frames):
            fr = render_frame_v7(fi)
            proc.stdin.write(fr.tobytes())
            if fi % 300 == 0 or fi == total_frames - 1:
                print(f"Rendered {fi+1}/{total_frames} frames ({(fi+1)/total_frames*100:.1f}%)", flush=True)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("FFmpeg encode failed")

        m4a = V5 / "03_Master_V5_14LUFS.m4a"
        final_local = V7 / "F20_SET_QUA_2011_V7_FINAL.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", str(vid_only), "-i", str(m4a),
            "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", str(final_local)
        ], check=True)

        for dp in [
            r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\F20_SET_QUA_2011_FINAL.mp4",
            r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\f20-set-qua-2011_FINAL.mp4",
            r"D:\XUẤT CAPCUT\F20_SET_QUA_2011_FINAL.mp4",
        ]:
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(final_local, dp)
            print("  -> Exported V7 Master MP4 to:", dp, flush=True)

        build_true_raw_source_capcut_draft()

        qc_ts = [0.8, 2.0, 9.5, 17.5, 30.8, 36.2, 49.2, 52.0, 55.2, 59.0, 62.0, 64.5, 66.8, 70.2, 74.8, 79.5, 84.0, 110.2, 114.0, total_dur - 1.4]
        sheet = Image.new("RGB", (270 * 5, 480 * 4))
        tmp = V7 / "_tmp_qcf.jpg"
        for i, ts in enumerate(qc_ts):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(final_local), "-frames:v", "1", str(tmp)], check=True)
            im = Image.open(tmp).resize((270, 480), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(im)
            d.rectangle([4, 4, 108, 26], fill=(0, 0, 0))
            d.text((8, 7), f"t={ts:5.1f}s", fill=(130, 255, 170))
            sheet.paste(im, ((i % 5) * 270, (i // 5) * 480))
        tmp.unlink(missing_ok=True)
        qc_path = V7 / "qc_v7_final_20frames.jpg"
        sheet.save(qc_path, quality=94)

        arch = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011")
        for sf in [qc_path, V7 / "_v7_vs_v6_color_check.jpg", V7 / "_v7_muse_full_sheet.jpg", V7 / "v7_step2_build_all_clips_and_muse_videos.py", V7 / "v7_step3_render_chrome_typography.js", V7 / "v7_step4_render_master_and_raw_capcut.py"]:
            if sf.exists():
                shutil.copy2(sf, arch / sf.name)
        print("ALL V7 DELIVERABLES COMPLETED!", flush=True)
