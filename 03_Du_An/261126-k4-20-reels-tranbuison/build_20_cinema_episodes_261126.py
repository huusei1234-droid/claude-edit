# -*- coding: utf-8 -*-
"""
Build Cinema Episodes Per-Wave or All-20 (`build_20_cinema_episodes_261126.py [r01 r02 ...]`):
1. Extracts any needed existing K4 characters from `G:\...\CHARACTER\`.
2. Splits newly generated K4 character sheets (`cast_clean/` + `cast_fullbody/`).
3. Immediately syncs every newly generated K4 character sheet `.png` into `G:\...\CHARACTER\`,
   and updates `character_registry.json` + `00_GIA_PHA_NHAN_VAT_K4.md`!
4. Optimizes `9:16` Location & Crowd Set `.png`s into `1280px` `.jpg`s.
5. Builds Visual `AssetBoard_RXX.jpg` -> saves to `assetboards/` & `ART_DIR`.
6. Generates `flow_rXX.json` + combined `flow_batch_<tag>.json` (`<= 3` refs/shot, `6s–10s` buffered durations).
"""
import json, os, shutil, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"C:\AI\full studio\output\k4-20-reels-261126"
sys.path.insert(0, BASE_DIR)
from episodes_r01_to_r20_spec import EPISODES_261126
from prepare_261126_chatgpt_assets import (
    ALL_CHAR_SPECS, ALL_SET_SPECS, EXISTING_K4_REUSE, split_k4_sheet_exact
)

CAST_FACE_DIR  = os.path.join(BASE_DIR, "cast_clean")
CAST_BODY_DIR  = os.path.join(BASE_DIR, "cast_fullbody")
PAIR_DIR       = os.path.join(BASE_DIR, "cast_pairs")
NEW_SHEETS_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR       = os.path.join(BASE_DIR, "sets")
BOARDS_DIR     = os.path.join(BASE_DIR, "assetboards")
ART_DIR        = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
CHAR_DRIVE     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"

for d in (CAST_FACE_DIR, CAST_BODY_DIR, PAIR_DIR, BOARDS_DIR, ART_DIR):
    os.makedirs(d, exist_ok=True)

CAMERA_DESC = {
    "WIDE": "TOÀN CẢNH RỘNG (WIDE ESTABLISHING SHOT, ống kính 24mm lấy trọn toàn thân nhân vật từ đầu đến chân và không gian căn phòng/sân nhà). Khung hình điện ảnh sạch vững chãi, không cắt cụt chân, tuyệt đối không xuất hiện máy quay hay thiết bị đoàn phim trong hình, một cảnh liền mạch không tự chia shot.",
    "WIDE_CROWD": "ĐẠI CẢNH RỘNG ĐÔNG NGƯỜI (WIDE CROWD ESTABLISHING SHOT, ống kính góc rộng 24mm thấy trọn toàn thân các nhân vật chính ở tiền cảnh và quan khách/người qua lại tự nhiên ở hậu cảnh). Một cảnh liền mạch không chia shot.",
    "MED": "TRUNG CẢNH HÀNH ĐỘNG (MEDIUM TWO-SHOT từ ngang hông/thắt lưng trở lên, thấy rõ cử chỉ tay, đạo cụ và tương tác hình thể giữa các nhân vật). Máy giữ ổn định ngang tầm mắt, một cảnh liền mạch.",
    "CU": "CẬN CẢNH ĐẶC TẢ CẢM XÚC (EMOTIONAL CLOSE-UP từ ngực lên mặt, lấy nét sắc sảo vào ánh mắt, cơ mặt và khẩu hình môi). Hậu cảnh xóa phông điện ảnh nhẹ, máy tĩnh vững chãi, một cảnh liền mạch.",
}

def ensure_existing_k4_extracted():
    for key, fn, smode in EXISTING_K4_REUSE:
        fdst = os.path.join(CAST_FACE_DIR, f"k4_{key}.jpg")
        bdst = os.path.join(CAST_BODY_DIR, f"k4_{key}_full.jpg")
        if os.path.exists(fdst) and os.path.exists(bdst):
            continue
        sp = os.path.join(CHAR_DRIVE, fn)
        assert os.path.exists(sp), f"Missing existing K4 character in CHARACTER/: {sp}"
        split_k4_sheet_exact(sp, fdst, bdst, special_mode=smode)

