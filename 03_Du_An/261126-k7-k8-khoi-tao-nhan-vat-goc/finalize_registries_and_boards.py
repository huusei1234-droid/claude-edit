# -*- coding: utf-8 -*-
import csv
import json
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = r"C:\AI\full studio\03_Du_An\261126-k7-k8-khoi-tao-nhan-vat-goc"
K7_CHAR_DIR = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\k7 sóng gió mái ấm\CHARACTER"
K8_CHAR_DIR = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\k8 sau cánh cửa nhà\CHARACTER"

K7_ITEMS = [
    {
        "code": "G01_01a",
        "branch": "G01",
        "name": "Bà Mỹ Vân",
        "age": 48,
        "role": "Mẹ chồng",
        "k4_counterpart": "Bà Hạnh (G01_03)",
        "relation": "Mẹ ruột Gia Bảo (G01_02); mẹ chồng Hạ Vi (G01_03)",
        "personality": "Phu nhân giàu sang trẻ đẹp sắc sảo, sĩ diện, khắt khe bắt bẻ con dâu nhưng thương con ruột",
        "file": "G01_01a - Bà Mỹ Vân (Mẹ ruột Gia Bảo - Mẹ chồng Hạ Vi) [Đầm lụa gấm đỏ mận Thiều Hoa].png",
        "shopee_item": "Đầm trung niên nữ chất liệu lụa gấm hoa cao cấp thương hiệu Thiều Hoa DD5L0144",
        "outfit_desc": "Đầm nhung lụa gấm hoa đỏ mận phu nhân hào môn, chuỗi ngọc trai kép & túi xách da",
        "shopee_short_url": "https://shopee.vn/product/395466446/41062390719",
        "shopee_full_url": "https://shopee.vn/Đầm-trung-niên-nữ-chất-liệu-lụa-gấm-hoa-cao-cấp-thương-hiệu-Thiều-Hoa-DD5L0144-i.395466446.41062390719",
    },
    {
        "code": "G01_02a",
        "branch": "G01",
        "name": "Gia Bảo",
        "age": 26,
        "role": "Chồng",
        "k4_counterpart": "Tuấn (G01_04)",
        "relation": "Con trai trưởng bà Mỹ Vân (G01_01); chồng Hạ Vi (G01_03)",
        "personality": "Nam thần tổng tài trẻ điển trai 1m83, điềm đạm lo kinh tế và thẳng thắn bảo vệ vợ",
        "file": "G01_02a - Gia Bảo (Chồng Hạ Vi - Con trai trưởng bà Mỹ Vân) [Áo polo dệt kim xanh navy cổ trắng].png",
        "shopee_item": "Áo Polo Nam Dệt Kim Cao Cấp Phối Cổ Trắng",
        "outfit_desc": "Áo polo dệt kim mịn màu xanh navy phối viền cổ trắng Hàn Quốc, quần âu kem xếp ly",
        "shopee_short_url": "https://shopee.vn/product/1219175223/46107254199",
        "shopee_full_url": "https://shopee.vn/Áo-Polo-Nam-Dệt-Kim-Cao-Cấp-Phối-Cổ-Trắng-i.1219175223.46107254199",
    },
    {
        "code": "G01_03a",
        "branch": "G01",
        "name": "Hạ Vi",
        "age": 23,
        "role": "Vợ / Nàng dâu",
        "k4_counterpart": "Thảo (G01_05)",
        "relation": "Vợ Gia Bảo (G01_02); con dâu trưởng bà Mỹ Vân (G01_01)",
        "personality": "Nàng thơ Ulzzang Bạch Nguyệt Quang da trắng sứ tóc nâu hạt dẻ bồng bềnh; hiền lành, tinh tế",
        "file": "G01_03a - Hạ Vi (Vợ Gia Bảo - Con dâu trưởng bà Mỹ Vân) [Váy trễ vai tơ bồng tiểu thư].png",
        "shopee_item": "Váy tiệc trễ vai tơ bồng bềnh tiểu thư sang chảnh HÀNG LOẠI 1",
        "outfit_desc": "Đầm tơ voan nhún trễ vai kem hồng phấn tiểu thư, dây chuyền mảnh & túi mini trắng kem",
        "shopee_short_url": "https://shopee.vn/product/428091817/29105845042",
        "shopee_full_url": "https://shopee.vn/Váy-tiệc-trễ-vai-tơ-bồng-bềnh-tiểu-thư-sang-chảnh-HÀNG-LOẠI-1-i.428091817.29105845042",
    },
]

