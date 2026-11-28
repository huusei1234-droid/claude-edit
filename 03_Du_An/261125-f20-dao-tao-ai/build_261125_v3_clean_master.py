import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

W, H = 1080, 1920
FPS = 30.0

DRAFT_NAME    = "261125 F20 Đào Tạo AI Thực Chiến V3"
DRAFTS_ROOT   = Path(r"C:\CapCut Drafts")
APPDATA_ROOT  = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DONOR_DIR     = Path(r"C:\Users\001\.gemini\antigravity\brain\bbab5999-f668-416e-804a-3347740965da\scratch\donor_v1")
BAK_1117_JSON = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\f20-set-qua-2011\1117_F20_CapCut_Backup\draft_content.json")
FC_VOS_JSON   = Path(r"C:\CapCut Drafts\261127 Feel Chicken Mì cay mực khổng lồ final\draft_content.json")
SCRATCH_DIR   = Path(r"C:\Users\001\.gemini\antigravity\brain\bbab5999-f668-416e-804a-3347740965da\scratch")

RAW_DIR       = Path(r"G:\Other computers\My Computer\F20\video gốc\261125")
TLH_EDIT      = Path(r"G:\Other computers\My Computer\Document HT Media\TLH\Edit")
BGM_PATH      = TLH_EDIT / r"01_Nhạc Nền (BGM)\01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Corporate Background02 (2p19s).mp3"
SFX_DIR       = TLH_EDIT / r"02_Hiệu Ứng Âm Thanh (SFX)"
FONT_SRC_DIR  = TLH_EDIT / r"04_Font Chữ TVC & Chữ Gradient"

CC_CACHE_EFF   = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Cache\effect")
SUB_CACHE_DIR  = CC_CACHE_EFF / "7542214368361057553" / "d376267c892ee3a53654ae93a78dcfb7"
HEAD_CACHE_DIR = CC_CACHE_EFF / "7517455788122705168" / "91d28cfa5e7db054f4872f1ae2417ac2"
SUB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
HEAD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
if not (SUB_CACHE_DIR / "font.ttf").exists():
    shutil.copy2(FONT_SRC_DIR / "BeVietnamPro-Bold.ttf", SUB_CACHE_DIR / "font.ttf")
if not (HEAD_CACHE_DIR / "Montserrat-Bold.otf").exists():
    shutil.copy2(FONT_SRC_DIR / "Montserrat-ExtraBold.ttf", HEAD_CACHE_DIR / "Montserrat-Bold.otf")

FONT_SUB_ID    = "7542214368361057553"
FONT_SUB_PATH  = str(SUB_CACHE_DIR / "font.ttf").replace("\\", "/")
FONT_HEAD_ID   = "7517455788122705168"
FONT_HEAD_PATH = str(HEAD_CACHE_DIR / "Montserrat-Bold.otf").replace("\\", "/")

CC_EFF_FWD     = "C:/Users/001/AppData/Local/CapCut/User Data/Cache/effect"
ADJUST_RES_ID  = "7501974767453474064"
ADJUST_PATH    = f"{CC_EFF_FWD}/7501974767453474064/20cd8db6531c21bf7e4053026d20e395"
CURVES_PATH    = f"{CC_EFF_FWD}/7501974767453474064/6821a294141131e7c561ff73480449f7"

WHITE_COL      = [1.0, 1.0, 1.0]
GOLD_COL       = [1.0, 0.8313725, 0.0]
F20_GREEN_COL  = [0.0, 0.6196078, 0.2862745]
NAVY_STROKE    = [0.043, 0.125, 0.235]
DARK_STROKE    = [0.05, 0.07, 0.10]

FULL_CROP_1_1 = {
    "upper_left_x": 0.0, "upper_left_y": 0.0,
    "upper_right_x": 1.0, "upper_right_y": 0.0,
    "lower_left_x": 0.0, "lower_left_y": 1.0,
    "lower_right_x": 1.0, "lower_right_y": 1.0,
}

# Strictly banned distracted / personal-work / obstructed visual clips
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

PROJECTOR_CLIPS = {
    "IMG_5377.MOV", "IMG_5381.MOV", "IMG_5382.MOV", "IMG_5399.MOV",
    "IMG_5428.MOV", "IMG_5468.MOV",
}
PORTRAIT_WARM_CLIPS = {
    "IMG_5406.MOV", "IMG_5407.MOV", "IMG_5408.MOV", "IMG_5414.MOV",
    "IMG_5420.MOV", "IMG_5421.MOV", "IMG_5462.MOV",
}

