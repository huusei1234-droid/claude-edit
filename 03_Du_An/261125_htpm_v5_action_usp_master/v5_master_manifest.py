# -*- coding: utf-8 -*-
"""
V5 MASTER MANIFEST — HẰNG THU PHARMA (25/11/2026)
Giải quyết triệt để 100% góp ý của Người dùng:
1. KHÔNG ĐỂ 1 SOURCE KÉO DÀI: Mỗi video (~38s-43s) cắt nhanh 10 CẢNH ĐỘC LẬP (~3.5s - 4.2s/cảnh, nhịp sóng TVC sinh động).
2. MẪU HÀNH ĐỘNG ĐỜI THỰC ĐA DẠNG (0% đứng nhìn cười đơ):
   - Đi xe ô tô (ngồi ghế sau uống cà phê sáng, mở túi xách trên xe, bước xuống xe sedan, xem điện thoại trên xe...)
   - Dạo dưới đường phố (bước vội đi làm buổi sáng, dạo phố rợp cây xanh, đi bộ khu phố thương mại, che nắng gắt...)
   - Sinh hoạt trong nhà & Tương tác thật với sản phẩm (ngồi laptop ôm thượng vị, xoa bụng trên sofa, pha nước ấm mở lọ uống tại bếp, bỏ gói 5ml vào túi xách, mở rèm đón nắng, pha trà thảo mộc đặt lọ Ngọc Long Hoàn, soi gương bàn phấn, cất hộp sản phẩm vào tủ đầu giường, họp kiểm định sản phẩm...)
3. TUYỆT ĐỐI 0% CHỮ HAY SẢN PHẨM CHE MẶT (100% Face-Safe + 100% Safe Zone TikTok/Reels):
   - Cảnh có người: 0% bảng trắng to, 0% hộp sản phẩm bay che người; chỉ đặt thanh phụ đề/nhãn thấp ở Y=1130..1525px.
   - Bảng thông tin USP lớn & Hộp sản phẩm lớn chỉ đặt trên cảnh 3D CGI / Bục Studio Sản Phẩm / 3D Macro / Split End-Card.
4. 10 THIẾT KẾ MỚI HOÀN TOÀN (0 file .PSD, không liên quan video, MỖI THIẾT KẾ 1 KIỂU BỐ CỤC & CONCEPT RIÊNG BIỆT!).
"""
import json
from pathlib import Path
from PIL import Image

BATCH_ROOT = Path(r"d:\AI\full studio\output\htpm-ngay-261125")
V4_COUPLE_ROOT = Path(r"d:\AI\full studio\output\htpm-ai-usp-v4-261125")
BRAND_KIT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma")
PROD_DIR = BRAND_KIT / "products_cutout_png"

V5_DIR = BATCH_ROOT / "10_V5_Action_USP"
V5_BOARDS = V5_DIR / "00_Combo_Boards"
V5_IMG_DIR = V5_DIR / "01_Refs"
V5_RAW_VID = V5_DIR / "02_Flow_Raw"
V5_CFR_VID = V5_DIR / "03_Clips_CFR24"
V5_PODIUM_VID = V5_DIR / "04_Studio_Podium_Clips"
V5_POSTERS_DIR = BATCH_ROOT / "11_V5_10_Unique_Designs"

