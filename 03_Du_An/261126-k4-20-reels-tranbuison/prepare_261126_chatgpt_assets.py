# -*- coding: utf-8 -*-
"""
Master ChatGPT Asset Specification & Splitter for all 20 Episodes (`261126`: `r01..r20`):
- 63 brand-new K4 2-panel character sheets (`G07_06..09`, `G10..G25`) + 7 existing canonical K4 reuses (`G01`, `G03`, `G04`, `G05`, `G08`) = 70 distinct actors!
- 23 bespoke `9:16` Location & Crowd Sets.
- Outputs wave specs:
  - `chatgpt_wave1_r01_r05.json`
  - `chatgpt_wave2_r06_r10.json`
  - `chatgpt_wave3_r11_r15.json`
  - `chatgpt_wave4_r16_r20.json`
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from PIL import Image
from chatgpt_assets_base import (
    CHAR_SPECS_BASE, SET_SPECS_BASE, EXISTING_K4_REUSE, SPLIT_PROMPT_TPL, SET_PROMPT_TPL
)

BASE_DIR = r"C:\AI\full studio\output\k4-20-reels-261126"
NEW_SHEETS_DIR = os.path.join(BASE_DIR, "new_characters_sheets")
SETS_DIR = os.path.join(BASE_DIR, "sets")
os.makedirs(NEW_SHEETS_DIR, exist_ok=True)
os.makedirs(SETS_DIR, exist_ok=True)

EXTRA_CHAR_SPECS_R06_R14 = [
    # --- R06 (G24: Bà Hợi tóc bạc bị chị dâu Lý vu rụng tóc & vợ chồng chú út Đoàn – Trúc đón mẹ về nuôi) ---
    ("r06", "bahoi_me", "G24_01 - Bà Hợi (Mẹ già tóc bạc búi gọn bị chị dâu vu làm rụng tóc - Mẹ Đoàn) [Áo bà ba xám nâu].png",
     "G24", "Bà Hợi (64t)", "Mẹ ruột tóc bạc búi gọn của Đoàn; bị con dâu cả Lý vu làm rụng tóc ra nhà",
     "Subject: Distinct 64-year-old gentle silver-haired Vietnamese mother, pure silver-white hair pulled tightly into a neat bun at the back of her head, humble wrinkled face, patient eyes. Outfit: modest grey-brown cotton long-sleeve button-up grandma blouse and black loose trousers, indoor slippers."),
    ("r06", "ly_cd", "G24_02 - Lý (Chị dâu cả tóc dài uốn nhuộm nâu đanh đá mắng mẹ chồng) [Áo kiểu vàng bơ quần tây].png",
     "G24", "Lý (34t)", "Con dâu cả của bà Hợi; chị dâu đanh đá có mái tóc dài uốn nhuộm nâu hạt dẻ [Tóc xoăn nâu]",
     "Subject: Distinct 34-year-old sharp-tongued Vietnamese eldest daughter-in-law, long voluminous wavy hair dyed medium chestnut-brown cascading over shoulders, annoyed nitpicking expression, gold earrings. Outfit: stylish butter-yellow short-sleeve pleated blouse tucked into black high-waisted trousers, slippers."),
    ("r06", "doan_em", "G24_03 - Đoàn (Người con trai út hiếu thảo đón mẹ về phụng dưỡng - Con bà Hợi - Chồng Trúc) [Polo xanh cổ vịt].png",
     "G24", "Đoàn (29t)", "Con trai út hiếu thảo của bà Hợi; chồng của Trúc [Áo polo xanh cổ vịt]",
     "Subject: Distinct 29-year-old upright filial Vietnamese younger son, clean short black hair, warm firm gaze, NO glasses, clean-shaven. Outfit: neat dark teal-blue collared polo shirt, dark grey chinos, casual leather loafers."),
    ("r06", "truc_ed", "G24_04 - Trúc (Nàng dâu út tinh ý hiếu thảo minh oan cho mẹ chồng - Vợ Đoàn) [Đầm sơ mi xanh pastel].png",
     "G24", "Trúc (27t)", "Vợ hiền sắc sảo của Đoàn; con dâu út thương yêu bà Hợi [Đầm sơ mi xanh nhạt]",
     "Subject: Distinct 27-year-old observant kind-hearted Vietnamese young wife, straight jet-black shoulder-length hair tucked behind ears, gentle intelligent eyes. Outfit: modest pastel sky-blue collared shirt-dress with waist belt, beige flats."),

    # --- R14 (G25: Bà Lành đục thủy tinh thể kho cá mặn giấu 10 triệu phụ con gái Quyên & con rể hiếu thảo Huy) ---
    ("r14", "balanh_me", "G25_01 - Bà Lành (Người mẹ đục thủy tinh thể mắt mờ vẫn nhịn ăn gom mười triệu cho con gái - Mẹ Quyên).png",
     "G25", "Bà Lành (61t)", "Mẹ ruột của Quyên; mẹ vợ của Huy; bị đục thủy tinh thể mắt mờ vẫn thương con bế cháu",
     "Subject: Distinct 61-year-old self-sacrificing Vietnamese mother with mild cataract cloudiness and slightly squinting tired eyes, salt-and-pepper hair tied low, compassionate gentle face, slightly swollen ankles. Outfit: humble muted grey-taupe cotton home button-up set, simple flat sandals, holding a small dark cloth travel bag."),
    ("r14", "quyen_vo", "G25_02 - Quyên (Cô con gái áp lực công việc trót trách mẹ kho cá mặn rồi òa khóc hối hận - Vợ Huy) [Sơ mi be quần âu].png",
     "G25", "Quyên (29t)", "Con gái ruột của bà Lành; vợ của Huy [Áo sơ mi công sở màu be]",
     "Subject: Distinct 29-year-old stressed urban Vietnamese working daughter/wife, medium-length dark hair tied half-up, expressive emotional face. Outfit: smart beige long-sleeve office blouse tucked into black tailored work trousers, wristwatch, low heels."),
    ("r14", "huy_ck", "G25_03 - Huy (Chàng rể tinh tế phát hiện mẹ vợ mờ mắt sưng chân và đưa mẹ đi mổ mắt - Chồng Quyên) [Sơ mi xanh navy].png",
     "G25", "Huy (31t)", "Chồng của Quyên; con rể hiếu thảo thấu hiểu nỗi đau bệnh mắt của bà Lành [Sơ mi xanh navy]",
     "Subject: Distinct 31-year-old warm perceptive Vietnamese son-in-law, neat short side-parted black hair, sincere empathetic eyes, NO glasses, clean-shaven. Outfit: clean dark navy short-sleeve button-up collared shirt, medium-grey dress trousers, dark shoes."),
]

EXTRA_SET_SPECS_R06_R14 = [
    ("r06", "r06bo1", "R06_BO1_PhongKhachNhaChiDauLy",
     SET_PROMPT_TPL.format(desc="Bright realistic Vietnamese middle-class townhouse living-dining room: polished light cream floor tiles, wooden sofa set on one side, dining table in background, warm indoor ceiling lights, clean open foreground floor.")),
    ("r14", "r14bo1", "R14_BO1_PhongKhachCanHoHuyQuyen",
     SET_PROMPT_TPL.format(desc="Warm lived-in Vietnamese young family apartment living room in early evening: comfortable fabric sofa with cushions, baby toy shelf neatly tucked in background corner, warm recessed ceiling lighting, open floor space near doorway.")),
]

ALL_CHAR_SPECS = sorted(CHAR_SPECS_BASE + EXTRA_CHAR_SPECS_R06_R14, key=lambda x: x[0])
ALL_SET_SPECS  = sorted(SET_SPECS_BASE + EXTRA_SET_SPECS_R06_R14, key=lambda x: x[0])

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

def write_wave_chatgpt_specs():
    waves = [
        ("wave1_r01_r05", {f"r{i:02d}" for i in range(1, 6)}),
        ("wave2_r06_r10", {f"r{i:02d}" for i in range(6, 11)}),
        ("wave3_r11_r15", {f"r{i:02d}" for i in range(11, 16)}),
        ("wave4_r16_r20", {f"r{i:02d}" for i in range(16, 21)}),
    ]
    for wname, eps in waves:
        jobs = []
        for ep, key, fn, branch, cname, rel, desc in ALL_CHAR_SPECS:
            if ep in eps:
                jobs.append({
                    "id": f"CHAR_{ep}_{key}",
                    "outPath": os.path.join(NEW_SHEETS_DIR, fn),
                    "ratio": "1:1",
                    "refs": [],
                    "prompt": SPLIT_PROMPT_TPL.format(desc=desc),
                })
        for ep, skey, sbase, sprompt in ALL_SET_SPECS:
            if ep in eps:
                jobs.append({
                    "id": f"SET_{sbase}",
                    "outPath": os.path.join(SETS_DIR, f"{sbase}.png"),
                    "ratio": "9:16",
                    "refs": [],
                    "prompt": sprompt,
                })
        sp = os.path.join(BASE_DIR, f"chatgpt_{wname}.json")
        json.dump(jobs, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Wrote {sp} -> {len(jobs)} jobs")

if __name__ == "__main__":
    write_wave_chatgpt_specs()
