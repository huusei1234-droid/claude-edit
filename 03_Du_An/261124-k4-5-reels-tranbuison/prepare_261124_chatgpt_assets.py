"""
Prepare all 27 ChatGPT Asset Jobs for the 5-Reel K4 Batch (`261124`):
- Strictly obeys K4 Character Genealogy (`1 character = 1 canonical relationship`, `0%` duplicate fathers, exact age fit!).
- Creates 16 brand-new / outfit-specific 2-panel K4 Character Sheets + 1 replacement for `G03_06 - Ông Khải` (fixing the old Ông Tấn face duplicate in `CHARACTER/`).
- Creates 10 Bespoke `9:16` Location & Crowd Sets (subtle marble/fluted-wood walls ONLY in modern apartments/halls; 0% in humble backrooms!).
"""
import json, os, shutil
from PIL import Image

BASE_DIR = r"d:\AI\full studio\output\k4-5-reels-261124"
CHAR_DRIVE = r"Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"
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
    if special_mode == "5panel":
        # Cleanly crop inside the top-left portrait box (avoiding blue header & footer text banners!)
        face = im.crop((int(w * 0.02), int(h * 0.115), int(w * 0.48), int(h * 0.61)))
        body = im.crop((int(w * 0.505), int(h * 0.12), int(w * 0.655), int(h * 0.92)))
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

