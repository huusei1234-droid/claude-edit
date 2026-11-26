# -*- coding: utf-8 -*-
"""
Ngày 03 (26/11/2026) — Sinh trọn bộ Tài nguyên Hình ảnh & Video Sinh hoạt Đời thường Khớp Kịch bản
(BỎ 100% bối cảnh Nha Trang! 0% truyền thông Bojomi trẻ em!):
- 4 Ảnh Chân dung 1:1 Bài Thiết Kế (ChatGPT HTPM song song 3 luồng, khóa 100% mặt AV_MODEL_MASTER_SHEET.jpg)
- 4 Ảnh Diện mạo 9:16 Video Anchor (ChatGPT HTPM song song 3 luồng, 4 bộ trang phục + tóc + phụ kiện hoàn toàn khác nhau)
- 28 Clip Hoạt động Sinh hoạt Đời thường 9:16 (7 cảnh/video × 4 video = 28 clip riêng biệt trên Google Flow `capcut274`,
  chế độ Thành phần / Ingredients, tối đa 1 hộp thật IS-Net ở cảnh s05, xuất bảng QC trực quan 28 clip thô!).
"""
import base64, json, os, re, shutil, subprocess, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
import ai_ref_video as arv

# Ưu tiên số 1 Google Flow (`capcut274`) cho Video, bỏ qua gemini.google.com bị chặn sorry page
arv.VIDEO_FALLBACK_CHAIN = [
    ("Google-Flow", "flow::flow-omni-1.2-flash"),
    ("Muse", "muse::muse-video"),
]

WORK = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_03_2611")
POST_PORTRAITS_DIR = WORK / "01_ChatGPT_Post_Portraits"
LOOKS_DIR = WORK / "04_Video_Looks_9x16"
CLIPS_DIR = WORK / "05_Flow_Raw_Clips"
for d in (POST_PORTRAITS_DIR, LOOKS_DIR, CLIPS_DIR):
    d.mkdir(parents=True, exist_ok=True)

MASTER_FACE = r"G:\My Drive\dự án ngoài\An Vượng\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\02. Ảnh Mẫu Nhân Vật Xuyên Suốt\AV_MODEL_MASTER_SHEET.jpg"
if not os.path.exists(MASTER_FACE):
    MASTER_FACE = r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\01_Mau_USP_Goc\AV_MODEL_MASTER_SHEET.jpg"

CUTOUT_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\07_An_Vuong_Pharma\02_San_Pham_Cutout_PNG")
BOX_PRO = str(CUTOUT_DIR / "av01_protein_a.png")
BOX_BOJ = str(CUTOUT_DIR / "av02_bojomi_b.png")
BOX_CUR = str(CUTOUT_DIR / "av04_curcumilk_b.png")
BOX_COL = str(CUTOUT_DIR / "av03_collamela_b.png")


def save_canvas_nodes_smart(node_id_to_dest: dict) -> dict:
    """
    Trích xuất trực tiếp nội dung ảnh/video từ Canvas node metadata (`data:` base64, URL nội bộ `:3100`/`:17371`,
    đường dẫn cục bộ, hoặc fallback qua `export:folder` nếu có) — hoạt động 100% kể cả khi Canvas trống!
    """
    r, nodes = arv.get_canvas_state()
    saved = {}
    missing = {}

    for nid, dest in node_id_to_dest.items():
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
        n = nodes.get(nid)
        if not n:
            missing[nid] = dest
            continue
        meta = n.get("metadata") or {}
        src = meta.get("content") or meta.get("videoUrl") or meta.get("url") or meta.get("src") or ""
        ok = False
        if isinstance(src, str) and src.startswith("data:"):
            m = re.match(r"^data:[^;]+;base64,(.+)$", src, flags=re.S)
            if m:
                raw = base64.b64decode(m.group(1))
                with open(dest, "wb") as f:
                    f.write(raw)
                ok = os.path.getsize(dest) > 2048
        elif isinstance(src, str) and (src.startswith("http://") or src.startswith("https://")):
            req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            ok = os.path.getsize(dest) > 2048
        elif isinstance(src, str) and src.startswith("/"):
            for base_u in ["http://127.0.0.1:3100", "http://127.0.0.1:17371"]:
                try:
                    with urllib.request.urlopen(base_u + src, timeout=30) as resp, open(dest, "wb") as f:
                        f.write(resp.read())
                    if os.path.getsize(dest) > 2048:
                        ok = True
                        break
                except Exception:
                    pass
        elif isinstance(src, str) and os.path.exists(src):
            shutil.copy2(src, dest)
            ok = os.path.getsize(dest) > 2048

        if ok:
            saved[nid] = dest
        else:
            print(f"[WARN] Direct extract could not resolve {nid} (src prefix={str(src)[:60]})", flush=True)
            missing[nid] = dest

    if missing:
        ex_nodes = [x for x in r.get("nodes", []) if x.get("type") == "export:folder"]
        if ex_nodes:
            saved.update(arv.export_canvas_nodes_to_files(missing))
    return saved


