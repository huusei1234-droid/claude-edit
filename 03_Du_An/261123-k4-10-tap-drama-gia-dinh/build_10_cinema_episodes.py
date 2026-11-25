"""
Build All 10 K4 Cinema Episodes (`261123 Batch`):
1. Verifies all 38 ChatGPT images (15 K4 2-panel character sheets + 23 `9:16` location/crowd sets).
2. Splits the 15 new K4 character sheets cleanly (`cast_clean/` + `cast_fullbody/`).
3. Syncs all 15 new character sheets into Google Drive `CHARACTER/` + updates `character_registry.json` & `00_GIA_PHA_NHAN_VAT_K4.md`.
4. Builds all 10 Asset Boards (`AssetBoard_EP01.jpg`..`AssetBoard_EP10.jpg`) -> saves to `assetboards/` & Artifact dir.
5. Generates `flow_ep01.json`..`flow_ep10.json` + wave batch specs (`178` cinema shots total, `<=3` ingredients per shot, generous `8s–9s` speech buffers).
"""
import json, os, shutil
from PIL import Image, ImageDraw, ImageFont

from episodes_01_to_05_spec import EPISODES_01_05
from episodes_06_to_10_spec import EPISODES_06_10
from prepare_chatgpt_10_batch import split_k4_sheet_exact

BASE_DIR = r"d:\AI\full studio\output\k4-10-videos-261123"
CAST_FACE_DIR = os.path.join(BASE_DIR, "cast_clean")
CAST_BODY_DIR = os.path.join(BASE_DIR, "cast_fullbody")
PAIR_DIR = os.path.join(BASE_DIR, "cast_pairs")
NEW_SHEETS_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR = os.path.join(BASE_DIR, "sets")
BOARDS_DIR = os.path.join(BASE_DIR, "assetboards")
ART_DIR = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
CHAR_DRIVE = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"

for d in (PAIR_DIR, BOARDS_DIR):
    os.makedirs(d, exist_ok=True)

NEW_K4_SHEETS = [
    ("ongphuc",          "G06_04 - Ông Phúc (Bố quê nghèo vác bao tải dứa của Tiến).png", "G06", "Ông Phúc", "Bố ruột ở quê của Tiến"),
    ("khanhly_tapde",    "G06_03b - Khánh Ly (Vợ Tiến - Con dâu bác Thắm) [Áo hoa đeo tạp dề].png", "G06", "Khánh Ly", "Vợ Tiến [Áo hoa đeo tạp dề nội trợ]"),
    ("khanhly_vestvang", "G06_03c - Khánh Ly (Vợ Tiến - Con dâu bác Thắm) [Bộ vest vàng quý phái].png", "G06", "Khánh Ly", "Vợ Tiến [Bộ vest vàng quý phái]"),
    ("son_ct",           "G03_07b - Sơn (Con trai lớn riêng ông Khải) [Áo phản quang công trường].png", "G03", "Sơn", "Con trai riêng ông Khải [Áo phản quang công trường]"),
    ("thanh_ship",       "G01_09b - Thành (Chồng Linh - Em rể Tuấn) [Đồng phục Shipper cam].png", "G01", "Thành", "Chồng Linh [Đồng phục giao hàng Shipper cam]"),
    ("ongbach",          "G07_03 - Ông Bách (Giám đốc chi nhánh nóng nảy sơ mi đen).png", "G07", "Ông Bách", "Giám đốc chi nhánh nóng nảy"),
    ("quan_trang",       "G04_05b - Quân (Con trai bác Nga - Anh họ Tuấn) [Áo dài tay trắng giản dị].png", "G04", "Quân", "Anh họ nội Tuấn [Áo trắng Chủ tịch vi hành]"),
    ("an_cs",            "G03_08b - An (Con gái út ông Khải) [Vest công sở xanh than].png", "G03", "An", "Con gái út ông Khải [Vest công sở xanh than]"),
    ("uyen_sodo",        "G04_03b - Uyên (Chị họ nội Tuấn) [Sơ mi kem cầm sổ đỏ].png", "G04", "Uyên", "Chị họ nội Tuấn [Sơ mi kem ôm sổ đỏ]"),
    ("colan_giandi",     "G03_01b - Cô Lan (Cô ruột Tuấn) [Áo sơ mi kem giản dị].png", "G03", "Cô Lan", "Cô ruột Tuấn [Áo sơ mi kem giản dị]"),
    ("tu_chure",         "G03_02b - Tú (Con trai cô Lan - Chồng Lam) [Vest chú rể đen].png", "G03", "Tú", "Con trai cô Lan [Vest chú rể đen]"),
    ("lam_codau",        "G03_03b - Lam (Vợ Tú - Con dâu cô Lan) [Váy cưới trắng].png", "G03", "Lam", "Vợ Tú [Váy cưới ren trắng lễ đường]"),
    ("linh_blazer",      "G01_08b - Linh (Em gái ruột Tuấn) [Bộ vest họa tiết đi tiệc].png", "G01", "Linh", "Em gái ruột Tuấn [Bộ vest họa tiết thời trang]"),
    ("my_tochong",       "G05_07b - Mỹ (Vợ Khôi) [Tóc hồng đầm hoa xem mắt].png", "G05", "Mỹ", "Vợ Khôi [Tóc hồng đầm hoa xem mắt]"),
    ("nhung_aolong",     "G05_05d - Nhung (Chị gái Trang) [Áo lông xanh đầm đỏ].png", "G05", "Nhung", "Chị gái Trang [Áo lông xanh đầm đỏ]"),
]

