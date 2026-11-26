"""Pick 1 best dramatic frame from a video and render a 1080x1920 TikTok cover with phrase-safe Vietnamese line breaks."""
import json
import os
import re
import subprocess
import sys
import tempfile
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

TYPO_FIXES = [
    (r"\bnhà trồng\b", "nhà chồng"),
    (r"\bchữ hiêu\b", "chữ hiếu"),
    (r"\btrong nha\b", "trong nhà"),
    (r"\bkhó thể sao\b", "khó thế sao"),
]

# Inseparable Vietnamese compound words & tight collocations (longest first)
COMPOUND_PHRASES = [
    "vô tích sự",
    "trọng nam khinh nữ",
    "ơn sinh thành",
    "cả một đời",
    "khó thế sao",
    "đã đi đâu",
    "300 triệu",
    "nhà chồng",
    "nhà ngoại",
    "nhà nội",
    "nhà vợ",
    "mẹ chồng",
    "bố chồng",
    "ba chồng",
    "em chồng",
    "chị chồng",
    "anh chồng",
    "mẹ ruột",
    "mẹ quê",
    "con dâu",
    "nàng dâu",
    "làm dâu",
    "con ruột",
    "con trai",
    "con gái",
    "con rể",
    "vợ chồng",
    "người dưng",
    "gọi mẹ",
    "gia đình",
    "bữa cơm",
    "vui vẻ",
    "chăm lo",
    "quần quật",
    "cả ngày",
    "lục túi",
    "đáy túi",
    "thứ này",
    "đã lâu",
    "chưa có",
    "động tĩnh",
    "lợi dụng",
    "cái kết",
    "vất vả",
    "ngược xuôi",
    "chỉ lo",
    "đi nhậu",
    "chữ hiếu",
    "nên tròn",
    "chữ nhân",
    "bất nghĩa",
    "túi cá",
    "số tiền",
    "quản lý",
    "chi tiêu",
    "trong nhà",
    "sinh thành",
    "lớn hơn",
    "biển cả",
    "một đời",
    "thả vườn",
    "gà quê",
    "rau sạch",
    "ở cữ",
    "tập 1",
    "tập 2",
    "tập 3",
]

# Natural clause/phrase starters where starting a new line reads very smoothly in Vietnamese
NATURAL_LINE_STARTERS = {
    "nhưng",
    "mà",
    "vẫn",
    "thì",
    "và",
    "cho",
    "vào",
    "với",
    "để",
    "vì",
    "khi",
    "lén",
    "chỉ",
    "chưa",
    "đã",
    "khó",
    "cả",
    "trọng",
    "chi",
}


def clean_title(raw: str) -> str:
    s = raw.strip()
    if s.lower().endswith(".mp4") or "\\" in s or "/" in s:
        s = os.path.basename(s)
        s = re.sub(r"\.mp4$", "", s, flags=re.I)
    s = re.sub(r"#\S+", "", s)
    s = re.sub(r"^\d{6}\s+", "", s)
    s = re.sub(r"\(\s*(?:full|\d+)\s*\)", "", s, flags=re.I)
    s = re.sub(r"\bfull\b$", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" -_,.")
    for pat, rep in TYPO_FIXES:
        s = re.sub(pat, rep, s, flags=re.I)
    return s.strip()


def tokenize_vietnamese_units(title: str) -> list[str]:
    """Group compound Vietnamese words into atomic units so they are never split across lines."""
    words = title.split()
    lower_words = [re.sub(r"[^\w\dàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", "", w.lower()) for w in words]
    phrases_sorted = sorted([p.split() for p in COMPOUND_PHRASES], key=len, reverse=True)

    units = []
    i = 0
    n = len(words)
    while i < n:
        matched_len = 1
        for ph in phrases_sorted:
            k = len(ph)
            if i + k <= n and lower_words[i : i + k] == ph:
                matched_len = k
                break
        unit = " ".join(words[i : i + matched_len])
        # If punctuation ends a clause (comma), keep it attached to this unit
        units.append(unit)
        i += matched_len
    return units


