"""
Prepare all 38 ChatGPT Asset Jobs for the 10-Episode K4 Cinema Batch (`261123`):
- Auto-detects exact white vertical divider on every existing K4 character sheet so face & full-body crops have 0% divider bleed!
- Prepares 15 K4 2-panel Character/Outfit Sheets (`1:1`, max 1 face ref -> 100% native ChatGPT `2MB+` PNG, chat immediately deleted!).
- Prepares 23 Bespoke `9:16` Location & Crowd Sets (subtle `MS Nội Thất` marble-vein & fluted wood decorative walls ONLY in modern indoor apartments/offices/restaurants/banquet halls; 0% luxury walls in poor countryside homes, street stalls, or construction sites!).
"""
import json, os, shutil
from PIL import Image

BASE_DIR = r"d:\AI\full studio\output\k4-10-videos-261123"
CHAR_DRIVE = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"
PREV_SETS = r"d:\AI\full studio\output\k4-5-videos-261122\sets"

CAST_FACE_DIR = os.path.join(BASE_DIR, "cast_clean")
CAST_BODY_DIR = os.path.join(BASE_DIR, "cast_fullbody")
NEW_SHEETS_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR = os.path.join(BASE_DIR, "sets")

for d in (CAST_FACE_DIR, CAST_BODY_DIR, NEW_SHEETS_DIR, SETS_DIR):
    os.makedirs(d, exist_ok=True)

def split_k4_sheet_exact(src_path, face_dst, body_dst, special_mode=None):
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    if special_mode == "uyen_5panel":
        # Top-left portrait box (x: 4%..42%, y: 12%..62%) and center full-body front (x: 42%..56%, y: 12%..92%)
        face = im.crop((int(w * 0.02), int(h * 0.11), int(w * 0.42), int(h * 0.62)))
        body = im.crop((int(w * 0.43), int(h * 0.12), int(w * 0.56), int(h * 0.92)))
    elif w >= h * 0.85:
        px = im.load()
        best_x = int(w * 0.50)
        best_score = -1
        for x in range(int(w * 0.42), int(w * 0.66)):
            white_cnt = sum(
                1 for y in range(int(h * 0.05), int(h * 0.95), 6)
                if px[x, y][0] > 235 and px[x, y][1] > 235 and px[x, y][2] > 235
            )
            if white_cnt > best_score:
                best_score = white_cnt
                best_x = x
        # Expand past the full width of the white bar
        left_end = best_x - 4
        while left_end > int(w * 0.38):
            wc = sum(1 for y in range(int(h * 0.1), int(h * 0.9), 12) if px[left_end, y][0] > 235 and px[left_end, y][1] > 235 and px[left_end, y][2] > 235)
            if wc < (h * 0.8 / 12) * 0.65:
                break
            left_end -= 1
        right_start = best_x + 4
        while right_start < int(w * 0.70):
            wc = sum(1 for y in range(int(h * 0.1), int(h * 0.9), 12) if px[right_start, y][0] > 235 and px[right_start, y][1] > 235 and px[right_start, y][2] > 235)
            if wc < (h * 0.8 / 12) * 0.65:
                break
            right_start += 1
        face = im.crop((0, 0, left_end, h))
        body = im.crop((right_start, 0, w, h))
    else:
        face = im
        body = im
    face.save(face_dst, "JPEG", quality=95)
    body.save(body_dst, "JPEG", quality=95)

