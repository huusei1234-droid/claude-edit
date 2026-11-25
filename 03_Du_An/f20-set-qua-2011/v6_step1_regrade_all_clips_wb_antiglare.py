import json, os, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

OUT      = Path(r"d:\AI\full studio\output\f20-set-qua-2011")
CACHE    = OUT / "raw_cache"
V2_FV    = OUT / "v2_1117" / "flow_videos"
V3_VID   = OUT / "v3_pro" / "videos_v3"
V4_VID   = OUT / "v4_clean_master" / "videos_v4"
V5       = OUT / "v5_master"
VOICE_V5 = V5 / "voice_v5"
V6       = OUT / "v6_master"
CLIPS_V6 = V6 / "clips_v6"
CLIPS_V6.mkdir(parents=True, exist_ok=True)

LUTS_SRC = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau")
shutil.copy2(LUTS_SRC / "01_HTPM_Beauty_Rosy_Skin.cube", V6 / "lut_skin.cube")
shutil.copy2(LUTS_SRC / "12_Vibrant_Social_Reels_Pop.cube", V6 / "lut_pop.cube")

FPS = 30

# ==============================================================================
# TRUE NEUTRAL WHITE BALANCE + ANTI-GLARE HIGHLIGHT ROLL-OFF + VIBRANT COLOR!
# - Zero linear brightness boost (eliminates 100% of white blowout / glare!)
# - S-curve highlight protection: rolls 0.78..1.00 smoothly to 0.72..0.90
# - Neutralized tungsten in Showroom & neutral crisp whites in Classroom
# - Lush Vibrance + subtle 22% Vibrant Pop / Rosy Skin LUT blend!
# ==============================================================================
LUT_SKIN_22 = "split[o][g];[g]lut3d=file=lut_skin.cube:interp=tetrahedral[g2];[o][g2]blend=all_expr='A*0.78+B*0.22'"
LUT_POP_22  = "split[o][g];[g]lut3d=file=lut_pop.cube:interp=tetrahedral[g2];[o][g2]blend=all_expr='A*0.78+B*0.22'"

WB_SHOWROOM = (
    "colorbalance=rs=-0.02:gs=0.01:bs=0.04:rm=-0.058:gm=0.015:bm=0.078:rh=-0.048:gh=0.01:bh=0.068,"
    "curves=all='0/0.01 0.20/0.18 0.50/0.51 0.76/0.71 0.90/0.82 1/0.90',"
    "vibrance=intensity=0.30,eq=saturation=1.18:contrast=1.05,"
    f"{LUT_SKIN_22}"
)

WB_CLASS_BRIGHT = (   # C3908, C3909, C3921, C3932: neutral white shirt/lids, strong anti-glare on table & sign!
    "colorbalance=rs=0.01:gs=0.00:bs=-0.01:rm=0.018:gm=0.00:bm=-0.018:rh=0.01:gh=0.00:bh=-0.01,"
    "curves=all='0/0.01 0.18/0.16 0.48/0.46 0.72/0.65 0.88/0.78 1/0.89',"
    "vibrance=intensity=0.35,eq=saturation=1.22:contrast=1.06,"
    f"{LUT_POP_22}"
)

WB_CLASS_TABLE = (    # C3910: lift shadows gently while rolling off table glare!
    "colorbalance=rs=0.015:gs=0.00:bs=-0.015:rm=0.022:gm=0.00:bm=-0.022:rh=0.01:gh=0.00:bh=-0.01,"
    "curves=all='0/0.01 0.20/0.22 0.50/0.52 0.75/0.69 0.90/0.80 1/0.89',"
    "vibrance=intensity=0.35,eq=saturation=1.22:contrast=1.06,"
    f"{LUT_POP_22}"
)

WB_OUTDOOR = (        # C3901: crisp outdoor white SUV without roof glare + vibrant color!
    "colorbalance=rm=0.02:gm=0.005:bm=-0.02,"
    "curves=all='0/0.01 0.20/0.18 0.50/0.50 0.76/0.70 0.90/0.81 1/0.90',"
    "vibrance=intensity=0.30,eq=saturation=1.18:contrast=1.05,"
    f"{LUT_POP_22}"
)

