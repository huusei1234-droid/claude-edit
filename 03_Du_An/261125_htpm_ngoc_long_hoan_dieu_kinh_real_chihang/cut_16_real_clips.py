# -*- coding: utf-8 -*-
"""
Cut 16 100%-REAL-CAMERA 24fps 1080x1920 clips onto local SSD D: using RTX 4070 h264_nvenc:
- Video 1 (Ngọc Long Hoàn, 40.75s): 8 fast-paced real cuts; Husband (Anh Hải) ONLY in final scene NLH3_C08!
- Video 2 (Điều Kinh HT, 36.75s): 8 fast-paced real cuts; 0% Husband anywhere!
- Zero AI face generation — 100% real CEO Nguyễn Thị Hằng & real hand-shot product B-roll!
"""
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

BASE = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma")
V2_ROOT = Path(r"d:\AI\full studio\output\htpm-couple-nlh-dk-v2-261125")
PROBE_DIR = V2_ROOT / "_real_footage_probe"
PROBE_DIR.mkdir(parents=True, exist_ok=True)

NLH_VID_DIR = V2_ROOT / "c01_ngoc_long_hoan" / "07_HyperFrames_Project" / "assets" / "videos"
DK_VID_DIR = V2_ROOT / "c02_dieu_kinh_ht" / "07_HyperFrames_Project" / "assets" / "videos"
NLH_VID_DIR.mkdir(parents=True, exist_ok=True)
DK_VID_DIR.mkdir(parents=True, exist_ok=True)


def encode_clip(src: Path, dst: Path, ss: float, raw_dur: float, out_dur: float, vf_chain: str):
    """Cut from src [ss, ss+raw_dur], stretch/trim smoothly to out_dur+0.35s @ 24fps CFR with h264_nvenc."""
    pts_factor = (out_dur + 0.35) / raw_dur
    full_vf = f"{vf_chain},setpts={pts_factor:.4f}*PTS,fps=24,setsar=1,format=yuv420p"
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{ss:.2f}", "-t", f"{raw_dur:.2f}", "-i", str(src),
        "-an", "-vf", full_vf,
        "-t", f"{out_dur + 0.30:.2f}", "-r", "24", "-fps_mode", "cfr",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-g", "24",
        str(dst),
    ]
    subprocess.run(cmd, check=True)
    print(f"  [OK] {dst.name} ({dst.stat().st_size/1024/1024:.2f} MB)", flush=True)


