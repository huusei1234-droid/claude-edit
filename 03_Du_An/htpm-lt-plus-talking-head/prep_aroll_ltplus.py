import copy, json, os, subprocess
from PIL import Image, ImageDraw

PROJ_DIR  = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
PY_EXE    = r"d:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
MATTE_PY  = r"d:\AI\full studio\phong-cach\talking-head\tools\matte.py"

def clean_transcript():
    src = os.path.join(AROLL_DIR, "main_cut.json")
    data = json.load(open(src, encoding="utf-8"))

    # Exact word-by-word fixes keyed by (round(start, 2), old_word)
    fixes = {
        (3.10, "tư"): "từ",
        (3.28, "đốt,"): "đâu?",
        (3.98, "khí"): "Khí",
        (7.22, "mẫu"): "máu",
        (7.94, "quá"): "quan",
        (8.14, "nghề"): "hệ",
        (10.06, "hơn"): "hơn.",
        (14.18, "tề"): "tế",
        (14.46, "bao"): "bào",
        (15.90, "hiền"): "hiện",
        (16.66, "ngoài"): "ngoài.",
        (18.94, "trung"): "trùng",
        (20.56, "thư"): "thư.",
        (22.92, "trị"): "trị.",
        (23.96, "triều"): "triệu",
        (24.60, "phiên"): "phiền",
        (24.86, "tói"): "toái,",
        (25.16, "Bác"): "bác",
        (26.26, "giả"): "giá",
        (26.70, "nhân"): "nhân,",
        (26.94, "Ngoài"): "loại",
        (27.44, "trường"): "trừ",
        (27.86, "trung"): "trùng",
        (28.60, "thương"): "thường",
        (29.08, "Để"): "để",
        (29.28, "nơi"): "lựa",
        (29.44, "trong"): "chọn",
        (30.66, "hợp"): "hợp.",
        (31.40, "LTB"): "LT",
        (32.00, "lợt"): "PLUS",
        (32.18, "ăn"): "Hằng",
        (32.34, "thu"): "Thu,",
        (32.56, "Công"): "công",
        (33.68, "hoang"): "Hoàng",
        (34.04, "bã,"): "Bá,",
        (34.70, "ít"): "Ích",
        (34.86, "bổ"): "Mẫu,",
        (35.14, "Khiên"): "Kim",
        (35.56, "ngân"): "Ngân",
        (35.66, "hoa,"): "Hoa,",
        (36.18, "trà"): "Trà",
        (36.38, "xanh,"): "Xanh,",
        (37.02, "trầu"): "Trầu",
        (37.20, "không"): "Không",
        (37.46, "Và"): "và",
        (37.72, "axit"): "Acid",
        (39.52, "thanh"): "thành",
        (39.84, "vần"): "phần",
        (40.78, "đáng"): "đang",
        (41.34, "hiểu"): "hiểu.",
        (43.34, "Đặt"): "đặt",
        (44.32, "tỉnh"): "tính",
        (44.98, "Và"): "và",
        (45.60, "trị"): "trị,",
        (45.92, "Thì"): "thì",
        (48.12, "LTB"): "LT",
        (48.66, "lợt"): "PLUS",
        (49.16, "hàng"): "Hằng",
        (49.28, "thu,"): "Thu,",
        (49.96, "nha"): "nha!",
        (51.52, "phù"): "phụ",
        (52.30, "kênh"): "cần",
        (52.54, "đụng"): "đúng",
        (53.36, "đụng"): "đúng",
        (53.72, "dẫn"): "dẫn.",
        (53.96, "Nhãn"): "Nhắn",
        (54.68, "LTPlet"): "LT PLUS",
        (57.68, "ký"): "kỹ",
        (58.52, "chọn"): "chọn.",
    }

    out = copy.deepcopy(data)
    lines_txt = []
    for seg in out["segments"]:
        new_words = []
        i = 0
        ws = seg["words"]
        while i < len(ws):
            w = copy.deepcopy(ws[i])
            k = (round(w["start"], 2), w["word"])
            # Merge "la" + "tích" -> "Lactic."
            if round(w["start"], 2) == 38.00 and w["word"] == "la" and i + 1 < len(ws) and ws[i + 1]["word"] == "tích":
                w["word"] = "Lactic."
                w["end"] = ws[i + 1]["end"]
                new_words.append(w)
                i += 2
                continue
            if k in fixes:
                w["word"] = fixes[k]
            new_words.append(w)
            i += 1
        seg["words"] = new_words
        seg["text"] = " ".join(x["word"] for x in new_words)
        lines_txt.append(f"[{seg['start']:05.2f}-{seg['end']:05.2f}] {seg['text']}")

    clean_json = os.path.join(AROLL_DIR, "main_cut_clean.json")
    clean_txt  = os.path.join(AROLL_DIR, "main_cut_clean.txt")
    with open(clean_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(clean_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines_txt) + "\n")
    print("Saved spellchecked transcript:", clean_json)
    print("\n".join(lines_txt))

