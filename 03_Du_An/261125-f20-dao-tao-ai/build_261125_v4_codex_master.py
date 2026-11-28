import copy, json, math, os, shutil, subprocess, time, uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30.0

DRAFT_NAME    = "261125 F20 Đào Tạo AI Thực Chiến V4"
DRAFTS_ROOT   = Path(r"C:\CapCut Drafts")
APPDATA_ROOT  = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DONOR_DIR     = Path(r"C:\Users\001\.gemini\antigravity\brain\bbab5999-f668-416e-804a-3347740965da\scratch\donor_v1")
BAK_1117_JSON = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\f20-set-qua-2011\1117_F20_CapCut_Backup\draft_content.json")
SCRATCH_DIR   = Path(r"C:\Users\001\.gemini\antigravity\brain\bbab5999-f668-416e-804a-3347740965da\scratch")

RAW_DIR       = Path(r"G:\Other computers\My Computer\F20\video gốc\261125")
TLH_EDIT      = Path(r"G:\Other computers\My Computer\Document HT Media\TLH\Edit")
BGM_PATH      = TLH_EDIT / r"01_Nhạc Nền (BGM)\01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Corporate Background02 (2p19s).mp3"
SFX_DIR       = TLH_EDIT / r"02_Hiệu Ứng Âm Thanh (SFX)"
FONT_SRC_DIR  = TLH_EDIT / r"04_Font Chữ TVC & Chữ Gradient"

# 3 Locally-Cached Pro Vietnamese Fonts in CapCut Desktop:
# 1) Oswald-Bold (Display Tall Impact for Tier-1 Top Keys & Main Titles)
# 2) Montserrat-ExtraBold (Crisp Geometric Sans for Tier-2 Pill Badges)
# 3) BeVietnamPro-Bold (Ultra-readable Vietnamese Subtitle Font)
CC_CACHE_EFF    = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Cache\effect")
OSWALD_DIR      = CC_CACHE_EFF / "7182504807289065985" / "0a5333de6f4d592cb2d2390d68b31efb"
MONTSERRAT_DIR  = CC_CACHE_EFF / "7517455788122705168" / "91d28cfa5e7db054f4872f1ae2417ac2"
BEVIETNAM_DIR   = CC_CACHE_EFF / "7542214368361057553" / "d376267c892ee3a53654ae93a78dcfb7"

OSWALD_DIR.mkdir(parents=True, exist_ok=True)
MONTSERRAT_DIR.mkdir(parents=True, exist_ok=True)
BEVIETNAM_DIR.mkdir(parents=True, exist_ok=True)

if not (OSWALD_DIR / "Oswald-Bold.ttf").exists():
    shutil.copy2(FONT_SRC_DIR / "Oswald-Bold.ttf", OSWALD_DIR / "Oswald-Bold.ttf")
if not (MONTSERRAT_DIR / "Montserrat-Bold.otf").exists():
    shutil.copy2(FONT_SRC_DIR / "Montserrat-ExtraBold.ttf", MONTSERRAT_DIR / "Montserrat-Bold.otf")
if not (BEVIETNAM_DIR / "font.ttf").exists():
    shutil.copy2(FONT_SRC_DIR / "BeVietnamPro-Bold.ttf", BEVIETNAM_DIR / "font.ttf")

FONT_DISPLAY_ID   = "7182504807289065985"
FONT_DISPLAY_PATH = str(OSWALD_DIR / "Oswald-Bold.ttf").replace("\\", "/")

FONT_BADGE_ID     = "7517455788122705168"
FONT_BADGE_PATH   = str(MONTSERRAT_DIR / "Montserrat-Bold.otf").replace("\\", "/")

FONT_SUB_ID       = "7542214368361057553"
FONT_SUB_PATH     = str(BEVIETNAM_DIR / "font.ttf").replace("\\", "/")

CC_EFF_FWD     = "C:/Users/001/AppData/Local/CapCut/User Data/Cache/effect"
ADJUST_RES_ID  = "7501974767453474064"
ADJUST_PATH    = f"{CC_EFF_FWD}/7501974767453474064/20cd8db6531c21bf7e4053026d20e395"
CURVES_PATH    = f"{CC_EFF_FWD}/7501974767453474064/6821a294141131e7c561ff73480449f7"

# =========================================================================
# CODEX x STUDIO LUXURY COLOR PALETTE (Hex -> normalized [R,G,B] floats)
# =========================================================================
def hex_rgb(h: str) -> list[float]:
    h = h.lstrip("#")
    return [round(int(h[0:2], 16) / 255.0, 5), round(int(h[2:4], 16) / 255.0, 5), round(int(h[4:6], 16) / 255.0, 5)]

THEMES = {
    # Theme A: Luxury Champagne Gold (Warning / Numbers / Executive Punch)
    "CHAMPAGNE": {
        "t1_main":   hex_rgb("#FFF6E5"),
        "t1_accent": hex_rgb("#F6C967"),
        "t1_stroke": hex_rgb("#2C1F14"),
        "t1_str_hex":"#2c1f14",
        "t2_fill":   hex_rgb("#FFF8EB"),
        "t2_accent": hex_rgb("#F7D27D"),
        "t2_stroke": hex_rgb("#241A12"),
        "pill_hex":  "#241B14",
        "pill_alpha": 0.86,
    },
    # Theme B: F20 Emerald Mint (AI Brain / Automation / System Solution)
    "EMERALD": {
        "t1_main":   hex_rgb("#F1FFF7"),
        "t1_accent": hex_rgb("#6BF0B0"),
        "t1_stroke": hex_rgb("#053320"),
        "t1_str_hex":"#053320",
        "t2_fill":   hex_rgb("#F2FFF8"),
        "t2_accent": hex_rgb("#8CE8B5"),
        "t2_stroke": hex_rgb("#042819"),
        "pill_hex":  "#063020",
        "pill_alpha": 0.86,
    },
    # Theme C: Bottom Clean Subtitle (Crisp on both white blazer & blue polo)
    "SUB": {
        "main":      hex_rgb("#FFFFFF"),
        "accent":    hex_rgb("#98F2C4"),
        "stroke":    hex_rgb("#0E1722"),
        "str_hex":   "#0e1722",
        "pill_hex":  "#0E1722",
        "pill_alpha": 0.68,
    }
}

FULL_CROP_1_1 = {
    "upper_left_x": 0.0, "upper_left_y": 0.0,
    "upper_right_x": 1.0, "upper_right_y": 0.0,
    "lower_left_x": 0.0, "lower_left_y": 1.0,
    "lower_right_x": 1.0, "lower_right_y": 1.0,
}

BANNED_VISUAL_CLIPS = {
    "IMG_5384.MOV", "IMG_5387.MOV", "IMG_5390.MOV", "IMG_5395.MOV", "IMG_5409.MOV",
    "IMG_5418.MOV", "IMG_5419.MOV", "IMG_5424.MOV", "IMG_5425.MOV", "IMG_5426.MOV",
    "IMG_5440.MOV", "IMG_5444.MOV", "IMG_5445.MOV", "IMG_5380.MOV", "IMG_5438.MOV",
    "IMG_5397.MOV", "IMG_5434.MOV", "IMG_5461.MOV",
}

def uid() -> str:
    return str(uuid.uuid4()).upper()

def us(sec: float) -> int:
    f = int(round(float(sec) * FPS))
    return int(round(f * 1_000_000 / FPS))

def norm_fwd(p: Path) -> str:
    return os.path.normpath(str(p)).replace("\\", "/")

MEDIA_CACHE = {}
def probe_media(path: Path):
    sp = str(path)
    if sp not in MEDIA_CACHE:
        r = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type,width,height:stream_side_data=rotation:format=duration",
            "-of", "json", sp
        ], capture_output=True, text=True, encoding="utf-8", check=True)
        j = json.loads(r.stdout)
        vs = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
        has_aud = any(s.get("codec_type") == "audio" for s in j.get("streams", []))
        w, h = int(vs.get("width") or 1080), int(vs.get("height") or 1920)
        rot = 0
        for sd in vs.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = abs(int(sd["rotation"]))
        if rot in (90, 270):
            w, h = h, w
        dur = float(j.get("format", {}).get("duration", 0.0) or 0.0)
        MEDIA_CACHE[sp] = (w, h, dur, has_aud)
    return MEDIA_CACHE[sp]

PROJECTOR_CLIPS = {"IMG_5377.MOV", "IMG_5381.MOV", "IMG_5382.MOV", "IMG_5399.MOV", "IMG_5428.MOV", "IMG_5468.MOV"}
PORTRAIT_WARM_CLIPS = {"IMG_5405.MOV", "IMG_5406.MOV", "IMG_5407.MOV", "IMG_5408.MOV", "IMG_5414.MOV", "IMG_5420.MOV", "IMG_5421.MOV", "IMG_5462.MOV"}

