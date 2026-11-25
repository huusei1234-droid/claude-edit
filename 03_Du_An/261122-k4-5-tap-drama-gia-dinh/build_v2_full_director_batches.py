"""
Director's Cut V2 — Full-Length Multi-Location Cinema Builder (`build_v2_full_director_batches.py`):
1. Extracts FULL-BODY standing panels (`51.4%..100%` right half -> `k4_*_full.jpg`) for every K4 actor so Wide & Crowd shots frame head-to-toe action naturally!
2. Syncs `G07_02 - Hùng (Bảo vệ sảnh tập đoàn cô Lan)` to Google Drive `CHARACTER/` + `character_registry.json` + `00_GIA_PHA_NHAN_VAT_K4.md`.
3. Builds updated Asset Boards (`AssetBoard_V2_01..05.jpg`) including the new Crowd & Multi-Location sets (`Siêu thị đông người`, `Sảnh tập đoàn đông nhân viên`, `Đám cưới đông quan khách hai họ`, `Sân vườn tưới rau`, `Phòng khách nhà Tú`, `Khoang xe hoa`).
4. Builds `flow_v2_wide_crowd_jobs_9x16.json` containing the 61 brand-new Wide, Crowd, Blocking & Story-Beat clips that interleave with our verified Close-Ups to achieve full 1m40s – 3m00s episode lengths matching all 5 source videos!
"""
import json, os, re, shutil
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
CAST_DIR = os.path.join(BASE_DIR, "cast_clean")
BODY_DIR = os.path.join(BASE_DIR, "cast_fullbody")
NEW_CHAR_RAW_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR = os.path.join(BASE_DIR, "sets")
BOARDS_DIR = os.path.join(BASE_DIR, "assetboards_v2")
ART_DIR = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
CHAR_DRIVE = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"

for d in (BODY_DIR, BOARDS_DIR):
    os.makedirs(d, exist_ok=True)

def extract_panels(src_path, face_dst, body_dst):
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    if w >= h * 0.85:
        face = im.crop((0, 0, int(w * 0.486), h))
        body = im.crop((int(w * 0.514), 0, w, h))
    else:
        face = im
        body = im
    if face_dst and not os.path.exists(face_dst):
        face.save(face_dst, "JPEG", quality=95)
    body.save(body_dst, "JPEG", quality=95)

# 1. Extract full-body panels for existing + new K4 cast
EXISTING_SRC = [
    ("baman",  os.path.join(CHAR_DRIVE, "G05_01 - Bà Mận (Chị gái bà Hạnh - Bác ruột Tuấn - Mẹ ruột Hiếu & Quỳnh).png"), "G05_01_BaMan.jpg"),
    ("hieu",   os.path.join(CHAR_DRIVE, "G05_02 - Hiếu (Con trai bà Mận - Anh họ ngoại Tuấn - Anh ruột Quỳnh - Chồng Trang).png"), "G05_02_Hieu.jpg"),
    ("trang",  os.path.join(CHAR_DRIVE, "G05_03 - Trang (Vợ Hiếu - Con dâu bà Mận - Em gái ruột Nhung).png"), "G05_03_Trang.jpg"),
    ("ongtan", os.path.join(CHAR_DRIVE, "G01_02 - Ông Tấn (Bố ruột Tuấn & Linh - Bố chồng Thảo).jpg"), "G01_02_OngTan.jpg"),
    ("thao",   os.path.join(CHAR_DRIVE, "G01_05a - Thảo (Vợ Tuấn - Con dâu bà Hạnh - Chị ruột Mai) [Váy trắng].png"), "G01_05a_Thao.jpg"),
    ("tuan",   os.path.join(CHAR_DRIVE, "G01_04b - Tuấn (Chồng Thảo - Anh trai Linh - Con trưởng ông Tấn) [Sơ mi trắng].png"), "G01_04b_Tuan.jpg"),
    ("colan",  os.path.join(CHAR_DRIVE, "G03_01 - Cô Lan (Em gái ruột ông Tấn - Cô ruột Tuấn - Mẹ ruột Tú & Hà).png"), "G03_01_CoLan.jpg"),
    ("tu",     os.path.join(CHAR_DRIVE, "G03_02 - Tú (Con trai cô Lan - Em họ nội Tuấn - Anh ruột Hà - Chồng Lam).png"), "G03_02_Tu.jpg"),
    ("lam",    os.path.join(CHAR_DRIVE, "G03_03 - Lam (Vợ Tú - Con dâu cô Lan - Em dâu họ Tuấn).png"), "G03_03_Lam.jpg"),
]

NEW_SRC = [
    ("khoi",  "G05_06 - Khôi (Con trai út bà Mận - Em ruột Hiếu & Quỳnh - Chồng Mỹ).png", "G05_06_Khoi.jpg"),
    ("my",    "G05_07 - Mỹ (Vợ Khôi - Con dâu út bà Mận - Em dâu Hiếu).png", "G05_07_My.jpg"),
    ("khai",  "G03_06 - Ông Khải (Chồng sau cô Lan - Dượng chú của Tuấn - Bố ruột Sơn & An).png", "G03_06_OngKhai.jpg"),
    ("son",   "G03_07 - Sơn (Con trai lớn riêng ông Khải - Anh ruột An).png", "G03_07_Son.jpg"),
    ("an",    "G03_08 - An (Con gái út riêng ông Khải - Em gái ruột Sơn).png", "G03_08_An.jpg"),
    ("basen", "G03_05 - Bà Sen (Mẹ ruột Lam ở quê - Mẹ vợ Tú - Thông gia cô Lan).png", "G03_05_BaSen.jpg"),
    ("quan",  "G04_05 - Quân (Con trai bác Nga - Anh ruột Uyên - Anh họ nội Tuấn) [Áo dài cưới đen].png", "G04_05_Quan.jpg"),
    ("kieu",  "G04_06 - Kiều (Cô dâu đòi 2 tỷ sính lễ của Quân) [Áo dài cưới trắng].png", "G04_06_Kieu.jpg"),
    ("nhung", "G05_05c - Nhung (Chị gái ruột Trang - Bạn thân phù dâu) [Áo dài ren trắng].png", "G05_05c_NhungPhuDau.jpg"),
    ("hung",  "G07_02 - Hùng (Bảo vệ sảnh tập đoàn cô Lan) [Đồng phục bảo vệ xanh].png", "G07_02_HungBaoVe.jpg"),
]

FACE_MAP = {}
BODY_MAP = {}

for key, sp, face_fn in EXISTING_SRC:
    fp = os.path.join(CAST_DIR, face_fn)
    bp = os.path.join(BODY_DIR, f"k4_{key}_full.jpg")
    extract_panels(sp, fp, bp)
    FACE_MAP[key] = (fp, f"k4_{key}.jpg")
    BODY_MAP[key] = (bp, f"k4_{key}_full.jpg")

for key, sheet_fn, face_fn in NEW_SRC:
    sp = os.path.join(NEW_CHAR_RAW_DIR, sheet_fn)
    assert os.path.exists(sp), f"Missing character sheet: {sp}"
    fp = os.path.join(CAST_DIR, face_fn)
    bp = os.path.join(BODY_DIR, f"k4_{key}_full.jpg")
    extract_panels(sp, fp, bp)
    FACE_MAP[key] = (fp, f"k4_{key}.jpg")
    BODY_MAP[key] = (bp, f"k4_{key}_full.jpg")
    # Sync G07_02 Hùng to CHARACTER/ Drive
    if os.path.isdir(CHAR_DRIVE):
        dst_drv = os.path.join(CHAR_DRIVE, sheet_fn)
        if not os.path.exists(dst_drv):
            shutil.copy2(sp, dst_drv)