K8_ITEMS = [
    {
        "code": "G01_01a",
        "branch": "G01",
        "name": "Bà Minh Nguyệt",
        "age": 49,
        "role": "Mẹ chồng",
        "k4_counterpart": "Bà Hạnh (G01_03)",
        "relation": "Mẹ ruột Đình Vũ (G01_02); mẹ chồng Tuệ Nhi (G01_03)",
        "personality": "Quý bà danh gia vọng tộc trẻ đẹp đài các, cầu toàn, giữ lễ nghĩa nghiêm khắc",
        "file": "G01_01a - Bà Minh Nguyệt (Mẹ ruột Đình Vũ - Mẹ chồng Tuệ Nhi) [Đầm lụa gấm xanh lục bảo Thiều Hoa].png",
        "shopee_item": "Đầm trung niên sang trọng chất liệu lụa gấm cao cấp thương hiệu Thiều Hoa DD4L0336",
        "outfit_desc": "Đầm lụa gấm hoa chìm màu xanh lục bảo đính trâm ngọc trai vàng, xách túi trần trám đen",
        "shopee_short_url": "https://shopee.vn/product/395466446/29706682458",
        "shopee_full_url": "https://shopee.vn/Đầm-trung-niên-sang-trọng-chất-liệu-lụa-gấm-cao-cấp-mềm-mượt-thương-hiệu-Thiều-Hoa-DD4L0336-i.395466446.29706682458",
    },
    {
        "code": "G01_02a",
        "branch": "G01",
        "name": "Đình Vũ",
        "age": 27,
        "role": "Chồng",
        "k4_counterpart": "Tuấn (G01_04)",
        "relation": "Con trai trưởng bà Minh Nguyệt (G01_01); chồng Tuệ Nhi (G01_03)",
        "personality": "Nam thần doanh nhân 1m84 lạnh lùng thâm tình, nói ít làm nhiều, luôn che chở bảo vệ vợ",
        "file": "G01_02a - Đình Vũ (Chồng Tuệ Nhi - Con trai trưởng bà Minh Nguyệt) [Áo sơ mi polo băng lụa nâu cafe].png",
        "shopee_item": "Áo sơ mi Polo nam cao cấp kiểu Pháp vải băng lụa không nhăn",
        "outfit_desc": "Áo sơ mi polo ngắn tay chất băng lụa màu nâu cafe trầm lịch lãm, quần âu xám ghi xếp ly",
        "shopee_short_url": "https://shopee.vn/product/423834136/28804087094",
        "shopee_full_url": "https://shopee.vn/Áo-sơ-mi-polo-nam-cao-cấp-kiểu-Pháp-mỏng-vừa-vặn-áo-sơ-mi-ngắn-tay-chất-lượng-cao-“băng-lụa-”-vải-mùa-hè-thiết-yếu-áo-sơ-mi-nam-i.423834136.28804087094",
    },
    {
        "code": "G01_03a",
        "branch": "G01",
        "name": "Tuệ Nhi",
        "age": 23,
        "role": "Vợ / Nàng dâu",
        "k4_counterpart": "Thảo (G01_05)",
        "relation": "Vợ Đình Vũ (G01_02); con dâu trưởng bà Minh Nguyệt (G01_01)",
        "personality": "Tiểu thư Ulzzang thanh thuần kiêu sa da trắng sứ tóc buộc nửa đầu; thông minh, kiên cường",
        "file": "G01_03a - Tuệ Nhi (Vợ Đình Vũ - Con dâu trưởng bà Minh Nguyệt) [Set dạ tweed tiểu thư chân váy xếp ly].png",
        "shopee_item": "Set dạ Tweed tiểu thư chân váy xếp ly dáng ngắn cổ đính đá phối nơ Hàn Quốc",
        "outfit_desc": "Set dạ Tweed kem trắng viền đính đá phối nơ đen ở cổ + chân váy xếp ly xòe, túi trắng",
        "shopee_short_url": "https://shopee.vn/product/48905200/54202330409",
        "shopee_full_url": "https://shopee.vn/Set-dạ-Tweed-tiểu-thư-chân-váy-xếp-ly-dáng-ngắn-cổ-đính-đá-phối-nơ-hai-màu-dày-dặn-phù-hợp-đi-chơi-hẹn-hò-dạo-phố-i.48905200.54202330409",
    },
]


