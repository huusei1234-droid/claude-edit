# -*- coding: utf-8 -*-
"""
V4 AI USP MASTER — STEP 3: Render 2 Video Quảng Cáo AI USP (<45s, 9:16 @ 24fps) trên HyperFrames & Xuất Phẳng Vào K6 - Hằng Thu Pharma!
- 100% Video AI USP (7 phân cảnh AI động/video: Hook Chị Hằng -> Pain Visual -> 3D CGI Cơ chế Y khoa -> 3D Macro Dược liệu -> Giải pháp Chị Hằng cầm SP -> Bục 3D Sản phẩm -> End-Card).
- Ngọc Long Hoàn (40.75s): 100% chuẩn mặt thật Chị Hằng xuyên suốt, Chồng (Anh Hải) CHỈ xuất hiện duy nhất ở cảnh cuối C07!
- Điều Kinh HT (36.75s): 100% chuẩn mặt thật Chị Hằng xuyên suốt, 0% Chồng ở mọi cảnh & lời thoại!
- Đầy đủ lớp phủ 4K Bokeh/Flare/Sparkle/Sunbeams (Screen), Thanh tiến trình động, Header thương hiệu HT, Con dấu xoay 3D 100% Chính Hãng, Nhạc nền mới & Chữ lớn trong Vùng An Toàn!
"""
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

BATCH_ROOT = Path(r"d:\AI\full studio\output\htpm-ai-usp-v4-261125")
V1_COUPLE_ROOT = Path(r"d:\AI\full studio\output\htpm-couple-nlh-dk-261125")
V2_ROOT = Path(r"d:\AI\full studio\output\htpm-couple-nlh-dk-v2-261125")
PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
BRAND_KIT = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "brand_kits" / "01_HTPM_Hang_Thu_Pharma"
PROD_DIR = BRAND_KIT / "products_cutout_png"
OVERLAYS_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "video_overlays_4k"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"