POST_FACE_LOCK = (
    "CRITICAL IDENTITY LOCK: Use the EXACT same 27-year-old Vietnamese woman's face, delicate oval jawline, "
    "bright dark almond eyes, natural brows, gentle nose, soft rose lips, fair luminous skin, and radiant warm smile "
    "from the reference image. "
    "COMPOSITION LOCK: Frame her neatly on the RIGHT 44% of the 1:1 square frame (three-quarter / waist-up shot), "
    "leaving the LEFT 56% open bright soft-focus indoor background for typography and product cutouts. "
    "NO beach, NO ocean, NO palm trees. Authentic everyday modern Vietnamese home or office interior. "
    "ZERO text, ZERO labels, ZERO brand logos, ZERO boxes in the photo. Canon R5 85mm f/2 editorial lifestyle photography."
)

POST_SPECS = [
    (
        "N03_POST1_AVP_KITCHEN.png",
        "N03_P1_AVP",
        POST_FACE_LOCK + " SETTING: Bright sunlit cozy modern Vietnamese family kitchen & breakfast island in early morning light with warm oak cabinets and a small plate of sliced banana in soft bokeh. "
        "OUTFIT 1: Crisp off-white fine-knit polo shirt with navy collar trim, neat high ponytail, tiny silver stud earrings, slim silver wristwatch. "
        "POSE: Holding a clean transparent glass of creamy light-beige plant protein smoothie with an energized happy morning smile before going to work."
    ),
    (
        "N03_POST2_BOJOMI_OFFICE.png",
        "N03_P2_BOJ",
        POST_FACE_LOCK + " SETTING: Bright modern corporate office workspace with clean wooden desk, sleek closed laptop, indoor green plant, and soft daylight windows in bokeh. "
        "OUTFIT 2: Elegant ivory silk blouse with a neat soft bow at the neck paired with a tailored beige high-waisted pencil skirt, polished high bun hairstyle, small gold hoop earrings. "
        "POSE: Holding a clear glass mug of warm creamy vanilla cereal milk with a poised confident professional smile."
    ),
    (
        "N03_POST3_CURCU_HOME.png",
        "N03_P3_CUR",
        POST_FACE_LOCK + " SETTING: Warm cozy sunlit wooden living room & tea corner at 3 PM golden afternoon indoor light, soft linen curtains and bookshelf in bokeh. "
        "OUTFIT 3: Effortless ivory-white linen dress with a soft butter-yellow lightweight knit cardigan draped comfortably over her shoulders, natural loose dark-brown hair with soft bangs, delicate gold hoops. "
        "POSE: Holding a clean cream ceramic mug of warm golden vanilla-coconut turmeric milk with a serene cozy smile."
    ),
    (
        "N03_POST4_COL_VANITY.png",
        "N03_P4_COL",
        POST_FACE_LOCK + " SETTING: Cozy warm-lit modern bedroom & neat skincare vanity table in the evening with warm bedside lamp bokeh and soft cream headboard. "
        "OUTFIT 4: Chic pastel sky-blue silk loungewear pajama shirt with crisp white piping, soft wavy dark-brown hair half-pinned with a pearl clip, tiny diamond stud earrings, dewy glowing skin. "
        "POSE: Holding a delicate crystal glass of chilled translucent rosy-peach collagen drink with a radiant relaxed evening smile."
    ),
]