ZONE_PROFILES = {
    "BLUE_TEAM": {
        "sliders": {
            "brightness": 0.04, "contrast": 0.07, "saturation": 0.07, "sharpen": 0.13,
            "highlight": -0.10, "shadow": 0.10, "white": 0.02, "black": -0.02,
            "clear": 0.09, "temperature": 0.04, "tone": 0.03, "light_sensation": 0.06,
        },
        "hsl": {1: (0, 10, 4), 2: (0, -4, 13), 3: (0, -10, 4), 4: (0, 8, 3), 6: (-2, 12, 6), 7: (0, -14, -4), 8: (0, 0, 0)}
    },
    "PROJECTOR": {
        "sliders": {
            "brightness": 0.05, "contrast": 0.06, "saturation": 0.07, "sharpen": 0.12,
            "highlight": -0.14, "shadow": 0.14, "white": 0.02, "black": -0.02,
            "clear": 0.09, "temperature": 0.02, "tone": 0.04, "light_sensation": 0.08,
        },
        "hsl": {1: (0, 8, 5), 2: (0, -3, 14), 3: (0, -10, 5), 4: (0, 8, 3), 6: (-2, 10, 5), 7: (0, -10, -2), 8: (0, 0, 0)}
    },
    "PORTRAIT_WARM": {
        "sliders": {
            "brightness": 0.05, "contrast": 0.06, "saturation": 0.07, "sharpen": 0.12,
            "highlight": -0.10, "shadow": 0.11, "white": 0.03, "black": -0.02,
            "clear": 0.08, "temperature": 0.04, "tone": 0.04, "light_sensation": 0.08,
        },
        "hsl": {1: (0, 9, 5), 2: (0, -3, 14), 3: (0, -8, 4), 4: (0, 8, 3), 6: (-2, 10, 5), 7: (0, -10, 0), 8: (0, 0, 0)}
    }
}

def get_zone_name(fn: str) -> str:
    if fn in PROJECTOR_CLIPS:
        return "PROJECTOR"
    if fn in PORTRAIT_WARM_CLIPS:
        return "PORTRAIT_WARM"
    return "BLUE_TEAM"


