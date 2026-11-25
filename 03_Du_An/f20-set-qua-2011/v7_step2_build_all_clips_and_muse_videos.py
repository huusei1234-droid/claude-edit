import base64, colorsys, io, json, math, os, shutil, subprocess, time, urllib.request
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT      = Path(r"d:\AI\full studio\output\f20-set-qua-2011")
CACHE    = OUT / "raw_cache"
V2_FV    = OUT / "v2_1117" / "flow_videos"
V3_DIR   = OUT / "v3_pro"
V3_VID   = V3_DIR / "videos_v3"
FB       = V3_DIR / "fb_assets"
V5       = OUT / "v5_master"
VOICE_V5 = V5 / "voice_v5"
V7       = OUT / "v7_master"
MUSE_D   = V7 / "muse_products"
CLIPS_V7 = V7 / "clips_v7"
CLIPS_V7.mkdir(parents=True, exist_ok=True)

OVERLAY_PEARL = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k\05_Soft_Pearl_Sparkles_Bling_9x16.mp4")
shutil.copy2(OVERLAY_PEARL, V7 / "ov_pearl.mp4")

FPS = 30
API_KEY = Path(r"d:\AI\full studio\canvas\muse2api\data\api_key").read_text(encoding="utf-8").strip()

# 1. Regenerate muse_06_kep_hat_500g_v2.png so tray ONLY has dark-green sandwiched seaweed bars (no boat wafers!)
kep_v2 = MUSE_D / "muse_06_kep_hat_500g_v2.png"
if not kep_v2.exists():
    def to_du(im):
        im = im.convert("RGB")
        im.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        b = io.BytesIO(); im.save(b, format="JPEG", quality=93)
        return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode("ascii")

    im_pkh = Image.open(MUSE_D / "_ref_pouch_kep_hat.jpg")
    im_bars_fb = Image.open(FB / "step_157_shot_6_rong_bien_kep_hat_1.png").convert("RGB")
    w, h = im_bars_fb.size
    im_bars_crop = im_bars_fb.crop((int(w * 0.22), int(h * 0.14), int(w * 0.68), int(h * 0.86)))
    payload = {
        "model": "muse-image",
        "prompt": (
            "Vertical 9:16 commercial food photography of the stand-up clear zipper pouch of 'Tuệ Tâm - RONG BIỂN KẸP HẠT' "
            "from reference 1 standing neatly on a calm light oak wooden table behind a small bamboo plate holding ONLY 5 rectangular "
            "dark-green roasted nori seaweed bars sandwiched with almonds, pumpkin seeds, and cashews (like reference 2, NO boat wafers). "
            "Soft natural daylight, calm neutral colors, medium studio framing. Keep the front label headline 'Tuệ Tâm' and 'RONG BIỂN KẸP HẠT' "
            "clean, sharp, and 100% accurate in Vietnamese, with clean minimal design and no messy tiny text."
        ),
        "size": "9:16",
        "n": 1,
        "response_format": "b64_json",
        "image": [to_du(im_pkh), to_du(im_bars_crop)],
    }
    req = urllib.request.Request(
        "http://127.0.0.1:18610/v1/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
        method="POST",
    )
    print("Generating clean muse_06_kep_hat_500g_v2.png (pure seaweed bars)...", flush=True)
    with urllib.request.urlopen(req, timeout=260) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    b64 = res["data"][0].get("b64_json")
    raw = base64.b64decode(b64) if b64 else urllib.request.urlopen(res["data"][0]["url"], timeout=60).read()
    Image.open(io.BytesIO(raw)).convert("RGB").save(kep_v2, format="PNG")
    print("  -> Saved muse_06_kep_hat_500g_v2.png!", flush=True)

# Cleanly soften the tiny 6px sub-caption line under '100% HẠT DINH DƯỠNG - KHÔNG CHẤT' on muse_05_banh_thuyen_250g.png
im_bt = Image.open(MUSE_D / "muse_05_banh_thuyen_250g.png").convert("RGB")
# Upscale all Muse images to 1080x1920 cleanly
def prep_muse_1080(src_png: Path, out_png: Path, clean_bt_sub=False):
    im = Image.open(src_png).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)
    if clean_bt_sub:
        # On 1080x1920 muse_05, replace the tiny 2nd subline (y=812..834, x=415..670) with clean matching label paper!
        arr = np.array(im)
        bg_col = np.median(arr[790:800, 405:420], axis=(0, 1)).astype(np.uint8)
        d = ImageDraw.Draw(im)
        d.rectangle([408, 811, 678, 835], fill=tuple(int(x) for x in bg_col))
        # Also softly blur the microscopic bottom paragraph (y=1030..1110, x=405..670) like natural shallow DOF print
        patch = im.crop((405, 1028, 675, 1112)).filter(ImageFilter.GaussianBlur(radius=1.8))
        im.paste(patch, (405, 1028))
    im.save(out_png, quality=96)
    return out_png