LOOK_LOCK = (
    "CRITICAL IDENTITY LOCK: Exact same 27-year-old Vietnamese woman's face, oval jawline, bright dark almond eyes, "
    "soft rose lips, fair luminous skin, and warm radiant smile from the reference image. "
    "Vertical 9:16 editorial commercial portrait, centered medium-full framing, authentic everyday modern Vietnamese indoor lifestyle setting (NO beach, NO ocean, NO palm trees). "
    "ZERO text, ZERO words, ZERO product boxes, ZERO logos, ZERO watermarks. Photorealistic 85mm commercial photography."
)

LOOK_SPECS = [
    (
        "N03_LOOK1_AVP_MORNING_9x16.png", "n03_lk1_avp",
        LOOK_LOCK + " OUTFIT 1: Crisp off-white fine-knit polo shirt with navy collar trim tucked into tailored light-beige trousers, neat high ponytail, silver stud earrings, slim silver wristwatch. "
        "SETTING: Sunlit warm modern Vietnamese apartment kitchen and wooden breakfast counter in early morning."
    ),
    (
        "N03_LOOK2_BOJOMI_OFFICE_9x16.png", "n03_lk2_boj",
        LOOK_LOCK + " OUTFIT 2: Elegant ivory silk bow-neck office blouse tucked into a tailored beige midi pencil skirt, neat high bun hairstyle, small gold hoop earrings, classic leather-strap watch. "
        "SETTING: Bright sunlit modern office workspace with wooden desk, sleek laptop, and indoor greenery."
    ),
    (
        "N03_LOOK3_CURCU_AFTERNOON_9x16.png", "n03_lk3_cur",
        LOOK_LOCK + " OUTFIT 3: Relaxed ivory-white linen midi dress layered with a soft butter-yellow lightweight knit cardigan, natural loose dark-brown hair with soft bangs, thin gold hoop earrings. "
        "SETTING: Cozy warm sunlit home living room & wooden tea table at 3 PM afternoon."
    ),
    (
        "N03_LOOK4_COL_EVENING_9x16.png", "n03_lk4_col",
        LOOK_LOCK + " OUTFIT 4: Chic pastel sky-blue silk pajama shirt with white piping and matching trousers, soft wavy hair half-up with a pearl clip, tiny crystal stud earrings, luminous dewy skin. "
        "SETTING: Warm cozy modern bedroom & softly lit evening vanity mirror."
    ),
]

NO_TALK = (
    "ZERO lip movement, ZERO talking, closed or gently smiling lips, natural real-time everyday human movement, "
    "smooth 24fps camera motion, NO beach, NO sea, ZERO text overlays, ZERO distorted hands."
)


