import json, os, shutil
from PIL import Image

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
CAST_DIR = os.path.join(BASE_DIR, "cast_clean")
NEW_CHAR_RAW_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR = os.path.join(BASE_DIR, "sets")
for d in (CAST_DIR, NEW_CHAR_RAW_DIR, SETS_DIR):
    os.makedirs(d, exist_ok=True)

CHAR_DRIVE = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"
MS_KIT = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\02_MS_Noi_That\hinh_anh_website_noithat"

# Convert webp interior wall references to clean jpg on D:\ so ChatGPT upload accepts 100% standard JPEG/PNG
WALL_REFS = {}
for key, fn in [
    ("wall_phongkhach", "05_phong-khach.webp"),
    ("wall_lamsong_sang", "08_lam-lam-4-song-160x22x3000mm.webp"),
    ("wall_sanh", "06_sanh.webp"),
    ("wall_lamsong_nauvang", "20_lam-anh-thuc-te-lam-song-nau-chi-vang.webp"),
]:
    src = os.path.join(MS_KIT, fn)
    dst = os.path.join(SETS_DIR, f"_ref_{key}.jpg")
    Image.open(src).convert("RGB").save(dst, "JPEG", quality=94)
    WALL_REFS[key] = dst

def crop_left_portrait(src_path, dst_path, ratio_w=0.486):
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    # Single portrait (like G05_05a Nhung 941x1672): keep whole portrait!
    if w < h * 0.85:
        im.save(dst_path, "JPEG", quality=96)
    else:
        crop = im.crop((0, 0, int(w * ratio_w), h))
        crop.save(dst_path, "JPEG", quality=96)
    print(f"Prepared clean K4 portrait: {os.path.basename(dst_path)}")

EXISTING_K4 = [
    ("G05_01_BaMan.jpg", "G05_01 - Bà Mận (Chị gái bà Hạnh - Bác ruột Tuấn - Mẹ ruột Hiếu & Quỳnh).png"),
    ("G05_02_Hieu.jpg", "G05_02 - Hiếu (Con trai bà Mận - Anh họ ngoại Tuấn - Anh ruột Quỳnh - Chồng Trang).png"),
    ("G05_03_Trang.jpg", "G05_03 - Trang (Vợ Hiếu - Con dâu bà Mận - Em gái ruột Nhung).png"),
    ("G01_02_OngTan.jpg", "G01_02 - Ông Tấn (Bố ruột Tuấn & Linh - Bố chồng Thảo).jpg"),
    ("G01_05a_Thao.jpg", "G01_05a - Thảo (Vợ Tuấn - Con dâu bà Hạnh - Chị ruột Mai) [Váy trắng].png"),
    ("G01_04b_Tuan.jpg", "G01_04b - Tuấn (Chồng Thảo - Anh trai Linh - Con trưởng ông Tấn) [Sơ mi trắng].png"),
    ("G03_01_CoLan.jpg", "G03_01 - Cô Lan (Em gái ruột ông Tấn - Cô ruột Tuấn - Mẹ ruột Tú & Hà).png"),
    ("G03_02_Tu.jpg", "G03_02 - Tú (Con trai cô Lan - Em họ nội Tuấn - Anh ruột Hà - Chồng Lam).png"),
    ("G03_03_Lam.jpg", "G03_03 - Lam (Vợ Tú - Con dâu cô Lan - Em dâu họ Tuấn).png"),
    ("G05_05a_Nhung.jpg", "G05_05a - Nhung (Chị gái ruột Trang - Chị vợ Hiếu) [Cận mặt].jpg"),
    ("G04_03_Uyen.jpg", "G04_03 - Uyên (Chị họ bên nội Tuấn - Con gái bác Nga - Mẹ ruột bé Na).png"),
]

for dst_fn, src_fn in EXISTING_K4:
    crop_left_portrait(os.path.join(CHAR_DRIVE, src_fn), os.path.join(CAST_DIR, dst_fn))