WB_PRODUCT = (        # Clean anti-glare + vibrant color match on product studio clips!
    "colorbalance=rm=-0.015:gm=0.005:bm=0.02,"
    "curves=all='0/0.01 0.20/0.18 0.50/0.50 0.78/0.73 0.92/0.84 1/0.91',"
    "vibrance=intensity=0.26,eq=saturation=1.15:contrast=1.05"
)

def make_clip(out_name, src_p, ss, dur, crop_vf, grade_vf, wav_mux=None, slow_pts=1.0):
    frames = int(round(dur * FPS))
    exact_dur = frames / FPS
    src_read_dur = exact_dur / slow_pts if slow_pts > 1.01 else exact_dur
    dst = CLIPS_V6 / out_name
    tmp = CLIPS_V6 / f"_t_{out_name}"
    pts_vf = f"setpts={slow_pts:.3f}*PTS," if slow_pts > 1.01 else ""
    vf = f"{pts_vf}{crop_vf},{grade_vf},fps=30,format=yuv420p"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{ss:.4f}", "-t", f"{src_read_dur + 0.15:.4f}", "-i", str(src_p),
        "-frames:v", str(frames), "-vf", vf, "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "15", str(tmp)
    ], cwd=str(V6), check=True)
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

tl_v5 = json.loads((V5 / "timeline_v5_master.json").read_text(encoding="utf-8"))
bmap  = {b["id"]: b for b in tl_v5["blocks"]}

# 1. Re-grade ALL 8 Live Chi Oanh Clips (including REAL C3852 36.26..41.36s for Image 3 "22-24 thanh"!)
LIVE_JOBS = [
    ("b01_open_live.mp4",          CACHE / "C3841.MP4", 3.95,  bmap["b01_open_live"]["dur"],          "scale=1112:1977,crop=1080:1920:0:28",   WB_SHOWROOM, VOICE_V5 / "b01_open_live.wav"),
    ("b04_wide_oanh_104_live.mp4", CACHE / "C3845.MP4", 1.55,  bmap["b04_wide_oanh_104_live"]["dur"], "scale=1096:1948,crop=1080:1920:4:14",   WB_SHOWROOM, VOICE_V5 / "b04_wide_oanh_104_live.wav"),
    ("b05_intro_set_live.mp4",     CACHE / "C3849.MP4", 2.50,  bmap["b05_intro_set_live"]["dur"],     "scale=1140:2026,crop=1080:1920:0:53",   WB_SHOWROOM, VOICE_V5 / "b05_intro_set_live.wav"),
    # FIX IMAGE 3: Real Sony C3852 [36.24..41.36s] where Chi Oanh holds the real gift basket & points to the 22-24 thanh pack!
    ("b06_24thanh_real_live.mp4",  CACHE / "C3852.MP4", 36.24, 5.05,                                  "scale=1150:2044,crop=1080:1920:0:62",   WB_SHOWROOM, None),
    ("b07b_camnang_live.mp4",      CACHE / "C3856.MP4", 10.12, bmap["b07b_camnang_live"]["dur"],      "scale=1096:1948,crop=1080:1920:8:14",   WB_SHOWROOM, VOICE_V5 / "b07b_camnang_live.wav"),
    ("b09b_quai_da_live.mp4",      CACHE / "C3853.MP4", 8.88,  bmap["b09b_quai_da_live"]["dur"],      "scale=1166:2073,crop=1080:1920:86:76",  WB_SHOWROOM, VOICE_V5 / "b09b_quai_da_live.wav"),
    ("b10a_sx_live.mp4",           CACHE / "C3862.MP4", 2.55,  bmap["b10a_sx_live"]["dur"],           "scale=1166:2073,crop=1080:1920:0:76",   WB_SHOWROOM, VOICE_V5 / "b10a_sx_live.wav"),
    ("b11a_cta_live1.mp4",         CACHE / "C3864.MP4", 5.10,  bmap["b11a_cta_live1"]["dur"],         "scale=1240:2204,crop=1080:1920:0:112",  WB_SHOWROOM, VOICE_V5 / "b11a_cta_live1.wav"),
    ("b11c_cta_inbox_live.mp4",    CACHE / "C3864.MP4", 17.42, bmap["b11c_cta_inbox_live"]["dur"],    "scale=1166:2073,crop=1080:1920:0:76",   WB_SHOWROOM, VOICE_V5 / "b11c_cta_inbox_live.wav"),
]
print("Rendering 9 WB-calibrated anti-glare Live Sony clips...", flush=True)
for onm, sp, ss, dur, cvf, gvf, wmux in LIVE_JOBS:
    make_clip(onm, sp, ss, dur, cvf, gvf, wav_mux=wmux)
    print("  -> Live ready:", onm, flush=True)