# Extract existing K4 characters needed across the 10 episodes + face refs for outfit variants
EXISTING_K4 = [
    ("bahien",   "G02_01 - Bà Hiền (Mẹ ruột Ngân, Thảo, Mai - Thông gia bà Hạnh).png", None),
    ("tuan_vest","G01_04c - Tuấn (Chồng Thảo - Anh trai Linh - Con trưởng ông Tấn) [Vest đen].png", None),
    ("tuan_somi","G01_04b - Tuấn (Chồng Thảo - Anh trai Linh - Con trưởng ông Tấn) [Sơ mi trắng].png", None),
    ("tuan_polo","G01_04a - Tuấn (Chồng Thảo - Anh trai Linh - Con trưởng ông Tấn) [Polo nâu].png", None),
    ("thao",     "G01_05a - Thảo (Vợ Tuấn - Con dâu bà Hạnh - Chị ruột Mai) [Váy trắng].png", None),
    ("mai",      "G02_03 - Mai (Em gái út ruột Thảo & Ngân - Em vợ Tuấn).png", None),
    ("ngan",     "G02_02a - Ngân (Chị gái ruột Thảo & Mai - Chị vợ Tuấn) [Công sở].png", None),
    ("linh",     "G01_08 - Linh (Em gái ruột Tuấn - Em chồng Thảo - Vợ Thành).png", None),
    ("thanh",    "G01_09 - Thành (Chồng Linh - Em rể Tuấn - Con rể ông Tấn).png", None),
    ("khoi",     "G05_06 - Khôi (Con trai út bà Mận - Em ruột Hiếu & Quỳnh - Chồng Mỹ).png", None),
    ("my",       "G05_07 - Mỹ (Vợ Khôi - Con dâu út bà Mận - Em dâu Hiếu).png", None),
    ("tien",     "G06_02a - Tiến (Con trai bác Thắm - Anh họ ngoại Thảo - Chồng Khánh Ly).png", None),
    ("bactham",  "G06_01 - Bác Thắm (Chị gái bà Hiền - Bác ruột Thảo - Mẹ ruột Tiến).png", None),
    ("khanhly",  "G06_03 - Khánh Ly (Vợ Tiến - Con dâu bác Thắm - Chị dâu họ Thảo).png", None),
    ("son",      "G03_07 - Sơn (Con trai lớn riêng ông Khải - Anh ruột An).png", None),
    ("an",       "G03_08 - An (Con gái út riêng ông Khải - Em gái ruột Sơn).png", None),
    ("khai",     "G03_06 - Ông Khải (Chồng sau cô Lan - Dượng chú của Tuấn - Bố ruột Sơn & An).png", None),
    ("colan",    "G03_01 - Cô Lan (Em gái ruột ông Tấn - Cô ruột Tuấn - Mẹ ruột Tú & Hà).png", None),
    ("tu",       "G03_02 - Tú (Con trai cô Lan - Em họ nội Tuấn - Anh ruột Hà - Chồng Lam).png", None),
    ("lam",      "G03_03 - Lam (Vợ Tú - Con dâu cô Lan - Em dâu họ Tuấn).png", None),
    ("uyen",     "G04_03 - Uyên (Chị họ bên nội Tuấn - Con gái bác Nga - Mẹ ruột bé Na).png", "uyen_5panel"),
    ("quan",     "G04_05 - Quân (Con trai bác Nga - Anh ruột Uyên - Anh họ nội Tuấn) [Áo dài cưới đen].png", None),
    ("quynh",    "G05_04 - Quỳnh (Con gái bà Mận - Em gái ruột Hiếu - Em chồng Trang - Em họ Tuấn).png", None),
    ("nhung",    "G05_05a - Nhung (Chị gái ruột Trang - Chị vợ Hiếu) [Cận mặt].jpg", None),
]

for key, fn, smode in EXISTING_K4:
    sp = os.path.join(CHAR_DRIVE, fn)
    assert os.path.exists(sp), f"Missing K4 character: {sp}"
    split_k4_sheet_exact(
        sp,
        os.path.join(CAST_FACE_DIR, f"k4_{key}.jpg"),
        os.path.join(CAST_BODY_DIR, f"k4_{key}_full.jpg"),
        special_mode=smode,
    )

# Copy wall combo refs from previous batch
for cname in ("_combo_pk_sang.jpg", "_combo_pk_nau.jpg", "_combo_sanh_nau.jpg", "_combo_sanh_sang.jpg"):
    shutil.copy2(os.path.join(PREV_SETS, cname), os.path.join(SETS_DIR, cname))