def get_flow_specs(lk_nodes: dict, box_nodes: dict):
    """
    28 clip hoạt động sinh hoạt đời thường riêng biệt (7 clip/video × 4 video = 28 clip, seconds=4),
    mỗi clip mô tả đúng 1 hoạt động thực tế bám sát câu kịch bản!
    """
    return [
        # === VIDEO 1: AV PROTEIN (7 cảnh sinh hoạt buổi sáng bận rộn trước giờ đi làm) ===
        {
            "file": "v1_s01.mp4", "out_title": "n03_v1_s01", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 everyday morning lifestyle shot of the Vietnamese woman in off-white navy-trim knit polo opening sheer white apartment curtains to let warm morning sunlight into her tidy living room, glancing at her wristwatch getting ready for work. {NO_TALK}",
        },
        {
            "file": "v1_s02.mp4", "out_title": "n03_v1_s02", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 relatable everyday morning shot of the same woman in off-white knit polo sitting briefly at a home wooden dining table looking at a plate of dry toast bread, gently shaking her head with a wry relatable expression as she has no appetite for dry food in a busy morning. {NO_TALK}",
        },
        {
            "file": "v1_s03.mp4", "out_title": "n03_v1_s03", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 brisk kitchen activity shot of the same woman in off-white knit polo stepping up to her sunlit modern home kitchen island, placing a clean transparent glass cup beside fresh sliced banana on a wooden board with a bright smile. {NO_TALK}",
        },
        {
            "file": "v1_s04.mp4", "out_title": "n03_v1_s04", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"Close-medium 9:16 tactile kitchen shot of the same woman in off-white knit polo pouring cool clear water from a glass pitcher into fine plant protein powder in a clear glass and stirring briskly with a spoon until smooth creamy light-beige. {NO_TALK}",
        },
        {
            "file": "v1_s05.mp4", "out_title": "n03_v1_s05", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk1_avp"], "extra_ref_node_ids": [box_nodes["pro"]],
            "motion_prompt": f"Clean 9:16 commercial lifestyle shot in a warm sunlit Vietnamese home kitchen: the same woman in off-white knit polo holds the EXACT green-and-cream AV PROTEIN box from the second reference image clearly toward camera next to her glass of creamy beige shake on the counter, exact box design preserved. {NO_TALK}",
        },
        {
            "file": "v1_s06.mp4", "out_title": "n03_v1_s06", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 natural morning routine shot of the same woman in off-white knit polo standing by her home breakfast counter taking a smooth refreshing sip of the creamy beige plant protein drink, resting a relaxed hand lightly on her comfortable stomach with a happy smile. {NO_TALK}",
        },
        {
            "file": "v1_s07.mp4", "out_title": "n03_v1_s07", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk1_avp"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 energetic everyday activity shot of the same woman in off-white knit polo and beige trousers slinging a neat leather work tote over her shoulder, picking up her planner, and walking briskly toward the sunlit apartment doorway with vibrant morning energy. {NO_TALK}",
        },

        # === VIDEO 2: BOJOMI (7 cảnh sinh hoạt dân văn phòng & người lớn — 0% trẻ em!) ===
        {
            "file": "v2_s01.mp4", "out_title": "n03_v2_s01", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 relatable office lifestyle shot of the Vietnamese woman in ivory silk bow blouse sitting at a modern office desk typing on a laptop, pausing to gently roll her shoulders and stretch her neck after hours of indoor desk work. {NO_TALK}",
        },
        {
            "file": "v2_s02.mp4", "out_title": "n03_v2_s02", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 everyday office activity shot of the same woman in ivory silk bow blouse and beige pencil skirt standing up beside a bright office window with city buildings softly blurred outside, stretching her arms and wrists gracefully. {NO_TALK}",
        },
        {
            "file": "v2_s03.mp4", "out_title": "n03_v2_s03", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk2_boj"], "extra_ref_node_ids": [box_nodes["boj"]],
            "motion_prompt": f"Clean 9:16 commercial office shot: the same woman in ivory silk bow blouse at her tidy wooden office desk holding the EXACT white-and-emerald BOJOMI box from the second reference image clearly visible while glancing thoughtfully at its nutrition panel with an approving nod, exact packaging preserved. {NO_TALK}",
        },
        {
            "file": "v2_s04.mp4", "out_title": "n03_v2_s04", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"Close-medium 9:16 office pantry activity shot of the same woman in ivory silk bow blouse pouring warm 60-degree water from a minimalist matte thermal flask into a clear glass mug of fine cereal powder, delicate warm steam rising softly. {NO_TALK}",
        },
        {
            "file": "v2_s05.mp4", "out_title": "n03_v2_s05", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 tactile close-medium shot of the same woman in ivory silk blouse stirring the warm creamy vanilla cereal milk in a clear glass mug with a silver spoon on her office desk until silky smooth with zero clumps. {NO_TALK}",
        },
        {
            "file": "v2_s06.mp4", "out_title": "n03_v2_s06", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 pleasant office break shot of the same woman in ivory silk bow blouse sitting at her bright desk taking a warm comforting sip of creamy vanilla cereal drink beside her laptop, smiling with relaxed satisfaction. {NO_TALK}",
        },
        {
            "file": "v2_s07.mp4", "out_title": "n03_v2_s07", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk2_boj"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 warm adult family lifestyle shot of the same woman in ivory silk blouse walking gracefully across a sunlit modern office hallway carrying a neat notebook with poised agile posture and confident smile. {NO_TALK}",
        },

        # === VIDEO 3: CURCUMILK PHYTO (7 cảnh sinh hoạt chiều bận rộn & chăm sóc gia đình) ===
        {
            "file": "v3_s01.mp4", "out_title": "n03_v3_s01", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk3_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 relatable afternoon lifestyle shot of the Vietnamese woman in ivory linen dress and butter-yellow cardigan working on documents at a home wooden table at 3 PM, pausing to place a gentle hand on her midsection feeling afternoon hunger after a late lunch. {NO_TALK}",
        },
        {
            "file": "v3_s02.mp4", "out_title": "n03_v3_s02", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk3_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 warm indoor activity shot of the same woman in ivory linen dress and butter-yellow cardigan closing her laptop on the living room table and walking into her cozy warm-lit home kitchen for an afternoon break. {NO_TALK}",
        },
        {
            "file": "v3_s03.mp4", "out_title": "n03_v3_s03", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk3_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 cozy home kitchen shot of the same woman in butter-yellow cardigan taking a clean cream ceramic mug from a wooden shelf and placing it on a tidy warm countertop bathed in afternoon sunlight. {NO_TALK}",
        },
        {
            "file": "v3_s04.mp4", "out_title": "n03_v3_s04", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk3_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"Close-medium 9:16 tactile shot of the same woman in butter-yellow cardigan pouring warm 45-degree water into the ceramic mug and stirring a smooth silky golden-yellow vanilla coconut turmeric milk swirl with gentle warm steam. {NO_TALK}",
        },
        {
            "file": "v3_s05.mp4", "out_title": "n03_v3_s05", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk3_cur"], "extra_ref_node_ids": [box_nodes["cur"]],
            "motion_prompt": f"Warm 9:16 commercial home shot: the same woman in ivory linen dress and butter-yellow cardigan at her cozy wooden tea table holding the EXACT cream-and-gold CURCUMILK PHYTO box from the second reference image clearly toward camera beside her warm golden ceramic mug, exact box label preserved. {NO_TALK}",
        },
        {
            "file": "v3_s06.mp4", "out_title": "n03_v3_s06", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk3_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 sensory lifestyle shot of the same woman in butter-yellow cardigan holding the warm ceramic mug with both hands, inhaling the pleasant sweet coconut-vanilla aroma with eyes briefly crinkling in delight and taking a soothing sip. {NO_TALK}",
        },
        {
            "file": "v3_s07.mp4", "out_title": "n03_v3_s07", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk3_cur"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 cozy everyday afternoon shot of the same woman in ivory linen dress and butter-yellow cardigan sitting comfortably in a plush living room armchair turning pages of a book beside her warm mug of golden milk in soft amber indoor light. {NO_TALK}",
        },

        # === VIDEO 4: COLLAMELA (7 cảnh sinh hoạt tối chăm da nhanh 10s đón Tết) ===
        {
            "file": "v4_s01.mp4", "out_title": "n03_v4_s01", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk4_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 evening skincare routine shot of the Vietnamese woman in pastel sky-blue silk pajamas sitting at a warm-lit bedroom vanity mirror after washing her face, gently patting both cheeks to check her hydrated skin. {NO_TALK}",
        },
        {
            "file": "v4_s02.mp4", "out_title": "n03_v4_col2", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk4_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 tidy bedroom activity shot of the same woman in pastel sky-blue silk pajamas organizing her neat wooden vanity tray with skincare bottles under warm cozy lamp light, smiling gently. {NO_TALK}",
        },
        {
            "file": "v4_s03.mp4", "out_title": "n03_v4_s03", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk4_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"Close-medium 9:16 evening routine shot of the same woman in pastel sky-blue silk pajamas pouring 100ml of cool clear water from a sleek glass carafe into a small crystal glass on her warm bedroom side table. {NO_TALK}",
        },
        {
            "file": "v4_s04.mp4", "out_title": "n03_v4_s04", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk4_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 tactile beauty lifestyle shot of the same woman in pastel sky-blue silk pajamas stirring a small crystal glass of translucent rosy-peach collagen drink with a delicate glass stirrer until crystal clear and sparkling. {NO_TALK}",
        },
        {
            "file": "v4_s05.mp4", "out_title": "n03_v4_s05", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk4_col"], "extra_ref_node_ids": [box_nodes["col"]],
            "motion_prompt": f"Cozy 9:16 evening beauty hero shot: the same woman in pastel sky-blue silk pajamas at her warm-lit bedroom vanity holding the EXACT white-and-emerald COLLAMELA box from the second reference image clearly toward camera beside her small glass of rosy-peach drink, exact packaging preserved. {NO_TALK}",
        },
        {
            "file": "v4_s06.mp4", "out_title": "n03_v4_s06", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk4_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 evening beauty shot of the same woman in pastel sky-blue silk pajamas taking a refreshing sip from the small glass of rosy-peach drink, smiling brightly at the sweet pleasant peach taste. {NO_TALK}",
        },
        {
            "file": "v4_s07.mp4", "out_title": "n03_v4_s07", "seconds": 4,
            "ref_img_node_id": lk_nodes["n03_lk4_col"], "extra_ref_node_ids": None,
            "motion_prompt": f"9:16 everyday evening habit shot of the same woman in pastel sky-blue silk pajamas neatly slipping a small cosmetic pouch into her handbag for tomorrow's workday and smiling warmly in her cozy lamp-lit bedroom. {NO_TALK}",
        },
    ]