# Extract existing canonical K4 characters used directly or as face refs for outfit sheets
EXISTING_K4 = [
    ("cucuc_raw", "G04_01 - Cụ Cúc (Chị gái cụ Tâm - Bà nội họ của Uyên & Tuấn).png", "5panel"),
    ("quan_raw",  "G04_05b - Quân (Con trai bác Nga - Anh họ Tuấn) [Áo dài tay trắng giản dị].png", None),
    ("bahanh",    "G01_03c - Bà Hạnh (Mẹ ruột Tuấn & Linh - Mẹ chồng Thảo) [Nhung đỏ].png", None),
    ("tuan_vest", "G01_04c - Tuấn (Chồng Thảo - Anh trai Linh - Con trưởng ông Tấn) [Vest đen].png", None),
    ("thao",      "G01_05a - Thảo (Vợ Tuấn - Con dâu bà Hạnh - Chị ruột Mai) [Váy trắng].png", None),
    ("linh",      "G01_08 - Linh (Em gái ruột Tuấn - Em chồng Thảo - Vợ Thành).png", None),
    ("baman",     "G05_01 - Bà Mận (Chị gái bà Hạnh - Bác ruột Tuấn - Mẹ ruột Hiếu & Quỳnh).png", None),
    ("hieu_raw",  "G05_02 - Hiếu (Con trai bà Mận - Anh họ ngoại Tuấn - Anh ruột Quỳnh - Chồng Trang).png", None),
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

# Copy wall decor reference images if available
for cname in ("_combo_pk_sang.jpg", "_combo_pk_nau.jpg", "_combo_sanh_nau.jpg", "_combo_sanh_sang.jpg"):
    sp = os.path.join(PREV_SETS, cname)
    if os.path.exists(sp):
        shutil.copy2(sp, os.path.join(SETS_DIR, cname))

def fref(key):
    return [{"path": os.path.join(CAST_FACE_DIR, f"k4_{key}.jpg"), "name": f"ref_{key}.jpg"}]

def wref(cname):
    p = os.path.join(SETS_DIR, cname)
    return [{"path": p, "name": "wall_decor_ref.jpg"}] if os.path.exists(p) else []

SPLIT_PROMPT_TPL = (
    "Character reference sheet split into two side-by-side panels separated by a clean thin white vertical line "
    "(left panel: close-up portrait from chest up looking slightly toward camera; "
    "right panel: full-body standing shot head-to-toe in a realistic neutral Vietnamese home or street setting). "
    "{desc} "
    "Photorealistic live-action Vietnamese TV family drama actor, natural skin pores, warm cinematic lighting, 8k, ZERO text, ZERO labels, ZERO watermarks."
)

CHAR_JOBS = [
    # --- FILM 1 (G04: Cụ Cúc 75t — Bác Trọng 55t — Quân 27t) ---
    {
        "id": "CHAR_G04_01b_CuCuc_MungTho",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G04_01b - Cụ Cúc (Bà nội Quân & Uyên - Mẹ ruột Bác Trọng) [Áo bà già nâu lễ mừng thọ].png"),
        "ratio": "1:1",
        "refs": fref("cucuc_raw"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same gentle 75-year-old elderly Vietnamese grandmother's face, silver-grey bun hairstyle, and kind wrinkled eyes from the attached portrait. Outfit: humble traditional dark-brown long-sleeve Vietnamese grandma cotton button-up shirt ('áo bà ba nâu') and loose black trousers, simple brown flat slippers, weathered elderly hands."
        ),
    },
    {
        "id": "CHAR_G04_07_BacTrong_55t",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G04_07 - Bác Trọng (Con trai cụ Cúc - Chồng bác Nga - Bố ruột Quân & Uyên) [Vest đen cài hoa đỏ mừng thọ].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: Distinct 55-year-old Vietnamese middle-aged man, broad square jawline, NO glasses, thick salt-and-pepper hair combed neatly backward, prominent stern eyebrows, clean-shaven, proud status-conscious expression. Outfit: formal black business suit jacket, crisp white dress shirt, deep crimson necktie, a small red celebratory boutonniere flower pinned on his left lapel, black leather dress shoes."
        ),
    },
    {
        "id": "CHAR_G04_05c_Quan_SoMiTrang",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G04_05c - Quân (Con trai Bác Trọng - Cháu đích tôn cụ Cúc) [Sơ mi trắng quần âu].png"),
        "ratio": "1:1",
        "refs": fref("quan_raw"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same handsome 27-year-old Vietnamese young man's face and neat black hair from the attached portrait. Outfit: crisp tailored white long-sleeve dress shirt with sleeves neatly rolled just below elbows, dark navy-charcoal dress trousers with black leather belt, wristwatch, dark dress shoes, upright filial expression."
        ),
    },

    # --- FILM 3 (G05 + G07: Bà Mận 63t — Giám đốc Hiếu 31t — Lễ tân Lê 26t — Quản lý Khang 29t) ---
    {
        "id": "CHAR_G05_02b_Hieu_VestGiamDoc",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G05_02b - Hiếu (Con trai trưởng bà Mận - Giám đốc công ty) [Vest đen lễ khánh thành].png"),
        "ratio": "1:1",
        "refs": fref("hieu_raw"),
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Keep 100% the exact same handsome 31-year-old Vietnamese man's face and hairstyle from the attached portrait. Outfit: sharp tailored charcoal-black CEO suit, crisp white dress shirt, dark navy silk necktie, polished black oxford shoes, dignified decisive posture."
        ),
    },
    {
        "id": "CHAR_G07_04_Le_LeTanKieuKy",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G07_04 - Lê (Trưởng lễ tân kiêu kỳ sự kiện công ty Hiếu) [Đầm lụa kem sự kiện].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 26-year-old Vietnamese female corporate event receptionist/coordinator, sharp haughty facial features, sleek low bun hairstyle, pearl drop earrings, polished makeup. Outfit: elegant champagne-ivory satin midi dress suitable for a corporate grand opening ceremony, beige stiletto heels."
        ),
    },
    {
        "id": "CHAR_G07_05_Khang_QuanLySuKien",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G07_05 - Khang (Quản lý sự kiện hách dịch công ty Hiếu) [Vest xanh navy].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 29-year-old Vietnamese male corporate event manager, slim narrow face, slick side-parted black hair, arrogant snobbish expression, NO glasses. Outfit: fitted navy-blue business suit, white collared shirt, diagonal striped blue tie, brown leather dress shoes."
        ),
    },

    # --- FILM 4 (G08 NEW BRANCH: Ông Lộc 63t — Anh Hải 36t — Bác sĩ Khoa 31t — Vợ Châu 28t — Bố vợ Ông Đạt 58t — Mẹ vợ Bà Quý 55t) ---
    {
        "id": "CHAR_G08_01_OngLoc_63t_ThoXay",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G08_01 - Ông Lộc (Bố quê thợ xây vôi ăn sần tay của bác sĩ Khoa & Hải).png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: Distinct 63-year-old Vietnamese rural bricklayer father, lean gaunt sun-weathered face, high cheekbones, very short cropped grey-black hair, clean-shaven (NO mustache, NO glasses), humble gentle eyes with deep wrinkles, visible dry calloused cement-worn hands. Outfit: faded dusty brown-grey button-up cotton work shirt over a worn grey tee, loose dark work pants, old dusty casual shoes."
        ),
    },
    {
        "id": "CHAR_G08_02_Hai_36t_AnhCa",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G08_02 - Hải (Anh trai cả thợ xây hiền lành của bác sĩ Khoa - Con lớn ông Lộc).png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 36-year-old Vietnamese working-class older brother from the countryside, tanned honest weathered skin, sturdy shoulders, short simple black hair, earnest humble expression, NO glasses. Outfit: worn muted olive-and-brown plaid long-sleeve work shirt with sleeves rolled to forearms, simple khaki work trousers, scuffed dark work shoes."
        ),
    },
    {
        "id": "CHAR_G08_03_Khoa_31t_TruongKhoa",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G08_03 - Khoa (Bác sĩ Trưởng khoa hiếu thảo - Con trai thứ ông Lộc - Chồng Châu) [Áo blouse trắng bác sĩ].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 31-year-old handsome upright Vietnamese male hospital Department Head doctor, sharp intelligent eyes, neat side-parted black hair, NO glasses, dignified composed expression. Outfit: crisp white knee-length doctor's coat worn open over a white dress shirt and dark navy necktie, charcoal tailored trousers, black leather shoes."
        ),
    },
    {
        "id": "CHAR_G08_04_Chau_28t_VoSiDien",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G08_04 - Châu (Vợ sĩ diện của bác sĩ Khoa - Con gái ông Đạt & bà Quý) [Đầm dạ tiệc đỏ rượu].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 28-year-old wealthy status-obsessed Vietnamese city woman, glamorous wavy dark-chestnut shoulder-length hair, proud judgmental expression, sparkling silver crystal necklace and matching earrings. Outfit: fitted off-shoulder deep burgundy-wine cocktail evening dress, silver heels."
        ),
    },
    {
        "id": "CHAR_G08_05_OngDat_58t_BoVoGiau",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G08_05 - Ông Đạt (Bố vợ giàu hách dịch của bác sĩ Khoa - Bố ruột Châu) [Vest kẻ xám ghi lê].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: Distinct 58-year-old wealthy arrogant Vietnamese city father-in-law, fuller rounder face, high forehead with sleek side-swept silver-streaked hair, thick arched eyebrows, NO glasses, clean-shaven, condescending expression. Outfit: medium-grey subtle windowpane-check three-piece suit with buttoned waistcoat over an open-collar white dress shirt (no tie), dark dress shoes."
        ),
    },
    {
        "id": "CHAR_G08_06_BaQuy_55t_MeVoChuaNgoa",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G08_06 - Bà Quý (Mẹ vợ chua ngoa của bác sĩ Khoa - Vợ ông Đạt - Mẹ ruột Châu) [Áo dài nhung xanh đen].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 55-year-old wealthy sharp-tongued Vietnamese city mother-in-law, elegant high bouffant updo hairstyle, stern haughty gaze, wearing a gold chain necklace with a round green jade pendant and pearl earrings. Outfit: luxurious midnight-navy velvet traditional Vietnamese mandarin-collar tunic ('áo dài nhung') with dark silk trousers, low dress heels."
        ),
    },

    # --- FILM 5 (G09 NEW BRANCH: Ông Bình 62t — Anh Đức 34t — Con gái Ngọc 28t — Con rể Minh 31t) ---
    {
        "id": "CHAR_G09_01_OngBinh_62t_BoVoTrungGa",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G09_01 - Ông Bình (Bố quê mang giỏ trứng gà thương con - Bố ruột Đức & Ngọc).png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: Distinct 62-year-old kind-hearted Vietnamese countryside father, warm round weathered face, soft greying hair parted naturally on the side, compassionate gentle eyes, NO glasses, clean-shaven. Outfit: humble earth-brown long-sleeve cotton shirt with a neat darker cloth patch on the sleeve, dark loose trousers, simple brown sandals, holding a small woven bamboo basket with handle."
        ),
    },
    {
        "id": "CHAR_G09_02_Duc_34t_ConTraiIchKy",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G09_02 - Đức (Con trai trưởng ích kỷ nhà giàu của ông Bình - Anh ruột Ngọc).png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 34-year-old affluent urban Vietnamese man, neat modern short fade haircut, slightly aloof impatient expression, NO glasses. Outfit: smart dark charcoal-navy collared polo shirt, silver metal wristwatch, beige-grey tailored chinos, loafers."
        ),
    },
    {
        "id": "CHAR_G09_03_Ngoc_28t_ConGaiHieuThao",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G09_03 - Ngọc (Con gái hiếu thảo của ông Bình - Vợ Minh) [Áo sơ mi kẻ caro ở nhà].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 28-year-old gentle natural Vietnamese young wife, hair tied back neatly in a simple low bun with soft wisps, natural light makeup, warm expressive emotional eyes. Outfit: modest maroon-and-navy plaid long-sleeve cotton home button-up shirt with sleeves rolled slightly, dark comfortable home trousers, indoor slippers."
        ),
    },
    {
        "id": "CHAR_G09_04_Minh_31t_ConReTotBung",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G09_04 - Minh (Con rể tốt bụng trầm tính của ông Bình - Chồng Ngọc) [Sơ mi trắng công sở].png"),
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: 31-year-old sincere hardworking Vietnamese office-worker husband, warm honest eyes, neat natural black hair, calm thoughtful expression, NO glasses. Outfit: plain white long-sleeve button-up dress shirt tucked into black dress trousers with a simple black leather belt, dark shoes."
        ),
    },

    # --- BONUS FIX FOR CHARACTER/ LIBRARY: Distinct G03_06 Ông Khải (replacing the old Ông Tấn clone!) ---
    {
        "id": "CHAR_G03_06_OngKhai_DistinctFix",
        "outPath": os.path.join(NEW_SHEETS_DIR, "G03_06 - Ông Khải (Chồng sau cô Lan - Dượng chú của Tuấn - Bố ruột Sơn & An).png"),
        "overwrite": True,
        "ratio": "1:1",
        "refs": [],
        "prompt": SPLIT_PROMPT_TPL.format(
            desc="Subject: Distinct 56-year-old compassionate dignified Vietnamese businessman, oval face, silver-streaked wavy black hair parted on the left, warm gentle eyes, NO glasses (completely bare eyes without spectacles), neatly trimmed subtle salt-and-pepper mustache. Outfit: refined dark slate-grey business suit, white shirt, patterned charcoal silk tie, black leather shoes."
        ),
    },
]