def fref(key):
    return [{"path": os.path.join(CAST_FACE_DIR, f"k4_{key}.jpg"), "name": f"ref_{key}.jpg"}]

def wref(cname):
    return [{"path": os.path.join(SETS_DIR, cname), "name": "wall_decor_ref.jpg"}]

SPLIT_PROMPT_TPL = (
    "Character reference sheet split into two side-by-side panels separated by a clean thin white vertical line "
    "(left panel: close-up portrait from chest up looking slightly toward camera; "
    "right panel: full-body standing shot head-to-toe in a realistic neutral Vietnamese home or street setting). "
    "{desc} "
    "Photorealistic live-action Vietnamese TV family drama actor, natural skin pores, warm cinematic lighting, 8k, no text, no watermarks."
)

CHAR_JOBS = [
    {
        "id": "CHAR_G06_04_OngPhuc",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G06_04 - Ông Phúc (Bố quê nghèo vác bao tải dứa của Tiến).png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: Vietnamese elderly countryside father, 64 years old, weathered kind face with greying short hair and gentle tired eyes, wearing a faded worn olive-brown cotton button-up work shirt over a grey undershirt, old dark trousers, worn sandals, holding a folded beige woven burlap sack over one shoulder."
        ),
    },
    {
        "id": "CHAR_G06_03b_KhanhLy_TapDe",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G06_03b - Khánh Ly (Vợ Tiến - Con dâu bác Thắm) [Áo hoa đeo tạp dề].png"),
        "ratio": "1:1",
        "refs": fref("khanhly"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same Vietnamese young woman's face, gentle eyes, and soft hairstyle from the attached reference portrait. Outfit: modest brick-red small floral short-sleeve button shirt with a neat brown-and-cream plaid kitchen apron tied over dark trousers and simple flats, no baby, empty hands relaxed at her sides."
        ),
    },
    {
        "id": "CHAR_G06_03c_KhanhLy_VestVang",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G06_03c - Khánh Ly (Vợ Tiến - Con dâu bác Thắm) [Bộ vest vàng quý phái].png"),
        "ratio": "1:1",
        "refs": fref("khanhly"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same Vietnamese young woman's face from the attached reference portrait, now styled with elegant light makeup, pearl earrings, and silky sleek hair. Outfit: a luxurious tailored warm mustard-gold blazer and matching wide-leg tailored trousers over a crisp ivory silk blouse, beige pointed heels, looking radiant and dignified."
        ),
    },
    {
        "id": "CHAR_G03_07b_Son_CongTruong",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G03_07b - Sơn (Con trai lớn riêng ông Khải) [Áo phản quang công trường].png"),
        "ratio": "1:1",
        "refs": fref("son"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same earnest young Vietnamese man's face and short black hair from the attached reference portrait, with slight honest sweat on his forehead. Outfit: dark plaid long-sleeve work shirt with sleeves rolled to forearms, bright orange reflective construction safety vest with silver reflective strips, dusty dark navy work pants, sturdy work boots."
        ),
    },
    {
        "id": "CHAR_G01_09b_Thanh_Shipper",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G01_09b - Thành (Chồng Linh - Em rể Tuấn) [Đồng phục Shipper cam].png"),
        "ratio": "1:1",
        "refs": fref("thanh"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same handsome Vietnamese man's face from the attached reference portrait. Outfit: bright orange delivery rider windbreaker jacket with subtle grey reflective trim over a dark green polo shirt, dark jeans, sneakers, wearing an orange open-face motorbike helmet with visor raised."
        ),
    },
    {
        "id": "CHAR_G07_03_OngBach_GiamDoc",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G07_03 - Ông Bách (Giám đốc chi nhánh nóng nảy sơ mi đen).png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: Vietnamese stocky middle-aged male corporate branch manager, 40 years old, spiky undercut black hair, stern imposing eyebrows, wearing a short-sleeve charcoal-black collared button shirt, a thick gold chain necklace, dark jeans with leather belt, gold wristwatch, leather shoes."
        ),
    },
    {
        "id": "CHAR_G04_05b_Quan_AoTrang",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G04_05b - Quân (Con trai bác Nga - Anh họ Tuấn) [Áo dài tay trắng giản dị].png"),
        "ratio": "1:1",
        "refs": fref("quan"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same handsome young Vietnamese man's face and neat black hair from the attached reference portrait. Outfit: clean minimalist crew-neck white long-sleeve cotton sweater, tailored dark charcoal slacks, minimalist black leather sneakers, looking calm, observant, and warm."
        ),
    },
    {
        "id": "CHAR_G03_08b_An_CongSo",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G03_08b - An (Con gái út ông Khải) [Vest công sở xanh than].png"),
        "ratio": "1:1",
        "refs": fref("an"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same gentle young Vietnamese woman's face and soft bangs from the attached reference portrait. Outfit: neat navy-blue office blazer over a white collared blouse, matching navy office trousers, low black heels, carrying a modest structured brown leather handbag."
        ),
    },
    {
        "id": "CHAR_G04_03b_Uyen_SoDo",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G04_03b - Uyên (Chị họ nội Tuấn) [Sơ mi kem cầm sổ đỏ].png"),
        "ratio": "1:1",
        "refs": fref("uyen"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same Vietnamese woman's face from the attached reference portrait, hair tied in a neat low ponytail with an emotional grateful expression. Outfit: modest cream long-sleeve button blouse and black tailored trousers, holding a crimson-red Vietnamese land-title certificate folder (red A4 hardcover booklet) against her chest."
        ),
    },
    {
        "id": "CHAR_G03_01b_CoLan_GianDi",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G03_01b - Cô Lan (Cô ruột Tuấn) [Áo sơ mi kem giản dị].png"),
        "ratio": "1:1",
        "refs": fref("colan"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same dignified 52-year-old Vietnamese woman's face from the attached reference portrait, hair neatly tied back in a low bun without flashy jewelry. Outfit: plain modest off-white cotton button-up blouse, simple black straight trousers, modest black flat shoes, calm dignified posture."
        ),
    },
    {
        "id": "CHAR_G03_02b_Tu_ChuRe",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G03_02b - Tú (Con trai cô Lan - Chồng Lam) [Vest chú rể đen].png"),
        "ratio": "1:1",
        "refs": fref("tu"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same young Vietnamese man's face from the attached reference portrait. Outfit: formal black three-piece groom wedding tuxedo suit with crisp white shirt, black necktie, a small white rose boutonniere pinned on the left lapel, polished black dress shoes."
        ),
    },
    {
        "id": "CHAR_G03_03b_Lam_CoDau",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G03_03b - Lam (Vợ Tú - Con dâu cô Lan) [Váy cưới trắng].png"),
        "ratio": "1:1",
        "refs": fref("lam"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same pretty young Vietnamese woman's face from the attached reference portrait, bridal updo with a delicate white tulle veil at the back. Outfit: elegant white floral-lace off-shoulder A-line wedding gown, pearl stud earrings, white bridal heels."
        ),
    },
    {
        "id": "CHAR_G01_08b_Linh_BlazerHoa",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G01_08b - Linh (Em gái ruột Tuấn) [Bộ vest họa tiết đi tiệc].png"),
        "ratio": "1:1",
        "refs": fref("linh"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same stylish young Vietnamese woman's face from the attached reference portrait with wavy chestnut-brown hair. Outfit: fashionable colorful baroque-print tailored blazer and matching trousers over a black camisole, holding a small designer handbag, high heels."
        ),
    },
    {
        "id": "CHAR_G05_07b_My_TocHong",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G05_07b - Mỹ (Vợ Khôi) [Tóc hồng đầm hoa xem mắt].png"),
        "ratio": "1:1",
        "refs": fref("my"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep the exact same sharp-featured young Vietnamese woman's face from the attached reference portrait, styled with shoulder-length pastel-pink straight hair. Outfit: flashy floral-print mini shirt-dress, hot-pink stiletto heels, carrying a structured tan leather handbag, haughty expression."
        ),
    },
    {
        "id": "CHAR_G05_05d_Nhung_AoLongXanh",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G05_05d - Nhung (Chị gái Trang) [Áo lông xanh đầm đỏ].png"),
        "ratio": "1:1",
        "refs": fref("nhung"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same glamorous Vietnamese woman's face from the attached reference portrait with chic wavy shoulder-length hair and pearl earrings. Outfit: plush sky-blue faux-fur short jacket draped/worn over a fitted crimson-red cocktail knee-length dress, emerald-green structured handbag, beige heels."
        ),
    },
]