SPLIT_SHEET_PREFIX = (
    "Photorealistic Vietnamese family drama character reference sheet split cleanly into TWO side-by-side vertical panels separated by a thin white line "
    "(LEFT panel: tight close-up portrait from chest up looking toward camera with natural skin pores and luminous daylight; "
    "RIGHT panel: full-body head-to-toe standing shot in a bright realistic Vietnamese home/courtyard setting). "
    "Pure photorealistic K-drama / Vietnamese cinema lighting, ZERO text, ZERO labels, ZERO watermarks. "
)

SET_STYLE_9X16 = (
    "Vertical 9:16 bright, airy, crystal-clear photorealistic Vietnamese architectural & film-set photography "
    "(Sony A7R5 35mm f/2.0, abundant soft natural daylight, luminous clean colors, open shadows, ZERO heavy dark contrast, ZERO people, ZERO text, ZERO logos, ZERO watermarks): "
)

jobs = [
    # --- 9 NEW K4 CHARACTER SHEETS (Split 2-Panel matching CHARACTER/ standard) ---
    {
        "id": "G05_06_Khoi",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G05_06 - Khôi (Con trai út bà Mận - Em ruột Hiếu & Quỳnh - Chồng Mỹ).png"),
        "refs": [{"path": os.path.join(CAST_DIR, "G05_02_Hieu.jpg"), "name": "anh_trai_hieu.jpg"}],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: Khôi, a 26-year-old Vietnamese younger brother (sharing subtle family facial resemblance to his older brother in the reference image, slightly weaker/evasive expression, neat short black hair), "
            "wearing a casual black zip-up bomber jacket over a burgundy-red crew-neck t-shirt and dark trousers."
        ),
    },
    {
        "id": "G05_07_My",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G05_07 - Mỹ (Vợ Khôi - Con dâu út bà Mận - Em dâu Hiếu).png"),
        "refs": [],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: Mỹ, a 25-year-old sharp-tongued Vietnamese younger sister-in-law with sleek black hair tied in a high ponytail, sharp brows, petty calculating expression, "
            "wearing a fitted black zip-up stand-collar casual jacket and dark pants inside a bright Vietnamese townhouse."
        ),
    },
    {
        "id": "G03_06_OngKhai",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G03_06 - Ông Khải (Chồng sau cô Lan - Dượng chú của Tuấn - Bố ruột Sơn & An).png"),
        "refs": [{"path": os.path.join(CAST_DIR, "G01_02_OngTan.jpg"), "name": "style_ref.jpg"}],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: Ông Khải, a dignified 56-year-old Vietnamese businessman with neatly combed salt-and-pepper hair, kind emotional eyes, warm weathered features, "
            "wearing a charcoal-grey tailored suit jacket over a crisp white dress shirt and dark tie (distinct individual face from the reference, same photorealistic K4 visual style)."
        ),
    },
    {
        "id": "G03_07_Son",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G03_07 - Sơn (Con trai lớn riêng ông Khải - Anh ruột An).png"),
        "refs": [],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: Sơn, a hardworking, upright 22-year-old Vietnamese young man with honest expressive eyes, slightly sun-tanned skin, neat short black hair, "
            "wearing a humble faded grey-olive button-up work shirt with subtle light plaster dust smudges on the shoulders and simple beige khaki work pants."
        ),
    },
    {
        "id": "G03_08_An",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G03_08 - An (Con gái út riêng ông Khải - Em gái ruột Sơn).png"),
        "refs": [],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: An, a gentle, fragile 18-year-old Vietnamese teenage girl with long straight black hair, delicate pale complexion, innocent tearful big eyes, "
            "wearing a modest soft pastel-pink knit crew-neck sweater and simple grey trousers."
        ),
    },
    {
        "id": "G03_05_BaSen",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G03_05 - Bà Sen (Mẹ ruột Lam ở quê - Mẹ vợ Tú - Thông gia cô Lan).png"),
        "refs": [{"path": os.path.join(CAST_DIR, "G03_03_Lam.jpg"), "name": "con_gai_lam.jpg"}],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: Bà Sen, a humble, kind-hearted 58-year-old rural Vietnamese mother (sharing gentle eye and nose resemblance with her daughter in the reference image), greying hair tied neatly in a low bun, weathered compassionate face, "
            "wearing a worn faded indigo-blue patterned knit cardigan with a dark wool scarf wrapped around her neck, brown country trousers, carrying a humble grey cloth travel bundle bag over one shoulder."
        ),
    },
    {
        "id": "G04_05_Quan",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G04_05 - Quân (Con trai bác Nga - Anh ruột Uyên - Anh họ nội Tuấn) [Áo dài cưới đen].png"),
        "refs": [],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: Quân, a handsome, self-respecting 28-year-old affluent Vietnamese groom with sharp masculine features and neat parted black hair, "
            "wearing a luxurious traditional Vietnamese groom black brocade Áo Dài (áo tấc / áo dài cưới nam) finely embroidered with elegant gold floral motifs on the chest and standing collar, paired with tailored black dress trousers."
        ),
    },
    {
        "id": "G04_06_Kieu",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G04_06 - Kiều (Cô dâu đòi 2 tỷ sính lễ của Quân) [Áo dài cưới trắng].png"),
        "refs": [],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: Kiều, a pretty but arrogant, materialistic 24-year-old Vietnamese bride with bridal makeup and haughty expression, "
            "wearing an ornate white silk Vietnamese wedding Áo Dài embroidered with delicate gold patterns, a matching gold-embroidered white circular bridal headdress (mấn cô dâu) with sheer white veil at the back."
        ),
    },
    {
        "id": "G05_05c_NhungPhuDau",
        "ratio": "1:1",
        "outPath": os.path.join(NEW_CHAR_RAW_DIR, "G05_05c - Nhung (Chị gái ruột Trang - Bạn thân phù dâu) [Áo dài ren trắng].png"),
        "refs": [{"path": os.path.join(CAST_DIR, "G05_05a_Nhung.jpg"), "name": "nhung_face.jpg"}],
        "prompt": SPLIT_SHEET_PREFIX + (
            "Subject: keep the exact glamorous young Vietnamese woman face from the reference image (Nhung, sharp elegant features, glossy black hair half-up), "
            "now wearing a chic fitted white floral-lace high-collar Vietnamese bridesmaid Áo Dài (without headdress/veil) and pearl drop earrings, looking sassy and calculating."
        ),
    },

    # --- 6 DECORATIVE-WALL BACKGROUND SETS (0% people, 0% text, subtle interior wall integration) ---
    {
        "id": "V1_BO1_NhaKhoi",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V1_BO1_NhaKhoi.png"),
        "refs": [
            {"path": WALL_REFS["wall_lamsong_sang"], "name": "lam_song_sang.jpg"},
            {"path": WALL_REFS["wall_phongkhach"], "name": "vach_phong_khach.jpg"},
        ],
        "prompt": SET_STYLE_9X16 + (
            "middle-class modern Vietnamese townhouse living-dining room in bright natural daylight; "
            "wooden dining chairs and sofa in mid-ground, and in the background a clean decorative accent wall featuring warm honey-oak vertical fluted wood slat panels paired with a cream marble-vein bamboo charcoal center panel inspired by the reference textures; "
            "completely empty room, ZERO people."
        ),
    },
    {
        "id": "V1_BO2_CanHoHieu",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V1_BO2_CanHoHieu.png"),
        "refs": [
            {"path": WALL_REFS["wall_phongkhach"], "name": "vach_phong_khach.jpg"},
            {"path": WALL_REFS["wall_lamsong_nauvang"], "name": "lam_song_nau_vang.jpg"},
        ],
        "prompt": SET_STYLE_9X16 + (
            "upscale modern Vietnamese city apartment living room in bright warm early-evening recessed cove lighting; "
            "beige fabric sofa and sleek wooden entrance door visible on the right, and behind the living area a luxurious decorative feature wall combining glossy white-and-gold marble-vein panels flanked by warm walnut-and-gold vertical fluted wood slat panels with soft vertical LED glow; "
            "completely empty room, ZERO people."
        ),
    },
    {
        "id": "V2_BO1_PhongKhachOngTan",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V2_BO1_PhongKhachOngTan.png"),
        "refs": [
            {"path": WALL_REFS["wall_phongkhach"], "name": "vach_phong_khach.jpg"},
            {"path": WALL_REFS["wall_lamsong_sang"], "name": "lam_song_sang.jpg"},
        ],
        "prompt": SET_STYLE_9X16 + (
            "sunlit affluent Vietnamese family villa living room with sheer white curtains and lush green garden plants visible outside the left window; "
            "a warm grey sofa and natural oak tea table in the center holding three elegant red-and-gold gift paper bags (health supplement gift bags, NO readable text), "
            "and behind the sofa a tasteful decorative interior wall combining glossy cream-white marble-vein panels framed symmetrically by warm oak vertical fluted wood slat panels; "
            "completely empty room, ZERO people."
        ),
    },
    {
        "id": "V3_BO1_PhongChuTichCoLan",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V3_BO1_PhongChuTichCoLan.png"),
        "refs": [
            {"path": WALL_REFS["wall_sanh"], "name": "vach_sanh.jpg"},
            {"path": WALL_REFS["wall_lamsong_nauvang"], "name": "lam_song_nau_vang.jpg"},
        ],
        "prompt": SET_STYLE_9X16 + (
            "prestigious Vietnamese executive chairwoman office and private reception lounge bathed in soft daylight through wooden venetian blinds; "
            "an executive walnut desk and leather armchair on the right, guest seating area on the left, and a grand decorative feature wall behind them combining rich dark-walnut vertical fluted wood slat panels with a bookmatched warm cream-gold marble-vein centerpiece panel and warm recessed accent strips; "
            "completely empty room, ZERO people."
        ),
    },
    {
        "id": "V4_BO1_CongSanhNhaTu",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V4_BO1_CongSanhNhaTu.png"),
        "refs": [
            {"path": WALL_REFS["wall_sanh"], "name": "vach_sanh.jpg"},
            {"path": WALL_REFS["wall_lamsong_sang"], "name": "lam_song_sang.jpg"},
        ],
        "prompt": SET_STYLE_9X16 + (
            "entrance gate and open sunlit foyer porch of an affluent modern Vietnamese villa in clear morning daylight; "
            "ornate black-and-gold wrought-iron villa gate and cream stone pillars on the left, leading directly into a wide open glass foyer entrance on the right where a bright decorative interior lobby wall of glossy white-gold marble-vein panels and honey-oak vertical fluted wood slats glows warmly inside; "
            "completely empty scene, ZERO people."
        ),
    },
    {
        "id": "V5_BO1_CongCuoiNhaQuan",
        "ratio": "9:16",
        "outPath": os.path.join(SETS_DIR, "V5_BO1_CongCuoiNhaQuan.png"),
        "refs": [
            {"path": WALL_REFS["wall_phongkhach"], "name": "vach_phong_khach.jpg"},
            {"path": WALL_REFS["wall_lamsong_sang"], "name": "lam_song_sang.jpg"},
        ],
        "prompt": SET_STYLE_9X16 + (
            "courtyard driveway right in front of an affluent modern Vietnamese villa decorated tastefully with fresh white-and-blush-pink floral arrangements for a wedding morning (STRICTLY ZERO text banners, ZERO Chinese characters, ZERO words); "
            "in the left foreground stands a sleek white luxury bridal sedan car with a floral hood bouquet and rear passenger door slightly ajar; "
            "in the right background through the wide-open grand villa entrance doors, a bright decorative interior foyer wall of cream-gold marble-vein panels and vertical fluted wood slats is clearly visible; "
            "completely empty scene, ZERO people."
        ),
    },
]

spec_path = os.path.join(BASE_DIR, "chatgpt_assets_batch.json")
with open(spec_path, "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(jobs)} ChatGPT image jobs -> {spec_path}")