SET_JOBS = [
    # F01: Lễ mừng thọ 75
    {
        "id": "F01_BO1_BuongTrongCuToi",
        "outPath": os.path.join(SETS_DIR, "F01_BO1_BuongTrongCuToi.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide interior shot of a dim, humble old back storage/bedroom in a Vietnamese house. Aged weathered pale-cream plaster walls (NO marble, NO luxury panels), a vintage wooden door on the left, a simple low dark wooden table with a plain white ceramic porridge bowl and spoon, dim warm single bulb lighting, clear foreground floor for actors, 8k live-action film set, no people, no text.",
    },
    {
        "id": "F01_BO2_SanhTiecMungThoDongKhach",
        "outPath": os.path.join(SETS_DIR, "F01_BO2_SanhTiecMungThoDongKhach.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of a lavish Vietnamese 75th longevity banquet hall and courtyard. Festive crimson-and-gold decorative silk backdrop curtain with traditional floral motifs (NO readable words or letters), warm fluted wood decorative wall pillars on the sides, round banquet tables with white tablecloths and dishes, blurred well-dressed guests seated in background, spacious open center foreground for main actors, 8k, no text.",
    },
    # F02: Xe hồi môn
    {
        "id": "F02_BO1_PhongNguTuDoTuanThao",
        "outPath": os.path.join(SETS_DIR, "F02_BO1_PhongNguTuDoTuanThao.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide interior shot of an upscale modern Vietnamese married couple's bedroom and dressing area. Warm illuminated glass-door wardrobe closet displaying neat dresses and handbags, a chic vanity mirror, and subtle cream marble-vein & warm fluted wood slat decorative wall panels in the background. Bright natural daylight, spacious floor for actors, 8k, no people, no text.",
    },
    {
        "id": "F02_BO2_PhongKhachNhaBaHanh",
        "outPath": os.path.join(SETS_DIR, "F02_BO2_PhongKhachNhaBaHanh.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_nau.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide interior shot of a luxurious modern Vietnamese family apartment living room. Soft cream-beige sofa, round wooden coffee table with a plate of cut apples and pears, subtle decorative feature wall combining warm walnut fluted wood slats and cream marble-vein stone panels behind the sofa, bright daylight window, 8k, no people, no text.",
    },
    # F03: Lễ khánh thành trụ sở mới
    {
        "id": "F03_BO1_ThamDoKhanhThanhDongNguoi",
        "outPath": os.path.join(SETS_DIR, "F03_BO1_ThamDoKhanhThanhDongNguoi.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide outdoor shot of a grand corporate headquarters opening ceremony in Vietnam. A long vibrant crimson red carpet stretches straight through the center toward a modern glass office tower decorated with celebratory floral stands and red ribbons, with blurred business guests and office staff in suits standing along both sides of the red carpet, wide open red-carpet foreground for main actors, natural daylight, 8k, no readable text.",
    },
    {
        "id": "F03_BO2_BacThemLeDaiKhanhThanh",
        "outPath": os.path.join(SETS_DIR, "F03_BO2_BacThemLeDaiKhanhThanh.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of wide red-carpeted grand entrance steps leading up to a festive corporate inauguration stage in front of a modern Vietnamese office building, colorful congratulatory flower baskets and blurred applauding guests lining both sides, open center red carpet for actors, daylight, 8k, no readable text.",
    },
    # F04: Tiệc thăng chức Trưởng khoa
    {
        "id": "F04_BO1_SanhTiecMungTruongKhoaDongKhach",
        "outPath": os.path.join(SETS_DIR, "F04_BO1_SanhTiecMungTruongKhoaDongKhach.png"),
        "ratio": "9:16",
        "refs": wref("_combo_sanh_nau.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide shot of an upscale Vietnamese hotel banquet hall hosting a doctor's promotion celebration dinner. Warm crystal chandeliers overhead, subtle cream marble and fluted wood decorative wall panels along the ballroom walls, blurred guests and colleagues seated at round white-tablecloth banquet tables in the background, clear spacious carpet foreground for main actors, 8k, no readable text.",
    },
    # F05: Bố vợ mang trứng gà lên thăm
    {
        "id": "F05_BO1_PhongKhachNhaDucSangTrong",
        "outPath": os.path.join(SETS_DIR, "F05_BO1_PhongKhachNhaDucSangTrong.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_sang.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide interior shot of a sleek modern affluent Vietnamese city apartment living room, dark leather sofa, subtle grey-vein marble and fluted wood slat decorative feature wall in background, large glass balcony window on an overcast rainy day, spacious floor for actors, 8k, no people, no text.",
    },
    {
        "id": "F05_BO2_CuaCanHoMinhNgoc",
        "outPath": os.path.join(SETS_DIR, "F05_BO2_CuaCanHoMinhNgoc.png"),
        "ratio": "9:16",
        "refs": [],
        "prompt": "Vertical 9:16 photorealistic wide shot of a cozy middle-class Vietnamese apartment entryway foyer and open wooden front door leading from a clean residential corridor, warm soft ceiling light, modest shoe cabinet, warm homely atmosphere, clear floor space for actors, 8k, no people, no text.",
    },
    {
        "id": "F05_BO3_BanAnAmCungMinhNgoc",
        "outPath": os.path.join(SETS_DIR, "F05_BO3_BanAnAmCungMinhNgoc.png"),
        "ratio": "9:16",
        "refs": wref("_combo_pk_nau.jpg"),
        "prompt": "Vertical 9:16 photorealistic wide interior shot of a warm cozy middle-class Vietnamese apartment dining and living room in the evening. A neat wooden dining table set with simple home-cooked dishes, ceramic rice bowls and teapot, soft warm pendant lamp, subtle light-oak fluted wood accent wall in the background, warm lived-in family feel, 8k, no people, no text.",
    },
]

ALL_JOBS = CHAR_JOBS + SET_JOBS
out_json = os.path.join(BASE_DIR, "chatgpt_27_assets.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(ALL_JOBS, f, ensure_ascii=False, indent=2)
print(f"Prepared {len(CHAR_JOBS)} K4 Character Sheets + {len(SET_JOBS)} Location Sets = {len(ALL_JOBS)} ChatGPT jobs -> {out_json}")