SET_JOBS = [
    # EP01
    {
        "id": "E01_BO1_CongBietThuSang",
        "outPath": os.path.join(SETS_DIR, "E01_BO1_CongBietThuSang.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide establishing architectural shot of the front iron gate and tree-lined driveway of an upscale modern Vietnamese city townhouse/villa in bright morning daylight, clean sidewalk, lush green bougainvillea, empty foreground ready for actors, 8k live-action film set, no people, no text.",
    },
    {
        "id": "E01_BO2_PhongKhachTuanThao",
        "outPath": os.path.join(SETS_DIR, "E01_BO2_PhongKhachTuanThao.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide interior shot of a warm modern Vietnamese family living room in daylight. Incorporate subtle decorative feature wall panels inspired by the attached reference (cream marble-vein charcoal slab framed by warm fluted wood slats) behind a soft beige sofa and wooden tea table. Spacious floor for actors, 8k TV drama set, no people, no text.",
    },
    {
        "id": "E01_BO3_BenXeKhachDongNguoi",
        "outPath": os.path.join(SETS_DIR, "E01_BO3_BenXeKhachDongNguoi.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of a bustling Vietnamese intercity bus station waiting hall in daytime. Rows of metal waiting benches, blurred background passengers carrying bags, intercity sleeper buses parked outside large glass bays, clear open foreground floor space for main actors, authentic Vietnamese cinema realism, 8k, no readable text.",
    },
    # EP02
    {
        "id": "E02_BO1_CuaCanHoLinh",
        "outPath": os.path.join(SETS_DIR, "E02_BO1_CuaCanHoLinh.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot looking inside the bright entryway foyer and living room of a chic modern Vietnamese high-rise apartment, sleek wooden entrance door open on the right, subtle fluted wood slat and marble accent wall in background, bright daylight balcony, empty foreground, 8k, no people, no text.",
    },
    {
        "id": "E02_BO2_PhoThuongMaiDongNguoi",
        "outPath": os.path.join(SETS_DIR, "E02_BO2_PhoThuongMaiDongNguoi.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of a busy modern Vietnamese urban shopping street and mall sidewalk before Tet, blurred pedestrians walking with shopping bags in the background, green street trees, wide clean stone pavement in foreground for main actors, natural overcast daylight, 8k, no readable signs.",
    },
    {
        "id": "E02_BO3_NhaCap4TienLy",
        "outPath": os.path.join(SETS_DIR, "E02_BO3_NhaCap4TienLy.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide interior shot of a humble, warm nostalgic Vietnamese countryside/suburban level-4 family house. Aged pale-yellow plaster walls (NO marble or luxury panels), vintage wooden double front door open to daylight on the left, simple wooden chairs and a small table with white lace cloth and ceramic teapot, warm homely atmosphere, no people, no text.",
    },
    # EP03
    {
        "id": "E03_BO1_PhongTroVoChongTre",
        "outPath": os.path.join(SETS_DIR, "E03_BO1_PhongTroVoChongTre.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of a modest, slightly weathered Vietnamese young couple's rented apartment room, plain off-white painted wall with slight age marks (NO luxury marble), simple wooden desk, small wardrobe, natural morning window light, realistic lived-in feel, empty center floor, no people, no text.",
    },
    {
        "id": "E03_BO2_ViaHePhoDongXe",
        "outPath": os.path.join(SETS_DIR, "E03_BO2_ViaHePhoDongXe.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of an everyday Vietnamese city street sidewalk in morning daylight, a parked commuter motorbike at the curb, blurred passing traffic and townhouses in the background, open sidewalk foreground for actors, realistic live-action look, 8k, no text.",
    },
    {
        "id": "E03_BO3_CongTruongMayXuc",
        "outPath": os.path.join(SETS_DIR, "E03_BO3_CongTruongMayXuc.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of an active outdoor Vietnamese civil construction site under bright warm sunlight, piles of golden sand and bricks, two yellow heavy excavators and distant construction workers blurred in the background, clear sandy foreground for main actors, cinematic depth, 8k, no text.",
    },
    # EP04
    {
        "id": "E04_BO1_PhongGiamDocBach",
        "outPath": os.path.join(SETS_DIR, "E04_BO1_PhongGiamDocBach.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_nau.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide interior shot of an upscale Vietnamese corporate branch director's office, dark executive wooden desk in foreground-left, decorative marble-vein slab and warm dark fluted wood slat feature wall with display shelves behind the desk, daylight window blinds, no people, no text.",
    },
    {
        "id": "E04_BO2_VanPhongMoDongNhanVien",
        "outPath": os.path.join(SETS_DIR, "E04_BO2_VanPhongMoDongNhanVien.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of a bright modern Vietnamese open-plan corporate office, neat white desks with computer monitors and green plants, several blurred office employees working quietly in the background, subtle wood-slat accent wall, clear foreground workstation aisle, 8k, no text.",
    },
    {
        "id": "E04_BO3_SanhTapDoanSangTrong",
        "outPath": os.path.join(SETS_DIR, "E04_BO3_SanhTapDoanSangTrong.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of a bright luxury Vietnamese corporate headquarters ground-floor lobby, polished cream marble floor, tall columns clad in marble-vein panels and warm fluted wood slats, glass facade with greenery outside, a few blurred staff walking far behind, 8k, no text.",
    },
    # EP05
    {
        "id": "E05_BO1_CanHoBanCongKinh",
        "outPath": os.path.join(SETS_DIR, "E05_BO1_CanHoBanCongKinh.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of a bright contemporary Vietnamese high-rise apartment living room, large sliding glass balcony doors showing city skyline in center-back, cream fabric sofa on left, decorative marble-vein and fluted wood slat feature wall on right, warm wood floor, no people, no text.",
    },
    {
        "id": "E05_BO2_HanhLangThangMay",
        "outPath": os.path.join(SETS_DIR, "E05_BO2_HanhLangThangMay.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_nau.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of an upscale Vietnamese apartment elevator lobby corridor, warm recessed ceiling lights, brushed bronze elevator doors, decorative marble and fluted wood wall paneling, clean tile floor, no people, no text.",
    },
    # EP06
    {
        "id": "E06_BO1_SanhTiecCuoiDongKhach",
        "outPath": os.path.join(SETS_DIR, "E06_BO1_SanhTiecCuoiDongKhach.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of a grand luxury Vietnamese hotel wedding banquet hall. Sparkling crystal chandeliers overhead, cream marble columns with subtle fluted gold-wood trim, white-tablecloth round banquet tables set with porcelain bowls and wine glasses, blurred well-dressed wedding guests seated at background tables, open aisle in foreground, 8k, no text.",
    },
    {
        "id": "E06_BO2_BacThemHoaLeDuong",
        "outPath": os.path.join(SETS_DIR, "E06_BO2_BacThemHoaLeDuong.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of wide cream marble steps leading up to a white floral wedding arch inside a luxury Vietnamese banquet hall, crystal chandelier and warm marble-and-wood walls glowing softly behind, empty marble steps in foreground, 8k, no people, no text.",
    },
    # EP07
    {
        "id": "E07_BO1_PhongKhachDemKhuya",
        "outPath": os.path.join(SETS_DIR, "E07_BO1_PhongKhachDemKhuya.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_nau.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of a moody modern Vietnamese apartment living room late at night, lit only by warm standing floor lamps and soft cove lighting. Cream sofa on the right, dark charcoal marble-vein and warm fluted wood slat accent wall behind, entrance hallway visible on the left, intimate nocturnal cinema atmosphere, no people, no text.",
    },
    {
        "id": "E07_BO2_GocBanAnDem",
        "outPath": os.path.join(SETS_DIR, "E07_BO2_GocBanAnDem.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_nau.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide reverse-angle shot of the same modern Vietnamese apartment at night, showing the dining area, subtle fluted wood wall, and large glass window with bokeh city night lights outside, warm dim lamp light, no people, no text.",
    },
    # EP08
    {
        "id": "E08_BO1_ViaHeSapOiBanNgay",
        "outPath": os.path.join(SETS_DIR, "E08_BO1_ViaHeSapOiBanNgay.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of a shaded Vietnamese neighborhood sidewalk beside a white-painted iron fence and green trees in daytime. On the patterned pavement sit a black plastic crate overflowing with fresh green guavas, a folding camp chair, and nearby a red plastic crate of green winter squash, a few blurred pedestrians far down the street, 8k, no people in foreground, no text.",
    },
    {
        "id": "E08_BO2_ViaHeSapOiHoangHon",
        "outPath": os.path.join(SETS_DIR, "E08_BO2_ViaHeSapOiHoangHon.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of the exact same Vietnamese neighborhood sidewalk beside a white iron fence and green trees, now bathed in warm golden late-afternoon sunset light, an empty black plastic fruit crate and folding chair on the pavement, nostalgic heartwarming cinema lighting, 8k, no people, no text.",
    },
    # EP09
    {
        "id": "E09_BO1_BaiDoXeMercedesDongNguoi",
        "outPath": os.path.join(SETS_DIR, "E09_BO1_BaiDoXeMercedesDongNguoi.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of an upscale open-air Vietnamese urban plaza parking lot in bright daylight. A sleek glossy black luxury executive sedan parked prominently near the foreground-right, several white and silver SUVs parked in background bays, trees, modern buildings, and a few blurred passersby in the distance, wide clean asphalt space in foreground, 8k, no readable license plates or text.",
    },
    # EP10
    {
        "id": "E10_BO1_NhaHangSangTrongDongKhach",
        "outPath": os.path.join(SETS_DIR, "E10_BO1_NhaHangSangTrongDongKhach.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_nau.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of an upscale contemporary Vietnamese fine-dining restaurant interior in daytime. Warm globe chandeliers, columns clad in dark-veined marble and warm fluted wood slats, wine display cabinets, several blurred diners seated quietly at background tables, gleaming cream tile aisle in foreground for main actors, 8k, no text.",
    },
    {
        "id": "E10_BO2_LoiRaPhongVipNhaHang",
        "outPath": os.path.join(SETS_DIR, "E10_BO2_LoiRaPhongVipNhaHang.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot looking toward the VIP lounge doorway of the same upscale Vietnamese fine-dining restaurant, framed by cream marble-vein panels, warm fluted wood slats, and golden chandelier glow, gleaming floor leading into the main dining room, 8k, no people, no text.",
    },
]

all_jobs = CHAR_JOBS + SET_JOBS
spec_path = os.path.join(BASE_DIR, "chatgpt_10_episodes_assets.json")
with open(spec_path, "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, ensure_ascii=False, indent=2)

print(f"Prepared {len(CHAR_JOBS)} Character Sheets + {len(SET_JOBS)} Sets = {len(all_jobs)} total ChatGPT jobs -> {spec_path}")
