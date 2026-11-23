"""
Builds:
1. Clean left-panel portraits for all 9 newly generated ChatGPT K4 characters.
2. Syncs the 9 new K4 character sheets to Google Drive CHARACTER/ + updates character_registry.json & 00_GIA_PHA_NHAN_VAT_K4.md.
3. Visual Asset Board Composite Sheets (AssetBoard_V01..V05.jpg) for all 5 episodes.
4. Complete Google Flow Ingredients Video Job Specs (flow_jobs_9x16.json & flow_jobs_16x9.json) following `phim-ai-flow-prompt` skill 100%.
"""
import json, os, re, shutil
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
CAST_DIR = os.path.join(BASE_DIR, "cast_clean")
NEW_CHAR_RAW_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR = os.path.join(BASE_DIR, "sets")
BOARDS_DIR = os.path.join(BASE_DIR, "assetboards")
ART_DIR = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
CHAR_DRIVE = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"

os.makedirs(BOARDS_DIR, exist_ok=True)

NEW_CHARS = [
    ("G05_06_Khoi.jpg", "G05_06 - Khôi (Con trai út bà Mận - Em ruột Hiếu & Quỳnh - Chồng Mỹ).png", "G05", "Khôi", "Con trai út bà Mận; em ruột Hiếu & Quỳnh; chồng Mỹ"),
    ("G05_07_My.jpg", "G05_07 - Mỹ (Vợ Khôi - Con dâu út bà Mận - Em dâu Hiếu).png", "G05", "Mỹ", "Vợ của Khôi; con dâu út đanh đá của bà Mận; em dâu Hiếu"),
    ("G03_06_OngKhai.jpg", "G03_06 - Ông Khải (Chồng sau cô Lan - Dượng chú của Tuấn - Bố ruột Sơn & An).png", "G03", "Ông Khải", "Chồng sau của cô Lan; dượng chú của Tuấn; bố ruột Sơn & An"),
    ("G03_07_Son.jpg", "G03_07 - Sơn (Con trai lớn riêng ông Khải - Anh ruột An).png", "G03", "Sơn", "Con trai lớn riêng của ông Khải; anh ruột An; con chồng cô Lan"),
    ("G03_08_An.jpg", "G03_08 - An (Con gái út riêng ông Khải - Em gái ruột Sơn).png", "G03", "An", "Con gái út riêng của ông Khải; em gái ruột Sơn; con chồng cô Lan"),
    ("G03_05_BaSen.jpg", "G03_05 - Bà Sen (Mẹ ruột Lam ở quê - Mẹ vợ Tú - Thông gia cô Lan).png", "G03", "Bà Sen", "Mẹ ruột dưới quê của Lam; mẹ vợ Tú; thông gia cô Lan"),
    ("G04_05_Quan.jpg", "G04_05 - Quân (Con trai bác Nga - Anh ruột Uyên - Anh họ nội Tuấn) [Áo dài cưới đen].png", "G04", "Quân", "Con trai lớn bác Nga; anh ruột Uyên; anh họ nội Tuấn (trang phục áo dài cưới đen)"),
    ("G04_06_Kieu.jpg", "G04_06 - Kiều (Cô dâu đòi 2 tỷ sính lễ của Quân) [Áo dài cưới trắng].png", "G04", "Kiều", "Cô dâu hụt đòi 2 tỷ sính lễ của Quân (trang phục áo dài cưới trắng mấn vàng)"),
    ("G05_05c_NhungPhuDau.jpg", "G05_05c - Nhung (Chị gái ruột Trang - Bạn thân phù dâu) [Áo dài ren trắng].png", "G05", "Nhung", "Trang phục áo dài ren trắng phù dâu sang chảnh"),
]

# 1. Crop left close-up portraits & sync new sheets to CHARACTER/ on Google Drive
reg_path = os.path.join(CHAR_DRIVE, "character_registry.json")
reg_data = json.load(open(reg_path, encoding="utf-8")) if os.path.exists(reg_path) else {"total_files": 0, "items": []}
existing_names = {it["new"] for it in reg_data.get("items", [])}

for clean_fn, sheet_fn, branch, cname, crel in NEW_CHARS:
    src = os.path.join(NEW_CHAR_RAW_DIR, sheet_fn)
    assert os.path.exists(src), f"Missing generated ChatGPT character sheet: {src}"
    im = Image.open(src).convert("RGB")
    w, h = im.size
    # If ChatGPT rendered 2 side-by-side panels, crop left panel (0..48.6%); if single portrait, keep whole
    if w >= h * 0.85:
        crop = im.crop((0, 0, int(w * 0.486), h))
    else:
        crop = im
    dst_clean = os.path.join(CAST_DIR, clean_fn)
    crop.save(dst_clean, "JPEG", quality=96)
    print(f"Cropped new portrait: {clean_fn} {crop.size}")

    # Sync to Google Drive CHARACTER/
    if os.path.isdir(CHAR_DRIVE):
        dst_drive = os.path.join(CHAR_DRIVE, sheet_fn)
        if not os.path.exists(dst_drive):
            shutil.copy2(src, dst_drive)
        if sheet_fn not in existing_names:
            reg_data["items"].append({
                "old": sheet_fn,
                "new": sheet_fn,
                "branch": branch,
                "name": cname,
                "relation": crel,
            })

if os.path.isdir(CHAR_DRIVE):
    reg_data["total_files"] = len(reg_data["items"])
    with open(reg_path, "w", encoding="utf-8") as f:
        json.dump(reg_data, f, ensure_ascii=False, indent=2)
    print(f"Synced character_registry.json ({reg_data['total_files']} total items)")

# Convert sets to clean optimized JPEGs for fast Flow upload
SET_JPGS = {}
for sid in ["V1_BO1_NhaKhoi", "V1_BO2_CanHoHieu", "V2_BO1_PhongKhachOngTan", "V3_BO1_PhongChuTichCoLan", "V4_BO1_CongSanhNhaTu", "V5_BO1_CongCuoiNhaQuan"]:
    p_png = os.path.join(SETS_DIR, f"{sid}.png")
    assert os.path.exists(p_png), f"Missing generated ChatGPT set: {p_png}"
    p_jpg = os.path.join(SETS_DIR, f"{sid}.jpg")
    im = Image.open(p_png).convert("RGB")
    im.thumbnail((1280, 1280), Image.LANCZOS)
    im.save(p_jpg, "JPEG", quality=93)
    SET_JPGS[sid] = p_jpg