def build_coord_grid():
    mc = os.path.join(AROLL_DIR, "main_cut.mp4")
    imgs = []
    for ts in [1.5, 8.5, 18.0, 26.0, 35.0, 44.0, 48.5, 55.0]:
        p = os.path.join(CHECK_DIR, f"_coord_{ts:.1f}.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(ts), "-i", mc, "-frames:v", "1", p], check=True)
        im = Image.open(p).convert("RGB")
        d = ImageDraw.Draw(im)
        for x in range(100, 1080, 100):
            d.line([(x, 0), (x, 1920)], fill=(255, 255, 0), width=2)
            d.text((x + 4, 980), str(x), fill=(255, 255, 0))
        for y in range(400, 1920, 100):
            d.line([(0, y), (1080, y)], fill=(0, 255, 255), width=2)
            d.text((12, y + 4), str(y), fill=(0, 255, 255))
        d.text((20, 20), f"t={ts:.1f}s", fill=(255, 80, 120))
        imgs.append(im.resize((360, 640)))
        os.remove(p)
    grid = Image.new("RGB", (360 * 4, 640 * 2))
    for idx, im in enumerate(imgs):
        grid.paste(im, ((idx % 4) * 360, (idx // 4) * 640))
    gp = os.path.join(CHECK_DIR, "box_coords_grid.jpg")
    grid.save(gp, quality=90)
    print("Saved coordinate grid:", gp)

def extract_parallel_matte():
    mc = os.path.join(AROLL_DIR, "main_cut.mp4")
    mout = os.path.join(AROLL_DIR, "main_cut_matte.mp4")
    if os.path.exists(mout) and os.path.getsize(mout) > 1_000_000:
        print("Matte already exists:", mout)
        return
    p1_in = os.path.join(AROLL_DIR, "_m1_in.mp4")
    p2_in = os.path.join(AROLL_DIR, "_m2_in.mp4")
    p1_out = os.path.join(AROLL_DIR, "_m1_out.mp4")
    p2_out = os.path.join(AROLL_DIR, "_m2_out.mp4")

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mc, "-vf", "trim=start_frame=0:end_frame=888,setpts=PTS-STARTPTS", "-an", "-c:v", "libx264", "-crf", "14", p1_in], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mc, "-vf", "trim=start_frame=888,setpts=PTS-STARTPTS", "-an", "-c:v", "libx264", "-crf", "14", p2_in], check=True)

    j1 = subprocess.Popen([PY_EXE, MATTE_PY, p1_in, p1_out])
    j2 = subprocess.Popen([PY_EXE, MATTE_PY, p2_in, p2_out])
    r1, r2 = j1.wait(), j2.wait()
    if r1 != 0 or r2 != 0:
        raise RuntimeError(f"matte.py failed: {r1}, {r2}")

    lst = os.path.join(AROLL_DIR, "_mconcat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        f.write(f"file '{p1_out}'\nfile '{p2_out}'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", mout], check=True)
    for tmp in [p1_in, p2_in, p1_out, p2_out, lst]:
        if os.path.exists(tmp):
            os.remove(tmp)
    print("Parallel RVM Matte complete:", mout)

if __name__ == "__main__":
    clean_transcript()
    build_coord_grid()
    extract_parallel_matte()