prep_muse_1080(MUSE_D / "muse_01_skanest_box.png",      MUSE_D / "hi_01_skanest_box.png")
prep_muse_1080(MUSE_D / "muse_02_two_jars_f20.png",     MUSE_D / "hi_02_two_jars_f20.png")
prep_muse_1080(MUSE_D / "muse_03_hu_say_gion.png",      MUSE_D / "hi_03_hu_say_gion.png")
prep_muse_1080(MUSE_D / "muse_04_hu_say_me.png",        MUSE_D / "hi_04_hu_say_me.png")
prep_muse_1080(MUSE_D / "muse_05_banh_thuyen_250g.png", MUSE_D / "hi_05_banh_thuyen_250g.png", clean_bt_sub=True)
prep_muse_1080(kep_v2,                                  MUSE_D / "hi_06_kep_hat_500g.png")

# 2. Refine Classroom LUT slightly (+4% fresh herbal green while keeping wood 100% de-oranged!)
from v7_test_hsl_grade import write_hsl_cube
write_hsl_cube(
    V7 / "lut_v7_classroom.cube",
    wb_rgb=(0.972, 0.998, 1.026), exp_mul=0.985, shoulder_top=0.902,
    global_sat=1.03, orange_sat=-0.40, orange_lum=-0.08, orange_hue_deg=3.0,
    yellow_sat=-0.24, yellow_lum=-0.09, red_sat=-0.07, red_lum=-0.03, green_sat=+0.05,
)

def make_sony_clip(out_name, src_p, ss, dur, crop_vf, lut_fn, wav_mux=None, slow_pts=1.0):
    frames = int(round(dur * FPS))
    exact_dur = frames / FPS
    src_read = exact_dur / slow_pts if slow_pts > 1.01 else exact_dur
    dst = CLIPS_V7 / out_name
    tmp = CLIPS_V7 / f"_t_{out_name}"
    pts_vf = f"setpts={slow_pts:.3f}*PTS," if slow_pts > 1.01 else ""
    vf = f"{pts_vf}{crop_vf},lut3d=file={lut_fn},fps=30,format=yuv420p"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{ss:.4f}", "-t", f"{src_read + 0.20:.4f}", "-i", str(src_p),
        "-frames:v", str(frames), "-vf", vf, "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "15", str(tmp)
    ], cwd=str(V7), check=True)
    if wav_mux and Path(wav_mux).exists():
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp), "-i", str(wav_mux),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(dst)
        ], check=True)
        tmp.unlink(missing_ok=True)
    else:
        tmp.replace(dst)
    return dst

def make_muse_steady_clip(out_name, hi_png, dur):
    # ZERO ZOOM on packaged text! Steady 1.00x crisp studio photo + 11% soft neutral pearl bokeh overlay + calm LUT!
    frames = int(round(dur * FPS))
    dst = CLIPS_V7 / out_name
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-framerate", "30", "-i", str(hi_png),
        "-stream_loop", "-1", "-i", "ov_pearl.mp4",
        "-frames:v", str(frames),
        "-filter_complex",
        "[0:v]unsharp=5:5:0.35:5:5:0.0,lut3d=file=lut_v7_product.cube,format=rgb24[bg];"
        "[1:v]scale=1080:1920,hue=s=0.15,format=rgb24[ov];"
        "[bg][ov]blend=all_mode=screen:all_opacity=0.10,fps=30,format=yuv420p[v]",
        "-map", "[v]", "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "15", str(dst)
    ], cwd=str(V7), check=True)
    return dst

tl_v5 = json.loads((V5 / "timeline_v5_master.json").read_text(encoding="utf-8"))
bmap  = {b["id"]: b for b in tl_v5["blocks"]}

