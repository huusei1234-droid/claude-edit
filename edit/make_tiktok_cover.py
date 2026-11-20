"""Extract 3 close-up emotional character frames from a video and render a 1080x1920 cinema poster cover."""
import os
import re
import subprocess
import sys
import tempfile
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\04_Font Chữ TVC & Chữ Gradient"


def clean_title(raw: str) -> str:
    s = os.path.basename(raw)
    s = re.sub(r"\.mp4$", "", s, flags=re.I)
    s = re.sub(r"^\d{6}\s+", "", s)
    s = s.strip()
    # Title Case works best for expressive brush-script calligraphy fonts
    return " ".join(w[:1].upper() + w[1:].lower() if w else "" for w in s.split())


def score_closeup_emotion(bgr: np.ndarray) -> tuple[float, np.ndarray]:
    """Score higher for close-up portraits (shallow DOF center vs blurred edges + skin tone in upper-center)."""
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # Center face/head ROI vs outer background
    cy0, cy1 = int(h * 0.12), int(h * 0.52)
    cx0, cx1 = int(w * 0.22), int(w * 0.78)
    center_roi = gray[cy0:cy1, cx0:cx1]
    center_sharp = float(cv2.Laplacian(center_roi, cv2.CV_64F).var())

    left_edge = gray[cy0:cy1, 0 : int(w * 0.14)]
    right_edge = gray[cy0:cy1, int(w * 0.86) : w]
    edge_sharp = (float(cv2.Laplacian(left_edge, cv2.CV_64F).var()) + float(cv2.Laplacian(right_edge, cv2.CV_64F).var())) / 2.0

    # Skin-tone ratio in YCrCb inside upper-center ROI
    ycrcb = cv2.cvtColor(bgr[cy0:cy1, cx0:cx1], cv2.COLOR_BGR2YCrCb)
    skin_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
    skin_ratio = float(np.count_nonzero(skin_mask)) / max(1, skin_mask.size)

    # Reject frames with almost no skin (empty room / object shots) or overly dark frames
    if skin_ratio < 0.08:
        score = 0.0
    else:
        dof_ratio = min(4.0, (center_sharp + 10.0) / (edge_sharp + 15.0))
        score = skin_ratio * 100.0 * dof_ratio + min(center_sharp, 300.0) * 0.05

    # Compare character ROI histogram (upper-center) so the same actor/outfit isn't picked twice
    roi_bgr = bgr[int(h * 0.10) : int(h * 0.65), int(w * 0.20) : int(w * 0.80)]
    hist = cv2.calcHist([roi_bgr], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]).flatten()
    cv2.normalize(hist, hist)
    return score, skin_ratio, hist


def extract_3_closeups(video_path: str, out_dir: str) -> list[str]:
    dur_str = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        text=True,
    ).strip()
    dur = max(4.0, float(dur_str))

    scored = []
    with tempfile.TemporaryDirectory() as tmp:
        pcts = (0.06, 0.13, 0.20, 0.27, 0.34, 0.41, 0.48, 0.55, 0.62, 0.69, 0.76, 0.83, 0.89, 0.94)
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
            sc, skin_r, hist = score_closeup_emotion(bgr)
            scored.append((sc, skin_r, pct, p, hist))

        # Pick 4 distinct close-up character portraits + 1 wide establishing shot (lowest skin_ratio)
        scored_faces = sorted(scored, key=lambda x: x[0], reverse=True)
        picked = []
        for item in scored_faces:
            sc, skin_r, pct, p, hist = item
            too_close = False
            for _, _, p_pct, _, p_hist in picked:
                sim = float(cv2.compareHist(hist, p_hist, cv2.HISTCMP_CORREL))
                if abs(pct - p_pct) < 0.10 or sim > 0.74:
                    too_close = True
                    break
            if not too_close:
                picked.append(item)
            if len(picked) >= 4:
                break

        while len(picked) < 4 and len(scored_faces) > len(picked):
            for item in scored_faces:
                if item not in picked:
                    picked.append(item)
                    break

        # Wide shot = lowest skin_ratio among remaining frames (room/group establishing shot)
        used_pcts = {x[2] for x in picked}
        wide_candidates = [x for x in scored if x[2] not in used_pcts]
        wide_candidates.sort(key=lambda x: x[1])
        if wide_candidates:
            picked.append(wide_candidates[0])
        elif len(scored_faces) > 4:
            picked.append(scored_faces[-1])

        os.makedirs(out_dir, exist_ok=True)
        out_paths = []
        for i, (_, _, _, p, _) in enumerate(picked, 1):
            suffix = "_wide.jpg" if i == 5 else ".jpg"
            dst = os.path.join(out_dir, f"c{i}{suffix}")
            img = cv2.imread(p)
            cv2.imwrite(dst, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            out_paths.append(dst)
        return out_paths


def split_title_cinema(title: str) -> tuple[str, str]:
    """Split a long Vietnamese title into (Top Accent Hook, Main Dramatic Title)."""
    words = title.split()
    if len(words) <= 5:
        return "", title
    mid = max(4, min(6, round(len(words) * 0.43)))
    return " ".join(words[:mid]), " ".join(words[mid:])


if __name__ == "__main__":
    video_arg = sys.argv[1]
    out_png = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "tiktok_cover_preview.png")
    frames_dir = os.path.join(HERE, ".cover_frames")
    crops = extract_3_closeups(video_arg, frames_dir)
    c4 = crops[3] if len(crops) >= 4 else crops[-1]
    c5_wide = crops[4] if len(crops) >= 5 else crops[-1]
    title = clean_title(video_arg)
    hook_line, main_line = split_title_cinema(title)

    render_js = os.path.join(HERE, "render_cover_poster.mjs")
    subprocess.run(
        ["node", render_js, crops[0], crops[1], crops[2], c4, c5_wide, hook_line, main_line, out_png],
        check=True,
    )
    print(out_png)
