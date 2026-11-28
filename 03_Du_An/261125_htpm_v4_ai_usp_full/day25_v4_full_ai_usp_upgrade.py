# -*- coding: utf-8 -*-
"""
UPGRADE TOÀN BỘ 10 VIDEO NGÀY 25/11/2026 (`261125 - Ngày 25.11.2026`) LÊN CHUẨN V4 AI USP PRO:
1. 100% VIDEO CHUYỂN ĐỘNG AI THẬT (Google Flow Omni 1.2 Flash chế độ Thành phần — 0% ảnh tĩnh Ken Burns lặp cảnh!).
2. 100% CHUẨN GƯƠNG MẶT THẬT CHỊ NGUYỄN THỊ HẰNG (`Chị Hằng RTFN/IMG_5632.jpg` — giữ nguyên mặt bầu tròn phúc hậu, cấm gọt V-line!).
3. CẤU TRÚC 5 HỒI VIDEO QUẢNG CÁO USP CHUẨN DƯỢC MỸ PHẨM:
   - S01: AI Hook Chị Hằng chuẩn mặt thật tại Nha Trang + Đại tự Hook 84px 2 dòng
   - S02: AI 3D CGI Cơ chế Y khoa / Vấn đề trực quan riêng từng sản phẩm + Bảng 3 Dấu hiệu 818px quét sáng
   - S03: AI Giải pháp Chị Hằng chuẩn mặt thật cầm sản phẩm + Thẻ lựa chọn kèm ảnh cutout gốc
   - S04: AI 3D Macro Thảo dược / Hoạt chất + Bục 3D Sản phẩm Studio thật 100% (`SP_*_CUTOUT.png`) + 3 Thẻ công dụng USP
   - S05: AI End-Card Chị Hằng chuẩn mặt thật bên trái vịnh Nha Trang + Khung End-Card chính hãng + Nút CTA lớn
4. ĐẦY ĐỦ LỚP PHỦ 4K (`Golden Bokeh`, `Window Sun Rays`, `Pearl Sparkles`, `Anamorphic Flare` chế độ `Screen`), Thanh tiến trình động, Pill thương hiệu `HẰNG THU PHARMA`, Con dấu xoay `100% CHÍNH HÃNG`, Nhạc nền mới tươi sáng & 100% Vùng An Toàn TikTok × Reels!
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

THIS_DIR = Path(r"d:\AI\full studio\output\htpm-ngay-261125")
sys.path.insert(0, str(THIS_DIR))
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")

from day25_master_spec import (
    BATCH_ROOT, PROD_DIR, BRAND_KIT, K6_DAY25_DIR, CLOUD_DAY25_VID, LOCAL_DAY25_DIR, SLOTS_261125,
)
from ai_ref_video import (
    cleanup_exported_canvas_nodes,
    export_canvas_nodes_to_files,
    generate_scene_assets_pipelined,
    stage_local_ref_image_once,
)

V4_COUPLE_ROOT = Path(r"d:\AI\full studio\output\htpm-ai-usp-v4-261125")
PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
OVERLAYS_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "video_overlays_4k"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
ARTIFACT_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682")

USP_REFS_DIR = BATCH_ROOT / "02_V4_USP_Refs"
USP_BOARDS_DIR = BATCH_ROOT / "00_V4_USP_Boards"
for _d in (USP_REFS_DIR, USP_BOARDS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

STYLE_LOCK = (
    "Ultra-clean 8K commercial pharmaceutical & wellness TVC cinematography, crystal-clear high-key natural coastal Nha Trang morning daylight "
    "(5400K airy sunlit clarity, turquoise-blue ocean bay & lush tropical palms in soft bokeh, zero muddy yellow cast, zero dark shadows, natural skin pores). "
)

CHIHANG_LOCK = (
    "[STRICT 100% REAL FACE IDENTITY LOCK — CEO NGUYEN THI HANG]: Keep 100.0% the EXACT SAME Vietnamese woman's face from the portrait reference: "
    "preserve her unmistakable warm round-oval face shape with full soft cheeks and natural gently-rounded jawline (STRICTLY DO NOT slim her face, DO NOT create a narrow V-chin or sharp pointed jaw!), "
    "exact broad smooth forehead, softly arched natural dark eyebrows, warm expressive dark-brown almond eyes with natural double eyelids, natural rounded Vietnamese nose tip, "
    "bright warm coral-red smile, and glossy dark-brown shoulder-length wavy hair. "
    "Portray her with a tall statuesque 170cm posture and a full-proportioned, curvy feminine hourglass S-line silhouette in tailored luxury attire. "
)

ZERO_LIP = " Natural calm breathing, lips gently closed or smiling warmly, zero speaking, zero lip-syncing, keep 100% exact facial features from reference, crystal-clear Nha Trang daylight, no text."

# 3D CGI Cơ chế Y khoa (S02) & 3D Macro Thảo dược/Hoạt chất (S04) riêng cho từng sản phẩm!
SKU_3D_USP_PROMPTS = {
    1: (  # LT Plus
        "Vertical 9:16 high-end 3D CGI feminine intimate-care USP visualization: a luminous translucent pearl-pink protective moisture shield and pure crystal pH-balance droplets gently repelling dark micro-impurities in an airy sunlit rose-ivory studio.",
        "High-end 3D CGI slow orbit: pure crystal pH-balance droplets and a luminous pearl-pink moisture barrier shimmer gently in sunlit studio light.",
        "Vertical 9:16 luxury 3D botanical USP macro cinematography: fresh dewy pink lotus petals, white chamomile blossoms, and crystal-clear rosewater droplets levitating above sunlit turquoise water ripples.",
        "Luxury 3D botanical macro slow-motion swirl: dewy pink lotus petals, chamomile blossoms, and pure water droplets float gracefully in warm morning sunbeams.",
    ),
    2: (  # Gel Phụ Khang
        "Vertical 9:16 high-end 3D CGI skincare & hygiene USP visualization: ultra-fine airy silk micro-foam bubbles and pure aqua-pink cooling mist gently refreshing a luminous pearl-satin surface in sunlit white studio light.",
        "High-end 3D CGI slow-motion glide: airy silk micro-foam bubbles and pure cooling mist droplets float smoothly in sunlit studio light.",
        "Vertical 9:16 luxury 3D botanical USP macro cinematography: fresh white orchids, green tea buds, mint leaves, and sparkling crystal essence droplets floating over sunlit water ripples.",
        "Luxury 3D botanical macro slow orbit: white orchid petals, green tea leaves, and crystal essence droplets shimmer in warm morning sunlight.",
    ),
    3: (  # Dạ Dày HT
        "Vertical 9:16 high-end 3D CGI digestive wellness USP visualization: a clean luminous translucent glass stomach silhouette in an airy sunlit ivory studio, where soothing golden-emerald herbal nectar coats and calms warm amber acid waves.",
        "High-end 3D CGI medical commercial camera orbit: soothing golden-emerald herbal streams flow smoothly inside the translucent crystal stomach sculpture, calming amber waves into peaceful glow.",
        "Vertical 9:16 luxury 3D herbal USP macro cinematography: fresh golden-orange turmeric slices (Nghệ), lush green Dạ cẩm leaves, Hoàng liên roots, and glowing amber herbal essence droplets floating over white travertine stone.",
        "Luxury 3D herbal macro slow-motion swirl: golden turmeric slices, green herbal leaves, and amber essence droplets float gracefully in warm sunbeams.",
    ),
    5: (  # Romance VIP
        "Vertical 9:16 high-end 3D CGI feminine pH-hydration USP visualization: flowing ruby-blush silk waves and luminous moisture micro-spheres forming a soft hydrating veil in an airy sunlit pearl-white studio.",
        "High-end 3D CGI slow-motion wave: ruby-blush silk ribbons and luminous moisture micro-spheres glide harmoniously in bright sunlit studio light.",
        "Vertical 9:16 luxury 3D botanical USP macro cinematography: velvet ruby-red rose petals, translucent aloe vera gel crystals, and pure sunlit water droplets levitating over sparkling rose-tinted ripples.",
        "Luxury 3D botanical macro slow orbit: dewy ruby rose petals, clear aloe crystals, and sparkling water droplets shimmer in morning sunlight.",
    ),
    6: (  # Legend WhiteSkin
        "Vertical 9:16 high-end 3D CGI dermal brightening USP visualization: clean translucent crystal skin-cell layers in a sunlit ice-blue studio awakening with glowing pearl-white L-Glutathione & golden Vitamin E spheres while deflecting harsh UV rays.",
        "High-end 3D CGI skincare slow push-in: glowing pearl-white L-Glutathione and golden Vitamin E light spheres illuminate translucent crystal dermal layers smoothly.",
        "Vertical 9:16 luxury 3D skincare USP macro cinematography: iridescent white pearls, golden Vitamin E essence spheres, and crystal-blue NMN water droplets floating above sunlit ocean-blue ripples.",
        "Luxury 3D skincare macro slow orbit: iridescent pearls, golden Vitamin E spheres, and crystal-blue droplets float gracefully in bright coastal sunlight.",
    ),
    7: (  # Viên Đặt Phụ Khoa Hộp Xanh
        "Vertical 9:16 high-end 3D CGI postpartum feminine-care USP visualization: graceful emerald-jade and pearl-white silk ribbons intertwining into a firm, elastic, luminous harmony ring in an airy sunlit mint-ivory studio.",
        "High-end 3D CGI slow orbit: emerald-jade and pearl-white silk ribbons intertwine smoothly with sparkling purity droplets in sunlit studio light.",
        "Vertical 9:16 luxury 3D herbal USP macro cinematography: fresh dewy green betel leaves (Trầu không), green tea buds, white jasmine blossoms, and pure emerald-tinted water droplets floating in morning sunbeams.",
        "Luxury 3D herbal macro slow-motion swirl: fresh green betel leaves, jasmine blossoms, and crystal dewdrops float gracefully over sunlit water ripples.",
    ),
    8: (  # Romance Love
        "Vertical 9:16 high-end 3D CGI feminine rejuvenation USP visualization: soft romantic magenta-rose satin ribbons and glowing rose-gold hydration droplets swirling into a supple, radiant pearl heart-wave in sunlit blush studio light.",
        "High-end 3D CGI slow-motion glide: magenta-rose satin ribbons and rose-gold hydration droplets flow smoothly and tenderly in warm sunlit studio light.",
        "Vertical 9:16 luxury 3D botanical USP macro cinematography: blooming blush-pink English roses, soft pink silk waves, and luminous rose-essence droplets levitating over crystal pearl-marble.",
        "Luxury 3D botanical macro slow orbit: blush-pink rose petals, soft silk waves, and glowing rose-essence droplets shimmer in morning sunlight.",
    ),
    10: (  # CEO Nguyễn Thị Hằng — Hệ Sinh Thái HTPM
        "Vertical 9:16 high-end 3D CGI brand-ecosystem USP visualization: a luminous crystal-blue and champagne-gold 3D light map of Vietnam in an airy sunlit glass studio, with radiant golden wellness beams expanding from coastal Nha Trang across the country.",
        "High-end 3D CGI brand commercial slow push-in: radiant golden and ocean-blue light beams expand smoothly across the crystal 3D Vietnam map in bright sunlit studio light.",
        "Vertical 9:16 luxury 3D brand showcase background: sunlit white travertine marble podium overlooking turquoise Nha Trang bay surrounded by white orchids, golden sunbeams, and sparkling sea bokeh.",
        "Luxury commercial slow camera drift across the sunlit white marble Nha Trang terrace with white orchids and sparkling turquoise ocean bokeh.",
    ),
}

OVERLAY_PAIRS = [
    ("01_Golden_Dust_Bokeh_9x16.mp4", "03_Warm_Window_Sun_Rays_9x16.mp4"),
    ("05_Soft_Pearl_Sparkles_Bling_9x16.mp4", "04_Anamorphic_Gold_Rose_Flare_9x16.mp4"),
]


def transcode_cfr24_nvenc(src_mp4: Path, dst_mp4: Path, min_dur_s: float):
    dst_mp4.parent.mkdir(parents=True, exist_ok=True)
    pr = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "json", str(src_mp4)]
        ).decode("utf-8")
    )
    raw_dur = float(pr["format"]["duration"])
    stretch = max(1.0, round((min_dur_s + 0.55) / max(1.0, raw_dur), 4))
    vf_chain = f"setpts={stretch}*PTS,fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(src_mp4),
            "-vf", vf_chain, "-r", "24", "-fps_mode", "cfr", "-an",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-g", "24",
            str(dst_mp4),
        ],
        check=True,
    )


def build_single_combo_board(face_path: Path, prod_path: Path, out_p: Path) -> Path:
    if out_p.exists() and out_p.stat().st_size > 80_000:
        return out_p
    im_f = ImageOps.fit(Image.open(face_path).convert("RGB"), (680, 920), Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    im_p = Image.open(prod_path).convert("RGBA")
    if im_p.getbbox():
        im_p = im_p.crop(im_p.getbbox())
    im_p.thumbnail((420, 840), Image.Resampling.LANCZOS)
    board = Image.new("RGBA", (1160, 920), (250, 252, 255, 255))
    board.paste(im_f.convert("RGBA"), (0, 0))
    board.alpha_composite(im_p, (700 + (440 - im_p.width) // 2, (920 - im_p.height) // 2))
    board.convert("RGB").save(out_p, quality=96)
    return out_p


def generate_5_usp_clips_for_slot(sl: dict, nid_hang: str):
    idx = sl["idx"]
    vkey = sl["vkey"]
    code = sl["code"]
    vdir = BATCH_ROOT / vkey / "07_HyperFrames_Project" / "assets" / "videos"
    vdir.mkdir(parents=True, exist_ok=True)
    vo_m = json.loads((BATCH_ROOT / vkey / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))
    segs = vo_m["segments"]

    # Reuse V4 AI USP solo clips for V04 (Điều Kinh HT) & V09 (Ngọc Long Hoàn)!
    if idx == 4:
        src_v4 = V4_COUPLE_ROOT / "c02_dieu_kinh_ht" / "07_HyperFrames_Project" / "assets" / "videos"
        mapping = [("DK4_C01", f"{code}_U01", segs[0]["shot_duration_s"]), ("DK4_C03", f"{code}_U02", segs[1]["shot_duration_s"]),
                   ("DK4_C04", f"{code}_U03", segs[2]["shot_duration_s"]), ("DK4_C05", f"{code}_U04", segs[3]["shot_duration_s"]),
                   ("DK4_C07", f"{code}_U05", segs[4]["shot_duration_s"])]
        for sc, dc, sdur in mapping:
            transcode_cfr24_nvenc(src_v4 / f"{sc}.mp4", vdir / f"{dc}.mp4", float(sdur))
        return
    if idx == 9:
        src_v4 = V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "07_HyperFrames_Project" / "assets" / "videos"
        mapping = [("NLH4_C01", f"{code}_U01", segs[0]["shot_duration_s"]), ("NLH4_C03", f"{code}_U02", segs[1]["shot_duration_s"]),
                   ("NLH4_C05", f"{code}_U03", segs[2]["shot_duration_s"]), ("NLH4_C04", f"{code}_U04", segs[3]["shot_duration_s"]),
                   ("NLH4_C01", f"{code}_U05", segs[4]["shot_duration_s"])]
        # Note: for V09 U05, generate 1 dedicated solo NLH End-Card clip if not cached so 0% clip reuse!
        for sc, dc, sdur in mapping[:4]:
            transcode_cfr24_nvenc(src_v4 / f"{sc}.mp4", vdir / f"{dc}.mp4", float(sdur))
        u05_dst = vdir / f"{code}_U05.mp4"
        if not (u05_dst.exists() and u05_dst.stat().st_size > 250_000):
            res9 = generate_scene_assets_pipelined([{
                "scene_id": "d25_v09_u05",
                "image_prompt": f"[D25 V09_U05] {STYLE_LOCK}{CHIHANG_LOCK}{sl['outfit']}Vertical 9:16 sunlit Nha Trang ocean-view balcony SOLO End-Card portrait: position CEO Nguyen Thi Hang standing gracefully on the LEFT HALF (X=8%..50%) smiling warmly with open turquoise bay on the right.",
                "motion_prompt": "Poised sunlit Nha Trang ocean-view balcony Solo End-Card push-in: CEO Nguyen Thi Hang stands gracefully on the left half smiling warmly." + ZERO_LIP,
                "ratio": "9:16", "seconds": 8, "reference_node_ids": [nid_hang],
            }], max_workers=1)
            raw9 = BATCH_ROOT / vkey / "03_Flow_Raw" / f"{code}_U05_raw.mp4"
            export_canvas_nodes_to_files({res9[0]["vid_node_id"]: str(raw9)}, timeout_s=60)
            transcode_cfr24_nvenc(raw9, u05_dst, float(segs[4]["shot_duration_s"]))
            cleanup_exported_canvas_nodes([res9[0]["img_node_id"], res9[0]["vid_node_id"]])
        return

    # Check which of U01..U05 still need generation for this SKU
    hang_rtfn_p = V4_COUPLE_ROOT / "00_Clean_Sources" / "chihang_rtfn_5632.jpg"
    b_combo = build_single_combo_board(hang_rtfn_p, PROD_DIR / sl["cutout"], USP_BOARDS_DIR / f"combo_{vkey}.jpg")
    nid_combo = stage_local_ref_image_once(str(b_combo), f"d25_cb_{code.lower()}", x=420, y=160)

    s2_img, s2_mot, s4_img, s4_mot = SKU_3D_USP_PROMPTS[idx]
    outfit = sl["outfit"]

    five_defs = [
        (1, f"d25_{code.lower()}_u01", [nid_hang],
         f"[D25 {code}_U01] {STYLE_LOCK}{CHIHANG_LOCK}{outfit}Vertical 9:16 medium front-facing shot {sl['scene_post']}. Frame CEO Nguyen Thi Hang's head cleanly around Y=26%..44% keeping 100% her exact full round-oval face, full soft cheeks, and gentle empathetic expression.",
         f"Smooth sunlit cinematic slow dolly-in {sl['scene_post']}; CEO Nguyen Thi Hang looks warmly at the camera with gentle natural poise." + ZERO_LIP),
        (2, f"d25_{code.lower()}_u02", None, f"[D25 {code}_U02] {STYLE_LOCK}{s2_img}", s2_mot),
        (3, f"d25_{code.lower()}_u03", [nid_combo],
         f"[D25 {code}_U03] {STYLE_LOCK}{CHIHANG_LOCK}{outfit}Vertical 9:16 medium front-facing commercial shot {sl['scene_vid']}: CEO Nguyen Thi Hang (LEFT half of reference — keep 100% her exact full round-oval face and radiant smile) proudly holds the product package (RIGHT half of reference) at chest height.",
         f"Warm uplifting dolly-in {sl['scene_vid']}; CEO Nguyen Thi Hang smiles radiantly while holding the product package steadily." + ZERO_LIP),
        (4, f"d25_{code.lower()}_u04", None, f"[D25 {code}_U04] {STYLE_LOCK}{s4_img}", s4_mot),
        (5, f"d25_{code.lower()}_u05", [nid_hang],
         f"[D25 {code}_U05] {STYLE_LOCK}{CHIHANG_LOCK}{outfit}Vertical 9:16 sunlit Nha Trang ocean-view terrace SOLO End-Card portrait: position CEO Nguyen Thi Hang standing gracefully on the LEFT HALF (X=8%..50%) keeping 100% her exact full round-oval face and warm smile, leaving open turquoise ocean & palm bokeh on the right.",
         "Poised sunlit Nha Trang ocean-terrace Solo End-Card slow push-in: CEO Nguyen Thi Hang stands gracefully on the left half beaming warmly." + ZERO_LIP),
    ]

    todo_scenes = []
    todo_meta = {}
    for s_num, sid, r_nids, iprompt, mprompt in five_defs:
        dst_mp4 = vdir / f"{code}_U0{s_num}.mp4"
        if dst_mp4.exists() and dst_mp4.stat().st_size > 250_000:
            continue
        todo_scenes.append({
            "scene_id": sid, "image_prompt": iprompt, "motion_prompt": mprompt,
            "ratio": "9:16", "seconds": 8, "reference_node_ids": r_nids,
        })
        todo_meta[sid] = (s_num, dst_mp4, float(segs[s_num - 1]["shot_duration_s"]))

    if not todo_scenes:
        print(f"[SKIP CACHED 5/5 USP CLIPS] {vkey}", flush=True)
        return

    print(f"\n=== STREAMING {len(todo_scenes)} AI USP SCENES (ChatGPT -> Flow) FOR {vkey} ===", flush=True)
    res_list = generate_scene_assets_pipelined(todo_scenes, max_workers=3)

    exp_map = {}
    clean_ids = []
    for r in res_list:
        sid = r["scene_id"]
        s_num, _, _ = todo_meta[sid]
        raw_mp4 = BATCH_ROOT / vkey / "03_Flow_Raw" / f"{code}_U0{s_num}_raw.mp4"
        exp_map[r["vid_node_id"]] = str(raw_mp4)
        exp_map[r["img_node_id"]] = str(USP_REFS_DIR / f"{sid}.png")
        clean_ids.extend([r["img_node_id"], r["vid_node_id"]])

    export_canvas_nodes_to_files(exp_map, timeout_s=90)
    for r in res_list:
        sid = r["scene_id"]
        s_num, dst_mp4, sdur = todo_meta[sid]
        raw_mp4 = BATCH_ROOT / vkey / "03_Flow_Raw" / f"{code}_U0{s_num}_raw.mp4"
        transcode_cfr24_nvenc(raw_mp4, dst_mp4, sdur)
        print(f"  [OK {code}_U0{s_num}.mp4] {dst_mp4.stat().st_size//1024} KB", flush=True)

    cleanup_exported_canvas_nodes(clean_ids)


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


def list_fresh_bgms():
    z_tvc = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng")
    z_aco = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)\05_Acoustic - Guitar - Nhẹ Nhàng Mộc Mạc")
    fb = [
        AUDIO_BUNDLE_DIR / "bgm_sunny_carefree.mp3",
        AUDIO_BUNDLE_DIR / "bgm_coconut_groove_tvc.mp3",
        AUDIO_BUNDLE_DIR / "bgm_fresh_wellness_tvc.mp3",
    ]
    found_tvc = sorted([f for f in z_tvc.rglob("*.mp3") if 1_200_000 < f.stat().st_size < 12_000_000]) if z_tvc.exists() else []
    found_aco = sorted([f for f in z_aco.rglob("*.mp3") if 1_200_000 < f.stat().st_size < 12_000_000]) if z_aco.exists() else []
    return (found_aco or fb), (found_tvc or fb)


def render_v4_pro_slot(sl: dict, aco_list: list, tvc_list: list):
    idx = sl["idx"]
    vkey = sl["vkey"]
    code = sl["code"]
    pdir = BATCH_ROOT / vkey
    vo_dir = pdir / "06_Audio_Voiceover"
    hf_dir = pdir / "07_HyperFrames_Project"
    comp_dir = hf_dir / "compositions"
    img_dir = hf_dir / "assets" / "images"
    aud_dir = hf_dir / "assets" / "audio"
    vid_dir = hf_dir / "assets" / "videos"
    fnt_dir = hf_dir / "assets" / "fonts"
    for d in (comp_dir, img_dir, aud_dir, vid_dir, fnt_dir):
        d.mkdir(parents=True, exist_ok=True)

    vo_manifest = json.loads((vo_dir / "vo_manifest.json").read_text(encoding="utf-8"))
    for s in vo_manifest["segments"]:
        shutil.copy2(vo_dir / f"{s['id']}.wav", aud_dir / f"{s['id']}.wav")
    for f in AUDIO_BUNDLE_DIR.glob("sfx_*.*"):
        shutil.copy2(f, aud_dir / f.name)
    for f in FONTS_BUNDLE_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in (".ttf", ".otf", ".woff2", ".css"):
            shutil.copy2(f, fnt_dir / f.name)

    b1 = aco_list[(idx - 1) % len(aco_list)]
    b2 = tvc_list[(idx - 1) % len(tvc_list)]
    shutil.copy2(b1, aud_dir / "bgm_part1_fresh.mp3")
    shutil.copy2(b2, aud_dir / "bgm_part2_fresh.mp3")
    shutil.copy2(PROD_DIR / sl["cutout"], img_dir / sl["cutout"])
    logo_src = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124\10_Bai_Thiet_Ke_Soft_Editorial\ht_logo_33mp_clean.png")
    shutil.copy2(logo_src if logo_src.exists() else (BRAND_KIT / "logos_png" / "ht_logo_official.png"), img_dir / "ht_logo_clean.png")

    ov1, ov2 = OVERLAY_PAIRS[(idx - 1) % len(OVERLAY_PAIRS)]
    shutil.copy2(OVERLAYS_DIR / ov1, vid_dir / ov1)
    shutil.copy2(OVERLAYS_DIR / ov2, vid_dir / ov2)

    segs_list = vo_manifest["segments"]
    segs = {s["id"]: s for s in segs_list}
    total_dur = vo_manifest["total_duration_s"]
    pri, pri_dark, pri_soft, grad_mid = sl["pri"], sl["pri_dark"], sl["pri_soft"], sl["grad_mid"]

    vid_tags, flash_times, rig_tweens = [], [], []
    for ci, s in enumerate(segs_list):
        ocode = f"{code}_U0{ci + 1}"
        cst = float(s["shot_start_s"])
        cdur = float(s["shot_duration_s"]) if ci < 4 else round(total_dur - cst, 2)
        trk = (ci % 2) + 1
        vid_tags.append(
            f'    <div id="rig-{ci}" class="cam-rig" data-layout-allow-overflow data-layout-allow-overlap>'
            f'<video data-color-grading="{COLOR_GRADE_CRYSTAL}" id="vid-{ci}" class="clip bg-video" src="assets/videos/{ocode}.mp4" '
            f'data-start="{cst}" data-duration="{cdur}" data-media-start="0.25" data-hf-media-start-basis="local" data-track-index="{trk}" muted playsinline></video></div>'
        )
        z0, z1 = (1.0, 1.045) if (ci % 2 == 0) else (1.045, 1.0)
        rig_tweens.append(f'    tl.fromTo("#rig-{ci}", {{ scale: {z0} }}, {{ scale: {z1}, duration: {cdur}, ease: "none" }}, {cst});')
        if ci > 0:
            flash_times.append(cst)

    s1_end = segs["vo_01"]["shot_end_s"]
    s2_st, s2_dur = segs["vo_02"]["shot_start_s"], segs["vo_02"]["shot_duration_s"]
    s3_st, s3_dur = segs["vo_03"]["shot_start_s"], segs["vo_03"]["shot_duration_s"]
    s4_st, s4_dur = segs["vo_04"]["shot_start_s"], segs["vo_04"]["shot_duration_s"]
    s5_st = segs["vo_05"]["shot_start_s"]
    s5_dur = round(total_dur - s5_st, 2)

    ov_tags = []
    t_cur, ov_idx = 0.0, 0
    while t_cur < total_dur - 0.5:
        chunk_d = round(min(4.8, total_dur - t_cur), 2)
        src_ov = ov1 if (ov_idx % 2 == 0) else ov2
        ov_tags.append(
            f'    <video id="ov-{ov_idx}" class="clip screen-overlay" src="assets/videos/{src_ov}" '
            f'data-start="{round(t_cur, 2)}" data-duration="{chunk_d}" data-media-start="0" data-hf-media-start-basis="local" '
            f'data-track-index="{3 + (ov_idx % 2)}" data-layout-ignore muted playsinline></video>'
        )
        t_cur += chunk_d
        ov_idx += 1

    # Split hook_hero cleanly into 2 giant lines if needed so font-size 78px fits 100% inside 822px Safe Zone!
    words = sl["hook_hero"].split()
    mid = max(1, len(words) // 2)
    hk_l1 = " ".join(words[:mid])
    hk_l2 = " ".join(words[mid:])

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
    .spin-seal-ring {{ position: absolute; inset: 0; border-radius: 50%; background: linear-gradient(135deg, {pri} 0%, {pri_dark} 100%); border: 4px dashed #ffffff; box-shadow: 0 12px 28px rgba(10,20,40,0.28); }}
    .spin-seal-core {{ position: relative; z-index: 2; text-align: center; color: #ffffff; line-height: 1.08; }}
    .spin-seal-core .sc1 {{ font-size: 15px; font-weight: 800; letter-spacing: 0.06em; }}
    .spin-seal-core .sc2 {{ font-family: "FrauncesVN", serif; font-size: 32px; font-weight: 900; }}
    .spin-seal-core .sc3 {{ font-size: 14px; font-weight: 800; background: rgba(255,255,255,0.22); padding: 2px 10px; border-radius: 99px; margin-top: 2px; display: inline-block; }}

    .hook-stage {{ position: absolute; left: 56px; top: 965px; width: 822px; z-index: 12; pointer-events: none; }}
    .hook-kicker-pill {{
      display: inline-block; background: {pri}; color: #ffffff; border: 3px solid #ffffff;
      padding: 10px 26px; border-radius: 999px; font-size: 27px; font-weight: 800;
      letter-spacing: 0.04em; text-transform: uppercase; box-shadow: 0 10px 24px rgba(10,20,40,0.28); margin-bottom: 14px;
    }}
    .hook-giant-line {{
      font-family: "FrauncesVN", Georgia, serif; font-size: 80px; font-weight: 900; line-height: 1.06;
      color: {pri}; paint-order: stroke fill; -webkit-text-stroke: 15px #ffffff;
      filter: drop-shadow(0 10px 22px rgba(10,20,40,0.36));
    }}

    .slide-card {{
      position: absolute; left: 58px; top: 930px; width: 818px; border-radius: 28px;
      background: rgba(255, 255, 255, 0.95); border: 3.5px solid {pri};
      box-shadow: 0 18px 40px rgba(10, 20, 40, 0.28); padding: 22px 28px; z-index: 12; overflow: hidden;
    }}
    .sheen-bar {{ position: absolute; top: -40%; left: -60%; width: 45%; height: 180%; background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.68) 50%, rgba(255,255,255,0) 100%); transform: skewX(-24deg); pointer-events: none; }}
    .slide-card-header {{ display: inline-flex; align-items: center; background: {pri}; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; padding: 8px 22px; border-radius: 999px; margin-bottom: 14px; }}
    .slide-row {{ display: flex; align-items: center; gap: 14px; font-size: 29px; font-weight: 800; color: {pri_dark}; padding: 8px 0; line-height: 1.25; }}
    .slide-badge-dot {{ width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 21px; font-weight: 800; flex-shrink: 0; background: {pri}; color: #ffffff; }}

    .slide-pill-stack {{ position: absolute; left: 58px; display: flex; flex-direction: column; gap: 14px; z-index: 12; }}
    .slide-pill {{
      display: inline-flex; align-items: center; gap: 16px; background: rgba(255, 255, 255, 0.96);
      border-left: 10px solid {pri}; border-top: 2px solid #fff; border-right: 2px solid {pri}; border-bottom: 2px solid {pri};
      border-radius: 22px; padding: 15px 26px; font-size: 29px; font-weight: 800; color: {pri_dark};
      box-shadow: 0 14px 30px rgba(10, 20, 40, 0.24); width: 816px;
    }}
    .s3-mini-pack {{ height: 108px; width: auto; max-width: 150px; object-fit: contain; flex-shrink: 0; filter: drop-shadow(0 6px 12px rgba(10,20,40,0.26)); }}

    .s4-prod-stage {{ position: absolute; left: 80px; top: 470px; width: 780px; height: 520px; display: flex; align-items: center; justify-content: center; z-index: 11; pointer-events: none; }}
    .s4-halo {{ position: absolute; width: 490px; height: 490px; border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.95) 0%, {pri_soft} 46%, rgba(255,255,255,0) 74%); }}
    .s4-real-pack {{ position: relative; z-index: 3; max-height: 490px; max-width: 680px; object-fit: contain; filter: drop-shadow(0 22px 34px rgba(10,20,45,0.38)); }}
    .s4-title-box {{ position: absolute; left: 58px; top: 342px; width: 820px; text-align: center; z-index: 12; }}
    .s4-kicker {{ display: inline-block; background: {pri}; color: #fff; padding: 7px 22px; border-radius: 99px; font-size: 24px; font-weight: 800; border: 2.5px solid #fff; }}
    .s4-hero {{ font-family: "FrauncesVN", serif; font-size: 76px; color: {pri}; paint-order: stroke fill; -webkit-text-stroke: 14px #fff; line-height: 1.05; margin-top: 6px; filter: drop-shadow(0 8px 18px rgba(0,0,0,0.28)); }}

    .end-card-panel {{
      position: absolute; left: 444px; top: 825px; width: 436px; border-radius: 28px;
      background: rgba(255, 255, 255, 0.96); border: 3.5px solid {pri};
      box-shadow: 0 18px 40px rgba(10, 20, 40, 0.30); padding: 15px 18px 14px 18px; text-align: center; z-index: 12;
    }}
    .end-packshot {{ display: block; margin: 6px auto 0 auto; max-width: 245px; max-height: 230px; object-fit: contain; filter: drop-shadow(0 12px 20px rgba(10,20,40,0.26)); }}
    .end-cta-box {{
      position: absolute; left: 56px; top: 1332px; width: 822px; background: {pri}; color: #ffffff;
      border: 4px solid #FFFFFF; border-radius: 999px; padding: 18px 22px; text-align: center;
      font-size: 27px; font-weight: 800; text-transform: uppercase; box-shadow: 0 16px 36px rgba(10,20,40,0.38); z-index: 14;
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
      <div id="hk-k" class="hook-kicker-pill">{sl['hook_kicker']}</div>
      <div id="hk-1" class="hook-giant-line">{hk_l1}</div>
      <div id="hk-2" class="hook-giant-line">{hk_l2}</div>
    </div>

    <div id="st-sl1" class="clip slide-card" data-start="{round(s2_st + 0.16, 2)}" data-duration="{round(s2_dur - 0.32, 2)}" data-track-index="8" data-layout-ignore>
      <div id="sh-1" class="sheen-bar"></div>
      <div class="slide-card-header">{sl['slide1_hdr']}</div>
      <div id="sr1" class="slide-row"><span class="slide-badge-dot">1</span> {sl['slide1_rows'][0]}</div>
      <div id="sr2" class="slide-row"><span class="slide-badge-dot">2</span> {sl['slide1_rows'][1]}</div>
      <div id="sr3" class="slide-row"><span class="slide-badge-dot">3</span> {sl['slide1_rows'][2]}</div>
    </div>

    <div id="st-sl2" class="clip slide-pill-stack" style="top: 1095px;" data-start="{round(s3_st + 0.18, 2)}" data-duration="{round(s3_dur - 0.36, 2)}" data-track-index="8" data-layout-ignore>
      <div id="cp1" class="slide-pill" style="font-size: 31px; line-height: 1.28; padding: 16px 26px;"><img class="s3-mini-pack" src="assets/images/{sl['cutout']}" alt="" /><span>{sl['slide2_pill']}</span></div>
    </div>

    <div id="st-s4t" class="clip s4-title-box" data-start="{round(s4_st + 0.12, 2)}" data-duration="{round(s4_dur - 0.24, 2)}" data-track-index="8" data-layout-ignore>
      <div class="s4-kicker">{sl['pack_kicker']}</div>
      <div class="s4-hero">{sl['pack_hero']}</div>
    </div>
    <div id="st-s4p" class="clip s4-prod-stage" data-start="{round(s4_st + 0.08, 2)}" data-duration="{round(s4_dur - 0.20, 2)}" data-track-index="9" data-layout-ignore>
      <div class="s4-halo"></div>
      <img id="s4-pack-img" class="s4-real-pack" src="assets/images/{sl['cutout']}" alt="" />
    </div>
    <div id="st-s4l" class="clip slide-pill-stack" style="top: 1012px;" data-start="{round(s4_st + 0.30, 2)}" data-duration="{round(s4_dur - 0.44, 2)}" data-track-index="10" data-layout-ignore>
      <div id="bp1" class="slide-pill"><span class="slide-badge-dot">✓</span> {sl['slide3_pills'][0]}</div>
      <div id="bp2" class="slide-pill"><span class="slide-badge-dot">✓</span> {sl['slide3_pills'][1]}</div>
      <div id="bp3" class="slide-pill"><span class="slide-badge-dot">✓</span> {sl['slide3_pills'][2]}</div>
    </div>

    <div id="st-end" class="clip end-card-panel" data-start="{round(s5_st + 0.12, 2)}" data-duration="{round(s5_dur - 0.12, 2)}" data-track-index="8" data-layout-ignore>
      <div style="font-size:16px;font-weight:800;color:{pri};letter-spacing:0.04em;">{sl['end_cat']}</div>
      <div style="font-family:'FrauncesVN',Georgia,serif;font-size:44px;font-weight:900;color:{pri};line-height:1.06;margin-top:4px;">{sl['end_name']}</div>
      <div style="font-family:'DancingVN',cursive;font-size:36px;font-weight:700;color:#0082C8;line-height:1.06;">Hằng Thu Pharma</div>
      <div style="font-size:15px;font-weight:800;color:{pri_dark};margin-top:4px;">{sl['end_sub']}</div>
      <img class="end-packshot" src="assets/images/{sl['cutout']}" alt="" />
    </div>
    <div id="st-cta" class="clip end-cta-box" data-start="{round(s5_st + 0.26, 2)}" data-duration="{round(s5_dur - 0.26, 2)}" data-track-index="9" data-layout-ignore>{sl['cta_txt']}</div>
    <div id="st-leg" class="clip legal-note" data-start="{round(s5_st + 0.34, 2)}" data-duration="{round(s5_dur - 0.34, 2)}" data-track-index="10" data-layout-ignore>{sl['legal_txt']}</div>
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
      .to("#st-s4t, #st-s4p, #st-s4l", {{ opacity: 0, filter: "blur(10px)", duration: 0.20 }}, {round(s4_st + s4_dur - 0.32, 2)})

      .fromTo("#st-end", {{ opacity: 0, x: 45, scale: 0.92, filter: "blur(12px)" }}, {{ opacity: 1, x: 0, scale: 1, filter: "blur(0px)", duration: 0.30, ease: "back.out(1.3)" }}, {round(s5_st + 0.14, 2)})
      .fromTo("#st-cta", {{ opacity: 0, y: 22, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.28, ease: "back.out(1.4)" }}, {round(s5_st + 0.28, 2)})
      .fromTo("#st-leg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.24 }}, {round(s5_st + 0.36, 2)});

    window.__timelines["main-stage"] = tl;
  </script>
</template>"""
    (comp_dir / "main-stage.html").write_text(stage_html, encoding="utf-8")

    caps = []
    for seg_id, line_a, line_b in sl["caps"]:
        s = segs[seg_id]
        st0 = s["start_s"]
        d_each = round((s["duration_s"] + 0.08) / 2.0, 3)
        caps.append((f"cap-{seg_id}-0", round(st0, 2), round(st0 + d_each - 0.02, 2), line_a))
        caps.append((f"cap-{seg_id}-1", round(st0 + d_each, 2), round(st0 + 2 * d_each - 0.02, 2), line_b))

    divs, js_g = [], []
    for ci_c, (cid, st, en, inner) in enumerate(caps):
        dur = round(max(0.4, en - st), 3)
        trk = (ci_c % 4) + 1
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
      font-family: "BeVietnamVN", sans-serif; font-weight: 800; font-size: 38px; line-height: 1.24; color: {pri_dark};
    }}
    .cap-kw {{ color: {pri}; font-family: "PlayfairVNItalic", Georgia, serif; font-style: italic; font-weight: 700; font-size: 42px; }}
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
    for vi, s in enumerate(segs_list):
        trk = 4 if (vi % 2 == 0) else 5
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

    sfx_tags = [f'      <audio id="sfx-cut-{fi}" class="clip" src="assets/audio/sfx_whoosh_soft.mp3" data-start="{max(0.0, round(ct - 0.08, 2))}" data-duration="0.48" data-track-index="8" data-volume="0.19" data-fade-out="0.12"></audio>' for fi, ct in enumerate(flash_times)]

    idx_html = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
    <title>{sl['final_mp4']}</title>
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

    out_mp4 = pdir / "08_Render_Master_V4" / sl["final_mp4"]
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["npx.cmd", "hyperframes", "render", "--output", str(out_mp4), "--quality", "delivery"], cwd=str(hf_dir), check=True)

    for base_dir in (K6_DAY25_DIR, CLOUD_DAY25_VID, LOCAL_DAY25_DIR):
        try:
            if Path(base_dir.anchor).exists():
                base_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(out_mp4, base_dir / sl["final_mp4"])
                print(f"[DAY25 V4 USP OVERWRITTEN IN K6] {base_dir / sl['final_mp4']}", flush=True)
        except Exception as e:
            print(f"[WARN COPY] {base_dir}: {e}")
    return out_mp4, segs_list, total_dur


