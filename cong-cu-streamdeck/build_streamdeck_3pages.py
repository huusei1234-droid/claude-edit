import json
import os
import shutil
import uuid
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_TOOL_DIR = Path(r"d:\AI\full studio\cong-cu-streamdeck")
STAGED_ROOT = OUT_TOOL_DIR / "staged_v3"
PROFILE_UUID = "BC31E860-727A-4D47-8EBF-276D4A834544"
PROFILE_UUID_LOWER = PROFILE_UUID.lower()

PAGE1_UUID = "C3E3AFAA-E139-41A4-BF81-024772CEFB8B"
PAGE2_UUID = "6F68EDD9-E505-4360-8F84-8FFA6E2066A7"
PAGE3_UUID = "8A42F190-7B31-4E88-9C12-55D90E11A303"
DEFAULT_EMPTY_UUID = "1FA1ADB6-A4C5-41B4-9B7C-EC90ECE20FDE"

FONTS_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
FONT_BOLD = str(FONTS_DIR / "BeVietnamPro-ExtraBold.ttf")
FONT_SUB = str(FONTS_DIR / "Montserrat-Bold.ttf")


def hex_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def draw_key_icon(badge_text: str, line1: str, line2: str, accent_hex: str, style: str = "card") -> Image.Image:
    sz = 144
    img = Image.new("RGBA", (sz, sz), (10, 12, 18, 255))
    acc = hex_rgb(accent_hex)

    # Radial/diagonal luxury glow background
    glow = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-20, -35, sz + 20, 95), fill=(acc[0], acc[1], acc[2], 78 if style != "nav" else 115))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, glow)

    d = ImageDraw.Draw(img)
    # Rounded glass border
    border_col = (acc[0], acc[1], acc[2], 195 if style == "nav" else 135)
    d.rounded_rectangle((4, 4, sz - 5, sz - 5), radius=24, outline=border_col, width=3)
    # Top glass highlight bar
    d.rounded_rectangle((18, 8, sz - 18, 12), radius=2, fill=(255, 255, 255, 45))

    # Center icon pill / emblem
    pill_w, pill_h = 98, 46
    px0, py0 = (sz - pill_w) // 2, 18
    d.rounded_rectangle(
        (px0, py0, px0 + pill_w, py0 + pill_h),
        radius=14,
        fill=(acc[0], acc[1], acc[2], 52 if style != "nav" else 92),
        outline=(acc[0], acc[1], acc[2], 210),
        width=2,
    )

    f_badge = ImageFont.truetype(FONT_SUB, 22 if len(badge_text) <= 5 else (17 if len(badge_text) <= 8 else 14))
    bb = d.textbbox((0, 0), badge_text, font=f_badge)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((sz - bw) / 2, py0 + (pill_h - bh) / 2 - bb[1]), badge_text, font=f_badge, fill=(255, 255, 255, 255))

    # Bottom Vietnamese labels (1 or 2 crisp lines)
    f_l1 = ImageFont.truetype(FONT_BOLD, 17 if len(line1) <= 10 else 14)
    b1 = d.textbbox((0, 0), line1, font=f_l1)
    w1 = b1[2] - b1[0]
    y1 = 76 if line2 else 88
    d.text(((sz - w1) / 2, y1 - b1[1]), line1, font=f_l1, fill=(255, 255, 255, 255))

    if line2:
        f_l2 = ImageFont.truetype(FONT_BOLD, 15 if len(line2) <= 11 else 13)
        b2 = d.textbbox((0, 0), line2, font=f_l2)
        w2 = b2[2] - b2[0]
        d.text(((sz - w2) / 2, 103 - b2[1]), line2, font=f_l2, fill=(acc[0] + (255 - acc[0]) // 2, acc[1] + (255 - acc[1]) // 2, acc[2] + (255 - acc[2]) // 2, 255))

    return img


def act_openapp(app_name: str, exe_path: str, img_rel: str, args: str = "", source: str = ""):
    p_fwd = exe_path.replace("\\", "/")
    return {
        "ActionID": str(uuid.uuid4()),
        "LinkedTitle": True,
        "Name": "Open Application",
        "Plugin": {"Name": "Open Application", "UUID": "com.elgato.streamdeck.system.openapp", "Version": "1.0"},
        "Resources": None,
        "Settings": {
            "app_name": app_name,
            "args": args,
            "bring_to_front": True,
            "bundle_id": exe_path,
            "bundle_path": p_fwd,
            "exec": p_fwd,
            "is_bundle": False,
            "long_press": "quit",
            "source": source or p_fwd,
        },
        "State": 0,
        "States": [{"Image": img_rel, "Title": ""}],
        "UUID": "com.elgato.streamdeck.system.openapp",
    }


def act_open_path(target_path: str, img_rel: str):
    return {
        "ActionID": str(uuid.uuid4()),
        "LinkedTitle": True,
        "Name": "Open",
        "Plugin": {"Name": "Open", "UUID": "com.elgato.streamdeck.system.open", "Version": "1.0"},
        "Resources": None,
        "Settings": {"path": f'"{target_path}"'},
        "State": 0,
        "States": [{"Image": img_rel, "Title": ""}],
        "UUID": "com.elgato.streamdeck.system.open",
    }


def act_website(url: str, img_rel: str):
    return {
        "ActionID": str(uuid.uuid4()),
        "LinkedTitle": True,
        "Name": "Website",
        "Plugin": {"Name": "Website", "UUID": "com.elgato.streamdeck.system.website", "Version": "1.0"},
        "Resources": None,
        "Settings": {"browser": "", "openInBrowser": True, "path": url},
        "State": 0,
        "States": [{"Image": img_rel, "Title": ""}],
        "UUID": "com.elgato.streamdeck.system.website",
    }


def act_switch_page(page_index_1based: int, img_rel: str):
    return {
        "ActionID": str(uuid.uuid4()),
        "LinkedTitle": True,
        "Name": "Switch Profile",
        "Plugin": {"Name": "Switch Profile", "UUID": "com.elgato.streamdeck.profile.rotate", "Version": "1.0"},
        "Resources": None,
        "Settings": {"DeviceUUID": "", "PageIndex": page_index_1based, "ProfileUUID": PROFILE_UUID_LOWER},
        "State": 0,
        "States": [{"Image": img_rel, "Title": ""}],
        "UUID": "com.elgato.streamdeck.profile.rotate",
    }


def act_hotkey(vkey: int, qtkey: int, img_rel: str, ctrl: bool = False, shift: bool = False, alt: bool = False, cmd: bool = False):
    mods = (1 if shift else 0) | (2 if ctrl else 0) | (4 if alt else 0) | (8 if cmd else 0)
    empty_slot = {"KeyCmd": False, "KeyCtrl": False, "KeyModifiers": 0, "KeyOption": False, "KeyShift": False, "NativeCode": 146, "QTKeyCode": 33554431, "VKeyCode": -1}
    return {
        "ActionID": str(uuid.uuid4()),
        "LinkedTitle": True,
        "Name": "Hotkey",
        "Plugin": {"Name": "Activate a Key Command", "UUID": "com.elgato.streamdeck.system.hotkey", "Version": "1.0"},
        "Resources": None,
        "Settings": {
            "Coalesce": True,
            "Hotkeys": [
                {
                    "KeyCmd": cmd,
                    "KeyCtrl": ctrl,
                    "KeyModifiers": mods,
                    "KeyOption": alt,
                    "KeyShift": shift,
                    "NativeCode": vkey,
                    "QTKeyCode": qtkey,
                    "VKeyCode": vkey,
                },
                dict(empty_slot),
                dict(empty_slot),
                dict(empty_slot),
            ],
        },
        "State": 0,
        "States": [{"Image": img_rel, "Title": ""}],
        "UUID": "com.elgato.streamdeck.system.hotkey",
    }


def build_pages_spec():
    tlh = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit"
    p1 = {
        "uuid": PAGE1_UUID,
        "name": "Trang Chính - Studio & Ảnh",
        "keys": {
            # Row 0: AI Video & Editing Core
            "0,0": (("STUDIO", "FULL", "STUDIO", "#F5B942", "card"), lambda im: act_openapp("Full Studio", r"d:\AI\full studio\full studido.exe", im)),
            "1,0": (("AGY AI", "ANTIGRAVITY", "CODE & AI", "#8B5CF6", "card"), lambda im: act_openapp("Antigravity", r"C:\Users\Hang thu\AppData\Local\Programs\Antigravity\Antigravity.exe", im)),
            "2,0": (("VOICE", "VOICE", "STUDIO", "#10B981", "card"), lambda im: act_openapp("VoiceStudio", r"C:\Program Files\VoiceStudio\VoiceStudio.exe", im)),
            "3,0": (("CC APP", "MỞ APP", "CAPCUT", "#06B6D4", "card"), lambda im: act_openapp("CapCut", r"C:\Users\Hang thu\AppData\Local\CapCut\Apps\CapCut.exe", im, args="--src3")),
            "4,0": (("CAPCUT >", "BÀN DỰNG", "CAPCUT PRO", "#F97316", "nav"), lambda im: act_switch_page(2, im)),
            # Row 1: Photo Suite (100% preserved)
            "0,1": (("Ps 26", "ADOBE", "PHOTOSHOP", "#3B82F6", "card"), lambda im: act_openapp("Adobe Photoshop 2026", r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe", im)),
            "1,1": (("Lr CC", "ADOBE", "LIGHTROOM", "#38BDF8", "card"), lambda im: act_openapp("Adobe Lightroom", r"C:\Program Files\Adobe\Adobe Lightroom CC\lightroom.exe", im)),
            "2,1": (("C1 PRO", "CAPTURE", "ONE PRO", "#6366F1", "card"), lambda im: act_openapp("Capture One", r"C:\Program Files\Capture One\Capture One\CaptureOne.exe", im)),
            "3,1": (("RAW", "SONY RAW", "VIEWER", "#F59E0B", "card"), lambda im: act_openapp("RAW Viewer", r"C:\Program Files\Sony\RAW Viewer\RAW Viewer.exe", im)),
            "4,1": (("KHO AI >", "TRANG AI", "& KHO EDIT", "#EC4899", "nav"), lambda im: act_switch_page(3, im)),
            # Row 2: Daily Apps & Quick Output Folders
            "0,2": (("ZALO", "NHẮN TIN", "ZALO", "#0EA5E9", "card"), lambda im: act_openapp("Zalo", r"C:\Users\Hang thu\AppData\Local\Programs\Zalo\Zalo.exe", im)),
            "1,2": (("WEB", "TRÌNH DUYỆT", "CỐC CỐC", "#22C55E", "card"), lambda im: act_openapp("hữu - Cốc Cốc", r"C:\Program Files\CocCoc\Browser\Application\browser.exe", im, args='--profile-directory="Default"')),
            "2,2": (("SEARCH", "TÌM FILE", "EVERYTHING", "#FB923C", "card"), lambda im: act_openapp("Everything", r"C:\Program Files (x86)\Everything\Everything.exe", im)),
            "3,2": (("EXPORT", "THƯ MỤC", "XUẤT VIDEO", "#EAB308", "card"), lambda im: act_open_path(r"D:\XUẤT CAPCUT", im)),
            "4,2": (("FINAL", "DRIVE", "VIDEOS FINAL", "#14B8A6", "card"), lambda im: act_open_path(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final", im)),
        },
    }

    p2 = {
        "uuid": PAGE2_UUID,
        "name": "CapCut Pro - Bàn Dựng Nhanh",
        "keys": {
            # Row 0: Primary Cut / Ripple Trim / Export
            "0,0": (("Ctrl+B", "CẮT ĐÔI", "CLIP", "#EF4444", "card"), lambda im: act_hotkey(66, 66, im, ctrl=True)),
            "1,0": (("[ Q ]", "XÓA ĐẦU", "BÊN TRÁI", "#F97316", "card"), lambda im: act_hotkey(81, 81, im)),
            "2,0": (("[ W ]", "XÓA ĐUÔI", "BÊN PHẢI", "#F97316", "card"), lambda im: act_hotkey(87, 87, im)),
            "3,0": (("DEL", "XÓA BỎ", "ĐOẠN CHỌN", "#DC2626", "card"), lambda im: act_hotkey(8, 16777219, im)),
            "4,0": (("Ctrl+E", "XUẤT", "VIDEO MP4", "#10B981", "card"), lambda im: act_hotkey(69, 69, im, ctrl=True)),
            # Row 1: Audio Extract, Compound, Zoom, Auto-Download SFX
            "0,1": (("AUDIO", "TÁCH ÂM", "Ctrl+Shift+S", "#A855F7", "card"), lambda im: act_hotkey(83, 83, im, ctrl=True, shift=True)),
            "1,1": (("Alt+G", "GỘP NHÓM", "COMPOUND", "#3B82F6", "card"), lambda im: act_hotkey(71, 71, im, alt=True)),
            "2,1": (("ZOOM -", "THU NHỎ", "TIMELINE", "#64748B", "card"), lambda im: act_hotkey(189, 45, im, ctrl=True)),
            "3,1": (("ZOOM +", "PHÓNG TO", "TIMELINE", "#94A3B8", "card"), lambda im: act_hotkey(187, 61, im, ctrl=True)),
            "4,1": (("AUTO DL", "TỰ CLICK", "TẢI SFX/BGM", "#F59E0B", "card"), lambda im: act_open_path(tlh + r"\_1_AUTO_CLICK_TAI_TREN_CAPCUT.bat", im)),
            # Row 2: Undo / Redo / Play-Pause / Page Nav
            "0,2": (("Ctrl+Z", "HOÀN TÁC", "UNDO", "#0EA5E9", "card"), lambda im: act_hotkey(90, 90, im, ctrl=True)),
            "1,2": (("REDO", "LÀM LẠI", "Ctrl+Shift+Z", "#38BDF8", "card"), lambda im: act_hotkey(90, 90, im, ctrl=True, shift=True)),
            "2,2": (("SPACE", "PHÁT /", "TẠM DỪNG", "#22C55E", "card"), lambda im: act_hotkey(32, 32, im)),
            "3,2": (("KHO AI >", "SANG KHO", "& WEB AI", "#EC4899", "nav"), lambda im: act_switch_page(3, im)),
            "4,2": (("< HOME", "VỀ TRANG", "CHÍNH", "#CBD5E1", "nav"), lambda im: act_switch_page(1, im)),
        },
    }

    p3 = {
        "uuid": PAGE3_UUID,
        "name": "AI Web & Kho Hậu Kỳ 3.000+ Files",
        "keys": {
            # Row 0: AI Web & Effect/Font Viewers
            "0,0": (("FLOW", "GOOGLE", "FLOW AI", "#4285F4", "card"), lambda im: act_website("https://flow.google.com/", im)),
            "1,0": (("GPT", "CHATGPT", "HTPM", "#10A37F", "card"), lambda im: act_website("https://chatgpt.com/g/g-p-69b17f05d8b481919dd06a0fbdaa4746-hang-thu-pharma", im)),
            "2,0": (("448 FX", "KHO 3D &", "FINAL CUT", "#A855F7", "card"), lambda im: act_open_path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fcp_hyperframes_pack\XEM_TOAN_BO_448_HIEU_UNG_3D_AE_FCP.html", im)),
            "3,0": (("GRAD", "18 FONT &", "GRADIENT", "#F5B942", "card"), lambda im: act_open_path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\XEM_TRUOC_TOAN_BO_18_FONT_VA_GRADIENT.html", im)),
            "4,0": (("SYNC SFX", "ĐỒNG BỘ", "SFX CAPCUT", "#F97316", "card"), lambda im: act_open_path(tlh + r"\_2_CAP_NHAT_NHAC_VA_SFX_TU_CAPCUT.bat", im)),
            # Row 1: 5 Media Vaults in TLH\Edit
            "0,1": (("1340 BGM", "KHO NHẠC", "NỀN BGM", "#3B82F6", "card"), lambda im: act_open_path(tlh + r"\01_Nhạc Nền (BGM)", im)),
            "1,1": (("1043 SFX", "HIỆU ỨNG", "ÂM SFX", "#EC4899", "card"), lambda im: act_open_path(tlh + r"\02_Hiệu Ứng Âm Thanh (SFX)", im)),
            "2,1": (("MEME", "76 CLIP", "MEME CHÈN", "#EAB308", "card"), lambda im: act_open_path(tlh + r"\03_Video Meme & Chèn Cảnh", im)),
            "3,1": (("12 LUT", "CHỈNH MÀU", ".CUBE LUTs", "#14B8A6", "card"), lambda im: act_open_path(tlh + r"\06_LUTs Chỉnh Màu Điện Ảnh (.cube)", im)),
            "4,1": (("BOKEH", "10 VIDEO", "OVERLAYS", "#F59E0B", "card"), lambda im: act_open_path(tlh + r"\07_Video Overlay Bụi Vàng & Light Leaks", im)),
            # Row 2: Brand Kits, Project Folders & Page Nav
            "0,2": (("BRAND", "BRAND KITS", "& TÁCH PNG", "#EF4444", "card"), lambda im: act_open_path(tlh + r"\08_Brand Kits Thương Hiệu & Ảnh PNG", im)),
            "1,2": (("REPO", "THƯ MỤC", "FULL STUDIO", "#6366F1", "card"), lambda im: act_open_path(r"d:\AI\full studio", im)),
            "2,2": (("CLOUD", "DRIVE", "HỒ SƠ DỰ ÁN", "#22C55E", "card"), lambda im: act_open_path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An", im)),
            "3,2": (("< CAPCUT", "SANG DỰNG", "CAPCUT PRO", "#F97316", "nav"), lambda im: act_switch_page(2, im)),
            "4,2": (("< HOME", "VỀ TRANG", "CHÍNH", "#CBD5E1", "nav"), lambda im: act_switch_page(1, im)),
        },
    }

    return [p1, p2, p3]


def main():
    if STAGED_ROOT.exists():
        shutil.rmtree(STAGED_ROOT)
    prof_dir = STAGED_ROOT / f"{PROFILE_UUID}.sdProfile"
    pages_dir = prof_dir / "Profiles"
    pages_dir.mkdir(parents=True, exist_ok=True)

    # Root manifest (preserving exact Device Model & UUID from user's Stream Deck!)
    root_manifest = {
        "Device": {"Model": "20GBA9901", "UUID": "@(1)[4057/128/A2RQA3462I3ASB]"},
        "Name": "Full Studio Pro (3 Trang)",
        "Pages": {
            "Current": PAGE1_UUID.lower(),
            "Default": DEFAULT_EMPTY_UUID.lower(),
            "Pages": [PAGE1_UUID.lower(), PAGE2_UUID.lower(), PAGE3_UUID.lower()],
        },
        "Version": "3.0",
    }
    (prof_dir / "manifest.json").write_text(json.dumps(root_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # Empty default fallback page required by Stream Deck V3
    def_dir = pages_dir / DEFAULT_EMPTY_UUID
    def_dir.mkdir(parents=True, exist_ok=True)
    (def_dir / "manifest.json").write_text(
        json.dumps({"Controllers": [{"Actions": {}, "Type": "Keypad"}], "Icon": "", "Name": ""}, ensure_ascii=False),
        encoding="utf-8",
    )

    pages = build_pages_spec()

    # Visual Preview Canvas (shows all 3 pages 5x3 cleanly!)
    prev_w = 880
    prev_h = 3 * 520 + 60
    preview = Image.new("RGB", (prev_w, prev_h), (11, 14, 22))
    pd = ImageDraw.Draw(preview)
    f_header = ImageFont.truetype(FONT_BOLD, 24)

    for p_idx, p in enumerate(pages):
        p_dir = pages_dir / p["uuid"]
        img_dir = p_dir / "Images"
        img_dir.mkdir(parents=True, exist_ok=True)
        actions = {}

        top_y = 24 + p_idx * 520
        pd.rounded_rectangle((24, top_y, prev_w - 24, top_y + 496), radius=24, fill=(18, 23, 36), outline=(55, 65, 90), width=2)
        pd.text((48, top_y + 18), f"TRANG {p_idx + 1}: {p['name'].upper()}", font=f_header, fill=(247, 201, 105))

        for pos, (icon_args, builder) in p["keys"].items():
            col, row = [int(x) for x in pos.split(",")]
            img_name = f"key_{col}_{row}.png"
            icon_im = draw_key_icon(*icon_args)
            icon_im.save(img_dir / img_name, format="PNG")
            actions[pos] = builder(f"Images/{img_name}")

            # Paste into preview sheet
            kx = 52 + col * 158
            ky = top_y + 66 + row * 138
            # Bezel shadow
            pd.rounded_rectangle((kx - 4, ky - 4, kx + 132, ky + 132), radius=24, fill=(6, 8, 12), outline=(38, 44, 62), width=2)
            thumb = icon_im.resize((128, 128), Image.Resampling.LANCZOS)
            preview.paste(thumb, (kx, ky), thumb)

        page_manifest = {
            "Controllers": [{"Actions": actions, "Type": "Keypad"}],
            "Icon": "",
            "Name": p["name"],
        }
        (p_dir / "manifest.json").write_text(json.dumps(page_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    preview_path = OUT_TOOL_DIR / "XEM_TRUOC_BO_NUT_STREAM_DECK_3_TRANG.png"
    preview.save(preview_path, format="PNG")
    print("[OK] Saved visual preview:", preview_path)

    # Also build importable .streamDeckProfile archive
    archive_path = OUT_TOOL_DIR / "Full_Studio_Pro_3Trang.streamDeckProfile"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in prof_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(STAGED_ROOT).as_posix()
                zf.write(f, rel)
    print("[OK] Built importable archive:", archive_path)

    # Build 1-click safe apply & relaunch script
    bat_code = r'''@echo off
chcp 65001 >nul
echo ====================================================================
echo   ĐANG CẬP NHẬT BỘ 3 TRANG STREAM DECK PRO (45 NÚT + ICON RETINA)
echo ====================================================================
set "SD_APP=%APPDATA%\Elgato\StreamDeck"
set "BACKUP_DIR=%SD_APP%\BackupV3\Backup_Truoc_Khi_Nang_Cap_%RANDOM%"

echo [1/4] Sao lưu cấu hình Stream Deck cũ vào BackupV3...
mkdir "%BACKUP_DIR%" 2>nul
xcopy /E /I /Y "%SD_APP%\ProfilesV3\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" "%BACKUP_DIR%\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" >nul

echo [2/4] Tạm đóng ứng dụng Stream Deck để ghi cấu hình mới...
taskkill /IM StreamDeck.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [3/4] Ghi bộ 3 Trang (45 phím + Icon Studio) vào thiết bị...
rmdir /S /Q "%SD_APP%\ProfilesV3\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" 2>nul
xcopy /E /I /Y "d:\AI\full studio\cong-cu-streamdeck\staged_v3\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" "%SD_APP%\ProfilesV3\BC31E860-727A-4D47-8EBF-276D4A834544.sdProfile" >nul

echo [4/4] Khởi động lại Stream Deck — bàn phím cứng sẽ sáng đủ 15 nút ngay!
start "" "C:\Program Files\Elgato\StreamDeck\StreamDeck.exe"
echo.
echo [HOÀN TẤT 100%%] Hãy nhìn xuống bàn phím Stream Deck của bạn!
timeout /t 3
'''
    bat_path = Path(r"d:\AI\full studio\_AP_DUNG_STREAM_DECK_MOI.bat")
    bat_path.write_text(bat_code, encoding="utf-8")
    print("[OK] Created 1-click launcher:", bat_path)


if __name__ == "__main__":
    main()