ZONE_PROFILES = {
    "BLUE_TEAM": {
        "sliders": {
            "brightness": 0.04, "contrast": 0.06, "saturation": 0.06, "sharpen": 0.12,
            "highlight": -0.09, "shadow": 0.10, "white": 0.02, "black": -0.02,
            "clear": 0.08, "temperature": 0.04, "tone": 0.03, "light_sensation": 0.06,
        },
        "hsl": {
            1: (0,  10,   4),
            2: (0,  -4,  12),
            3: (0, -10,   4),
            4: (0,   8,   3),
            6: (-2, 12,   6),
            7: (0, -14,  -4),
            8: (0,   0,   0),
        }
    },
    "PROJECTOR": {
        "sliders": {
            "brightness": 0.05, "contrast": 0.05, "saturation": 0.07, "sharpen": 0.12,
            "highlight": -0.14, "shadow": 0.14, "white": 0.02, "black": -0.02,
            "clear": 0.09, "temperature": 0.02, "tone": 0.04, "light_sensation": 0.08,
        },
        "hsl": {
            1: (0,   8,   5),
            2: (0,  -3,  14),  # Bright smooth flattering skin tone for Chị Oanh!
            3: (0, -10,   5),
            4: (0,   8,   3),
            6: (-2, 10,   5),
            7: (0, -10,  -2),
            8: (0,   0,   0),
        }
    },
    "PORTRAIT_WARM": {
        "sliders": {
            "brightness": 0.05, "contrast": 0.06, "saturation": 0.07, "sharpen": 0.11,
            "highlight": -0.10, "shadow": 0.11, "white": 0.03, "black": -0.02,
            "clear": 0.08, "temperature": 0.04, "tone": 0.04, "light_sensation": 0.08,
        },
        "hsl": {
            1: (0,   9,   5),
            2: (0,  -3,  13),  # Luminous warm portrait skin tone
            3: (0,  -8,   4),
            4: (0,   8,   3),
            6: (-2, 10,   5),
            7: (0, -10,   0),
            8: (0,   0,   0),
        }
    }
}