LIVE_JOBS = [
    ("b01_open_live.mp4",          CACHE / "C3841.MP4", 3.95,  bmap["b01_open_live"]["dur"],          "scale=1112:1977,crop=1080:1920:0:28",  "lut_v7_showroom.cube", VOICE_V5 / "b01_open_live.wav"),
    ("b04_wide_oanh_104_live.mp4", CACHE / "C3845.MP4", 1.55,  bmap["b04_wide_oanh_104_live"]["dur"], "scale=1096:1948,crop=1080:1920:4:14",  "lut_v7_showroom.cube", VOICE_V5 / "b04_wide_oanh_104_live.wav"),
    ("b05_intro_set_live.mp4",     CACHE / "C3849.MP4", 2.50,  bmap["b05_intro_set_live"]["dur"],     "scale=1140:2026,crop=1080:1920:0:53",  "lut_v7_showroom.cube", VOICE_V5 / "b05_intro_set_live.wav"),
    ("b06_24thanh_real_live.mp4",  CACHE / "C3852.MP4", 36.24, 5.15,                                  "scale=1150:2044,crop=1080:1920:0:62",  "lut_v7_showroom.cube", None),
    ("b07b_camnang_live.mp4",      CACHE / "C3856.MP4", 10.12, bmap["b07b_camnang_live"]["dur"],      "scale=1096:1948,crop=1080:1920:8:14",  "lut_v7_showroom.cube", VOICE_V5 / "b07b_camnang_live.wav"),
    ("b09b_quai_da_live.mp4",      CACHE / "C3853.MP4", 8.88,  bmap["b09b_quai_da_live"]["dur"],      "scale=1166:2073,crop=1080:1920:86:76", "lut_v7_showroom.cube", VOICE_V5 / "b09b_quai_da_live.wav"),
    ("b10a_sx_live.mp4",           CACHE / "C3862.MP4", 2.55,  bmap["b10a_sx_live"]["dur"],           "scale=1166:2073,crop=1080:1920:0:76",  "lut_v7_showroom.cube", VOICE_V5 / "b10a_sx_live.wav"),
    ("b11a_cta_live1.mp4",         CACHE / "C3864.MP4", 5.10,  bmap["b11a_cta_live1"]["dur"],         "scale=1240:2204,crop=1080:1920:0:112", "lut_v7_showroom.cube", VOICE_V5 / "b11a_cta_live1.wav"),
    ("b11c_cta_inbox_live.mp4",    CACHE / "C3864.MP4", 17.42, bmap["b11c_cta_inbox_live"]["dur"],    "scale=1166:2073,crop=1080:1920:0:76",  "lut_v7_showroom.cube", VOICE_V5 / "b11c_cta_inbox_live.wav"),
]
print("Rendering 9 V7 De-Oranged Calm Live Sony clips...", flush=True)
for onm, sp, ss, dur, cvf, lfn, wmux in LIVE_JOBS:
    make_sony_clip(onm, sp, ss, dur, cvf, lfn, wav_mux=wmux)
    print("  -> Live:", onm, flush=True)