def sync_and_split_wave_assets(ep_ids):
    ensure_existing_k4_extracted()
    ep_set = set(ep_ids)
    synced_entries = []

    for ep, key, fn, branch, cname, rel, _ in ALL_CHAR_SPECS:
        if ep not in ep_set:
            continue
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
                print(f"[CHARACTER SYNC] Saved -> {fn}")
        synced_entries.append((fn, branch, cname, rel))

    if synced_entries and os.path.isdir(CHAR_DRIVE):
        reg_path = os.path.join(CHAR_DRIVE, "character_registry.json")
        if os.path.exists(reg_path):
            reg = json.load(open(reg_path, encoding="utf-8"))
            by_new = {x["new"]: x for x in reg["items"]}
            for fn, branch, cname, rel in synced_entries:
                by_new[fn] = {"old": fn, "new": fn, "branch": branch, "name": cname, "relation": rel}
            reg["items"] = list(by_new.values())
            reg["total_files"] = len(reg["items"])
            json.dump(reg, open(reg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

        md_path = os.path.join(CHAR_DRIVE, "00_GIA_PHA_NHAN_VAT_K4.md")
        if os.path.exists(md_path):
            md_txt = open(md_path, encoding="utf-8").read()
            new_lines = []
            for fn, branch, cname, rel in synced_entries:
                code_prefix = fn.split(" - ")[0].strip()
                if code_prefix not in md_txt:
                    new_lines.append(f"  - `{code_prefix}`: **{cname}** — {rel} (`{fn}`).")
            if new_lines:
                header = "\n\n---\n\n### Bổ Sung Lô `261126` (20 Tập Trần Bùi Sơn — Nhánh `G10..G25` & `G07_06..09` Đúng Tuổi, Không Trùng Vai)\n\n"
                if "### Bổ Sung Lô `261126`" not in md_txt:
                    md_txt = md_txt.rstrip() + header + "\n".join(new_lines) + "\n"
                else:
                    md_txt = md_txt.rstrip() + "\n" + "\n".join(new_lines) + "\n"
                open(md_path, "w", encoding="utf-8").write(md_txt)
                print(f"[GIA PHA MD] Appended {len(new_lines)} new K4 characters!")

    set_jpg = {}
    for ep, skey, sbase, _ in ALL_SET_SPECS:
        if ep not in ep_set:
            continue
        p_png = os.path.join(SETS_DIR, f"{sbase}.png")
        assert os.path.exists(p_png), f"Missing generated Set PNG: {p_png}"
        p_jpg = os.path.join(SETS_DIR, f"{sbase}.jpg")
        im = Image.open(p_png).convert("RGB")
        im.thumbnail((1280, 1280), Image.LANCZOS)
        im.save(p_jpg, "JPEG", quality=93)
        set_jpg[skey] = p_jpg
    return set_jpg

FORCE_FULLBODY_KEYS = {"bacay_cu"}
FORCE_FACE_KEYS = {"tu_ck", "lam_vo"}

def get_char_img(ckey, is_wide):
    if ckey in FORCE_FACE_KEYS:
        return os.path.join(CAST_FACE_DIR, f"k4_{ckey}.jpg"), f"k4_{ckey}.jpg"
    if is_wide or ckey in FORCE_FULLBODY_KEYS:
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
    cols = 4
    rows = (len(items) + cols - 1) // cols
    cw, ch = 320, 400
    board = Image.new("RGB", (cols * cw, 64 + rows * ch), (16, 18, 24))
    draw = ImageDraw.Draw(board)
    try:
        fh = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 19)
        fs = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 14)
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

def build_episodes(ep_ids):
    set_jpg = sync_and_split_wave_assets(ep_ids)
    batch_jobs = []
    for ep_id in ep_ids:
        cfg = EPISODES_261126[ep_id]
        build_asset_board(ep_id, cfg, set_jpg)
        ep_jobs = []
        raw_dir = os.path.join(BASE_DIR, ep_id, "raw_9x16")
        os.makedirs(raw_dir, exist_ok=True)

        for sid, scale, skey, char_keys, spatial, action, speaker, dlg in cfg["shots"]:
            is_wide = scale in ("WIDE", "WIDE_CROWD", "MED")
            wc = len(dlg.split()) if dlg else 0
            if not speaker or not dlg:
                sec = 6
            elif wc <= 15:
                sec = 8
            elif wc <= 20:
                sec = 9
            else:
                sec = 10

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
                f"YÊU CẦU BẮT BUỘC:\nTUYỆT ĐỐI KHÔNG HIỂN THỊ PHỤ ĐỀ, KHÔNG CHỮ TRÊN MÀN HÌNH (ZERO SUBTITLES, ZERO CAPTIONS, ZERO ON-SCREEN TEXT), không logo/watermark, không hiệu ứng hoạt hình."
            )

            prompt_v2 = (
                prompt_v1.replace("quát", "nói nghiêm nghị")
                         .replace("xô đẩy", "ngăn cản")
                         .replace("chà đạp", "coi nhẹ")
                         .replace("tống cổ", "mời ra ngoài")
                         .replace("ăn cắp", "lấy nhầm")
                         .replace("móc túi", "cầm nhầm")
                         .replace("vu khống", "đổ lỗi")
                         .replace("vu oan", "hiểu lầm")
                         .replace("đồng nát", "lớn tuổi")
                         .replace("nhặt rác", "lao động")
                         .replace("dơ bẩn", "lấm bụi")
                         .replace("khinh miệt", "lạnh nhạt")
                         .replace("hỗn xược", "thiếu lễ phép")
                         .replace("chửi", "trách móc")
                         .replace("độc ác", "ích kỷ")
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
    print(f"\n=== BUILT {len(batch_jobs)} FLOW JOBS FOR [{tag}] -> {out_batch} ===")

if __name__ == "__main__":
    ep_ids = sys.argv[1:] if len(sys.argv) > 1 else [f"r{i:02d}" for i in range(1, 21)]
    build_episodes(ep_ids)
