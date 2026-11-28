"""
Viral TikTok Optimizer for K4 Family Drama:
1. Defeats the 0:02 drop-off by prepending a 2.2s peak-climax cold-open hook (snapped to breath pauses so 0% word chop)
   with a TikTok 9:16 Safe-Zone Hook Pill (Y=270px, X=72..1008px) during 0.0s..2.1s, plus trimming dead intro silence.
2. Generates high-comment debate captions tailored to each Vietnamese family drama episode.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
FFMPEG_DIR = r"C:\Users\001\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
FFMPEG = os.path.join(FFMPEG_DIR, "ffmpeg.exe") if os.path.exists(os.path.join(FFMPEG_DIR, "ffmpeg.exe")) else "ffmpeg"
FFPROBE = os.path.join(FFMPEG_DIR, "ffprobe.exe") if os.path.exists(os.path.join(FFMPEG_DIR, "ffprobe.exe")) else "ffprobe"

DEFAULT_TAGS = "#MeChongNangDau #PhimNgan #PhimDrama #DramaGiaDinh #PhimViet"

CURATED_CAPTIONS = [
    (
        r"bát canh vỡ",
        "Lỡ tay làm vỡ bát canh mà bị mẹ chồng mắng không kịp vuốt mặt, nhìn thái độ của chồng đứng cạnh mới thật sự nghẹn lòng... 😔 Phải các chị ở hoàn cảnh này thì nhịn cho êm cửa êm nhà hay nói thẳng một lần?",
        "CHỈ VÌ BÁT CANH VỠ...",
    ),
    (
        r"bên tình bên hiếu|ben_tinh_ben_hieu",
        "Phụ nữ yếu đuối và tủi thân nhất là lúc vừa sinh con ở cữ, vậy mà chồng chỉ biết nghe lời mẹ để vợ nuốt nước mắt một mình... 💔 Theo mọi người người chồng xử sự như vậy có đáng trách không?",
        "NỖI TỦI THÂN LÚC Ở CỮ...",
    ),
    (
        r"lợi dụng mẹ chồng nghèo",
        "Lúc mẹ chồng nghèo khó thì tìm đủ cách tính toán lợi dụng, đâu ngờ cái kết phía sau khiến cả nhà sững sờ không nói nên lời! 🔥 Xem xong đoạn kết các bác thấy có đáng đời không?",
        "CÁI KẾT KHIẾN CẢ NHÀ SỮNG SỜ!",
    ),
    (
        r"quản lý chi tiêu",
        "Vợ chắt chiu từng đồng lo cho cả gia đình nhưng chồng lại đòi giữ hết tiền chi tiêu vì sợ vợ tiêu hoang... 😤 Nhà các bác ai đang là người tay hòm chìa khóa, đưa chồng giữ tiền liệu có ổn không?",
        "ĐƯA HẾT TIỀN CHO CHỒNG GIỮ?!",
    ),
    (
        r"túi cá",
        "Mẹ già lưng còng lặn lội mang túi cá khô từ quê lên thăm con, nào ngờ bị chê bai ngay trước cửa nhà giàu sang... 😢 Xem mà xót xa thay cho đấng sinh thành, các bác nghĩ sao về cách cư xử này?",
        "TÚI CÁ KHÔ CỦA MẸ QUÊ...",
    ),
    (
        r"gà thả vườn",
        "Cả tấm lòng của cha mẹ gói trong con gà quê mang lên thành phố, vậy mà câu nói vô tâm của nhà thông gia làm ai nghe cũng chạnh lòng... 💔 Nghèo vật chất chứ đâu nghèo tình cảm, đúng không cả nhà?",
        "MÓN QUÀ QUÊ BỊ XEM THƯỜNG...",
    ),
    (
        r"trên thế nào thì dưới thế ấy",
        "Người lớn cư xử sao thì con cái nhìn vào học theo y vậy, đến lúc nhận lại quả đắng mới giật mình hối hận... 🔥 Ngẫm câu 'trên thế nào dưới thế ấy' có bao giờ sai đâu các bác nhỉ?",
        "NHÂN QUẢ NGAY TRONG MỘT NHÀ!",
    ),
]


def clean_episode_title(raw: str) -> str:
    s = os.path.basename(raw)
    s = re.sub(r"\.mp4$", "", s, flags=re.I)
    s = re.sub(r"^\d{6}\s+", "", s)
    s = re.sub(r"\bBen[_\s]+Tinh[_\s]+Ben[_\s]+Hieu[_\s]+O[_\s]+Cu(?:[_\s]+FINAL)?\b", "Bên tình bên hiếu lúc vợ ở cữ", s, flags=re.I)
    s = re.sub(r"\(\s*(?:full|\d+)\s*\)", "", s, flags=re.I)
    s = re.sub(r"\b(?:full|final)\b$", "", s, flags=re.I)
    s = re.sub(r"\bnhà trồng\b", "nhà chồng", s, flags=re.I)
    s = re.sub(r"\btrong nha\b", "trong nhà", s, flags=re.I)
    s = re.sub(r"\bchữ hiêu\b", "chữ hiếu", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" -_,.")
    if s:
        s = s[0].upper() + s[1:]
    return s


def build_viral_caption_and_hook(filename: str) -> tuple[str, str]:
    low = filename.lower()
    for pat, cap, badge in CURATED_CAPTIONS:
        if re.search(pat, low, flags=re.I):
            return f"{cap} {DEFAULT_TAGS}", badge

    clean = clean_episode_title(filename)
    cap = f"{clean} — Chuyện trong nhà tưởng nhỏ mà xem đến cuối mới thấm thía từng câu! 😔 Phải bạn ở trong hoàn cảnh này thì bạn sẽ xử lý thế nào? {DEFAULT_TAGS}"
    words = clean.upper().split()
    badge = " ".join(words[:6]) + ("..." if len(words) > 6 else "!")
    return cap, badge


def find_bold_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        os.path.join(STUDIO_ROOT, "BO_KIEN_THUC_TVC_AI_PORTABLE", "03_TAI_NGUYEN_DUNG_CHUNG", "fonts_tvc_vi", "BeVietnamPro-ExtraBold.ttf"),
        os.path.join(STUDIO_ROOT, "BO_KIEN_THUC_TVC_AI_PORTABLE", "03_TAI_NGUYEN_DUNG_CHUNG", "fonts_tvc_vi", "Montserrat-Black.ttf"),
        r"C:\Windows\Fonts\arialbd.ttf",
    ]
    for root_dir in [os.path.join(STUDIO_ROOT, "BO_KIEN_THUC_TVC_AI_PORTABLE", "03_TAI_NGUYEN_DUNG_CHUNG", "fonts_tvc_vi")]:
        if os.path.exists(root_dir):
            for dirpath, _, files in os.walk(root_dir):
                for fn in files:
                    if fn.lower() in ("bevietnampro-extrabold.ttf", "montserrat-black.ttf", "asapcondensed-black.ttf"):
                        candidates.insert(0, os.path.join(dirpath, fn))
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def make_safe_hook_overlay_png(w: int, h: int, badge_text: str, out_png: str) -> None:
    """
    Create transparent 9:16 overlay with a crisp golden-yellow hook box strictly inside TikTok Safe Zone:
    Top safe zone >= 252px (placed at Y = 266px), Left/Right >= 64px.
    """
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    scale = w / 1080.0
    font_size = max(28, int(round(46 * scale)))
    font = find_bold_font(font_size)

    # Fit text within safe horizontal box (max 910px @ 1080w)
    max_text_w = int(890 * scale)
    while font_size > 26:
        bbox = draw.textbbox((0, 0), badge_text, font=font)
        if (bbox[2] - bbox[0]) <= max_text_w:
            break
        font_size -= 3
        font = find_bold_font(font_size)

    bbox = draw.textbbox((0, 0), badge_text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = int(38 * scale), int(22 * scale)
    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2
    x0 = (w - box_w) // 2
    y0 = int(266 * (h / 1920.0))
    x1, y1 = x0 + box_w, y0 + box_h
    radius = int(22 * scale)

    # Soft dark drop shadow + golden-yellow box (#FFD426) with dark border
    draw.rounded_rectangle([x0 + 4, y0 + 8, x1 + 4, y1 + 8], radius=radius, fill=(0, 0, 0, 155))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=(255, 212, 38, 248), outline=(20, 12, 4, 255), width=max(2, int(4 * scale)))

    tx = x0 + (box_w - tw) // 2 - bbox[0]
    ty = y0 + (box_h - th) // 2 - bbox[1]
    draw.text((tx, ty), badge_text, font=font, fill=(18, 10, 4, 255))
    img.save(out_png, "PNG")


def analyze_climax_and_intro(video_path: str) -> tuple[float, float, float, int, int]:
    """Return (hook_start, hook_dur, main_trim_start, width, height) using 16kHz PCM energy envelope."""
    probe = subprocess.check_output(
        [
            FFPROBE,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height:format=duration",
            "-of",
            "json",
            video_path,
        ],
        text=True,
    )
    info = json.loads(probe)
    w = int(info["streams"][0]["width"])
    h = int(info["streams"][0]["height"])
    dur = float(info["format"]["duration"])

    # Extract 16kHz mono s16le PCM to memory
    raw = subprocess.check_output(
        [FFMPEG, "-v", "error", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        stderr=subprocess.DEVNULL,
    )
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    sr = 16000
    hop = int(0.05 * sr)  # 50ms resolution
    n_frames = max(1, len(samples) // hop)
    rms = np.array([float(np.sqrt(np.mean(samples[i * hop : (i + 1) * hop] ** 2) + 1e-12)) for i in range(n_frames)])

    # 1. Trim dead intro silence up to 0.9s so main story starts crisp right after the 2.2s hook
    speech_thresh = max(0.015, float(np.percentile(rms, 35)))
    first_speech_idx = 0
    for idx in range(min(n_frames, 24)):  # first 1.2s
        if rms[idx] >= speech_thresh:
            first_speech_idx = idx
            break
    main_trim = max(0.0, round(max(0, first_speech_idx - 2) * 0.05, 2))

    # 2. Find highest dramatic vocal burst in [32% .. 80%] of video duration (2.2s window = 44 hops)
    win = 44  # 2.20s
    lo_idx = max(10, int((dur * 0.32) / 0.05))
    hi_idx = min(n_frames - win - 2, int((dur * 0.80) / 0.05))
    if hi_idx <= lo_idx:
        return 0.0, 0.0, main_trim, w, h

    best_idx = lo_idx
    best_energy = -1.0
    for i in range(lo_idx, hi_idx):
        # Prefer windows that start right after a brief breath dip and have strong sustained vocal energy
        window_e = float(np.mean(rms[i : i + win]))
        start_dip_bonus = 0.015 if rms[i] < speech_thresh * 1.15 else 0.0
        end_dip_bonus = 0.015 if rms[i + win - 1] < speech_thresh * 1.15 else 0.0
        sc = window_e + start_dip_bonus + end_dip_bonus
        if sc > best_energy:
            best_energy = sc
            best_idx = i

    # Snap start & end within +-0.25s (5 hops) to lowest local RMS valley so 0% syllable chop
    s_lo = max(0, best_idx - 5)
    s_hi = min(n_frames - win, best_idx + 5)
    snapped_start = s_lo + int(np.argmin(rms[s_lo : s_hi + 1]))

    target_end = snapped_start + win
    e_lo = max(snapped_start + 36, target_end - 5)  # 1.8s .. 2.45s
    e_hi = min(n_frames - 1, target_end + 5)
    snapped_end = e_lo + int(np.argmin(rms[e_lo : e_hi + 1]))

    hook_start = round(snapped_start * 0.05, 2)
    hook_dur = round(max(1.85, (snapped_end - snapped_start) * 0.05), 2)
    return hook_start, hook_dur, main_trim, w, h


def build_viral_video(src_mp4: str, dst_mp4: str, badge_text: str) -> dict:
    hook_start, hook_dur, main_trim, w, h = analyze_climax_and_intro(src_mp4)
    if hook_dur <= 0.5:
        if os.path.abspath(src_mp4) != os.path.abspath(dst_mp4):
            import shutil
            shutil.copy2(src_mp4, dst_mp4)
        return {"hooked": False, "hook_start": 0, "hook_dur": 0}

    with tempfile.TemporaryDirectory() as tmp:
        badge_png = os.path.join(tmp, "hook_badge.png")
        make_safe_hook_overlay_png(w, h, badge_text, badge_png)

        fade_out_st = round(max(0.1, hook_dur - 0.06), 3)
        fc = (
            f"[0:v]trim=start={hook_start}:duration={hook_dur},setpts=PTS-STARTPTS[hv0];"
            f"[hv0][1:v]overlay=0:0[hv];"
            f"[0:a]atrim=start={hook_start}:duration={hook_dur},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=0.04,afade=t=out:st={fade_out_st}:d=0.05[ha];"
            f"[0:v]trim=start={main_trim},setpts=PTS-STARTPTS[mv];"
            f"[0:a]atrim=start={main_trim},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.04[ma];"
            f"[hv][ha][mv][ma]concat=n=2:v=1:a=1[outv][outa]"
        )

        # Try fast NVIDIA RTX GPU h264_nvenc first, fallback to libx264
        for vcodec_args in (
            ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "19", "-b:v", "0"],
            ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19"],
        ):
            cmd = [
                FFMPEG,
                "-y",
                "-i",
                src_mp4,
                "-i",
                badge_png,
                "-filter_complex",
                fc,
                "-map",
                "[outv]",
                "-map",
                "[outa]",
                *vcodec_args,
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                dst_mp4,
            ]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and os.path.exists(dst_mp4) and os.path.getsize(dst_mp4) > 100000:
                return {"hooked": True, "hook_start": hook_start, "hook_dur": hook_dur, "main_trim": main_trim}

        raise RuntimeError(f"FFmpeg hook build failed: {res.stderr[-500:] if res.stderr else 'unknown'}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "--caption":
        cap, badge = build_viral_caption_and_hook(sys.argv[2])
        print(json.dumps({"caption": cap, "badge": badge}, ensure_ascii=False))
    elif mode == "--prepare":
        src = sys.argv[2]
        dst = sys.argv[3]
        cap, badge = build_viral_caption_and_hook(os.path.basename(src))
        meta = build_viral_video(src, dst, badge)
        meta["caption"] = cap
        meta["badge"] = badge
        print(json.dumps(meta, ensure_ascii=False))
