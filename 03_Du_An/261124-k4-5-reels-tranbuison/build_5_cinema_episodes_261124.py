"""
Build All 5 K4 Cinema Episodes (`261124 Tran Bui Son Reels Batch`):
1. Verifies all 27 ChatGPT images (17 K4 2-panel character sheets + 10 `9:16` location/crowd sets).
2. Splits all 17 new K4 character sheets cleanly (`cast_clean/` + `cast_fullbody/`).
3. Syncs all 17 character sheets into `Z:\...\CHARACTER\` (including overwriting `G03_06 - Ông Khải` with his distinct bare-eyed face!), updates `character_registry.json` AND `00_GIA_PHA_NHAN_VAT_K4.md`.
4. Builds 5 Visual Asset Boards (`AssetBoard_F01.jpg`..`AssetBoard_F05.jpg`) -> saves to `assetboards/` & Artifact dir.
5. Generates `flow_f01.json`..`flow_f05.json` + wave batch specs (`104` cinema shots total, `<=3` ingredients per shot, `8s–10s` speech buffers).
"""
import json, os, shutil
from PIL import Image, ImageDraw, ImageFont

from episodes_f01_to_f05_spec import EPISODES_261124
from prepare_261124_chatgpt_assets import split_k4_sheet_exact

BASE_DIR = r"d:\AI\full studio\output\k4-5-reels-261124"
CAST_FACE_DIR = os.path.join(BASE_DIR, "cast_clean")
CAST_BODY_DIR = os.path.join(BASE_DIR, "cast_fullbody")
PAIR_DIR = os.path.join(BASE_DIR, "cast_pairs")
NEW_SHEETS_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR = os.path.join(BASE_DIR, "sets")
BOARDS_DIR = os.path.join(BASE_DIR, "assetboards")
ART_DIR = r"C:\Users\Hang thu\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
CHAR_DRIVE = r"Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"

for d in (PAIR_DIR, BOARDS_DIR, ART_DIR):
    os.makedirs(d, exist_ok=True)