for _d in (V5_DIR, V5_BOARDS, V5_IMG_DIR, V5_RAW_VID, V5_CFR_VID, V5_PODIUM_VID, V5_POSTERS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

HANG_RTFN = V4_COUPLE_ROOT / "00_Clean_Sources" / "chihang_rtfn_5632.jpg"
HAI_RTFN = V4_COUPLE_ROOT / "00_Clean_Sources" / "anhhai_rtfn_5829.jpg"


def build_combo_board(face_p: Path, prod_p: Path, out_p: Path) -> str:
    if out_p.exists() and out_p.stat().st_size > 60_000:
        return str(out_p)
    im_f = Image.open(face_p).convert("RGB")
    # Center-crop portrait cleanly
    fw, fh = im_f.size
    im_f = im_f.resize((680, int(fh * 680 / fw)), Image.Resampling.LANCZOS)
    if im_f.height > 920:
        im_f = im_f.crop((0, 0, 680, 920))
    canvas = Image.new("RGBA", (1160, 920), (250, 251, 254, 255))
    canvas.paste(im_f.convert("RGBA"), (0, (920 - im_f.height) // 2))
    im_p = Image.open(prod_p).convert("RGBA")
    if im_p.getbbox():
        im_p = im_p.crop(im_p.getbbox())
    im_p.thumbnail((420, 820), Image.Resampling.LANCZOS)
    canvas.alpha_composite(im_p, (700 + (440 - im_p.width) // 2, (920 - im_p.height) // 2))
    canvas.convert("RGB").save(out_p, quality=94)
    return str(out_p)


def ensure_8sku_shelf_cutout() -> str:
    """Tạo kệ trưng bày 8 sản phẩm thật 100% Hằng Thu Pharma cho Thiết kế 10 & Video 10."""
    out_p = PROD_DIR / "SP_HTPM_FULL_8SKU_SHELF.png"
    if out_p.exists() and out_p.stat().st_size > 200_000:
        return str(out_p)
    canvas = Image.new("RGBA", (1800, 680), (0, 0, 0, 0))
    lineup = [
        ("SP_GEL_PHU_KHANG_CUTOUT.png", 310, 20, 320),
        ("SP_VIEN_DAT_HOP_XANH_CUTOUT.png", 260, 230, 370),
        ("SP_ROMANCE_VIP_CUTOUT.png", 470, 500, 160),
        ("SP_LT_PLUS_COMBO_CUTOUT.png", 390, 690, 240),
        ("SP_WHITESKIN_COMBO_CUTOUT.png", 460, 950, 170),
        ("SP_DIEU_KINH_HT_CUTOUT.png", 440, 1210, 190),
        ("SP_DA_DAY_HT_COMBO_CUTOUT.png", 420, 1390, 210),
        ("SP_NGOC_LONG_HOAN_CUTOUT.png", 410, 1600, 220),
    ]
    for fn, th, lx, ty in lineup:
        im = Image.open(PROD_DIR / fn).convert("RGBA")
        if im.getbbox():
            im = im.crop(im.getbbox())
        tw = int(round(im.width * (th / float(im.height))))
        im_r = im.resize((tw, th), Image.Resampling.LANCZOS)
        if lx + tw > canvas.width:
            lx = canvas.width - tw - 10
        canvas.alpha_composite(im_r, (lx, ty))
    if canvas.getbbox():
        canvas = canvas.crop(canvas.getbbox())
    canvas.save(out_p, format="PNG")
    return str(out_p)


ensure_8sku_shelf_cutout()

CINE_STYLE = (
    "Photorealistic 8K commercial lifestyle TVC cinematography, ARRI Alexa Mini LF, 35mm prime lens, "
    "natural sunlit daylight & warm realistic architectural interiors, crisp focus, natural skin pores, zero text, zero watermarks. "
)

CHIHANG_ACTION_LOCK = (
    "[STRICT 100% REAL FACE LOCK — VIETNAMESE WOMAN IN REFERENCE]: Keep 100.0% the EXACT SAME Vietnamese woman's face from the portrait reference: "
    "preserve her unmistakable warm full round-oval face shape with full soft cheeks and gently-rounded jawline (STRICTLY NO slimmed V-chin or narrow jaw!), "
    "exact dark eyebrows, warm dark-brown eyes with double eyelids, rounded Vietnamese nose tip, natural coral-rose lips, and glossy dark-brown wavy hair; "
    "tall 170cm poised feminine hourglass figure. CRITICAL: DO NOT make her stand stiffly staring and smiling at the camera — capture her naturally IN THE MIDDLE OF THE DESCRIBED REAL-LIFE ACTION! "
)

NO_TALK = " Natural candid real-life body & hand movement, lips closed or natural subtle expression, zero speaking to camera, zero lip-syncing, no text."

# Build 1-image side-by-side combo boards for hands-on product scenes
COMBO_LT = build_combo_board(HANG_RTFN, PROD_DIR / "SP_LT_PLUS_COMBO_CUTOUT.png", V5_BOARDS / "cb_lt_plus.jpg")
COMBO_GPK = build_combo_board(HANG_RTFN, PROD_DIR / "SP_GEL_PHU_KHANG_SACHET_CUTOUT.png", V5_BOARDS / "cb_gel_phu_khang.jpg")
COMBO_DD = build_combo_board(HANG_RTFN, PROD_DIR / "SP_DA_DAY_HT_COMBO_CUTOUT.png", V5_BOARDS / "cb_da_day.jpg")
COMBO_DK = build_combo_board(HANG_RTFN, PROD_DIR / "SP_DIEU_KINH_HT_CUTOUT.png", V5_BOARDS / "cb_dieu_kinh.jpg")
COMBO_RVIP = build_combo_board(HANG_RTFN, PROD_DIR / "SP_ROMANCE_VIP_CUTOUT.png", V5_BOARDS / "cb_romance_vip.jpg")
COMBO_WS = build_combo_board(HANG_RTFN, PROD_DIR / "SP_WHITESKIN_COMBO_CUTOUT.png", V5_BOARDS / "cb_whiteskin.jpg")
COMBO_VDX = build_combo_board(HANG_RTFN, PROD_DIR / "SP_VIEN_DAT_HOP_XANH_CUTOUT.png", V5_BOARDS / "cb_vien_dat_xanh.jpg")
COMBO_RL = build_combo_board(HANG_RTFN, PROD_DIR / "SP_ROMANCE_LOVE_CUTOUT.png", V5_BOARDS / "cb_romance_love.jpg")
COMBO_NLH = build_combo_board(HANG_RTFN, PROD_DIR / "SP_NGOC_LONG_HOAN_CUTOUT.png", V5_BOARDS / "cb_ngoc_long_hoan.jpg")
COMBO_CEO = build_combo_board(HANG_RTFN, PROD_DIR / "SP_HTPM_ECOSYSTEM_3SKU_CUTOUT.png", V5_BOARDS / "cb_ceo_3sku.jpg")
COMBO_COUPLE = str(V4_COUPLE_ROOT / "00_Clean_Sources" / "couple_rtfn_pair_s07.jpg")

# ==============================================================================
# PART A: 10 COMPLETELY UNRELATED, DISTINCT POSTER BACKGROUND PLATES (4:5 / 9:16)
# ==============================================================================
POSTER_PLATES = [
    {
        "id": "p01_studio_rosequartz",
        "refs": [],
        "prompt": "Vertical luxury cosmetic advertising studio photography (zero people, zero text): a sculpted circular rose-quartz and white marble pedestal rising from crystal-clear pink-tinted water ripples, soft floating ivory silk ribbons and dewy pink lotus petals in warm champagne studio rim lighting, clean airy blush-ivory space at top and sides.",
    },
    {
        "id": "p02_handbag_flatlay",
        "refs": [],
        "prompt": "Vertical top-down editorial flat-lay commercial photography on white Carrara marble (zero people, zero text): an open luxury cream-beige pebbled leather designer handbag in the upper-left corner beside tortoiseshell sunglasses, a folded pastel-pink silk scarf, white phalaenopsis orchid blossoms, and an open sunlit marble space in the center-right for product placement.",
    },
    {
        "id": "p03_herbal_travertine",
        "refs": [],
        "prompt": "Vertical clean modern pharmaceutical studio background (zero people, zero text): sunlit warm cream travertine stone surface in the lower-left with fresh sliced golden turmeric, green Dạ cẩm herbal leaves, chamomile flowers, and warm golden sunbeams casting soft botanical leaf shadows across a clean ivory plaster background.",
    },
    {
        "id": "p04_tearoom_arch_hang",
        "refs": [str(HANG_RTFN)],
        "prompt": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a soft plum-ivory silk ao-style modern blouse in a warm cozy indoor wooden Oriental tea room with soft lantern glow and pink peonies: candid medium shot of her sitting at a carved wooden tea table gently pouring hot herbal tea from a ceramic teapot into a small cup, looking down warmly at the teacup.",
    },
    {
        "id": "p05_ruby_watersplash",
        "refs": [],
        "prompt": "Vertical high-end French perfume & cosmetic dark-luxury studio key visual background (zero people, zero text): dramatic deep ruby-burgundy velvet studio backdrop with a crystal-clear crown splash of pure water and floating velvet red Bulgarian rose petals illuminated by golden rim light above a glossy reflective black-ruby glass floor.",
    },
    {
        "id": "p06_clinical_prism",
        "refs": [],
        "prompt": "Vertical luxury clinical dermatology skincare ad background (zero people, zero text): crisp sunlit ice-blue and pearl-white architectural glass studio split diagonally by a refracting crystal prism light beam, with luminous translucent golden & pearl serum spheres floating near a sleek frosted glass pedestal in the lower right.",
    },
    {
        "id": "p07_home_window_hang",
        "refs": [str(HANG_RTFN)],
        "prompt": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a soft sage-green linen cardigan over a white camisole inside a warm sunlit home reading corner beside sheer white curtains and indoor plants: candid lifestyle shot of her sitting on a cozy armchair reading a wellness journal while holding a warm ceramic mug, peaceful natural expression.",
    },
    {
        "id": "p08_satin_medallion",
        "refs": [],
        "prompt": "Vertical haute-couture romantic gift-box studio photography (zero people, zero text): flowing champagne-blush and magenta-rose silk satin fabric drapes with warm golden candlelight bokeh, fresh blush English roses, and a luminous pearl-marble circular stage in the center.",
    },
    {
        "id": "p09_imperial_gold_herbs",
        "refs": [],
        "prompt": "Vertical royal masculine Oriental wellness studio background (zero people, zero text): deep espresso walnut wood and brushed antique gold background with dramatic warm amber spotlight illuminating a dark black-gold marble pedestal surrounded by premium Cordyceps (Đông trùng hạ thảo), aged Korean ginseng roots, and golden herbal mist.",
    },
    {
        "id": "p10_ceo_sedan_arrival",
        "refs": [str(HANG_RTFN)],
        "prompt": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a sharp royal-navy tailored executive suit with pearl earrings: dynamic candid Forbes-style editorial shot of her stepping confidently out of the open rear door of a sleek black luxury executive sedan onto a sunlit modern glass headquarters forecourt, holding a leather portfolio, looking slightly off-camera in natural forward motion.",
    },
]

# ==============================================================================
# PART B: 42 LIVE REAL-LIFE ACTION VIDEO SCENES (CAR, STREET, HOME, PRODUCT USE)
# Zero standing-and-staring! Every shot has concrete physical storytelling action!
# ==============================================================================
ACTION_SCENES = [
    # --- V01: LT PLUS (6 bespoke action clips) ---
    {
        "id": "act_v01_c01_street_rush",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing an ivory-white tailored blazer and high-waisted skirt, carrying a beige leather handbag and document folder: dynamic 3/4 tracking shot walking briskly along a sunlit tree-lined city sidewalk in the morning while glancing down at her wristwatch in a busy workday rush. Keep head in Y=28%..56%.",
        "vid_p": "Dynamic gimbal tracking shot as the Vietnamese businesswoman walks briskly along the sunlit tree-lined city sidewalk carrying her handbag and glancing at her wristwatch." + NO_TALK,
    },
    {
        "id": "act_v01_c02_office_shift",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing an ivory blazer at a sunlit modern indoor office desk with an open laptop and coffee cup: candid medium shot as she pauses typing, leans back slightly in her office chair, and exhales softly with mild tired discomfort after sitting for hours.",
        "vid_p": "Natural candid indoor office motion: she stops typing on her laptop, sighs subtly, and shifts posture slightly uncomfortable after long desk hours." + NO_TALK,
    },
    {
        "id": "act_v01_c04_car_schedule",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing an ivory blazer sitting in the tan-leather backseat of a moving car with sunlit street trees blurred outside the car window: candid medium shot looking down scrolling her smartphone calendar thoughtfully.",
        "vid_p": "Inside moving luxury car backseat with passing street reflections on window: she scrolls her phone thoughtfully while riding through the city." + NO_TALK,
    },
    {
        "id": "act_v01_c05_vanity_pick",
        "refs": [COMBO_LT],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest ivory tailored blazer over a high-neck silk blouse inside a bright sunlit modern home living-room console table: candid medium-three-quarter shot picking up the pink-and-white LT Plus box (from right half of reference) from a marble tray while looking down warmly at the box.",
        "vid_p": "Candid sunlit home interior action: the businesswoman gently picks up the pink-and-white box from a marble console tray and looks at it calmly." + NO_TALK,
    },
    {
        "id": "act_v01_c06_pouch_pack",
        "refs": [COMBO_LT],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing an ivory blazer at a sunlit marble console table: angled medium-close candid shot as she neatly places the pink LT Plus package (right half of reference) into a chic cream zippered leather handbag organizer.",
        "vid_p": "Natural hands-on indoor action: she places the pink box neatly into her cream leather handbag organizer on the marble table." + NO_TALK,
    },
    {
        "id": "act_v01_c09_boulevard_walk",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a flowing ivory blazer-skirt ensemble: joyful candid tracking shot strolling effortlessly down a sunlit palm-and-flower boulevard sidewalk, hair swaying gently in the morning breeze as she looks across the street refreshed.",
        "vid_p": "Smooth side-tracking gimbal shot as she strolls lightly and confidently down the sunlit tree-lined boulevard with hair moving in the breeze." + NO_TALK,
    },

    # --- V02: GEL PHỤ KHANG (4 bespoke action clips + shares 2 crisp car/street cuts) ---
    {
        "id": "act_v02_c01_desk_stretch",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a pastel ice-blue silk blouse at a bright indoor office glass desk stacked with files and laptop: candid afternoon shot as she takes off reading glasses and stretches her shoulders feeling stuffy after 8 hours indoors.",
        "vid_p": "Candid office afternoon motion: she sets down her pen at the laptop desk and gently stretches her neck and shoulders after long office hours." + NO_TALK,
    },
    {
        "id": "act_v02_c02_bulky_luggage",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a pastel ice-blue dress inside a sunlit walk-in closet at home packing a small carry-on handbag on an ottoman: candid shot looking hesitantly at a large generic plain plastic bottle that won't fit into her compact purse.",
        "vid_p": "Candid indoor packing scene: she tries fitting a bulky plain bottle near her small purse on the closet ottoman and shakes her head slightly." + NO_TALK,
    },
    {
        "id": "act_v02_c04_handbag_sachet",
        "refs": [COMBO_GPK],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a pastel ice-blue dress standing beside a marble entryway console table at home: candid medium shot slipping the compact pink Gel Phụ Khang sachet packet (right half of reference) effortlessly into her small white designer handbag.",
        "vid_p": "Smooth natural indoor action: she slips the slim pink Gel Phụ Khang sachet neatly into her small white handbag at the entryway table." + NO_TALK,
    },
    {
        "id": "act_v02_c09_boutique_stroll",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a pastel ice-blue midi dress carrying a small white shoulder bag: lively tracking shot walking past sunlit outdoor cafe tables and boutique shopfronts on a clean stone sidewalk, carefree active motion.",
        "vid_p": "Lively tracking camera following her as she walks gracefully past sunlit boutique shopfronts and outdoor cafe greenery." + NO_TALK,
    },

    # --- V03: DẠ DÀY HT (5 bespoke action clips) ---
    {
        "id": "act_v03_c01_car_coffee",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a crisp white bow-tie silk blouse and olive skirt sitting in the backseat of a car in morning traffic: candid shot checking emails on her phone in one hand while taking a hurried sip of iced coffee in a clear cup.",
        "vid_p": "Inside moving car in morning city light: she glances at her phone and takes a rushed sip of iced coffee during her busy commute." + NO_TALK,
    },
    {
        "id": "act_v03_c02_stomach_burn",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a white silk blouse at an indoor work desk at midday with an untouched lunchbox nearby: candid medium shot leaning forward slightly, pressing her hand gently over her upper stomach (epigastric area) with a subtle wince of acid heartburn.",
        "vid_p": "Candid empathetic indoor shot: sitting at her desk, she pauses work and presses her hand gently against her upper stomach feeling burning discomfort." + NO_TALK,
    },
    {
        "id": "act_v03_c04_evening_sofa_bloat",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Inside a warm lamp-lit home living room at evening: candid shot sitting on a beige linen sofa rubbing her stomach gently feeling bloated and uncomfortable after eating late.",
        "vid_p": "Warm indoor evening living room: sitting on the sofa, she rubs her abdomen gently with a tired expression from late-night indigestion." + NO_TALK,
    },
    {
        "id": "act_v03_c05_kitchen_daday",
        "refs": [COMBO_DD],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a white silk blouse standing at a sunlit modern home kitchen marble island in the morning: candid medium action shot pouring warm water from a glass carafe into a cup beside the green-and-white Dạ Dày HT box and bottle (right half of reference).",
        "vid_p": "Natural sunlit home kitchen action: she pours warm water into a clear glass beside the green Dạ Dày HT bottle on the kitchen island." + NO_TALK,
    },
    {
        "id": "act_v03_c09_happy_breakfast",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a white silk blouse sitting at a sunlit home dining table with a healthy warm bowl of porridge, fruit, and herbal tea: candid shot enjoying a spoonful of warm breakfast comfortably and peacefully.",
        "vid_p": "Sunlit home dining room: she enjoys a warm healthy morning meal at the wooden dining table with relaxed, comfortable ease." + NO_TALK,
    },

    # --- V04 & DEDICATED ĐIỀU KINH HT (5 bespoke solo action clips — 0% husband!) ---
    {
        "id": "act_v04_c01_sofa_cramps",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest soft cream knit sweater sitting on a sunlit living room window sofa at home: candid empathetic shot holding a warm ceramic tea mug with both hands resting on her lap looking slightly tired and low-energy.",
        "vid_p": "Empathetic sunlit living room shot: sitting on a cushioned window sofa, she holds a warm ceramic tea mug in both hands looking slightly fatigued." + NO_TALK,
    },
    {
        "id": "act_v04_c02_mirror_pale",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest cream blouse beside a bright morning sunlit dressing mirror in a modern home study: candid reflection shot as she touches her cheek softly and rubs her hands together.",
        "vid_p": "Candid sunlit home mirror shot: she looks calmly into the mirror touching her cheek gently and warming her hands." + NO_TALK,
    },
    {
        "id": "act_v04_c04_open_curtains",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing an elegant cream-ivory dress inside an airy home living room: dynamic candid back-three-quarter shot walking to tall glass doors and pulling open sheer white curtains to let warm golden morning sunbeams flood the room.",
        "vid_p": "Graceful indoor home action: she walks up to the tall window and sweeps open the sheer white curtains as warm morning sunlight streams in." + NO_TALK,
    },
    {
        "id": "act_v04_c05_tea_dieukinh",
        "refs": [COMBO_DK],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a cream-ivory dress sitting at a sunlit wooden tea table at home with pink peonies: candid medium action shot holding a glass of warm water while opening the white-and-plum Điều Kinh HT bottle (right half of reference).",
        "vid_p": "Warm indoor home routine: sitting at the sunlit table with peonies, she opens the Điều Kinh HT bottle beside a glass of warm water." + NO_TALK,
    },
    {
        "id": "act_v04_c09_flower_street_walk",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a flowing cream-ivory dress: radiant tracking shot strolling lively along a sunlit bougainvillea-lined garden street in the morning breeze, glowing rosy complexion, carrying a small woven handbag.",
        "vid_p": "Fluid tracking camera following her walking gracefully along a sunlit flower-lined street with glowing vitality and breeze in her hair." + NO_TALK,
    },

    # --- V05: DDVS ROMANCE VIP (4 bespoke action clips) ---
    {
        "id": "act_v05_c01_hot_sun_walk",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest ruby-rose silk midi dress walking outdoors along a bright midday paved promenade under strong tropical sun: candid shot raising one hand to shade her eyes from the hot midday glare.",
        "vid_p": "Outdoor sunlit tracking shot: walking in bright midday sunshine, she raises her hand lightly to shade her brow from the sun." + NO_TALK,
    },
    {
        "id": "act_v05_c02_bathroom_check",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest ruby-rose blouse beside a bright white-marble cosmetic boutique counter with sunlit window: candid shot holding a plain generic bottle, reading the ingredients label skeptically, and setting it aside.",
        "vid_p": "Candid sunlit marble counter scene: she reads the label on a plain bottle skeptically and sets it back down on the counter." + NO_TALK,
    },
    {
        "id": "act_v05_c05_bathroom_rvip",
        "refs": [COMBO_RVIP],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest ruby-rose silk blouse beside a sunlit white marble vanity console accented with fresh red roses: candid action shot placing the red-and-white Romance VIP box (right half of reference) onto a crystal tray beside a floral vase.",
        "vid_p": "Natural sunlit marble console action: she places the red-and-white Romance VIP box neatly onto a crystal tray beside fresh red roses." + NO_TALK,
    },
    {
        "id": "act_v05_c09_car_exit_breeze",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a ruby-rose silk dress: dynamic candid shot stepping gracefully out of a white luxury SUV onto a sunlit palm-lined coastal avenue, smoothing her silk dress in the fresh breeze.",
        "vid_p": "Smooth tracking shot as she steps out of a white luxury car onto a sunlit avenue, hair and silk dress moving lightly in the breeze." + NO_TALK,
    },

    # --- V06: LEGEND WHITESKIN (4 bespoke action clips) ---
    {
        "id": "act_v06_c01_sunglasses_sun",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a tailored white belted blazer-dress stepping onto a bright sunlit coastal crosswalk from beside a parked car: candid action shot putting on chic sunglasses against the intense UV sunlight.",
        "vid_p": "Candid outdoor street motion: walking under bright coastal sunshine, she slips on her sunglasses and shields her cheek lightly from harsh UV rays." + NO_TALK,
    },
    {
        "id": "act_v06_c05_kitchen_whiteskin",
        "refs": [COMBO_WS],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a crisp white blazer-dress at a sunlit white kitchen breakfast bar in the morning: candid medium action shot holding a clear glass of water while taking her morning supplement from the blue-and-amber Legend WhiteSkin bottle (right half of reference).",
        "vid_p": "Sunlit morning indoor routine: at her white breakfast counter, she holds a glass of water beside the Legend WhiteSkin bottle and box." + NO_TALK,
    },
    {
        "id": "act_v06_c06_car_selfie_cam",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Sitting in the sunlit leather backseat of a moving car with natural daylight through the side window: candid shot holding her smartphone at arm's length checking her bare-skin natural camera reflection and touching her luminous rosy cheek pleased.",
        "vid_p": "Inside sunlit moving car: she checks her bare-skin reflection on her phone screen by the car window and touches her smooth radiant cheek." + NO_TALK,
    },
    {
        "id": "act_v06_c09_coastal_promenade",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a tailored white blazer-dress: dynamic tracking shot walking joyfully along a sunlit oceanfront stone promenade with turquoise sea and palms in the background, radiant porcelain-rosy skin glowing in natural daylight.",
        "vid_p": "Smooth sunlit tracking shot following her brisk confident walk along the coastal stone promenade with sea breeze." + NO_TALK,
    },

    # --- V07: VIÊN ĐẶT PHỤ KHOA HỘP XANH (4 bespoke action clips) ---
    {
        "id": "act_v07_c01_home_tidy_tired",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest cream blouse and tailored slacks inside a warm sunlit family living room: candid shot folding a soft knit throw blanket on the sofa and sitting down quietly with a thoughtful sigh.",
        "vid_p": "Warm candid indoor home scene: she folds a soft throw blanket on the living room sofa and sits down quietly looking thoughtful." + NO_TALK,
    },
    {
        "id": "act_v07_c05_nightstand_greenbox",
        "refs": [COMBO_VDX],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest cream-ivory tailored blazer in a calm sunlit home study room: candid medium shot sitting beside a wooden cabinet holding the emerald-green Hằng Thu box (right half of reference) and placing it neatly into a wooden organizer drawer.",
        "vid_p": "Calm sunlit indoor action: she holds the green box beside a wooden cabinet and places it neatly into the organizer drawer." + NO_TALK,
    },
    {
        "id": "act_v07_c06_car_buckle_confident",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a cream tailored blazer with emerald earrings sitting in the passenger seat of a sleek car in the morning: candid shot closing the car door and adjusting the mirror with renewed poise and confidence.",
        "vid_p": "Natural car interior action: sitting inside her car in morning light, she adjusts the mirror ready to start her day with poised energy." + NO_TALK,
    },
    {
        "id": "act_v07_c09_livingroom_flowers",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a cream tailored outfit in a sunlit home dining room: joyful candid shot arranging fresh white lilies and green eucalyptus stems into a glass vase on the table, serene and fulfilled.",
        "vid_p": "Sunlit indoor home lifestyle: she arranges fresh white flowers into a crystal vase on the dining table with graceful movements." + NO_TALK,
    },

    # --- V08: VIÊN DƯỠNG ROMANCE LOVE (4 bespoke action clips) ---
    {
        "id": "act_v08_c01_bedside_book_dusk",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a modest ivory silk blouse in a warm golden lamp-lit home reading lounge at evening: candid shot sitting in a plush armchair closing a hardcover book slowly on her lap with a quiet, wistful expression.",
        "vid_p": "Warm evening home reading lounge: sitting in an armchair by a golden table lamp, she gently closes her hardcover book and looks down thoughtfully." + NO_TALK,
    },
    {
        "id": "act_v08_c05_vanity_romancelove",
        "refs": [COMBO_RL],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a chic ivory tweed jacket at a warm sunlit living-room console table with blush roses and crystal perfume bottles: candid medium action shot placing the magenta-pink gift box (right half of reference) onto a pearl tray.",
        "vid_p": "Graceful sunlit indoor action: she places the magenta-pink gift box beside crystal perfume bottles and pink roses on the pearl tray." + NO_TALK,
    },
    {
        "id": "act_v08_c06_evening_car_ride",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing an ivory tweed jacket with pearl earrings riding in the backseat of a luxury car during warm golden-hour sunset with city lights beginning to glow outside the window: candid shot adjusting her pearl earring softly.",
        "vid_p": "Golden-hour luxury car ride: warm sunset light glides across the window as she touches her pearl earring with gentle poise." + NO_TALK,
    },
    {
        "id": "act_v08_c09_terrace_tea_pour",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing an ivory tweed set at a sunlit garden tea table adorned with blush English roses: candid action shot lifting a porcelain teapot to pour fragrant rose tea into two delicate teacups.",
        "vid_p": "Romantic sunlit garden tea action: she gracefully pours warm rose tea from a porcelain teapot surrounded by blooming blush roses." + NO_TALK,
    },

    # --- V09 & DEDICATED NGỌC LONG HOÀN (4 bespoke solo action clips + 1 warm tea couple end shot) ---
    {
        "id": "act_v09_c01_late_study_care",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a burgundy silk cardigan inside a warm wood-paneled home study room at night: candid shot tidying folders beside an open laptop and a cooled cup of tea on a mahogany desk with an empathetic caring expression.",
        "vid_p": "Warm indoor home study scene: she tidy papers beside a late-night work laptop on a wooden desk with quiet caring attentiveness." + NO_TALK,
    },
    {
        "id": "act_v09_c04_brew_herbal_tea",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a crimson-burgundy tailored blazer-dress in a sunlit modern home dining room: candid medium shot pouring steaming golden herbal tea from a glass teapot onto a wooden serving tray.",
        "vid_p": "Sunlit indoor morning routine: she pours warm golden herbal tea into a porcelain cup on a wooden tray." + NO_TALK,
    },
    {
        "id": "act_v09_c05_tray_ngoclonghoan",
        "refs": [COMBO_NLH],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a crimson-burgundy blazer-dress in a sunlit living room: candid medium action shot placing the dark-amber-and-gold Ngọc Long Hoàn jar (right half of reference) thoughtfully beside a warm teacup on the wooden coffee table.",
        "vid_p": "Thoughtful indoor home action: she places the Ngọc Long Hoàn jar neatly beside a steaming cup of tea on the living room table." + NO_TALK,
    },
    {
        "id": "act_v09_c06_giftbag_car_step",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a crimson-burgundy tailored blazer-dress stepping onto a sunlit villa driveway beside a parked black car while carrying a luxury burgundy-gold gift bag into the house.",
        "vid_p": "Sunlit outdoor driveway tracking shot: carrying a luxury burgundy-gold gift bag, she walks from beside her car toward the sunlit house entrance." + NO_TALK,
    },
    {
        "id": "act_nlh_couple_tea_end",
        "refs": [COMBO_COUPLE],
        "img_p": CINE_STYLE + "[STRICT DUAL REAL FACE LOCK]: Keep 100% exact real faces of BOTH people in reference (LEFT = Vietnamese husband ~40yo neat short black hair in crisp white dress shirt; RIGHT = CEO Nguyen Thi Hang full round-oval face, full soft cheeks in crimson blazer-dress). Candid sunlit home garden veranda morning action: they sit side-by-side at a wooden tea table clinking warm porcelain teacups together happily in natural conversation, framed cleanly in the upper-middle so faces are 100% clear.",
        "vid_p": "Warm candid morning veranda action: the Vietnamese husband and wife sit together at a sunlit garden tea table sharing warm tea in happy natural harmony." + NO_TALK,
    },

    # --- V10: CEO NGUYỄN THỊ HẰNG & HỆ SINH THÁI HTPM (4 bespoke executive action clips) ---
    {
        "id": "act_v10_c01_ceo_car_ipad",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a sharp ocean-navy executive suit vest with a pearl necklace sitting in the leather backseat of a luxury sedan gliding along sunlit coastal Nha Trang boulevard (turquoise sea visible outside window): candid shot reviewing brand strategy notes on a tablet.",
        "vid_p": "Executive luxury car interior gliding along sunlit coastal avenue: she reviews notes on her tablet and glances thoughtfully out at the sunlit city." + NO_TALK,
    },
    {
        "id": "act_v10_c02_hq_entrance_stride",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a royal-navy executive suit with pearl necklace: dynamic low-angle tracking shot stepping out of a black sedan and striding purposefully across a sunlit glass office plaza holding a leather portfolio.",
        "vid_p": "Confident cinematic tracking shot as the Vietnamese female CEO strides purposefully across a sunlit modern glass headquarters plaza." + NO_TALK,
    },
    {
        "id": "act_v10_c04_boardroom_inspect",
        "refs": [COMBO_CEO],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a royal-navy suit in a sunlit glass executive boardroom overlooking Nha Trang bay: candid action shot sitting at the conference table inspecting the real Hằng Thu Pharma product boxes (right half of reference) alongside a quality-check binder and pen.",
        "vid_p": "Candid executive boardroom action: she examines the Hằng Thu Pharma product packages on the glass conference table and writes a quality note in her binder." + NO_TALK,
    },
    {
        "id": "act_v10_c06_coastal_ceo_walk",
        "refs": [str(HANG_RTFN)],
        "img_p": CINE_STYLE + CHIHANG_ACTION_LOCK + "Wearing a royal-navy tailored suit with pearl necklace: inspiring tracking shot walking gracefully along a sunlit palm-lined coastal Nha Trang walkway overlooking turquoise water, calm visionary demeanour in motion.",
        "vid_p": "Inspiring sunlit tracking camera following her poised walk along the palm-lined Nha Trang coastal walkway." + NO_TALK,
    },
]

# Map EVERY SINGLE ONE OF THE 12 VIDEOS to 10 DISTINCT CUTS (~3.6s - 4.2s each, ZERO repeated clip within a video!)
# Legend of clip sources:
# - "act_..." -> V5_CFR_VID / "<id>.mp4" (Brand-new live real-life action Flow clip)
# - "cgi_vXX" -> Existing pure 3D CGI Mechanism Flow clip (V01_U02, DK4_C03, NLH4_C03, etc.)
# - "mac_vXX" -> Existing pure 3D Botanical Macro Flow clip (V01_U04, DK4_C05, NLH4_C04, etc.)
# - "pod_vXX" -> V5_PODIUM_VID / "pod_vXX.mp4" (Ultra-crisp 100% real SP_*_CUTOUT 3D parallax & water-shimmer studio video)
# - "nlh_back_pain" -> V4 NLH4_C02.mp4 (Husband rubbing tired lower back at desk)

VIDEO_10CUT_MAPS = {
    "v01_lt_plus": [
        "act_v01_c01_street_rush",     # Cut 1 (Hook A: bước vội trên phố đi làm)
        "act_v01_c02_office_shift",    # Cut 2 (Hook B: ngồi bàn văn phòng bí bách)
        "cgi_v01",                     # Cut 3 (3D CGI màng chắn pH + Thẻ 1)
        "act_v01_c04_car_schedule",    # Cut 4 (Đi xe ô tô xem lịch trình)
        "act_v01_c05_vanity_pick",     # Cut 5 (Bàn phấn phòng ngủ lấy hộp LT Plus)
        "act_v01_c06_pouch_pack",      # Cut 6 (Xếp LT Plus vào túi cá nhân)
        "pod_v01",                     # Cut 7 (Bục Studio LT Plus thật + Thẻ 2)
        "mac_v01",                     # Cut 8 (3D Macro Sen hồng & Cúc La Mã + Thẻ 3)
        "act_v01_c09_boulevard_walk",  # Cut 9 (Dạo bước rạng rỡ dưới phố)
        "act_v07_c06_car_buckle_confident", # Cut 10 Top Window (Lên xe đi làm tự tin đồng bộ vest kem + Split End-Card)
    ],
    "v02_gel_phu_khang": [
        "act_v02_c01_desk_stretch",    # Cut 1 (Ngồi văn phòng 8 tiếng mỏi vai)
        "act_v02_c02_bulky_luggage",   # Cut 2 (Chai to cồng kềnh khó bỏ túi)
        "cgi_v02",                     # Cut 3 (3D CGI bọt tơ mịn + Thẻ 1)
        "act_v01_c01_street_rush",     # Cut 4 (Di chuyển bận rộn ngoài phố)
        "act_v02_c04_handbag_sachet",  # Cut 5 (Thả gói 5ml Gel Phụ Khang vào túi xách)
        "act_v01_c04_car_schedule",    # Cut 6 (Ngồi xe ô tô đi công tác gọn nhẹ)
        "pod_v02",                     # Cut 7 (Bục Studio Gel Phụ Khang thật + Thẻ 2)
        "mac_v02",                     # Cut 8 (3D Macro Hoa lan trắng & Trà xanh + Thẻ 3)
        "act_v02_c09_boutique_stroll", # Cut 9 (Dạo phố boutique chiều năng động)
        "act_v01_c09_boulevard_walk",  # Cut 10 Top Window + Split End-Card
    ],
    "v03_da_day_ht": [
        "act_v03_c01_car_coffee",      # Cut 1 (Ngồi ô tô uống vội cà phê đá buổi sáng)
        "act_v03_c02_stomach_burn",    # Cut 2 (Ngồi bàn làm việc ôm vùng thượng vị nóng rát)
        "cgi_v03",                     # Cut 3 (3D CGI Dạ dày pha lê & thảo mộc + Thẻ 1)
        "act_v03_c04_evening_sofa_bloat", # Cut 4 (Tối ngồi sofa xoa bụng đầy hơi)
        "act_v04_c04_open_curtains",   # Cut 5 (Sáng mở rèm đón nắng ngày mới)
        "act_v03_c05_kitchen_daday",   # Cut 6 (Đứng bếp rót nước ấm bên lọ Dạ Dày HT)
        "pod_v03",                     # Cut 7 (Bục Studio Dạ Dày HT thật + Thẻ 2)
        "mac_v03",                     # Cut 8 (3D Macro Nghệ, Dạ cẩm, Hoàng liên + Thẻ 3)
        "act_v03_c09_happy_breakfast", # Cut 9 (Ăn sáng ngon miệng êm bụng trong nhà)
        "act_v02_c09_boutique_stroll", # Cut 10 Top Window + Split End-Card
    ],
    "v04_dieu_kinh_ht": [
        "act_v04_c01_sofa_cramps",     # Cut 1 (Ngồi ghế cửa sổ ôm cốc ấm vào bụng dưới)
        "act_v04_c02_mirror_pale",     # Cut 2 (Soi gương bàn phấn thấy da kém tươi, tay lạnh)
        "cgi_v04",                     # Cut 3 (3D CGI Dải lụa khí huyết hồng ngọc + Thẻ 1)
        "act_v04_c04_open_curtains",   # Cut 4 (Mở rèm voan phòng khách đón nắng ấm)
        "act_v04_c05_tea_dieukinh",    # Cut 5 (Ngồi bàn gỗ mở lọ Điều Kinh HT cùng nước ấm)
        "act_v06_c06_car_selfie_cam",  # Cut 6 (Ngồi xe ô tô sắc diện hồng hào tươi tắn)
        "pod_v04",                     # Cut 7 (Bục Studio Điều Kinh HT thật + Thẻ 2)
        "mac_v04",                     # Cut 8 (3D Macro Đương quy & Hoa mẫu đơn + Thẻ 3)
        "act_v04_c09_flower_street_walk", # Cut 9 (Dạo đường hoa nắng sớm rạng rỡ)
        "act_v08_c09_terrace_tea_pour",   # Cut 10 Top Window + Split End-Card
    ],
    "v05_romance_vip": [
        "act_v05_c01_hot_sun_walk",    # Cut 1 (Đi bộ ngoài trời nắng gắt oi bức)
        "act_v05_c02_bathroom_check",  # Cut 2 (Đọc nhãn chai xà phòng tẩy mạnh phân vân)
        "cgi_v05",                     # Cut 3 (3D CGI Lụa hồng ẩm chuẩn pH + Thẻ 1)
        "act_v04_c04_open_curtains",   # Cut 4 (Không gian sống thoáng đãng ngập nắng)
        "act_v05_c05_bathroom_rvip",   # Cut 5 (Đặt Romance VIP lên kệ đá hoa hồng phòng tắm)
        "act_v02_c09_boutique_stroll", # Cut 6 (Sải bước thanh thoát suốt ngày dài)
        "pod_v05",                     # Cut 7 (Bục Studio Romance VIP thật + Thẻ 2)
        "mac_v05",                     # Cut 8 (3D Macro Hoa hồng đỏ & Lô hội + Thẻ 3)
        "act_v05_c09_car_exit_breeze", # Cut 9 (Bước xuống xe ô tô lụa bay trong gió)
        "act_v04_c09_flower_street_walk", # Cut 10 Top Window + Split End-Card
    ],
    "v06_whiteskin": [
        "act_v06_c01_sunglasses_sun",  # Cut 1 (Bước ra nắng biển đeo kính che gò má)
        "act_v04_c02_mirror_pale",     # Cut 2 (Soi gương bàn phấn kiểm tra nền da sau nắng)
        "cgi_v06",                     # Cut 3 (3D CGI Biểu bì pha lê L-Glutathione + Thẻ 1)
        "act_v04_c04_open_curtains",   # Cut 4 (Mở rèm đón ban mai trong trẻo tại nhà)
        "act_v06_c05_kitchen_whiteskin", # Cut 5 (Đứng quầy bếp uống viên dưỡng WhiteSkin)
        "act_v06_c06_car_selfie_cam",  # Cut 6 (Ngồi xe ô tô kiểm tra cam thường tự tin)
        "pod_v06",                     # Cut 7 (Bục Studio Legend WhiteSkin thật + Thẻ 2)
        "mac_v06",                     # Cut 8 (3D Macro Ngọc trai, Vitamin E & NMN + Thẻ 3)
        "act_v06_c09_coastal_promenade", # Cut 9 (Dạo đại lộ ven biển nắng vàng sáng da)
        "act_v01_c09_boulevard_walk",    # Cut 10 Top Window + Split End-Card
    ],
    "v07_vien_dat_xanh": [
        "act_v07_c01_home_tidy_tired", # Cut 1 (Gấp chăn trên sofa gia đình trầm tư sau sinh)
        "act_v08_c01_bedside_book_dusk", # Cut 2 (Ngồi bên đèn phòng ngủ nhiều nỗi niềm khó nói)
        "cgi_v07",                     # Cut 3 (3D CGI Dải lụa ngọc bích săn chắc + Thẻ 1)
        "act_v04_c04_open_curtains",   # Cut 4 (Mở rèm đón ánh nắng mới tích cực)
        "act_v07_c05_nightstand_greenbox", # Cut 5 (Cầm hộp xanh Viên Đặt cất ngăn tủ đầu giường)
        "act_v07_c06_car_buckle_confident", # Cut 6 (Ngồi lên xe ô tô đi làm tự chủ rạng ngời)
        "pod_v07",                     # Cut 7 (Bục Studio Viên Đặt Hộp Xanh thật + Thẻ 2)
        "mac_v07",                     # Cut 8 (3D Macro Lá trầu không & Hoa nhài + Thẻ 3)
        "act_v07_c09_livingroom_flowers", # Cut 9 (Cắm hoa tươi trong phòng khách viên mãn)
        "act_v04_c09_flower_street_walk", # Cut 10 Top Window + Split End-Card
    ],
    "v08_romance_love": [
        "act_v08_c01_bedside_book_dusk", # Cut 1 (Ngồi bên giường ánh đèn ấm khép trang sách trầm tư)
        "act_v04_c02_mirror_pale",       # Cut 2 (Ngồi bàn phấn chăm chút bản thân buổi tối)
        "cgi_v08",                       # Cut 3 (3D CGI Lụa hồng sen cấp ẩm + Thẻ 1)
        "act_v08_c09_terrace_tea_pour",  # Cut 4 (Rót trà hoa hồng chiều thư thái)
        "act_v08_c05_vanity_romancelove", # Cut 5 (Mở ruy-băng đặt hộp Romance Love lên khay ngọc)
        "act_v08_c06_evening_car_ride",  # Cut 6 (Ngồi xe ô tô dưới hoàng hôn đi hẹn hò)
        "pod_v08",                       # Cut 7 (Bục Studio Romance Love thật + Thẻ 2)
        "mac_v08",                       # Cut 8 (3D Macro Hoa hồng Anh & Tinh chất + Thẻ 3)
        "act_v05_c09_car_exit_breeze",   # Cut 9 (Bước xuống xe trong gió chiều quyến rũ)
        "act_v07_c09_livingroom_flowers", # Cut 10 Top Window + Split End-Card
    ],
    "v09_ngoc_long_hoan": [
        "act_v09_c01_late_study_care",   # Cut 1 (Thu dọn bàn làm việc khuya thấu hiểu áp lực)
        "act_v09_c06_giftbag_car_step",  # Cut 2 (Cầm túi quà sức khỏe từ xe bước vào nhà)
        "cgi_v09",                       # Cut 3 (3D CGI Cột sống & Nguyên khí thận vàng kim + Thẻ 1)
        "act_v09_c04_brew_herbal_tea",   # Cut 4 (Pha ấm trà thảo mộc nóng trong phòng ăn)
        "act_v09_c05_tray_ngoclonghoan", # Cut 5 (Đặt lọ Ngọc Long Hoàn chu đáo cạnh tách trà)
        "act_v07_c09_livingroom_flowers", # Cut 6 (Chăm chút tổ ấm ngập tràn sinh khí)
        "pod_v09",                       # Cut 7 (Bục Studio Ngọc Long Hoàn thật + Thẻ 2)
        "mac_v09",                       # Cut 8 (3D Macro Đông trùng hạ thảo & Nhân sâm + Thẻ 3)
        "act_v03_c09_happy_breakfast",   # Cut 9 (Bữa sáng ấm cúng tràn năng lượng tại nhà)
        "act_v06_c09_coastal_promenade", # Cut 10 Top Window (0% chồng ở V09!) + Split End-Card
    ],
    "v10_ceo_thuong_hieu": [
        "act_v10_c01_ceo_car_ipad",      # Cut 1 (Ngồi xe sedan lướt đại lộ biển đọc iPad chiến lược)
        "act_v10_c02_hq_entrance_stride", # Cut 2 (Bước xuống xe sải bước vào tòa nhà kính)
        "cgi_v10",                       # Cut 3 (3D CGI Bản đồ Việt Nam kết nối từ Nha Trang + Thẻ 1)
        "act_v10_c04_boardroom_inspect", # Cut 4 (Họp bàn kính kiểm định chất lượng sản phẩm HTPM)
        "act_v01_c01_street_rush",       # Cut 5 (Nhịp làm việc năng động quyết liệt mỗi ngày)
        "act_v10_c06_coastal_ceo_walk",  # Cut 6 (Dạo bước điềm đạm bên hàng cọ đại lộ Nha Trang)
        "pod_v10",                       # Cut 7 (Bục Studio Hệ Sinh Thái 8 Sản Phẩm HTPM thật + Thẻ 2)
        "mac_v10",                       # Cut 8 (Không gian trưng bày chuẩn mực thương hiệu + Thẻ 3)
        "act_v09_c04_brew_herbal_tea",   # Cut 9 (Phút đời thường giản dị pha trà ấm tại gia)
        "act_v06_c09_coastal_promenade", # Cut 10 Top Window + Split End-Card
    ],
    # Dedicated Flagship #1: Ngọc Long Hoàn (Anh Hải ONLY in final scene!)
    "flagship_ngoc_long_hoan": [
        "act_v09_c01_late_study_care",   # Cut 1 (Chị Hằng thu dọn bàn làm việc khuya thấu hiểu chồng)
        "nlh_back_pain",                 # Cut 2 (Người chồng ngồi bàn làm việc xoa lưng mỏi mệt)
        "cgi_v09",                       # Cut 3 (3D CGI Cột sống & Nguyên khí thận vàng kim + Thẻ 1)
        "mac_v09",                       # Cut 4 (3D Macro Đông trùng hạ thảo & Nhân sâm quý)
        "act_v09_c04_brew_herbal_tea",   # Cut 5 (Chị Hằng pha ấm trà thảo mộc nóng tại nhà)
        "act_v09_c05_tray_ngoclonghoan", # Cut 6 (Chị Hằng đặt lọ Ngọc Long Hoàn cạnh tách trà)
        "act_v09_c06_giftbag_car_step",  # Cut 7 (Chị Hằng mang túi quà từ xe bước vào nhà)
        "pod_v09",                       # Cut 8 (Bục Studio Ngọc Long Hoàn thật + Thẻ 2)
        "act_v07_c09_livingroom_flowers", # Cut 9 (Không gian gia đình ấm áp tràn sinh khí)
        "act_nlh_couple_tea_end",        # Cut 10 (CẢNH CUỐI DUY NHẤT CÓ ANH HẢI: Vợ chồng nâng tách trà bên hiên nhà trong Khung Trên không chữ che mặt + End-Card Khung Dưới!)
    ],
    # Dedicated Flagship #2: Điều Kinh HT (0% chồng xuyên suốt!)
    "flagship_dieu_kinh_ht": [
        "act_v04_c01_sofa_cramps",       # Cut 1 (Ngồi ôm cốc ấm vào bụng dưới ngày đèn đỏ)
        "act_v04_c02_mirror_pale",       # Cut 2 (Soi gương thấy sắc mặt kém hồng hào, tay lạnh)
        "cgi_v04",                       # Cut 3 (3D CGI Dải lụa khí huyết hồng ngọc + Thẻ 1)
        "act_v04_c04_open_curtains",     # Cut 4 (Mở rèm voan phòng khách đón nắng ban mai)
        "act_v04_c05_tea_dieukinh",      # Cut 5 (Mở lọ Điều Kinh HT dùng cùng nước ấm tại bàn trà)
        "act_v08_c09_terrace_tea_pour",  # Cut 6 (Rót trà hoa hồng chăm dưỡng cơ thể từ gốc)
        "pod_v04",                       # Cut 7 (Bục Studio Điều Kinh HT thật + Thẻ 2)
        "mac_v04",                       # Cut 8 (3D Macro Đương quy & Hương phụ + Thẻ 3)
        "act_v06_c06_car_selfie_cam",    # Cut 9 (Ngồi xe ô tô đi làm nhẹ tênh sắc diện hồng hào)
        "act_v04_c09_flower_street_walk", # Cut 10 Top Window (Dạo đường hoa rạng rỡ) + Split End-Card
    ],
}


def export_v5_jobs_json():
    jobs = {
        "poster_plates": [
            {
                "id": p["id"],
                "refs": p["refs"],
                "prompt": p["prompt"],
                "png_path": str(V5_IMG_DIR / f"{p['id']}.png"),
                "jpg_path": str(V5_IMG_DIR / f"{p['id']}.jpg"),
            }
            for p in POSTER_PLATES
        ],
        "action_scenes": [
            {
                "id": s["id"],
                "refs": s["refs"],
                "img_p": s["img_p"],
                "vid_p": s["vid_p"],
                "png_path": str(V5_IMG_DIR / f"{s['id']}.png"),
                "jpg_path": str(V5_IMG_DIR / f"{s['id']}.jpg"),
                "raw_mp4": str(V5_RAW_VID / f"{s['id']}_raw.mp4"),
                "cfr_mp4": str(V5_CFR_VID / f"{s['id']}.mp4"),
            }
            for s in ACTION_SCENES
        ],
    }
    out_json = V5_DIR / "v5_jobs.json"
    out_json.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[V5 MANIFEST READY] {len(POSTER_PLATES)} Poster Plates + {len(ACTION_SCENES)} Live Action Video Scenes -> {out_json}")


if __name__ == "__main__":
    export_v5_jobs_json()