def main():
    sc = BASE / r"06. Video Quay Gốc\260800 - Showcase Chủ Tịch Tháng 8"
    q_today = BASE / r"06. Video Quay Gốc\261125"
    q_0709 = BASE / r"06. Video Quay Gốc\260709 - Quay Chị Hằng"
    qt_root = BASE / r"06. Video Quay Gốc\Kho Footage Quay Tay"
    fin_ch = BASE / r"05. Video Hoàn Thiện\Final Video Chị Hằng"

    # =========================================================================
    # 1. NGỌC LONG HOÀN — 8 REAL CLIPS (Total = 40.75s; Husband ONLY in C08!)
    # =========================================================================
    print("=== CUTTING 8 REAL CLIPS FOR NGỌC LONG HOÀN ===")
    # C01 (0.0 -> 4.8s, dur=4.8s): Real Chị Hằng in Executive Suite (C4136 silent smiling intro 0.05..1.55s slowed smoothly + subtle zoom)
    encode_clip(
        q_today / "C4136.MP4", NLH_VID_DIR / "NLH3_C01.mp4",
        ss=0.05, raw_dur=1.45, out_dur=4.80,
        vf_chain="scale=1134:2016,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.35",
    )
    # C02 (4.8 -> 10.0s, dur=5.2s): Real Chị Hằng standing on Nha Trang Villa balcony overlooking bay & mountains (SC/C0984.MP4 1920x1080 -> 9:16)
    encode_clip(
        sc / "C0984.MP4", NLH_VID_DIR / "NLH3_C02.mp4",
        ss=0.50, raw_dur=5.20, out_dur=5.20,
        vf_chain="scale=-2:1920,crop=1080:1920:(iw-1080)*0.44:0",
    )
    # C03 (10.0 -> 14.5s, dur=4.5s): Real Chị Hằng in sunlit Nha Trang Villa garden (SC/C0989.MP4 1920x1080 -> 9:16)
    encode_clip(
        sc / "C0989.MP4", NLH_VID_DIR / "NLH3_C03.mp4",
        ss=1.00, raw_dur=4.50, out_dur=4.50,
        vf_chain="scale=-2:1920,crop=1080:1920:(iw-1080)*0.45:0",
    )
    # C04 (14.5 -> 19.0s, dur=4.5s): Real Chị Hằng relaxing in sunlit Nha Trang Villa courtyard (SC/C0995.MP4 1920x1080 -> 9:16)
    encode_clip(
        sc / "C0995.MP4", NLH_VID_DIR / "NLH3_C04.mp4",
        ss=0.80, raw_dur=4.50, out_dur=4.50,
        vf_chain="scale=-2:1920,crop=1080:1920:(iw-1080)*0.58:0",
    )
    # C05 (19.0 -> 22.5s, dur=3.5s): Real Hand-Shot Ngọc Long Hoàn bottle in manicured hands (250903 NLH/C0304.MP4 9:16)
    encode_clip(
        qt_root / r"250903 NLH\C0304.MP4", NLH_VID_DIR / "NLH3_C05.mp4",
        ss=0.60, raw_dur=3.50, out_dur=3.50,
        vf_chain="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
    )
    # C06 (22.5 -> 25.5s, dur=3.0s): Real Hand-Shot Ngọc Long Hoàn rustic wood sunlight (250820 NLH quay tay/C0101.MP4 9:16)
    encode_clip(
        qt_root / r"250820 NLH quay tay\C0101.MP4", NLH_VID_DIR / "NLH3_C06.mp4",
        ss=0.50, raw_dur=3.00, out_dur=3.00,
        vf_chain="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
    )
    # C07 (25.5 -> 33.25s): Split into C07A (25.5->29.5s Herbal Macro NLH2_C05) + C07B (29.5->33.25s Real Hand-Shot NLH C0305.MP4)
    shutil.copy2(NLH_VID_DIR / "NLH2_C05.mp4", NLH_VID_DIR / "NLH3_C07A.mp4")
    encode_clip(
        qt_root / r"250903 NLH\C0305.MP4", NLH_VID_DIR / "NLH3_C07B.mp4",
        ss=0.80, raw_dur=3.75, out_dur=3.75,
        vf_chain="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
    )
    # C08 (33.25 -> 40.75s, dur=7.5s): ONLY SCENE WITH HUSBAND! Real video of Anh Hải & Chị Hằng hugging at Vinpearl Nha Trang!
    # Crop y=440..1920 (height=1480, width=832) so 100% of old top caption is removed, shifting couple slightly left so End-Card fits right!
    encode_clip(
        fin_ch / "video a hải và chị hằng vinpearl.mp4", NLH_VID_DIR / "NLH3_C08.mp4",
        ss=27.85, raw_dur=3.45, out_dur=7.50,
        vf_chain="crop=832:1480:145:440,scale=1080:1920",
    )

    # =========================================================================
    # 2. ĐIỀU KINH HT — 8 REAL CLIPS (Total = 36.75s; 0% HUSBAND ANYWHERE!)
    # =========================================================================
    print("=== CUTTING 8 REAL CLIPS FOR ĐIỀU KINH HT (SOLO CHỊ HẰNG) ===")
    # C01 (0.0 -> 4.2s, dur=4.2s): Real Chị Hằng in Garden Villa white pearl tweed jacket + laptop (C1275 silent intro 0.05..1.40s)
    encode_clip(
        q_0709 / "C1275.MP4", DK_VID_DIR / "DK3_C01.mp4",
        ss=0.05, raw_dur=1.35, out_dur=4.20,
        vf_chain="scale=1134:2016,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.32",
    )
    # C02 (4.2 -> 8.0s, dur=3.8s): Real Chị Hằng walking gracefully in sunlit Nha Trang Villa glass doorway (SC/C0986.MP4)
    encode_clip(
        sc / "C0986.MP4", DK_VID_DIR / "DK3_C02.mp4",
        ss=0.60, raw_dur=3.80, out_dur=3.80,
        vf_chain="scale=-2:1920,crop=1080:1920:(iw-1080)*0.50:0",
    )
    # C03 (8.0 -> 11.3s, dur=3.3s): Real Chị Hằng by turquoise Nha Trang bay in breeze (SC/C1005.MP4)
    encode_clip(
        sc / "C1005.MP4", DK_VID_DIR / "DK3_C03.mp4",
        ss=1.20, raw_dur=3.30, out_dur=3.30,
        vf_chain="scale=-2:1920,crop=1080:1920:(iw-1080)*0.52:0",
    )
    # C04 (11.3 -> 14.5s, dur=3.2s): Real Chị Hằng strolling in white dress among Nha Trang palms (SC/C1014.MP4)
    encode_clip(
        sc / "C1014.MP4", DK_VID_DIR / "DK3_C04.mp4",
        ss=0.50, raw_dur=3.20, out_dur=3.20,
        vf_chain="scale=-2:1920,crop=1080:1920:(iw-1080)*0.52:0",
    )
    # C05 (14.5 -> 17.8s, dur=3.3s): Real Hand-Shot Điều Kinh HT bottle in manicured hand (250822 điều kinh HT/C0168.MP4)
    encode_clip(
        qt_root / r"250822 điều kinh HT\C0168.MP4", DK_VID_DIR / "DK3_C05.mp4",
        ss=0.60, raw_dur=3.30, out_dur=3.30,
        vf_chain="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
    )
    # C06 (17.8 -> 21.0s, dur=3.2s): Real Hand-Shot Điều Kinh HT open cap showing herbal pills (250903 Điều kinh quay tay/C0312.MP4)
    encode_clip(
        qt_root / r"250903 Điều kinh quay tay\C0312.MP4", DK_VID_DIR / "DK3_C06.mp4",
        ss=0.60, raw_dur=3.20, out_dur=3.20,
        vf_chain="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
    )
    # C07A (21.0 -> 25.8s, dur=4.8s): Live Dewy Pink Peony & Herbal Macro (DK2_C05) + C07B (25.8 -> 29.75s Real Hand-Shot ĐK C0317.MP4)
    shutil.copy2(DK_VID_DIR / "DK2_C05.mp4", DK_VID_DIR / "DK3_C07A.mp4")
    encode_clip(
        qt_root / r"250903 Điều kinh quay tay\C0317.MP4", DK_VID_DIR / "DK3_C07B.mp4",
        ss=0.60, raw_dur=3.95, out_dur=3.95,
        vf_chain="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
    )
    # C08 (29.75 -> 36.75s, dur=7.0s): SOLO REAL CHỊ HẰNG END-CARD over Nha Trang Ocean Bay (SC/C1008.MP4, framed on left-center so End-Card sits cleanly on right!)
    encode_clip(
        sc / "C1008.MP4", DK_VID_DIR / "DK3_C08.mp4",
        ss=1.00, raw_dur=7.00, out_dur=7.00,
        vf_chain="scale=-2:1920,crop=1080:1920:(iw-1080)*0.66:0",
    )

    # Build 18-tile verification sheet (9 clips per video)
    all_clips = [
        ("NLH_1_Suite", NLH_VID_DIR / "NLH3_C01.mp4"),
        ("NLH_2_Balcony", NLH_VID_DIR / "NLH3_C02.mp4"),
        ("NLH_3_Garden", NLH_VID_DIR / "NLH3_C03.mp4"),
        ("NLH_4_Villa", NLH_VID_DIR / "NLH3_C04.mp4"),
        ("NLH_5_HandBottle", NLH_VID_DIR / "NLH3_C05.mp4"),
        ("NLH_6_WoodSun", NLH_VID_DIR / "NLH3_C06.mp4"),
        ("NLH_7A_Herbs", NLH_VID_DIR / "NLH3_C07A.mp4"),
        ("NLH_7B_HandClose", NLH_VID_DIR / "NLH3_C07B.mp4"),
        ("NLH_8_CoupleEnd", NLH_VID_DIR / "NLH3_C08.mp4"),
        ("DK_1_VillaDesk", DK_VID_DIR / "DK3_C01.mp4"),
        ("DK_2_GlassDoor", DK_VID_DIR / "DK3_C02.mp4"),
        ("DK_3_OceanBay", DK_VID_DIR / "DK3_C03.mp4"),
        ("DK_4_WhiteDress", DK_VID_DIR / "DK3_C04.mp4"),
        ("DK_5_HandBottle", DK_VID_DIR / "DK3_C05.mp4"),
        ("DK_6_HerbalPills", DK_VID_DIR / "DK3_C06.mp4"),
        ("DK_7A_Peony", DK_VID_DIR / "DK3_C07A.mp4"),
        ("DK_7B_HandLabel", DK_VID_DIR / "DK3_C07B.mp4"),
        ("DK_8_SoloEnd", DK_VID_DIR / "DK3_C08.mp4"),
    ]
    tw, th = 220, 390
    sh = Image.new("RGB", (tw * 9, th * 2), (16, 20, 28))
    dr = ImageDraw.Draw(sh)
    for idx, (lbl, mp) in enumerate(all_clips):
        r, c = divmod(idx, 9)
        fj = PROBE_DIR / f"_v3chk_{idx:02d}.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", str(mp), "-frames:v", "1", "-q:v", "3", str(fj)], check=True)
        im = ImageOps.fit(Image.open(fj).convert("RGB"), (tw - 8, th - 28))
        sh.paste(im, (c * tw + 4, r * th + 24))
        dr.text((c * tw + 6, r * th + 4), lbl, fill=(170, 245, 255))
    out_sh = PROBE_DIR / "sheet_18_real_cuts_verify.jpg"
    sh.save(out_sh, quality=90)
    print("SAVED VERIFY SHEET:", out_sh, flush=True)


if __name__ == "__main__":
    main()
