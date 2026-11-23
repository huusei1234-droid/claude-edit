import json, os
from PIL import Image

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
NEW_CHAR_RAW_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR = os.path.join(BASE_DIR, "sets")

combo_sanh_nau = os.path.join(SETS_DIR, "_combo_sanh_nau.jpg")
combo_pk_sang  = os.path.join(SETS_DIR, "_combo_pk_sang.jpg")

SPLIT_SHEET_PREFIX = (
    "Photorealistic Vietnamese family drama character reference sheet split cleanly into TWO side-by-side vertical panels separated by a thin white line "
    "(LEFT panel: tight close-up portrait from chest up looking toward camera with natural skin texture; "
    "RIGHT panel: full-body head-to-toe standing shot inside a modern corporate building lobby). "
    "Pure photorealistic Vietnamese cinema lighting, ZERO text, ZERO badges with words, ZERO watermarks. "
)

SET_9X16 = (
    "Vertical 9:16 bright, crystal-clear photorealistic Vietnamese cinema wide-angle location photography "
    "(Sony A7R5 24mm f/2.8, abundant natural daylight, deep architectural space suitable for full-body wide shots, ZERO text, ZERO readable signs, ZERO logos, ZERO watermarks): "
)

jobs = [
    {
        "id": "G07_02_HungBaoVe",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G07_02 - Hùng (Bảo vệ sảnh tập đoàn cô Lan) [Đồng phục bảo vệ xanh].png"),
        "refs": [],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: Chú Hùng, a stern, snobbish 42-year-old Vietnamese corporate building security guard with short buzzed black hair, thick brows, arrogant expression, "
            "wearing a crisp olive-green Vietnamese security guard button-up shirt with shoulder epaulets, dark olive trousers, black leather belt, and black shoes (plain uniform, NO text patches)."
        ),
    },
    {
        "id": "V2_BO2_SanVuonTuoiRau",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V2_BO2_SanVuonTuoiRau.png"),
        "refs": [{"path": combo_pk_sang, "name": "wall_ref.jpg"}],
        "prompt": SET_9X16 + (
            "wide establishing view of a sunlit affluent Vietnamese suburban villa front courtyard and neat home vegetable-and-bonsai garden in morning sunlight; "
            "in the foreground-left is a neat raised garden bed of lush green leafy vegetables with a coiled grey garden watering hose resting beside it, paved stone courtyard path in the center, "
            "and in the background the villa's wide glass porch doors reveal a glimpse of a warm interior decorative fluted wood slat and cream marble accent wall inside; empty scene, ZERO people."
        ),
    },
    {
        "id": "V2_BO3_SieuThiDongNguoi",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V2_BO3_SieuThiDongNguoi.png"),
        "refs": [],
        "prompt": SET_9X16 + (
            "wide establishing shot down a bright, spacious modern Vietnamese supermarket aisle stocked neatly with red-and-gold premium health gift boxes and colourful grocery packages (softly blurred product graphics with ZERO readable text or letters); "
            "in the mid-ground and background, 8 to 10 everyday Vietnamese shoppers (men and women in casual clothes pushing shopping carts and browsing shelves) create a lively, realistic crowded supermarket atmosphere."
        ),
    },
    {
        "id": "V3_BO2_SanhTapDoanDongNguoi",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V3_BO2_SanhTapDoanDongNguoi.png"),
        "refs": [{"path": combo_sanh_nau, "name": "lobby_wall_ref.jpg"}],
        "prompt": SET_9X16 + (
            "grand double-height luxury Vietnamese corporate headquarters ground-floor lobby with polished cream marble floors and towering decorative walls of dark-walnut vertical fluted wood slats and bookmatched gold-vein marble panels; "
            "in the mid-ground and background, 10 to 12 smartly dressed Vietnamese office employees in business attire walk and stand naturally near the reception and elevator hall, creating a bustling corporate lobby crowd (ZERO wall logos, ZERO text)."
        ),
    },
    {
        "id": "V4_BO2_PhongKhachNhaTu",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V4_BO2_PhongKhachNhaTu.png"),
        "refs": [{"path": combo_pk_sang, "name": "living_wall_ref.jpg"}],
        "prompt": SET_9X16 + (
            "wide angle interior shot of a warm, spacious modern Vietnamese luxury villa living room in soft golden daylight; "
            "cream L-shaped sofa, wooden tea table with ceramic tea set in the center, and a prominent full-height decorative feature wall behind the sofa combining glossy cream-white marble-vein bamboo charcoal panels framed by honey-oak vertical fluted wood slats with warm recessed cove lighting; empty room, ZERO people."
        ),
    },
    {
        "id": "V5_BO2_DamCuoiDongNguoi",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V5_BO2_DamCuoiDongNguoi.png"),
        "refs": [{"path": combo_pk_sang, "name": "villa_wall_ref.jpg"}],
        "prompt": SET_9X16 + (
            "wide establishing shot of a lively Vietnamese wedding morning in the spacious courtyard right in front of an affluent modern villa (through the open grand entrance doors behind, a cream-gold marble and fluted wood lobby wall is visible); "
            "a sleek white luxury bridal sedan decorated with fresh pink-and-white roses is parked in the center-left driveway, and standing along both sides of the courtyard are 12 to 15 festively dressed Vietnamese wedding guests and relatives in suits and colorful pastel Áo Dài smiling and watching the arrival (STRICTLY ZERO text banners, ZERO words, ZERO Chinese characters)."
        ),
    },
    {
        "id": "V5_BO3_KhoangXeHoa",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V5_BO3_KhoangXeHoa.png"),
        "refs": [],
        "prompt": SET_9X16 + (
            "medium-wide interior view of the spacious cream-beige quilted leather backseat cabin of a luxury white wedding sedan car parked in daylight; "
            "the rear right passenger door is open, showing blurred festive flowers and a bright villa courtyard outside in natural morning sunlight; empty car seat, ZERO people."
        ),
    },
]

spec_path = os.path.join(BASE_DIR, "chatgpt_v2_crowd_wide_assets.json")
with open(spec_path, "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(jobs)} ChatGPT V2 crowd & wide-set jobs -> {spec_path}")