BROLL_JOBS = [
    ("br_intro1_sunlit_sets.mp4",  CACHE / "C3909.MP4", 0.40, 2.20, "scale=1080:1920", "lut_v7_classroom.cube", 1.0),
    ("br_intro2_long_table.mp4",   CACHE / "C3910.MP4", 0.50, 2.20, "scale=1080:1920", "lut_v7_classroom.cube", 1.0),
    ("br_intro3_shelf_tower.mp4",  CACHE / "C3875.MP4", 0.50, 2.40, "scale=1080:1920", "lut_v7_showroom.cube",  1.0),
    ("br_wide_oanh_arms_104.mp4",  CACHE / "C3845.MP4", 1.50, 5.80, "scale=1096:1948,crop=1080:1920:4:14", "lut_v7_showroom.cube", 1.0),
    ("br_wide_oanh_row_104.mp4",   CACHE / "C3865.MP4", 5.00, 5.00, "scale=1080:1920", "lut_v7_showroom.cube",  1.0),
    ("br_clean_row_104sets.mp4",   CACHE / "C3869.MP4", 1.50, 5.00, "scale=1080:1920", "lut_v7_showroom.cube",  1.0),
    ("br_anh_hau_handover.mp4",    CACHE / "C3921.MP4", 0.80, 4.50, "scale=1080:1920", "lut_v7_classroom.cube", 1.0),
    ("br_anh_hau_77sets.mp4",      CACHE / "C3932.MP4", 0.60, 4.50, "scale=1080:1920", "lut_v7_classroom.cube", 1.0),
    ("br_phu_huynh_13sets.mp4",    CACHE / "C3866.MP4", 3.00, 5.00, "scale=1080:1920", "lut_v7_showroom.cube",  1.0),
    ("br_hanoi_carton.mp4",        CACHE / "C3892.MP4", 0.60, 4.50, "scale=1080:1920", "lut_v7_showroom.cube",  1.0),
    ("br_hcmc_suv.mp4",            CACHE / "C3901.MP4", 0.50, 4.50, "scale=1080:1920", "lut_v7_outdoor.cube",   1.0),
    ("br_basket_full_hero.mp4",    CACHE / "C3908.MP4", 0.40, 6.50, "scale=1080:1920", "lut_v7_classroom.cube", 1.0),
    ("br_basket_flower_bow.mp4",   CACHE / "C3909.MP4", 1.60, 6.50, "scale=1080:1920", "lut_v7_classroom.cube", 1.0),
    ("br_basket_row_bow.mp4",      CACHE / "C3910.MP4", 2.00, 6.00, "scale=1080:1920", "lut_v7_classroom.cube", 1.0),
    ("br_inside_basket_clean.mp4", CACHE / "C3873.MP4", 0.15, 3.80, "scale=1080:1920", "lut_v7_showroom.cube",  1.60),
    ("br_factory_pack1.mp4",       CACHE / "C3882.MP4", 0.60, 5.00, "scale=1080:1920", "lut_v7_showroom.cube",  1.0),
    # Text-free pure raw bird's nest & stewed bowl clips (ZERO text on these!)
    ("prod_to_yen_dedicated1.mp4", V2_FV  / "OUT_f20_v1_full_to_yen.mp4", 0.25, 4.80, "scale=1160:2062,crop=1080:1920:40:71", "lut_v7_product.cube", 1.0),
    ("prod_to_yen_soi_dai2.mp4",   V3_VID / "V3_vid03_to_yen_pure.mp4",   0.25, 4.20, "scale=1080:1920", "lut_v7_product.cube", 1.65),
    ("prod_kep_hat_real_bars.mp4", V3_VID / "V3_vid12_kep_hat_bars.mp4",  0.20, 5.20, "crop=920:1280:80:60,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "lut_v7_product.cube", 1.0),
    ("prod_chung_yen.mp4",         V3_VID / "V3_vid10_chung_yen.mp4",     0.20, 4.20, "scale=1080:1920", "lut_v7_product.cube", 1.0),
    ("prod_quai_loupe.mp4",        V3_VID / "V3_vid14_quai_no_macro.mp4", 0.20, 5.20, "scale=1080:1920", "lut_v7_product.cube", 1.0),
]
print("Rendering 21 V7 De-Oranged B-roll & text-free bird's nest clips...", flush=True)
for onm, sp, ss, dur, cvf, lfn, spts in BROLL_JOBS:
    make_sony_clip(onm, sp, ss, dur, cvf, lfn, slow_pts=spts)
    print("  -> B-roll:", onm, flush=True)

# 3. Render 6 Error-Free Muse Studio Product Clips (Steady 1.00x, ZERO ZOOM, Crisp Text!)
MUSE_CLIP_JOBS = [
    ("muse_skanest_box.mp4",  MUSE_D / "hi_01_skanest_box.png",      5.00),
    ("muse_two_jars.mp4",     MUSE_D / "hi_02_two_jars_f20.png",     4.20),
    ("muse_hu_say_gion.mp4",  MUSE_D / "hi_03_hu_say_gion.png",      3.60),
    ("muse_hu_say_me.mp4",    MUSE_D / "hi_04_hu_say_me.png",        3.60),
    ("muse_banh_thuyen.mp4",  MUSE_D / "hi_05_banh_thuyen_250g.png", 5.20),
    ("muse_kep_hat.mp4",      MUSE_D / "hi_06_kep_hat_500g.png",     5.00),
]
print("Rendering 6 Steady 1.00x Muse Studio Product Clips (0% Text Error)...", flush=True)
for onm, hpng, dur in MUSE_CLIP_JOBS:
    make_muse_steady_clip(onm, hpng, dur)
    print("  -> Muse Clip:", onm, flush=True)

# Save quick audit of Muse 05 & Muse 06 v2
sh = Image.new("RGB", (540 * 2, 960), (20, 20, 20))
sh.paste(Image.open(MUSE_D / "hi_05_banh_thuyen_250g.png").resize((540, 960), Image.Resampling.LANCZOS), (0, 0))
sh.paste(Image.open(MUSE_D / "hi_06_kep_hat_500g.png").resize((540, 960), Image.Resampling.LANCZOS), (540, 0))
sh.save(V7 / "_v7_muse_05_06_check.jpg", quality=94)
print("ALL V7 CLIPS & MUSE SHOWCASES READY!", flush=True)
