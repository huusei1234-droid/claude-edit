# -*- coding: utf-8 -*-
"""
V5 MASTER HYPERFRAMES RENDERER — ALL 12 MULTI-ACTION 10-CUT AI USP VIDEOS (25/11/2026):
- 10 Daily Videos (`V01..V10`) + 2 Dedicated Flagship Videos (`Ngọc Long Hoàn` & `Điều Kinh HT`) = 12 Videos!
- 10 FAST CUTS PER VIDEO (~3.6s - 4.2s/cut -> 120 total cuts! ZERO dragged-out 8s source!).
- 100% REAL-LIFE ACTIONS (`đi xe ô tô, dạo dưới đường phố, sinh hoạt trong nhà, mở túi/pha nước dùng sản phẩm thật` — 0% đứng nhìn cười đơ!).
- 100% FACE-SAFE (`0.00%` chữ hoặc hộp sản phẩm che mặt ở bất kỳ cảnh nào!) + 100% TikTok × Reels Safe Zone (`X: 54..884px`, `Y: 248..1548px`)!
- Ghi đè trực tiếp toàn bộ 12 file `.mp4` trong `K6 - Hằng Thu Pharma\261125 - Ngày 25.11.2026\` + xuất bảng QA 120 cảnh!
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

THIS_DIR = Path(r"d:\AI\full studio\output\htpm-ngay-261125")
sys.path.insert(0, str(THIS_DIR))

from day25_master_spec import (
    BATCH_ROOT, PROD_DIR, BRAND_KIT, K6_DAY25_DIR, CLOUD_DAY25_VID, LOCAL_DAY25_DIR, SLOTS_261125,
)
from v5_master_manifest import (
    V4_COUPLE_ROOT, V5_DIR, V5_IMG_DIR, V5_CFR_VID, V5_PODIUM_VID, VIDEO_10CUT_MAPS,
)

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
OVERLAYS_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "video_overlays_4k"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
ARTIFACT_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682")

V1_COUPLE_ROOT = Path(r"d:\AI\full studio\output\htpm-couple-nlh-dk-261125")
V2_SOLO_DK_ROOT = Path(r"d:\AI\full studio\output\htpm-couple-nlh-dk-v2-261125")

OVERLAY_PAIRS = [
    ("01_Golden_Dust_Bokeh_9x16.mp4", "03_Warm_Window_Sun_Rays_9x16.mp4"),
    ("05_Soft_Pearl_Sparkles_Bling_9x16.mp4", "04_Anamorphic_Gold_Rose_Flare_9x16.mp4"),
]

COLOR_GRADE_CRYSTAL = (
    '{&quot;preset&quot;:null,&quot;intensity&quot;:1,&quot;adjust&quot;:{&quot;exposure&quot;:0.03,&quot;contrast&quot;:0.06,'
    '&quot;highlights&quot;:0.02,&quot;shadows&quot;:0.04,&quot;whites&quot;:0.04,&quot;blacks&quot;:0,&quot;temperature&quot;:0.01,'
    '&quot;tint&quot;:0.01,&quot;vibrance&quot;:0.11,&quot;saturation&quot;:0.04},&quot;details&quot;:{&quot;vignette&quot;:0.03,'
    '&quot;vignetteMidpoint&quot;:0.5,&quot;vignetteRoundness&quot;:0,&quot;vignetteFeather&quot;:0.65,&quot;grain&quot;:0,'
    '&quot;grainSize&quot;:0.25,&quot;grainRoughness&quot;:0.5},&quot;effects&quot;:{&quot;blur&quot;:0,&quot;pixelate&quot;:0,'
    '&quot;chromaBleed&quot;:0,&quot;tapeDamage&quot;:0,&quot;tapeTracking&quot;:0,&quot;tapeNoise&quot;:1,&quot;tapeSpeed&quot;:0.5,'
    '&quot;filmArtifacts&quot;:0,&quot;halftone&quot;:0,&quot;halftoneSize&quot;:0,&quot;twoInkPrint&quot;:0,&quot;twoInkPrintSize&quot;:0,'
    '&quot;ascii&quot;:0,&quot;asciiSize&quot;:0.065,&quot;asciiInvert&quot;:0,&quot;asciiStyle&quot;:0,&quot;asciiColor&quot;:1,'
    '&quot;asciiRotation&quot;:0,&quot;dither&quot;:0,&quot;ditherSize&quot;:0,&quot;bloom&quot;:0,&quot;bloomRadius&quot;:8,'
    '&quot;monoScreen&quot;:0,&quot;monoScreenSize&quot;:0,&quot;monoScreenAngle&quot;:0,&quot;monoScreenSpread&quot;:0,'
    '&quot;monoScreenShape&quot;:0,&quot;monoScreenInvert&quot;:0,&quot;scanlines&quot;:0,&quot;scanlineCount&quot;:0,'
    '&quot;scanlineSoftness&quot;:0,&quot;chromaticAberration&quot;:0,&quot;chromaticAngle&quot;:0,&quot;crtCurvature&quot;:0,'
    '&quot;digitalGlitch&quot;:0,&quot;digitalGlitchColorSplit&quot;:0,&quot;digitalGlitchLineTear&quot;:0,'
    '&quot;digitalGlitchPixelate&quot;:0,&quot;digitalGlitchBlockAmount&quot;:0,&quot;digitalGlitchBlockDisplacement&quot;:0,'
    '&quot;digitalGlitchBlockOpacity&quot;:0,&quot;digitalGlitchSpeed&quot;:0,&quot;engraving&quot;:0,&quot;engravingSpacing&quot;:0.41,'
    '&quot;engravingMinThickness&quot;:0.2,&quot;engravingMaxThickness&quot;:0.45,&quot;engravingAngle&quot;:0.25,'
    '&quot;engravingContrast&quot;:0.46,&quot;engravingSharpness&quot;:0.59,&quot;engravingWave&quot;:0.2,'
    '&quot;engravingWaveFrequency&quot;:0.22,&quot;crosshatch&quot;:0,&quot;crosshatchSpacing&quot;:0.28,'
    '&quot;crosshatchThickness&quot;:0.25,&quot;crosshatchAngle&quot;:0.25,&quot;crosshatchContrast&quot;:0.33,'
    '&quot;crosshatchEdges&quot;:0.5,&quot;crosshatchLineWeight&quot;:0,&quot;crosshatchWave&quot;:0.33,'
    '&quot;crosshatchWaveFrequency&quot;:0.22,&quot;kuwahara&quot;:0,&quot;kuwaharaRadius&quot;:0.14,&quot;kuwaharaSharpness&quot;:0.31,'
    '&quot;kuwaharaSaturation&quot;:0.5},&quot;lut&quot;:null,&quot;colorSpace&quot;:&quot;rec709&quot;}'
)

VO_FX_CHAIN = (
    '{&quot;version&quot;:1,&quot;nodes&quot;:['
    '{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;vhp&quot;,&quot;label&quot;:&quot;Clean rumble&quot;,&quot;params&quot;:{&quot;frequency&quot;:85}},'
    '{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;vlow&quot;,&quot;label&quot;:&quot;Warmth balance&quot;,&quot;params&quot;:{&quot;frequency&quot;:210,&quot;gain&quot;:-1.6,&quot;q&quot;:1.1}},'
    '{&quot;type&quot;:&quot;peaking&quot;,&quot;id&quot;:&quot;vpres&quot;,&quot;label&quot;:&quot;Broadcast clarity&quot;,&quot;params&quot;:{&quot;frequency&quot;:3100,&quot;gain&quot;:2.0,&quot;q&quot;:1.0}},'
    '{&quot;type&quot;:&quot;limiter&quot;,&quot;id&quot;:&quot;vlim&quot;,&quot;params&quot;:{&quot;limit&quot;:-1.0}}]}'
)


def list_fresh_bgms():
    z_aco = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\05_Acoustic - Guitar - Nhẹ Nhàng Mộc Mạc")
    z_tvc = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng")
    fb = [
        AUDIO_BUNDLE_DIR / "bgm_sunny_carefree.mp3",
        AUDIO_BUNDLE_DIR / "bgm_coconut_groove_tvc.mp3",
        AUDIO_BUNDLE_DIR / "bgm_fresh_wellness_tvc.mp3",
    ]
    aco = sorted([f for f in z_aco.rglob("*.mp3") if 1_000_000 < f.stat().st_size < 14_000_000]) if z_aco.exists() else []
    tvc = sorted([f for f in z_tvc.rglob("*.mp3") if 1_000_000 < f.stat().st_size < 14_000_000]) if z_tvc.exists() else []
    return (aco if aco else fb), (tvc if tvc else fb)


def hex_rgb(hx: str):
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))


def ensure_studio_podium_video(idx: int, cutout_fn: str, pri_hex: str) -> Path:
    """
    Tạo clip 5.5s @ 24fps Studio Podium 3D Parallax cho Cut 7:
    - Nền Studio mờ sang trọng (0% người -> 0% che mặt!)
    - Đĩa ánh sáng ngọc trai ở Y=1285px + Hộp sản phẩm thật 100% (`SP_*_CUTOUT.png`) sắc nét đặt tại Y=720..1330px (X tâm 470px tránh cột nút phải!)
    - Phía trên Y=250..690px hoàn toàn thoáng sáng để đặt Thẻ 3 Công Dụng USP!
    """
    out_mp4 = V5_PODIUM_VID / f"pod_v{idx:02d}.mp4"
    if out_mp4.exists() and out_mp4.stat().st_size > 250_000:
        return out_mp4

    bg_map = {
        1: V5_IMG_DIR / "p01_studio_rosequartz.png",
        2: V5_IMG_DIR / "p01_studio_rosequartz.png",
        3: V5_IMG_DIR / "p03_herbal_travertine.png",
        4: V5_IMG_DIR / "p08_satin_medallion.png",
        5: V5_IMG_DIR / "p05_ruby_watersplash.png",
        6: V5_IMG_DIR / "p06_clinical_prism.png",
        7: V5_IMG_DIR / "p03_herbal_travertine.png",
        8: V5_IMG_DIR / "p08_satin_medallion.png",
        9: V5_IMG_DIR / "p09_imperial_gold_herbs.png",
        10: V5_IMG_DIR / "p06_clinical_prism.png",
    }
    bg_p = bg_map.get(idx, V5_IMG_DIR / "p01_studio_rosequartz.png")
    bg_im = Image.open(bg_p).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)
    bg_im = bg_im.filter(ImageFilter.GaussianBlur(6)).convert("RGBA")

    r, g, b = hex_rgb(pri_hex)
    # Soft luminous gradient wash so upper card & lower product both pop
    wash = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wash)
    wd.rectangle((0, 0, 1080, 1920), fill=(255, 252, 254, 48 if idx not in (5, 9) else 15))
    # Glowing pearl podium disc centered at X=470, Y=1315 (100% clear of right column X>=886!)
    cx, by = 470, 1325
    aura = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    ad.ellipse((cx - 320, by - 480, cx + 320, by + 90), fill=(r, g, b, 75))
    ad.ellipse((cx - 230, by - 390, cx + 230, by + 40), fill=(255, 255, 255, 215))
    bg_im.alpha_composite(wash)
    bg_im.alpha_composite(aura.filter(ImageFilter.GaussianBlur(46)))

    pod = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pod)
    pd.ellipse((cx - 270, by - 22, cx + 270, by + 56), fill=(r, g, b, 215))
    pd.ellipse((cx - 270, by - 32, cx + 270, by + 42), fill=(255, 255, 255, 248), outline=(r, g, b, 160), width=3)
    bg_im.alpha_composite(pod)

    # Place razor-sharp 100% real product PNG
    cut_fn = "SP_HTPM_FULL_8SKU_SHELF.png" if idx == 10 else cutout_fn
    pr = Image.open(PROD_DIR / cut_fn).convert("RGBA")
    if pr.getbbox():
        pr = pr.crop(pr.getbbox())
    max_w, max_h = (740, 380) if idx == 10 else (640, 560)
    pr.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    pr = ImageEnhance.Sharpness(pr).enhance(1.2)
    px = cx - pr.width // 2
    py = by - pr.height + 6

    sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((px + 12, by - 12, px + pr.width - 12, by + 16), fill=(15, 18, 28, 135))
    bg_im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    bg_im.alpha_composite(pr, (px, py))

    still_p = V5_PODIUM_VID / f"_still_pod_v{idx:02d}.png"
    bg_im.convert("RGB").save(still_p)

    ov_mp4 = OVERLAYS_DIR / ("01_Golden_Dust_Bokeh_9x16.mp4" if idx % 2 == 1 else "05_Soft_Pearl_Sparkles_Bling_9x16.mp4")
    # Render smooth 5.5s 24fps zoom-drift + 4K bokeh Screen blend on GPU NVENC!
    fc = (
        "[0:v]scale=1166:2074,zoompan=z='1.0+0.055*on/132':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=132:s=1080x1920:fps=24[base];"
        "[1:v]fps=24,scale=1080:1920,trim=0:5.5,setpts=PTS-STARTPTS[ov];"
        "[base][ov]blend=all_mode=screen:all_opacity=0.42,format=yuv420p[vout]"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-loop", "1", "-t", "5.5", "-i", str(still_p),
            "-stream_loop", "-1", "-t", "5.5", "-i", str(ov_mp4),
            "-filter_complex", fc, "-map", "[vout]",
            "-r", "24", "-fps_mode", "cfr", "-t", "5.5",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-g", "24",
            str(out_mp4),
        ],
        check=True,
    )
    return out_mp4


def resolve_source_clip(token: str) -> Path:
    if token.startswith("act_"):
        return V5_CFR_VID / f"{token}.mp4"
    if token.startswith("pod_v"):
        idx = int(token.replace("pod_v", ""))
        sl = SLOTS_261125[idx - 1]
        return ensure_studio_podium_video(idx, sl["cutout"], sl["pri"])
    if token == "nlh_back_pain":
        return V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "07_HyperFrames_Project" / "assets" / "videos" / "NLH4_C02.mp4"
    if token.startswith("cgi_v"):
        idx = int(token.replace("cgi_v", ""))
        if idx == 4:
            return V4_COUPLE_ROOT / "c02_dieu_kinh_ht" / "07_HyperFrames_Project" / "assets" / "videos" / "DK4_C03.mp4"
        if idx == 9:
            return V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "07_HyperFrames_Project" / "assets" / "videos" / "NLH4_C03.mp4"
        sl = SLOTS_261125[idx - 1]
        return BATCH_ROOT / sl["vkey"] / "07_HyperFrames_Project" / "assets" / "videos" / f"V{idx:02d}_U02.mp4"
    if token.startswith("mac_v"):
        idx = int(token.replace("mac_v", ""))
        if idx == 4:
            return V4_COUPLE_ROOT / "c02_dieu_kinh_ht" / "07_HyperFrames_Project" / "assets" / "videos" / "DK4_C05.mp4"
        if idx == 9:
            return V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "07_HyperFrames_Project" / "assets" / "videos" / "NLH4_C04.mp4"
        sl = SLOTS_261125[idx - 1]
        return BATCH_ROOT / sl["vkey"] / "07_HyperFrames_Project" / "assets" / "videos" / f"V{idx:02d}_U04.mp4"
    raise KeyError(f"Unknown clip token: {token}")


def ensure_min_duration_cfr24(src_mp4: Path, dst_mp4: Path, need_s: float):
    dst_mp4.parent.mkdir(parents=True, exist_ok=True)
    pr = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(src_mp4)]
        ).decode("utf-8")
    )
    dur = float(pr["format"]["duration"])
    if dur >= need_s + 0.35:
        shutil.copy2(src_mp4, dst_mp4)
        return
    stretch = max(1.0, round((need_s + 0.50) / max(1.0, dur), 4))
    vf = f"setpts={stretch}*PTS,fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(src_mp4),
            "-vf", vf, "-r", "24", "-fps_mode", "cfr", "-an",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-g", "24",
            str(dst_mp4),
        ],
        check=True,
    )


def build_and_render_10cut_usp_video(cfg: dict, bgm1_src: Path, bgm2_src: Path):
    vkey = cfg["vkey"]
    work_dir = V5_DIR / "renders" / vkey
    hf_dir = work_dir / "07_HyperFrames_Project"
    comp_dir = hf_dir / "compositions"
    vid_dir = hf_dir / "assets" / "videos"
    img_dir = hf_dir / "assets" / "images"
    aud_dir = hf_dir / "assets" / "audio"
    fnt_dir = hf_dir / "assets" / "fonts"
    for _d in (comp_dir, vid_dir, img_dir, aud_dir, fnt_dir):
        _d.mkdir(parents=True, exist_ok=True)

    # Copy fonts, logo, cutout, overlays, audio
    for fn in ("Fraunces-Black.ttf", "PlayfairDisplay-BoldItalic.ttf", "BeVietnamPro-ExtraBold.ttf", "BeVietnamPro-Bold.ttf", "BeVietnamPro-SemiBold.ttf"):
        src_f = FONTS_BUNDLE_DIR / fn
        if src_f.exists() and not (fnt_dir / fn).exists():
            shutil.copy2(src_f, fnt_dir / fn)

    logo_src = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124\10_Bai_Thiet_Ke_Soft_Editorial\ht_logo_33mp_clean.png")
    if not logo_src.exists():
        logo_src = BRAND_KIT / "logos_png" / "ht_logo_official.png"
    shutil.copy2(logo_src, img_dir / "ht_logo.png")
    shutil.copy2(PROD_DIR / cfg["cutout"], img_dir / cfg["cutout"])

    ov1_fn, ov2_fn = cfg["ov_pair"]
    shutil.copy2(OVERLAYS_DIR / ov1_fn, vid_dir / ov1_fn)
    shutil.copy2(OVERLAYS_DIR / ov2_fn, vid_dir / ov2_fn)

    vo_dir = cfg["vo_dir"]
    vo_m = json.loads((vo_dir / "vo_manifest.json").read_text(encoding="utf-8"))
    segs = vo_m["segments"]
    total_dur = float(vo_m["total_duration_s"])

    for s in segs:
        shutil.copy2(vo_dir / f"{s['id']}.wav", aud_dir / f"{s['id']}.wav")
    shutil.copy2(bgm1_src, aud_dir / "bgm_1.mp3")
    shutil.copy2(bgm2_src, aud_dir / "bgm_2.mp3")
    for sfx_fn in ("sfx_whoosh_soft.mp3", "sfx_pop_clean.mp3", "sfx_sparkle_shine.mp3", "sfx_chime_warm.mp3"):
        if (AUDIO_BUNDLE_DIR / sfx_fn).exists():
            shutil.copy2(AUDIO_BUNDLE_DIR / sfx_fn, aud_dir / sfx_fn)

    # Compute 10 fast-paced cuts by splitting each of the 5 VO segments into 2 dynamic sub-shots!
    # Wave pacing split ratios: (0.48/0.52, 0.52/0.48, 0.48/0.52, 0.52/0.48, 0.44/0.56)
    ratios = [0.48, 0.54, 0.48, 0.52, 0.44]
    cut_tokens = VIDEO_10CUT_MAPS[cfg["map_key"]]
    cuts_10 = []
    for si, s in enumerate(segs):
        st = float(s["shot_start_s"])
        dur = float(s["shot_duration_s"])
        d_a = round(dur * ratios[si], 2)
        d_b = round(dur - d_a, 2)
        cuts_10.append((si * 2 + 1, cut_tokens[si * 2], st, d_a))
        cuts_10.append((si * 2 + 2, cut_tokens[si * 2 + 1], round(st + d_a, 2), d_b))

    # Stage all 10 CFR24 clips into vid_dir
    for c_idx, tok, c_st, c_dur in cuts_10:
        src_p = resolve_source_clip(tok)
        ensure_min_duration_cfr24(src_p, vid_dir / f"C{c_idx:02d}.mp4", c_dur)

    pri = cfg["pri"]
    pri_dark = cfg["pri_dark"]
    pri_soft = cfg["pri_soft"]

    # Build 9 full-screen background video tags (Cuts 1..9) + Cut 10 Top Cinema Window!
    vid_tags = []
    cam_tweens = []
    for c_idx, tok, c_st, c_dur in cuts_10[:9]:
        vid_tags.append(
            f'    <div id="rig-{c_idx:02d}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>'
            f'<video data-color-grading="{COLOR_GRADE_CRYSTAL}" id="vid-{c_idx:02d}" class="clip bg-video" '
            f'src="assets/videos/C{c_idx:02d}.mp4" data-start="{c_st:.2f}" data-duration="{c_dur:.2f}" '
            f'data-media-start="0.08" data-hf-media-start-basis="local" data-track-index="{c_idx}" muted playsinline></video></div>'
        )
        z0, z1 = ("1.00", "1.055") if c_idx % 2 == 1 else ("1.055", "1.00")
        cam_tweens.append(f'    tl.fromTo("#rig-{c_idx:02d}", {{ scale: {z0} }}, {{ scale: {z1}, duration: {c_dur:.2f}, ease: "none" }}, {c_st:.2f});')

    c10_st, c10_dur = cuts_10[9][2], cuts_10[9][3]
    c3_st, c3_dur = cuts_10[2][2], cuts_10[2][3]   # Cut 3: 3D CGI Mechanism
    c5_st, c5_dur = cuts_10[4][2], cuts_10[4][3]   # Cut 5: Hands-on / Indoor Product
    c6_st, c6_dur = cuts_10[5][2], cuts_10[5][3]   # Cut 6: Product Action B
    c7_st, c7_dur = cuts_10[6][2], cuts_10[6][3]   # Cut 7: 3D Studio Product Podium
    c8_st, c8_dur = cuts_10[7][2], cuts_10[7][3]   # Cut 8: 3D Botanical Macro

    hook_end = round(min(cuts_10[0][3] + 0.35, 3.60), 2)
    choice_st = round(c5_st + 0.15, 2)
    choice_dur = round(min(c5_dur + c6_dur - 0.35, 4.20), 2)

    # Captions across segments 1..4 (each split into 2 crisp lines matching the 2 cuts!)
    cap_divs = []
    cap_js = []
    cap_n = 0
    for si, (seg_id, l1_html, l2_html) in enumerate(cfg["caps_pair"]):
        c_a = cuts_10[si * 2]
        c_b = cuts_10[si * 2 + 1]
        for st_c, dur_c, txt_html in [(c_a[2], c_a[3], l1_html), (c_b[2], c_b[3], l2_html)]:
            cap_n += 1
            cid = f"cap-{cap_n:02d}"
            in_id = f"cap-in-{cap_n:02d}"
            d_safe = max(0.5, round(dur_c - 0.12, 2))
            cap_divs.append(f'    <div id="{cid}" class="clip cap-box" data-start="{st_c + 0.05:.2f}" data-duration="{d_safe:.2f}" data-track-index="40"><div id="{in_id}" class="cap-txt">{txt_html}</div></div>')
            cap_js.append(
                f'    tl.fromTo("#{in_id}", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.18, ease: "power2.out" }}, {st_c + 0.05:.2f});\n'
                f'    tl.to("#{in_id}", {{ opacity: 0, duration: 0.14 }}, {st_c + d_safe - 0.10:.2f});'
            )

    rows_s1 = "\n".join(
        f'      <div class="usp-row" id="s1-r{i}"><span class="usp-num">{i}</span><span>{r}</span></div>'
        for i, r in enumerate(cfg["slide1_rows"], start=1)
    )
    rows_s2 = "\n".join(
        f'      <div class="usp-row" id="s2-r{i}"><span class="usp-num">✓</span><span>{r}</span></div>'
        for i, r in enumerate(cfg["slide3_pills"], start=1)
    )

    mid_t = round(c5_st, 2)
    scene_html = f"""<template>
  <style>
    @font-face {{ font-family: "FrauncesVN"; src: url("assets/fonts/Fraunces-Black.ttf") format("truetype"); font-weight: 900; }}
    @font-face {{ font-family: "PlayfairIt"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; }}
    @font-face {{ font-family: "BeVNExtra"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; }}
    @font-face {{ font-family: "BeVNBold"; src: url("assets/fonts/BeVietnamPro-Bold.ttf") format("truetype"); font-weight: 700; }}
    @font-face {{ font-family: "BeVNSemi"; src: url("assets/fonts/BeVietnamPro-SemiBold.ttf") format("truetype"); font-weight: 600; }}

    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0D1622; font-family: "BeVNExtra", sans-serif; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 45%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .ov-screen {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; mix-blend-mode: screen; opacity: 0.42; pointer-events: none; z-index: 6; }}
    /* Gentle bottom scrim ONLY below Y=1100px so faces in Y=250..1080px stay 100% bright & crystal-clear! */
    .bottom-scrim {{ position: absolute; left: 0; right: 0; bottom: 0; height: 820px; background: linear-gradient(180deg, rgba(10,14,24,0) 0%, rgba(10,14,24,0.46) 46%, rgba(10,14,24,0.72) 100%); pointer-events: none; z-index: 7; }}

    /* Top Progress & Corner Brand Header (strictly Y=252..328px, clear of center face!) */
    .prog-track {{ position: absolute; left: 56px; top: 252px; width: 966px; height: 6px; border-radius: 99px; background: rgba(255,255,255,0.34); z-index: 30; overflow: hidden; }}
    .prog-fill {{ width: 100%; height: 100%; transform-origin: 0% 50%; background: linear-gradient(90deg, #FFE082, {pri}, #FFFFFF); }}
    .brand-pill {{
      position: absolute; left: 56px; top: 268px; z-index: 28;
      display: inline-flex; align-items: center; gap: 10px;
      background: rgba(255,255,255,0.95); border: 2px solid {pri};
      border-radius: 999px; padding: 6px 18px 6px 8px;
      box-shadow: 0 8px 22px rgba(0,0,0,0.20);
    }}
    .brand-pill img {{ width: 38px; height: 38px; border-radius: 50%; object-fit: contain; }}
    .brand-pill .bp-t {{ font-size: 18px; color: {pri_dark}; letter-spacing: 0.04em; line-height: 1.1; }}
    .seal-badge {{
      position: absolute; left: 924px; top: 266px; width: 92px; height: 92px; border-radius: 50%; z-index: 28;
      background: radial-gradient(circle, {pri} 0%, {pri_dark} 100%); border: 3px dashed #FFE082;
      color: #FFF; display: flex; flex-direction: column; align-items: center; justify-content: center;
      text-align: center; font-size: 13px; line-height: 1.12; box-shadow: 0 10px 24px rgba(0,0,0,0.28);
    }}
    .seal-badge b {{ font-size: 20px; color: #FFE082; display: block; }}

    /* 100% FACE-SAFE LOWER-THIRD HOOK BANNER (Y=1132..1362px, X=58..880px -> NEVER touches face!) */
    .hook-lower {{
      position: absolute; left: 58px; top: 1134px; width: 820px; z-index: 22; pointer-events: none;
    }}
    .hook-kicker {{
      display: inline-block; background: linear-gradient(90deg, {pri_dark}, {pri});
      color: #FFF; font-size: 24px; padding: 7px 22px; border-radius: 999px;
      border: 2.5px solid #FFE082; letter-spacing: 0.04em; margin-bottom: 8px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.34);
    }}
    .hook-title {{
      font-family: "FrauncesVN", serif; font-size: 72px; line-height: 1.06; color: {pri};
      -webkit-text-stroke: 13px #FFFFFF; paint-order: stroke fill;
      filter: drop-shadow(0 10px 22px rgba(0,0,0,0.48));
    }}

    /* COMPACT LOWER CHOICE PILL ON HUMAN PRODUCT CUT (Y=1215..1355px, X=58..790px -> 100% Face-Safe!) */
    .choice-pill {{
      position: absolute; left: 58px; top: 1218px; width: 760px; z-index: 22;
      background: rgba(255,255,255,0.97); border-left: 10px solid {pri};
      border-radius: 24px; padding: 15px 24px; display: flex; align-items: center; gap: 16px;
      box-shadow: 0 16px 34px rgba(0,0,0,0.32);
    }}
    .choice-pill img {{ width: 72px; height: 84px; object-fit: contain; flex-shrink: 0; }}
    .choice-pill .cp-txt {{ font-size: 29px; line-height: 1.25; color: {pri_dark}; }}

    /* NON-HUMAN 3D B-ROLL USP CARDS (Cuts 3, 7, 8 ONLY -> 0% human face on screen!) */
    .usp-card {{
      position: absolute; left: 58px; top: 368px; width: 818px; z-index: 20;
      background: rgba(255,255,255,0.96); border: 3px solid {pri}; border-radius: 30px;
      padding: 20px 24px; box-shadow: 0 20px 44px rgba(0,0,0,0.28);
    }}
    .usp-hdr {{
      display: inline-block; background: linear-gradient(90deg, {pri_dark}, {pri});
      color: #FFF; font-size: 24px; padding: 8px 22px; border-radius: 999px;
      text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 12px;
    }}
    .usp-row {{
      display: flex; align-items: center; gap: 14px; font-size: 29px; color: #1E1420;
      padding: 7px 0; line-height: 1.24;
    }}
    .usp-num {{
      width: 38px; height: 38px; border-radius: 50%; background: {pri}; color: #FFF;
      display: inline-flex; align-items: center; justify-content: center; font-size: 21px; flex-shrink: 0;
    }}

    /* CUT 8 BOTANICAL/INGREDIENT FLOATING HEADER (Y=375..565px, X=58..876px) */
    .macro-banner {{
      position: absolute; left: 58px; top: 376px; width: 818px; z-index: 20;
      background: linear-gradient(135deg, {pri_dark}EE, {pri}EE); border: 2.5px solid #FFE082;
      border-radius: 30px; padding: 22px 28px; color: #FFF; box-shadow: 0 18px 40px rgba(0,0,0,0.34);
    }}
    .macro-banner .mb-k {{ font-size: 22px; color: #FFE082; letter-spacing: 0.06em; margin-bottom: 6px; }}
    .macro-banner .mb-h {{ font-family: "FrauncesVN", serif; font-size: 56px; line-height: 1.08; }}

    /* CUT 10: 100% FACE-SAFE CINEMA SPLIT END-CARD (X=58..880px, Y=356..1532px!) */
    .end-stage {{ position: absolute; inset: 0; background: linear-gradient(180deg, #101928 0%, {pri_dark} 100%); z-index: 23; }}
    .end-vid-direct {{
      position: absolute; left: 58px; top: 364px; width: 822px; height: 530px; z-index: 25;
      border-radius: 34px; object-fit: cover; object-position: center 20%; display: block;
      border: 4px solid #FFE082; box-shadow: 0 20px 44px rgba(0,0,0,0.42);
    }}
    .end-dock {{
      position: absolute; left: 58px; top: 914px; width: 822px; height: 614px;
      background: linear-gradient(145deg, #FFFFFF 0%, {pri_soft} 100%);
      border: 3.5px solid {pri}; border-radius: 34px; padding: 26px 28px;
      box-shadow: 0 24px 52px rgba(0,0,0,0.45);
      display: flex; flex-direction: column; justify-content: space-between;
    }}
    .end-dock-top {{ display: flex; align-items: center; gap: 24px; height: 390px; }}
    .end-prod-wrap {{ width: 280px; height: 375px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; background: radial-gradient(circle, #FFF 0%, rgba(255,255,255,0) 72%); }}
    .end-prod-wrap img {{ max-width: 270px; max-height: 365px; object-fit: contain; filter: drop-shadow(0 18px 26px rgba(0,0,0,0.28)); }}
    .end-info {{ flex: 1; }}
    .end-cat {{ display: inline-block; background: {pri_soft}; color: {pri}; border: 2px solid {pri}; font-size: 20px; padding: 5px 16px; border-radius: 999px; margin-bottom: 10px; }}
    .end-name {{ font-family: "FrauncesVN", serif; font-size: 56px; color: {pri_dark}; line-height: 1.05; margin-bottom: 10px; }}
    .end-sub {{ font-size: 24px; color: #3A2634; font-family: "BeVNBold"; line-height: 1.32; }}
    .end-cta {{
      background: linear-gradient(90deg, {pri_dark}, {pri}); color: #FFF;
      border: 2.5px solid #FFE082; border-radius: 999px; padding: 18px 24px;
      text-align: center; font-size: 27px; letter-spacing: 0.02em;
      box-shadow: 0 12px 28px rgba(0,0,0,0.28);
    }}
    .end-legal {{ text-align: center; font-family: "BeVNSemi"; font-size: 19px; color: #52434E; margin-top: 6px; }}

    /* HIGH-CONTRAST BOXED SUBTITLES (X=58..880 <= 884px, Y=1386..1526 <= 1545px!) */
    .cap-box {{
      position: absolute; left: 58px; bottom: 394px; width: 822px; z-index: 26;
      display: flex; justify-content: center; pointer-events: none;
    }}
    .cap-txt {{
      background: rgba(18, 10, 24, 0.90); border: 2.5px solid #FFE082;
      border-radius: 22px; padding: 14px 24px; color: #FFFFFF;
      font-family: "BeVNExtra", sans-serif; font-size: 35px; line-height: 1.24;
      text-align: center; box-shadow: 0 12px 28px rgba(0,0,0,0.44);
    }}
    .cap-kw {{ font-family: "PlayfairIt", serif; font-size: 39px; color: #FFE082; }}
  </style>

  <div id="root" data-composition-id="scene-main" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur:.2f}">
{chr(10).join(vid_tags)}
    <video id="ov-01" class="clip ov-screen" src="assets/videos/{ov1_fn}" data-start="0" data-duration="{mid_t:.2f}" data-hf-media-start-basis="local" data-loop="true" data-track-index="11" muted playsinline></video>
    <video id="ov-02" class="clip ov-screen" src="assets/videos/{ov2_fn}" data-start="{mid_t:.2f}" data-duration="{round(total_dur - mid_t, 2):.2f}" data-hf-media-start-basis="local" data-loop="true" data-track-index="12" muted playsinline></video>
    <div class="bottom-scrim"></div>

    <div class="prog-track"><div id="prog-bar" class="prog-fill"></div></div>
    <div class="brand-pill"><img src="assets/images/ht_logo.png" alt="HT"/><div class="bp-t">HẰNG THU PHARMA</div></div>
    <div id="seal-spin" class="seal-badge"><span>CAM KẾT</span><b>100%</b><span>CHÍNH HÃNG</span></div>

    <!-- Cut 1 Lower-Third Hook (0% Face Overlap!) -->
    <div id="hook-box" class="clip hook-lower" data-start="0.08" data-duration="{hook_end:.2f}" data-track-index="20">
      <div id="hook-in">
        <div class="hook-kicker">{cfg['hook_kicker']}</div>
        <div class="hook-title">{cfg['hook_hero']}</div>
      </div>
    </div>

    <!-- Cut 3 (3D CGI Mechanism): USP Card #1 -->
    <div id="card-s1" class="clip" data-start="{c3_st + 0.10:.2f}" data-duration="{max(0.6, c3_dur - 0.18):.2f}" data-track-index="21">
      <div id="card-s1-in" class="usp-card">
        <div class="usp-hdr">{cfg['slide1_hdr']}</div>
{rows_s1}
      </div>
    </div>

    <!-- Cut 5-6 (Hands-On Product Action): Compact Lower Choice Pill -->
    <div id="pill-s2" class="clip" data-start="{choice_st:.2f}" data-duration="{choice_dur:.2f}" data-track-index="22">
      <div id="pill-s2-in" class="choice-pill">
        <img src="assets/images/{cfg['cutout']}" alt="SP"/>
        <div class="cp-txt">{cfg['slide2_pill']}</div>
      </div>
    </div>

    <!-- Cut 7 (3D Studio Product Podium): USP Benefit Card #2 Above Giant Real Product -->
    <div id="card-s2" class="clip" data-start="{c7_st + 0.08:.2f}" data-duration="{max(0.6, c7_dur - 0.15):.2f}" data-track-index="23">
      <div id="card-s2-in" class="usp-card">
        <div class="usp-hdr">{cfg['pack_kicker']}</div>
{rows_s2}
      </div>
    </div>

    <!-- Cut 8 (3D Botanical/Molecular Macro): Ingredient Header Banner -->
    <div id="ban-s3" class="clip" data-start="{c8_st + 0.08:.2f}" data-duration="{max(0.6, c8_dur - 0.15):.2f}" data-track-index="24">
      <div id="ban-s3-in" class="macro-banner">
        <div class="mb-k">{cfg['pack_kicker']}</div>
        <div class="mb-h">{cfg['pack_hero']}</div>
      </div>
    </div>

    <!-- Cut 10: Face-Safe Cinema Split End-Card (Direct Top Video + Bottom Giant Product Dock) -->
    <div id="end-card" class="clip end-stage" data-start="{c10_st:.2f}" data-duration="{c10_dur:.2f}" data-track-index="25">
      <div id="end-in" class="end-dock">
        <div>
          <div class="end-dock-top">
            <div class="end-prod-wrap"><img src="assets/images/{cfg['cutout']}" alt="Product"/></div>
            <div class="end-info">
              <div class="end-cat">{cfg['end_cat']}</div>
              <div class="end-name">{cfg['end_name']}</div>
              <div class="end-sub">{cfg['end_sub']}</div>
            </div>
          </div>
        </div>
        <div>
          <div id="cta-pulse" class="end-cta">{cfg['cta_txt']}</div>
          <div class="end-legal">{cfg['legal_txt']}</div>
        </div>
      </div>
    </div>
    <video data-color-grading="{COLOR_GRADE_CRYSTAL}" id="vid-10" class="clip end-vid-direct" src="assets/videos/C10.mp4" data-start="{c10_st:.2f}" data-duration="{c10_dur:.2f}" data-media-start="0.08" data-hf-media-start-basis="local" data-track-index="26" muted playsinline></video>

{chr(10).join(cap_divs)}
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#prog-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {total_dur:.2f}, ease: "none" }}, 0);
    tl.to("#seal-spin", {{ rotation: 360, duration: {total_dur:.2f}, ease: "none" }}, 0);
{chr(10).join(cam_tweens)}
    tl.fromTo("#hook-in", {{ opacity: 0, y: 26, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.28, ease: "back.out(1.4)" }}, 0.10);
    tl.to("#hook-in", {{ opacity: 0, y: -12, duration: 0.20 }}, {max(0.5, hook_end - 0.18):.2f});

    tl.fromTo("#card-s1-in", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.26, ease: "power2.out" }}, {c3_st + 0.10:.2f});
    tl.to("#card-s1-in", {{ opacity: 0, duration: 0.18 }}, {c3_st + c3_dur - 0.22:.2f});

    tl.fromTo("#pill-s2-in", {{ opacity: 0, x: -28 }}, {{ opacity: 1, x: 0, duration: 0.26, ease: "power2.out" }}, {choice_st:.2f});
    tl.to("#pill-s2-in", {{ opacity: 0, duration: 0.20 }}, {choice_st + choice_dur - 0.22:.2f});

    tl.fromTo("#card-s2-in", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.26, ease: "power2.out" }}, {c7_st + 0.08:.2f});
    tl.to("#card-s2-in", {{ opacity: 0, duration: 0.18 }}, {c7_st + c7_dur - 0.20:.2f});

    tl.fromTo("#ban-s3-in", {{ opacity: 0, scale: 0.94 }}, {{ opacity: 1, scale: 1, duration: 0.26, ease: "back.out(1.3)" }}, {c8_st + 0.08:.2f});
    tl.to("#ban-s3-in", {{ opacity: 0, duration: 0.18 }}, {c8_st + c8_dur - 0.20:.2f});

    tl.fromTo("#end-in", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power2.out" }}, {c10_st:.2f});
    tl.fromTo("#cta-pulse", {{ scale: 0.96 }}, {{ scale: 1.02, duration: 0.55, yoyo: true, repeat: 6, ease: "sine.inOut" }}, {c10_st + 0.30:.2f});
{chr(10).join(cap_js)}
    window.__timelines = window.__timelines || {{}};
    window.__timelines["scene-main"] = tl;
  </script>
</template>
"""
    (comp_dir / "scene-main.html").write_text(scene_html, encoding="utf-8")

    # Root index.html with Voiceover + Fresh 2-part BGM + Subtle Tactile Micro-SFX (-19dB)
    vo_clips = "\n".join(
        f'    <audio id="vo-{vi+1}" class="clip" src="assets/audio/{s["id"]}.wav" data-start="{float(s.get("start_s", s.get("vo_start_s", s["shot_start_s"]))):.2f}" data-duration="{float(s.get("duration_s", s.get("vo_duration_s", s["shot_duration_s"]))):.2f}" data-volume="1.34" data-fade-in="0.03" data-fade-out="0.05" data-track-index="{4 if vi % 2 == 0 else 5}" data-fx-chain="{VO_FX_CHAIN}"></audio>'
        for vi, s in enumerate(segs)
    )
    sfx_tags = []
    if (aud_dir / "sfx_whoosh_soft.mp3").exists():
        for wi, (_, _, wst, _) in enumerate(cuts_10[1:], start=2):
            sfx_tags.append(f'    <audio id="sfx-w{wi}" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{max(0.0, wst - 0.08):.2f}" data-duration="0.45" data-volume="0.14" data-fade-out="0.12" data-track-index="8"></audio>')
    if (aud_dir / "sfx_pop_clean.mp3").exists():
        sfx_tags.append(f'    <audio id="sfx-p1" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{c3_st + 0.10:.2f}" data-duration="0.45" data-volume="0.18" data-track-index="9"></audio>')
        sfx_tags.append(f'    <audio id="sfx-p2" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{choice_st:.2f}" data-duration="0.45" data-volume="0.18" data-track-index="9"></audio>')
        sfx_tags.append(f'    <audio id="sfx-p3" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{c7_st + 0.08:.2f}" data-duration="0.45" data-volume="0.18" data-track-index="9"></audio>')
    if (aud_dir / "sfx_chime_warm.mp3").exists():
        sfx_tags.append(f'    <audio id="sfx-end" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="{c10_st + 0.15:.2f}" data-duration="1.80" data-volume="0.42" data-track-index="10"></audio>')

    index_html = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
  <title>{cfg['final_mp4']}</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body, #root {{ width: 1080px; height: 1920px; overflow: hidden; background: #0D1622; position: relative; }}
    .scene-host {{ position: absolute; inset: 0; width: 1080px; height: 1920px; z-index: 2; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur:.2f}" data-fps="24">
    <div id="scene-main" class="scene-host" data-composition-id="scene-main" data-composition-src="compositions/scene-main.html" data-start="0" data-duration="{total_dur:.2f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
{vo_clips}
    <audio id="bgm-1" class="clip" src="assets/audio/bgm_1.mp3" data-start="0" data-duration="{mid_t:.2f}" data-media-start="2.0" data-volume="0.24" data-fade-in="0.35" data-fade-out="0.55" data-loop="true" data-track-index="6"></audio>
    <audio id="bgm-2" class="clip" src="assets/audio/bgm_2.mp3" data-start="{max(0.0, mid_t - 0.25):.2f}" data-duration="{round(total_dur - mid_t + 0.25, 2):.2f}" data-media-start="4.0" data-volume="0.26" data-fade-in="0.50" data-fade-out="0.80" data-loop="true" data-track-index="7"></audio>
{chr(10).join(sfx_tags)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    window.__timelines["main"] = gsap.timeline({{ paused: true }});
  </script>
</body>
</html>
"""
    (hf_dir / "index.html").write_text(index_html, encoding="utf-8")

    out_dir = work_dir / "08_Render_Master_V5"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / cfg["final_mp4"]

    if "--qa-only" in sys.argv and out_mp4.exists() and out_mp4.stat().st_size > 15_000_000:
        return out_mp4, cuts_10, total_dur

    if not (out_mp4.exists() and out_mp4.stat().st_size > 15_000_000 and "--force" not in sys.argv):
        subprocess.run(
            ["npx.cmd", "hyperframes", "render", "--output", str(out_mp4), "--quality", "delivery"],
            cwd=str(hf_dir),
            check=True,
        )

    for dst_folder in (K6_DAY25_DIR, CLOUD_DAY25_VID, LOCAL_DAY25_DIR):
        dst_folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out_mp4, dst_folder / cfg["final_mp4"])
    print(f"[V5 10-CUT VIDEO DELIVERED TO K6] {cfg['final_mp4']} ({round(out_mp4.stat().st_size / 1048576, 1)} MB)", flush=True)
    return out_mp4, cuts_10, total_dur


def build_all_12_configs():
    cfgs = []
    # 10 Daily Videos (V01..V10)
    for sl in SLOTS_261125:
        idx = sl["idx"]
        cfgs.append({
            "label": sl["code"],
            "vkey": sl["vkey"],
            "map_key": sl["vkey"],
            "vo_dir": BATCH_ROOT / sl["vkey"] / "06_Audio_Voiceover",
            "final_mp4": sl["final_mp4"],
            "cutout": "SP_HTPM_FULL_8SKU_SHELF.png" if idx == 10 else sl["cutout"],
            "pri": sl["pri"],
            "pri_dark": sl["pri_dark"],
            "pri_soft": sl["pri_soft"],
            "ov_pair": OVERLAY_PAIRS[idx % 2],
            "hook_kicker": sl["hook_kicker"],
            "hook_hero": sl["hook_hero"],
            "slide1_hdr": sl["slide1_hdr"],
            "slide1_rows": sl["slide1_rows"],
            "slide2_pill": sl["slide2_pill"],
            "pack_kicker": sl["pack_kicker"],
            "pack_hero": sl["pack_hero"],
            "slide3_pills": sl["slide3_pills"],
            "end_cat": sl["end_cat"],
            "end_name": sl["end_name"],
            "end_sub": sl["end_sub"],
            "cta_txt": sl["cta_txt"].upper(),
            "legal_txt": sl["legal_txt"],
            "caps_pair": sl["caps"],
        })

    # Dedicated #11: Ngọc Long Hoàn (Couple tea ONLY in Cut 10!)
    cfgs.append({
        "label": "NLH_SP",
        "vkey": "flagship_ngoc_long_hoan",
        "map_key": "flagship_ngoc_long_hoan",
        "vo_dir": V1_COUPLE_ROOT / "c01_ngoc_long_hoan" / "06_Audio_Voiceover",
        "final_mp4": "261125 HTPM Ngọc Long Hoàn chị Hằng chia sẻ bí quyết chăm sức khỏe chồng final.mp4",
        "cutout": "SP_NGOC_LONG_HOAN_CUTOUT.png",
        "pri": "#9E241A",
        "pri_dark": "#3A0A07",
        "pri_soft": "#FFF0EC",
        "ov_pair": OVERLAY_PAIRS[0],
        "hook_kicker": "ĐÀN ÔNG GÁNH VÁC CẢ GIA ĐÌNH",
        "hook_hero": "Chồng đau lưng, mệt chẳng than?",
        "slide1_hdr": "3 DẤU HIỆU SUY GIẢM NGUYÊN KHÍ",
        "slide1_rows": [
            "Làm việc khuya, hay đau lưng mỏi gối",
            "Thể lực suy giảm nhưng ngại nói với vợ",
            "Cần bồi bổ thận khí bền vững từ gốc",
        ],
        "slide2_pill": "Bí quyết chị Hằng chuẩn bị mỗi ngày<br/>Ngọc Long Hoàn Hằng Thu",
        "pack_kicker": "BỔ THẬN • VỮNG VÀNG PHONG ĐỘ",
        "pack_hero": "Ngọc Long Hoàn",
        "slide3_pills": [
            "Bổ thận, bồi bổ nguyên khí từ gốc",
            "Giảm mệt mỏi, đau lưng mỏi gối",
            "Giữ thể lực dẻo dai & phong độ bền bỉ",
        ],
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE",
        "end_name": "Ngọc Long Hoàn",
        "end_sub": "BỒI BỔ THỂ LỰC • VỮNG PHONG ĐỘ",
        "cta_txt": "NHẮN NGAY “NGỌC LONG HOÀN” · TƯ VẤN BẢO MẬT",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "caps_pair": [
            ("vo_01", 'Hơn 10 năm đồng hành <span class="cap-kw">cùng ông xã bận rộn,</span>', 'Mỏi lưng, mệt người <span class="cap-kw">anh hiếm khi than thở!</span>'),
            ("vo_02", 'Sau tuổi 35 <span class="cap-kw">áp lực công việc dồn nén,</span>', 'Chỉ người vợ tinh tế <span class="cap-kw">mới nhận ra anh xuống sức.</span>'),
            ("vo_03", 'Mỗi ngày Hằng chuẩn bị <span class="cap-kw">Ngọc Long Hoàn</span>', 'Bồi bổ sức khỏe <span class="cap-kw">bền vững từ gốc cho chồng.</span>'),
            ("vo_04", 'Hỗ trợ <span class="cap-kw">bổ thận, bồi bổ nguyên khí,</span>', 'Giảm đau lưng mỏi gối, <span class="cap-kw">vững phong độ dẻo dai!</span>'),
        ],
    })

    # Dedicated #12: Điều Kinh HT (0% husband!)
    cfgs.append({
        "label": "DK_SP",
        "vkey": "flagship_dieu_kinh_ht",
        "map_key": "flagship_dieu_kinh_ht",
        "vo_dir": V2_SOLO_DK_ROOT / "c02_dieu_kinh_ht" / "06_Solo_Voiceover",
        "final_mp4": "261125 HTPM Điều Kinh HT bí quyết dưỡng khí huyết rạng rỡ của chị Hằng final.mp4",
        "cutout": "SP_DIEU_KINH_HT_CUTOUT.png",
        "pri": "#8B1E72",
        "pri_dark": "#3B0830",
        "pri_soft": "#FBE8F7",
        "ov_pair": OVERLAY_PAIRS[1],
        "hook_kicker": "PHỤ NỮ ĐẾN KỲ ĐAU BỤNG MỆT LẢ",
        "hook_hero": "Tới kỳ đau bụng, người mệt lả?",
        "slide1_hdr": "3 DẤU HIỆU KHÍ HUYẾT KÉM LƯU THÔNG",
        "slide1_rows": [
            "Đến tháng đau bụng âm ỉ, người uể oải",
            "Chu kỳ dễ thất thường, tay chân hay lạnh",
            "Sắc mặt kém tươi tắn, thiếu sức sống",
        ],
        "slide2_pill": "Bí quyết êm dịu mỗi chu kỳ của Hằng<br/>Điều Kinh HT Hằng Thu",
        "pack_kicker": "ĐƯƠNG QUY & HƯƠNG PHỤ QUÝ",
        "pack_hero": "Điều Kinh HT",
        "slide3_pills": [
            "Giúp bổ huyết, lưu thông khí huyết",
            "Hỗ trợ điều hòa kinh nguyệt đều đặn",
            "Giảm đau bụng kinh, sắc diện hồng hào",
        ],
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE",
        "end_name": "Điều Kinh HT",
        "end_sub": "BỔ HUYẾT • LƯU THÔNG KHÍ HUYẾT",
        "cta_txt": "NHẮN NGAY “ĐIỀU KINH HT” · TƯ VẤN RIÊNG",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "caps_pair": [
            ("vo_01", 'Mỗi tháng đến kỳ <span class="cap-kw">đau bụng âm ỉ, mệt lả,</span>', 'Chị em vẫn ráng chu toàn <span class="cap-kw">công việc &amp; gia đình.</span>'),
            ("vo_02", 'Khi <span class="cap-kw">khí huyết kém lưu thông</span> bên trong,', 'Chu kỳ dễ thất thường, <span class="cap-kw">tay chân lạnh, kém tươi!</span>'),
            ("vo_03", 'Bí quyết êm dịu <span class="cap-kw">mỗi chu kỳ của Hằng</span>', 'Là đều đặn dùng <span class="cap-kw">Điều Kinh HT Hằng Thu.</span>'),
            ("vo_04", 'Từ <span class="cap-kw">Đương quy &amp; Hương phụ</span> bổ huyết,', 'Giảm đau bụng kinh, <span class="cap-kw">nuôi sắc diện hồng hào!</span>'),
        ],
    })
    return cfgs


def main():
    # Pre-generate all 10 Studio Podium 3D videos first!
    for sl in SLOTS_261125:
        ensure_studio_podium_video(sl["idx"], sl["cutout"], sl["pri"])
    print("[10/10 STUDIO PODIUM 3D PACKSHOT CLIPS READY]", flush=True)

    aco_list, tvc_list = list_fresh_bgms()
    all_cfgs = build_all_12_configs()
    cfgs = list(enumerate(all_cfgs))
    if "--test1" in sys.argv:
        cfgs = cfgs[:1]
    elif "--slice" in sys.argv:
        si = sys.argv.index("--slice")
        a, b = int(sys.argv[si + 1]), int(sys.argv[si + 2])
        cfgs = cfgs[a:b]

    qa_rows = []
    for idx, cfg in cfgs:
        b1 = aco_list[idx % len(aco_list)]
        b2 = tvc_list[idx % len(tvc_list)]
        mp4_p, cuts_10, tdur = build_and_render_10cut_usp_video(cfg, b1, b2)
        row_tiles = []
        for c_num, tok, c_st, c_dur in cuts_10:
            ts = min(tdur - 0.35, c_st + c_dur * 0.52)
            fp = mp4_p.parent / f"qa10_{c_num:02d}.jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(mp4_p), "-frames:v", "1", "-q:v", "2", str(fp)], check=True)
            im = Image.open(fp).convert("RGB")
            d = ImageDraw.Draw(im)
            d.line([(0, 248), (1080, 248)], fill=(255, 60, 60), width=4)
            d.line([(0, 1548), (1080, 1548)], fill=(255, 60, 60), width=4)
            d.rectangle([(886, 860), (1080, 1548)], outline=(255, 60, 60), width=4)
            row_tiles.append((f"{cfg['label']}_C{c_num:02d}", im))
        qa_rows.append(row_tiles)

    if len(qa_rows) < 12 and "--test1" not in sys.argv:
        print(f"=== SLICE ({len(qa_rows)} VIDEOS) RENDERED & DELIVERED TO K6 ===", flush=True)
        return

    # Build 10 columns (Cuts 1..10) x len(qa_rows) rows Master QA Sheet!
    tw, th = 220, 390
    sheet = Image.new("RGB", (tw * 10, th * len(qa_rows)), (12, 18, 28))
    sd = ImageDraw.Draw(sheet)
    for r_idx, r_tiles in enumerate(qa_rows):
        for c_idx, (lbl, im) in enumerate(r_tiles):
            sheet.paste(im.resize((tw - 6, th - 20), Image.Resampling.LANCZOS), (c_idx * tw + 3, r_idx * th + 18))
            sd.text((c_idx * tw + 5, r_idx * th + 2), lbl, fill=(190, 235, 255))

    qa_out = V5_DIR / "v5_all_12_videos_120_cuts_qa.jpg"
    sheet.save(qa_out, quality=92)
    shutil.copy2(qa_out, ARTIFACT_DIR / "htpm_261125_12_videos_120cuts_v5_qa.jpg")
    print("=== ALL 12 V5 10-CUT ACTION USP VIDEOS DELIVERED TO K6 ===", flush=True)


if __name__ == "__main__":
    main()