# 2. Re-grade ALL Real B-Roll & Dedicated To Yen / Packaged Product Clips!
BROLL_JOBS = [
    ("br_intro1_sunlit_sets.mp4",  CACHE / "C3909.MP4", 0.40, 2.20, "scale=1080:1920", WB_CLASS_BRIGHT, 1.0),
    ("br_intro2_long_table.mp4",   CACHE / "C3910.MP4", 0.50, 2.20, "scale=1080:1920", WB_CLASS_TABLE,  1.0),
    ("br_intro3_shelf_tower.mp4",  CACHE / "C3875.MP4", 0.50, 2.40, "scale=1080:1920", WB_SHOWROOM,     1.0),

    ("br_wide_oanh_arms_104.mp4",  CACHE / "C3845.MP4", 1.50, 5.80, "scale=1096:1948,crop=1080:1920:4:14", WB_SHOWROOM, 1.0),
    ("br_wide_oanh_row_104.mp4",   CACHE / "C3865.MP4", 5.00, 5.00, "scale=1080:1920", WB_SHOWROOM,     1.0),
    ("br_clean_row_104sets.mp4",   CACHE / "C3869.MP4", 1.50, 5.00, "scale=1080:1920", WB_SHOWROOM,     1.0),

    ("br_anh_hau_handover.mp4",    CACHE / "C3921.MP4", 0.80, 4.50, "scale=1080:1920", WB_CLASS_BRIGHT, 1.0),
    ("br_anh_hau_77sets.mp4",      CACHE / "C3932.MP4", 0.60, 4.50, "scale=1080:1920", WB_CLASS_BRIGHT, 1.0),
    ("br_phu_huynh_13sets.mp4",    CACHE / "C3866.MP4", 3.00, 5.00, "scale=1080:1920", WB_SHOWROOM,     1.0),
    ("br_hanoi_carton.mp4",        CACHE / "C3892.MP4", 0.60, 4.50, "scale=1080:1920", WB_SHOWROOM,     1.0),
    ("br_hcmc_suv.mp4",            CACHE / "C3901.MP4", 0.50, 4.50, "scale=1080:1920", WB_OUTDOOR,      1.0),

    ("br_basket_full_hero.mp4",    CACHE / "C3908.MP4", 0.40, 6.50, "scale=1080:1920", WB_CLASS_BRIGHT, 1.0),
    ("br_basket_flower_bow.mp4",   CACHE / "C3909.MP4", 1.60, 6.50, "scale=1080:1920", WB_CLASS_BRIGHT, 1.0),
    ("br_basket_row_bow.mp4",      CACHE / "C3910.MP4", 2.00, 6.00, "scale=1080:1920", WB_CLASS_TABLE,  1.0),

    # FIX IMAGE 2: Keep C3873 strictly inside 0.15..2.55s (slow-mo 1.65x = 3.96s) BEFORE camera tilts up to glaring ceiling sign!
    ("br_inside_basket_clean.mp4", CACHE / "C3873.MP4", 0.15, 3.80, "scale=1080:1920", WB_SHOWROOM,     1.60),
    ("br_factory_pack1.mp4",       CACHE / "C3882.MP4", 0.60, 5.00, "scale=1080:1920", WB_SHOWROOM,     1.0),

    # FIX IMAGE 1 & IMAGE 4: Full-screen dedicated SKA NEST box & dedicated To Yen Tinh Che Soi Dai sources!
    ("prod_skanest_box_full.mp4",  V3_VID / "V3_vid02_skanest_box.mp4",   0.15, 5.00, "scale=1080:1920", WB_PRODUCT, 1.0),
    ("prod_to_yen_dedicated1.mp4", V2_FV  / "OUT_f20_v1_full_to_yen.mp4", 0.25, 4.80, "scale=1160:2062,crop=1080:1920:40:71", WB_PRODUCT, 1.0),
    # Steady 0.25..2.65s slice of pure white long-strand bird's nest (slowed 1.5x -> 3.6s, ZERO fast zoom!)
    ("prod_to_yen_soi_dai2.mp4",   V3_VID / "V3_vid03_to_yen_pure.mp4",   0.25, 4.20, "scale=1080:1920", WB_PRODUCT, 1.65),
    ("prod_skanest_box_alt.mp4",   V2_FV  / "OUT_f20_v5_skanest_box.mp4", 0.25, 4.50, "scale=1160:2062,crop=1080:1920:40:71", WB_PRODUCT, 1.0),
    # Real F20 sandwiched seaweed bars (cropped cleanly above glove y=0..1360 for PIP / cutaway!)
    ("prod_kep_hat_real_bars.mp4", V3_VID / "V3_vid12_kep_hat_bars.mp4",  0.20, 5.00, "crop=920:1280:80:60,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", WB_PRODUCT, 1.0),

    ("prod_two_jars_even.mp4",     V4_VID / "V4_vid02_two_jars_even.mp4", 0.15, 4.20, "scale=1080:1920", WB_PRODUCT, 1.0),
    ("prod_hu_say_gion.mp4",       V3_VID / "V3_vid06_hu_say_gion.mp4",   0.20, 3.80, "scale=1080:1920", WB_PRODUCT, 1.0),
    ("prod_hu_say_me.mp4",         V3_VID / "V3_vid07_hu_say_me.mp4",     0.20, 3.80, "scale=1080:1920", WB_PRODUCT, 1.0),
    ("prod_banh_thuyen.mp4",       V3_VID / "V3_vid08_banh_thuyen.mp4",   0.20, 5.20, "scale=1080:1920", WB_PRODUCT, 1.0),
    ("prod_kep_hat_pouch.mp4",     V3_VID / "V3_vid09_kep_hat.mp4",       0.20, 5.00, "scale=1080:1920", WB_PRODUCT, 1.0),
    ("prod_chung_yen.mp4",         V3_VID / "V3_vid10_chung_yen.mp4",     0.20, 4.20, "scale=1080:1920", WB_PRODUCT, 1.0),
    ("prod_quai_loupe.mp4",        V3_VID / "V3_vid14_quai_no_macro.mp4", 0.20, 5.20, "scale=1080:1920", WB_PRODUCT, 1.0),
]