def load_vn_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def write_channel_meta(channel_id, channel_title, char_dir, items, csv_name, board_name, accent_rgb):
    reg_path = os.path.join(char_dir, "character_registry.json")
    reg_obj = {
        "channel_id": channel_id,
        "channel_title": channel_title,
        "updated_at": "2026-11-26",
        "beauty_standard": "Chuẩn nhan sắc cực phẩm K4 (Thảo Ulzzang Bạch Nguyệt Quang - Tuấn Tổng tài trẻ - Bà Hạnh Phu nhân hào môn)",
        "strict_isolation_rule": f"Vũ trụ nhân vật riêng của {channel_title}. Tuyệt đối không dùng chéo ảnh với K4 hoặc kênh khác. Mọi nhân vật mới sinh ra phải gắn quan hệ gia phả vào G01..G07 và lưu link Shopee.",
        "reserved_branches": {
            "G01": "Nhánh trung tâm nhà nội (Mẹ chồng G01_01, Chồng G01_02, Vợ G01_03, Bố chồng chờ G01_04, Em chồng chờ G01_05, Em rể chờ G01_06, Con nhỏ chờ G01_07..08)",
            "G02": "Nhánh nhà ngoại của Vợ (Mẹ đẻ Vợ G02_01, Chị gái Vợ G02_02, Em Vợ G02_03...)",
            "G03": "Nhánh Cô/Chú ruột bên nội của Chồng",
            "G04": "Nhánh Bác cả bên nội của Chồng",
            "G05": "Nhánh Dì/Bác ruột bên ngoại của Chồng (Chị/em của Mẹ chồng)",
            "G06": "Nhánh họ hàng ở quê của Vợ",
            "G07": "Tuyến Công ty / Sếp / Đồng nghiệp / Hàng xóm",
        },
        "total_files": len(items),
        "items": items,
    }
    with open(reg_path, "w", encoding="utf-8") as f:
        json.dump(reg_obj, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(char_dir, csv_name)
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as cf:
        writer = csv.writer(cf)
        writer.writerow([
            "Mã Nhân Vật",
            "Họ Tên",
            "Tuổi",
            "Vai Vế",
            "Ánh Xạ Từ K4 (Chuyện Trong Nhà)",
            "Quan Hệ Gia Phả",
            "Tên Sản Phẩm Shopee Bán Chạy",
            "Mô Tả Trang Phục",
            "Link Shopee Rút Gọn",
            "Link Shopee Đầy Đủ",
            "Tên File Ảnh Tham Chiếu",
        ])
        for it in items:
            writer.writerow([
                it["code"],
                it["name"],
                it["age"],
                it["role"],
                it["k4_counterpart"],
                it["relation"],
                it["shopee_item"],
                it["outfit_desc"],
                it["shopee_short_url"],
                it["shopee_full_url"],
                it["file"],
            ])

    paths = [os.path.join(char_dir, it["file"]) for it in items]
    if all(os.path.exists(p) for p in paths):
        card_w, card_h = 640, 640
        pad = 32
        header_h = 110
        footer_h = 152
        W = pad * 4 + card_w * 3
        H = header_h + card_h + footer_h + pad
        board = Image.new("RGB", (W, H), (250, 248, 244))
        draw = ImageDraw.Draw(board)

        draw.rectangle([0, 0, W, header_h - 14], fill=accent_rgb)
        f_title = load_vn_font(34, bold=True)
        f_sub = load_vn_font(20, bold=False)
        f_name = load_vn_font(23, bold=True)
        f_meta = load_vn_font(17, bold=False)

        draw.text((pad, 20), f"BẢNG GIA PHẢ NHÂN VẬT GỐC — {channel_title.upper()}", fill=(255, 255, 255), font=f_title)
        draw.text((pad, 64), "Nhánh Trung Tâm G01 (Mẹ Chồng – Chồng – Vợ) · Chuẩn Nhan Sắc K4 · Đồ Bán Chạy Shopee", fill=(242, 236, 228), font=f_sub)

        for idx, (it, img_p) in enumerate(zip(items, paths)):
            x0 = pad + idx * (card_w + pad)
            y0 = header_h
            im = Image.open(img_p).convert("RGB").resize((card_w, card_h), Image.Resampling.LANCZOS)
            board.paste(im, (x0, y0))
            draw.rectangle([x0 - 2, y0 - 2, x0 + card_w + 2, y0 + card_h + 2], outline=accent_rgb, width=3)

            ty = y0 + card_h + 14
            draw.text((x0, ty), f"{it['code']} — {it['name']} ({it['age']}t · {it['role']})", fill=accent_rgb, font=f_name)
            draw.text((x0, ty + 34), f"Quan hệ: {it['relation']}", fill=(45, 45, 45), font=f_meta)
            draw.text((x0, ty + 62), f"Đồ Shopee: {it['outfit_desc'][:58]}...", fill=(75, 75, 75), font=f_meta)
            draw.text((x0, ty + 90), f"Link: {it['shopee_short_url']}", fill=(180, 55, 20), font=f_meta)

        board_path = os.path.join(char_dir, board_name)
        board.save(board_path, "JPEG", quality=95)
        shutil.copy2(board_path, os.path.join(PROJECT_DIR, board_name))
        print(f"[BOARD SAVED] {board_path}")


if __name__ == "__main__":
    write_channel_meta(
        "K7",
        "K7 - Sóng Gió Mái Ấm",
        K7_CHAR_DIR,
        K7_ITEMS,
        "shopee_links_k7.csv",
        "00_BANG_GIA_PHA_NHAN_VAT_K7.jpg",
        (122, 28, 48),
    )
    write_channel_meta(
        "K8",
        "K8 - Sau Cánh Cửa Nhà",
        K8_CHAR_DIR,
        K8_ITEMS,
        "shopee_links_k8.csv",
        "00_BANG_GIA_PHA_NHAN_VAT_K8.jpg",
        (22, 78, 68),
    )
    print("ALL_META_V2_DONE")