# 2. Build Visual Asset Boards (1 per episode)
def make_asset_board(ep_code, ep_title, items):
    cols = 3
    rows = (len(items) + cols - 1) // cols
    cw, ch = 380, 440
    board = Image.new("RGB", (cols * cw, 64 + rows * ch), (18, 20, 26))
    draw = ImageDraw.Draw(board)
    try:
        font_h = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
        font_s = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 17)
    except Exception:
        font_h = font_s = None
    draw.text((20, 18), f"ASSET BOARD — {ep_code}: {ep_title}", fill=(255, 215, 60), font=font_h)
    for idx, (code_label, img_p) in enumerate(items):
        r, c = idx // cols, idx % cols
        x0, y0 = c * cw + 12, 64 + r * ch + 10
        im = Image.open(img_p).convert("RGB")
        im.thumbnail((cw - 24, ch - 54), Image.LANCZOS)
        board.paste(im, (x0 + (cw - 24 - im.width) // 2, y0 + 34))
        draw.text((x0 + 4, y0 + 6), code_label, fill=(140, 235, 255), font=font_s)
    out_p = os.path.join(BOARDS_DIR, f"AssetBoard_{ep_code}.jpg")
    board.save(out_p, "JPEG", quality=92)
    shutil.copy2(out_p, os.path.join(ART_DIR, f"AssetBoard_{ep_code}.jpg"))
    print(f"Saved AssetBoard: {out_p}")

ASSET_DEFS = {
    "V01": ("Mẹ chỉ có một, vợ chọn đi", [
        ("CH-1: Bà Mận (G05_01)", os.path.join(CAST_DIR, "G05_01_BaMan.jpg")),
        ("CH-2: Hiếu (G05_02)", os.path.join(CAST_DIR, "G05_02_Hieu.jpg")),
        ("CH-3: Trang (G05_03)", os.path.join(CAST_DIR, "G05_03_Trang.jpg")),
        ("CH-4: Khôi (G05_06 Mới)", os.path.join(CAST_DIR, "G05_06_Khoi.jpg")),
        ("CH-5: Mỹ (G05_07 Mới)", os.path.join(CAST_DIR, "G05_07_My.jpg")),
        ("BO-1: Nhà Khôi (Vách gỗ)", SET_JPGS["V1_BO1_NhaKhoi"]),
        ("BO-2: Căn hộ Hiếu (Vách đá)", SET_JPGS["V1_BO2_CanHoHieu"]),
    ]),
    "V02": ("Bố chồng thu thẻ lương dạy con", [
        ("CH-1: Ông Tấn (G01_02)", os.path.join(CAST_DIR, "G01_02_OngTan.jpg")),
        ("CH-2: Thảo (G01_05a)", os.path.join(CAST_DIR, "G01_05a_Thao.jpg")),
        ("CH-3: Tuấn (G01_04b)", os.path.join(CAST_DIR, "G01_04b_Tuan.jpg")),
        ("BO-1: Phòng khách Ông Tấn", SET_JPGS["V2_BO1_PhongKhachOngTan"]),
    ]),
    "V03": ("Bánh đúc có xương - Mẹ kế Chủ tịch", [
        ("CH-1: Cô Lan (G03_01)", os.path.join(CAST_DIR, "G03_01_CoLan.jpg")),
        ("CH-2: Ông Khải (G03_06 Mới)", os.path.join(CAST_DIR, "G03_06_OngKhai.jpg")),
        ("CH-3: Sơn (G03_07 Mới)", os.path.join(CAST_DIR, "G03_07_Son.jpg")),
        ("CH-4: An (G03_08 Mới)", os.path.join(CAST_DIR, "G03_08_An.jpg")),
        ("BO-1: Phòng Chủ tịch Cô Lan", SET_JPGS["V3_BO1_PhongChuTichCoLan"]),
    ]),
    "V04": ("Mẹ quê ngàn cây số tìm con gái", [
        ("CH-1: Tú (G03_02)", os.path.join(CAST_DIR, "G03_02_Tu.jpg")),
        ("CH-2: Lam (G03_03)", os.path.join(CAST_DIR, "G03_03_Lam.jpg")),
        ("CH-3: Bà Sen (G03_05 Mới)", os.path.join(CAST_DIR, "G03_05_BaSen.jpg")),
        ("BO-1: Cổng & Sảnh nhà Tú", SET_JPGS["V4_BO1_CongSanhNhaTu"]),
    ]),
    "V05": ("Đòi 2 tỷ sính lễ trước cổng cưới", [
        ("CH-1: Chú rể Quân (G04_05)", os.path.join(CAST_DIR, "G04_05_Quan.jpg")),
        ("CH-2: Cô dâu Kiều (G04_06)", os.path.join(CAST_DIR, "G04_06_Kieu.jpg")),
        ("CH-3: Phù dâu Nhung (G05_05c)", os.path.join(CAST_DIR, "G05_05c_NhungPhuDau.jpg")),
        ("BO-1: Sân & Sảnh cưới nhà Quân", SET_JPGS["V5_BO1_CongCuoiNhaQuan"]),
    ]),
}

for ep_k, (ep_t, ep_items) in ASSET_DEFS.items():
    make_asset_board(ep_k, ep_t, ep_items)

# 3. Helper to build structured `phim-ai-flow-prompt` compliant prompts (max 3 refs per scene, exact @name mention once)
R = {
    # Characters (distinct short names so Flow asset picker searches cleanly with 0 collisions!)
    "baman": (os.path.join(CAST_DIR, "G05_01_BaMan.jpg"), "k4_baman.jpg"),
    "hieu":  (os.path.join(CAST_DIR, "G05_02_Hieu.jpg"),  "k4_hieu.jpg"),
    "trang": (os.path.join(CAST_DIR, "G05_03_Trang.jpg"), "k4_trang.jpg"),
    "khoi":  (os.path.join(CAST_DIR, "G05_06_Khoi.jpg"),  "k4_khoi.jpg"),
    "my":    (os.path.join(CAST_DIR, "G05_07_My.jpg"),    "k4_my.jpg"),

    "ongtan":(os.path.join(CAST_DIR, "G01_02_OngTan.jpg"),"k4_ongtan.jpg"),
    "thao":  (os.path.join(CAST_DIR, "G01_05a_Thao.jpg"), "k4_thao.jpg"),
    "tuan":  (os.path.join(CAST_DIR, "G01_04b_Tuan.jpg"), "k4_tuan.jpg"),

    "colan": (os.path.join(CAST_DIR, "G03_01_CoLan.jpg"), "k4_colan.jpg"),
    "khai":  (os.path.join(CAST_DIR, "G03_06_OngKhai.jpg"),"k4_khai.jpg"),
    "son":   (os.path.join(CAST_DIR, "G03_07_Son.jpg"),   "k4_son.jpg"),
    "an":    (os.path.join(CAST_DIR, "G03_08_An.jpg"),    "k4_an.jpg"),

    "tu":    (os.path.join(CAST_DIR, "G03_02_Tu.jpg"),    "k4_tu.jpg"),
    "lam":   (os.path.join(CAST_DIR, "G03_03_Lam.jpg"),   "k4_lam.jpg"),
    "basen": (os.path.join(CAST_DIR, "G03_05_BaSen.jpg"), "k4_basen.jpg"),

    "quan":  (os.path.join(CAST_DIR, "G04_05_Quan.jpg"),  "k4_quan.jpg"),
    "kieu":  (os.path.join(CAST_DIR, "G04_06_Kieu.jpg"),  "k4_kieu.jpg"),
    "nhung": (os.path.join(CAST_DIR, "G05_05c_NhungPhuDau.jpg"), "k4_nhung.jpg"),

    # Sets (BO-*)
    "v1bo1": (SET_JPGS["V1_BO1_NhaKhoi"],           "set_v1bo1.jpg"),
    "v1bo2": (SET_JPGS["V1_BO2_CanHoHieu"],         "set_v1bo2.jpg"),
    "v2bo1": (SET_JPGS["V2_BO1_PhongKhachOngTan"],  "set_v2bo1.jpg"),
    "v3bo1": (SET_JPGS["V3_BO1_PhongChuTichCoLan"], "set_v3bo1.jpg"),
    "v4bo1": (SET_JPGS["V4_BO1_CongSanhNhaTu"],     "set_v4bo1.jpg"),
    "v5bo1": (SET_JPGS["V5_BO1_CongCuoiNhaQuan"],   "set_v5bo1.jpg"),
}

def p_scene(sec, rl, set_key, char_keys, spatial, cam, action, speaker_desc, line_v1, line_v2, line_v3):
    """Generates 3 safety-hardened prompt variants following `phim-ai-flow-prompt` skill (1 scene = 1 seamless take, close-up dominant, exact @mention once)."""
    set_name = R[set_key][1]
    spatial_fixed = re.sub(r"@(k4_[a-z0-9_]+)(?!\.jpg)", r"@\1.jpg", spatial)
    all_keys = [set_key] + list(char_keys)
    assert len(all_keys) <= 3, f"Flow max 3 refs exceeded: {all_keys}"
    refs_out = [{"path": R[k][0], "name": R[k][1]} for k in all_keys]

    def fmt(line_txt, style_prefix):
        body = (
            f"{style_prefix} {sec} giây, photorealistic live-action diễn viên người lớn trưởng thành (26-58 tuổi), {rl}. "
            f"BỐI CẢNH: tại @{set_name} giữ nguyên 100% ánh sáng trong trẻo và hậu cảnh trang nhã theo ảnh tham chiếu. "
            f"CHỐT KHÔNG GIAN & CAMERA: {cam} {spatial_fixed} "
            f"DIỄN BIẾN: {action} "
            f"THOẠI TRỰC TIẾP: {speaker_desc} nói tiếng Việt rõ chữ khớp khẩu hình tự nhiên: \"{line_txt}\" "
            f"YÊU CẦU: Giữ nguyên 100% gương mặt và trang phục nhân vật người lớn tham chiếu, một cảnh liền mạch không cắt shot, không nhạc nền, không phụ đề, không chữ trên màn hình, không logo góc."
        )
        # Verify each ref name appears with @ at least once
        for rk in all_keys:
            rn = R[rk][1]
            assert f"@{rn}" in body, f"Missing @{rn} in prompt: {body}"
        return body

    return refs_out, [
        fmt(line_v1, "Tạo video"),
        fmt(line_v2, "Video điện ảnh"),
        fmt(line_v3, "Cảnh quay liền mạch"),
    ]

def build_all_episodes(ratio):
    rl = "khung dọc 9:16" if ratio == "9:16" else "khung ngang 16:9"
    r_folder = "raw_9x16" if ratio == "9:16" else "raw_16x9"
    episodes = {}

    # ==================== EPISODE 1 (V01: Mẹ chỉ có một, vợ chọn đi - 9 scenes) ====================
    episodes["v01"] = [
        ("s01", 6, *p_scene(
            6, rl, "v1bo1", ["my", "baman"],
            "Phía bên phải @k4_my đứng khoanh tay liếc xéo xuống phía bên trái nơi @k4_baman ngồi khép nép cúi đầu buồn bã.",
            "Trung cận một cảnh liền mạch, máy tĩnh.",
            "Cô con dâu thái độ hách dịch hất mặt chì chiết mẹ chồng già yếu.",
            "Cô con dâu phía phải",
            "Lương hưu của bà cạn sạch rồi, ngày tôi cho ăn một bữa cơm là phước lắm rồi còn đòi hỏi gì nữa!",
            "Tiền lương hưu bà hết sạch rồi, mỗi ngày tôi nấu cho một bữa là tốt lắm rồi bà còn đòi gì nữa!",
            "Giờ bà làm gì còn tiền hưu, ngày có một chén cơm ăn là may lắm rồi đừng đòi hỏi thêm!"
        )),
        ("s02", 6, *p_scene(
            6, rl, "v1bo1", ["hieu", "khoi"],
            "Bên trái @k4_hieu đứng nghiêm nghị nhìn thẳng sang @k4_khoi đang đứng lúng túng bên phải (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh hai anh em từ ngực trở lên, máy cố định.",
            "Người anh cả nhíu mày giận dữ chất vấn cậu em trai nhu nhược.",
            "Người anh trai mặc áo đen bên trái",
            "Khôi! Mày để vợ mày ăn nói hỗn hào với mẹ ruột mình như vậy mà mày đứng trơ mắt nhìn được hả?!",
            "Khôi! Sao mày để vợ mày nặng lời với mẹ ruột của anh em mình như vậy mà không nói một tiếng hả?!",
            "Mày nghe rõ chưa Khôi?! Vợ mày đối xử tệ bạc với mẹ mình vậy mà mày vẫn làm ngơ được sao?!"
        )),
        ("s03", 6, *p_scene(
            6, rl, "v1bo1", ["khoi"],
            "Cận mặt @k4_khoi đứng phía bên phải nhìn sang trái (hai tay để dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Cậu em trai chột dạ đảo mắt né tránh rồi gạt ngang bênh vợ.",
            "Cậu em trai",
            "Chuyện nhà em anh đừng xía vô! Mẹ già bệnh tật tốn kém đủ thứ, anh thương quá thì tự rước về mà nuôi!",
            "Anh đừng xen vào chuyện gia đình em! Mẹ giờ đau ốm tốn tiền lắm, anh giỏi thì tự đón mẹ về mà lo!",
            "Việc riêng nhà em anh khỏi lo! Chăm người già bệnh tật cực lắm, anh xót mẹ thì đón về nhà anh đi!"
        )),
        ("s04", 6, *p_scene(
            6, rl, "v1bo1", ["hieu", "baman"],
            "Bên trái @k4_hieu vòng tay đỡ vai @k4_baman rưng rưng nước mắt, cả hai nhìn gắt sang phải rồi quay người bước đi.",
            "Trung cận từ thắt lưng trở lên, máy lia nhẹ theo bước chân.",
            "Người anh cả dứt khoát dìu mẹ già rời đi trong niềm đau xót nhưng kiên quyết.",
            "Người anh cả mặc áo đen",
            "Được! Ngay hôm nay tao rước mẹ về phụng dưỡng! Từ giờ coi như tao không có người em vô tâm như mày!",
            "Tốt thôi! Hôm nay tao đón mẹ về nhà tao chăm sóc! Từ nay tao chấm dứt tình anh em với mày!",
            "Được lắm! Để tao đưa mẹ về nhà tao lo! Từ giây phút này coi như tao không còn người em như mày nữa!"
        )),
        ("s05", 6, *p_scene(
            6, rl, "v1bo2", ["trang", "baman"],
            "Phía bên phải @k4_trang vừa đi làm về nhăn mặt khó chịu liếc nhìn sang @k4_baman ngồi rụt rè mép ghế bên trái.",
            "Trung cận một cảnh liền mạch, máy cố định.",
            "Cô vợ trẻ tỏ thái độ chê bai ra mặt khi thấy mẹ chồng ở quê lên ở lại.",
            "Cô vợ trẻ mặc áo trắng bên phải",
            "Ủa sao tự nhiên rước bà cụ ở quê lên đây? Sáng mai khám xong đưa bà về liền nha, em không chịu cảnh phiền phức đâu!",
            "Sao anh lại đón mẹ ở quê lên ngủ lại đây? Mai khám bệnh xong phải đưa bà về ngay, một đêm em cũng thấy phiền!",
            "Nhà đang yên tĩnh sao lại rước mẹ anh lên đây? Sáng mai khám xong trả bà về quê liền cho em nha!"
        )),
        ("s06", 6, *p_scene(
            6, rl, "v1bo2", ["hieu"],
            "Cận mặt @k4_hieu đứng phía bên trái nhìn nghiêm túc sang phải (hai tay để dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Người chồng nén cơn giận, giọng trầm đanh giải thích rõ ràng với vợ.",
            "Người chồng",
            "Đó là mẹ ruột tần tảo nuôi anh khôn lớn đó Trang! Mẹ yếu rồi, từ nay mẹ sẽ ở lại đây để anh chăm sóc!",
            "Người đang ngồi kia là mẹ ruột sinh ra anh đó Trang! Mẹ đang bệnh, anh đón mẹ lên ở hẳn đây để tiện phụng dưỡng!",
            "Em ăn nói cho đàng hoàng, đó là mẹ ruột của anh! Mẹ tuổi cao sức yếu rồi, từ nay anh sẽ nuôi mẹ tại nhà này!"
        )),
        ("s07", 6, *p_scene(
            6, rl, "v1bo2", ["trang"],
            "Cận mặt @k4_trang đứng bên phải hất cao cằm thách thức nhìn sang trái (không đưa tay lên khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Cô vợ kiêu kỳ trừng mắt ra tối hậu thư bắt chồng phải chọn giữa mẹ và vợ.",
            "Cô vợ trẻ",
            "Em chốt thẳng một câu cuối khỏi bàn cãi: Một là mẹ anh bước ra khỏi nhà này, hai là em đi! Anh tự chọn đi!",
            "Lần cuối cùng em nói rõ cho anh chọn: Mẹ anh ở thì không có em, mẹ anh đi hoặc em đi, anh quyết đi!",
            "Khỏi nói dài dòng, giờ em cho anh chọn một trong hai: Đưa mẹ anh đi chỗ khác, hoặc chính em rời khỏi cái nhà này!"
        )),
        ("s08", 6, *p_scene(
            6, rl, "v1bo2", ["hieu"],
            "Cận mặt @k4_hieu đứng bên trái ánh mắt sắc lạnh kiên quyết nhìn thẳng sang phải (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Người chồng không một giây do dự, gằn giọng đáp trả dứt khoát làm vợ chết sững.",
            "Người chồng",
            "Khỏi cần dọa! Cửa nằm ngay đằng kia, cô dọn đồ bước ra khỏi nhà tôi ngay! Vợ sống bạc thì nghỉ, chứ mẹ trên đời chỉ có một thôi!",
            "Được! Cửa ngay trước mặt đó, cô xếp hành lý rời khỏi nhà tôi liền đi! Mẹ ruột cả đời chỉ có một, không ai thay thế được!",
            "Tôi chọn mẹ tôi! Cửa ở ngay kia, mời cô thu dọn đồ đạc đi ngay cho khuất mắt! Trên đời này mẹ chỉ có một mà thôi!"
        )),
        ("s09", 8, *p_scene(
            8, rl, "v1bo2", ["hieu", "baman"],
            "Tiền cảnh @k4_hieu đứng chính diện nhìn thẳng vào ống kính camera, phía sau bên trái mờ nhẹ @k4_baman ngồi ấm áp trên ghế (không thấy bàn tay).",
            "Cận cảnh từ vai trở lên hướng thẳng ống kính, máy tĩnh.",
            "Người con trai quay thẳng về phía khán giả tâm sự chân thành, ánh mắt điềm đạm.",
            "Người con trai nhìn thẳng ống kính",
            "Hôm nay vì bảo vệ mẹ già, tôi đã thẳng tay cắt đứt với em trai và tiễn luôn người vợ vô tâm ra khỏi cửa. Cô chú anh chị thấy tôi xử vậy là đúng hay sai? Cho tôi xin lời nhận xét công tâm bên dưới nhé!",
            "Mẹ vất vả cả đời nuôi tôi nên người, hôm nay vì chữ hiếu tôi chấp nhận mất lòng em ruột và chia tay vợ. Mọi người thấy tôi làm vậy có đúng không ạ? Hãy thả tim và bình luận bên dưới nhé!",
            "Vì bảo vệ mẹ ruột lúc ốm đau, tôi đã dứt khoát tiễn cô vợ ích kỷ ra khỏi nhà. Khán giả xem xong thấy tôi làm vậy là đúng hay quá nghiêm khắc, hãy để lại bình luận công tâm nhé!"
        )),
    ]

    # ==================== EPISODE 2 (V02: Bố chồng thu thẻ lương dạy con trai thương vợ - 9 scenes) ====================
    episodes["v02"] = [
        ("s01", 6, *p_scene(
            6, rl, "v2bo1", ["thao"],
            "Cận mặt người phụ nữ trưởng thành hai mươi tám tuổi @k4_thao đứng phía bên trái vẻ mặt hiền lành lễ phép nhìn sang phải (hai tay để dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Người con dâu trưởng thành lễ phép mở lời thưa chuyện với bố chồng về ngày sinh nhật mẹ ruột ở quê.",
            "Người con dâu trưởng thành",
            "Dạ thưa bố chồng… cuối tuần này mừng sinh nhật mẹ ruột con ở quê, bố cho vợ chồng con ứng tạm ba triệu mua hộp quà về thăm mẹ được không ạ?",
            "Thưa bố… sắp tới ngày mừng tuổi mới của mẹ đẻ con dưới quê rồi, con xin phép hỏi mượn bố ba triệu mua ít quà sức khỏe biếu mẹ được không ạ?",
            "Bố ơi… cuối tuần này sinh nhật bà thông gia dưới quê, con muốn mua hộp quà nhỏ về thăm mẹ mà trong người chưa sẵn tiền mặt, bố cho con ứng tạm nhé ạ?"
        )),
        ("s02", 5, *p_scene(
            5, rl, "v2bo1", ["ongtan"],
            "Cận mặt @k4_ongtan ngồi trên sofa phía bên phải nhìn điềm đạm sang trái (hai tay đặt dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Ông bố chồng nhíu nhẹ chân mày giả vờ hỏi nghiêm để dò xem cách chồng cô đối xử với vợ thế nào.",
            "Ông bố chồng",
            "Ủa sao lại hỏi mượn ba? Tiền lương thằng Tuấn làm ra mỗi tháng đâu, sao con không bảo chồng con đưa?",
            "Mượn tiền hả? Thế thằng Tuấn chồng con đâu, tiền nó kiếm hàng tháng sao con phải ngửa tay mượn ba?",
            "Chuyện quà cáp về ngoại sao con không lấy tiền của thằng Tuấn, vợ chồng sống với nhau tiền bạc nó giữ hết hả?"
        )),
        ("s03", 6, *p_scene(
            6, rl, "v2bo1", ["tuan", "thao"],
            "Trung cận @k4_tuan đứng bên phải cạnh bàn trà có mấy túi quà đỏ, nhìn lạnh nhạt sang @k4_thao đứng bên trái đang chưng hửng.",
            "Trung cận từ ngực trở lên, máy tĩnh.",
            "Anh chồng vô tâm gạt phắt sự mừng hụt của vợ, tuyên bố quà xịn chỉ mua cho bố đẻ mình.",
            "Anh chồng sơ mi trắng bên phải",
            "Ai bảo em là anh mua quà đi thăm mẹ vợ? Mấy hộp yến sào cao cấp này là anh mua bồi bổ cho ba anh đó!",
            "Thăm mẹ em hồi nào? Đống đồ bổ đắt tiền này là anh sắm riêng để biếu ba ruột anh, em đừng có tưởng bở!",
            "Em nghĩ đi đâu vậy? Mấy phần quà sức khỏe thượng hạng này anh mua tặng ba anh chứ có phải cho nhà ngoại đâu!"
        )),
        ("s04", 5, *p_scene(
            5, rl, "v2bo1", ["tuan"],
            "Cận mặt @k4_tuan đứng bên trái tươi cười nịnh nọt nhìn sang phía bố ở bên phải (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Anh con trai hớn hở khoe công hiếu thảo với bố ruột mà không hề biết bố đang nổi giận.",
            "Anh con trai",
            "Ba coi con trai ba có hiếu chưa nè, tiền con làm ra lúc nào cũng chỉ ưu tiên chăm lo cho ba đầu tiên thôi đó!",
            "Ba thấy con chu đáo không, đi làm có tiền là con sắm toàn đồ tốt nhất mang về biếu ba liền đó ạ!",
            "Ba cứ yên tâm bồi bổ nha, con trai ba kiếm tiền trước hết là để báo hiếu cho ba mà!"
        )),
        ("s05", 7, *p_scene(
            7, rl, "v2bo1", ["ongtan"],
            "Cận mặt @k4_ongtan ngồi bên phải nghiêm mặt quắc mắt nhìn thẳng sang trái (không thấy bàn tay).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Ông bố chồng đanh mặt lại, gằn giọng chấn chỉnh thói ích kỷ của con trai ngay lập tức.",
            "Ông bố chồng",
            "Mày bớt nịnh tao lại đi Tuấn! Nhà mình cưới con Thảo về làm dâu đàng hoàng, chứ ba má vợ có bán đứt con gái cho mày đâu mà lễ nghĩa bên ngoại mày ngó lơ?!",
            "Thôi ngay kiểu nịnh đó đi! Mình rước vợ về làm người một nhà, chứ nhà ngoại người ta có bán đứt con gái đâu mà tới sinh nhật mẹ vợ mày không lo nổi một đồng?!",
            "Tao nghe mà chướng tai lắm Tuấn! Con gái người ta nuôi lớn gả về đây làm vợ mày, sao mày chỉ biết nịnh ba ruột mà bỏ mặc bên nhà ngoại hả?!"
        )),
        ("s06", 7, *p_scene(
            7, rl, "v2bo1", ["ongtan"],
            "Cận mặt @k4_ongtan ngồi bên phải ánh mắt uy nghiêm đanh thép nhìn sang trái nói dõng dạc (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Ông bố chồng kể rõ từng công lao vất vả của con dâu khiến con trai phải cúi mặt xấu hổ.",
            "Ông bố chồng",
            "Cơm ngon ba bữa vợ mày nấu, nhà cửa sạch tươm ba trăm sáu mươi lăm ngày một tay nó quán xuyến không lương! Vậy mà mua quà cho mẹ đẻ nó cũng phải đi mượn ba triệu là sao?!",
            "Việc nhà từ trên xuống dưới một tay vợ mày lo trọn ba trăm sáu lăm ngày không nghỉ! Làm chồng kiểu gì mà để vợ về thăm mẹ ruột cũng phải rụt rè đi vay từng đồng hả?!",
            "Mày thuê giúp việc cả năm trả bao nhiêu tiền, trong khi vợ mày tần tảo lo cho cái nhà này chẳng than nửa lời, vậy mà mày khóa chặt túi tiền để vợ thiệt thòi thế hả?!"
        )),
        ("s07", 7, *p_scene(
            7, rl, "v2bo1", ["tuan", "ongtan"],
            "Bên trái @k4_tuan ngơ ngác phân bua nhỏ, bên phải @k4_ongtan nghiêm nghị nhìn thẳng bắt con trai giao thẻ lương (khung ngực trở lên, không giơ tay rối).",
            "Trung cận hai cha con, máy cố định.",
            "Anh con trai vừa hé miệng nói mình mới là con ruột liền bị bố chồng dập tắt và thu thẻ lương trao quyền cho con dâu.",
            "Ông bố chồng bên phải",
            "Ai là người ngoài?! Mai mốt ba khuất núi, người bầu bạn chăm lo cho mày tới già chính là vợ mày đó! Móc ngay thẻ lương ra nộp cho con Thảo giữ, tiêu gì xin phép vợ!",
            "Mày dám gọi vợ đầu ấp tay gối là người ngoài hả?! Đưa ngay cái thẻ lương đây giao cho con Thảo quản lý, từ nay mày tiêu tiền phải hỏi ý vợ nghe rõ chưa!",
            "Sống vô tâm với vợ thì nhà này sớm muộn cũng nát! Nộp ngay thẻ lương cho vợ mày giữ, từ giờ tài chính trong nhà để một tay con Thảo nắm hết!"
        )),
        ("s08", 7, *p_scene(
            7, rl, "v2bo1", ["ongtan", "thao"],
            "Bên phải @k4_ongtan nét mặt hiền từ ấm áp nhìn sang @k4_thao bên trái đang rưng rưng nước mắt xúc động biết ơn.",
            "Trung cận hai bố con trên nền phòng khách sáng ấm, máy tĩnh.",
            "Ông bố chồng ân cần dặn dò và bảo các con mang toàn bộ quà quý về biếu bà thông gia.",
            "Ông bố chồng",
            "Hiếu với cha mẹ ruột là bản năng, còn hiếu với cha mẹ vợ mới là trách nhiệm người đàn ông! Hai đứa gói hết mấy túi quà bổ này về quê mừng sinh nhật mẹ hai ngày cho ba!",
            "Chúng ta là người một nhà mà con gái! Cầm lấy tiền mặt của ba với toàn bộ đống quà bổ trên bàn, bảo thằng Tuấn lái xe đưa con về quê chăm mẹ chơi vài hôm cho trọn hiếu!",
            "Con dâu đừng ngại, cha mẹ bên nào cũng là đấng sinh thành! Đem hết quà cáp xịn này về biếu bà thông gia, ở lại quê chơi thêm hai ngày cho mẹ con vui lòng nghe chưa!"
        )),
        ("s09", 8, *p_scene(
            8, rl, "v2bo1", ["ongtan"],
            "Cận mặt @k4_ongtan ở trung tâm khung hình mỉm cười điềm đạm phúc hậu nhìn thẳng ống kính camera (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh từ vai trở lên hướng thẳng ống kính, máy tĩnh.",
            "Ông bố chồng trò chuyện trực tiếp với khán giả bằng giọng trầm ấm thấu tình đạt lý.",
            "Ông bố chồng nhìn thẳng ống kính",
            "Con trai mình vô tâm là làm cha phải chấn chỉnh ngay, chứ để con dâu tủi thân tội nghiệp lắm. Cô chú anh chị thấy tôi xử lý và đối đãi với bên thông gia vậy đã ổn thỏa chưa? Bình luận cho tôi biết nhé!",
            "Làm cha mẹ chồng thương con dâu thật lòng thì gia đạo mới êm ấm bền lâu được. Mọi người thấy cách tôi dạy lại con trai và cư xử với nhà ngoại như vậy đã hợp lý chưa ạ? Nhớ thả tim và bình luận nhé!",
            "Vừa rồi tôi đã thu thẻ lương giao cho con dâu và giục hai đứa mang quà về mừng thọ bà thông gia. Khán giả thấy bố chồng xử lý vậy được mấy điểm, hãy để lại ý kiến bên dưới nha!"
        )),
    ]

    # ==================== EPISODE 3 (V03: Bánh đúc có xương? Mẹ kế Chủ tịch làm chủ cho con chồng - 9 scenes) ====================
    episodes["v03"] = [
        ("s01", 6, *p_scene(
            6, rl, "v3bo1", ["son", "an"],
            "Bên trái @k4_son mặc áo lao động bạc màu đứng che chở cạnh em gái @k4_an xanh xao yếu ớt bên phải, cả hai nhìn khẩn thiết về phía trước.",
            "Trung cận từ ngực trở lên (hai tay để thấp ngoài khung hình), máy tĩnh.",
            "Hai anh em nghèo khổ ánh mắt rưng rưng nhưng đàng hoàng lễ phép trình bày lý do tìm bố ruột.",
            "Người anh trai mặc áo xám bên trái",
            "Thưa bà Chủ tịch… hai anh em cháu không tới nhận vơ xin tiền đâu ạ, bác Khải thiệt sự là ba ruột thất lạc mười lăm năm của tụi cháu!",
            "Dạ thưa bác… tụi cháu đi làm thuê chân chính chứ không dám lừa gạt ai, bác Khải đúng là ba ruột của hai anh em cháu suốt mười lăm năm chưa gặp!",
            "Xin bác tin tụi cháu một lời… cực chẳng đã vì em gái cháu bệnh nặng quá nên hôm nay cháu mới đánh liều tìm tới đây gặp ba ruột ạ!"
        )),
        ("s02", 6, *p_scene(
            6, rl, "v3bo1", ["colan"],
            "Cận mặt @k4_colan đứng phía bên phải phong thái quý phái điềm tĩnh nhìn ấm áp sang trái (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Nữ chủ tịch gật đầu nhẹ, ánh mắt nhân hậu và quyết đoán trấn an hai đứa trẻ.",
            "Nữ chủ tịch",
            "Nhìn nét mặt hai đứa là bác nhận ra hình bóng chồng bác hồi trẻ rồi! Để bác gọi ông ấy về ngay, nếu đúng máu mủ thì chính bác sẽ đứng ra làm chủ cho hai con!",
            "Hai cháu cứ bình tĩnh ngồi xuống đây với bác! Bác vừa gọi điện báo ông Khải về rồi, đúng là giọt máu của chồng bác thì không ai được phép để hai đứa chịu thiệt!",
            "Bác tin lời hai đứa! Chồng bác đau đáu tìm các con bao năm nay, hai cháu cứ yên tâm ở đây chờ ba về nói rõ đầu đuôi cho bác nghe!"
        )),
        ("s03", 7, *p_scene(
            7, rl, "v3bo1", ["khai", "son"],
            "Bên phải @k4_khai mắt đỏ hoe xúc động nhìn chằm chằm sang con trai @k4_son đứng bên trái (khung cận vai, không giơ tay che mặt).",
            "Trung cận hai cha con, máy cố định.",
            "Người cha trung niên nghẹn ngào rơi nước mắt khi thấy hai con ruột tiều tụy khổ sở sau nhiều năm xa cách.",
            "Người cha mặc vest xám bên phải",
            "Trời ơi thằng Sơn, cái An của ba đây rồi! Sao con phải bỏ đại học đi phụ hồ lấm lem, còn em gái lại xanh xao bệnh tật tới mức này hả con?!",
            "Đúng là hai đứa con ruột ba tìm kiếm bấy lâu nay rồi! Sao áo quần con sờn cũ bụi bặm, còn con bé An lại tiều tụy yếu ớt thế này hả Sơn?!",
            "Sơn ơi, An ơi! Nhìn hai anh em con gầy gò khổ cực thế này mà lòng ba đau như cắt, suốt những năm qua có chuyện gì xảy ra vậy con?!"
        )),
        ("s04", 7, *p_scene(
            7, rl, "v3bo1", ["an"],
            "Cận mặt cô gái trưởng thành hai mươi hai tuổi @k4_an đứng phía bên trái nước mắt lăn dài nghẹn ngào nhìn sang phải (không thấy bàn tay).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Người con gái trưởng thành xúc động kể lại hoàn cảnh hai anh em tự lập vất vả nhiều năm qua.",
            "Người con gái mặc áo len hồng",
            "Từ ngày mẹ lập gia đình mới là hai anh em con phải dọn ra ngoài tự bươn chải kiếm sống… Anh Sơn đi làm công trình lo cho con, nay bệnh tim con trở nặng hết tiền viện phí rồi ba ơi!",
            "Bao năm nay anh Sơn phải gác việc học đại học đi làm thợ hồ nuôi con… Giờ bác sĩ báo tim con phải phẫu thuật sớm mà hai anh em không còn khả năng xoay xở nữa ạ!",
            "Mẹ có gia đình riêng nên hai anh em con tự nương tựa nhau sống ở phòng trọ suốt mấy năm qua… Nay con bị bệnh tim nặng quá anh Sơn mới đánh liều tìm tới ba ạ!"
        )),
        ("s05", 6, *p_scene(
            6, rl, "v3bo1", ["khai"],
            "Cận mặt @k4_khai đứng bên phải mở to mắt sững sờ và phẫn nộ nhìn sang trái (hai tay để dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Người cha bàng hoàng tiết lộ khoản tiền chu cấp khổng lồ suốt mười lăm năm bị vợ cũ biển thủ.",
            "Người cha",
            "Cái gì?! Suốt mười lăm năm qua tháng nào ba cũng chuyển đều đặn mười lăm triệu vào tài khoản mẹ con để nuôi hai đứa mà! Bà ấy giữ sạch không đưa con đồng nào sao?!",
            "Trời đất ơi! Tháng nào ba cũng gửi đủ mười lăm triệu tiền chu cấp nuôi hai anh em suốt mười lăm năm trời, chẳng lẽ mẹ với dượng tụi con nuốt trọn hết rồi sao?!",
            "Sao lại nhẫn tâm tới mức đó được! Suốt mười lăm năm ba chưa từng trễ một tháng tiền chu cấp nào cho hai đứa, vậy mà các con phải nhịn đói đi phụ hồ sao?!"
        )),
        ("s06", 6, *p_scene(
            6, rl, "v3bo1", ["son"],
            "Cận mặt @k4_son đứng bên trái mím môi kìm nước mắt, cúi đầu lễ phép nhìn sang phải (không thấy bàn tay).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Chàng trai nghèo đầy lòng tự trọng sợ ba khó xử với người vợ hiện tại nên xin phép cáo từ.",
            "Người anh trai",
            "Thấy ba mạnh khỏe là anh em con mãn nguyện rồi ạ! Con không dám nhận tiền làm ba khó xử với bác gái đâu, tụi con xin phép về tự xoay xở viện phí ạ!",
            "Dạ thôi ba ơi, ba còn gia đình riêng của ba nữa! Dù cực khổ mấy con cũng ráng làm lụng lo cho em chứ không để ba phải khó xử vì tụi con đâu, con chào ba!",
            "Biết lòng ba vẫn thương tụi con là đủ ấm lòng rồi ạ! Hai anh em con xin phép ra về tìm chỗ khác vay mượn, không dám làm phiền bác gái với ba đâu ạ!"
        )),
        ("s07", 7, *p_scene(
            7, rl, "v3bo1", ["colan"],
            "Cận mặt @k4_colan bước lên phía bên phải ánh mắt nghiêm nghị nhưng chan chứa yêu thương nhìn sang trái (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Bà mẹ kế Chủ tịch dõng dạc ngăn hai đứa trẻ lại, công bố đã cho luật sư đòi công bằng và lo trọn ca mổ tim.",
            "Nữ chủ tịch",
            "Hai đứa đứng lại hết cho bác! Bác vừa chỉ đạo luật sư khởi kiện đòi lại trọn vẹn tiền chu cấp mười lăm năm, và đặt xong phòng mổ tim tốt nhất cho cái An rồi!",
            "Không đi đâu hết! Bác đã gọi luật sư lập hồ sơ truy thu không thiếu một đồng tiền chu cấp mười lăm năm qua, chiều nay đưa bé An nhập viện phòng đặc biệt mổ ngay!",
            "Chưa ăn chén cháo yến cho ấm bụng mà đòi đi đâu! Bác vừa bảo luật sư đòi lại công bằng mười lăm năm cho hai đứa và lo xong toàn bộ chi phí mổ tim cho An rồi!"
        )),
        ("s08", 6, *p_scene(
            6, rl, "v3bo1", ["colan", "khai"],
            "Bên phải @k4_colan mỉm cười hiền hậu ấm áp, bên trái @k4_khai rơi nước mắt cảm kích nhìn vợ (khung cận vai, không thấy bàn tay).",
            "Trung cận hai vợ chồng Chủ tịch nhìn sang hai con, máy tĩnh.",
            "Bà mẹ kế nhân hậu mở rộng vòng tay đón hai con riêng của chồng về chung sống một nhà.",
            "Nữ chủ tịch bên phải",
            "Người đời hay bảo bánh đúc có xương, nhưng con của chồng cũng là khúc ruột của bác! Mổ tim khỏe lại rồi hai anh em dọn hẳn về nhà mình ở cho ấm cửa ấm nhà!",
            "Tuổi xế chiều tìm lại được hai đứa là phúc phần lớn nhất của ba và bác! Từ nay Sơn đi học đại học lại, hai con dọn về sống chung với vợ chồng bác luôn nghe chưa!",
            "Nhà mình rộng mà vắng tiếng cười lâu rồi, từ hôm nay Sơn với An chính thức là con của bác, mổ xong hai đứa về thẳng nhà mình để ba và bác bù đắp!"
        )),
        ("s09", 7, *p_scene(
            7, rl, "v3bo1", ["colan"],
            "Cận mặt @k4_colan đứng chính diện mỉm cười đoan trang nhân hậu nhìn thẳng ống kính camera (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh từ vai trở lên hướng thẳng ống kính, máy tĩnh.",
            "Bà mẹ kế Chủ tịch trò chuyện trực tiếp cùng khán giả bằng giọng nhẹ nhàng sâu sắc.",
            "Nữ chủ tịch nhìn thẳng ống kính",
            "Đã thương chồng thì phải thương luôn cả giọt máu của chồng… Cô chú anh chị thấy phận làm mẹ kế như tôi đứng ra lo liệu vậy đã trọn tình trọn nghĩa chưa ạ? Nhớ thả tim và bình luận chia sẻ cùng tôi nhé!",
            "Trẻ con không có lỗi, hôm nay tôi vừa nhờ luật sư đòi lại công bằng vừa đón hai con riêng của chồng về chăm sóc. Mọi người thấy tôi làm vậy có đúng đắn không ạ? Hãy bình luận bên dưới nhé!",
            "Ai bảo bánh đúc nào cũng có xương phải không cả nhà? Khán giả xem xong thấy cách cư xử của người mẹ kế như tôi đã ấm lòng chưa, cho tôi xin một lượt thích và bình luận nha!"
        )),
    ]

    # ==================== EPISODE 4 (V04: Mẹ quê vượt ngàn cây số tìm con gái, con rể xử đẹp - 8 scenes) ====================
    episodes["v04"] = [
        ("s01", 6, *p_scene(
            6, rl, "v4bo1", ["basen", "tu"],
            "Bên trái trước cổng @k4_basen đeo tay nải quê rụt rè hỏi thăm @k4_tu ăn mặc lịch sự đứng bên phải.",
            "Trung cận hai người từ ngực trở lên, máy tĩnh.",
            "Bà mẹ già khắc khổ vượt đường xa ba ngày ba đêm lễ phép hỏi thăm địa chỉ nhà con gái.",
            "Bà mẹ quê bên trái",
            "Cậu ơi làm ơn cho bác hỏi thăm chút… bác đi xe đò ba ngày ba đêm từ quê vô tới đây, nhà này có phải nhà con bé Lam không cậu?",
            "Cháu ơi xem giúp bác cái địa chỉ này với… bác ở tít ngoài quê lặn lội hàng ngàn cây số vào đây tìm con gái tên Lam có đúng nhà này không cháu?",
            "Cậu làm phước chỉ giùm bác… bác từ dưới quê bắt xe suốt ba ngày ròng rã lên phố, ở đây có ai tên là Lam không hả cậu?"
        )),
        ("s02", 6, *p_scene(
            6, rl, "v4bo1", ["tu"],
            "Cận mặt @k4_tu đứng bên phải mở to mắt ngạc nhiên xen lẫn khó hiểu nhìn sang trái (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Chàng rể trẻ sững sờ khi phát hiện sự thật trái ngược hoàn toàn với lời vợ từng nói ngày cưới.",
            "Chàng rể trẻ",
            "Ủa Lam chính là vợ cháu mà bác! Vậy cháu là con rể bác rồi… nhưng sao hồi đám cưới cô ấy lại bảo với nhà cháu là mồ côi không còn cha mẹ?!",
            "Dạ đúng địa chỉ nhà cháu rồi, Lam là vợ cháu đây ạ! Mà lạ thiệt, ngày cưới vợ cháu khăng khăng nói mình lớn lên một mình không còn bố mẹ ở quê cơ mà?!",
            "Trời ơi Lam là vợ cháu đó bác! Sao chuyện động trời vậy mà cô ấy giấu kín, lúc cưới lại nói với gia đình cháu là không còn người thân nào ở quê?!"
        )),
        ("s03", 7, *p_scene(
            7, rl, "v4bo1", ["basen"],
            "Cận mặt @k4_basen đứng bên trái cúi mặt rưng rưng nước mắt nghẹn ngào nhìn sang phải (không thấy bàn tay).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Người mẹ già chạnh lòng xót xa đoán ra lý do con gái xấu hổ chối bỏ cha mẹ nghèo.",
            "Bà mẹ quê",
            "Tội nghiệp… học xong đại học nó lấy chồng thành phố giàu sang, chắc sợ nhà chồng chê cười cha mẹ quê mùa nghèo khổ nên mới đành lòng nói dối là mồ côi…",
            "Khổ thân con bé… chắc thấy gia đình bên cháu bề thế giàu có quá, nó mặc cảm cảnh nhà quê nghèo rớt mồng tơi nên mới không dám nhận bố mẹ ruột đó cháu ơi…",
            "Nghe cháu nói mà bác xót hết ruột gan… chỉ tại bố mẹ ở quê nghèo khó lam lũ, con bé sợ mất mặt với nhà chồng nên mới nói dối mình không còn cha mẹ…"
        )),
        ("s04", 6, *p_scene(
            6, rl, "v4bo1", ["tu"],
            "Cận mặt @k4_tu đứng bên phải vẻ mặt nghiêm nghị bất bình gọi điện chất vấn vợ (không thấy bàn tay, nhìn thẳng hơi chếch trái).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Chàng rể thẳng thắn nghiêm giọng gọi vợ về nhà ngay lập tức để đối diện với mẹ đẻ.",
            "Chàng rể trẻ",
            "Alo Lam hả, em về nhà ngay lập tức cho anh! Mẹ ruột của em tên Sen đang đứng khóc ngay trước cổng nhà mình đây này, sao em dám giấu anh chuyện lớn vậy hả?!",
            "Lam! Em bỏ hết việc chạy về nhà ngay cho anh! Mẹ Sen từ quê lặn lội ba ngày đêm đang đứng trước cửa đây, tại sao em dám nói dối anh là không còn bố mẹ hả?!",
            "Em về tới cổng ngay bây giờ cho anh Lam! Đấng sinh thành bằng xương bằng thịt đang đứng trước mặt anh đây mà ngày cưới em dám bảo mình mồ côi là sao?!"
        )),
        ("s05", 6, *p_scene(
            6, rl, "v4bo1", ["lam"],
            "Cận mặt @k4_lam đứng ở sảnh phía bên phải bật khóc hối hận cúi đầu nhìn sang trái (hai tay để dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt từ vai trở lên, máy tĩnh.",
            "Cô vợ trẻ vừa chạy về tới nhà đã òa khóc nức nở nhận lỗi với mẹ già và chồng.",
            "Cô vợ trẻ",
            "Mẹ ơi… anh Tú ơi cho em xin lỗi! Chỉ tại ngày xưa em tự ti sợ nhà chồng coi thường gốc gác nghèo khó nên em mới trót dại giấu giếm anh thôi ạ!",
            "Con có lỗi với mẹ nhiều lắm mẹ ơi… Anh Tú tha lỗi cho em, em sợ anh biết nhà em nghèo khổ dưới quê sẽ chê bai nên mới không dám nói thật!",
            "Mẹ ơi con bất hiếu quá… Anh ơi em sai thật rồi, chỉ vì chút sĩ diện hão sợ mất mặt trước họ hàng nhà chồng mà em nói lời có tội với bố mẹ!"
        )),
        ("s06", 7, *p_scene(
            7, rl, "v4bo1", ["basen"],
            "Cận mặt @k4_basen đứng bên trái rơi nước mắt hiền từ thương con, giọng run run nhìn sang phải (không thấy bàn tay).",
            "Cận cảnh gương mặt từ vai trở lên, máy cố định.",
            "Người mẹ già không một lời trách móc con gái, chỉ nghẹn ngào báo tin ông bố ở quê đổ bệnh nặng vì nhớ con.",
            "Bà mẹ quê",
            "Hơn mười năm con biền biệt chưa về thăm nhà, dưới quê bố con nhớ con quá hóa đổ bệnh nằm liệt giường… mẹ vay mượn khắp nơi hết cách rồi mới tìm lên đây…",
            "Mẹ không giận con đâu Lam ơi… chỉ tại ở quê bố con thương nhớ con gái tới mức ngã bệnh nặng, mẹ chạy vạy không đủ tiền viện phí mới liều đi tìm con…",
            "Thấy con sống sung túc vầy là mẹ mừng rồi… ngặt nỗi dưới quê ông nhà ốm nặng nằm viện cả tháng nay, mẹ hết sạch tiền thuốc thang mới phải lên nhờ con…"
        )),
        ("s07", 7, *p_scene(
            7, rl, "v4bo1", ["tu", "basen"],
            "Bên phải @k4_tu ánh mắt chân thành lễ phép cúi đầu ấm áp trước @k4_basen đang xúc động rơi nước mắt bên trái (khung ngực trở lên).",
            "Trung cận con rể và mẹ vợ trước sảnh nhà sáng rực, máy tĩnh.",
            "Chàng rể lập tức đổi cách xưng hô gọi Mẹ đầy trân trọng và nhận lo toàn bộ việc chạy chữa phụng dưỡng bố mẹ vợ.",
            "Chàng rể trẻ bên phải",
            "Từ giây phút này con xin phép gọi bác là Mẹ! Mẹ cầm thẻ ngân hàng của con lo thuốc thang tốt nhất cho bố, bố khỏe lại con đón cả bố mẹ lên đây phụng dưỡng trọn đời!",
            "Bố mẹ của Lam cũng chính là bố mẹ ruột của con! Toàn bộ viện phí của bố để con rể lo hết, xong xuôi con rước bố mẹ lên thành phố ở chung với tụi con cho sum vầy!",
            "Mẹ đừng lo lắng gì nữa hết, giờ chúng ta là người một nhà rồi! Mẹ vào nhà nghỉ ngơi đi, ngay mai con đưa vợ về quê lo chữa bệnh cho bố rồi đón hai cụ lên ở cùng luôn!"
        )),
        ("s08", 8, *p_scene(
            8, rl, "v4bo1", ["tu"],
            "Cận mặt @k4_tu đứng trước tiền sảnh sáng ấm mỉm cười đĩnh đạc nhìn thẳng vào ống kính camera (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh từ vai trở lên hướng thẳng ống kính, máy tĩnh.",
            "Chàng rể tốt bụng chia sẻ quan điểm sống trọng nghĩa tình trực tiếp với khán giả.",
            "Chàng rể nhìn thẳng ống kính",
            "Cha mẹ dù nghèo khổ lam lũ tới đâu cũng là đấng sinh thành không bao giờ được phép chối bỏ! Hôm nay tôi vừa chấn chỉnh lại vợ vừa rước mẹ vợ vào nhà chăm sóc, cả nhà thấy tôi xử vậy đã chuẩn chưa ạ?",
            "Vừa rồi tôi đã nghiêm khắc dạy lại vợ vì giấu mẹ nghèo dưới quê, đồng thời lo toàn bộ viện phí cho bố vợ. Cô chú anh chị thấy chàng rể này làm vậy đã hợp tình hợp lý chưa? Nhớ thả tim và bình luận nhé!",
            "Giàu sang mấy mà quên nguồn cội thì cũng chẳng đáng quý. Khán giả xem xong thấy cách tôi đón nhận và phụng dưỡng bố mẹ vợ nghèo như vậy đã hài lòng chưa, hãy bình luận bên dưới nha!"
        )),
    ]

    # ==================== EPISODE 5 (V05: Đòi 2 tỷ sính lễ ngay trước cổng cưới & cái kết quay xe - 8 scenes) ====================
    episodes["v05"] = [
        ("s01", 6, *p_scene(
            6, rl, "v5bo1", ["kieu"],
            "Cận mặt @k4_kieu mặc áo dài cưới trắng đội mấn vàng ngồi bên trái cạnh cửa xe hoa, hất mặt kiêu kỳ nhìn sang phải (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt cô dâu từ vai trở lên, máy tĩnh.",
            "Cô dâu trang điểm lộng lẫy nhưng thái độ thực dụng, lạnh lùng ra giá ngay lúc xe hoa vừa đỗ trước cổng nhà trai.",
            "Cô dâu áo dài trắng",
            "Khoan mở cửa rước dâu! Hai tỷ tiền sính lễ phát sinh chưa nổ tinh tinh vô tài khoản riêng của em thì hôm nay đừng hòng em bước chân xuống xe!",
            "Đứng yên đó đi anh! Chưa thấy chuyển khoản đủ hai tỷ tiền trao tay ngay trước cổng này thì miễn bàn chuyện bước chân vô nhà chồng nha!",
            "Em nói thẳng luôn cho nhanh, tiền sính lễ hai tỷ thêm ngay tại cửa xe còn chưa thấy đâu thì hôm nay khỏi xuống xe làm lễ gì hết!"
        )),
        ("s02", 6, *p_scene(
            6, rl, "v5bo1", ["quan"],
            "Cận mặt @k4_quan mặc áo dài cưới đen thêu vàng đứng bên phải sững sờ nhíu mày nhìn sang trái (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt chú rể từ vai trở lên, máy cố định.",
            "Chú rể bất ngờ nén cơn giận, cố gắng khuyên nhủ cô dâu giữ thể diện cho hai bên họ hàng đang chờ.",
            "Chú rể áo dài đen",
            "Em giỡn quá trớn rồi đó Kiều! Sính lễ năm trăm triệu với vàng cưới hai bên gia đình đã trao nhận xong xuôi hết rồi, quan khách hai họ đang đợi kín trong sảnh kìa!",
            "Sao tự nhiên tới trước cổng lại đòi thêm hai tỷ vô lý vậy Kiều?! Mọi lễ nghĩa nhà anh đã lo chu toàn hết rồi, em đừng làm loạn trước mặt bao nhiêu họ hàng nữa!",
            "Chuyện gì từ từ vô nhà nói, giờ giờ lành sắp qua mà khách khứa đang nhìn kìa Kiều, sao em lại đem tiền bạc ra làm khó nhà anh ngay trước cửa vậy?!"
        )),
        ("s03", 6, *p_scene(
            6, rl, "v5bo1", ["nhung"],
            "Cận mặt @k4_nhung mặc áo dài ren trắng đứng phía bên trái chắn trước xe hoa, nhướng mày đanh đá nhìn sang phải (không thấy bàn tay).",
            "Cận cảnh gương mặt cô bạn thân phù dâu từ vai trở lên, máy tĩnh.",
            "Cô bạn thân phù dâu chống lưng xúi giục, buông lời ngạo mạn ép giá chú rể.",
            "Cô bạn thân phù dâu",
            "Tôi nói cho anh nghe rõ nha, nhỏ bạn thân cực phẩm của tôi chịu gả vô nhà anh là phước ba đời rồi! Không chồng đủ hai tỷ ngay tại chỗ thì miễn bước xuống xe!",
            "Cưới được cô dâu xinh đẹp như bạn thân tôi là phúc đức lớn nhà anh đó! Mau xoay đủ hai tỷ chuyển khoản liền đi chứ đừng có đứng đó kỳ kèo mất thời gian!",
            "Đàn ông cưới vợ mà tiếc hai tỷ lẻ trước cổng sao coi được? Bạn tôi có giá của bạn tôi, chưa thấy tiền nổi trong tài khoản thì cửa xe này không mở đâu!"
        )),
        ("s04", 6, *p_scene(
            6, rl, "v5bo1", ["kieu"],
            "Cận mặt @k4_kieu ở phía bên trái nhếch môi tự đắc nhìn sang phải chắc mẩm chú rể sợ mất mặt sẽ phải chuyển tiền (không thấy bàn tay).",
            "Cận cảnh gương mặt cô dâu từ vai trở lên, máy cố định.",
            "Cô dâu vênh mặt thách thức ép chú rể vào thế bí ngay giờ làm lễ.",
            "Cô dâu",
            "Anh nghe rõ bạn thân em nói chưa? Con gái đi lấy chồng không thể tay trắng thiệt thòi được, một là chuyển ngay hai tỷ, hai là khỏi cưới xin gì hết!",
            "Đúng đó, giờ khách khứa nhà anh ngồi đầy trong kia rồi, anh sợ mất mặt họ hàng thì mau chuyển khoản đủ hai tỷ đây em mới chịu bước xuống!",
            "Em đếm từ một tới ba thôi nha, có hai tỷ tiền mặt làm vốn riêng thì em bước vô làm dâu, bằng không thì ngồi yên trên xe luôn cho biết mặt!"
        )),
        ("s05", 7, *p_scene(
            7, rl, "v5bo1", ["quan"],
            "Cận mặt @k4_quan đứng bên phải từ vẻ sững sờ chuyển sang mỉm cười lạnh lùng cực kỳ tỉnh táo nhìn thẳng sang trái (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh gương mặt chú rể từ vai trở lên, máy tĩnh.",
            "Chú rể bình thản lật ngược thế cờ khiến cô dâu và bạn thân sững người.",
            "Chú rể",
            "Tốt lắm! Cảm ơn hai cô đã diễn màn kịch thực dụng này ngay trước khi đặt bút ký giấy kết hôn! Nhà tôi rước vợ hiền thảo chứ không ra chợ đấu giá mua cục nợ hai tỷ!",
            "Hay lắm, may mà cô lộ rõ bản chất coi tiền hơn tình nghĩa ngay trước cổng nhà tôi! Gia đình tôi cưới nàng dâu biết điều chứ không bỏ hai tỷ mua sự ngang ngược!",
            "Khỏi cần đếm tới ba! Tôi phải cảm ơn cô bạn thân của em đã giúp tôi sáng mắt ra ngay phút chót, nhà này cưới vợ chứ không phải cây rút tiền để hai người ra giá!"
        )),
        ("s06", 6, *p_scene(
            6, rl, "v5bo1", ["quan"],
            "Cận mặt @k4_quan đứng bên phải ánh mắt đanh thép dứt khoát nói lớn sang trái (không thấy bàn tay).",
            "Cận cảnh gương mặt chú rể từ vai trở lên, máy cố định.",
            "Chú rể dõng dạc tuyên bố hủy hôn ngay tại cổng và cho xe quay đầu.",
            "Chú rể",
            "Hôn lễ chính thức hủy ngay tại cổng! Bác tài đóng cửa quay đầu xe trả cô dâu về đúng nơi sản xuất giùm tôi, mâm cỗ hôm nay tôi mời hai họ ăn mừng thoát nạn!",
            "Khỏi bước xuống xe mất công! Nhờ bác tài quay đầu chở thẳng cô dâu với phù dâu về nhà ngoại ngay lập tức, đám cưới này tôi tuyên bố dừng tại đây!",
            "Cứ ngồi yên trên xe mà giữ cái giá hai tỷ đó đi! Bác tài cho xe lăn bánh trả về nhà ngoại liền giùm tôi, tiệc hôm nay nhà trai đổi thành tiệc ăn mừng tỉnh ngộ!"
        )),
        ("s07", 7, *p_scene(
            7, rl, "v5bo1", ["kieu", "nhung"],
            "Bên trái @k4_kieu tái mét mặt mũi hốt hoảng quay sang trách móc @k4_nhung đang ngơ ngác cứng họng bên phải (khung ngực trở lên, không thấy bàn tay).",
            "Trung cận cô dâu và bạn thân phù dâu hoảng loạn, máy tĩnh.",
            "Cô dâu sụp đổ hoàn toàn khi mất trắng đám cưới nhà giàu, quay sang trút giận lên cô bạn thân xúi dại.",
            "Cô dâu áo dài trắng bên trái",
            "Trời ơi anh Quân đứng lại đã! Tại mày hết đó Nhung ơi, tự nhiên xúi tao làm căng đòi hai tỷ trước cổng giờ mất trắng đám cưới nhà giàu rồi mày bắt đền tao đi!",
            "Chết tao rồi Nhung ơi, ảnh hủy hôn thiệt luôn kìa! Nghe lời mày xúi ép giá giờ nhục nhã ê chề cả hai họ, tao biết ăn nói sao với ba mẹ tao đây!",
            "Anh Quân ơi em giỡn thôi mà đừng hủy hôn! Tất cả là tại con Nhung xúi dại tao đòi thêm hai tỷ, giờ tan tành hết đám cưới của tao rồi!"
        )),
        ("s08", 8, *p_scene(
            8, rl, "v5bo1", ["quan"],
            "Cận mặt @k4_quan đứng đĩnh đạc điềm tĩnh trước tiền sảnh biệt thự nhìn thẳng vào ống kính camera (hai tay dưới thấp ngoài khung hình).",
            "Cận cảnh từ vai trở lên hướng thẳng ống kính, máy tĩnh.",
            "Chú rể tự tin trò chuyện trực tiếp với khán giả sau màn hủy hôn quyết đoán.",
            "Chú rể nhìn thẳng ống kính",
            "Hôn nhân là chuyện nghĩa tình cả đời chứ đâu phải phiên chợ mà chờ tới cổng nhà chồng rồi hét giá hai tỷ… Cô chú anh chị thấy pha quay xe hủy hôn ngay tại cổng của tôi vậy đã đủ tỉnh táo chưa? Bình luận cho tôi biết nhé!",
            "Thà đau một lần ngay trước cổng còn hơn rước nhầm người thực dụng về khổ cả cha mẹ mình về sau. Mọi người thấy quyết định dừng đám cưới của tôi hôm nay đúng hay sai? Nhớ thả tim và bình luận bên dưới nha!",
            "Nghe lời bạn thân xúi giục làm giá phút chót và cái kết mất luôn đám cưới… Khán giả xem xong thấy tôi xử lý dứt khoát vậy có hợp lý không ạ? Hãy để lại bình luận chia sẻ nhé!"
        )),
    ]

    flat_jobs = []
    for ep_id, sc_list in episodes.items():
        ep_out_dir = os.path.join(BASE_DIR, ep_id, r_folder)
        os.makedirs(ep_out_dir, exist_ok=True)
        for sid, sec, refs, variants in sc_list:
            flat_jobs.append({
                "id": f"{ep_id}_{sid}_{ratio.replace(':','x')}",
                "episode": ep_id,
                "scene": sid,
                "ratio": ratio,
                "seconds": sec,
                "outPath": os.path.join(ep_out_dir, f"{sid}.mp4"),
                "refs": refs,
                "prompts": variants,
            })
    return flat_jobs

for r_str, fn_out in [("9:16", "flow_jobs_9x16.json"), ("16:9", "flow_jobs_16x9.json")]:
    jobs_r = build_all_episodes(r_str)
    out_p = os.path.join(BASE_DIR, fn_out)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(jobs_r, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(jobs_r)} Flow video jobs ({r_str}) -> {out_p}")