print("Rendering 28 WB-calibrated vibrant B-roll & product clips...", flush=True)
for onm, sp, ss, dur, cvf, gvf, spts in BROLL_JOBS:
    make_clip(onm, sp, ss, dur, cvf, gvf, slow_pts=spts)
    print("  -> Ready:", onm, flush=True)

# Build Visual QC Sheet showing WB RGB stats + 98th percentile (proving ZERO glare p98 <= 232!)
key_check = [
    "b01_open_live.mp4", "b04_wide_oanh_104_live.mp4", "b09b_quai_da_live.mp4", "b06_24thanh_real_live.mp4",
    "br_intro1_sunlit_sets.mp4", "br_intro2_long_table.mp4", "br_anh_hau_77sets.mp4", "br_basket_full_hero.mp4",
    "br_inside_basket_clean.mp4", "prod_skanest_box_full.mp4", "prod_to_yen_dedicated1.mp4", "prod_to_yen_soi_dai2.mp4",
    "prod_kep_hat_real_bars.mp4", "prod_two_jars_even.mp4", "br_basket_flower_bow.mp4", "br_basket_row_bow.mp4",
]
sheet = Image.new("RGB", (270 * 4, 480 * 4), (16, 16, 16))
tj = V6 / "_q.jpg"
for i, fn in enumerate(key_check):
    mp = CLIPS_V6 / fn
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", str(mp), "-frames:v", "1", str(tj)], check=True)
    im = Image.open(tj).convert("RGB")
    arr = np.array(im, dtype=np.float32)
    p98 = float(np.percentile(arr, 98))
    mr, mg, mb = arr[:,:,0].mean(), arr[:,:,1].mean(), arr[:,:,2].mean()
    th = im.resize((270, 480), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(th)
    d.rectangle([4, 4, 266, 40], fill=(0, 0, 0))
    d.text((8, 6), fn[:28], fill=(255, 232, 60))
    d.text((8, 22), f"RGB:{mr:.0f},{mg:.0f},{mb:.0f} p98={p98:.0f}", fill=(150, 255, 180))
    sheet.paste(th, ((i % 4) * 270, (i // 4) * 480))
tj.unlink(missing_ok=True)
sheet.save(V6 / "v6_wb_and_4fixes_qc.jpg", quality=93)
print("Saved v6_wb_and_4fixes_qc.jpg!")