def build_raw_qc_sheet():
    clips = sorted(CLIPS_DIR.glob("v*_s0*.mp4"))
    if not clips:
        return
    cols, rows = 7, 4
    tw, th = 216, 384
    sheet = Image.new("RGB", (cols * (tw + 12) + 12, rows * (th + 30) + 12), (14, 18, 24))
    draw = ImageDraw.Draw(sheet)
    tmp = WORK / "_tmp_raw_qc.png"
    for idx, cp in enumerate(clips[:28]):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.6", "-i", str(cp), "-frames:v", "1", str(tmp)], check=True)
        im = Image.open(tmp).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x = (idx % cols) * (tw + 12) + 12
        y = (idx // cols) * (th + 30) + 12
        sheet.paste(im, (x, y))
        draw.text((x + 4, y + th + 5), cp.name, fill=(255, 232, 120))
    tmp.unlink(missing_ok=True)
    out = WORK / "QA_N03_28_RawClips.jpg"
    sheet.save(out, quality=90)
    print(f"[RAW QC SHEET] {out}", flush=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    face_nid = arv.stage_local_ref_image_once(MASTER_FACE, ref_tag="av_face_n03")
    tmp_img_nodes = []

    # Step A: 4 Square 1:1 Post Portraits
    if mode in ("all", "posts", "images"):
        todo_posts = [(fn, tag, pr) for fn, tag, pr in POST_SPECS if not (POST_PORTRAITS_DIR / fn).exists()]
        if todo_posts:
            res = arv.generate_ref_images_parallel_batch(
                [{"prompt": pr, "ref_tag": tag, "ratio": "1:1", "reference_node_ids": [face_nid]} for fn, tag, pr in todo_posts],
                max_workers=3,
            )
            exp = {}
            for (fn, _, _), (_, nid, prov) in zip(todo_posts, res):
                tmp_img_nodes.append(nid)
                exp[nid] = str(POST_PORTRAITS_DIR / fn)
                print(f"[POST 1:1] {fn} via {prov}", flush=True)
            save_canvas_nodes_smart(exp)

    # Step B: 4 Vertical 9:16 Video Look Anchors
    if mode in ("all", "videos", "images"):
        todo_looks = [(fn, tag, pr) for fn, tag, pr in LOOK_SPECS if not (LOOKS_DIR / fn).exists()]
        if todo_looks:
            res = arv.generate_ref_images_parallel_batch(
                [{"prompt": pr, "ref_tag": tag, "ratio": "9:16", "reference_node_ids": [face_nid]} for fn, tag, pr in todo_looks],
                max_workers=3,
            )
            exp = {}
            for (fn, _, _), (_, nid, prov) in zip(todo_looks, res):
                tmp_img_nodes.append(nid)
                exp[nid] = str(LOOKS_DIR / fn)
                print(f"[LOOK 9:16] {fn} via {prov}", flush=True)
            save_canvas_nodes_smart(exp)

    if tmp_img_nodes:
        arv.cleanup_exported_canvas_nodes(tmp_img_nodes)

    if mode in ("posts", "images"):
        arv.cleanup_exported_canvas_nodes([face_nid])
        return

    # Step C: Stage 4 Look Anchors + 4 Real IS-Net Product Boxes & Generate 28 Fast Everyday Flow Clips!
    stage_nodes = [face_nid]
    lk_nodes = {}
    for fn, tag, _ in LOOK_SPECS:
        nid = arv.stage_local_ref_image_once(str(LOOKS_DIR / fn), ref_tag=tag)
        lk_nodes[tag] = nid
        stage_nodes.append(nid)

    box_nodes = {}
    for bk, bp in [("pro", BOX_PRO), ("boj", BOX_BOJ), ("cur", BOX_CUR), ("col", BOX_COL)]:
        nid = arv.stage_local_ref_image_once(bp, ref_tag=f"box_{bk}_n03")
        box_nodes[bk] = nid
        stage_nodes.append(nid)

    all_vspecs = get_flow_specs(lk_nodes, box_nodes)
    todo_vids = [sp for sp in all_vspecs if not (CLIPS_DIR / sp["file"]).exists() or (CLIPS_DIR / sp["file"]).stat().st_size < 80_000]
    print(f"[FLOW QUEUE] {len(todo_vids)}/{len(all_vspecs)} clips to generate...", flush=True)

    def _run_one(idx_sp):
        idx, sp = idx_sp
        if idx > 0:
            time.sleep((idx % 4) * 1.4)
        vnid, prov = arv.generate_video_with_ref(
            motion_prompt=sp["motion_prompt"],
            ref_img_node_id=sp["ref_img_node_id"],
            out_title=sp["out_title"],
            ratio="9:16",
            seconds=int(sp.get("seconds", 4)),
            video_mode="reference",
            extra_ref_node_ids=sp.get("extra_ref_node_ids"),
        )
        saved = save_canvas_nodes_smart({vnid: str(CLIPS_DIR / sp["file"])})
        if vnid in saved:
            arv.cleanup_exported_canvas_nodes([vnid])
            print(f"[SAVED CLIP] {sp['file']} via {prov}", flush=True)
        else:
            raise RuntimeError(f"Failed to save clip {sp['file']} (node={vnid})")
        return sp["file"]

    try:
        if todo_vids:
            with ThreadPoolExecutor(max_workers=4) as pool:
                futs = [pool.submit(_run_one, (i, sp)) for i, sp in enumerate(todo_vids)]
                for f in as_completed(futs):
                    f.result()
    finally:
        arv.cleanup_exported_canvas_nodes(stage_nodes)

    build_raw_qc_sheet()


if __name__ == "__main__":
    main()