def main():
    d_donor   = json.loads((DONOR_DIR / "draft_content.json").read_text(encoding="utf-8"))
    dmi_donor = json.loads((DONOR_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))
    d_1117    = json.loads(BAK_1117_JSON.read_text(encoding="utf-8"))

    draft_uuid = uid()
    main_tl_id = uid()
    now_s  = int(time.time())
    now_us = int(time.time() * 1_000_000)

    D = copy.deepcopy(d_donor)
    D["id"] = main_tl_id
    D["name"] = ""
    D["canvas_config"] = {"ratio": "original", "width": W, "height": H, "background": None}
    D["fps"] = FPS
    D["render_index_track_mode_on"] = True
    D["free_render_index_mode_on"] = False

    vtrack_tpl = copy.deepcopy(d_donor["tracks"][0])
    vseg_tpl   = copy.deepcopy(d_donor["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(d_donor["materials"]["videos"][0])
    dm_mat_tpl = copy.deepcopy(dmi_donor["draft_materials"][0]["value"][1])

    slider_tpls = {}
    for ef in d_donor["materials"]["effects"]:
        et = ef.get("type")
        if et in ("brightness", "contrast", "saturation", "sharpen", "highlight", "shadow", "white", "black", "clear", "temperature", "tone", "light_sensation") and et not in slider_tpls:
            slider_tpls[et] = copy.deepcopy(ef)
    hsl_tpls = {h["hsl_color_type"]: copy.deepcopy(h) for h in d_donor["materials"]["hsl"]}
    curve_tpl = copy.deepcopy(d_donor["materials"]["color_curves"][0])

    ttrack_tpl = copy.deepcopy(next(t for t in d_1117["tracks"] if t["type"] == "text"))
    tseg_tpl   = copy.deepcopy(ttrack_tpl["segments"][0])
    tmat_tpl   = copy.deepcopy(d_1117["materials"]["texts"][0])

    atrack_tpl = copy.deepcopy(next(t for t in d_1117["tracks"] if t["type"] == "audio"))
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    amat_tpl   = copy.deepcopy(d_1117["materials"]["audios"][0])

    kf_tpl = copy.deepcopy(next(sg["common_keyframes"][0] for tr in d_1117["tracks"] for sg in tr["segments"] if sg.get("common_keyframes")))

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl = {k: copy.deepcopy(d_donor["materials"][k][0]) for k in v_extra_keys if d_donor["materials"].get(k)}
    a_extra_keys = ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl = {
        k: copy.deepcopy(next(x for x in d_1117["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"]))
        for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in d_1117["materials"].get(k, []))
    }

    for k, val in list(D["materials"].items()):
        if isinstance(val, list):
            D["materials"][k] = []

    vmat_map, vos_map, amat_map = {}, {}, {}
    dm_entries = [copy.deepcopy(dmi_donor["draft_materials"][0]["value"][0])]

    def get_or_add_raw_video(fn: str):
        src_path = RAW_DIR / fn
        if not src_path.is_file():
            raise FileNotFoundError(f"Missing raw 261125 source file: {src_path}")
        fwd = norm_fwd(src_path)
        assert "261125/" in fwd
        if fwd in vmat_map:
            return vmat_map[fwd]
        w, h, dur_s, has_aud = probe_media(src_path)
        dur_u = max(33333, us(dur_s))
        mid, uhex, lmid = uid(), uuid.uuid4().hex, str(uuid.uuid4())
        m = copy.deepcopy(vmat_tpl)
        m.update({
            "id": mid, "unique_id": uhex, "local_material_id": lmid,
            "type": "video", "path": fwd, "media_path": "", "local_id": "",
            "material_name": src_path.name, "width": w, "height": h,
            "duration": dur_u, "has_audio": bool(has_aud),
            "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0,
            "audio_fade": None,
        })
        D["materials"]["videos"].append(m)

        dme = copy.deepcopy(dm_mat_tpl)
        dme.update({
            "id": lmid, "file_Path": fwd, "extra_info": src_path.name,
            "duration": dur_u, "width": w, "height": h,
            "metetype": "video", "item_source": 1,
            "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
            "roughcut_time_range": {"start": 0, "duration": dur_u},
            "sub_time_range": {"start": -1, "duration": -1},
        })
        dm_entries.append(dme)
        vmat_map[fwd] = (mid, dur_u, w, h, uhex)
        return mid, dur_u, w, h, uhex

    def get_or_add_raw_voice_from_mov(fn: str):
        mid, dur_u, w, h, uhex = get_or_add_raw_video(fn)
        fwd = norm_fwd(RAW_DIR / fn)
        if fwd in vos_map:
            return vos_map[fwd]
        aid = uid()
        am = copy.deepcopy(amat_tpl)
        am.update({
            "id": aid, "unique_id": uhex, "type": "video_original_sound",
            "name": fn, "duration": dur_u, "path": fwd,
            "category_name": "", "video_id": mid, "local_material_id": "", "check_flag": 1,
        })
        D["materials"]["audios"].append(am)
        vos_map[fwd] = (aid, dur_u)
        return aid, dur_u

    VALID_KF_PROPS = {"KFTypeScaleX", "KFTypeScaleY", "KFTypePositionX", "KFTypePositionY", "KFTypeRotation", "KFTypeAlpha"}
    def make_kf(prop_type: str, pts_sec_val: list[tuple[float, float]]):
        assert prop_type in VALID_KF_PROPS
        kf = copy.deepcopy(kf_tpl)
        kf["id"] = uid()
        kf["material_id"] = ""
        kf["property_type"] = prop_type
        pt_base = copy.deepcopy(kf_tpl["keyframe_list"][0])
        kl = []
        for off_s, val in pts_sec_val:
            pt = copy.deepcopy(pt_base)
            pt["id"] = uid()
            pt["curveType"] = "Line"
            pt["time_offset"] = max(0, us(off_s))
            pt["values"] = [float(val)]
            pt["left_control"] = {"x": 0.0, "y": 0.0}
            pt["right_control"] = {"x": 0.0, "y": 0.0}
            pt["string_value"] = ""
            pt["graphID"] = ""
            kl.append(pt)
        kf["keyframe_list"] = kl
        return kf

    def attach_native_color_grade(refs: list[str], fn: str):
        prof = ZONE_PROFILES[get_zone_name(fn)]
        for stype, sval in prof["sliders"].items():
            if stype not in slider_tpls:
                continue
            ef = copy.deepcopy(slider_tpls[stype])
            ef["id"] = uid()
            ef["value"] = round(float(sval), 4)
            ef["path"] = ADJUST_PATH
            ef["lumi_hub_path"] = f"{ADJUST_PATH}/lumi_hub_path"
            ef["resource_id"] = ADJUST_RES_ID
            ef["effect_id"] = ADJUST_RES_ID
            D["materials"]["effects"].append(ef)
            refs.append(ef["id"])

        for htype, (hue_v, sat_v, light_v) in prof["hsl"].items():
            if htype not in hsl_tpls:
                continue
            hm = copy.deepcopy(hsl_tpls[htype])
            hm["id"] = uid()
            hm["hue"], hm["saturation"], hm["lightness"] = int(hue_v), int(sat_v), int(light_v)
            hm["path"] = ADJUST_PATH
            hm["lumi_hub_path"] = f"{ADJUST_PATH}/lumi_hub_path"
            hm["resource_id"] = ADJUST_RES_ID
            D["materials"]["hsl"].append(hm)
            refs.append(hm["id"])

        cv = copy.deepcopy(curve_tpl)
        cv["id"] = uid()
        cv["path"] = CURVES_PATH
        cv["resource_id"] = ADJUST_RES_ID
        D["materials"]["color_curves"].append(cv)
        refs.append(cv["id"])

    def make_clean_video_seg(fn: str, t0_s: float, dur_s: float, src_in_s: float, spd: float = 1.0, zoom_mode: str = "in"):
        assert fn not in BANNED_VISUAL_CLIPS, f"Banned visual clip {fn}!"
        mid, mat_dur_u, w, h, _ = get_or_add_raw_video(fn)
        tgt_st_u = us(t0_s)
        tgt_du_u = max(33333, us(t0_s + dur_s) - tgt_st_u)
        src_st_u = us(src_in_s)
        src_du_u = us((tgt_du_u / 1e6) * spd)
        if src_st_u + src_du_u > mat_dur_u:
            raise ValueError(f"Clip {fn} overrun: {src_in_s}s + {(src_du_u/1e6):.2f}s > {(mat_dur_u/1e6):.2f}s")

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e)
            em["id"] = uid()
            if k == "speeds":
                em["speed"] = round(spd, 3)
            D["materials"][k].append(em)
            refs.append(em["id"])

        attach_native_color_grade(refs, fn)

        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        seg["clip"]["rotation"] = 0.0
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        seg["hdr_settings"] = {"intensity": 1.0, "mode": 1, "nits": 1000}

        actual_dur_s = tgt_du_u / 1e6
        kfs = []
        if zoom_mode == "punch":
            # Crisp dynamic emphasis push right when a Top Keyphrase pops up!
            kfs.append(make_kf("KFTypeScaleX", [(0.0, 1.00), (0.22, 1.045), (actual_dur_s, 1.072)]))
            kfs.append(make_kf("KFTypeScaleY", [(0.0, 1.00), (0.22, 1.045), (actual_dur_s, 1.072)]))
        elif zoom_mode == "in" and actual_dur_s >= 1.6:
            kfs.append(make_kf("KFTypeScaleX", [(0.0, 1.00), (actual_dur_s, 1.048)]))
            kfs.append(make_kf("KFTypeScaleY", [(0.0, 1.00), (actual_dur_s, 1.048)]))
        elif zoom_mode == "out" and actual_dur_s >= 1.6:
            kfs.append(make_kf("KFTypeScaleX", [(0.0, 1.048), (actual_dur_s, 1.00)]))
            kfs.append(make_kf("KFTypeScaleY", [(0.0, 1.048), (actual_dur_s, 1.00)]))

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": src_st_u, "duration": src_du_u},
            "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
            "speed": round(spd, 3), "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [],
        })
        return seg, tgt_st_u + tgt_du_u

    # =========================================================================
    # 1. DYNAMIC WAVE-PACED SINGLE VISUAL TRACK (22 SHOTS — 0% OVERLAY CHAOS!)
    #    Every Top Keyphrase Jump lands cleanly on a fresh cut + camera push!
    #    8 Flattering Hero Shots of Chị Oanh + 14 Focused F20 Team Shots
    # =========================================================================
    VISUAL_PLAN = [
        # --- HOOK MỞ MÀN NHỊP ĐÔI NHANH (0.00s - 2.75s) ---
        ("IMG_5376.MOV", 1.35, 0.20, 1.00, "in",    "S01: Đại cảnh mở màn F20 nghiêm túc"),
        ("IMG_5405.MOV", 1.40, 0.08, 0.95, "punch", "S02: 🌟 CHỊ OANH #1 — Cận bàn tay gõ MacBook mở màn"),

        # --- MỞ BÀI (2.75s - 12.20s): Nhanh - Nhanh - Chậm + Cut đúng Key #1 @9.76s ---
        ("IMG_5428.MOV", 3.35, 0.45, 1.00, "in",    "S03: 🌟 CHỊ OANH #2 — Chân dung sáng đẹp làm việc với MacBook"),
        ("IMG_5382.MOV", 1.85, 3.60, 1.00, "out",   "S04: Toàn cảnh lớp học & Giảng viên chia sẻ"),
        ("IMG_5381.MOV", 1.81, 1.00, 1.00, "in",    "S05: Góc rộng học viên F20 hướng lên màn chiếu"),
        ("IMG_5375.MOV", 2.44, 0.65, 1.00, "punch", "S06: Tập thể 10 nhân sự F20 chăm chú [Đúng nhịp KEY #1: MẤT 2 NĂM]"),

        # --- NHỊP NGHỈ CHUYỂN Ý (12.20s - 13.80s) ---
        ("IMG_5399.MOV", 1.60, 2.66, 0.58, "in",    "S07: 🌟 CHỊ OANH #3 — Đứng cầm MacBook mỉm cười tươi tắn"),

        # --- THÂN BÀI Ý 1: BỘ NÃO DỮ LIỆU (13.80s - 23.10s) + Cut đúng Key #2 @16.20s ---
        ("IMG_5377.MOV", 2.40, 0.85, 1.00, "in",    "S08: Chuyên gia chỉ sơ đồ Bộ não AI trên màn chiếu"),
        ("IMG_5406.MOV", 2.08, 0.45, 1.00, "punch", "S09: 🌟 CHỊ OANH #4 — Gõ phím thực hành [Đúng nhịp KEY #2: TRÊN NÃO]"),
        ("IMG_5465.MOV", 2.52, 0.65, 1.00, "out",   "S10: Đội ngũ nhân sự F20 tập trung cao độ trước màn hình"),
        ("IMG_5429.MOV", 2.30, 0.60, 1.00, "in",    "S11: Chuyên gia hướng dẫn trực tiếp trên laptop"),

        # --- THÂN BÀI Ý 2: KẾ TOÁN & EXCEL (23.10s - 36.90s) + Cut đúng Key #3 @27.62s & Key #4 @32.38s ---
        ("IMG_5383.MOV", 2.20, 0.15, 1.00, "in",    "S12: 5 nhân sự F20 đồng loạt gõ phím bằng cả 2 tay"),
        ("IMG_5378.MOV", 2.32, 0.65, 1.00, "out",   "S13: 4 nữ nhân sự F20 ngồi thẳng lưng mỉm cười"),
        ("IMG_5379.MOV", 2.33, 0.85, 1.00, "punch", "S14: 2 nhân sự nam bảng hiệu F20 [Đúng nhịp KEY #3: LẤY TỪ NÃO]"),
        ("IMG_5430.MOV", 2.43, 0.80, 1.00, "in",    "S15: Bàn họp F20 chăm chú theo dõi quy trình báo cáo"),
        ("IMG_5408.MOV", 4.52, 0.55, 0.92, "punch", "S16: Cận màn hình MacBook xuất báo cáo [Đúng nhịp KEY #4: SHEET & EXCEL]"),

        # --- THÂN BÀI Ý 3: MARKETING & NGỮ ĐIỆU (36.90s - 47.20s) + Cut đúng Key #5 @37.15s & Key #6 @44.82s ---
        ("IMG_5414.MOV", 2.90, 1.20, 1.00, "punch", "S17: 🌟 CHỊ OANH #5 — Chủ trì bàn dài [Đúng nhịp KEY #5: MARKETING]"),
        ("IMG_5467.MOV", 2.35, 0.45, 1.00, "in",    "S18: Nữ nhân sự Marketing F20 chăm chú thực hành"),
        ("IMG_5468.MOV", 2.57, 0.25, 0.76, "out",   "S19: Giảng viên truyền lửa & Chị Oanh ngồi mỉm cười phía sau"),
        ("IMG_5463.MOV", 2.48, 0.55, 1.00, "punch", "S20: Kèm cặp thực hành viết nội dung [Đúng nhịp KEY #6: LẤY NỘI DUNG]"),

        # --- KẾT BÀI & ĐẠI CẢNH KẾT SANG TRỌNG (47.20s - 57.20s) + Cut đúng Key #7 @47.45s ---
        ("IMG_5431.MOV", 2.75, 0.80, 1.00, "punch", "S21: Tập thể F20 đồng lòng [Đúng nhịp KEY #7: ĐỘI NGŨ AI ĐANG CÀY]"),
        ("IMG_5462.MOV", 1.85, 0.35, 1.00, "in",    "S22: Cầm tay chỉ việc 1-1 sát sao trên máy tính"),
        ("IMG_5420.MOV", 2.30, 0.85, 1.00, "out",   "S23: 🌟 CHỊ OANH #6 — Đứng trao đổi rạng rỡ dưới ánh đèn ấm"),
        ("IMG_5428.MOV", 3.10, 3.65, 0.72, "in",    "S24: 🌟 CHỊ OANH #7 — Chân dung sang trọng khép lại video (3.65-5.88s)"),
    ]

    v0_segs = []
    cur_u = 0
    shot_meta = []
    for idx, (fn, dur_s, src_in_s, spd, zmode, desc) in enumerate(VISUAL_PLAN, 1):
        t0_s = cur_u / 1e6
        seg, cur_u = make_clean_video_seg(fn, t0_s, dur_s, src_in_s, spd=spd, zoom_mode=zmode)
        v0_segs.append(seg)
        src_out_s = src_in_s + (seg["source_timerange"]["duration"] / 1e6)
        shot_meta.append((f"S{idx:02d}", fn, t0_s, cur_u / 1e6, src_in_s, src_out_s, desc))

    total_dur_u = cur_u
    total_dur_s = total_dur_u / 1e6

    tr_v0 = copy.deepcopy(vtrack_tpl)
    tr_v0["id"] = uid()
    tr_v0["segments"] = v0_segs

    # =========================================================================
    # 2. LOGICAL 3-ACT VOICEOVER (100% RAW .MOV via video_original_sound)
    # =========================================================================
    def make_raw_voice_seg(fn: str, tgt_t0_s: float, src_in_s: float, src_out_s: float, vol: float):
        aid, full_u = get_or_add_raw_voice_from_mov(fn)
        src_st_u = us(src_in_s)
        dur_u    = max(33333, us(src_out_s) - src_st_u)
        if src_st_u + dur_u > full_u:
            dur_u = full_u - src_st_u
        tgt_st_u = us(tgt_t0_s)

        sg = copy.deepcopy(aseg_tpl)
        refs = []
        for k, tpl_e in a_extra_tpl.items():
            em = copy.deepcopy(tpl_e)
            em["id"] = uid()
            if k == "speeds":
                em["speed"] = 1.0
            D["materials"][k].append(em)
            refs.append(em["id"])

        fid = uid()
        D["materials"].setdefault("audio_fades", []).append({
            "fade_in_duration": min(33333, dur_u // 5),
            "fade_out_duration": min(50000, dur_u // 4),
            "fade_type": 0, "id": fid, "type": "audio_fade"
        })
        refs.append(fid)

        sg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": src_st_u, "duration": dur_u},
            "target_timerange": {"start": tgt_st_u, "duration": dur_u},
            "speed": 1.0, "volume": round(vol, 3), "last_nonzero_volume": round(vol, 3),
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []
        })
        return sg, (tgt_st_u + dur_u) / 1e6

    VOICE_SCRIPT = [
        ("M1",   "IMG_5382.MOV",  2.75, 3.58, 7.44, 1.25),
        ("M2a",  "IMG_5380.MOV",  6.80, 1.74, 4.58, 1.02),
        ("M2b",  "IMG_5380.MOV",  9.76, 5.18, 7.60, 1.02),

        ("T1a",  "IMG_5392.MOV", 13.80, 2.15, 3.35, 1.24),
        ("T1b",  "IMG_5390.MOV", 15.12, 1.52, 4.50, 1.45),
        ("T1c",  "IMG_5404.MOV", 18.28, 0.00, 4.58, 1.50),

        ("T2a",  "IMG_5377.MOV", 23.30, 0.72, 2.54, 1.04),
        ("T2b",  "IMG_5377.MOV", 25.20, 4.98, 7.30, 1.04),
        ("T2c",  "IMG_5378.MOV", 27.62, 2.04, 4.18, 1.20),
        ("T2d",  "IMG_5375.MOV", 29.95, 0.80, 7.56, 1.24),

        ("T3a",  "IMG_5406.MOV", 37.15, 0.05, 2.50, 1.32),
        ("T3b1", "IMG_5467.MOV", 39.80, 1.06, 1.52, 1.10),
        ("T3b2", "IMG_5467.MOV", 40.28, 1.72, 3.46, 1.10),
        ("T3c1", "IMG_5468.MOV", 42.15, 0.22, 1.01, 1.20),
        ("T3c2", "IMG_5468.MOV", 42.96, 1.34, 5.30, 1.20),

        ("K1a",  "IMG_5386.MOV", 47.45, 0.00, 2.46, 1.38),
        ("K1b",  "IMG_5386.MOV", 50.02, 5.35, 6.12, 1.38),
    ]

    voice_lanes = [[], []]
    vs = {}
    for idx, (vid, fn, t0_s, sin_s, sout_s, vol) in enumerate(VOICE_SCRIPT):
        sg, t1_s = make_raw_voice_seg(fn, t0_s, sin_s, sout_s, vol)
        lane_i = idx % 2
        if voice_lanes[lane_i] and (voice_lanes[lane_i][-1]["target_timerange"]["start"] + voice_lanes[lane_i][-1]["target_timerange"]["duration"] > sg["target_timerange"]["start"]):
            lane_i = 1 - lane_i
        voice_lanes[lane_i].append(sg)
        vs[vid] = (t0_s, t1_s)

    tr_voice_a = copy.deepcopy(atrack_tpl); tr_voice_a["id"] = uid(); tr_voice_a["segments"] = voice_lanes[0]
    tr_voice_b = copy.deepcopy(atrack_tpl); tr_voice_b["id"] = uid(); tr_voice_b["segments"] = voice_lanes[1]

    # =========================================================================
    # 3. LUXURY TYPOGRAPHY ENGINE (CODEX PALETTE + 100% MUTUAL EXCLUSION!)
    #    Rule: Whenever a TOP KEY jumps up, BOTTOM SUB is 100% OFF (0ms overlap)!
    # =========================================================================
    SHADOW_SPEC = [{
        "thickness_projection_angle": -45,
        "thickness_projection_enable": False,
        "diffuse": 0.18,
        "alpha": 0.78,
        "distance": 6,
        "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
        "angle": -45,
        "thickness_projection_distance": 0,
    }]

    def build_rich_text_seg(
        parts: list[tuple[str, bool]],
        t0_s: float,
        t1_s: float,
        pos_y: float,
        font_id: str,
        font_path: str,
        font_title: str,
        base_size: float,
        emph_size: float,
        main_col: list[float],
        emph_col: list[float],
        stroke_col: list[float],
        stroke_hex: str,
        stroke_w: float,
        pill_hex: str | None = None,
        pill_alpha: float = 0.0,
        pill_radius: float = 0.28,
        motion: str = "sub",
        text_type: str = "text",
    ):
        full_text = "".join(p[0] for p in parts)
        styles = []
        cur = 0
        for sub_str, is_emph in parts:
            ln = len(sub_str)
            if ln == 0:
                continue
            fcol = emph_col if is_emph else main_col
            sz   = emph_size if is_emph else base_size
            styles.append({
                "fill": {"content": {"render_type": "solid", "solid": {"color": fcol}}},
                "font": {"path": font_path, "id": font_id},
                "size": sz,
                "bold": True,
                "useLetterColor": True,
                "strokes": [{"content": {"render_type": "solid", "solid": {"color": stroke_col}}, "width": stroke_w, "mode": 0}],
                "shadows": copy.deepcopy(SHADOW_SPEC),
                "range": [cur, cur + ln],
            })
            cur += ln

        content_json = json.dumps({"text": full_text, "styles": styles}, ensure_ascii=False)
        use_pill = bool(pill_hex and pill_alpha > 0.01)

        tm = copy.deepcopy(tmat_tpl)
        tm_id = uid()
        tm.update({
            "id": tm_id,
            "type": text_type,
            "name": full_text.replace("\n", " ")[:30],
            "recognize_text": full_text,
            "translate_original_text": full_text,
            "content": content_json,
            "base_content": content_json,
            "font_size": base_size,
            "font_path": font_path,
            "font_resource_id": font_id,
            "fonts": [{
                "id": uid(),
                "resource_id": font_id,
                "effect_id": font_id,
                "third_resource_id": "",
                "category_id": "user",
                "category_name": "Đã sử dụng gần đây",
                "source_platform": 1,
                "path": font_path,
                "title": font_title,
                "team_id": "",
                "file_uri": "",
                "request_id": "",
            }],
            "text_color": "#ffffff",
            "border_alpha": 1.0,
            "border_color": stroke_hex,
            "border_width": stroke_w,
            "has_shadow": True,
            "shadow_color": "#000000",
            "shadow_alpha": 0.78,
            "shadow_smoothing": 0.35,
            "shadow_distance": 5.5,
            "shadow_angle": -45.0,
            "letter_spacing": 0.015 if font_id == FONT_DISPLAY_ID else 0.005,
            "line_spacing": 0.035,
            "alignment": 1,
            "line_feed": 1,
            "line_max_width": 0.90,
            "force_apply_line_max_width": False,
            "background_style": 1 if use_pill else 0,
            "background_color": pill_hex if use_pill else "#000000",
            "background_alpha": round(pill_alpha, 3) if use_pill else 0.0,
            "background_round_radius": pill_radius if use_pill else 0.0,
            "background_width": 0.14 if use_pill else 0.0,
            "background_height": 0.11 if use_pill else 0.0,
            "is_rich_text": len(styles) > 1,
            "check_flag": 55 if use_pill else 47,
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.35), us(t1_s) - st_u)
        dur_s = du_u / 1e6
        fade_out_t = max(0.28, dur_s - 0.16)

        if motion == "jump_tier1":
            # Elastic upward jump + pop-bounce + clean fade out
            kfs = [
                make_kf("KFTypeScaleX",    [(0.0, 0.74), (0.15, 1.07), (0.25, 1.00)]),
                make_kf("KFTypeScaleY",    [(0.0, 0.74), (0.15, 1.07), (0.25, 1.00)]),
                make_kf("KFTypePositionY", [(0.0, pos_y - 0.055), (0.16, pos_y + 0.008), (0.26, pos_y)]),
                make_kf("KFTypeAlpha",     [(0.0, 0.0), (0.10, 1.0), (fade_out_t, 1.0), (dur_s, 0.0)]),
            ]
        elif motion == "jump_tier2":
            # Crisp snap-up into pill slot right below Tier 1
            kfs = [
                make_kf("KFTypeScaleX",    [(0.0, 0.84), (0.14, 1.04), (0.23, 1.00)]),
                make_kf("KFTypeScaleY",    [(0.0, 0.84), (0.14, 1.04), (0.23, 1.00)]),
                make_kf("KFTypePositionY", [(0.0, pos_y - 0.035), (0.16, pos_y)]),
                make_kf("KFTypeAlpha",     [(0.0, 0.0), (0.10, 1.0), (fade_out_t, 1.0), (dur_s, 0.0)]),
            ]
        else:
            # Clean gentle pop-in for bottom subtitles
            kfs = [
                make_kf("KFTypeScaleX", [(0.0, 0.94), (0.12, 1.015), (0.20, 1.00)]),
                make_kf("KFTypeScaleY", [(0.0, 0.94), (0.12, 1.015), (0.20, 1.00)]),
                make_kf("KFTypeAlpha",  [(0.0, 0.0), (0.08, 1.0), (max(0.20, dur_s - 0.10), 1.0), (dur_s, 0.0)]),
            ]

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tm_id,
            "target_timerange": {"start": st_u, "duration": du_u},
            "extra_material_refs": [],
            "common_keyframes": kfs, "keyframe_refs": [],
        })
        ts["clip"]["transform"] = {"x": 0.0, "y": round(pos_y, 4)}
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["rotation"] = 0.0
        ts["clip"]["alpha"] = 1.0
        ts["uniform_scale"] = {"on": True, "value": 1.0}
        return ts

    def make_top_key_pair(t0_s: float, t2_delay_s: float, t1_end_s: float, theme_name: str, tier1_parts, tier2_parts):
        th = THEMES[theme_name]
        s_t1 = build_rich_text_seg(
            tier1_parts, t0_s, t1_end_s, pos_y=+0.535,
            font_id=FONT_DISPLAY_ID, font_path=FONT_DISPLAY_PATH, font_title="Oswald",
            base_size=13.8, emph_size=14.4,
            main_col=th["t1_main"], emph_col=th["t1_accent"],
            stroke_col=th["t1_stroke"], stroke_hex=th["t1_str_hex"], stroke_w=0.082,
            pill_hex=None, pill_alpha=0.0, motion="jump_tier1", text_type="text"
        )
        s_t2 = build_rich_text_seg(
            tier2_parts, t0_s + t2_delay_s, t1_end_s, pos_y=+0.415,
            font_id=FONT_BADGE_ID, font_path=FONT_BADGE_PATH, font_title="Montserrat",
            base_size=9.1, emph_size=9.4,
            main_col=th["t2_fill"], emph_col=th["t2_accent"],
            stroke_col=th["t2_stroke"], stroke_hex=th["t1_str_hex"], stroke_w=0.062,
            pill_hex=th["pill_hex"], pill_alpha=th["pill_alpha"], pill_radius=0.32,
            motion="jump_tier2", text_type="text"
        )
        return s_t1, s_t2

    def make_sub_card(t0_s: float, t1_s: float, parts):
        th = THEMES["SUB"]
        txt_check = "".join(p[0] for p in parts)
        for ln in txt_check.split("\n"):
            assert len(ln) <= 26, f"Bottom sub line too long ({len(ln)}): '{ln}'"
        return build_rich_text_seg(
            parts, t0_s, t1_s, pos_y=-0.48,
            font_id=FONT_SUB_ID, font_path=FONT_SUB_PATH, font_title="BeVietnamPro",
            base_size=10.0, emph_size=10.4,
            main_col=th["main"], emph_col=th["accent"],
            stroke_col=th["stroke"], stroke_hex=th["str_hex"], stroke_w=0.062,
            pill_hex=th["pill_hex"], pill_alpha=th["pill_alpha"], pill_radius=0.25,
            motion="sub", text_type="subtitle"
        )

    # -------------------------------------------------------------------------
    # EXACT MUTUALLY-EXCLUSIVE DIALOGUE MAP:
    # Bottom Sub (setup/bridge)  <-->  Top 2-Tier Key Jump (0% bottom sub!)
    # -------------------------------------------------------------------------
    # Exact internal split timestamps inside raw clips:
    # - T1b (IMG_5390 [1.52-4.50s] starts @15.12s):
    #     15.12 - 16.12s = "không đi đâu cả," (Bottom Sub)
    #     16.18 - 18.10s = "tất cả nó nằm ở trên não!" (JUMP TO TOP KEY #2!)
    # - T2d (IMG_5375 [0.80-7.56s] starts @29.95s):
    #     29.95 - 32.30s = "Tổng tiền bao nhiêu, của đơn vị nào —" (Bottom Sub)
    #     32.38 - 36.71s = "nó báo cáo ngay file Google Sheet hay Excel ngon lành!" (JUMP TO TOP KEY #4!)
    # - T3c (IMG_5468 starts @42.15s, "Nó lấy luôn..." starts @44.82s):
    #     42.15 - 44.72s = "khi viết văn, nội dung hay viết bài," (Bottom Sub)
    #     44.80 - 46.92s = "nó lấy luôn đúng nội dung của mình!" (JUMP TO TOP KEY #6!)

    BOTTOM_SUB_SPECS = [
        # Mở bài dẫn -> nhường sân cho KEY #1 lúc 9.76s
        (vs["M1"][0],   vs["M1"][1],  [("Tôi là người ", False), ("nghiên cứu AI\n", True), ("rất nhiều năm rồi", False)]),
        (vs["M2a"][0],  vs["M2a"][1], [("Riêng các bạn ", False), ("tự tìm hiểu,\n", True), ("tôi khẳng định luôn:", False)]),

        # Thân bài 1 dẫn -> nhường sân cho KEY #2 lúc 16.18s -> trả về Sub dưới lúc 18.28s
        (vs["T1a"][0],  16.10,        [("Cá nhân hóa ", True), ("từng người —\n", False), ("không đi đâu cả,", False)]),
        (vs["T1c"][0],  20.80,        [("Dự án hay ", False), ("dữ liệu nào\n", True), ("trong não đã có,", False)]),
        (20.86,         vs["T1c"][1], [("thì nó sẽ ", False), ("làm cho mình!", True)]),

        # Thân bài 2 dẫn -> nhường sân cho KEY #3 lúc 27.62s -> trả Sub 29.95s -> nhường KEY #4 lúc 32.38s
        (vs["T2a"][0],  vs["T2b"][1], [("Ví dụ ", False), ("Kế toán làm tháng,\n", True), ("quý, báo cáo cuối năm —", False)]),
        (vs["T2d"][0],  32.30,        [("Tổng tiền bao nhiêu,\n", False), ("của đơn vị nào —", True)]),

        # Thân bài 3: KEY #5 bật đầu câu 37.15s -> trả về Sub dưới lúc 39.80s -> nhường KEY #6 lúc 44.80s
        (vs["T3b1"][0], vs["T3b2"][1],[("Để nó hiểu đúng\n", False), ("ngữ điệu của mình này:", True)]),
        (vs["T3c1"][0], 44.72,        [("khi viết văn, ", False), ("nội dung\n", True), ("hay viết bài,", False)]),

        # Kết bài: KEY #7 bật đầu câu 47.45s -> câu hỏi chốt trả về Sub dưới lúc 50.02s
        (vs["K1b"][0],  vs["K1b"][1] + 0.35, [("Các bạn ", False), ("hình dung không?!", True)]),
    ]

    TOP_KEY_SPECS = [
        # KEY #1 (9.76s - 12.18s | Champagne Gold): "phải mất khoảng 2 năm mới quay lại đi tìm!"
        (vs["M2b"][0],  0.78, vs["M2b"][1], "CHAMPAGNE",
         [("PHẢI MẤT ", False), ("KHOẢNG 2 NĂM", True)],
         [("MỚI QUAY LẠI ", False), ("ĐI TÌM!", True)]),

        # KEY #2 (16.18s - 18.10s | F20 Emerald): "tất cả nó nằm ở trên não!"
        (16.18,         0.22, vs["T1b"][1], "EMERALD",
         [("TẤT CẢ ", False), ("DỮ LIỆU", True)],
         [("NẰM Ở ", False), ("TRÊN NÃO!", True)]),

        # KEY #3 (27.62s - 29.76s | Champagne Gold): "thì nó lấy hết thông tin từ não ra rồi!"
        (vs["T2c"][0],  0.38, vs["T2c"][1], "CHAMPAGNE",
         [("LẤY HẾT ", True), ("THÔNG TIN", False)],
         [("TỪ TRÊN NÃO ", False), ("RA RỒI!", True)]),

        # KEY #4 (32.38s - 36.71s | F20 Emerald): "báo cáo lại cho mình file Google Sheet hay file Excel ngon lành luôn!"
        (32.38,         1.35, vs["T2d"][1], "EMERALD",
         [("XUẤT FILE ", False), ("GOOGLE SHEET", True)],
         [("& FILE EXCEL ", True), ("NGON LÀNH LUÔN!", False)]),

        # KEY #5 (37.15s - 39.60s | Champagne Gold): "Cực kỳ quan trọng này: kể cả Marketing làm lại nhé!"
        (vs["T3a"][0],  0.82, vs["T3a"][1], "CHAMPAGNE",
         [("CỰC KỲ ", False), ("QUAN TRỌNG", True)],
         [("KỂ CẢ ", False), ("MARKETING LÀM LẠI!", True)]),

        # KEY #6 (44.80s - 46.92s | F20 Emerald): "nó lấy luôn cái nội dung của mình!"
        (44.80,         0.32, vs["T3c2"][1],"EMERALD",
         [("LẤY LUÔN ", False), ("CHUẨN XÁC", True)],
         [("NỘI DUNG ", True), ("CỦA CHÍNH MÌNH!", False)]),

        # KEY #7 (47.45s - 49.91s | Champagne Gold): "Ở đây nhưng mà đội ngũ AI vẫn đang cày!"
        (vs["K1a"][0],  0.42, vs["K1a"][1], "CHAMPAGNE",
         [("Ở ĐÂY NHƯNG ", False), ("ĐỘI NGŨ AI", True)],
         [("VẪN ĐANG CÀY ", True), ("LIÊN TỤC!", False)]),
    ]

    # Opening & Closing Centered Brand Lockups (0.16-2.58s & 51.35-57.02s)
    outro_t0 = 51.35
    outro_t1 = total_dur_s - 0.18
    intro_t1_seg = build_rich_text_seg(
        [("ĐÀO TẠO ", False), ("AI THỰC CHIẾN", True)], 0.16, 2.58, pos_y=-0.35,
        font_id=FONT_DISPLAY_ID, font_path=FONT_DISPLAY_PATH, font_title="Oswald",
        base_size=14.0, emph_size=14.4,
        main_col=THEMES["CHAMPAGNE"]["t1_main"], emph_col=THEMES["CHAMPAGNE"]["t1_accent"],
        stroke_col=THEMES["CHAMPAGNE"]["t1_stroke"], stroke_hex="#2c1f14", stroke_w=0.082,
        pill_hex=None, pill_alpha=0.0, motion="jump_tier1", text_type="text"
    )
    intro_t2_seg = build_rich_text_seg(
        [("CÔNG TY TNHH ", False), ("THỰC PHẨM F20", True)], 0.34, 2.58, pos_y=-0.48,
        font_id=FONT_BADGE_ID, font_path=FONT_BADGE_PATH, font_title="Montserrat",
        base_size=9.0, emph_size=9.2,
        main_col=THEMES["EMERALD"]["t2_fill"], emph_col=THEMES["EMERALD"]["t2_accent"],
        stroke_col=THEMES["EMERALD"]["t2_stroke"], stroke_hex="#053320", stroke_w=0.062,
        pill_hex="#063020", pill_alpha=0.88, pill_radius=0.32, motion="jump_tier2", text_type="text"
    )

    outro_t1_seg = build_rich_text_seg(
        [("CÔNG TY TNHH ", False), ("THỰC PHẨM F20", True)], outro_t0, outro_t1, pos_y=-0.35,
        font_id=FONT_DISPLAY_ID, font_path=FONT_DISPLAY_PATH, font_title="Oswald",
        base_size=13.2, emph_size=13.6,
        main_col=THEMES["CHAMPAGNE"]["t1_main"], emph_col=THEMES["CHAMPAGNE"]["t1_accent"],
        stroke_col=THEMES["CHAMPAGNE"]["t1_stroke"], stroke_hex="#2c1f14", stroke_w=0.082,
        pill_hex=None, pill_alpha=0.0, motion="jump_tier1", text_type="text"
    )
    outro_t2_seg = build_rich_text_seg(
        [("TIÊN PHONG ", False), ("ỨNG DỤNG AI THỰC CHIẾN", True)], outro_t0 + 0.22, outro_t1, pos_y=-0.48,
        font_id=FONT_BADGE_ID, font_path=FONT_BADGE_PATH, font_title="Montserrat",
        base_size=8.6, emph_size=8.8,
        main_col=THEMES["EMERALD"]["t2_fill"], emph_col=THEMES["EMERALD"]["t2_accent"],
        stroke_col=THEMES["EMERALD"]["t2_stroke"], stroke_hex="#053320", stroke_w=0.062,
        pill_hex="#063020", pill_alpha=0.88, pill_radius=0.32, motion="jump_tier2", text_type="text"
    )

    sub_segs = [make_sub_card(t0, t1, pts) for t0, t1, pts in BOTTOM_SUB_SPECS]
    top_tier1_segs = [intro_t1_seg]
    top_tier2_segs = [intro_t2_seg]
    for kt0, kdelay, kt1, ktheme, p1, p2 in TOP_KEY_SPECS:
        s1, s2 = make_top_key_pair(kt0, kdelay, kt1, ktheme, p1, p2)
        top_tier1_segs.append(s1)
        top_tier2_segs.append(s2)
    top_tier1_segs.append(outro_t1_seg)
    top_tier2_segs.append(outro_t2_seg)

    # STRICT MATHEMATICAL VERIFICATION: 0ms OVERLAP BETWEEN ANY TOP KEY AND ANY BOTTOM SUB!
    for s_sub in sub_segs:
        b0 = s_sub["target_timerange"]["start"]
        b1 = b0 + s_sub["target_timerange"]["duration"]
        for s_top in top_tier1_segs:
            k0 = s_top["target_timerange"]["start"]
            k1 = k0 + s_top["target_timerange"]["duration"]
            overlap = min(b1, k1) - max(b0, k0)
            assert overlap <= 0, f"CRITICAL OVERLAP ({overlap} us) between Sub [{b0/1e6:.2f}-{b1/1e6:.2f}s] and Top Key [{k0/1e6:.2f}-{k1/1e6:.2f}s]!"

    tr_sub    = copy.deepcopy(ttrack_tpl); tr_sub["id"] = uid();    tr_sub["segments"] = sub_segs
    tr_key_t1 = copy.deepcopy(ttrack_tpl); tr_key_t1["id"] = uid(); tr_key_t1["segments"] = top_tier1_segs
    tr_key_t2 = copy.deepcopy(ttrack_tpl); tr_key_t2["id"] = uid(); tr_key_t2["segments"] = top_tier2_segs

    # =========================================================================
    # 4. BGM WITH DYNAMIC DUCKING + TACTILE MICRO-SFX SYNCED TO EVERY TOP JUMP!
    # =========================================================================
    def add_audio_material(audio_path: Path, name_lbl: str, mtype: str = "sound"):
        fwd = norm_fwd(audio_path)
        if fwd in amat_map:
            return amat_map[fwd]
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio_path)], capture_output=True, text=True, check=True)
        du_u = us(float(json.loads(r.stdout)["format"]["duration"]))
        aid, lmid = uid(), str(uuid.uuid4())
        am = copy.deepcopy(amat_tpl)
        am.update({
            "id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
            "name": name_lbl, "path": fwd, "duration": du_u, "type": mtype
        })
        D["materials"]["audios"].append(am)
        amat_map[fwd] = (aid, du_u)
        return aid, du_u

    def make_audio_slice(aid: str, src_st_u: int, tgt_st_u: int, dur_u: int, vol: float, fi_u: int, fo_u: int):
        sg = copy.deepcopy(aseg_tpl)
        refs = []
        for k, tpl_e in a_extra_tpl.items():
            em = copy.deepcopy(tpl_e)
            em["id"] = uid()
            if k == "speeds":
                em["speed"] = 1.0
            D["materials"][k].append(em)
            refs.append(em["id"])
        fid = uid()
        D["materials"].setdefault("audio_fades", []).append({
            "fade_in_duration": fi_u, "fade_out_duration": fo_u, "fade_type": 0, "id": fid, "type": "audio_fade"
        })
        refs.append(fid)
        sg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": src_st_u, "duration": dur_u},
            "target_timerange": {"start": tgt_st_u, "duration": dur_u},
            "speed": 1.0, "volume": round(vol, 3), "last_nonzero_volume": round(vol, 3),
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []
        })
        return sg

    bgm_id, _ = add_audio_material(BGM_PATH, "Corporate Background02 - F20 AI Training", mtype="music")
    u_b1, u_b2, u_b3, u_b4 = us(2.65), us(12.20), us(13.75), us(51.15)
    bgm_segs = [
        make_audio_slice(bgm_id, 0,    0,    u_b1,               0.48, 300000, 160000),
        make_audio_slice(bgm_id, u_b1, u_b1, u_b2 - u_b1,        0.22, 160000, 140000),
        make_audio_slice(bgm_id, u_b2, u_b2, u_b3 - u_b2,        0.44, 140000, 140000),
        make_audio_slice(bgm_id, u_b3, u_b3, u_b4 - u_b3,        0.22, 140000, 200000),
        make_audio_slice(bgm_id, u_b4, u_b4, total_dur_u - u_b4, 0.55, 240000, 1400000),
    ]
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["segments"] = bgm_segs

    def make_sfx_seg(sfx_fn: str, lbl: str, t0_s: float, vol: float, max_dur_s: float):
        aid, du_full = add_audio_material(SFX_DIR / sfx_fn, lbl, mtype="sound")
        du = min(du_full, us(max_dur_s))
        return make_audio_slice(aid, 0, max(0, us(t0_s)), du, vol, min(12000, du // 6), min(90000, du // 3))

    SFX_POP    = "Pop & Bong Bóng - Pop (lower) telop sound etc (1s).mp3"
    SFX_CLICK  = "Click & Máy Chữ - el_interface_button_15_hpx (1s).mp3"
    SFX_SWOOSH = "Whoosh - Title Swoosh (1s).mp3"
    SFX_CHIME  = "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3"

    sfx_events = [
        (0.12,  SFX_SWOOSH, "Intro Swoosh", 0.11, 0.75),
        (0.34,  SFX_POP,    "Intro Badge Pop", 0.09, 0.45),
        (1.32,  SFX_CLICK,  "Hook Cut Click", 0.08, 0.35),
        (12.18, SFX_SWOOSH, "Breather Air", 0.09, 0.70),
    ]
    # Attach exact tactile Pop + Snap SFX to every one of the 7 Top Keyphrase Jumps!
    for idx_k, (kt0, kdelay, kt1, ktheme, _, _) in enumerate(TOP_KEY_SPECS, 1):
        sfx_events.append((max(0.0, kt0 - 0.04), SFX_POP,   f"Key {idx_k} Jump Pop",  0.10, 0.50))
        sfx_events.append((kt0 + kdelay,         SFX_CLICK, f"Key {idx_k} Pill Snap", 0.08, 0.38))
    sfx_events.append((outro_t0, SFX_CHIME, "Outro Brand Chime", 0.11, 1.50))

    sfx_lanes: list[list[dict]] = []
    for t0, fn, lbl, vol, mdur in sorted(sfx_events, key=lambda x: x[0]):
        sg = make_sfx_seg(fn, lbl, t0, vol=vol, max_dur_s=mdur)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for lane in sfx_lanes:
            if lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                lane.append(sg)
                placed = True
                break
        if not placed:
            sfx_lanes.append([sg])

    sfx_tracks = []
    for lane in sfx_lanes:
        tr_s = copy.deepcopy(atrack_tpl); tr_s["id"] = uid(); tr_s["segments"] = lane
        sfx_tracks.append(tr_s)

    D["tracks"] = [
        tr_v0,
        tr_sub,
        tr_key_t2,
        tr_key_t1,
        tr_voice_a,
        tr_voice_b,
        tr_bgm,
        *sfx_tracks,
    ]
    D["duration"] = total_dur_u
    D["update_time"] = now_s

    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video":
                s["render_index"] = ti
            elif tr["type"] == "text":
                s["render_index"] = 14000 + ti

    out_dir = DRAFTS_ROOT / DRAFT_NAME
    if out_dir.exists() and not (out_dir / ".locked").exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for aux_fn in ("draft_agency_config.json", "draft_biz_config.json", "attachment_pc_common.json", "key_value.json", "performance_opt_info.json", "draft_settings"):
        if (DONOR_DIR / aux_fn).exists():
            shutil.copy2(DONOR_DIR / aux_fn, out_dir / aux_fn)
    for aux_dir in ("common_attachment", "Resources"):
        if (DONOR_DIR / aux_dir).exists() and not (out_dir / aux_dir).exists():
            shutil.copytree(DONOR_DIR / aux_dir, out_dir / aux_dir)

    dvs = {
        "draft_materials": [],
        "draft_virtual_store": [
            {"type": 0, "value": [{"creation_time": 0, "display_name": "", "filter_type": 0, "id": "", "import_time": 0, "import_time_us": 0, "material_color_tag": "", "sort_sub_type": 0, "sort_type": 0, "subdraft_filter_type": 0}]},
            {"type": 1, "value": [{"child_id": e["id"], "parent_id": ""} for e in dm_entries]}
        ]
    }
    (out_dir / "draft_virtual_store.json").write_text(json.dumps(dvs, ensure_ascii=False), encoding="utf-8")

    tl_layout = {
        "dockItems": [{"dockIndex": 0, "ratio": 1, "timelineIds": [main_tl_id], "timelineNames": ["Dòng thời gian 01"]}],
        "layoutOrientation": 1
    }
    (out_dir / "timeline_layout.json").write_text(json.dumps(tl_layout, ensure_ascii=False), encoding="utf-8")

    cover_jpg = out_dir / "draft_cover.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", str(RAW_DIR / "IMG_5428.MOV"),
        "-frames:v", "1", "-vf", "scale=540:960", "-q:v", "2", str(cover_jpg)
    ], check=False)

    tl_root = out_dir / "Timelines"
    new_tl_dir = tl_root / main_tl_id
    new_tl_dir.mkdir(parents=True, exist_ok=True)
    if (out_dir / "attachment_pc_common.json").exists():
        shutil.copy2(out_dir / "attachment_pc_common.json", new_tl_dir / "attachment_pc_common.json")
    if (out_dir / "common_attachment").exists() and not (new_tl_dir / "common_attachment").exists():
        shutil.copytree(out_dir / "common_attachment", new_tl_dir / "common_attachment")
    if cover_jpg.exists():
        shutil.copy2(cover_jpg, new_tl_dir / "draft_cover.jpg")

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for tp in [out_dir / "draft_content.json", out_dir / "template-2.tmp", new_tl_dir / "draft_content.json", new_tl_dir / "template-2.tmp"]:
        if tp.exists():
            tp.unlink()
        tp.write_bytes(dc_bytes)

    pj = {
        "config": {"color_space": 0, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False},
        "create_time": now_us, "id": main_tl_id, "main_timeline_id": main_tl_id,
        "timelines": [{"create_time": now_us, "id": main_tl_id, "is_marked_delete": False, "name": "Dòng thời gian 01", "update_time": now_us}],
        "update_time": now_us, "version": 0
    }
    (tl_root / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

    dmi = copy.deepcopy(dmi_donor)
    fold_fwd = norm_fwd(out_dir)
    dmi.update({
        "draft_id": draft_uuid, "draft_name": DRAFT_NAME,
        "draft_fold_path": fold_fwd, "draft_root_path": str(DRAFTS_ROOT),
        "draft_cover": "draft_cover.jpg",
        "tm_draft_create": now_us, "tm_draft_modified": now_us, "tm_duration": total_dur_u,
    })
    for bucket in dmi.get("draft_materials", []):
        if bucket.get("type") == 0:
            bucket["value"] = dm_entries
    (out_dir / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

    rmi_path = APPDATA_ROOT / "root_meta_info.json"
    if rmi_path.exists():
        rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
        store = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_NAME]
        entry = copy.deepcopy(store[0]) if store else {}
        total_bytes = sum((RAW_DIR / Path(p).name).stat().st_size for p in vmat_map)
        entry.update({
            "draft_id": draft_uuid, "draft_name": DRAFT_NAME,
            "draft_fold_path": fold_fwd, "draft_root_path": str(DRAFTS_ROOT),
            "draft_cover": f"{fold_fwd}\\draft_cover.jpg",
            "draft_json_file": f"{fold_fwd}\\draft_content.json",
            "draft_timeline_materials_size": total_bytes,
            "streaming_edit_draft_ready": True,
            "tm_draft_create": now_us, "tm_draft_modified": now_us,
            "tm_draft_removed": 0, "tm_duration": total_dur_u,
        })
        store.insert(0, entry)
        rmi["all_draft_store"] = store
        rmi["draft_ids"] = len(store)
        rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    # =========================================================================
    # 5. RENDER WYSIWYG 1080x1920 TYPOGRAPHY PREVIEWS + 48-FRAME IN/OUT QC SHEET
    # =========================================================================
    qc_dir = SCRATCH_DIR / "qc_v4_codex"
    qc_dir.mkdir(parents=True, exist_ok=True)

    f_oswald = ImageFont.truetype(str(FONT_SRC_DIR / "Oswald-Bold.ttf"), 84)
    f_mont   = ImageFont.truetype(str(FONT_SRC_DIR / "Montserrat-ExtraBold.ttf"), 42)
    f_be     = ImageFont.truetype(str(FONT_SRC_DIR / "BeVietnamPro-Bold.ttf"), 46)

    def render_mockup_card(vid_fn: str, vid_ts: float, mode: str, out_png: Path):
        bg_jpg = qc_dir / f"_bg_{out_png.stem}.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", f"{vid_ts:.2f}", "-i", str(RAW_DIR / vid_fn), "-frames:v", "1", "-vf", "scale=1080:1920", "-q:v", "2", str(bg_jpg)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        im = Image.open(bg_jpg).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)

        def draw_pill_text(y_center: int, parts_rgb, font_obj, stroke_rgb, stroke_px: int, pill_rgba=None):
            full_s = "".join(p[0] for p in parts_rgb)
            lines = full_s.split("\n")
            line_h = int(font_obj.size * 1.24)
            tot_h = line_h * len(lines)
            max_w = max(int(d.textlength(ln, font=font_obj)) for ln in lines)
            if pill_rgba:
                px0, py0 = W // 2 - max_w // 2 - 34, y_center - tot_h // 2 - 16
                px1, py1 = W // 2 + max_w // 2 + 34, y_center + tot_h // 2 + 20
                d.rounded_rectangle([px0, py0, px1, py1], radius=26, fill=pill_rgba)
            # Draw per-segment rich color
            # Split parts across lines
            cur_line_idx = 0
            line_runs = [[]]
            for txt_seg, col_rgb in parts_rgb:
                chunks = txt_seg.split("\n")
                for ci, ch_s in enumerate(chunks):
                    if ci > 0:
                        line_runs.append([])
                    if ch_s:
                        line_runs[-1].append((ch_s, col_rgb))
            for li, runs in enumerate(line_runs):
                ln_txt = "".join(r[0] for r in runs)
                lw = int(d.textlength(ln_txt, font=font_obj))
                cx = W // 2 - lw // 2
                cy = y_center - tot_h // 2 + li * line_h
                for r_txt, r_col in runs:
                    d.text((cx + 4, cy + 5), r_txt, font=font_obj, fill=(0, 0, 0, 185))
                    d.text((cx, cy), r_txt, font=font_obj, fill=r_col + (255,), stroke_width=stroke_px, stroke_fill=stroke_rgb + (255,))
                    cx += int(d.textlength(r_txt, font=font_obj))

        if mode == "champagne":
            # Y = +0.535 -> pixel Y = 960 - 0.535*960 = 446; Y = +0.415 -> pixel Y = 562
            draw_pill_text(446, [("PHẢI MẤT ", (255, 246, 229)), ("KHOẢNG 2 NĂM", (246, 201, 103))], f_oswald, (44, 31, 20), 6, None)
            draw_pill_text(562, [("MỚI QUAY LẠI ", (255, 248, 235)), ("ĐI TÌM!", (247, 210, 125))], f_mont, (36, 26, 18), 3, (36, 27, 20, 220))
        elif mode == "emerald":
            draw_pill_text(446, [("XUẤT FILE ", (241, 255, 247)), ("GOOGLE SHEET", (107, 240, 176))], f_oswald, (5, 51, 32), 6, None)
            draw_pill_text(562, [("& FILE EXCEL ", (140, 232, 181)), ("NGON LÀNH LUÔN!", (242, 255, 248))], f_mont, (4, 40, 25), 3, (6, 48, 32, 220))
        else:
            # Y = -0.48 -> pixel Y = 960 + 0.48*960 = 1420 (strictly < 1548 Safe Zone!)
            draw_pill_text(1410, [("Tôi là người ", (255, 255, 255)), ("nghiên cứu AI\n", (152, 242, 196)), ("rất nhiều năm rồi", (255, 255, 255))], f_be, (14, 23, 34), 4, (14, 23, 34, 178))

        comp = Image.alpha_composite(im, ov).convert("RGB")
        comp.save(out_png, quality=92)
        return out_png

    p1 = render_mockup_card("IMG_5375.MOV", 1.8, "champagne", qc_dir / "preview_v4_key_champagne.jpg")
    p2 = render_mockup_card("IMG_5408.MOV", 1.8, "emerald",   qc_dir / "preview_v4_key_emerald.jpg")
    p3 = render_mockup_card("IMG_5428.MOV", 1.8, "sub",       qc_dir / "preview_v4_sub_chi_oanh.jpg")

    # Side-by-side 3-up Typography & Color Showcase Sheet
    trio = Image.new("RGB", (3 * 540 + 24, 960 + 48), (14, 18, 24))
    dt = ImageDraw.Draw(trio)
    for idx_p, (lbl, pp) in enumerate([
        ("KEY TREN #1 (Champagne Gold - SUB DUOI TAT 100%)", p1),
        ("KEY TREN #4 (Emerald F20 - SUB DUOI TAT 100%)", p2),
        ("SUB DUOI (Tren ao vest trang Chi Oanh - CUC NET)", p3),
    ]):
        im_s = Image.open(pp).resize((540, 960), Image.Resampling.LANCZOS)
        x0 = idx_p * 548 + 6
        trio.paste(im_s, (x0, 42))
        dt.text((x0 + 8, 12), lbl, fill=(246, 209, 120))
    typo_sheet_p = qc_dir / "qc_261125_v4_typography_showcase.jpg"
    trio.save(typo_sheet_p, quality=90)

    # 48-Frame IN/OUT QC Sheet for all 24 shots
    def grab_pair(item):
        sid, fn, t0, t1, sin, sout, desc = item
        vp = RAW_DIR / fn
        out_items = []
        for tag, ts in [("IN", sin + 0.06), ("OUT", max(sin + 0.06, sout - 0.06))]:
            jp = qc_dir / f"{sid}_{tag}.jpg"
            subprocess.run(["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", str(vp), "-frames:v", "1", "-vf", "scale=220:391", "-q:v", "3", str(jp)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            out_items.append((f"{sid} {tag} [{t0:.1f}-{t1:.1f}s]", f"{fn} @{ts:.2f}s", desc, jp))
        return out_items

    with ThreadPoolExecutor(max_workers=8) as ex:
        nested = list(ex.map(grab_pair, shot_meta))
    flat_frames = [x for pair in nested for x in pair]

    cols = 8
    rows = (len(flat_frames) + cols - 1) // cols
    cw, ch = 228, 438
    sheet = Image.new("RGB", (cols * cw, rows * ch), (15, 20, 26))
    draw = ImageDraw.Draw(sheet)
    for idx, (l1, l2, desc, jp) in enumerate(flat_frames):
        r, c = divmod(idx, cols)
        x, y = c * cw + 4, r * ch + 42
        sheet.paste(Image.open(jp), (x, y))
        col = (246, 201, 103) if "CHỊ OANH" in desc else (210, 235, 255)
        draw.text((x + 2, r * ch + 4), l1[:27], fill=col)
        draw.text((x + 2, r * ch + 20), l2[:27], fill=(152, 235, 190))
    qc_sheet_p = qc_dir / "qc_261125_v4_all_24_shots_inout.jpg"
    sheet.save(qc_sheet_p, quality=88)

    cloud_dir = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\261125-f20-dao-tao-ai")
    cloud_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), cloud_dir / "build_261125_v4_codex_master.py")
    shutil.copy2(qc_sheet_p, cloud_dir / "qc_261125_v4_all_24_shots_inout.jpg")
    shutil.copy2(typo_sheet_p, cloud_dir / "qc_261125_v4_typography_showcase.jpg")

    print(f"SUCCESS V4 CODEX MASTER: {out_dir}")
    print(f"  Duration       : {total_dur_s:.2f}s | 1 Single Video Track ({len(shot_meta)} Wave-Paced clean shots, 7 Chị Oanh hero shots)")
    print(f"  Top Pop-Up Keys: {len(TOP_KEY_SPECS)} 2-Tier Keyphrases (Y=+0.535/+0.415, X=0.0, 0ms overlap with Bottom Subs!)")
    print(f"  Bottom Subs    : {len(BOTTOM_SUB_SPECS)} Centered Pills (Y=-0.48, X=0.0, auto-OFF whenever Top Key jumps!)")
    print(f"  Micro-SFX      : {len(sfx_events)} Tactile Pop + Pill Snap + Swoosh accents")
    print(f"  Typo Showcase  : {typo_sheet_p}")
    print(f"  Shots QC Sheet : {qc_sheet_p}")

if __name__ == "__main__":
    main()