NEW_K4_SHEETS = [
    ("cucuc",     "G04_01b - Cụ Cúc (Bà nội Quân & Uyên - Mẹ ruột Bác Trọng) [Áo bà già nâu lễ mừng thọ].png", "G04", "Cụ Cúc (75t)", "Mẹ ruột Bác Trọng; bà nội Quân & Uyên [Áo bà già nâu lễ mừng thọ 75]", False),
    ("bactrong",  "G04_07 - Bác Trọng (Con trai cụ Cúc - Chồng bác Nga - Bố ruột Quân & Uyên) [Vest đen cài hoa đỏ mừng thọ].png", "G04", "Bác Trọng (55t)", "Con trai cụ Cúc; chồng bác Nga; bố ruột Quân & Uyên; bác cả Tuấn [Vest đen hoa đỏ]", False),
    ("quan_somi", "G04_05c - Quân (Con trai Bác Trọng - Cháu đích tôn cụ Cúc) [Sơ mi trắng quần âu].png", "G04", "Quân (27t)", "Con trai Bác Trọng & Bác Nga; cháu đích tôn cụ Cúc [Sơ mi trắng quần âu]", False),
    ("hieu_vest", "G05_02b - Hiếu (Con trai trưởng bà Mận - Giám đốc công ty) [Vest đen lễ khánh thành].png", "G05", "Hiếu (31t)", "Con trai trưởng bà Mận; Giám đốc công ty [Vest đen lễ khánh thành]", False),
    ("le_letan",  "G07_04 - Lê (Trưởng lễ tân kiêu kỳ sự kiện công ty Hiếu) [Đầm lụa kem sự kiện].png", "G07", "Lê (26t)", "Trưởng ban lễ tân kiêu kỳ tại lễ khánh thành công ty Hiếu [Đầm lụa kem]", False),
    ("khang_ql",  "G07_05 - Khang (Quản lý sự kiện hách dịch công ty Hiếu) [Vest xanh navy].png", "G07", "Khang (29t)", "Quản lý sự kiện hách dịch công ty Hiếu [Vest xanh navy]", False),
    ("ongloc",    "G08_01 - Ông Lộc (Bố quê thợ xây vôi ăn sần tay của bác sĩ Khoa & Hải).png", "G08", "Ông Lộc (63t)", "Bố ruột ở quê làm thợ xây vôi ăn sần tay của Hải & bác sĩ Khoa", False),
    ("hai_anhca", "G08_02 - Hải (Anh trai cả thợ xây hiền lành của bác sĩ Khoa - Con lớn ông Lộc).png", "G08", "Hải (36t)", "Con trai cả ông Lộc; anh trai ruột nhường suất đại học nuôi bác sĩ Khoa", False),
    ("khoa_bs",   "G08_03 - Khoa (Bác sĩ Trưởng khoa hiếu thảo - Con trai thứ ông Lộc - Chồng Châu) [Áo blouse trắng bác sĩ].png", "G08", "Bác sĩ Khoa (31t)", "Con trai thứ ông Lộc; em ruột Hải; Tân Trưởng khoa bệnh viện; chồng Châu", False),
    ("chau_vo",   "G08_04 - Châu (Vợ sĩ diện của bác sĩ Khoa - Con gái ông Đạt & bà Quý) [Đầm dạ tiệc đỏ rượu].png", "G08", "Châu (28t)", "Vợ sĩ diện của bác sĩ Khoa; con gái ruột ông Đạt & bà Quý [Đầm đỏ rượu]", False),
    ("ongdat",    "G08_05 - Ông Đạt (Bố vợ giàu hách dịch của bác sĩ Khoa - Bố ruột Châu) [Vest kẻ xám ghi lê].png", "G08", "Ông Đạt (58t)", "Bố ruột Châu; chồng bà Quý; bố vợ giàu hách dịch của bác sĩ Khoa [Vest kẻ xám]", False),
    ("baquy",     "G08_06 - Bà Quý (Mẹ vợ chua ngoa của bác sĩ Khoa - Vợ ông Đạt - Mẹ ruột Châu) [Áo dài nhung xanh đen].png", "G08", "Bà Quý (55t)", "Vợ ông Đạt; mẹ ruột Châu; mẹ vợ chua ngoa của bác sĩ Khoa [Áo dài nhung xanh đen]", False),
    ("ongbinh",   "G09_01 - Ông Bình (Bố quê mang giỏ trứng gà thương con - Bố ruột Đức & Ngọc).png", "G09", "Ông Bình (62t)", "Bố ruột ở quê giàu lòng tự trọng của Đức & Ngọc; bố vợ Minh [Xách giỏ trứng gà]", False),
    ("duc_anh",   "G09_02 - Đức (Con trai trưởng ích kỷ nhà giàu của ông Bình - Anh ruột Ngọc).png", "G09", "Đức (34t)", "Con trai trưởng khá giả nhưng ích kỷ của ông Bình; anh trai ruột Ngọc", False),
    ("ngoc_vo",   "G09_03 - Ngọc (Con gái hiếu thảo của ông Bình - Vợ Minh) [Áo sơ mi kẻ caro ở nhà].png", "G09", "Ngọc (28t)", "Con gái út hiếu thảo của ông Bình; em gái Đức; vợ của Minh [Sơ mi caro]", False),
    ("minh_re",   "G09_04 - Minh (Con rể tốt bụng trầm tính của ông Bình - Chồng Ngọc) [Sơ mi trắng công sở].png", "G09", "Minh (31t)", "Chồng của Ngọc; con rể tinh tế trọng tình nghĩa của ông Bình [Sơ mi trắng]", False),
    ("ongkhai_fix", "G03_06 - Ông Khải (Chồng sau cô Lan - Dượng chú của Tuấn - Bố ruột Sơn & An).png", "G03", "Ông Khải (56t)", "Chồng sau cô Lan; bố ruột Sơn & An (Gương mặt riêng không kính, tách biệt 100% với Ông Tấn)", True),
]

# 1. Split new K4 sheets & sync to CHARACTER/ Drive + character_registry.json + 00_GIA_PHA_NHAN_VAT_K4.md
for key, fn, branch, cname, rel, force_ow in NEW_K4_SHEETS:
    sp = os.path.join(NEW_SHEETS_DIR, fn)
    assert os.path.exists(sp), f"Missing generated K4 sheet: {sp}"
    split_k4_sheet_exact(
        sp,
        os.path.join(CAST_FACE_DIR, f"k4_{key}.jpg"),
        os.path.join(CAST_BODY_DIR, f"k4_{key}_full.jpg"),
    )
    if os.path.isdir(CHAR_DRIVE):
        dst = os.path.join(CHAR_DRIVE, fn)
        if force_ow or not os.path.exists(dst):
            shutil.copy2(sp, dst)
            print(f"[CHARACTER SYNC] {'Overwrote' if force_ow else 'Saved'} -> {fn}")