# Update character_registry.json with G07_02 Hùng
if os.path.isdir(CHAR_DRIVE):
    reg_path = os.path.join(CHAR_DRIVE, "character_registry.json")
    if os.path.exists(reg_path):
        reg = json.load(open(reg_path, encoding="utf-8"))
        hung_fn = "G07_02 - Hùng (Bảo vệ sảnh tập đoàn cô Lan) [Đồng phục bảo vệ xanh].png"
        if not any(x["new"] == hung_fn for x in reg["items"]):
            reg["items"].append({
                "old": hung_fn, "new": hung_fn, "branch": "G07",
                "name": "Chú Hùng", "relation": "Bảo vệ đại sảnh tập đoàn của cô Lan"
            })
            reg["total_files"] = len(reg["items"])
            json.dump(reg, open(reg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 2. Convert all 12 Sets (6 original + 6 new Crowd/Wide sets) to optimized JPEGs
ALL_SET_NAMES = [
    ("v1bo1", "V1_BO1_NhaKhoi"),
    ("v1bo2", "V1_BO2_CanHoHieu"),
    ("v2bo1", "V2_BO1_PhongKhachOngTan"),
    ("v2bo2", "V2_BO2_SanVuonTuoiRau"),
    ("v2bo3", "V2_BO3_SieuThiDongNguoi"),
    ("v3bo1", "V3_BO1_PhongChuTichCoLan"),
    ("v3bo2", "V3_BO2_SanhTapDoanDongNguoi"),
    ("v4bo1", "V4_BO1_CongSanhNhaTu"),
    ("v4bo2", "V4_BO2_PhongKhachNhaTu"),
    ("v5bo1", "V5_BO1_CongCuoiNhaQuan"),
    ("v5bo2", "V5_BO2_DamCuoiDongNguoi"),
    ("v5bo3", "V5_BO3_KhoangXeHoa"),
]
SET_MAP = {}
for skey, sbase in ALL_SET_NAMES:
    p_png = os.path.join(SETS_DIR, f"{sbase}.png")
    assert os.path.exists(p_png), f"Missing set PNG: {p_png}"
    p_jpg = os.path.join(SETS_DIR, f"{sbase}.jpg")
    if not os.path.exists(p_jpg):
        im = Image.open(p_png).convert("RGB")
        im.thumbnail((1280, 1280), Image.LANCZOS)
        im.save(p_jpg, "JPEG", quality=93)
    SET_MAP[skey] = (p_jpg, f"set_{skey}.jpg")

# 3. Build Updated V2 Asset Boards (showing Crowd & Multi-Location Sets!)
def make_board_v2(ep_code, title, items):
    cols = 4
    rows = (len(items) + cols - 1) // cols
    cw, ch = 320, 400
    board = Image.new("RGB", (cols * cw, 64 + rows * ch), (16, 18, 24))
    draw = ImageDraw.Draw(board)
    try:
        fh = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
        fs = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
    except Exception:
        fh = fs = None
    draw.text((18, 18), f"ASSET BOARD V2 (WIDE + CROWD) — {ep_code}: {title}", fill=(255, 215, 70), font=fh)
    for idx, (lbl, ip) in enumerate(items):
        r, c = idx // cols, idx % cols
        x0, y0 = c * cw + 10, 64 + r * ch + 8
        im = Image.open(ip).convert("RGB")
        im.thumbnail((cw - 20, ch - 46), Image.LANCZOS)
        board.paste(im, (x0 + (cw - 20 - im.width) // 2, y0 + 30))
        draw.text((x0 + 4, y0 + 5), lbl, fill=(130, 235, 255), font=fs)
    out = os.path.join(BOARDS_DIR, f"AssetBoard_V2_{ep_code}.jpg")
    board.save(out, "JPEG", quality=92)
    shutil.copy2(out, os.path.join(ART_DIR, f"AssetBoard_V2_{ep_code}.jpg"))

make_board_v2("V01", "Mẹ chỉ có một, vợ tự chọn đi (~1m45s)", [
    ("CH-1: Bà Mận", BODY_MAP["baman"][0]), ("CH-2: Hiếu", BODY_MAP["hieu"][0]),
    ("CH-3: Trang", BODY_MAP["trang"][0]), ("CH-4: Khôi", BODY_MAP["khoi"][0]),
    ("CH-5: Mỹ", BODY_MAP["my"][0]), ("BO-1: Nhà Khôi (Toàn)", SET_MAP["v1bo1"][0]),
    ("BO-2: Căn hộ Hiếu (Toàn)", SET_MAP["v1bo2"][0]),
])
make_board_v2("V02", "Bố chồng xử lý — Siêu thị đông người & Thu thẻ lương (~3m)", [
    ("CH-1: Ông Tấn", BODY_MAP["ongtan"][0]), ("CH-2: Thảo", BODY_MAP["thao"][0]),
    ("CH-3: Tuấn", BODY_MAP["tuan"][0]), ("BO-1: Phòng khách", SET_MAP["v2bo1"][0]),
    ("BO-2: Sân vườn tưới rau", SET_MAP["v2bo2"][0]), ("BO-3: Siêu thị đông người", SET_MAP["v2bo3"][0]),
])
make_board_v2("V03", "Mẹ kế Chủ tịch — Sảnh tập đoàn đông người (~3m)", [
    ("CH-1: Cô Lan", BODY_MAP["colan"][0]), ("CH-2: Ông Khải", BODY_MAP["khai"][0]),
    ("CH-3: Sơn", BODY_MAP["son"][0]), ("CH-4: An", BODY_MAP["an"][0]),
    ("CH-5: Bảo vệ Hùng", BODY_MAP["hung"][0]), ("BO-1: Phòng Chủ tịch", SET_MAP["v3bo1"][0]),
    ("BO-2: Sảnh đông người", SET_MAP["v3bo2"][0]),
])
make_board_v2("V04", "Mẹ quê ngàn cây số tìm con gái (~1m55s)", [
    ("CH-1: Tú", BODY_MAP["tu"][0]), ("CH-2: Lam", BODY_MAP["lam"][0]),
    ("CH-3: Bà Sen", BODY_MAP["basen"][0]), ("BO-1: Cổng & Sảnh", SET_MAP["v4bo1"][0]),
    ("BO-2: Phòng khách trong nhà", SET_MAP["v4bo2"][0]),
])
make_board_v2("V05", "Đòi 2 tỷ sính lễ — Đám cưới đông người (~1m38s)", [
    ("CH-1: Chú rể Quân", BODY_MAP["quan"][0]), ("CH-2: Cô dâu Kiều", BODY_MAP["kieu"][0]),
    ("CH-3: Phù dâu Nhung", BODY_MAP["nhung"][0]), ("BO-1: Cổng biệt thự", SET_MAP["v5bo1"][0]),
    ("BO-2: Đám cưới đông người", SET_MAP["v5bo2"][0]), ("BO-3: Khoang xe hoa", SET_MAP["v5bo3"][0]),
])
print("Built all 5 V2 Wide+Crowd Asset Boards!")

# 4. Prompt builder supporting WIDE (full-body refs), MEDIUM-WIDE (full-body refs), and CLOSE-UP (portrait refs)
def mk_clip(ep, cid, sec, scale_type, set_key, char_keys, action_spatial, speaker_label, line1, line2):
    """
    scale_type:
      - 'WIDE': TOÀN CẢNH RỘNG (uses BODY_MAP full-body refs!)
      - 'MED':  TRUNG CẢNH HÀNH ĐỘNG (uses BODY_MAP full-body refs!)
      - 'CU':   CẬN CẢNH ĐẶC TẢ (uses FACE_MAP portrait refs!)
    """
    use_body = scale_type in ("WIDE", "MED")
    cmap = BODY_MAP if use_body else FACE_MAP
    s_path, s_name = SET_MAP[set_key]
    assert len(char_keys) <= 2, f"Max 2 chars + 1 set = 3 Flow Ingredients: {ep}_{cid}"
    refs = [{"path": s_path, "name": s_name}]
    tag_map = {}
    for ck in char_keys:
        cp, cn = cmap[ck]
        refs.append({"path": cp, "name": cn})
        tag_map[ck] = f"@{cn}"

    txt_sp = action_spatial
    for ck, mention in sorted(tag_map.items(), key=lambda x: len(x[0]), reverse=True):
        txt_sp = re.sub(r"@" + re.escape(ck) + r"(?![a-z0-9_])", mention, txt_sp)

    if scale_type == "WIDE":
        cam_desc = "TOÀN CẢNH RỘNG (WIDE ESTABLISHING SHOT, ống kính góc rộng 24mm): thấy rõ TOÀN THÂN TỪ ĐẦU TỚI CHÂN các nhân vật và toàn bộ không gian rộng lớn của bối cảnh xung quanh, máy quay lia nhẹ tự nhiên theo bước chân nhân vật."
    elif scale_type == "MED":
        cam_desc = "TRUNG CẢNH RỘNG (MEDIUM WIDE SHOT từ đùi/thắt lưng trở lên): thấy rõ dáng đứng, chuyển động cơ thể và không gian căn phòng phía sau, máy quay vững chãi."
    else:
        cam_desc = "CẬN CẢNH (CLOSE-UP từ vai trở lên, hai tay để dưới thấp ngoài khung hình): tập trung vào ánh mắt và biểu cảm gương mặt, máy cố định."

    def build_p(line_txt, opener):
        speech_part = (
            f'THOẠI TRỰC TIẾP: {speaker_label} nói tiếng Việt tự nhiên rõ chữ khớp khẩu hình: "{line_txt}" '
            if line_txt else
            "ÂM THANH & BIỂU CẢM: Cảnh hành động hình ảnh giàu cảm xúc, nhân vật ngậm miệng diễn xuất tự nhiên không nói thành tiếng. "
        )
        p = (
            f"{opener} {sec} giây, điện ảnh người thật photorealistic live-action (diễn viên người lớn trưởng thành), khung dọc 9:16. "
            f"BỐI CẢNH: tại @{s_name} giữ đúng không gian, đám đông nền (nếu có) và hậu cảnh trang nhã theo ảnh tham chiếu. "
            f"GÓC MÁY: {cam_desc} "
            f"CHỐT KHÔNG GIAN & DIỄN BIẾN: {txt_sp} "
            f"{speech_part}"
            f"YÊU CẦU: Giữ nguyên 100% gương mặt và trang phục nhân vật tham chiếu, một cảnh liền mạch không chia cắt shot, không nhạc nền, không phụ đề, không chữ trên màn hình, không logo góc."
        )
        for r in refs:
            assert f"@{r['name']}" in p, f"Missing @{r['name']} in {ep}_{cid}: {p}"
        return p

    out_dir = os.path.join(BASE_DIR, ep, "raw_9x16")
    os.makedirs(out_dir, exist_ok=True)
    return {
        "id": f"{ep}_{cid}_9x16",
        "episode": ep,
        "scene": cid,
        "ratio": "9:16",
        "seconds": sec,
        "outPath": os.path.join(out_dir, f"{cid}.mp4"),
        "refs": refs,
        "prompts": [build_p(line1, "Tạo video"), build_p(line2, "Cảnh quay điện ảnh")],
    }

new_jobs = []

# ==============================================================================
# EPISODE 1 (v01): 9 NEW WIDE/BLOCKING SCENES + 9 EXISTING CU = 18 SCENES (~105s)
# ==============================================================================
new_jobs += [
    mk_clip("v01", "w01", 6, "WIDE", "v1bo1", ["hieu", "baman"],
        "Giữa phòng khách bàn ăn rộng rãi thấy trọn vách trang trí phía sau, người anh cả @hieu xách giỏ trái cây tươi từ cửa bước nhanh vào hướng về phía người mẹ già @baman đang ngồi lủi thủi một mình bên bàn ăn.",
        "Người con trai áo đen bước vào",
        "Mẹ ơi! Hôm nay con thu xếp công việc ghé qua thăm mẹ đây, dạo này trong người mẹ đỡ mệt chưa ạ?",
        "Mẹ ơi con trai đến thăm mẹ đây ạ! Sao giờ này mẹ vẫn ngồi một mình ngoài bàn ăn thế này?"),
    mk_clip("v01", "w02", 6, "MED", "v1bo1", ["hieu", "my"],
        "Đứng giữa phòng ăn rộng trước bức vách gỗ sáng, người anh cả @hieu bức xúc chỉ về phía mâm cơm đạm bạc đối chất thẳng mặt cô em dâu @my đang đứng khoanh tay hất mặt bên phải.",
        "Người anh cả áo đen bên trái",
        "Em làm dâu kiểu gì mà đối xử cay nghiệt với mẹ chồng lúc tuổi già sức yếu như vậy hả Mỹ?!",
        "Mẹ tần tảo nuôi chồng em khôn lớn, sao giờ mẹ già yếu mà em nỡ ăn nói bạc bẽo như thế hả?!"),
    mk_clip("v01", "w03", 7, "WIDE", "v1bo1", ["hieu", "khoi"],
        "Toàn cảnh giữa phòng khách, người anh cả @hieu nổi giận bước tới đối mặt cậu em trai @khoi đang giơ tay chắn ngang trước cửa định ngăn cản anh trai đón mẹ đi, hai anh em cự cãi gay gắt.",
        "Cậu em trai áo khoác đen bên phải",
        "Anh đứng lại đó! Tự nhiên qua nhà tôi lớn tiếng mắng vợ chồng tôi rồi đòi tự ý dẫn mẹ đi đâu hả?!",
        "Anh đứng lại ngay! Đây là nhà riêng của vợ chồng em, anh lấy quyền gì qua đây làm ầm lên như vậy?!"),
    mk_clip("v01", "w04", 6, "WIDE", "v1bo2", ["hieu", "trang"],
        "Toàn cảnh phòng khách căn hộ cao cấp rộng sáng thấy rõ bộ sofa và bức vách đá cẩm thạch phía sau, @hieu vừa đặt chén nước ấm lên bàn thì cô vợ @trang từ cửa gỗ bên phải bước vào sững người nhìn quanh.",
        "Cô vợ áo trắng vừa bước vào cửa",
        "Ủa nhà mình tối nay có ai tới chơi mà nhìn anh tất bật dọn dẹp nấu nướng dưới bếp vậy?",
        "Nhà hôm nay có khách nào ghé chơi hả anh, sao vừa mở cửa vào em đã thấy bày biện cơm nước thế này?"),
    mk_clip("v01", "w05", 6, "MED", "v1bo2", ["hieu", "trang"],
        "Đứng giữa phòng khách căn hộ sang trọng, người chồng @hieu bên trái ôn tồn giải thích còn cô vợ @trang bên phải khoanh tay liếc xéo tỏ vẻ hờn mát khó chịu.",
        "Cô vợ áo trắng bên phải",
        "À thì ra tối nay anh chịu khó vào bếp nấu đủ món ngon là vì rước mẹ anh ở dưới quê lên chứ gì!",
        "Thảo nào hôm nay anh về sớm nấu cơm chu đáo thế, hóa ra là đón mẹ anh lên đây ở lại à!"),
    mk_clip("v01", "w06", 6, "WIDE", "v1bo2", ["trang", "baman"],
        "Toàn cảnh phòng khách căn hộ, bà mẹ già @baman ngồi thu mình rụt rè ở góc ghế sofa bên trái muốn đứng dậy, trong khi cô con dâu @trang đứng chống nạnh giữa phòng lớn tiếng xua đuổi.",
        "Cô con dâu áo trắng đứng giữa phòng",
        "Lúc anh đi làm vắng nhà tôi cũng mời bà ra khỏi cửa thôi, nhà thành phố sạch sẽ không hợp người quê đâu!",
        "Tôi nói trước cho biết, đợi chồng tôi đi làm là tôi tiễn bà về quê ngay chứ không để ở lì trong nhà này đâu!"),
    mk_clip("v01", "w07", 6, "CU", "v1bo2", ["hieu"],
        "Cận mặt người chồng @hieu đứng phía bên trái đanh mặt lại tức giận nhìn thẳng sang phải (hai tay để dưới thấp ngoài khung hình).",
        "Người chồng",
        "Đủ rồi! Bao lâu nay cô đỏng đảnh tôi đều nhường nhịn, nhưng tôi không ngờ mình lại cưới phải người vợ vô tâm như cô!",
        "Cô im ngay đi! Chuyện gì tôi cũng nhịn cô được, nhưng xúc phạm mẹ ruột tôi là bước qua giới hạn cuối cùng rồi!"),
    mk_clip("v01", "w08", 7, "WIDE", "v1bo2", ["hieu", "trang"],
        "Toàn cảnh cao trào giữa phòng khách rộng thấy trọn bức tường đá sang trọng và cửa ra vào bên phải, @hieu đứng sừng sững chỉ thẳng tay ra cửa chính trong khi @trang giậm chân tức tối hét ngược lại.",
        "Cô vợ áo trắng bên phải",
        "Tôi nói cho anh biết nha, anh vì một bà già nhà quê mà đuổi vợ ra khỏi cửa, để xem thiên hạ có ai ủng hộ anh không!",
        "Được lắm! Anh dám vì mẹ anh mà đuổi vợ mình ra đường, anh bước ra ngoài hỏi thử coi có ai bênh vực anh không!"),
    mk_clip("v01", "w09", 5, "CU", "v1bo2", ["hieu"],
        "Cận mặt người chồng @hieu đứng bên trái điềm tĩnh lạnh lùng nhìn thẳng sang phải chốt lời cuối (hai tay dưới thấp ngoài khung hình).",
        "Người chồng",
        "Tôi hoàn toàn tự tin mọi người sẽ ủng hộ tôi! Còn cô thu dọn đồ đạc rời khỏi nhà tôi ngay đi!",
        "Ai sống có hiếu cũng sẽ đồng tình với tôi thôi! Mời cô xếp hành lý bước ra khỏi cửa ngay lập tức!"),
]

# ==============================================================================
# EPISODE 2 (v02): 19 NEW WIDE/GARDEN/CROWD-SUPERMARKET SCENES + 7 EXISTING CU = 26 SCENES (~175s)
# ==============================================================================
new_jobs += [
    # Act 1: Garden Watering Vegetables (V2_BO2)
    mk_clip("v02", "w01", 6, "WIDE", "v2bo2", ["ongtan", "thao"],
        "Toàn cảnh sân vườn xanh mát trước biệt thự buổi sáng, bố chồng @ongtan đứng bên phải đang cầm vòi tưới luống rau xanh, nàng dâu @thao từ lối lát đá bên trái rụt rè bước tới lễ phép chào.",
        "Nàng dâu bước tới bên trái",
        "Dạ con chào bố buổi sáng ạ… Bố đang tưới rau hả bố, con có chuyện nhỏ này muốn thưa với bố một chút ạ.",
        "Bố ơi để lát con tưới phụ cho ạ… Nhân lúc có mình bố ở ngoài sân, con xin phép thưa với bố việc này một xíu ạ."),
    mk_clip("v02", "w02", 6, "CU", "v2bo2", ["thao"],
        "Cận mặt người con dâu trưởng thành @thao đứng ngoài sân vườn nắng sớm nhìn lễ phép sang phải (hai tay dưới thấp ngoài khung hình).",
        "Nàng dâu",
        "Cuối tuần này sinh nhật mẹ ruột con ở quê, con muốn sắm ít đồ bổ với bộ quần áo mới tặng mẹ mà anh Tuấn chưa đưa tiền nhà cho con ạ.",
        "Mấy hôm nữa tới ngày mừng tuổi mẹ đẻ con dưới quê rồi, con tính mua hộp quà sức khỏe với tấm áo mới về thăm mẹ ạ."),
    mk_clip("v02", "w03", 5, "CU", "v2bo2", ["ongtan"],
        "Cận mặt ông bố chồng @ongtan đứng ngoài sân vườn nhíu nhẹ mày giả vờ nghiêm nghị nhìn sang trái (hai tay dưới thấp ngoài khung hình).",
        "Ông bố chồng",
        "Cần tiền mua quà thì con đi mà bảo thằng Tuấn đưa chứ, tiền nó đi làm kiếm ra sao lại chạy ra đây tìm bố?",
        "Ủa chuyện chi tiêu quà cáp thì con cứ nói thẳng với chồng con, sao không bảo thằng Tuấn mà lại hỏi bố?"),
    mk_clip("v02", "w04", 7, "WIDE", "v2bo2", ["ongtan", "thao"],
        "Toàn cảnh ngoài sân vườn biệt thự, nàng dâu @thao đứng khép nép bên trái phân trần, ông bố chồng @ongtan bên phải trao vòi nước tưới cây sang tay con dâu rồi quay người bước ra cổng.",
        "Ông bố chồng áo xám",
        "Tiền nó kiếm đưa hay không là việc của vợ chồng nó! Thôi con đứng đây tưới luống rau trước đi, bố ra ngoài dạo một vòng!",
        "Chuyện tiền bạc của tụi con tự bảo ban nhau! Cầm vòi nước tưới nốt mấy luống rau giúp bố, bố đi ra phố có chút việc!"),
    mk_clip("v02", "w05", 5, "MED", "v2bo2", ["thao"],
        "Trung cảnh ngoài sân vườn xanh mát, nàng dâu @thao đứng một mình cầm vòi nước tưới nhẹ lên luống rau, gương mặt buồn bã thở dài tủi thân.",
        "Nàng dâu",
        "Bố ơi con thật lòng chỉ muốn báo hiếu mẹ một chút thôi mà… con phải sống sao thì gia đình chồng mới thông cảm cho con đây…",
        "Làm dâu quanh năm lo lắng đủ đường, tới sinh nhật mẹ ruột cũng chẳng có đồng nào trong tay, nghĩ mà tủi thân quá…"),

    # Act 2: Crowded Supermarket (V2_BO3 — Bối cảnh đông người!)
    mk_clip("v02", "w06", 6, "WIDE", "v2bo3", ["ongtan"],
        "Toàn cảnh lối đi siêu thị rộng lớn ĐÔNG ĐÚC KHÁCH HÀNG MUA SẮM QUA LẠI phía sau, ông bố chồng @ongtan đẩy chiếc xe đẩy siêu thị đi dọc dãy kệ bày nhiều hộp quà đỏ vàng sang trọng, chăm chú nhìn ngắm hai bên kệ.",
        "Ông bố chồng đẩy xe hàng",
        "Cái đám con cái này ngày nào cũng không để cho người già bớt lo được… để xem siêu thị có hộp quà bổ nào tốt nhất nào!",
        "Đi chọn quà cho bà thông gia mà nhìn nhiều loại quá, phải tự tay ra siêu thị lựa loại chất lượng nhất mới yên tâm!"),
    mk_clip("v02", "w07", 6, "MED", "v2bo3", ["ongtan"],
        "Trung cảnh giữa quầy kệ siêu thị có người mua sắm đi lại mờ nhẹ phía sau, @ongtan cầm một hộp quà màu đỏ sang trọng lên xem xét kỹ lưỡng rồi hài lòng gật đầu đặt vào xe đẩy.",
        "Ông bố chồng",
        "Loại thượng hạng này nguồn gốc xuất xứ rõ ràng, bồi bổ cho người lớn tuổi dưới quê chắc chắn là hợp ý bà thông gia rồi!",
        "Mấy hộp quà sức khỏe cao cấp này đóng gói trang trọng lịch sự, lấy hẳn mấy bộ đem về cho con dâu mang về quê mới xứng!"),
    mk_clip("v02", "w08", 5, "WIDE", "v2bo3", ["ongtan"],
        "Toàn cảnh lối đi siêu thị nhộn nhịp đông người mua sắm, @ongtan vui vẻ đẩy chiếc xe hàng chất đầy ắp các hộp quà màu đỏ tiến thẳng về phía trước với nụ cười mãn nguyện.",
        "", "", ""),

    # Act 3: Living Room Arrival & Misunderstanding (V2_BO1)
    mk_clip("v02", "w09", 6, "WIDE", "v2bo1", ["tuan", "thao"],
        "Toàn cảnh phòng khách biệt thự rộng sáng thấy trọn bức tường vân đá và lam sóng gỗ phía sau, người chồng @tuan xách nhiều túi quà từ bên phải bước vào gọi lớn, nàng dâu @thao từ bên trái mừng rỡ chạy lại đón đỡ túi quà.",
        "Người chồng sơ mi trắng",
        "Vợ ơi mau ra đây xách phụ anh một tay coi, hôm nay anh mua bao nhiêu là đồ bổ xịn mang về nhà mình nè!",
        "Thảo ơi ra đỡ phụ anh mấy túi quà lớn này với, nặng trĩu cả hai tay luôn rồi nè!"),
    mk_clip("v02", "w10", 5, "CU", "v2bo1", ["thao"],
        "Cận mặt nàng dâu @thao đứng bên trái phòng khách ánh mắt chưng hửng buồn bã rưng rưng khi nghe chồng nói quà không phải cho mẹ mình (không thấy bàn tay).",
        "Nàng dâu",
        "Em cứ tưởng anh nhớ cuối tuần sinh nhật mẹ em ở quê nên mới mua sẵn quà cho hai vợ chồng mang về thăm mẹ…",
        "Hóa ra anh chỉ nhớ bồi bổ cho ba ruột anh thôi, còn ngày sinh nhật mẹ đẻ của em thì anh quên sạch rồi sao…"),
    mk_clip("v02", "w11", 6, "WIDE", "v2bo1", ["ongtan", "tuan"],
        "Toàn cảnh phòng khách rộng đẹp, ông bố chồng @ongtan vừa xách mấy túi giấy quà đỏ từ ngoài bước vào ngồi xuống ghế sofa bên phải, con trai @tuan lập tức đon đả bước tới khoe các hộp quà trên bàn trà.",
        "Ông bố chồng ngồi xuống sofa",
        "Ủa hôm nay thằng Tuấn đi đâu về mà bày nhiều hộp quà trước bàn khách thế kia, con mua gì mà lắm vậy?",
        "Bố vừa đi siêu thị xách ít đồ về mỏi cả chân, thế mấy túi quà trên bàn kia là con mua cho ai đấy Tuấn?"),
    mk_clip("v02", "w12", 7, "MED", "v2bo1", ["tuan", "ongtan"],
        "Trung cảnh hai cha con bên bàn trà phòng khách, @tuan bên trái hào hứng chỉ vào hộp quà tặng bố, còn @ongtan ngồi bên phải nét mặt chuyển từ gật đầu sang nghiêm nghị hỏi vặn con trai.",
        "Ông bố chồng bên phải",
        "Con biết lo sức khỏe cho ba là tốt… nhưng hiếu thuận với ba mẹ mình là lẽ đương nhiên, thế còn vợ mày sao không lo cho nó về báo hiếu mẹ ruột nó?!",
        "Bố ghi nhận tấm lòng của mày… nhưng mày chỉ biết chăm chăm lo cho bố ruột, thế còn sinh nhật mẹ đẻ của vợ mày dưới quê thì mày tính sao?!"),

    # Act 4: Full Father-in-law Lecture & Salary Card Confiscation (V2_BO1)
    mk_clip("v02", "w13", 6, "WIDE", "v2bo1", ["tuan", "ongtan"],
        "Toàn cảnh phòng khách sang trọng, người con trai @tuan đứng khép nép bên trái trước bàn trà phân bua chống chế, trong khi ông bố chồng @ongtan ngồi uy nghiêm trên ghế sofa bên phải nhìn thẳng chất vấn.",
        "Người con trai sơ mi trắng bên trái",
        "Dạ con có ngăn cản cô ấy về quê thăm mẹ đâu ạ, con cũng chưa bảo không đưa tiền, chỉ là muốn xin ý kiến ba trước thôi!",
        "Ba nói oan cho con quá, con đâu có cấm vợ về ngoại mừng sinh nhật mẹ đâu, tại con muốn hỏi qua ý ba một tiếng mà!"),
    mk_clip("v02", "w14", 7, "CU", "v2bo1", ["ongtan"],
        "Cận mặt ông bố chồng @ongtan ngồi bên phải quắc mắt nghiêm khắc nhìn thẳng sang trái dạy dỗ con trai (hai tay dưới thấp ngoài khung hình).",
        "Ông bố chồng",
        "Vợ chồng kết tóc là một thể, đồng tiền con kiếm ra cũng là tài sản chung hai đứa! Sống phải có trước có sau chứ ai lại để vợ ngày nào cũng phải rụt rè xin xỏ?!",
        "Không cản vợ về thăm ngoại mà mày giữ khư khư tiền bạc trong túi à?! Vợ chồng là nghĩa tào khang, sao mày nỡ để vợ mình chịu thiệt thòi trước mặt nhà ngoại như thế?!"),
    mk_clip("v02", "w15", 5, "CU", "v2bo1", ["tuan"],
        "Cận mặt người con trai @tuan đứng bên trái nhăn mặt ấm ức nhìn sang phải cãi lại bố (hai tay để dưới thấp ngoài khung hình).",
        "Người con trai",
        "Ủa ba! Rõ ràng con mới là con trai ruột máu mủ của ba mà, sao chuyện gì ba cũng đứng về phía người ngoài thế ạ?!",
        "Ba kỳ thiệt đó, con là con đẻ của ba đây không bênh, sao ba cứ toàn bênh vực con dâu người ngoài vậy hả ba?!"),
    mk_clip("v02", "w16", 8, "MED", "v2bo1", ["ongtan", "tuan"],
        "Trung cảnh rộng giữa phòng khách trước bức vách đá cẩm thạch, ông bố chồng @ongtan đứng thẳng dậy đầy uy quyền nhìn thẳng mặt @tuan đang cúi gằm xấu hổ bên trái, dạy câu đạo lý thấm thía.",
        "Ông bố chồng đứng nghiêm nghị bên phải",
        "Mày mở miệng nói ai là trong, ai là ngoài?! Ba chỉ nuôi mày khôn lớn chứ không bầu bạn với mày tới già được, mai này ba khuất núi người ở bên mày cuối cùng chính là vợ mày đó!",
        "Đồ hồ đồ! Vợ đầu ấp tay gối cả đời mà mày gọi là người ngoài à?! Ba đối xử tốt với con dâu thì gia đạo nhà này mới hưng thịnh, chứ vô tâm như mày là hỏng hết!"),

    # Act 5: Awakening, Handing All Supermarket Gifts & Courtyard Send-off (V2_BO1 & V2_BO2)
    mk_clip("v02", "w17", 6, "CU", "v2bo1", ["tuan"],
        "Cận mặt người con trai @tuan đứng bên trái cúi đầu hối lỗi chân thành rồi ngước nhìn bố đầy tỉnh ngộ (không thấy bàn tay).",
        "Người con trai",
        "Dạ thưa ba… nghe ba phân tích con sáng mắt ra rồi ạ! Ngay bây giờ con chuẩn bị xe đưa Thảo về quê tổ chức sinh nhật thật chu đáo cho mẹ vợ liền!",
        "Ba dạy chí phải, con biết mình vô tâm với vợ rồi ạ! Để hôm nay con thu xếp công việc đưa Thảo về ngoại mừng thọ mẹ ngay lập tức!"),
    mk_clip("v02", "w18", 7, "WIDE", "v2bo1", ["ongtan", "thao"],
        "Toàn cảnh phòng khách ấm áp, ông bố chồng @ongtan đứng cạnh bàn trà trao tận tay các túi quà đỏ mua ở siêu thị cho nàng dâu @thao đang cúi đầu xúc động rưng rưng đón nhận.",
        "Ông bố chồng hiền hậu bên phải",
        "Mấy túi quà bổ ba vừa tự tay ra siêu thị chọn kỹ lắm, hai đứa mang đi biếu mẹ hết nha! Còn quần áo ba không rành cỡ, con cầm phong bì của ba về tự chọn cho mẹ!",
        "Con gái cầm lấy hết mấy phần quà sức khỏe ba mới mua ngoài siêu thị này đem về biếu bà thông gia! Hai nhà tuy hai mà một, đừng ngại ngùng gì với ba hết!"),
    mk_clip("v02", "w19", 6, "WIDE", "v2bo2", ["ongtan", "thao"],
        "Toàn cảnh ngoài sân vườn biệt thự nắng đẹp, nàng dâu @thao xách túi quà đỏ mỉm cười chào tạm biệt bên trái trong khi ông bố chồng @ongtan đứng trước hiên nhà bên phải tươi cười vẫy tay dặn dò.",
        "Ông bố chồng vẫy tay tiễn con",
        "Lên đường thượng lộ bình an nha hai đứa! Lâu lâu mới về thăm quê một chuyến, cứ ở lại chơi thêm hai ngày chăm sóc mẹ cho trọn vẹn nghe con!",
        "Đi đường cẩn thận nha con gái! Về dưới đó cho ba gửi lời hỏi thăm sức khỏe bà thông gia, hai vợ chồng cứ ở chơi vài hôm cho mẹ con vui lòng!"),
]

# ==============================================================================
# EPISODE 3 (v03): 16 NEW CROWDED-LOBBY/GUARD/WIDE SCENES + 9 EXISTING CU = 25 SCENES (~175s)
# ==============================================================================
new_jobs += [
    # Act 1: Crowded Corporate Lobby & Security Guard Hùng (V3_BO2 — Bối cảnh đông người!)
    mk_clip("v03", "w01", 6, "WIDE", "v3bo2", ["son", "hung"],
        "Toàn cảnh đại sảnh tập đoàn sang trọng ĐÔNG NHÂN VIÊN VĂN PHÒNG QUA LẠI phía sau, chàng trai nghèo @son đứng bên trái lễ phép chìa tấm ảnh cũ nhờ gã bảo vệ mặc đồ xanh @hung đứng chắn nghiêm mặt bên phải.",
        "Chàng trai áo xám bên trái",
        "Anh bảo vệ làm ơn báo giúp bác Khải một tiếng thôi ạ, bác ấy thật sự là ba ruột thất lạc nhiều năm của hai anh em tôi!",
        "Xin chú thông cảm chuyển lời giúp tụi cháu gặp ông Khải một lát, tụi cháu từ xa tìm tới có tấm ảnh kỷ niệm của ba đây ạ!"),
    mk_clip("v03", "w02", 6, "MED", "v3bo2", ["hung", "son"],
        "Trung cảnh giữa đại sảnh tập đoàn có đám đông nhân viên ngoái nhìn phía sau, gã bảo vệ @hung bên phải hách dịch xua tay đuổi @son đang đứng nhẫn nhịn bên trái.",
        "Gã bảo vệ áo xanh bên phải",
        "Đi chỗ khác ngay! Ông Khải là chồng của Chủ tịch Lan danh giá, làm gì có đứa con đi làm thợ hồ lấm lem nghèo rách thế này!",
        "Tránh ra ngoài cửa liền đi! Tập đoàn lớn chứ đâu phải chỗ cho mấy người nghèo khổ cầm tấm ảnh cũ tới nhận vơ người thân!"),
    mk_clip("v03", "w03", 7, "WIDE", "v3bo2", ["colan", "hung"],
        "Toàn cảnh đại sảnh tập đoàn đông đúc nhân viên văn phòng đứng dạt hai bên, nữ Chủ tịch @colan phong thái quyền lực bước ra ở trung tâm nghiêm giọng chấn chỉnh gã bảo vệ @hung đang giật mình khép nép bên phải.",
        "Nữ Chủ tịch đầm xanh hoa",
        "Chú Hùng! Đang giờ làm việc có chuyện gì mà chú lớn tiếng xua đuổi người ta ngay giữa đại sảnh tập đoàn thế này hả?!",
        "Dừng tay lại ngay chú Hùng! Ai cho phép chú hành xử thiếu tôn trọng, quát tháo người dân ngay tại sảnh công ty của tôi vậy?!"),
    mk_clip("v03", "w04", 5, "CU", "v3bo2", ["hung"],
        "Cận mặt gã bảo vệ @hung đứng giữa sảnh tập đoàn cúi đầu khép nép thanh minh với cấp trên (hai tay để dưới thấp ngoài khung hình).",
        "Gã bảo vệ",
        "Dạ thưa Chủ tịch… tại hai anh em ăn mặc luộm thuộm này cứ khăng khăng cầm ảnh cũ tới nhận chồng Chủ tịch là bố ruột ạ!",
        "Dạ bẩm bà Chủ tịch, tôi sợ người lạ làm phiền ngài Khải vì hai đứa trẻ nghèo này cứ đòi gặp nhận chồng bà làm ba đẻ ạ!"),
    mk_clip("v03", "w05", 6, "MED", "v3bo2", ["colan", "son"],
        "Trung cảnh tại đại sảnh tập đoàn có nhân viên dõi theo phía sau, @colan bên phải cầm xem tấm ảnh kỷ niệm từ tay @son bên trái rồi ánh mắt chấn động xen lẫn ấm áp.",
        "Nữ Chủ tịch bên phải",
        "Không sai vào đâu được, đây đúng là tấm ảnh chồng tôi chụp thời còn trẻ! Hai cháu đi theo tôi lên phòng riêng nói chuyện cho đàng hoàng!",
        "Đúng là nét mặt ông Khải chồng tôi hồi hai mươi lăm năm trước rồi! Hai đứa đừng đứng ngoài sảnh nữa, theo bác lên phòng làm việc ngay!"),
    mk_clip("v03", "w06", 5, "WIDE", "v3bo2", ["colan", "an"],
        "Toàn cảnh đại sảnh tập đoàn đông người, nữ Chủ tịch @colan ân cần nắm nhẹ tay cô gái trẻ yếu ớt @an dẫn bước về phía thang máy trước ánh mắt nể phục của các nhân viên văn phòng xung quanh.",
        "", "", ""),

    # Act 2: Chairwoman Office Inquiry (V3_BO1)
    mk_clip("v03", "w07", 6, "WIDE", "v3bo1", ["colan", "son"],
        "Toàn cảnh phòng làm việc Chủ tịch rộng lớn thấy trọn bàn gỗ và bức vách lam sóng nâu phối vân đá sang trọng, @colan ngồi bên phải nhẹ nhàng hỏi thăm @son đang đứng lễ phép bên ghế sofa phía trái.",
        "Nữ Chủ tịch ngồi ghế bên phải",
        "Tôi và chồng kết hôn tới nay cũng ngót nghét hai mươi năm rồi, sao mãi tới hôm nay hai cháu mới tìm đến tận đây?",
        "Hai cháu ngồi xuống uống ngụm nước đi rồi kể bác nghe, sao bao nhiêu năm qua hai đứa không hề liên lạc gì với ba ruột?"),
    mk_clip("v03", "w08", 6, "CU", "v3bo1", ["son"],
        "Cận mặt chàng trai @son trong phòng Chủ tịch ánh mắt đượm buồn thành thật giãi bày (hai tay để dưới thấp ngoài khung hình).",
        "Người anh trai",
        "Dạ từ ngày ba mẹ cháu chia tay, hai anh em dọn đi theo mẹ và bị cấm tiệt không được liên lạc với ba… nay em gái trở bệnh nặng quá cháu mới dám tìm tới ạ.",
        "Hồi nhỏ tụi cháu theo mẹ chuyển đi xa không còn biết tin tức gì của ba nữa… giờ sức khỏe em An nguy cấp quá cháu mới đánh liều đi tìm ba ạ."),

    # Act 3: Father Reunion & 15-Year Child Support Truth (V3_BO1)
    mk_clip("v03", "w09", 7, "WIDE", "v3bo1", ["khai", "son"],
        "Toàn cảnh phòng Chủ tịch rộng sáng, người cha @khai mặc vest xám vội vã bước nhanh từ bên phải tới nắm chặt hai vai con trai @son đang đứng rưng rưng bên trái, khung cảnh đoàn tụ đầy xúc động.",
        "Người cha mặc vest xám",
        "Con trai của ba! Đúng là thằng Sơn với cái An bằng xương bằng thịt đây rồi, ba đi tìm kiếm hai đứa mòn mỏi bao nhiêu năm nay con ơi!",
        "Trời đất ơi đúng là hai con của ba rồi! Bà Lan ơi, hai đứa nhỏ mà tôi hằng đêm trăn trở tìm kiếm bấy lâu nay đang đứng trước mặt mình đây rồi!"),
    mk_clip("v03", "w10", 6, "CU", "v3bo1", ["son"],
        "Cận mặt chàng trai @son mím môi nghẹn ngào nước mắt trực trào khi nghe ba nhắc chuyện tiền chu cấp hằng tháng (không thấy bàn tay).",
        "Người anh trai",
        "Tụi con chưa từng nhận được một đồng nào hết ba ơi… Mẹ với dượng giữ trọn số tiền đó sắm sửa riêng, tối qua con sang hỏi nhờ cứu em còn bị xua đuổi về!",
        "Hai anh em con hoàn toàn không hề hay biết chuyện ba gửi tiền… bao năm qua mẹ giữ hết lo cho gia đình mới, chưa từng đưa tụi con lấy một xu!"),
    mk_clip("v03", "w11", 6, "MED", "v3bo1", ["colan", "khai"],
        "Trung cảnh trước bức vách gỗ đá sang trọng phòng Chủ tịch, @colan bên phải chau mày phẫn nộ đập nhẹ tay xuống mặt bàn, cạnh bên là @khai đau xót thở dài.",
        "Nữ Chủ tịch bên phải",
        "Nghe con trẻ kể mà tôi giận sôi cả người! Sao lại có người mẹ nhẫn tâm giữ hết tiền chu cấp mười lăm năm để mặc con ruột thất học đau ốm như vậy!",
        "Thật không thể chấp nhận nổi sự ích kỷ quá đáng như thế! Tiền mồ hôi nước mắt ông gửi nuôi con mà họ nỡ lòng ăn chặn suốt mười lăm năm trời!"),
    mk_clip("v03", "w12", 6, "MED", "v3bo1", ["khai", "son"],
        "Trung cảnh trong phòng Chủ tịch, người cha @khai bên phải rút phong bì dày từ túi áo vest ân cần đặt về phía con trai @son đang lưỡng lự bối rối bên trái.",
        "Người cha mặc vest xám",
        "Sơn ơi con cầm đỡ khoản tiền mặt này đưa cái An vô bệnh viện khám trước đi con, ba nhất định sẽ thu xếp ổn thỏa để đón hai anh em!",
        "Trước mắt con cứ nhận lấy phong bì này lo thuốc thang cấp cứu cho em gái đã, mọi chuyện còn lại để ba từ từ tính toán bù đắp cho hai đứa!"),

    # Act 4: Bird's Nest Porridge Doorway Stop & Grand Family Ending (V3_BO1)
    mk_clip("v03", "w13", 7, "WIDE", "v3bo1", ["colan", "son"],
        "Toàn cảnh lối cửa phòng Chủ tịch rộng sáng, khi @son bên trái đang cúi đầu định bước ra cửa rời đi thì nữ Chủ tịch @colan bên phải bưng khay sứ có hai thố cháo yến trắng tinh bước tới chắn ngang giữ lại.",
        "Nữ Chủ tịch bưng khay cháo yến",
        "Chưa ăn chén cháo yến nóng cho ấm bụng mà hai anh em đã vội vàng dắt nhau bỏ đi đâu giữa trưa nắng thế này!",
        "Hai đứa dừng chân lại ngay cho bác! Bác vừa dặn nhà bếp chưng sẵn hai thố cháo yến bổ dưỡng đây, ăn xong khỏe người rồi nói chuyện tiếp!"),
    mk_clip("v03", "w14", 6, "MED", "v3bo1", ["colan", "khai"],
        "Trung cảnh ấm áp trước vách đá vàng phòng Chủ tịch, @colan bên phải quay sang trách nhẹ đầy bao dung với người chồng @khai đang rưng rưng cảm động bên trái.",
        "Nữ Chủ tịch bên phải",
        "Sao ông lại chỉ đưa tiền bảo con đi tạm? Cả nửa đời ông đau đáu nhớ thương con, nay tuổi xế chiều tìm lại được hai đứa chính là phúc lớn nhất của vợ chồng mình!",
        "Ông khờ quá đi mất, con ruột tìm tới tận nơi sao lại để chúng nó quay về phòng trọ? Đoàn tụ được với hai con là niềm hạnh phúc lớn nhất đời ông mà!"),
    mk_clip("v03", "w15", 6, "WIDE", "v3bo1", ["son", "an"],
        "Toàn cảnh trong phòng Chủ tịch tràn ngập ánh sáng ấm áp, hai anh em @son và @an đứng sóng đôi cúi đầu thật sâu rưng rưng nước mắt cảm tạ tấm lòng cao thượng của bà mẹ kế.",
        "Người anh trai cúi đầu cảm ơn",
        "Dạ hai anh em con xin cúi đầu đội ơn bác gái đã rộng lượng thương xót và cưu mang tụi con lúc hoạn nạn này ạ!",
        "Tụi con không biết nói gì hơn ngoài lời biết ơn tận đáy lòng vì bác đã xem hai anh em con như người một nhà ạ!"),
    mk_clip("v03", "w16", 6, "MED", "v3bo1", ["khai", "colan"],
        "Trung cảnh hai vợ chồng già đứng cạnh nhau giữa phòng Chủ tịch, người chồng @khai bên trái nắm chặt đôi bàn tay người vợ @colan bên phải với ánh mắt rưng rưng trân trọng.",
        "Người chồng mặc vest xám",
        "Cảm ơn bà nhiều lắm! Kiếp này tôi gặp được người bạn đời nhân hậu, thấu tình đạt lý như bà thật sự là phúc đức lớn nhất của cha con tôi!",
        "Tôi thay mặt hai đứa nhỏ cảm tạ tấm lòng Bồ Tát của bà! Có người vợ bao dung như bà, gia đình mình từ nay trọn vẹn tiếng cười rồi!"),
]

# ==============================================================================
# EPISODE 4 (v04): 8 NEW WIDE-GATE/LIVING-ROOM SCENES + 8 EXISTING CU = 16 SCENES (~112s)
# ==============================================================================
new_jobs += [
    mk_clip("v04", "w01", 6, "WIDE", "v4bo1", ["basen", "tu"],
        "Toàn cảnh trước cổng sắt biệt thự sang trọng buổi sáng, bà mẹ quê @basen đeo túi vải xám bước chậm rãi tới ngước nhìn biển số nhà bên trái, đúng lúc chàng rể trẻ @tu từ trong sảnh bước ra cổng.",
        "Chàng rể trẻ bước ra cổng bên phải",
        "Dạ chào bác ạ, bác đi tìm ai mà đứng ngó nghiêng mãi trước cổng nhà cháu giữa trời nắng thế này ạ?",
        "Bác ơi bác từ đâu tới mà tay xách nách mang đứng tần ngần trước cửa nhà cháu vậy, bác cần tìm ai để cháu giúp ạ?"),
    mk_clip("v04", "w02", 6, "MED", "v4bo1", ["basen", "tu"],
        "Trung cảnh rộng trước cổng biệt thự mở hé thấy sảnh đá bên trong, @basen bên trái đưa mảnh giấy trắng ghi địa chỉ cho @tu bên phải cúi nhìn xác nhận đầy kinh ngạc.",
        "Chàng rể trẻ cầm mảnh giấy bên phải",
        "Ơ… dòng chữ ghi trên tờ giấy này đúng chính xác số nhà của vợ chồng cháu rồi! Ai ở dưới quê đưa địa chỉ này cho bác vậy ạ?",
        "Đúng là địa chỉ nhà cháu không sai một chữ nào luôn bác ơi! Mà bác lấy thông tin số nhà này từ ai dưới quê thế ạ?"),
    mk_clip("v04", "w03", 6, "WIDE", "v4bo1", ["tu", "basen"],
        "Toàn cảnh trước cổng biệt thự thoáng đãng, @tu bên phải rút chiếc điện thoại từ túi quần ra vẻ mặt nghiêm túc hỏi han @basen đang đứng nép bên cột cổng phía trái.",
        "Chàng rể trẻ bên phải",
        "Bác không có số điện thoại của cô ấy thì cho cháu hỏi quý danh của bác là gì ạ? Bác đứng mát đợi cháu một lát để cháu gọi xác nhận ngay!",
        "Chuyện này lạ quá, bác cho cháu biết họ tên đầy đủ của bác đi ạ, bác cứ đứng nghỉ chân dưới mái hiên để cháu bấm máy gọi cô ấy về liền!"),
    mk_clip("v04", "w04", 6, "WIDE", "v4bo1", ["lam", "basen"],
        "Toàn cảnh sân cổng biệt thự rộng sáng, cô vợ trẻ @lam từ bên phải hớt hải chạy vội vào tới hiên nhà thì khựng đứng chôn chân mở to mắt sững sờ khi thấy mẹ ruột @basen đứng bên trái.",
        "Cô vợ trẻ hốt hoảng dừng bước",
        "Trời ơi… mẹ! Sao hôm nay mẹ lặn lội từ tận ngoài quê tìm vào tới tận cửa nhà con thế này hả mẹ?!",
        "Mẹ ơi… sao mẹ biết đường tìm lên tới tận thành phố mà không báo trước câu nào làm con hết hồn vậy mẹ?!"),
    mk_clip("v04", "w05", 6, "MED", "v4bo1", ["tu", "basen"],
        "Trung cảnh trước sảnh kính sáng rực của biệt thự, chàng rể @tu bên phải từ nét mặt nghiêm khắc với vợ lập tức chuyển sang cúi đầu lễ phép ấm áp thưa chuyện cùng mẹ vợ @basen bên trái.",
        "Chàng rể trẻ lễ phép bên phải",
        "Bác ơi… à không, từ giây phút này con là con rể thì phải thưa là Mẹ mới đúng đạo lý! Mẹ ơi hôm nay ngoài quê nhà mình có chuyện gì gấp hả mẹ?",
        "Dạ thưa bác… không phải, con xin phép gọi bằng Mẹ luôn mới phải phép! Mẹ vượt cả ngàn cây số lên đây chắc ở quê đang có việc hệ trọng phải không mẹ?"),
    mk_clip("v04", "w06", 6, "MED", "v4bo1", ["tu", "basen"],
        "Trung cảnh rộng trước thềm sảnh biệt thự, @tu bên phải ân cần đặt ví và thẻ vào tay mẹ vợ @basen bên trái khiến bà cụ bối rối xua nhẹ tay ngại ngùng.",
        "Bà mẹ quê bối rối bên trái",
        "Con rể đưa cho mẹ nhiều tiền bạc quý giá thế này mẹ cầm sao đặng hả con, hai đứa trên phố còn bao nhiêu thứ phải chi tiêu mà…",
        "Nhiều quá con ơi, mẹ ở nhà quê làm gì dám cầm cả thẻ ngân hàng lớn thế này của vợ chồng con, ngại chết đi được…"),
    mk_clip("v04", "w07", 6, "WIDE", "v4bo1", ["tu", "basen"],
        "Toàn cảnh trước cửa đại sảnh biệt thự thấy rõ bức vách trang trí vân đá và lam gỗ sáng ấm bên trong, @tu trân trọng đỡ lấy túi đồ quê và khoác vai dìu mẹ vợ @basen bước qua bậc thềm vào nhà.",
        "Chàng rể trẻ dìu mẹ vợ vào nhà",
        "Đi đường xa ba ngày đêm chắc mẹ mỏi chân lắm rồi, thôi hai mẹ con mình vào trong nhà uống chén trà nóng nghỉ ngơi thôi mẹ ơi!",
        "Ngoài trời nắng lên rồi mẹ đừng đứng ngoài cổng nữa, để con xách hành lý dìu mẹ vào phòng khách ngồi nghỉ cho khỏe người nha mẹ!"),
    mk_clip("v04", "w08", 6, "WIDE", "v4bo2", ["tu", "basen"],
        "Toàn cảnh bên trong phòng khách biệt thự sang trọng ấm cúng với bức tường vân đá kem vàng và lam sóng gỗ phía sau, @tu ân cần mời mẹ vợ @basen ngồi xuống bộ ghế sofa êm ái.",
        "Chàng rể trẻ niềm nở trong phòng khách",
        "Mẹ cứ ngồi nghỉ tự nhiên như ở nhà mình nha mẹ, để con bảo nhà bếp nấu chén súp nóng hổi dọn ra mời mẹ dùng liền ạ!",
        "Từ hôm nay đây cũng là ngôi nhà của bố mẹ rồi, mẹ ngồi tựa lưng nghỉ ngơi cho đỡ mệt để tụi con pha trà ấm mời mẹ nhé!"),
]

# ==============================================================================
# EPISODE 5 (v05): 7 NEW CROWDED-WEDDING / CAR-INTERIOR SCENES + 8 EXISTING CU = 15 SCENES (~95s)
# ==============================================================================
new_jobs += [
    mk_clip("v05", "w01", 6, "WIDE", "v5bo2", ["quan"],
        "Toàn cảnh đám cưới náo nhiệt trước cổng biệt thự ĐÔNG ĐẢO QUAN KHÁCH HAI HỌ MẶC VEST VÀ ÁO DÀI ĐỨNG HAI BÊN, chú rể @quan mặc áo dài đen thêu vàng tươi cười bước tới cạnh chiếc xe hoa trắng dừng giữa sân đón dâu.",
        "Chú rể áo dài đen tươi cười",
        "Xe hoa về tới cổng đúng giờ lành rồi, mời bà con hai họ chuẩn bị đón cô dâu bước vào đại sảnh làm lễ gia tiên nha!",
        "Tới giờ đẹp rồi Kiều ơi, hai bên gia đình quan khách đứng chờ đông đủ hết ngoài sân rồi, anh mở cửa đón em xuống xe nhé!"),
    mk_clip("v05", "w02", 6, "MED", "v5bo3", ["kieu", "nhung"],
        "Trung cảnh bên trong khoang ghế da kem sang trọng của chiếc xe hoa, cô dâu @kieu đội mấn ngồi bên trái và cô bạn thân phù dâu @nhung ngồi sát bên phải thì thầm bàn tính giữ chặt giá không chịu bước xuống xe.",
        "Phù dâu áo dài ren trắng bên phải",
        "Nghe lời tao ngồi im trên ghế chưa được bước xuống vội, giờ lành tới sát nút rồi nhà trai kiểu gì cũng sợ mất mặt mà chuyển đủ hai tỷ thôi!",
        "Mày cứ giữ cứng thái độ ngay trên xe hoa này cho tao, họ hàng nhà ảnh đứng đông nghẹt ngoài kia, đòi thêm hai tỷ lúc này là chắc thắng trăm phần trăm!"),
    mk_clip("v05", "w03", 6, "WIDE", "v5bo2", ["nhung", "quan"],
        "Toàn cảnh sân biệt thự ĐÔNG KÍN QUAN KHÁCH HAI HỌ ĐANG NGƠ NGÁC NHÌN, phù dâu @nhung bước hẳn xuống đứng khoanh tay chắn ngang trước cửa xe hoa đối đầu trực diện với chú rể @quan bên phải.",
        "Phù dâu đứng chắn cửa xe bên trái",
        "Đứng lùi lại đi anh chú rể! Hôm nay chưa thấy tin nhắn báo đủ hai tỷ sính lễ phát sinh thì không ai được phép rước cô dâu bước qua cánh cửa xe này!",
        "Mọi người làm chứng luôn nha, nhà trai chưa thu xếp xong khoản sính lễ hai tỷ trao tay ngay tại cổng thì cô dâu nhất quyết ngồi yên trên xe!"),
    mk_clip("v05", "w04", 6, "MED", "v5bo2", ["quan", "kieu"],
        "Trung cảnh rộng trước chiếc xe hoa giữa vòng vây họ hàng quan khách phía xa, chú rể @quan bên phải cố nén giận ôn tồn thương lượng với cô dâu @kieu đang lấp ló ở khung cửa xe bên trái.",
        "Chú rể áo dài đen bên phải",
        "Kiều ơi em nghĩ cho thể diện cha mẹ hai bên một chút đi! Chuyện tiền bạc đợi cử hành hôn lễ xong vào nhà bàn bạc anh nhất định sẽ bù đắp mà!",
        "Bao nhiêu cô chú họ hàng đang đứng phơi nắng chờ tụi mình kìa Kiều, có chuyện gì vào làm lễ gia tiên xong hai vợ chồng đóng cửa bảo nhau sau đi em!"),
    mk_clip("v05", "w05", 6, "WIDE", "v5bo2", ["kieu", "quan"],
        "Toàn cảnh trước cửa xe hoa giữa sân đông đúc khách cưới xì xào, cô dâu @kieu đứng ngay bậc cửa xe bên trái khoanh tay lạnh lùng lắc đầu từ chối thẳng thừng trước mặt chú rể @quan bên phải.",
        "Cô dâu áo dài trắng bên trái",
        "Không có chuyện đợi cưới xong mới bàn bạc hứa suông! Hôm nay tiền không trao tận tay ngay trước cổng này thì đám cưới khỏi tiến hành luôn!",
        "Em nói một lời là một lời, bước qua cổng hào môn không thể nói miệng được, chưa thấy đủ hai tỷ thì miễn bàn chuyện vào làm lễ!"),
    mk_clip("v05", "w06", 7, "WIDE", "v5bo2", ["quan", "nhung"],
        "Toàn cảnh cao trào giữa sân biệt thự ĐÔNG ĐẢO QUAN KHÁCH HAI HỌ SỮNG SỜ CHỨNG KIẾN, chú rể @quan bên phải dứt khoát đẩy khép cánh cửa xe hoa lại trước mặt @nhung và vẫy tay ra hiệu cho tài xế quay đầu xe.",
        "Chú rể dõng dạc giữa sân đông người",
        "Khỏi cần mở cửa nữa! Nhờ bác tài nổ máy quay đầu xe chở cô dâu về lại nhà ngoại ngay bây giờ, gia đình tôi không giữ nữa!",
        "Đã coi đồng tiền nặng hơn tình nghĩa thì dừng ngay tại đây! Bác tài cho xe lăn bánh rời khỏi sân giùm tôi, mời hai họ vào trong dự tiệc bình thường!"),
    mk_clip("v05", "w07", 6, "WIDE", "v5bo2", ["kieu", "quan"],
        "Toàn cảnh sân cổng biệt thự đông người, cô dâu @kieu bên trái hoảng hốt bước vội từ xe hoa xuống định chạy theo gọi với nhưng chú rể @quan bên phải đã dứt khoát xoay người bước thẳng về phía đại sảnh không ngoảnh lại.",
        "Cô dâu hoảng hốt gọi với theo",
        "Khoan đã anh Quân ơi! Đứng lại nghe em giải thích một câu đã, sao tự nhiên anh nói hủy hôn là quay lưng bỏ vào trong thật vậy?!",
        "Anh Quân ơi đừng bỏ đi mà! Em chỉ nghe lời bạn thử lòng anh một chút thôi chứ đâu có ý hủy đám cưới của tụi mình đâu anh!"),
]

out_json = os.path.join(BASE_DIR, "flow_v2_wide_crowd_jobs_9x16.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(new_jobs, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(new_jobs)} V2 Wide/Crowd/Multi-Location Flow jobs -> {out_json}")