def split_semantic_lines(title: str) -> tuple[list[str], list[str]]:
    """
    Partition Vietnamese title into 2 or 3 phrase-complete lines (never splitting compound words,
    never leaving a 1-syllable orphan line).
    Returns (hook_lines_white, main_lines_gold).
    """
    words = title.split()
    n_syllables = len(words)
    if n_syllables == 0:
        return [], []
    if n_syllables <= 3:
        return [], [title.upper()]
    if n_syllables == 4:
        return [" ".join(words[:2]).upper()], [" ".join(words[2:]).upper()]

    units = tokenize_vietnamese_units(title)
    if len(units) == 1:
        mid = n_syllables // 2
        return [" ".join(words[:mid]).upper()], [" ".join(words[mid:]).upper()]

    target_lines = 2 if n_syllables <= 9 else 3
    target_lines = min(target_lines, len(units))

    def syl_count(line_str: str) -> int:
        return len(line_str.split())

    def score_partition(lines: list[str]) -> float:
        # Reject any line with only 1 syllable or overly long (> 6 syllables when 3 lines, > 6 when 2 lines)
        counts = [syl_count(ln) for ln in lines]
        if any(c < 2 for c in counts):
            return 1e9
        char_lens = [len(ln) for ln in lines]
        if any(cl > 28 for cl in char_lens):
            return 1e8 + max(char_lens) * 100.0

        mean_len = sum(char_lens) / len(char_lens)
        variance = sum((cl - mean_len) ** 2 for cl in char_lens)

        bonus = 0.0
        # Reward breaking right after a comma or before a natural Vietnamese clause/preposition starter
        for idx in range(1, len(lines)):
            prev_ln = lines[idx - 1].strip()
            first_word = re.sub(r"[^\wđàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]", "", lines[idx].split()[0].lower())
            if prev_ln.endswith(","):
                bonus -= 65.0
            if first_word in NATURAL_LINE_STARTERS:
                bonus -= 38.0
        return variance + bonus

    best_lines = None
    best_cost = 1e12
    m = len(units)

    if target_lines == 2:
        for i in range(1, m):
            cand = [" ".join(units[:i]), " ".join(units[i:])]
            c = score_partition(cand)
            if c < best_cost:
                best_cost = c
                best_lines = cand
    else:
        for i in range(1, m - 1):
            for j in range(i + 1, m):
                cand = [" ".join(units[:i]), " ".join(units[i:j]), " ".join(units[j:])]
                c = score_partition(cand)
                if c < best_cost:
                    best_cost = c
                    best_lines = cand

    # Fallback if 2-line partition exceeded 28 chars per line -> try 3 lines
    if best_lines is None or (best_cost >= 1e8 and m >= 3 and target_lines == 2):
        for i in range(1, m - 1):
            for j in range(i + 1, m):
                cand = [" ".join(units[:i]), " ".join(units[i:j]), " ".join(units[j:])]
                c = score_partition(cand)
                if c < best_cost:
                    best_cost = c
                    best_lines = cand

    if not best_lines:
        mid = max(2, n_syllables // 2)
        best_lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    upper_lines = [ln.strip(" ,").upper() for ln in best_lines]
    return [upper_lines[0]], upper_lines[1:]


def score_frame(bgr: np.ndarray) -> float:
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    uy0, uy1 = int(h * 0.14), int(h * 0.58)
    ux0, ux1 = int(w * 0.06), int(w * 0.94)
    roi_gray = gray[uy0:uy1, ux0:ux1]
    sharpness = float(cv2.Laplacian(roi_gray, cv2.CV_64F).var())
    mean_lum = float(np.mean(roi_gray))
    if mean_lum < 35 or mean_lum > 235:
        return -1e9

    ycrcb = cv2.cvtColor(bgr[uy0:uy1, ux0:ux1], cv2.COLOR_BGR2YCrCb)
    skin = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, kernel)
    skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, kernel)

    skin_ratio = float(np.count_nonzero(skin)) / max(1, skin.size)
    if skin_ratio < 0.025:
        return -1e6

    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(skin)
    min_blob_area = int(skin.size * 0.012)
    max_blob_area = int(skin.size * 0.45)
    face_blobs = []
    for lbl in range(1, num_labels):
        area = int(stats[lbl, cv2.CC_STAT_AREA])
        bw = int(stats[lbl, cv2.CC_STAT_WIDTH])
        bh = int(stats[lbl, cv2.CC_STAT_HEIGHT])
        if min_blob_area <= area <= max_blob_area and 0.35 <= (bw / max(1, bh)) <= 2.4:
            face_blobs.append((centroids[lbl][0] / max(1, ux1 - ux0), area))

    face_blobs.sort(key=lambda x: x[1], reverse=True)
    distinct_x = []
    for cx, _ in face_blobs:
        if all(abs(cx - ox) > 0.18 for ox in distinct_x):
            distinct_x.append(cx)

    n_chars = len(distinct_x)
    if n_chars >= 2:
        char_score = 260.0 + min(n_chars, 3) * 45.0
    elif n_chars == 1:
        char_score = 195.0
    else:
        char_score = skin_ratio * 200.0

    sub_band = gray[int(h * 0.66) : int(h * 0.86), int(w * 0.10) : int(w * 0.90)]
    sub_edges = cv2.Canny(sub_band, 150, 245)
    bright_sub = float(np.count_nonzero((sub_band > 235) & (sub_edges > 0))) / max(1, sub_band.size)
    sub_penalty = bright_sub * 2500.0

    return char_score + min(sharpness, 350.0) * 0.35 - sub_penalty


def pick_best_frame(video_path: str, out_jpg: str) -> str:
    dur_str = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        text=True,
    ).strip()
    dur = max(3.0, float(dur_str))

    best_score = -1e12
    best_img = None

    with tempfile.TemporaryDirectory() as tmp:
        pcts = [0.07, 0.13, 0.19, 0.25, 0.31, 0.37, 0.43, 0.49, 0.55, 0.61, 0.67, 0.73, 0.79, 0.85, 0.91]
        for idx, pct in enumerate(pcts, 1):
            t = round(dur * pct, 2)
            p = os.path.join(tmp, f"f{idx}.jpg")
            subprocess.run(
                ["ffmpeg", "-y", "-ss", str(t), "-i", video_path, "-frames:v", "1", p],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if not os.path.exists(p):
                continue
            bgr = cv2.imread(p)
            if bgr is None:
                continue
            sc = score_frame(bgr)
            if sc > best_score:
                best_score = sc
                best_img = bgr

    if best_img is None:
        raise RuntimeError(f"Could not extract a valid frame from {video_path}")

    os.makedirs(os.path.dirname(os.path.abspath(out_jpg)), exist_ok=True)
    if out_jpg.lower().endswith(".png"):
        cv2.imwrite(out_jpg, best_img)
    else:
        cv2.imwrite(out_jpg, best_img, [cv2.IMWRITE_JPEG_QUALITY, 96])
    return out_jpg


if __name__ == "__main__":
    video_arg = sys.argv[1]
    out_png = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "tiktok_cover_preview.png")
    pick_best_frame(video_arg, out_png)
    print(out_png)
