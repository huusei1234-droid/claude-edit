# -*- coding: utf-8 -*-
"""
Build Asset Boards & Reference-Locked Shot Specs for all 6 Million-View K4 Episodes (`k01..k06` — `261128`).
"""
import json, os, shutil, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"C:\AI\full studio\output\k4-6-reels-261128"
sys.path.insert(0, BASE_DIR)
from episodes_k01_to_k06_spec import EPISODES_261128, CHARACTER_SHEETS_MAP, LOCATION_SETS_MAP

CHAR_DRIVE     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"
CAST_FACE_DIR  = os.path.join(BASE_DIR, "cast_clean")
CAST_BODY_DIR  = os.path.join(BASE_DIR, "cast_fullbody")
PAIR_DIR       = os.path.join(BASE_DIR, "cast_pairs")
SETS_DIR       = os.path.join(BASE_DIR, "sets")
BOARDS_DIR     = os.path.join(BASE_DIR, "assetboards")
ART_DIR        = r"C:\Users\001\.gemini\antigravity\brain\f4888e86-3baf-4f6d-a99b-37fec920ebdf"
DU_AN_DIR      = r"C:\AI\full studio\03_Du_An\261128-k4-6-tap-trieu-view"

for d in (CAST_FACE_DIR, CAST_BODY_DIR, PAIR_DIR, SETS_DIR, BOARDS_DIR, ART_DIR, DU_AN_DIR):
    os.makedirs(d, exist_ok=True)

CAMERA_DESC = {
    "WIDE": "TOÀN CẢNH RỘNG (WIDE ESTABLISHING SHOT, ống kính 24mm lấy trọn toàn thân nhân vật từ đầu đến chân và không gian căn phòng/sân nhà). Khung hình điện ảnh sạch vững chãi, không cắt cụt chân, tuyệt đối không xuất hiện máy quay hay thiết bị đoàn phim trong hình, một cảnh liền mạch không tự chia shot.",
    "WIDE_CROWD": "ĐẠI CẢNH RỘNG ĐÔNG NGƯỜI (WIDE CROWD ESTABLISHING SHOT, ống kính góc rộng 24mm thấy trọn toàn thân các nhân vật chính ở tiền cảnh và họ hàng quan khách tự nhiên ở hậu cảnh). Một cảnh liền mạch không chia shot.",
    "MED": "TRUNG CẢNH HÀNH ĐỘNG (MEDIUM TWO-SHOT từ ngang hông/thắt lưng trở lên, thấy rõ cử chỉ tay, đạo cụ và tương tác hình thể giữa các nhân vật). Máy giữ ổn định ngang tầm mắt, một cảnh liền mạch.",
    "CU": "CẬN CẢNH ĐẶC TẢ CẢM XÚC (EMOTIONAL CLOSE-UP từ ngực lên mặt, lấy nét sắc sảo vào ánh mắt, cơ mặt và khẩu hình môi). Hậu cảnh xóa phông điện ảnh nhẹ, máy tĩnh vững chãi, một cảnh liền mạch.",
}


def split_k4_sheet_exact(src_path, face_dst, body_dst, special_mode=None):
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    if special_mode == "5panel":
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


def prepare_characters_and_sets():
    for ckey, (fn, smode) in CHARACTER_SHEETS_MAP.items():
        fdst = os.path.join(CAST_FACE_DIR, f"k4_{ckey}.jpg")
        bdst = os.path.join(CAST_BODY_DIR, f"k4_{ckey}_full.jpg")
        if os.path.exists(fdst) and os.path.exists(bdst):
            continue
        sp = os.path.join(CHAR_DRIVE, fn)
        if not os.path.exists(sp):
            raise FileNotFoundError(f"Missing K4 character sheet: {sp}")
        split_k4_sheet_exact(sp, fdst, bdst, special_mode=smode)

    set_jpg = {}
    for skey, src in LOCATION_SETS_MAP.items():
        dst = os.path.join(SETS_DIR, f"{skey}.jpg")
        if not os.path.exists(dst):
            im = Image.open(src).convert("RGB")
            im.thumbnail((1280, 1280), Image.LANCZOS)
            im.save(dst, "JPEG", quality=93)
        set_jpg[skey] = dst
    return set_jpg


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