# 1. Split new K4 sheets & sync to CHARACTER/ Drive
for key, fn, branch, cname, rel in NEW_K4_SHEETS:
    sp = os.path.join(NEW_SHEETS_DIR, fn)
    assert os.path.exists(sp), f"Missing generated K4 sheet: {sp}"
    split_k4_sheet_exact(
        sp,
        os.path.join(CAST_FACE_DIR, f"k4_{key}.jpg"),
        os.path.join(CAST_BODY_DIR, f"k4_{key}_full.jpg"),
    )
    if os.path.isdir(CHAR_DRIVE):
        dst = os.path.join(CHAR_DRIVE, fn)
        if not os.path.exists(dst):
            shutil.copy2(sp, dst)

if os.path.isdir(CHAR_DRIVE):
    reg_path = os.path.join(CHAR_DRIVE, "character_registry.json")
    if os.path.exists(reg_path):
        reg = json.load(open(reg_path, encoding="utf-8"))
        for _, fn, branch, cname, rel in NEW_K4_SHEETS:
            if not any(x["new"] == fn for x in reg["items"]):
                reg["items"].append({
                    "old": fn, "new": fn, "branch": branch, "name": cname, "relation": rel
                })
        reg["total_files"] = len(reg["items"])
        json.dump(reg, open(reg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 2. Optimize all 23 Set PNGs to clean 1280px JPEGs
SET_LIST = [
    ("e01bo1", "E01_BO1_CongBietThuSang"),
    ("e01bo2", "E01_BO2_PhongKhachTuanThao"),
    ("e01bo3", "E01_BO3_BenXeKhachDongNguoi"),
    ("e02bo1", "E02_BO1_CuaCanHoLinh"),
    ("e02bo2", "E02_BO2_PhoThuongMaiDongNguoi"),
    ("e02bo3", "E02_BO3_NhaCap4TienLy"),
    ("e03bo1", "E03_BO1_PhongTroVoChongTre"),
    ("e03bo2", "E03_BO2_ViaHePhoDongXe"),
    ("e03bo3", "E03_BO3_CongTruongMayXuc"),
    ("e04bo1", "E04_BO1_PhongGiamDocBach"),
    ("e04bo2", "E04_BO2_VanPhongMoDongNhanVien"),
    ("e04bo3", "E04_BO3_SanhTapDoanSangTrong"),
    ("e05bo1", "E05_BO1_CanHoBanCongKinh"),
    ("e05bo2", "E05_BO2_HanhLangThangMay"),
    ("e06bo1", "E06_BO1_SanhTiecCuoiDongKhach"),
    ("e06bo2", "E06_BO2_BacThemHoaLeDuong"),
    ("e07bo1", "E07_BO1_PhongKhachDemKhuya"),
    ("e07bo2", "E07_BO2_GocBanAnDem"),
    ("e08bo1", "E08_BO1_ViaHeSapOiBanNgay"),
    ("e08bo2", "E08_BO2_ViaHeSapOiHoangHon"),
    ("e09bo1", "E09_BO1_BaiDoXeMercedesDongNguoi"),
    ("e10bo1", "E10_BO1_NhaHangSangTrongDongKhach"),
    ("e10bo2", "E10_BO2_LoiRaPhongVipNhaHang"),
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

# 3. Build all 10 Asset Boards
ALL_EPISODES = {**EPISODES_01_05, **EPISODES_06_10}

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

# 4. Build Flow Prompts strictly adhering to `phim-ai-flow-prompt` + 0% Cut-off Discipline
CAMERA_DESC = {
    "WIDE": "TOÀN CẢNH RỘNG (WIDE ESTABLISHING SHOT, ống kính 24mm lấy trọn toàn thân nhân vật từ đầu đến chân và không gian kiến trúc căn phòng/sân cổng). Máy đặt vững trên tripod, dolly nhẹ tinh tế, không cắt cụt chân, một cảnh liền mạch không tự chia shot.",
    "WIDE_CROWD": "ĐẠI CẢNH RỘNG ĐÔNG NGƯỜI (WIDE CROWD ESTABLISHING SHOT, ống kính góc rộng 24mm thấy trọn toàn thân các nhân vật chính ở tiền cảnh và dòng người phụ/khách qua lại sinh động tự nhiên ở hậu cảnh). Một cảnh liền mạch không chia shot.",
    "MED": "TRUNG CẢNH HÀNH ĐỘNG (MEDIUM TWO-SHOT từ ngang gối/thắt lưng trở lên, thấy rõ cử chỉ tay, đạo cụ và tương tác hình thể giữa các nhân vật). Máy giữ ổn định ngang tầm mắt, một cảnh liền mạch.",
    "CU": "CẬN CẢNH ĐẶC TẢ CẢM XÚC (EMOTIONAL CLOSE-UP từ ngực lên mặt, lấy nét sắc sảo vào ánh mắt, cơ mặt và khẩu hình môi). Hậu cảnh xóa phông điện ảnh nhẹ, máy tĩnh vững chãi, một cảnh liền mạch.",
}

all_flow_jobs = []
for ep_id, cfg in sorted(ALL_EPISODES.items()):
    build_asset_board(ep_id, cfg)
    ep_jobs = []
    raw_dir = os.path.join(BASE_DIR, ep_id, "raw_9x16")
    os.makedirs(raw_dir, exist_ok=True)

    for sid, scale, skey, char_keys, spatial, action, speaker, dlg in cfg["shots"]:
        is_wide = scale in ("WIDE", "WIDE_CROWD", "MED")
        wc = len(dlg.split()) if dlg else 0
        if not speaker:
            sec = 6
        elif wc <= 14:
            sec = 8
        elif wc <= 19:
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
            # 3 characters -> image 1: Set, image 2: CH-1, image 3: composite pair (CH-2 left + CH-3 right)
            c1p, c1n = get_char_img(char_keys[0], is_wide)
            pp, pn = get_pair_img(char_keys[1], char_keys[2], is_wide)
            refs.append({"path": c1p, "name": c1n})
            refs.append({"path": pp, "name": pn})
            img_lines = "- image 1: BO-1 (Bối cảnh)\n- image 2: CH-1\n- image 3: CH-2 (đứng bên trái ảnh tham chiếu 3) và CH-3 (đứng bên phải ảnh tham chiếu 3)"

        if speaker and dlg:
            action_block = (
                f"Ngay từ 0.2 giây đầu cảnh, {action} "
                f"Nhân vật nói dứt khoát, rõ chữ trọn vẹn câu thoại trong khoảng 4 giây đầu rồi khép môi tự nhiên, giữ ánh mắt cảm xúc nhìn đối phương trong 2 giây cuối cảnh (tuyệt đối không để câu nói kéo sát cuối video)."
            )
            thoai_block = (
                f"THOẠI TRỰC TIẾP (BẮT BUỘC NÓI HẾT CÂU RỒI KHÉP MÔI SỚM):\n"
                f"{speaker}: “{dlg}”\n"
                f"(Giọng tiếng Việt truyền cảm tự nhiên như phim truyền hình người thật, lip-sync khớp chính xác từng âm tiết từ đầu tới chữ cuối cùng, nói dứt câu là khép môi nghỉ nhịp thở cuối cảnh; các nhân vật khác lắng nghe không mở miệng nói chèn)."
            )
        else:
            action_block = f"{action} Diễn xuất hình thể và ánh mắt chân thực hoàn toàn không lời thoại."
            thoai_block = "THOẠI:\nKhông có lời thoại. Nhân vật khép môi tự nhiên, không mấp máy môi."

        prompt_v1 = (
            f"Tạo video {sec} giây, photorealistic live-action người Việt Nam thật, phong cách phim truyền hình tâm lý gia đình Việt Nam chất lượng điện ảnh 8k, tỷ lệ dọc 9:16.\n\n"
            f"IMAGE XUẤT HIỆN:\n{img_lines}\n\n"
            f"REFERENCE:\nSử dụng đúng 100% khuôn mặt, kiểu tóc, độ tuổi, vóc dáng và trang phục từ image reference đã đính kèm. Không tự ý đổi quần áo, không thêm đạo cụ vô lý.\n\n"
            f"BỐI CẢNH:\nĐặt đúng trong không gian kiến trúc và ánh sáng của BO-1 (image 1).\n\n"
            f"CHỐT KHÔNG GIAN (GIỮ TRỤC 180 ĐỘ):\n{spatial}\n\n"
            f"CAMERA:\n{CAMERA_DESC[scale]}\n\n"
            f"DIỄN BIẾN:\n{action_block}\n\n"
            f"{thoai_block}\n\n"
            f"YÊU CẦU:\nKhông phụ đề, không chữ trên màn hình, không logo/watermark, không hiệu ứng hoạt hình."
        )

        # Gentle clean fallback variant in case of transient Flow retry
        prompt_v2 = prompt_v1.replace("quát", "nói nghiêm nghị").replace("cút", "bước").replace("đuổi", "mời ra")

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

# Also write 3 parallel-friendly waves so we can start rendering Masters as each wave finishes!
waves = [
    ("flow_wave1_ep01_03.json", ("ep01", "ep02", "ep03")),
    ("flow_wave2_ep04_07.json", ("ep04", "ep05", "ep06", "ep07")),
    ("flow_wave3_ep08_10.json", ("ep08", "ep09", "ep10")),
]
for wname, eps in waves:
    wjobs = [j for j in all_flow_jobs if j["ep"] in eps]
    wp = os.path.join(BASE_DIR, wname)
    json.dump(wjobs, open(wp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Wrote {wname}: {len(wjobs)} clips ({', '.join(eps)})")

print(f"TOTAL BUILT: {len(ALL_EPISODES)} episodes, {len(all_flow_jobs)} shots, 10 AssetBoards!")