def export_direct_jobs_json():
    hang_rtfn_p = V4_COUPLE_ROOT / "00_Clean_Sources" / "chihang_rtfn_5632.jpg"
    scenes = []
    for sl in SLOTS_261125:
        idx = sl["idx"]
        vkey = sl["vkey"]
        code = sl["code"]
        vdir = BATCH_ROOT / vkey / "07_HyperFrames_Project" / "assets" / "videos"
        vdir.mkdir(parents=True, exist_ok=True)
        vo_m = json.loads((BATCH_ROOT / vkey / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))
        segs = vo_m["segments"]

        if idx == 4:
            continue
        if idx == 9:
            sid = "d25_v09_u05"
            scenes.append({
                "scene_id": sid,
                "refs": [str(hang_rtfn_p)],
                "image_prompt": f"[D25 V09_U05] {STYLE_LOCK}{CHIHANG_LOCK}{sl['outfit']}Vertical 9:16 sunlit Nha Trang ocean-view balcony SOLO End-Card portrait: position CEO Nguyen Thi Hang standing gracefully on the LEFT HALF (X=8%..50%) smiling warmly with open turquoise bay on the right.",
                "motion_prompt": "Poised sunlit Nha Trang ocean-view balcony Solo End-Card push-in: CEO Nguyen Thi Hang stands gracefully on the left half smiling warmly." + ZERO_LIP,
                "shot_dur": float(segs[4]["shot_duration_s"]),
                "ref_png": str(USP_REFS_DIR / f"{sid}.png"),
                "ref_jpg": str(USP_REFS_DIR / f"{sid}.jpg"),
                "raw_mp4": str(BATCH_ROOT / vkey / "03_Flow_Raw" / f"{code}_U05_raw.mp4"),
                "dst_mp4": str(vdir / f"{code}_U05.mp4"),
            })
            continue

        b_combo = build_single_combo_board(hang_rtfn_p, PROD_DIR / sl["cutout"], USP_BOARDS_DIR / f"combo_{vkey}.jpg")
        s2_img, s2_mot, s4_img, s4_mot = SKU_3D_USP_PROMPTS[idx]
        outfit = sl["outfit"]

        five_defs = [
            (1, f"d25_{code.lower()}_u01", [str(hang_rtfn_p)],
             f"[D25 {code}_U01] {STYLE_LOCK}{CHIHANG_LOCK}{outfit}Vertical 9:16 medium front-facing shot {sl['scene_post']}. Frame CEO Nguyen Thi Hang's head cleanly around Y=26%..44% keeping 100% her exact full round-oval face, full soft cheeks, and gentle empathetic expression.",
             f"Smooth sunlit cinematic slow dolly-in {sl['scene_post']}; CEO Nguyen Thi Hang looks warmly at the camera with gentle natural poise." + ZERO_LIP),
            (2, f"d25_{code.lower()}_u02", [], f"[D25 {code}_U02] {STYLE_LOCK}{s2_img}", s2_mot),
            (3, f"d25_{code.lower()}_u03", [str(b_combo)],
             f"[D25 {code}_U03] {STYLE_LOCK}{CHIHANG_LOCK}{outfit}Vertical 9:16 medium front-facing commercial shot {sl['scene_vid']}: CEO Nguyen Thi Hang (LEFT half of reference — keep 100% her exact full round-oval face and radiant smile) proudly holds the product package (RIGHT half of reference) at chest height.",
             f"Warm uplifting dolly-in {sl['scene_vid']}; CEO Nguyen Thi Hang smiles radiantly while holding the product package steadily." + ZERO_LIP),
            (4, f"d25_{code.lower()}_u04", [], f"[D25 {code}_U04] {STYLE_LOCK}{s4_img}", s4_mot),
            (5, f"d25_{code.lower()}_u05", [str(hang_rtfn_p)],
             f"[D25 {code}_U05] {STYLE_LOCK}{CHIHANG_LOCK}{outfit}Vertical 9:16 sunlit Nha Trang ocean-view terrace SOLO End-Card portrait: position CEO Nguyen Thi Hang standing gracefully on the LEFT HALF (X=8%..50%) keeping 100% her exact full round-oval face and warm smile, leaving open turquoise ocean & palm bokeh on the right.",
             "Poised sunlit Nha Trang ocean-terrace Solo End-Card slow push-in: CEO Nguyen Thi Hang stands gracefully on the left half beaming warmly." + ZERO_LIP),
        ]

        for s_num, sid, r_files, iprompt, mprompt in five_defs:
            scenes.append({
                "scene_id": sid,
                "refs": r_files,
                "image_prompt": iprompt,
                "motion_prompt": mprompt,
                "shot_dur": float(segs[s_num - 1]["shot_duration_s"]),
                "ref_png": str(USP_REFS_DIR / f"{sid}.png"),
                "ref_jpg": str(USP_REFS_DIR / f"{sid}.jpg"),
                "raw_mp4": str(BATCH_ROOT / vkey / "03_Flow_Raw" / f"{code}_U0{s_num}_raw.mp4"),
                "dst_mp4": str(vdir / f"{code}_U0{s_num}.mp4"),
            })

    out_p = BATCH_ROOT / "day25_v4_usp_jobs.json"
    out_p.write_text(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[EXPORTED {len(scenes)} DIRECT AI USP SCENE JOBS] -> {out_p}", flush=True)


def copy_v04_v09_from_v4_couple():
    for sl in SLOTS_261125:
        idx, vkey, code = sl["idx"], sl["vkey"], sl["code"]
        vdir = BATCH_ROOT / vkey / "07_HyperFrames_Project" / "assets" / "videos"
        vo_m = json.loads((BATCH_ROOT / vkey / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))
        segs = vo_m["segments"]
        if idx == 4:
            src_v4 = V4_COUPLE_ROOT / "c02_dieu_kinh_ht" / "07_HyperFrames_Project" / "assets" / "videos"
            for sc, dc, sdur in [("DK4_C01", f"{code}_U01", segs[0]["shot_duration_s"]), ("DK4_C03", f"{code}_U02", segs[1]["shot_duration_s"]),
                                 ("DK4_C04", f"{code}_U03", segs[2]["shot_duration_s"]), ("DK4_C05", f"{code}_U04", segs[3]["shot_duration_s"]),
                                 ("DK4_C07", f"{code}_U05", segs[4]["shot_duration_s"])]:
                transcode_cfr24_nvenc(src_v4 / f"{sc}.mp4", vdir / f"{dc}.mp4", float(sdur))
        elif idx == 9:
            src_v4 = V4_COUPLE_ROOT / "c01_ngoc_long_hoan" / "07_HyperFrames_Project" / "assets" / "videos"
            for sc, dc, sdur in [("NLH4_C01", f"{code}_U01", segs[0]["shot_duration_s"]), ("NLH4_C03", f"{code}_U02", segs[1]["shot_duration_s"]),
                                 ("NLH4_C05", f"{code}_U03", segs[2]["shot_duration_s"]), ("NLH4_C04", f"{code}_U04", segs[3]["shot_duration_s"])]:
                transcode_cfr24_nvenc(src_v4 / f"{sc}.mp4", vdir / f"{dc}.mp4", float(sdur))


def main():
    if "--prep" in sys.argv:
        export_direct_jobs_json()
        return

    copy_v04_v09_from_v4_couple()
    aco_list, tvc_list = list_fresh_bgms()

    qa_tiles = []
    for sl in SLOTS_261125:
        mp4_p, segs_list, tdur = render_v4_pro_slot(sl, aco_list, tvc_list)
        for si, s in enumerate(segs_list, start=1):
            ts = min(tdur - 0.5, float(s["shot_start_s"]) + float(s["shot_duration_s"]) * 0.5)
            fp = mp4_p.parent / f"qa5_{si}.jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", str(mp4_p), "-frames:v", "1", "-q:v", "2", str(fp)], check=True)
            im = Image.open(fp).convert("RGB")
            d = ImageDraw.Draw(im)
            d.line([(0, 248), (1080, 248)], fill=(255, 60, 60), width=4)
            d.line([(0, 1548), (1080, 1548)], fill=(255, 60, 60), width=4)
            d.rectangle([(886, 860), (1080, 1548)], outline=(255, 60, 60), width=4)
            qa_tiles.append((f"{sl['code']}_U0{si} {ts:.1f}s", im))

    tw, th_c = 210, 375
    sh = Image.new("RGB", (tw * 10, th_c * 5), (14, 20, 32))
    sd = ImageDraw.Draw(sh)
    for i, (lbl, im) in enumerate(qa_tiles):
        r, c = divmod(i, 10)
        sh.paste(im.resize((tw - 6, th_c - 22), Image.Resampling.LANCZOS), (c * tw + 3, r * th_c + 19))
        sd.text((c * tw + 5, r * th_c + 2), lbl, fill=(190, 235, 255))
    qa_out = BATCH_ROOT / "day25_v4_10_usp_videos_50shots_qa.jpg"
    sh.save(qa_out, quality=92)
    shutil.copy2(qa_out, ARTIFACT_DIR / "htpm_261125_10_videos_v4_usp_qa.jpg")
    print("=== ALL 10 DAY-25 V4 AI USP VIDEOS 100% OVERWRITTEN IN K6 ===", flush=True)


if __name__ == "__main__":
    main()