if os.path.isdir(CHAR_DRIVE):
    reg_path = os.path.join(CHAR_DRIVE, "character_registry.json")
    if os.path.exists(reg_path):
        reg = json.load(open(reg_path, encoding="utf-8"))
        by_new = {x["new"]: x for x in reg["items"]}
        for _, fn, branch, cname, rel, _ in NEW_K4_SHEETS:
            by_new[fn] = {"old": fn, "new": fn, "branch": branch, "name": cname, "relation": rel}
        reg["items"] = list(by_new.values())
        reg["total_files"] = len(reg["items"])
        json.dump(reg, open(reg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Updated character_registry.json -> {reg['total_files']} total items!")

    md_path = os.path.join(CHAR_DRIVE, "00_GIA_PHA_NHAN_VAT_K4.md")
    if os.path.exists(md_path):
        md_txt = open(md_path, encoding="utf-8").read()
        if "G08_01" not in md_txt:
            extra_md = """

---

### Bổ Sung Lô `261124` — Các Nhánh Gia Đình Độc Lập & Nhân Vật Đúng Độ Tuổi (Không Trùng Vai Bố!)

- **`G04` & `G05` & `G07` (Mở rộng đúng vai vế & độ tuổi)**:
  - `G04_01b`: **Cụ Cúc (75 tuổi)** — Bà nội Quân & Uyên, mẹ ruột Bác Trọng `[Áo bà già nâu lễ mừng thọ]`.
  - `G04_07`: **Bác Trọng (55 tuổi)** — Con trai Cụ Cúc, chồng Bác Nga, bố ruột Quân & Uyên, bác cả Tuấn `[Vest đen cài hoa đỏ mừng thọ]` *(gương mặt vuông không đeo kính)*.
  - `G04_05c`: **Quân (27 tuổi)** — Con trai Bác Trọng, cháu đích tôn Cụ Cúc `[Sơ mi trắng quần âu]`.
  - `G05_02b`: **Hiếu (31 tuổi)** — Con trai trưởng Bà Mận, Giám đốc công ty `[Vest đen lễ khánh thành]`.
  - `G07_04`: **Lê (26 tuổi)** — Trưởng lễ tân sự kiện công ty Hiếu `[Đầm lụa kem]`.
  - `G07_05`: **Khang (29 tuổi)** — Quản lý sự kiện công ty Hiếu `[Vest xanh navy]`.
  - `G03_06` *(Cập nhật mới)*: **Ông Khải (56 tuổi)** — Chồng sau cô Lan, gương mặt riêng không kính (tách biệt hoàn toàn với Ông Tấn `G01_02`).

- **`G08` — Nhánh Bác Sĩ Khoa: Gia Đình Ông Lộc Thợ Xây & Nhà Vợ Giàu Ông Đạt – Bà Quý (6 nhân vật)**:
  - `G08_01`: **Ông Lộc (63 tuổi)** — Bố ruột ở quê làm thợ xây vôi ăn sần tay của Hải & bác sĩ Khoa *(gương mặt gầy rám nắng, tóc cua ngắn điểm bạc, không kính)*.
  - `G08_02`: **Hải (36 tuổi)** — Con trai cả Ông Lộc; anh trai hiền lành nhường suất đại học đi vác xi măng nuôi em.
  - `G08_03`: **Bác sĩ Khoa (31 tuổi)** — Con trai thứ Ông Lộc; Tân Trưởng khoa bệnh viện; chồng Châu `[Áo blouse trắng sơ mi cà vạt]`.
  - `G08_04`: **Châu (28 tuổi)** — Vợ sĩ diện của bác sĩ Khoa; con gái Ông Đạt & Bà Quý `[Đầm dạ tiệc đỏ rượu]`.
  - `G08_05`: **Ông Đạt (58 tuổi)** — Bố vợ giàu hách dịch của bác sĩ Khoa; bố ruột Châu `[Vest kẻ xám ghi lê]` *(gương mặt tròn đầy, trán cao, không kính)*.
  - `G08_06`: **Bà Quý (55 tuổi)** — Mẹ vợ chua ngoa của bác sĩ Khoa; vợ Ông Đạt `[Áo dài nhung xanh đen]`.

- **`G09` — Nhánh Gia Đình Ông Bình Ở Quê & Con Rể Minh Trọng Tình Nghĩa (4 nhân vật)**:
  - `G09_01`: **Ông Bình (62 tuổi)** — Bố quê hiền từ giàu lòng tự trọng của Đức & Ngọc; bố vợ Minh `[Áo nâu vá xách giỏ trứng gà]` *(gương mặt tròn phúc hậu, tóc muối tiêu tự nhiên, không kính)*.
  - `G09_02`: **Đức (34 tuổi)** — Con trai trưởng khá giả nhưng thoái thác của Ông Bình; anh ruột Ngọc.
  - `G09_03`: **Ngọc (28 tuổi)** — Con gái út hiếu thảo của Ông Bình; vợ Minh `[Áo sơ mi kẻ caro ở nhà]`.
  - `G09_04`: **Minh (31 tuổi)** — Chồng Ngọc; con rể trầm tính tinh tế rút tiết kiệm đặt dưới giỏ trứng gà giúp bố vợ sửa mái nhà `[Sơ mi trắng công sở]`.
"""
            open(md_path, "w", encoding="utf-8").write(md_txt.rstrip() + extra_md + "\n")
            print("Appended G04_07, G07_04..05, G08, G09 to 00_GIA_PHA_NHAN_VAT_K4.md!")

# 2. Optimize all 10 Set PNGs to clean 1280px JPEGs
SET_LIST = [
    ("f01bo1", "F01_BO1_BuongTrongCuToi"),
    ("f01bo2", "F01_BO2_SanhTiecMungThoDongKhach"),
    ("f02bo1", "F02_BO1_PhongNguTuDoTuanThao"),
    ("f02bo2", "F02_BO2_PhongKhachNhaBaHanh"),
    ("f03bo1", "F03_BO1_ThamDoKhanhThanhDongNguoi"),
    ("f03bo2", "F03_BO2_BacThemLeDaiKhanhThanh"),
    ("f04bo1", "F04_BO1_SanhTiecMungTruongKhoaDongKhach"),
    ("f05bo1", "F05_BO1_PhongKhachNhaDucSangTrong"),
    ("f05bo2", "F05_BO2_CuaCanHoMinhNgoc"),
    ("f05bo3", "F05_BO3_BanAnAmCungMinhNgoc"),
]

SET_JPG = {}
for skey, sbase in SET_LIST:
    p_png = os.path.join(SETS_DIR, f"{sbase}.png")
    assert os.path.exists(p_png), f"Missing generated Set PNG: {p_png}"
    p_jpg = os.path.join(SETS_DIR, f"{sbase}.jpg")
    im = Image.open(p_png).convert("RGB")
    im.thumbnail((1280, 1280), Image.LANCZOS)
    im.save(p_jpg, "JPEG", quality=93)
    SET_JPG[skey] = p_jpg

def get_char_img(ckey, is_wide):
    if is_wide:
        return os.path.join(CAST_BODY_DIR, f"k4_{ckey}_full.jpg"), f"k4_{ckey}_full.jpg"
    return os.path.join(CAST_FACE_DIR, f"k4_{ckey}.jpg"), f"k4_{ckey}.jpg"

def get_pair_img(ck2, ck3, is_wide):
    tag = "full" if is_wide else "face"
    out_name = f"pair_{ck2}_{ck3}_{tag}.jpg"
    out_path = os.path.join(PAIR_DIR, out_name)
    if not os.path.exists(out_path):
        p2, _ = get_char_img(ck2, is_wide)
        p3, _ = get_char_img(ck3, is_wide)
        i2 = Image.open(p2).convert("RGB")
        i3 = Image.open(p3).convert("RGB")
        th = 960
        w2 = int(i2.width * th / i2.height)
        w3 = int(i3.width * th / i3.height)
        i2 = i2.resize((w2, th), Image.LANCZOS)
        i3 = i3.resize((w3, th), Image.LANCZOS)
        combo = Image.new("RGB", (w2 + w3 + 12, th), (240, 240, 240))
        combo.paste(i2, (0, 0))
        combo.paste(i3, (w2 + 12, 0))
        combo.save(out_path, "JPEG", quality=93)
    return out_path, out_name

def build_asset_board(ep_id, cfg):
    items = cfg["board_items"]
    cols = 4
    rows = (len(items) + cols - 1) // cols
    cw, ch = 320, 400
    board = Image.new("RGB", (cols * cw, 64 + rows * ch), (16, 18, 24))
    draw = ImageDraw.Draw(board)
    try:
        fh = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
        fs = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
    except Exception:
        fh = fs = None
    draw.text((16, 18), f"ASSET BOARD — {ep_id.upper()}: {cfg['title']} ({len(cfg['shots'])} cảnh)", fill=(255, 215, 70), font=fh)
    for idx, (lbl, key) in enumerate(items):
        r, c = idx // cols, idx % cols
        x0, y0 = c * cw + 10, 64 + r * ch + 8
        ip = SET_JPG[key] if key in SET_JPG else get_char_img(key, True)[0]
        im = Image.open(ip).convert("RGB")
        im.thumbnail((cw - 20, ch - 46), Image.LANCZOS)
        board.paste(im, (x0 + (cw - 20 - im.width) // 2, y0 + 30))
        draw.text((x0 + 4, y0 + 5), lbl, fill=(130, 235, 255), font=fs)
    out = os.path.join(BOARDS_DIR, f"AssetBoard_{ep_id.upper()}.jpg")
    board.save(out, "JPEG", quality=92)
    shutil.copy2(out, os.path.join(ART_DIR, f"AssetBoard_{ep_id.upper()}.jpg"))

CAMERA_DESC = {
    "WIDE": "TOÀN CẢNH RỘNG (WIDE ESTABLISHING SHOT, ống kính 24mm lấy trọn toàn thân nhân vật từ đầu đến chân và không gian căn phòng/sân sảnh). Khung hình điện ảnh sạch vững chãi, không cắt cụt chân, tuyệt đối không xuất hiện máy quay hay thiết bị đoàn phim trong hình, một cảnh liền mạch không tự chia shot.",
    "WIDE_CROWD": "ĐẠI CẢNH RỘNG ĐÔNG NGƯỜI (WIDE CROWD ESTABLISHING SHOT, ống kính góc rộng 24mm thấy trọn toàn thân các nhân vật chính ở tiền cảnh và quan khách/đám đông tự nhiên ở hậu cảnh). Một cảnh liền mạch không chia shot.",
    "MED": "TRUNG CẢNH HÀNH ĐỘNG (MEDIUM TWO-SHOT từ ngang hông/thắt lưng trở lên, thấy rõ cử chỉ tay, đạo cụ và tương tác hình thể giữa các nhân vật). Máy giữ ổn định ngang tầm mắt, một cảnh liền mạch.",
    "CU": "CẬN CẢNH ĐẶC TẢ CẢM XÚC (EMOTIONAL CLOSE-UP từ ngực lên mặt, lấy nét sắc sảo vào ánh mắt, cơ mặt và khẩu hình môi). Hậu cảnh xóa phông điện ảnh nhẹ, máy tĩnh vững chãi, một cảnh liền mạch.",
}

all_flow_jobs = []
for ep_id, cfg in sorted(EPISODES_261124.items()):
    build_asset_board(ep_id, cfg)
    ep_jobs = []
    raw_dir = os.path.join(BASE_DIR, ep_id, "raw_9x16")
    os.makedirs(raw_dir, exist_ok=True)

    for sid, scale, skey, char_keys, spatial, action, speaker, dlg in cfg["shots"]:
        is_wide = scale in ("WIDE", "WIDE_CROWD", "MED")
        wc = len(dlg.split()) if dlg else 0
        if not speaker:
            sec = 6
        elif wc <= 15:
            sec = 8
        elif wc <= 20:
            sec = 9
        else:
            sec = 10

        set_path = SET_JPG[skey]
        refs = [{"path": set_path, "name": f"set_{skey}.jpg"}]

        if len(char_keys) == 1:
            cp, cn = get_char_img(char_keys[0], is_wide)
            refs.append({"path": cp, "name": cn})
            img_lines = "- image 1: BO-1 (Bối cảnh)\n- image 2: CH-1"
        elif len(char_keys) == 2:
            c1p, c1n = get_char_img(char_keys[0], is_wide)
            c2p, c2n = get_char_img(char_keys[1], is_wide)
            refs.append({"path": c1p, "name": c1n})
            refs.append({"path": c2p, "name": c2n})
            img_lines = "- image 1: BO-1 (Bối cảnh)\n- image 2: CH-1\n- image 3: CH-2"
        else:
            c1p, c1n = get_char_img(char_keys[0], is_wide)
            pp, pn = get_pair_img(char_keys[1], char_keys[2], is_wide)
            refs.append({"path": c1p, "name": c1n})
            refs.append({"path": pp, "name": pn})
            img_lines = "- image 1: BO-1 (Bối cảnh)\n- image 2: CH-1\n- image 3: CH-2 (bên trái ảnh 3) và CH-3 (bên phải ảnh 3)"

        if speaker and dlg:
            action_block = (
                f"Ngay từ 0.2 giây đầu cảnh, {action} "
                f"Nhân vật nói dứt khoát, rõ chữ trọn vẹn câu thoại trong khoảng 4.5 giây đầu rồi khép môi tự nhiên, giữ ánh mắt cảm xúc nhìn đối phương trong 2 giây cuối cảnh (tuyệt đối không để câu nói kéo sát cuối video, không nói lặp lại câu)."
            )
            thoai_block = (
                f"THOẠI TRỰC TIẾP (NÓI ĐÚNG MỘT LẦN TRỌN VẸN RỒI KHÉP MÔI):\n"
                f"{speaker}: “{dlg}”\n"
                f"(Giọng tiếng Việt truyền cảm tự nhiên như phim truyền hình người thật, lip-sync khớp chính xác từng âm tiết từ đầu tới chữ cuối cùng, nói dứt câu là khép môi nghỉ nhịp thở cuối cảnh; các nhân vật khác lắng nghe không mở miệng nói chèn)."
            )
        else:
            action_block = f"{action} Diễn xuất hình thể và ánh mắt chân thực hoàn toàn không lời thoại."
            thoai_block = "THOẠI:\nKhông có lời thoại. Nhân vật khép môi tự nhiên, không mấp máy môi."

        prompt_v1 = (
            f"Tạo video {sec} giây, photorealistic live-action người Việt Nam thật, phong cách phim truyền hình tâm lý gia đình Việt Nam chất lượng điện ảnh 8k, tỷ lệ dọc 9:16.\n\n"
            f"IMAGE XUẤT HIỆN:\n{img_lines}\n\n"
            f"REFERENCE:\nSử dụng đúng 100% khuôn mặt, kiểu tóc, độ tuổi, vóc dáng và trang phục từ image reference đã đính kèm. Không tự ý đổi quần áo, không thêm người lạ hay đạo cụ vô lý.\n\n"
            f"BỐI CẢNH:\nĐặt đúng trong không gian kiến trúc và ánh sáng của BO-1 (image 1).\n\n"
            f"CHỐT KHÔNG GIAN (GIỮ TRỤC 180 ĐỘ):\n{spatial}\n\n"
            f"CAMERA:\n{CAMERA_DESC[scale]}\n\n"
            f"DIỄN BIẾN:\n{action_block}\n\n"
            f"{thoai_block}\n\n"
            f"YÊU CẦU:\nKhông phụ đề, không chữ trên màn hình, không logo/watermark, không hiệu ứng hoạt hình."
        )

        prompt_v2 = prompt_v1.replace("quát", "nói nghiêm nghị").replace("xô đẩy", "ngăn cản").replace("chà đạp", "coi nhẹ").replace("câm miệng", "dừng lời")

        job = {
            "id": f"{ep_id}_{sid}_9x16",
            "ep": ep_id,
            "sid": sid,
            "scale": scale,
            "ratio": "9:16",
            "seconds": sec,
            "expected_dialogue": dlg or "",
            "outPath": os.path.join(raw_dir, f"{sid}.mp4"),
            "refs": refs,
            "prompts": [prompt_v1, prompt_v2],
        }
        ep_jobs.append(job)
        all_flow_jobs.append(job)

    ep_spec = os.path.join(BASE_DIR, f"flow_{ep_id}.json")
    json.dump(ep_jobs, open(ep_spec, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

waves = [
    ("flow_wave1_f01_f03.json", ("f01", "f02", "f03")),
    ("flow_wave2_f04_f05.json", ("f04", "f05")),
]
for wfn, ep_set in waves:
    wjobs = [j for j in all_flow_jobs if j["ep"] in ep_set]
    json.dump(wjobs, open(os.path.join(BASE_DIR, wfn), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

json.dump(all_flow_jobs, open(os.path.join(BASE_DIR, "flow_all_5_f01_f05.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Built 5 Asset Boards + {len(all_flow_jobs)} Flow Cinema Jobs across f01..f05!")