def build_asset_board(ep_id, cfg, set_jpg):
    items = cfg["board_items"]
    cols = 3
    rows = (len(items) + cols - 1) // cols
    cw, ch = 360, 420
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
        ip = set_jpg[key] if key in set_jpg else get_char_img(key, True)[0]
        im = Image.open(ip).convert("RGB")
        im.thumbnail((cw - 20, ch - 46), Image.LANCZOS)
        board.paste(im, (x0 + (cw - 20 - im.width) // 2, y0 + 30))
        draw.text((x0 + 4, y0 + 5), lbl, fill=(130, 235, 255), font=fs)
    out = os.path.join(BOARDS_DIR, f"AssetBoard_{ep_id.upper()}.jpg")
    board.save(out, "JPEG", quality=92)
    shutil.copy2(out, os.path.join(ART_DIR, f"AssetBoard_{ep_id.upper()}.jpg"))
    shutil.copy2(out, os.path.join(DU_AN_DIR, f"AssetBoard_{ep_id.upper()}.jpg"))


def build_episodes(ep_ids):
    set_jpg = prepare_characters_and_sets()
    batch_jobs = []
    for ep_id in ep_ids:
        cfg = EPISODES_261128[ep_id]
        build_asset_board(ep_id, cfg, set_jpg)
        ep_jobs = []
        raw_dir = os.path.join(BASE_DIR, ep_id, "raw_9x16")
        os.makedirs(raw_dir, exist_ok=True)

        for sid, scale, skey, char_keys, spatial, action, speaker, dlg in cfg["shots"]:
            is_wide = scale in ("WIDE", "WIDE_CROWD", "MED")
            wc = len(dlg.split()) if dlg else 0
            sec = 5 if (not speaker or not dlg) else (6 if wc <= 14 else (7 if wc <= 16 else 8))

            set_path = set_jpg[skey]
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

            action_block = (
                f"Ngay từ 0.2 giây đầu cảnh, {action} "
                f"Nhân vật nói dứt khoát, rõ chữ trọn vẹn câu thoại trong khoảng 4.2 giây đầu rồi khép môi tự nhiên, giữ ánh mắt cảm xúc nhìn đối phương trong 2 giây cuối cảnh (tuyệt đối không để câu nói kéo sát cuối video, không nói lặp lại câu)."
            )
            thoai_block = (
                f"THOẠI TRỰC TIẾP (NÓI ĐÚNG MỘT LẦN TRỌN VẸN RỒI KHÉP MÔI):\n"
                f"{speaker}: “{dlg}”\n"
                f"(Giọng tiếng Việt truyền cảm tự nhiên như phim truyền hình người thật, lip-sync khớp chính xác từng âm tiết từ đầu tới chữ cuối cùng, nói dứt câu là khép môi nghỉ nhịp thở cuối cảnh; các nhân vật khác lắng nghe không mở miệng nói chèn)."
            )

            prompt_v1 = (
                f"Tạo video {sec} giây, photorealistic live-action người Việt Nam thật, phong cách phim truyền hình tâm lý gia đình Việt Nam chất lượng điện ảnh 8k, tỷ lệ dọc 9:16.\n\n"
                f"IMAGE XUẤT HIỆN:\n{img_lines}\n\n"
                f"REFERENCE:\nSử dụng đúng 100% khuôn mặt, kiểu tóc, độ tuổi, vóc dáng và trang phục từ image reference đã đính kèm. Không tự ý đổi quần áo, không thêm người lạ, mặt bàn gọn gàng tuyệt đối không có hộp giấy hay túi quà ngoài kịch bản.\n\n"
                f"BỐI CẢNH:\nĐặt đúng trong không gian kiến trúc và ánh sáng của BO-1 (image 1).\n\n"
                f"CHỐT KHÔNG GIAN (GIỮ TRỤC 180 ĐỘ):\n{spatial}\n\n"
                f"CAMERA:\n{CAMERA_DESC[scale]}\n\n"
                f"DIỄN BIẾN:\n{action_block}\n\n"
                f"{thoai_block}\n\n"
                f"YÊU CẦU BẮT BUỘC:\nTUYỆT ĐỐI KHÔNG HIỂN THỊ PHỤ ĐỀ, KHÔNG CHỮ TRÊN MÀN HÌNH (ZERO SUBTITLES, ZERO CAPTIONS, ZERO ON-SCREEN TEXT), không logo/watermark, không hiệu ứng hoạt hình."
            )

            prompt_v2 = (
                prompt_v1.replace("quát", "nói nghiêm nghị")
                         .replace("đập", "đặt xuống")
                         .replace("giật", "kéo")
                         .replace("lấy trộm", "tự ý lấy")
                         .replace("trộm", "lấy")
                         .replace("xúc phạm", "trách lầm")
                         .replace("khinh miệt", "coi nhẹ")
                         .replace("khinh", "xem nhẹ")
                         .replace("tệ bạc", "vô tâm")
                         .replace("bất hiếu", "thiếu hiếu thảo")
                         .replace("cứu con", "giúp con")
                         .replace("mất mạng", "kiệt sức")
                         .replace("đuổi", "bảo về")
            )

            job = {
                "id": f"{ep_id}_{sid}_9x16",
                "episode": ep_id,
                "scene": sid,
                "scale": scale,
                "ratio": "9:16",
                "seconds": sec,
                "outPath": os.path.join(raw_dir, f"{sid}.mp4"),
                "refs": refs,
                "prompt": prompt_v1,
                "prompts": [prompt_v1, prompt_v2],
            }
            ep_jobs.append(job)
            batch_jobs.append(job)

        json.dump(ep_jobs, open(os.path.join(BASE_DIR, f"flow_{ep_id}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Built {ep_id.upper()} ({len(ep_jobs)} shots) -> AssetBoard_{ep_id.upper()}.jpg + flow_{ep_id}.json")

    tag = "_".join(ep_ids)
    out_batch = os.path.join(BASE_DIR, f"flow_batch_{tag}.json")
    json.dump(batch_jobs, open(out_batch, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"=== BUILT {len(batch_jobs)} JOBS FOR [{tag}] -> {out_batch} ===")


if __name__ == "__main__":
    ep_ids = sys.argv[1:] if len(sys.argv) > 1 else [f"k0{i}" for i in range(1, 7)]
    build_episodes(ep_ids)