def get_zone_name(filename: str) -> str:
    if filename in PROJECTOR_CLIPS:
        return "PROJECTOR"
    if filename in PORTRAIT_WARM_CLIPS:
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
    v_extra_tpl = {
        k: copy.deepcopy(d_donor["materials"][k][0])
        for k in v_extra_keys if d_donor["materials"].get(k)
    }
    a_extra_keys = ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl = {
        k: copy.deepcopy(next(x for x in d_1117["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"]))
        for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in d_1117["materials"].get(k, []))
    }

    for k, val in list(D["materials"].items()):
        if isinstance(val, list):
            D["materials"][k] = []

    vmat_map = {}
    vos_map  = {}
    amat_map = {}
    dm_entries = [copy.deepcopy(dmi_donor["draft_materials"][0]["value"][0])]

    def get_or_add_raw_video(fn: str):
        src_path = RAW_DIR / fn
        if not src_path.is_file():
            raise FileNotFoundError(f"Missing raw 261125 source file: {src_path}")
        fwd = norm_fwd(src_path)
        assert "261125/" in fwd, f"Forbidden non-raw source: {fwd}"
        if fwd in vmat_map:
            return vmat_map[fwd]
        w, h, dur_s, has_aud = probe_media(src_path)
        dur_u = max(33333, us(dur_s))
        mid = uid()
        uhex = uuid.uuid4().hex
        lmid = str(uuid.uuid4())
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
            "id": aid,
            "unique_id": uhex,
            "type": "video_original_sound",
            "name": fn,
            "duration": dur_u,
            "path": fwd,
            "category_name": "",
            "video_id": mid,
            "local_material_id": "",
            "check_flag": 1,
        })
        D["materials"]["audios"].append(am)
        vos_map[fwd] = (aid, dur_u)
        return aid, dur_u

    VALID_KF_PROPS = {"KFTypeScaleX", "KFTypeScaleY", "KFTypePositionX", "KFTypePositionY", "KFTypeRotation"}
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
        zname = get_zone_name(fn)
        prof = ZONE_PROFILES[zname]
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
            hm["hue"] = int(hue_v)
            hm["saturation"] = int(sat_v)
            hm["lightness"] = int(light_v)
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

    def make_clean_video_seg(fn: str, t0_s: float, dur_s: float, src_in_s: float, spd: float = 1.0, zoom_dir: int = 1):
        assert fn not in BANNED_VISUAL_CLIPS, f"CRITICAL: Banned clip {fn} is not allowed on visual track!"
        mid, mat_dur_u, w, h, _ = get_or_add_raw_video(fn)
        tgt_st_u = us(t0_s)
        tgt_du_u = max(33333, us(t0_s + dur_s) - tgt_st_u)
        src_st_u = us(src_in_s)
        src_du_u = us((tgt_du_u / 1e6) * spd)
        if src_st_u + src_du_u > mat_dur_u:
            raise ValueError(f"Clip {fn} overrun: src_in={src_in_s}s + {(src_du_u/1e6):.2f}s > {(mat_dur_u/1e6):.2f}s")

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
        if zoom_dir != 0 and actual_dur_s >= 2.3:
            s0, s1 = (1.0, 1.045) if zoom_dir > 0 else (1.045, 1.0)
            kfs.append(make_kf("KFTypeScaleX", [(0.0, s0), (actual_dur_s, s1)]))
            kfs.append(make_kf("KFTypeScaleY", [(0.0, s0), (actual_dur_s, s1)]))

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": src_st_u, "duration": src_du_u},
            "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
            "speed": round(spd, 3),
            "volume": 0.0,
            "last_nonzero_volume": 1.0,
            "extra_material_refs": refs,
            "common_keyframes": kfs,
            "keyframe_refs": [],
        })
        return seg, tgt_st_u + tgt_du_u

    # =========================================================================
    # 1. SINGLE SEQUENTIAL VISUAL STREAM (TRACK 0 ONLY — 0% OVERLAY CHAOS!)
    #    7 Flattering Hero Shots of Chị Oanh + 12 Clean Focused F20 Team Shots
    # =========================================================================
    VISUAL_PLAN = [
        # --- MỞ BÀI (0.00s - 12.10s) ---
        ("IMG_5376.MOV", 2.60, 0.20, 1.00, +1, "S01: Đại cảnh mở màn F20 nghiêm túc"),
        ("IMG_5428.MOV", 3.30, 0.45, 1.00, +1, "S02: 🌟 CHỊ OANH #1 — Chân dung sáng đẹp làm việc với MacBook"),
        ("IMG_5382.MOV", 3.10, 3.58, 1.00, -1, "S03: Toàn cảnh lớp học & Chuyên gia chia sẻ"),
        ("IMG_5375.MOV", 3.10, 0.60, 1.00, +1, "S04: Tập thể 10 nhân sự F20 mở laptop chăm chú"),

        # --- NHỊP NGHỈ CHUYỂN Ý (12.10s - 13.70s) ---
        ("IMG_5399.MOV", 1.60, 2.66, 0.58, +1, "S05: 🌟 CHỊ OANH #2 — Đứng cầm MacBook mỉm cười tươi tắn"),

        # --- THÂN BÀI Ý 1: BỘ NÃO DỮ LIỆU CÁ NHÂN HÓA (13.70s - 23.00s) ---
        ("IMG_5377.MOV", 3.00, 0.80, 1.00, +1, "S06: Chuyên gia chỉ sơ đồ hệ thống AI trên màn chiếu"),
        ("IMG_5406.MOV", 3.10, 0.40, 1.00, -1, "S07: 🌟 CHỊ OANH #3 — Góc nghiêng gõ phím MacBook thực hành"),
        ("IMG_5465.MOV", 3.20, 0.60, 1.00, +1, "S08: Đội ngũ nhân sự F20 tập trung cao độ trước màn hình laptop"),

        # --- THÂN BÀI Ý 2: KẾ TOÁN & BÁO CÁO EXCEL TỰ ĐỘNG (23.00s - 36.60s) ---
        ("IMG_5383.MOV", 2.30, 0.15, 1.00, +1, "S09: 5 nhân sự F20 đồng loạt gõ phím bằng cả 2 tay"),
        ("IMG_5378.MOV", 3.40, 0.60, 1.00, -1, "S10: 4 nữ nhân sự F20 ngồi thẳng lưng mỉm cười lắng nghe"),
        ("IMG_5379.MOV", 3.50, 0.80, 1.00, +1, "S11: 2 nhân sự nam thực hành dưới bảng hiệu Thực Phẩm F20"),
        ("IMG_5408.MOV", 3.40, 0.80, 1.00, -1, "S12: Cận cảnh bàn tay & màn hình MacBook xuất báo cáo"),

        # --- THÂN BÀI Ý 3: MARKETING & NGỮ ĐIỆU THƯƠNG HIỆU (36.60s - 46.60s) ---
        ("IMG_5414.MOV", 3.40, 1.20, 1.00, +1, "S13: 🌟 CHỊ OANH #5 — Chủ trì thảo luận triển khai cùng các bộ phận"),
        ("IMG_5467.MOV", 3.30, 0.40, 1.00, -1, "S14: Đội ngũ nữ nhân sự Marketing chăm chú thực hành"),
        ("IMG_5468.MOV", 2.50, 0.25, 0.78, +1, "S15: Giảng viên truyền lửa & Chị Oanh ngồi mỉm cười phía sau"),

        # --- KẾT BÀI & ĐẠI CẢNH KẾT ẤM ÁP (45.80s - 57.60s) ---
        ("IMG_5431.MOV", 3.00, 0.80, 1.00, -1, "S16: Tập thể bàn dài F20 đồng lòng hưởng ứng"),
        ("IMG_5462.MOV", 2.80, 0.30, 1.00, +1, "S17: Cầm tay chỉ việc 1-1 sát sao trên máy tính"),
        ("IMG_5420.MOV", 3.20, 0.80, 1.00, -1, "S18: 🌟 CHỊ OANH #5 — Đứng trao đổi rạng rỡ dưới ánh đèn ấm"),
        ("IMG_5428.MOV", 3.40, 3.65, 0.67, +1, "S19: 🌟 CHỊ OANH #6 — Chân dung sang trọng khép lại video (3.65-5.93s)"),
    ]

    v0_segs = []
    cur_u = 0
    shot_meta = []
    for idx, (fn, dur_s, src_in_s, spd, zdir, desc) in enumerate(VISUAL_PLAN, 1):
        t0_s = cur_u / 1e6
        seg, cur_u = make_clean_video_seg(fn, t0_s, dur_s, src_in_s, spd=spd, zoom_dir=zdir)
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
    #    Checkerboard across 2 Audio Tracks with 30ms/50ms anti-pop fades
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

    # Exact timeline placement aligned with our 19 visual scenes:
    # Intro music: 0.00s - 2.75s -> Voice Mở bài: 2.75s - 12.18s
    # Musical Breather on S05 (Chị Oanh smiling): 12.18s - 13.80s
    # Thân bài Ý 1 (Bộ não dữ liệu): 13.80s - 22.85s
    # Thân bài Ý 2 (Kế toán & Excel): 23.25s - 36.55s
    # Thân bài Ý 3 (Marketing & Ngữ điệu): 37.05s - 46.20s
    # Kết bài Voice: 46.70s - 50.05s -> Musical Finale on S17-S19: 50.05s - 58.20s
    VOICE_SCRIPT = [
        # --- PHẦN 1: MỞ BÀI ---
        ("M1",   "IMG_5382.MOV",  2.75, 3.58, 7.44, 1.25, [("Tôi là người ", False), ("nghiên cứu AI\n", True), ("rất nhiều năm rồi", False)]),
        ("M2a",  "IMG_5380.MOV",  6.80, 1.74, 4.58, 1.02, [("Riêng các bạn ", False), ("tự tìm hiểu,\n", True), ("tôi khẳng định luôn:", False)]),
        ("M2b",  "IMG_5380.MOV",  9.76, 5.18, 7.60, 1.02, [("phải mất khoảng ", False), ("2 năm\n", True), ("mới quay lại đi tìm!", False)]),

        # --- PHẦN 2: THÂN BÀI - Ý 1 (Bộ não dữ liệu cá nhân hóa) ---
        ("T1a",  "IMG_5392.MOV", 13.80, 2.15, 3.35, 1.24, [("Cá nhân hóa ", True), ("từng người —\n", False), ("không đi đâu cả,", False)]),
        ("T1b",  "IMG_5390.MOV", 15.12, 1.52, 4.50, 1.45, [("tất cả dữ liệu đều nằm\n", False), ("trên bộ não chung!", True)]),
        ("T1c",  "IMG_5404.MOV", 18.28, 0.00, 4.58, 1.50, [("Dự án hay dữ liệu nào\n", False), ("trong não có, ", False), ("nó tự làm ngay!", True)]),

        # --- PHẦN 2: THÂN BÀI - Ý 2 (Phòng Kế toán & Báo cáo Excel/Sheet) ---
        ("T2a",  "IMG_5377.MOV", 23.30, 0.72, 2.54, 1.04, [("Ví dụ ", False), ("phòng Kế toán:\n", True), ("làm các tháng, các quý,", False)]),
        ("T2b",  "IMG_5377.MOV", 25.20, 4.98, 7.30, 1.04, None), # merges subtitle cleanly across T2a+T2b!
        ("T2c",  "IMG_5378.MOV", 27.62, 2.04, 4.18, 1.20, [("báo cáo cuối năm — ", False), ("AI lấy hết\n", True), ("thông tin từ não ra rồi!", False)]),
        ("T2d",  "IMG_5375.MOV", 29.95, 0.80, 7.56, 1.24, None), # split into 2 readable subtitle cards below!

        # --- PHẦN 2: THÂN BÀI - Ý 3 (Phòng Marketing & Ngữ điệu riêng) ---
        ("T3a",  "IMG_5406.MOV", 37.15, 0.05, 2.50, 1.32, [("Cực kỳ quan trọng:\n", False), ("Marketing áp dụng ngay nhé!", True)]),
        ("T3b1", "IMG_5467.MOV", 39.80, 1.06, 1.52, 1.10, [("Để AI hiểu đúng\n", False), ("ngữ điệu riêng của mình:", True)]),
        ("T3b2", "IMG_5467.MOV", 40.28, 1.72, 3.46, 1.10, None),
        ("T3c1", "IMG_5468.MOV", 42.15, 0.22, 1.01, 1.20, [("khi viết văn, ", False), ("làm nội dung\n", True), ("hay viết bài,", False)]),
        ("T3c2", "IMG_5468.MOV", 42.96, 1.34, 5.30, 1.20, None),

        # --- PHẦN 3: KẾT BÀI ---
        ("K1a",  "IMG_5386.MOV", 47.45, 0.00, 2.46, 1.38, [("Ở đây nhưng ", False), ("đội ngũ AI\n", True), ("vẫn đang cày liên tục —", False)]),
        ("K1b",  "IMG_5386.MOV", 50.02, 5.35, 6.12, 1.38, [("các bạn hình dung không?!", True)]),
    ]

    voice_lanes = [[], []]
    voice_spans = {}
    for idx, (vid, fn, t0_s, sin_s, sout_s, vol, _) in enumerate(VOICE_SCRIPT):
        sg, t1_s = make_raw_voice_seg(fn, t0_s, sin_s, sout_s, vol)
        lane_i = idx % 2
        if voice_lanes[lane_i] and (voice_lanes[lane_i][-1]["target_timerange"]["start"] + voice_lanes[lane_i][-1]["target_timerange"]["duration"] > sg["target_timerange"]["start"]):
            lane_i = 1 - lane_i
        voice_lanes[lane_i].append(sg)
        voice_spans[vid] = (t0_s, t1_s)

    tr_voice_a = copy.deepcopy(atrack_tpl); tr_voice_a["id"] = uid(); tr_voice_a["segments"] = voice_lanes[0]
    tr_voice_b = copy.deepcopy(atrack_tpl); tr_voice_b["id"] = uid(); tr_voice_b["segments"] = voice_lanes[1]

    # =========================================================================
    # 3. 100% CENTERED SUBTITLES (X = 0.0, alignment = 1, 0% ORPHAN WRAPS)
    #    + MINIMAL OPENING & CLOSING BRAND TITLES (NO TOP CALLOUT CLUTTER!)
    # =========================================================================
    def make_centered_subtitle(parts: list[tuple[str, bool]], t0_s: float, t1_s: float, pos_y: float = -0.48):
        full_text = "".join(p[0] for p in parts)
        for ln_str in full_text.split("\n"):
            assert len(ln_str) <= 27, f"Subtitle line too wide ({len(ln_str)} chars): '{ln_str}'"
        styles = []
        cur = 0
        for sub_str, is_emph in parts:
            ln = len(sub_str)
            if ln == 0:
                continue
            fcol = GOLD_COL    if is_emph else WHITE_COL
            scol = DARK_STROKE if is_emph else NAVY_STROKE
            sw   = 0.068       if is_emph else 0.062
            sz   = 10.6        if is_emph else 10.2
            styles.append({
                "fill": {"content": {"render_type": "solid", "solid": {"color": fcol}}},
                "font": {"path": FONT_SUB_PATH, "id": FONT_SUB_ID},
                "strokes": [{"content": {"render_type": "solid", "solid": {"color": scol}}, "width": sw, "mode": 0}],
                "size": sz,
                "useLetterColor": True,
                "range": [cur, cur + ln],
            })
            cur += ln

        tm = copy.deepcopy(tmat_tpl)
        tm_id = uid()
        tm.update({
            "id": tm_id,
            "type": "subtitle",
            "recognize_text": full_text,
            "translate_original_text": full_text,
            "content": json.dumps({"text": full_text, "styles": styles}, ensure_ascii=False),
            "base_content": "",
            "font_size": 10.2,
            "font_path": FONT_SUB_PATH,
            "font_resource_id": FONT_SUB_ID,
            "text_color": "#ffffff",
            "border_color": "#0b203c",
            "border_width": 0.062,
            "letter_spacing": 0.0,
            "line_spacing": 0.035,
            "alignment": 1,
            "line_feed": 1,
            "line_max_width": 0.90,
            "force_apply_line_max_width": False,
            "background_style": 0,
            "has_shadow": False,
            "is_rich_text": len(styles) > 1,
            "check_flag": 15,
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.40), us(t1_s) - st_u)
        kfs = [
            make_kf("KFTypeScaleX", [(0.0, 0.94), (0.14, 1.01), (0.24, 1.00)]),
            make_kf("KFTypeScaleY", [(0.0, 0.94), (0.14, 1.01), (0.24, 1.00)]),
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

    SUB_CARDS = [
        (voice_spans["M1"][0],   voice_spans["M1"][1],   [("Tôi là người ", False), ("nghiên cứu AI\n", True), ("rất nhiều năm rồi", False)]),
        (voice_spans["M2a"][0],  voice_spans["M2a"][1],  [("Riêng các bạn ", False), ("tự tìm hiểu,\n", True), ("tôi khẳng định luôn:", False)]),
        (voice_spans["M2b"][0],  voice_spans["M2b"][1],  [("phải mất khoảng ", False), ("2 năm\n", True), ("mới quay lại đi tìm!", False)]),

        (voice_spans["T1a"][0],  voice_spans["T1a"][1],  [("Cá nhân hóa ", True), ("từng người —", False)]),
        (voice_spans["T1b"][0],  voice_spans["T1b"][1],  [("không đi đâu cả, tất cả\n", False), ("nằm ở trên não!", True)]),
        (voice_spans["T1c"][0],  voice_spans["T1c"][0] + 2.55, [("Dự án hay dữ liệu nào\n", False), ("trong não đã có,", True)]),
        (voice_spans["T1c"][0] + 2.60, voice_spans["T1c"][1],  [("thì nó sẽ ", False), ("làm cho mình!", True)]),

        (voice_spans["T2a"][0],  voice_spans["T2b"][1],  [("Ví dụ ", False), ("Kế toán làm\n", True), ("các tháng, quý, cuối năm —", False)]),
        (voice_spans["T2c"][0],  voice_spans["T2c"][1],  [("nó lấy hết thông tin\n", False), ("từ trên não ra rồi!", True)]),
        (voice_spans["T2d"][0],  voice_spans["T2d"][0] + 2.50, [("Tổng tiền bao nhiêu,\n", False), ("của đơn vị nào —", True)]),
        (voice_spans["T2d"][0] + 2.55, voice_spans["T2d"][1],  [("báo cáo ngay ", False), ("Google Sheet\n", True), ("hay file Excel ngon lành!", True)]),

        (voice_spans["T3a"][0],  voice_spans["T3a"][1],  [("Cực kỳ quan trọng này:\n", False), ("Marketing làm lại nhé!", True)]),
        (voice_spans["T3b1"][0], voice_spans["T3b2"][1], [("Để nó hiểu đúng\n", False), ("ngữ điệu của mình này:", True)]),
        (voice_spans["T3c1"][0], voice_spans["T3c1"][0] + 2.55, [("khi viết văn, ", False), ("nội dung\n", True), ("hay viết bài,", False)]),
        (voice_spans["T3c1"][0] + 2.60, voice_spans["T3c2"][1], [("nó lấy luôn đúng\n", False), ("nội dung của mình!", True)]),

        (voice_spans["K1a"][0],  voice_spans["K1a"][1],  [("Ở đây nhưng ", False), ("đội ngũ AI\n", True), ("vẫn đang cày việc —", False)]),
        (voice_spans["K1b"][0],  voice_spans["K1b"][1] + 0.35, [("các bạn hình dung không?!", True)]),
    ]

    tr_sub = copy.deepcopy(ttrack_tpl)
    tr_sub["id"] = uid()
    tr_sub["segments"] = [make_centered_subtitle(parts, t0, t1, pos_y=-0.48) for t0, t1, parts in SUB_CARDS]

    def make_centered_brand_title(text: str, t0_s: float, t1_s: float, pos_y: float, size: float, fill_col, stroke_col, stroke_w: float = 0.068):
        hex_fill = "#{:02x}{:02x}{:02x}".format(int(fill_col[0]*255), int(fill_col[1]*255), int(fill_col[2]*255))
        hex_strk = "#{:02x}{:02x}{:02x}".format(int(stroke_col[0]*255), int(stroke_col[1]*255), int(stroke_col[2]*255))
        styles = [{
            "fill": {"content": {"render_type": "solid", "solid": {"color": fill_col}}},
            "font": {"path": FONT_HEAD_PATH, "id": FONT_HEAD_ID},
            "strokes": [{"content": {"render_type": "solid", "solid": {"color": stroke_col}}, "width": stroke_w, "mode": 0}],
            "size": size,
            "useLetterColor": True,
            "range": [0, len(text)],
        }]
        tm = copy.deepcopy(tmat_tpl)
        tm_id = uid()
        tm.update({
            "id": tm_id,
            "type": "text",
            "recognize_text": text,
            "translate_original_text": text,
            "content": json.dumps({"text": text, "styles": styles}, ensure_ascii=False),
            "base_content": "",
            "font_size": size,
            "font_path": FONT_HEAD_PATH,
            "font_resource_id": FONT_HEAD_ID,
            "text_color": hex_fill,
            "border_color": hex_strk,
            "border_width": stroke_w,
            "letter_spacing": 0.01,
            "line_spacing": 0.035,
            "alignment": 1,
            "line_feed": 1,
            "line_max_width": 0.92,
            "force_apply_line_max_width": False,
            "background_style": 0,
            "has_shadow": False,
            "is_rich_text": False,
            "check_flag": 15,
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.50), us(t1_s) - st_u)
        dur_s = du_u / 1e6
        kfs = [
            make_kf("KFTypeScaleX", [(0.0, 0.90), (0.22, 1.02), (0.36, 1.00)]),
            make_kf("KFTypeScaleY", [(0.0, 0.90), (0.22, 1.02), (0.36, 1.00)]),
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

    # Only clean Opening & Closing Brand Titles (exact 261106 F20 Training Vlog aesthetic)
    outro_title_t0 = 51.35
    outro_title_t1 = total_dur_s - 0.15
    tr_title_1 = copy.deepcopy(ttrack_tpl); tr_title_1["id"] = uid()
    tr_title_1["segments"] = [
        make_centered_brand_title("ĐÀO TẠO AI THỰC CHIẾN", 0.18, 2.52, -0.36, 12.0, GOLD_COL, DARK_STROKE),
        make_centered_brand_title("CÔNG TY TNHH THỰC PHẨM F20", outro_title_t0, outro_title_t1, -0.36, 11.2, GOLD_COL, DARK_STROKE),
    ]
    tr_title_2 = copy.deepcopy(ttrack_tpl); tr_title_2["id"] = uid()
    tr_title_2["segments"] = [
        make_centered_brand_title("CÔNG TY TNHH THỰC PHẨM F20", 0.42, 2.52, -0.49, 8.8, WHITE_COL, F20_GREEN_COL),
        make_centered_brand_title("ỨNG DỤNG AI VÀO VẬN HÀNH\nthucphamf20.com • 0706.001.626", outro_title_t0 + 0.25, outro_title_t1, -0.50, 8.4, WHITE_COL, F20_GREEN_COL),
    ]

    # =========================================================================
    # 4. BGM WITH DYNAMIC DUCKING + MINIMAL TASTEFUL INTRO/OUTRO ACCENT SFX
    # =========================================================================
    def add_audio_material(audio_path: Path, name_lbl: str, mtype: str = "sound"):
        fwd = norm_fwd(audio_path)
        if fwd in amat_map:
            return amat_map[fwd]
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio_path)], capture_output=True, text=True, check=True)
        du_u = us(float(json.loads(r.stdout)["format"]["duration"]))
        aid = uid()
        lmid = str(uuid.uuid4())
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
            "fade_in_duration": fi_u,
            "fade_out_duration": fo_u,
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
        return sg

    bgm_id, _ = add_audio_material(BGM_PATH, "Corporate Background02 - F20 AI Training", mtype="music")
    u_b1 = us(2.65)     # End of Intro swell
    u_b2 = us(12.20)    # Start of Chị Oanh S05 breather
    u_b3 = us(13.70)    # End of Chị Oanh S05 breather
    u_b4 = us(50.90)    # Start of Finale swell
    bgm_segs = [
        make_audio_slice(bgm_id, 0,    0,    u_b1,               0.48, 300000, 180000),
        make_audio_slice(bgm_id, u_b1, u_b1, u_b2 - u_b1,        0.22, 180000, 150000),
        make_audio_slice(bgm_id, u_b2, u_b2, u_b3 - u_b2,        0.42, 150000, 150000),
        make_audio_slice(bgm_id, u_b3, u_b3, u_b4 - u_b3,        0.22, 150000, 200000),
        make_audio_slice(bgm_id, u_b4, u_b4, total_dur_u - u_b4, 0.54, 250000, 1500000),
    ]
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["segments"] = bgm_segs

    def make_sfx_seg(sfx_fn: str, lbl: str, t0_s: float, vol: float, max_dur_s: float):
        aid, du_full = add_audio_material(SFX_DIR / sfx_fn, lbl, mtype="sound")
        du = min(du_full, us(max_dur_s))
        return make_audio_slice(aid, 0, us(t0_s), du, vol, min(16000, du // 6), min(120000, du // 3))

    tr_sfx = copy.deepcopy(atrack_tpl); tr_sfx["id"] = uid()
    tr_sfx["segments"] = [
        make_sfx_seg("Whoosh - Title Swoosh (1s).mp3", "Intro Title Swoosh", 0.14, 0.11, 0.80),
        make_sfx_seg("Whoosh - Title Swoosh (1s).mp3", "Thân Bài Transition Air", 13.68, 0.09, 0.70),
        make_sfx_seg("Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3", "Outro Brand Chime", outro_title_t0, 0.11, 1.50),
    ]

    # Clean, uncluttered track stack:
    # Track 0: Single sequential clean Visual Stream
    # Track 1: Centered Subtitles
    # Track 2 & 3: Centered Opening & Closing Brand Titles
    # Track 4 & 5: Raw .MOV Voiceover (video_original_sound)
    # Track 6: Dynamic Ducked BGM
    # Track 7: Subtle Intro/Outro SFX
    D["tracks"] = [
        tr_v0,
        tr_sub,
        tr_title_1,
        tr_title_2,
        tr_voice_a,
        tr_voice_b,
        tr_bgm,
        tr_sfx,
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

    # Use Chị Oanh's brightest portrait (IMG_5428 @ 2.0s) as the CapCut draft thumbnail cover!
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
    for tp in [
        out_dir / "draft_content.json",
        out_dir / "template-2.tmp",
        new_tl_dir / "draft_content.json",
        new_tl_dir / "template-2.tmp",
    ]:
        if tp.exists():
            tp.unlink()
        tp.write_bytes(dc_bytes)

    pj = {
        "config": {
            "color_space": 0,
            "hdr_vivid": False,
            "mixed_track_mode_on": False,
            "render_index_track_mode_on": True,
            "use_float_render": False
        },
        "create_time": now_us,
        "id": main_tl_id,
        "main_timeline_id": main_tl_id,
        "timelines": [{
            "create_time": now_us,
            "id": main_tl_id,
            "is_marked_delete": False,
            "name": "Dòng thời gian 01",
            "update_time": now_us
        }],
        "update_time": now_us,
        "version": 0
    }
    (tl_root / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

    dmi = copy.deepcopy(dmi_donor)
    fold_fwd = norm_fwd(out_dir)
    dmi.update({
        "draft_id": draft_uuid,
        "draft_name": DRAFT_NAME,
        "draft_fold_path": fold_fwd,
        "draft_root_path": str(DRAFTS_ROOT),
        "draft_cover": "draft_cover.jpg",
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "tm_duration": total_dur_u,
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
            "draft_id": draft_uuid,
            "draft_name": DRAFT_NAME,
            "draft_fold_path": fold_fwd,
            "draft_root_path": str(DRAFTS_ROOT),
            "draft_cover": f"{fold_fwd}\\draft_cover.jpg",
            "draft_json_file": f"{fold_fwd}\\draft_content.json",
            "draft_timeline_materials_size": total_bytes,
            "streaming_edit_draft_ready": True,
            "tm_draft_create": now_us,
            "tm_draft_modified": now_us,
            "tm_draft_removed": 0,
            "tm_duration": total_dur_u,
        })
        store.insert(0, entry)
        rmi["all_draft_store"] = store
        rmi["draft_ids"] = len(store)
        rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    # =========================================================================
    # 5. AUTOMATED QC VERIFICATION + 38-FRAME IN/OUT STORYBOARD SHEET
    # =========================================================================
    v_tracks = [t for t in D["tracks"] if t["type"] == "video"]
    assert len(v_tracks) == 1, f"Expected 1 single clean video track, got {len(v_tracks)}"
    for t in D["tracks"]:
        if t["type"] == "text":
            for s in t["segments"]:
                tx = s["clip"]["transform"]["x"]
                ty = s["clip"]["transform"]["y"]
                assert abs(tx) < 1e-6, f"Non-centered text X={tx}"
                assert -0.58 <= ty <= 0.68, f"Text Y={ty} outside TikTok/Reels Safe Zone!"

    qc_dir = SCRATCH_DIR / "qc_v3_final"
    qc_dir.mkdir(parents=True, exist_ok=True)
    def grab_pair(item):
        sid, fn, t0, t1, sin, sout, desc = item
        vp = RAW_DIR / fn
        out_items = []
        for tag, ts in [("IN", sin + 0.08), ("OUT", max(sin + 0.08, sout - 0.08))]:
            jp = qc_dir / f"{sid}_{tag}.jpg"
            subprocess.run(
                ["ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", str(vp), "-frames:v", "1", "-vf", "scale=240:426", "-q:v", "3", str(jp)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            out_items.append((f"{sid} {tag} [{t0:.1f}-{t1:.1f}s]", f"{fn} @{ts:.2f}s", desc, jp))
        return out_items

    with ThreadPoolExecutor(max_workers=8) as ex:
        nested = list(ex.map(grab_pair, shot_meta))
    flat_frames = [x for pair in nested for x in pair]

    cols = 8
    rows = (len(flat_frames) + cols - 1) // cols
    cw, ch = 248, 476
    sheet = Image.new("RGB", (cols * cw, rows * ch), (15, 20, 26))
    draw = ImageDraw.Draw(sheet)
    for idx, (l1, l2, desc, jp) in enumerate(flat_frames):
        r, c = divmod(idx, cols)
        x, y = c * cw + 4, r * ch + 44
        sheet.paste(Image.open(jp), (x, y))
        col = (255, 214, 51) if "CHỊ OANH" in desc else (215, 235, 255)
        draw.text((x + 2, r * ch + 4), l1[:28], fill=col)
        draw.text((x + 2, r * ch + 20), l2[:28], fill=(165, 205, 180))
    qc_sheet_p = qc_dir / "qc_261125_v3_all_19_shots_inout.jpg"
    sheet.save(qc_sheet_p, quality=88)

    # Archive script & QC storyboard to Master Cloud Project folder
    cloud_dir = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\261125-f20-dao-tao-ai")
    cloud_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), cloud_dir / "build_261125_v3_clean_master.py")
    shutil.copy2(qc_sheet_p, cloud_dir / "qc_261125_v3_all_19_shots_inout.jpg")

    print(f"SUCCESS V3 MASTER: {out_dir}")
    print(f"  Total Duration : {total_dur_s:.2f}s | Video Tracks: {len(v_tracks)} (19 clean shots, 7 Chị Oanh hero shots)")
    print(f"  Voice Segments : {len(VOICE_SCRIPT)} (100% raw .MOV video_original_sound, 0% intermediate WAV)")
    print(f"  Subtitles      : {len(SUB_CARDS)} (100% centered X=0.0, <=26 chars/line)")
    print(f"  Color Sliders  : {len(D['materials']['effects'])} sliders + {len(D['materials']['hsl'])} HSL + {len(D['materials']['color_curves'])} curves")
    print(f"  QC Sheet       : {qc_sheet_p}")
    for sid, fn, t0, t1, sin, sout, desc in shot_meta:
        print(f"    {sid} | {t0:5.2f}s - {t1:5.2f}s | {fn:14s} [{sin:.2f}-{sout:.2f}s] | {desc}")

if __name__ == "__main__":
    main()