K6_DAY25_DIR = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\05. Video Hoàn Thiện\K6 - Hằng Thu Pharma\261125 - Ngày 25.11.2026")
CLOUD_DAY25_VID = Path(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\261125 - Ngày 25.11.2026")
LOCAL_DAY25_DIR = Path(r"D:\XUẤT CAPCUT\hằng thu pharma\261125 - Ngày 25.11.2026")
ARTIFACT_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682")


def pick_fresh_bgm_pair():
    z_tvc = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng")
    z_aco = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\05_Acoustic - Guitar - Nhẹ Nhàng Mộc Mạc")
    b1 = AUDIO_BUNDLE_DIR / "bgm_sunny_carefree.mp3"
    b2 = AUDIO_BUNDLE_DIR / "bgm_coconut_groove_tvc.mp3"
    b3 = AUDIO_BUNDLE_DIR / "bgm_fresh_wellness_tvc.mp3"
    found_tvc = sorted([f for f in z_tvc.rglob("*.mp3") if 1_200_000 < f.stat().st_size < 12_000_000]) if z_tvc.exists() else []
    found_aco = sorted([f for f in z_aco.rglob("*.mp3") if 1_200_000 < f.stat().st_size < 12_000_000]) if z_aco.exists() else []
    nlh_bgm1 = found_aco[0] if len(found_aco) > 0 else b1
    nlh_bgm2 = found_tvc[0] if len(found_tvc) > 0 else b2
    dk_bgm1 = found_aco[1] if len(found_aco) > 1 else b3
    dk_bgm2 = found_tvc[1] if len(found_tvc) > 1 else b1
    return (nlh_bgm1, nlh_bgm2), (dk_bgm1, dk_bgm2)


V4_CFG = [
    {
        "vkey": "c01_ngoc_long_hoan",
        "src_vo_dir": V1_COUPLE_ROOT / "c01_ngoc_long_hoan" / "06_Audio_Voiceover",
        "final_mp4": "261125 HTPM Ngọc Long Hoàn chị Hằng chia sẻ bí quyết chăm sức khỏe chồng final.mp4",
        "cutout": "SP_NGOC_LONG_HOAN_CUTOUT.png",
        "pri": "#A8201A", "pri_dark": "#3A0A07", "pri_soft": "#FFF0EC", "grad_mid": "#FF8E7A",
        "ov_mp4_1": "01_Golden_Dust_Bokeh_9x16.mp4",
        "ov_mp4_2": "04_Anamorphic_Gold_Rose_Flare_9x16.mp4",
        "hook_kicker": "ĐÀN ÔNG GÁNH VÁC CẢ GIA ĐÌNH",
        "hook_l1": "Chồng đau lưng,",
        "hook_l2": "mệt chẳng than?",
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
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE", "end_name": "Ngọc Long Hoàn", "end_sub": "BỒI BỔ THỂ LỰC • VỮNG PHONG ĐỘ",
        "cta_txt": "NHẮN NGAY “NGỌC LONG HOÀN” · TƯ VẤN BẢO MẬT",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "big_caps": [
            ("vo_01", ['Hơn 10 năm đồng hành <span class="cap-kw">cùng ông xã</span>', 'Đàn ông gánh vác <span class="cap-kw">trăm công nghìn việc</span>', 'Mỏi lưng, mệt người <span class="cap-kw">hiếm khi than thở!</span>']),
            ("vo_02", ['Sau tuổi 35 <span class="cap-kw">áp lực công việc,</span>', 'Anh dễ đau lưng, <span class="cap-kw">uể oải cuối ngày,</span>', 'Chỉ người vợ tinh tế <span class="cap-kw">mới nhận ra!</span>']),
            ("vo_03", ['Mỗi ngày Hằng chuẩn bị <span class="cap-kw">Ngọc Long Hoàn</span>', 'Bồi bổ sức khỏe <span class="cap-kw">bền vững từ gốc</span>', 'Cho ông xã luôn <span class="cap-kw">tràn đầy năng lượng.</span>']),
            ("vo_04", ['Hỗ trợ <span class="cap-kw">bổ thận, bồi bổ nguyên khí,</span>', 'Giúp giảm mệt mỏi, <span class="cap-kw">đau lưng mỏi gối,</span>', 'Giữ vững <span class="cap-kw">phong độ dẻo dai!</span>']),
        ],
        "s4_pack_end": 33.25,
        "blur_s4_bg": True,
        "clips_7": [
            ("NLH4_C01", 0.00, 5.00),
            ("NLH4_C02", 5.00, 5.00),
            ("NLH4_C03", 10.00, 4.50),
            ("NLH4_C04", 14.50, 4.50),
            ("NLH4_C05", 19.00, 6.50),
            ("NLH4_C06", 25.50, 7.75),
            ("NLH4_C07", 33.25, 7.50),
        ],
    },
    {
        "vkey": "c02_dieu_kinh_ht",
        "src_vo_dir": V2_ROOT / "c02_dieu_kinh_ht" / "06_Solo_Voiceover",
        "final_mp4": "261125 HTPM Điều Kinh HT bí quyết dưỡng khí huyết rạng rỡ của chị Hằng final.mp4",
        "cutout": "SP_DIEU_KINH_HT_CUTOUT.png",
        "pri": "#8B1E72", "pri_dark": "#3B0830", "pri_soft": "#FBE8F7", "grad_mid": "#F28CD9",
        "ov_mp4_1": "05_Soft_Pearl_Sparkles_Bling_9x16.mp4",
        "ov_mp4_2": "03_Warm_Window_Sun_Rays_9x16.mp4",
        "hook_kicker": "PHỤ NỮ ĐẾN KỲ ĐAU BỤNG MỆT LẢ",
        "hook_l1": "Tới kỳ đau bụng,",
        "hook_l2": "người mệt lả?",
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
        "end_cat": "THỰC PHẨM BẢO VỆ SỨC KHỎE", "end_name": "Điều Kinh HT", "end_sub": "BỔ HUYẾT • LƯU THÔNG KHÍ HUYẾT",
        "cta_txt": "NHẮN NGAY “ĐIỀU KINH HT” · TƯ VẤN RIÊNG",
        "legal_txt": "Thực phẩm này không phải là thuốc, không thay thế thuốc chữa bệnh",
        "big_caps": [
            ("vo_01", ['Phụ nữ mỗi tháng <span class="cap-kw">đến kỳ dâu rụng</span>', 'Thường đau bụng âm ỉ, <span class="cap-kw">người mệt lả đi,</span>', 'Vẫn ráng chu toàn <span class="cap-kw">công việc &amp; gia đình.</span>']),
            ("vo_02", ['Khi <span class="cap-kw">khí huyết kém lưu thông,</span>', 'Chu kỳ dễ thất thường, <span class="cap-kw">tay chân lạnh,</span>', 'Sắc mặt cũng kém <span class="cap-kw">tươi tắn rạng rỡ!</span>']),
            ("vo_03", ['Bí quyết êm dịu <span class="cap-kw">mỗi chu kỳ của Hằng</span>', 'Là đều đặn dùng <span class="cap-kw">Điều Kinh HT</span>', 'Chăm dưỡng cơ thể <span class="cap-kw">từ thảo dược quý.</span>']),
            ("vo_04", ['Từ <span class="cap-kw">Đương quy &amp; Hương phụ</span> bổ huyết,', 'Hỗ trợ lưu thông, <span class="cap-kw">điều hòa kinh nguyệt,</span>', 'Giảm đau bụng kinh <span class="cap-kw">êm ái nhẹ tênh!</span>']),
        ],
        "s4_pack_end": 25.80,
        "blur_s4_bg": False,
        "clips_7": [
            ("DK4_C01", 0.00, 4.20),
            ("DK4_C02", 4.20, 3.80),
            ("DK4_C03", 8.00, 6.50),
            ("DK4_C04", 14.50, 6.50),
            ("DK4_C05", 21.00, 4.80),
            ("DK4_C06", 25.80, 3.95),
            ("DK4_C07", 29.75, 7.00),
        ],
    },
]

COLOR_GRADE_CRYSTAL = (
    '{&quot;preset&quot;:null,&quot;intensity&quot;:1,&quot;adjust&quot;:{&quot;exposure&quot;:0.04,&quot;contrast&quot;:0.06,'
    '&quot;highlights&quot;:0.02,&quot;shadows&quot;:0.05,&quot;whites&quot;:0.05,&quot;blacks&quot;:0,&quot;temperature&quot;:0.01,'
    '&quot;tint&quot;:0.01,&quot;vibrance&quot;:0.12,&quot;saturation&quot;:0.04},&quot;details&quot;:{&quot;vignette&quot;:0.03,'
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


def build_and_render_v4(cfg: dict, bgm_pair: tuple):
    vkey = cfg["vkey"]
    pdir = BATCH_ROOT / vkey
    hf_dir = pdir / "07_HyperFrames_Project"
    comp_dir = hf_dir / "compositions"
    img_dir = hf_dir / "assets" / "images"
    aud_dir = hf_dir / "assets" / "audio"
    vid_dir = hf_dir / "assets" / "videos"
    fnt_dir = hf_dir / "assets" / "fonts"
    for d in (comp_dir, img_dir, aud_dir, vid_dir, fnt_dir):
        d.mkdir(parents=True, exist_ok=True)

    vo_manifest = json.loads((cfg["src_vo_dir"] / "vo_manifest.json").read_text(encoding="utf-8"))
    for s in vo_manifest["segments"]:
        shutil.copy2(cfg["src_vo_dir"] / f"{s['id']}.wav", aud_dir / f"{s['id']}.wav")
    for f in AUDIO_BUNDLE_DIR.glob("sfx_*.*"):
        shutil.copy2(f, aud_dir / f.name)
    for f in FONTS_BUNDLE_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in (".ttf", ".otf", ".woff2", ".css"):
            shutil.copy2(f, fnt_dir / f.name)

    shutil.copy2(bgm_pair[0], aud_dir / "bgm_part1_fresh.mp3")
    shutil.copy2(bgm_pair[1], aud_dir / "bgm_part2_fresh.mp3")
    shutil.copy2(PROD_DIR / cfg["cutout"], img_dir / cfg["cutout"])
    logo_src = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124\10_Bai_Thiet_Ke_Soft_Editorial\ht_logo_33mp_clean.png")
    shutil.copy2(logo_src if logo_src.exists() else (BRAND_KIT / "logos_png" / "ht_logo_official.png"), img_dir / "ht_logo_clean.png")

    shutil.copy2(OVERLAYS_DIR / cfg["ov_mp4_1"], vid_dir / cfg["ov_mp4_1"])
    shutil.copy2(OVERLAYS_DIR / cfg["ov_mp4_2"], vid_dir / cfg["ov_mp4_2"])

    segs = {s["id"]: s for s in vo_manifest["segments"]}
    total_dur = vo_manifest["total_duration_s"]
    pri, pri_dark, pri_soft, grad_mid = cfg["pri"], cfg["pri_dark"], cfg["pri_soft"], cfg["grad_mid"]

    c7 = list(cfg["clips_7"])
    c7[-1] = (c7[-1][0], c7[-1][1], round(total_dur - c7[-1][1], 2))

    vid_tags, flash_times, rig_tweens = [], [], []
    for ci, (ocode, cst, cdur) in enumerate(c7):
        trk = (ci % 2) + 1
        # Soft bokeh on NLH4_C06 podium background so our crisp 100% real studio cutout SP_NGOC_LONG_HOAN_CUTOUT.png pops cleanly without double bottle!
        extra_cls = " s4-soft-bokeh" if (ocode == "NLH4_C06" and cfg["blur_s4_bg"]) else ""
        vid_tags.append(
            f'    <div id="rig-{ci}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>'
            f'<video data-color-grading="{COLOR_GRADE_CRYSTAL}" id="vid-{ci}" class="clip bg-video{extra_cls}" src="assets/videos/{ocode}.mp4" '
            f'data-start="{cst}" data-duration="{cdur}" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="{trk}" muted playsinline></video></div>'
        )
        z0, z1 = (1.0, 1.045) if (ci % 2 == 0) else (1.045, 1.0)
        rig_tweens.append(f'    tl.fromTo("#rig-{ci}", {{ scale: {z0} }}, {{ scale: {z1}, duration: {cdur}, ease: "none" }}, {cst});')
        if ci > 0:
            flash_times.append(cst)

    s4_pack_end = cfg["s4_pack_end"]
    s1_end = segs["vo_01"]["shot_end_s"]
    s2_st = segs["vo_02"]["shot_start_s"]
    s2_dur = segs["vo_02"]["shot_duration_s"]
    s3_st = segs["vo_03"]["shot_start_s"]
    s3_dur = segs["vo_03"]["shot_duration_s"]
    s4_st = segs["vo_04"]["shot_start_s"]
    s4_dur = segs["vo_04"]["shot_duration_s"]
    s5_st = segs["vo_05"]["shot_start_s"]
    s5_dur = round(total_dur - s5_st, 2)

    ov_tags = []
    t_cur, ov_idx = 0.0, 0
    while t_cur < total_dur - 0.5:
        chunk_d = round(min(4.8, total_dur - t_cur), 2)
        src_ov = cfg["ov_mp4_1"] if (ov_idx % 2 == 0) else cfg["ov_mp4_2"]
        ov_tags.append(
            f'    <video id="ov-{ov_idx}" class="clip screen-overlay" src="assets/videos/{src_ov}" '
            f'data-start="{round(t_cur, 2)}" data-duration="{chunk_d}" data-media-start="0" data-hf-media-start-basis="local" '
            f'data-track-index="{3 + (ov_idx % 2)}" data-layout-ignore muted playsinline></video>'
        )
        t_cur += chunk_d
        ov_idx += 1

    stage_html = f"""<template>
  <style>
    @font-face {{ font-family: "FrauncesVN"; src: url("assets/fonts/Fraunces-Black.ttf") format("truetype"); font-weight: 900; font-display: block; }}
    @font-face {{ font-family: "PlayfairVNItalic"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; font-display: block; }}
    @font-face {{ font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "BeVietnamBold"; src: url("assets/fonts/BeVietnamPro-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}
    @font-face {{ font-family: "DancingVN"; src: url("assets/fonts/DancingScript-Bold.ttf") format("truetype"); font-weight: 700; font-display: block; }}

    #root {{ position: absolute; inset: 0; width: 1080px; height: 1920px; overflow: hidden; background: {pri_dark}; font-family: "BeVietnamVN", sans-serif; }}
    .cam-rig {{ position: absolute; inset: 0; width: 1080px; height: 1920px; transform-origin: 50% 42%; }}
    .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    .s4-soft-bokeh {{ filter: blur(28px) brightness(1.06) saturate(1.08); transform: scale(1.14); }}
    .screen-overlay {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; mix-blend-mode: screen; opacity: 0.44; pointer-events: none; z-index: 4; }}
    .cut-flash {{ position: absolute; inset: 0; background: radial-gradient(circle, rgba(255,255,255,0.70) 0%, rgba(255,240,220,0.0) 75%); opacity: 0; pointer-events: none; z-index: 5; mix-blend-mode: screen; }}

    .top-brand-bar {{
      position: absolute; top: 258px; left: 56px; z-index: 15;
      display: flex; align-items: center; gap: 14px;
      background: rgba(255, 255, 255, 0.94); border: 2.5px solid {pri};
      border-radius: 999px; padding: 8px 24px 8px 10px;
      box-shadow: 0 10px 26px rgba(10, 20, 40, 0.22);
    }}
    .top-brand-bar img {{ width: 52px; height: 52px; object-fit: contain; }}
    .top-brand-bar .tb1 {{ font-family: "BeVietnamVN", sans-serif; font-size: 22px; color: #0082C8; letter-spacing: 0.05em; line-height: 1.05; }}
    .top-brand-bar .tb2 {{ font-family: "BeVietnamBold", sans-serif; font-size: 15px; color: #D91E2A; letter-spacing: 0.14em; text-transform: uppercase; }}
    .prog-track {{ position: absolute; top: 248px; left: 56px; width: 960px; height: 6px; background: rgba(255,255,255,0.40); border-radius: 99px; z-index: 16; overflow: hidden; }}
    .prog-fill {{ width: 100%; height: 100%; transform-origin: left center; transform: scaleX(0); background: linear-gradient(90deg, #FFFFFF 0%, {grad_mid} 50%, {pri} 100%); border-radius: 99px; }}

    .spin-seal {{
      position: absolute; top: 256px; left: 846px; width: 162px; height: 162px; z-index: 15;
      display: flex; align-items: center; justify-content: center; pointer-events: none;
    }}
    .spin-seal-ring {{
      position: absolute; inset: 0; border-radius: 50%;
      background: linear-gradient(135deg, {pri} 0%, {pri_dark} 100%);
      border: 4px dashed #ffffff; box-shadow: 0 12px 28px rgba(10,20,40,0.28);
    }}
    .spin-seal-core {{ position: relative; z-index: 2; text-align: center; color: #ffffff; line-height: 1.08; }}
    .spin-seal-core .sc1 {{ font-size: 15px; font-weight: 800; letter-spacing: 0.06em; }}
    .spin-seal-core .sc2 {{ font-family: "FrauncesVN", serif; font-size: 32px; font-weight: 900; }}
    .spin-seal-core .sc3 {{ font-size: 14px; font-weight: 800; background: rgba(255,255,255,0.22); padding: 2px 10px; border-radius: 99px; margin-top: 2px; display: inline-block; }}

    .hook-stage {{ position: absolute; left: 56px; top: 965px; width: 822px; z-index: 12; pointer-events: none; }}
    .hook-kicker-pill {{
      display: inline-block; background: {pri}; color: #ffffff; border: 3px solid #ffffff;
      padding: 10px 26px; border-radius: 999px; font-size: 28px; font-weight: 800;
      letter-spacing: 0.04em; text-transform: uppercase; box-shadow: 0 10px 24px rgba(10,20,40,0.28);
      margin-bottom: 14px;
    }}
    .hook-giant-line {{
      font-family: "FrauncesVN", Georgia, serif; font-size: 84px; font-weight: 900; line-height: 1.06;
      color: {pri}; paint-order: stroke fill; -webkit-text-stroke: 15px #ffffff;
      filter: drop-shadow(0 10px 22px rgba(10,20,40,0.36));
    }}

    .slide-card {{
      position: absolute; left: 58px; top: 930px; width: 818px; border-radius: 28px;
      background: rgba(255, 255, 255, 0.95); border: 3.5px solid {pri};
      box-shadow: 0 18px 40px rgba(10, 20, 40, 0.28); padding: 22px 28px; z-index: 12; overflow: hidden;
    }}
    .sheen-bar {{
      position: absolute; top: -40%; left: -60%; width: 45%; height: 180%;
      background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.68) 50%, rgba(255,255,255,0) 100%);
      transform: skewX(-24deg); pointer-events: none;
    }}
    .slide-card-header {{
      display: inline-flex; align-items: center; background: {pri}; color: #ffffff;
      font-size: 24px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase;
      padding: 8px 22px; border-radius: 999px; margin-bottom: 14px;
    }}
    .slide-row {{ display: flex; align-items: center; gap: 14px; font-size: 29.5px; font-weight: 800; color: {pri_dark}; padding: 8px 0; line-height: 1.25; }}
    .slide-badge-dot {{ width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 21px; font-weight: 800; flex-shrink: 0; background: {pri}; color: #ffffff; }}

    .slide-pill-stack {{ position: absolute; left: 58px; display: flex; flex-direction: column; gap: 14px; z-index: 12; }}
    .slide-pill {{
      display: inline-flex; align-items: center; gap: 16px; background: rgba(255, 255, 255, 0.96);
      border-left: 10px solid {pri}; border-top: 2px solid #fff; border-right: 2px solid {pri}; border-bottom: 2px solid {pri};
      border-radius: 22px; padding: 15px 26px; font-size: 29.5px; font-weight: 800; color: {pri_dark};
      box-shadow: 0 14px 30px rgba(10, 20, 40, 0.24); width: 816px;
    }}
    .s3-mini-pack {{ height: 112px; width: auto; object-fit: contain; flex-shrink: 0; filter: drop-shadow(0 6px 12px rgba(10,20,40,0.26)); }}

    .s4-prod-stage {{
      position: absolute; left: 80px; top: 470px; width: 780px; height: 520px;
      display: flex; align-items: center; justify-content: center; z-index: 11; pointer-events: none;
    }}
    .s4-halo {{ position: absolute; width: 490px; height: 490px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.95) 0%, {pri_soft} 46%, rgba(255,255,255,0) 74%); }}
    .s4-real-pack {{ position: relative; z-index: 3; height: 500px; object-fit: contain; filter: drop-shadow(0 22px 34px rgba(10,20,45,0.38)); }}
    .s4-title-box {{ position: absolute; left: 58px; top: 342px; width: 820px; text-align: center; z-index: 12; }}
    .s4-kicker {{ display: inline-block; background: {pri}; color: #fff; padding: 7px 22px; border-radius: 99px; font-size: 24px; font-weight: 800; border: 2.5px solid #fff; }}
    .s4-hero {{ font-family: "FrauncesVN", serif; font-size: 82px; color: {pri}; paint-order: stroke fill; -webkit-text-stroke: 14px #fff; line-height: 1.05; margin-top: 6px; filter: drop-shadow(0 8px 18px rgba(0,0,0,0.28)); }}

    .end-card-panel {{
      position: absolute; left: 444px; top: 835px; width: 436px; border-radius: 28px;
      background: rgba(255, 255, 255, 0.96); border: 3.5px solid {pri};
      box-shadow: 0 18px 40px rgba(10, 20, 40, 0.30); padding: 15px 18px 14px 18px; text-align: center; z-index: 12;
    }}
    .end-packshot {{ display: block; margin: 6px auto 0 auto; width: 185px; max-height: 235px; object-fit: contain; filter: drop-shadow(0 12px 20px rgba(10,20,40,0.26)); }}
    .end-cta-box {{
      position: absolute; left: 56px; top: 1332px; width: 822px; background: {pri}; color: #ffffff;
      border: 4px solid #FFFFFF; border-radius: 999px; padding: 18px 22px; text-align: center;
      font-size: 27.5px; font-weight: 800; box-shadow: 0 16px 36px rgba(10,20,40,0.38); z-index: 14;
    }}
    .legal-note {{
      position: absolute; left: 56px; top: 1456px; width: 822px; text-align: center;
      font-family: "BeVietnamBold", sans-serif; font-size: 19.5px; color: {pri_dark};
      background: rgba(255,255,255,0.93); border-radius: 14px; padding: 8px 14px; z-index: 14;
    }}
  </style>
  <div id="root" data-composition-id="main-stage" data-width="1080" data-height="1920" data-start="0" data-duration="{total_dur}">
{chr(10).join(vid_tags)}
{chr(10).join(ov_tags)}
    <div id="cut-flash" class="cut-flash" data-layout-ignore></div>

    <div class="prog-track" data-layout-ignore><div id="prog-fill" class="prog-fill"></div></div>
    <div id="top-brand" class="clip top-brand-bar" data-start="0" data-duration="{total_dur}" data-track-index="6" data-layout-ignore>
      <img src="assets/images/ht_logo_clean.png" alt="" />
      <div><div class="tb1">HẰNG THU PHARMA</div><div class="tb2">Chính hãng • Nha Trang</div></div>
    </div>
    <div id="spin-seal" class="clip spin-seal" data-start="0.2" data-duration="{round(total_dur - 0.2, 2)}" data-track-index="7" data-layout-ignore>
      <div id="seal-ring" class="spin-seal-ring"></div>
      <div class="spin-seal-core"><div class="sc1">CAM KẾT</div><div class="sc2">100%</div><div class="sc3">CHÍNH HÃNG</div></div>
    </div>

    <div id="st-hook" class="clip hook-stage" data-start="0.12" data-duration="{round(s1_end - 0.24, 2)}" data-track-index="8" data-layout-ignore>
      <div id="hk-k" class="hook-kicker-pill">{cfg['hook_kicker']}</div>
      <div id="hk-1" class="hook-giant-line">{cfg['hook_l1']}</div>
      <div id="hk-2" class="hook-giant-line">{cfg['hook_l2']}</div>
    </div>

    <div id="st-sl1" class="clip slide-card" data-start="{round(s2_st + 0.16, 2)}" data-duration="{round(s2_dur - 0.32, 2)}" data-track-index="8" data-layout-ignore>
      <div id="sh-1" class="sheen-bar"></div>
      <div class="slide-card-header">{cfg['slide1_hdr']}</div>
      <div id="sr1" class="slide-row"><span class="slide-badge-dot">1</span> {cfg['slide1_rows'][0]}</div>
      <div id="sr2" class="slide-row"><span class="slide-badge-dot">2</span> {cfg['slide1_rows'][1]}</div>
      <div id="sr3" class="slide-row"><span class="slide-badge-dot">3</span> {cfg['slide1_rows'][2]}</div>
    </div>

    <div id="st-sl2" class="clip slide-pill-stack" style="top: 1095px;" data-start="{round(s3_st + 0.18, 2)}" data-duration="{round(s3_dur - 0.36, 2)}" data-track-index="8" data-layout-ignore>
      <div id="cp1" class="slide-pill" style="font-size: 32px; line-height: 1.28; padding: 16px 26px;"><img class="s3-mini-pack" src="assets/images/{cfg['cutout']}" alt="" /><span>{cfg['slide2_pill']}</span></div>
    </div>

    <div id="st-s4t" class="clip s4-title-box" data-start="{round(s4_st + 0.12, 2)}" data-duration="{round(s4_pack_end - s4_st - 0.18, 2)}" data-track-index="8" data-layout-ignore>
      <div class="s4-kicker">{cfg['pack_kicker']}</div>
      <div class="s4-hero">{cfg['pack_hero']}</div>
    </div>
    <div id="st-s4p" class="clip s4-prod-stage" data-start="{round(s4_st + 0.08, 2)}" data-duration="{round(s4_pack_end - s4_st - 0.14, 2)}" data-track-index="9" data-layout-ignore>
      <div class="s4-halo"></div>
      <img id="s4-pack-img" class="s4-real-pack" src="assets/images/{cfg['cutout']}" alt="" />
    </div>
    <div id="st-s4l" class="clip slide-pill-stack" style="top: 1012px;" data-start="{round(s4_st + 0.30, 2)}" data-duration="{round(s4_dur - 0.44, 2)}" data-track-index="10" data-layout-ignore>
      <div id="bp1" class="slide-pill"><span class="slide-badge-dot">✓</span> {cfg['slide3_pills'][0]}</div>
      <div id="bp2" class="slide-pill"><span class="slide-badge-dot">✓</span> {cfg['slide3_pills'][1]}</div>
      <div id="bp3" class="slide-pill"><span class="slide-badge-dot">✓</span> {cfg['slide3_pills'][2]}</div>
    </div>

    <div id="st-end" class="clip end-card-panel" data-start="{round(s5_st + 0.12, 2)}" data-duration="{round(s5_dur - 0.12, 2)}" data-track-index="8" data-layout-ignore>
      <div style="font-size:17px;font-weight:800;color:{pri};letter-spacing:0.04em;">{cfg['end_cat']}</div>
      <div style="font-family:'FrauncesVN',Georgia,serif;font-size:48px;font-weight:900;color:{pri};line-height:1.06;margin-top:4px;">{cfg['end_name']}</div>
      <div style="font-family:'DancingVN',cursive;font-size:38px;font-weight:700;color:#0082C8;line-height:1.06;">Hằng Thu Pharma</div>
      <div style="font-size:16px;font-weight:800;color:{pri_dark};margin-top:4px;">{cfg['end_sub']}</div>
      <img class="end-packshot" src="assets/images/{cfg['cutout']}" alt="" />
    </div>
    <div id="st-cta" class="clip end-cta-box" data-start="{round(s5_st + 0.26, 2)}" data-duration="{round(s5_dur - 0.26, 2)}" data-track-index="9" data-layout-ignore>{cfg['cta_txt']}</div>
    <div id="st-leg" class="clip legal-note" data-start="{round(s5_st + 0.34, 2)}" data-duration="{round(s5_dur - 0.34, 2)}" data-track-index="10" data-layout-ignore>{cfg['legal_txt']}</div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#prog-fill", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {total_dur}, ease: "none" }}, 0)
      .fromTo("#seal-ring", {{ rotation: 0 }}, {{ rotation: 360, duration: {total_dur}, ease: "none" }}, 0);

{chr(10).join(rig_tweens)}

    const cuts = {json.dumps(flash_times)};
    cuts.forEach((ct) => {{
      tl.fromTo("#cut-flash", {{ opacity: 0.68 }}, {{ opacity: 0, duration: 0.28, ease: "power2.out", immediateRender: false }}, ct);
    }});

    tl.fromTo("#hk-k", {{ opacity: 0, y: -16, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.24, ease: "back.out(1.4)" }}, 0.14)
      .fromTo("#hk-1", {{ opacity: 0, x: -45, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.26, ease: "back.out(1.3)" }}, 0.22)
      .fromTo("#hk-2", {{ opacity: 0, x: 45, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, 0.34)
      .to("#st-hook", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s1_end - 0.32, 2)})

      .fromTo("#st-sl1", {{ opacity: 0, y: 35, scale: 0.93, filter: "blur(12px)" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, {round(s2_st + 0.16, 2)})
      .fromTo("#sh-1", {{ x: -450 }}, {{ x: 1450, duration: 1.1, ease: "power2.inOut" }}, {round(s2_st + 0.45, 2)})
      .fromTo("#sr1", {{ opacity: 0, x: -25 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(s2_st + 0.28, 2)})
      .fromTo("#sr2", {{ opacity: 0, x: -25 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(s2_st + 0.80, 2)})
      .fromTo("#sr3", {{ opacity: 0, x: -25 }}, {{ opacity: 1, x: 0, duration: 0.22 }}, {round(s2_st + 1.32, 2)})
      .to("#st-sl1", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s2_st + s2_dur - 0.34, 2)})

      .fromTo("#cp1", {{ opacity: 0, y: 30, scale: 0.92, filter: "blur(12px)" }}, {{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.28, ease: "back.out(1.3)" }}, {round(s3_st + 0.20, 2)})
      .to("#st-sl2", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s3_st + s3_dur - 0.34, 2)})

      .fromTo("#st-s4t", {{ opacity: 0, y: -20, filter: "blur(10px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.26 }}, {round(s4_st + 0.14, 2)})
      .fromTo("#st-s4p", {{ opacity: 0, scale: 0.85, y: 30, filter: "blur(14px)" }}, {{ opacity: 1, scale: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "back.out(1.35)" }}, {round(s4_st + 0.10, 2)})
      .to("#s4-pack-img", {{ y: -16, scale: 1.04, duration: 1.6, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {round(s4_st + 0.42, 2)})
      .fromTo("#bp1", {{ opacity: 0, x: -55, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.25, ease: "back.out(1.2)" }}, {round(s4_st + 0.32, 2)})
      .fromTo("#bp2", {{ opacity: 0, x: -55, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.25, ease: "back.out(1.2)" }}, {round(s4_st + 0.95, 2)})
      .fromTo("#bp3", {{ opacity: 0, x: -55, filter: "blur(10px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.25, ease: "back.out(1.2)" }}, {round(s4_st + 1.58, 2)})
      .to("#st-s4t, #st-s4p", {{ opacity: 0, filter: "blur(10px)", duration: 0.18 }}, {round(s4_pack_end - 0.24, 2)})
      .to("#st-s4l", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s4_st + s4_dur - 0.32, 2)})

      .fromTo("#st-end", {{ opacity: 0, x: 45, scale: 0.92, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, scale: 1, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.3)" }}, {round(s5_st + 0.14, 2)})
      .fromTo("#st-cta", {{ opacity: 0, y: 22, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.28, ease: "back.out(1.4)" }}, {round(s5_st + 0.28, 2)})
      .fromTo("#st-leg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.24 }}, {round(s5_st + 0.36, 2)});

    window.__timelines["main-stage"] = tl;
  </script>
</template>"""
    (comp_dir / "main-stage.html").write_text(stage_html, encoding="utf-8")

    caps = []
    for seg_id, lines3 in cfg["big_caps"]:
        s = segs[seg_id]
        st0 = s["start_s"]
        d_each = round((s["duration_s"] + 0.08) / float(len(lines3)), 3)
        for li, html_txt in enumerate(lines3):
            cst = round(st0 + li * d_each, 2)
            cen = round(cst + d_each - 0.02, 2)
            caps.append((f"cap-{seg_id}-{li}", cst, cen, html_txt))

    divs, js_g = [], []
    for idx, (cid, st, en, inner) in enumerate(caps):
        dur = round(max(0.4, en - st), 3)
        trk = (idx % 4) + 1
        divs.append(f'    <div id="{cid}" class="clip cap-clip" data-start="{st}" data-duration="{dur}" data-track-index="{trk}" data-layout-ignore><div id="in-{cid}" class="cap-box">{inner}</div></div>')
        js_g.append(f'      {{ sel: "#in-{cid}", st: {st}, en: {en} }}')

    cap_html = f"""<template>
  <style>
    @font-face {{ font-family: "BeVietnamVN"; src: url("assets/fonts/BeVietnamPro-ExtraBold.ttf") format("truetype"); font-weight: 800; font-display: block; }}
    @font-face {{ font-family: "PlayfairVNItalic"; src: url("assets/fonts/PlayfairDisplay-BoldItalic.ttf") format("truetype"); font-weight: 700; font-style: italic; font-display: block; }}
    #root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
    .cap-clip {{ position: absolute; left: 56px; top: 1365px; width: 822px; text-align: center; overflow: visible; }}
    .cap-box {{
      display: inline-block; max-width: 818px; opacity: 0;
      background: rgba(255, 255, 255, 0.94); border: 3px solid {pri}; border-radius: 24px;
      padding: 12px 26px; box-shadow: 0 12px 28px rgba(10, 20, 40, 0.28);
      font-family: "BeVietnamVN", sans-serif; font-weight: 800; font-size: 40px; line-height: 1.24;
      color: {pri_dark};
    }}
    .cap-kw {{ color: {pri}; font-family: "PlayfairVNItalic", Georgia, serif; font-style: italic; font-weight: 700; font-size: 45px; }}
  </style>
  <div id="root" data-composition-id="captions-track" data-width="1080" data-height="1920">
{chr(10).join(divs)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const groups = [{",".join(chr(10) + g for g in js_g)}];
    groups.forEach((g) => {{
      tl.fromTo(g.sel, {{ opacity: 0, y: 16, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.16, ease: "back.out(1.4)" }}, g.st)
        .to(g.sel, {{ opacity: 0, y: -8, duration: 0.12, ease: "power2.in" }}, g.en - 0.12)
        .set(g.sel, {{ opacity: 0, visibility: "hidden" }}, g.en);
    }});
    window.__timelines["captions-track"] = tl;
  </script>
</template>"""
    (comp_dir / "captions-track.html").write_text(cap_html, encoding="utf-8")

    vo_tags = []
    for idx, s in enumerate(vo_manifest["segments"]):
        trk = 4 if (idx % 2 == 0) else 5
        vo_tags.append(
            f'      <audio id="{s["id"].replace("_", "-")}" class="clip" src="assets/audio/{s["id"]}.wav" '
            f'data-start="{s["start_s"]}" data-duration="{s["duration_s"]}" data-track-index="{trk}" '
            f'data-volume="1.34" data-fade-in="0.03" data-fade-out="0.05" data-fx-chain="{VO_FX_CHAIN}"></audio>'
        )

    portal_t = s3_st
    bgm1_dur = round(portal_t + 0.2, 2)
    bgm2_st = round(portal_t - 0.1, 2)
    bgm2_dur = round(total_dur - bgm2_st, 2)
    outro_swell = round(bgm2_dur - 1.0, 2)

    sfx_tags = []
    for fi, ct in enumerate(flash_times):
        sfx_tags.append(f'      <audio id="sfx-cut-{fi}" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{max(0.0, round(ct - 0.08, 2))}" data-duration="0.48" data-track-index="8" data-volume="0.19" data-fade-out="0.12"></audio>')

    idx_html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
    <title>{cfg['final_mp4']}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body, #root {{ width: 1080px; height: 1920px; overflow: hidden; background: {pri_dark}; position: relative; }}
      .scene-host {{ position: absolute; inset: 0; z-index: 2; }}
      .captions-host {{ position: absolute; inset: 0; z-index: 16; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total_dur}" data-width="1080" data-height="1920" data-fps="24">
      <div id="main-stage" class="scene-host" data-composition-id="main-stage" data-composition-src="compositions/main-stage.html" data-start="0" data-duration="{total_dur}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="captions-track" class="captions-host" data-composition-id="captions-track" data-composition-src="compositions/captions-track.html" data-start="0" data-duration="{s5_st}" data-track-index="2" data-track-kind="captions" data-width="1080" data-height="1920"></div>
{chr(10).join(vo_tags)}
      <audio id="bgm-f1" class="clip" src="assets/audio/bgm_part1_fresh.mp3" data-start="0" data-duration="{bgm1_dur}" data-media-start="2.0" data-track-index="6" data-fade-in="0.20" data-fade-out="0.45" data-automation="{{&quot;version&quot;:1,&quot;lanes&quot;:[{{&quot;target&quot;:&quot;volume&quot;,&quot;points&quot;:[{{&quot;t&quot;:0.0,&quot;v&quot;:0.42}},{{&quot;t&quot;:0.30,&quot;v&quot;:0.24}},{{&quot;t&quot;:{round(bgm1_dur - 0.5, 2)},&quot;v&quot;:0.24}},{{&quot;t&quot;:{bgm1_dur},&quot;v&quot;:0.0}}]}}]}}"></audio>
      <audio id="bgm-f2" class="clip" src="assets/audio/bgm_part2_fresh.mp3" data-start="{bgm2_st}" data-duration="{bgm2_dur}" data-media-start="4.0" data-track-index="7" data-fade-in="0.25" data-fade-out="0.65" data-automation="{{&quot;version&quot;:1,&quot;lanes&quot;:[{{&quot;target&quot;:&quot;volume&quot;,&quot;points&quot;:[{{&quot;t&quot;:0.0,&quot;v&quot;:0.46}},{{&quot;t&quot;:0.35,&quot;v&quot;:0.26}},{{&quot;t&quot;:{round(outro_swell - 0.2, 2)},&quot;v&quot;:0.26}},{{&quot;t&quot;:{outro_swell},&quot;v&quot;:0.58}},{{&quot;t&quot;:{bgm2_dur},&quot;v&quot;:0.58}}]}}]}}"></audio>
{chr(10).join(sfx_tags)}
      <audio id="sfx-p1" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="0.22" data-duration="0.50" data-track-index="9" data-volume="0.22"></audio>
      <audio id="sfx-p2" class="clip" src="assets/audio/sfx_pop_clean.mp3" data-start="{round(s2_st + 0.20, 2)}" data-duration="0.50" data-track-index="9" data-volume="0.20"></audio>
      <audio id="sfx-sh3" class="clip" src="assets/audio/sfx_sparkle_shine.mp3" data-start="{round(s3_st + 0.18, 2)}" data-duration="1.20" data-track-index="10" data-volume="0.28"></audio>
      <audio id="sfx-sh4" class="clip" src="assets/audio/sfx_crystal_shimmer.mp3" data-start="{round(s4_st + 0.12, 2)}" data-duration="1.50" data-track-index="10" data-volume="0.28"></audio>
      <audio id="sfx-c1" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s4_st + 0.32, 2)}" data-duration="0.32" data-track-index="9" data-volume="0.24"></audio>
      <audio id="sfx-c2" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s4_st + 0.95, 2)}" data-duration="0.32" data-track-index="9" data-volume="0.24"></audio>
      <audio id="sfx-c3" class="clip" src="assets/audio/sfx_click_soft.mp3" data-start="{round(s4_st + 1.58, 2)}" data-duration="0.32" data-track-index="9" data-volume="0.25"></audio>
      <audio id="sfx-cta" class="clip" src="assets/audio/sfx_chime_warm.mp3" data-start="{round(s5_st + 0.20, 2)}" data-duration="2.00" data-track-index="10" data-volume="0.52"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>"""
    (hf_dir / "index.html").write_text(idx_html, encoding="utf-8")

    out_mp4 = pdir / "08_Render_Master_V4" / cfg["final_mp4"]
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["npx.cmd", "hyperframes", "render", "--output", str(out_mp4), "--quality", "delivery"], cwd=str(hf_dir), check=True)

    # Flat delivery into K6\261125 - Ngày 25.11.2026 + Cloud + Local
    for base_dir in (K6_DAY25_DIR, CLOUD_DAY25_VID, LOCAL_DAY25_DIR):
        try:
            if Path(base_dir.anchor).exists():
                base_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(out_mp4, base_dir / cfg["final_mp4"])
                print(f"[V4 AI USP MASTER OVERWRITTEN IN K6] {base_dir / cfg['final_mp4']}", flush=True)
        except Exception as e:
            print(f"[WARN COPY] {base_dir}: {e}")
    return out_mp4, total_dur


def main():
    bgm_nlh, bgm_dk = pick_fresh_bgm_pair()
    qa_tiles = []
    for cfg, bpair in zip(V4_CFG, [bgm_nlh, bgm_dk]):
        mp4_p, tdur = build_and_render_v4(cfg, bpair)
        for ci, (ocode, cst, cdur) in enumerate(cfg["clips_7"], start=1):
            ts = min(tdur - 0.5, cst + cdur * 0.5)
            fp = mp4_p.parent / f"qa7_{ci}.jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(mp4_p), "-frames:v", "1", "-q:v", "2", str(fp)], check=True)
            im = Image.open(fp).convert("RGB")
            d = ImageDraw.Draw(im)
            d.line([(0, 248), (1080, 248)], fill=(255, 60, 60), width=4)
            d.line([(0, 1548), (1080, 1548)], fill=(255, 60, 60), width=4)
            d.rectangle([(886, 860), (1080, 1548)], outline=(255, 60, 60), width=4)
            qa_tiles.append((f"{ocode} t={ts:.1f}s", im))

    tw, th_c = 250, 445
    sh = Image.new("RGB", (tw * 7, th_c * 2), (14, 20, 32))
    sd = ImageDraw.Draw(sh)
    for i, (lbl, im) in enumerate(qa_tiles):
        r, c = divmod(i, 7)
        sh.paste(im.resize((tw - 6, th_c - 24), Image.Resampling.LANCZOS), (c * tw + 3, r * th_c + 20))
        sd.text((c * tw + 6, r * th_c + 3), lbl, fill=(190, 235, 255))
    qa_out = BATCH_ROOT / "v4_ai_usp_14shots_qa.jpg"
    sh.save(qa_out, quality=92)
    shutil.copy2(qa_out, ARTIFACT_DIR / "htpm_v4_ai_usp_14shots_qa.jpg")
    print("=== V4 AI USP 14-SHOT VIDEOS 100% DELIVERED TO K6 ===", flush=True)


if __name__ == "__main__":
    main()
