import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path

W, H = 1080, 1920
FPS = 30.0

DRAFT_NAME   = "261125 F20 Đào Tạo AI Thực Chiến"
FIXED_DRAFT_ID = "1EFBAEDD-2850-4E30-8E32-57F4237424BD"  # Matches live CapCut Home Screen card ID!

DRAFTS_ROOT  = Path(r"C:\CapCut Drafts")
APPDATA_ROOT = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
TPL_1126_DIR = DRAFTS_ROOT / "1126"
TPL_HTAV_DIR = DRAFTS_ROOT / "HT-AV"
BAK_1117_JSON = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\f20-set-qua-2011\1117_F20_CapCut_Backup\draft_content.json")

RAW_DIR      = Path(r"G:\Other computers\My Computer\F20\video gốc\261125")
TLH_EDIT     = Path(r"G:\Other computers\My Computer\Document HT Media\TLH\Edit")
BGM_PATH     = TLH_EDIT / r"01_Nhạc Nền (BGM)\01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Corporate Background02 (2p19s).mp3"
SFX_DIR      = TLH_EDIT / r"02_Hiệu Ứng Âm Thanh (SFX)"
FONT_SRC_DIR = TLH_EDIT / r"04_Font Chữ TVC & Chữ Gradient"

CC_CACHE_EFF = Path(r"C:\Users\001\AppData\Local\CapCut\User Data\Cache\effect")

# Stage clean local ASCII CapCut font cache entries with official CapCut resource_ids!
SUB_CACHE_DIR  = CC_CACHE_EFF / "7542214368361057553" / "d376267c892ee3a53654ae93a78dcfb7"
HEAD_CACHE_DIR = CC_CACHE_EFF / "7517455788122705168" / "91d28cfa5e7db054f4872f1ae2417ac2"
SUB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
HEAD_CACHE_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(FONT_SRC_DIR / "BeVietnamPro-Bold.ttf", SUB_CACHE_DIR / "font.ttf")
shutil.copy2(FONT_SRC_DIR / "Montserrat-ExtraBold.ttf", HEAD_CACHE_DIR / "Montserrat-Bold.otf")

FONT_SUB_ID    = "7542214368361057553"
FONT_SUB_PATH  = str(SUB_CACHE_DIR / "font.ttf").replace("\\", "/")
FONT_HEAD_ID   = "7517455788122705168"
FONT_HEAD_PATH = str(HEAD_CACHE_DIR / "Montserrat-Bold.otf").replace("\\", "/")

CC_EFF_FWD     = "C:/Users/001/AppData/Local/CapCut/User Data/Cache/effect"
RECT_MASK_PATH = f"{CC_EFF_FWD}/1068046537/02b8999168d121538a98ea59127483ef"
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
    "1K88BFQG5_A0EH1R.mp4", "IMG_5377.MOV", "IMG_5381.MOV", "IMG_5382.MOV",
    "IMG_5385.MOV", "IMG_5386.MOV", "IMG_5388.MOV", "IMG_5389.MOV",
    "IMG_5391.MOV", "IMG_5393.MOV", "IMG_5399.MOV", "IMG_5401.MOV",
    "IMG_5402.MOV", "IMG_5403.MOV", "IMG_5404.MOV", "IMG_5412.MOV",
    "IMG_5425.MOV", "IMG_5428.MOV", "IMG_5434.MOV", "IMG_5468.MOV",
}
GLASS_CLOSEUP_CLIPS = {
    "IMG_5397.MOV", "IMG_5405.MOV", "IMG_5406.MOV", "IMG_5407.MOV",
    "IMG_5408.MOV", "IMG_5414.MOV", "IMG_5415.MOV", "IMG_5416.MOV",
    "IMG_5420.MOV", "IMG_5421.MOV", "IMG_5422.MOV", "IMG_5427.MOV",
    "IMG_5429.MOV", "IMG_5436.MOV", "IMG_5438.MOV", "IMG_5461.MOV",
    "IMG_5462.MOV", "IMG_5463.MOV", "IMG_5464.MOV",
}

ZONE_PROFILES = {
    "BLUE_TEAM": {
        "sliders": {
            "brightness": 0.03, "contrast": 0.06, "saturation": 0.06, "sharpen": 0.12,
            "highlight": -0.09, "shadow": 0.09, "white": 0.02, "black": -0.02,
            "clear": 0.09, "temperature": 0.04, "tone": 0.03, "light_sensation": 0.06,
        },
        "hsl": {
            1: (0,  10,   4),
            2: (0,  -5,  12),
            3: (0, -10,   4),
            4: (0,   8,   2),
            6: (-2, 12,   6),
            7: (0, -14,  -4),
            8: (0,   0,   0),
        }
    },
    "PROJECTOR": {
        "sliders": {
            "brightness": 0.06, "contrast": 0.05, "saturation": 0.08, "sharpen": 0.14,
            "highlight": -0.15, "shadow": 0.16, "white": -0.02, "black": -0.03,
            "clear": 0.12, "temperature": -0.03, "tone": 0.04, "light_sensation": 0.08,
        },
        "hsl": {
            1: (0,   8,   4),
            2: (0,  -4,  14),
            3: (0, -12,   5),
            4: (0,   6,   2),
            6: (-2, 10,   5),
            7: (0, -10,  -2),
            8: (0,   0,   0),
        }
    },
    "GLASS_CLOSEUP": {
        "sliders": {
            "brightness": 0.04, "contrast": 0.07, "saturation": 0.08, "sharpen": 0.12,
            "highlight": -0.10, "shadow": 0.10, "white": 0.03, "black": -0.03,
            "clear": 0.10, "temperature": 0.05, "tone": 0.03, "light_sensation": 0.07,
        },
        "hsl": {
            1: (0,  10,   4),
            2: (0,  -4,  11),
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
    if filename in GLASS_CLOSEUP_CLIPS:
        return "GLASS_CLOSEUP"
    return "BLUE_TEAM"


def main():
    for must_p in [TPL_1126_DIR, TPL_HTAV_DIR, BAK_1117_JSON, RAW_DIR, BGM_PATH, Path(FONT_SUB_PATH), Path(FONT_HEAD_PATH), Path(RECT_MASK_PATH), Path(ADJUST_PATH), Path(CURVES_PATH)]:
        if not must_p.exists():
            raise FileNotFoundError(f"Required local asset/template missing: {must_p}")

    d_1126 = json.loads((TPL_1126_DIR / "draft_content.json").read_text(encoding="utf-8"))
    d_htav = json.loads((TPL_HTAV_DIR / "draft_content.json").read_text(encoding="utf-8"))
    d_1117 = json.loads(BAK_1117_JSON.read_text(encoding="utf-8"))
    dmi_1126 = json.loads((TPL_1126_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))

    # CRITICAL v193 INVARIANT: D["id"] MUST EQUAL main_tl_id == Timelines/<main_tl_id> == timeline_layout.json!
    draft_uuid = FIXED_DRAFT_ID
    main_tl_id = "A6112500-F20A-4E30-8E32-57F4237424BD"
    now_s  = int(time.time())
    now_us = int(time.time() * 1_000_000)

    D = copy.deepcopy(d_htav)  # Clone from HT-AV (proven multi-track v193.0.0 project on THIS exact PC!)
    D["id"] = main_tl_id
    D["name"] = ""
    D["canvas_config"] = {"ratio": "original", "width": W, "height": H, "background": None}
    D["fps"] = FPS
    D["render_index_track_mode_on"] = True
    D["free_render_index_mode_on"] = False

    vtrack_tpl = copy.deepcopy(d_1126["tracks"][0])
    vseg_tpl   = copy.deepcopy(d_1126["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(d_1126["materials"]["videos"][0])
    dm_mat_tpl = copy.deepcopy(dmi_1126["draft_materials"][0]["value"][1])

    slider_tpls = {}
    for ef in d_1126["materials"]["effects"] + d_htav["materials"]["effects"]:
        et = ef.get("type")
        if et in ("brightness", "contrast", "saturation", "sharpen", "highlight", "shadow", "white", "black", "clear", "temperature", "tone", "light_sensation") and et not in slider_tpls:
            slider_tpls[et] = copy.deepcopy(ef)
    hsl_tpls = {h["hsl_color_type"]: copy.deepcopy(h) for h in d_1126["materials"]["hsl"]}
    curve_tpl = copy.deepcopy(d_htav["materials"]["color_curves"][0])

    ttrack_tpl = copy.deepcopy(next(t for t in d_1117["tracks"] if t["type"] == "text"))
    tseg_tpl   = copy.deepcopy(ttrack_tpl["segments"][0])
    tmat_tpl   = copy.deepcopy(d_1117["materials"]["texts"][0])

    atrack_tpl = copy.deepcopy(next(t for t in d_1117["tracks"] if t["type"] == "audio"))
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    amat_tpl   = copy.deepcopy(d_1117["materials"]["audios"][0])

    # Clone exact verified keyframe template directly from 1117!
    kf_tpl = copy.deepcopy(next(sg["common_keyframes"][0] for tr in d_1117["tracks"] for sg in tr["segments"] if sg.get("common_keyframes")))

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl = {
        k: copy.deepcopy(d_1126["materials"][k][0])
        for k in v_extra_keys if d_1126["materials"].get(k)
    }
    a_extra_keys = ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl = {
        k: copy.deepcopy(next(x for x in d_1117["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"]))
        for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in d_1117["materials"].get(k, []))
    }

    # Clear all material lists cleanly
    for k, val in list(D["materials"].items()):
        if isinstance(val, list):
            D["materials"][k] = []

    vmat_map = {}
    amat_map = {}
    dm_entries = [copy.deepcopy(dmi_1126["draft_materials"][0]["value"][0])]

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
        lmid = str(uuid.uuid4())
        m = copy.deepcopy(vmat_tpl)
        m.update({
            "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
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
        vmat_map[fwd] = (mid, dur_u, w, h)
        return mid, dur_u, w, h

    # Use ONLY 100% verified CapCut C++ keyframe property_types:
    # KFTypeScaleX, KFTypeScaleY, KFTypePositionX, KFTypePositionY!
    VALID_KF_PROPS = {"KFTypeScaleX", "KFTypeScaleY", "KFTypePositionX", "KFTypePositionY", "KFTypeRotation"}
    def make_kf(prop_type: str, pts_sec_val: list[tuple[float, float]]):
        assert prop_type in VALID_KF_PROPS, f"Unverified keyframe enum: {prop_type}"
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

    def attach_native_color_grade(refs: list[str], fn: str, darken_backdrop: bool = False):
        zname = get_zone_name(fn)
        prof = ZONE_PROFILES[zname]
        for stype, sval in prof["sliders"].items():
            if stype not in slider_tpls:
                continue
            ef = copy.deepcopy(slider_tpls[stype])
            ef["id"] = uid()
            val = float(sval)
            if darken_backdrop and stype == "brightness":
                val = -0.34
            elif darken_backdrop and stype == "contrast":
                val = -0.06
            ef["value"] = round(val, 4)
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

    def make_video_seg(
        fn: str, t0_s: float, t1_s: float, src_in_s: float,
        spd: float = 1.0, vol: float = 0.0,
        zoom_dir: int = 0, base_scale: float = 1.0, tx: float = 0.0, ty: float = 0.0,
        slide_in_x: float = 0.0, pop_in: bool = False,
        mask_cfg: dict | None = None, darken_backdrop: bool = False
    ):
        mid, mat_dur_u, w, h = get_or_add_raw_video(fn)
        tgt_st_u = us(t0_s)
        tgt_du_u = max(us(0.18), us(t1_s) - tgt_st_u)
        src_st_u = us(src_in_s)
        src_du_u = us((tgt_du_u / 1e6) * spd)
        if src_st_u + src_du_u > mat_dur_u:
            src_st_u = max(0, mat_dur_u - src_du_u)
        dur_s = tgt_du_u / 1e6

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e)
            em["id"] = uid()
            if k == "speeds":
                em["speed"] = round(spd, 3)
            D["materials"][k].append(em)
            refs.append(em["id"])

        if vol > 0.01:
            af_id = uid()
            D["materials"].setdefault("audio_fades", []).append({
                "fade_in_duration": 33333,
                "fade_out_duration": 66666,
                "fade_type": 0, "id": af_id, "type": "audio_fade"
            })
            refs.append(af_id)

        attach_native_color_grade(refs, fn, darken_backdrop=darken_backdrop)

        if mask_cfg is not None:
            mk_id = uid()
            D["materials"].setdefault("common_mask", []).append({
                "config": mask_cfg,
                "id": mk_id, "name": "Hình chữ nhật", "path": RECT_MASK_PATH,
                "platform": "all", "position_info": "", "resource_id": "7374021450748924432",
                "resource_type": "rectangle", "source_platform": 1, "type": "mask"
            })
            refs.append(mk_id)

        seg["clip"]["scale"] = {"x": round(base_scale, 4), "y": round(base_scale, 4)}
        seg["clip"]["transform"] = {"x": round(tx, 4), "y": round(ty, 4)}
        seg["clip"]["rotation"] = 0.0
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": round(base_scale, 4)}
        seg["hdr_settings"] = {"intensity": 1.0, "mode": 1, "nits": 1000}

        kfs = []
        if zoom_dir != 0 and mask_cfg is None and dur_s >= 2.2:
            s0, s1 = (base_scale, round(base_scale * 1.045, 4)) if zoom_dir > 0 else (round(base_scale * 1.045, 4), base_scale)
            kfs.append(make_kf("KFTypeScaleX", [(0.0, s0), (dur_s, s1)]))
            kfs.append(make_kf("KFTypeScaleY", [(0.0, s0), (dur_s, s1)]))
        elif pop_in:
            s_start = round(base_scale * 0.86, 4)
            s_over  = round(base_scale * 1.02, 4)
            kfs.append(make_kf("KFTypeScaleX", [(0.0, s_start), (0.18, s_over), (0.28, base_scale)]))
            kfs.append(make_kf("KFTypeScaleY", [(0.0, s_start), (0.18, s_over), (0.28, base_scale)]))

        if abs(slide_in_x) > 0.005:
            kfs.append(make_kf("KFTypePositionX", [(0.0, tx + slide_in_x), (min(0.24, dur_s * 0.35), tx)]))

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": src_st_u, "duration": src_du_u},
            "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
            "speed": round(spd, 3),
            "volume": round(vol, 3),
            "last_nonzero_volume": round(vol if vol > 0.01 else 1.0, 3),
            "extra_material_refs": refs,
            "common_keyframes": kfs,
            "keyframe_refs": [],
        })
        return seg

    # ==========================================================================
    # TRACK 0 — CONTINUOUS VISUAL & VOICE SPINE (0.00s -> 82.50s, Zero Gaps!)
    # ==========================================================================
    TRACK0_PLAN = [
        ("IMG_5409.MOV", 0.70, 0.80, 1.00, 0.00,  0),
        ("IMG_5408.MOV", 0.70, 1.00, 1.00, 0.00,  0),
        ("IMG_5377.MOV", 0.70, 0.10, 1.00, 0.00,  0),

        ("IMG_5380.MOV", 5.50, 2.05, 1.00, 1.38, +1),
        ("IMG_5375.MOV", 0.20, 0.60, 1.00, 0.00,  0),
        ("IMG_5375.MOV", 6.80, 0.80, 1.00, 1.38, -1),
        ("IMG_5375.MOV", 0.60, 8.60, 1.00, 1.44,  0),

        ("IMG_5433.MOV", 0.30, 3.25, 1.00, 0.00,  0),
        ("IMG_5433.MOV", 7.27, 3.55, 1.00, 1.72, +1),
        ("IMG_5377.MOV", 0.26, 0.29, 1.00, 0.00,  0),
        ("IMG_5377.MOV", 6.63, 0.55, 1.00, 1.36, -1),
        ("IMG_5378.MOV", 2.37, 1.95, 1.00, 1.38, +1),
        ("IMG_5423.MOV", 6.77, 0.35, 1.00, 1.56, -1),

        ("IMG_5392.MOV", 2.35, 1.20, 1.00, 1.36, +1),
        ("IMG_5393.MOV", 2.05, 0.20, 1.00, 1.40,  0),
        ("IMG_5399.MOV", 2.57, 1.98, 1.00, 1.42, +1),
        ("IMG_5403.MOV", 4.57, 1.45, 1.00, 1.42, -1),
        ("IMG_5404.MOV", 4.65, 0.00, 1.00, 1.45, +1),
        ("IMG_5406.MOV", 2.58, 0.00, 1.00, 1.42, -1),
        ("IMG_5407.MOV", 1.60, 0.62, 1.00, 1.45,  0),

        ("IMG_5467.MOV", 3.08, 0.42, 1.00, 1.36, +1),
        ("IMG_5468.MOV", 5.24, 0.18, 1.00, 1.38, -1),
        ("IMG_5438.MOV", 0.27, 0.28, 1.00, 0.00,  0),
        ("IMG_5438.MOV", 7.83, 0.55, 1.00, 1.58, +1),

        ("IMG_5386.MOV", 2.52, 0.00, 1.00, 1.38, -1),
        ("IMG_5386.MOV", 0.80, 5.35, 1.00, 1.44,  0),
        ("IMG_5463.MOV", 1.20, 1.20, 0.85, 0.00, +1),
        ("IMG_5420.MOV", 1.20, 1.00, 0.85, 0.00, -1),
        ("IMG_5444.MOV", 1.20, 0.80, 0.85, 0.00, +1),
    ]

    t0_segs = []
    cur_s = 0.0
    for fn, dur_s, sin_s, spd, vol, zdir in TRACK0_PLAN:
        nxt_s = round(cur_s + dur_s, 4)
        sg = make_video_seg(fn, cur_s, nxt_s, sin_s, spd=spd, vol=vol, zoom_dir=zdir)
        if t0_segs:
            prev_end = t0_segs[-1]["target_timerange"]["start"] + t0_segs[-1]["target_timerange"]["duration"]
            end_u = us(nxt_s)
            sg["target_timerange"]["start"] = prev_end
            sg["target_timerange"]["duration"] = max(33333, end_u - prev_end)
        t0_segs.append(sg)
        cur_s = nxt_s

    total_dur_u = t0_segs[-1]["target_timerange"]["start"] + t0_segs[-1]["target_timerange"]["duration"]
    total_dur_s = total_dur_u / 1e6

    tr_v0 = copy.deepcopy(vtrack_tpl)
    tr_v0["id"] = uid()
    tr_v0["segments"] = t0_segs

    # ==========================================================================
    # TRACK 1 — FULL-SCREEN RAW B-ROLL OVERLAYS
    # ==========================================================================
    BROLL_FULL_PLAN = [
        ("IMG_5384.MOV",  4.20,  5.85, 0.60, 1.00,  0, False),
        ("IMG_5379.MOV",  5.85,  7.85, 0.80, 1.00, +1, False),
        ("IMG_5395.MOV", 11.10, 13.00, 1.00, 1.00,  0, False),
        ("IMG_5390.MOV", 13.00, 15.55, 0.60, 1.00, +1, False),
        ("IMG_5432.MOV", 18.80, 21.20, 1.20, 1.00, -1, False),
        ("IMG_5387.MOV", 25.40, 27.60, 0.50, 1.00,  0, False),
        ("IMG_5414.MOV", 27.60, 29.85, 1.20, 1.00, +1, False),
        ("IMG_5445.MOV", 34.60, 36.90, 0.80, 0.90, +1, False),
        ("1K88BFQG5_A0EH1R.mp4", 38.80, 43.20, 0.40, 1.00, 0, True),
        ("IMG_5428.MOV", 47.60, 50.40, 3.00, 1.00, +1, False),
        ("IMG_5461.MOV", 52.10, 55.02, 0.40, 1.00, -1, False),
        ("IMG_5408.MOV", 57.57, 59.20, 0.40, 1.00,  0, False),
        ("IMG_5465.MOV", 60.60, 62.45, 0.80, 1.00,  0, False),
        ("IMG_5462.MOV", 64.40, 66.10, 0.30, 1.00,  0, False),
        ("IMG_5429.MOV", 66.10, 67.80, 0.50, 1.00,  0, False),
        ("IMG_5442.MOV", 71.80, 74.10, 0.80, 1.00, +1, False),
        ("IMG_5410.MOV", 76.80, 78.91, 1.20, 1.00, +1, False),
    ]

    tr_v1 = copy.deepcopy(vtrack_tpl)
    tr_v1["id"] = uid()
    tr_v1["segments"] = [
        make_video_seg(fn, t0, t1, sin, spd=spd, vol=0.0, zoom_dir=zd, darken_backdrop=dk)
        for fn, t0, t1, sin, spd, zd, dk in BROLL_FULL_PLAN
    ]

    # ==========================================================================
    # TRACKS 2..5 — SAFE-ZONE CORNER PIPs + 4-TRACK RAW 2x2 BENTO GRID
    # ==========================================================================
    PIP_MASK = {
        "aspectRatio": 0.78, "centerX": 0.0, "centerY": 0.0, "expansion": 0.0,
        "feather": 0.015, "height": 0.84, "invert": False, "rotation": 0.0,
        "roundCorner": 0.18, "width": 0.86,
    }
    BENTO_MASK = {
        "aspectRatio": 0.75, "centerX": 0.0, "centerY": 0.0, "expansion": 0.0,
        "feather": 0.01, "height": 0.44, "invert": False, "rotation": 0.0,
        "roundCorner": 0.16, "width": 0.72,
    }

    bento_sc = 0.45
    bento_specs = [
        ("IMG_5406.MOV",         38.82, 0.40, -0.47, +0.38),
        ("IMG_5462.MOV",         39.00, 0.50, +0.25, +0.38),
        ("IMG_5390.MOV",         39.18, 1.00, -0.47, -0.08),
        ("1K88BFQG5_A0EH1R.mp4", 39.36, 1.20, +0.25, -0.08),
    ]
    bento_segs = [
        make_video_seg(
            fn, t0_b, 43.18, sin_b, spd=1.00, vol=0.0,
            base_scale=bento_sc, tx=ccx, ty=ccy, pop_in=True,
            mask_cfg=copy.deepcopy(BENTO_MASK)
        )
        for fn, t0_b, sin_b, ccx, ccy in bento_specs
    ]

    pip_excel = make_video_seg(
        "IMG_5408.MOV", 8.40, 11.00, 1.40, spd=1.00, vol=0.0,
        base_scale=0.31, tx=0.48, ty=0.42, slide_in_x=0.14, pop_in=True,
        mask_cfg=copy.deepcopy(PIP_MASK)
    )
    pip_handson = make_video_seg(
        "IMG_5397.MOV", 45.90, 47.55, 1.20, spd=1.00, vol=0.0,
        base_scale=0.31, tx=0.48, ty=0.42, slide_in_x=0.14, pop_in=True,
        mask_cfg=copy.deepcopy(PIP_MASK)
    )

    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid(); tr_v2["segments"] = [pip_excel, bento_segs[0], pip_handson]
    tr_v3 = copy.deepcopy(vtrack_tpl); tr_v3["id"] = uid(); tr_v3["segments"] = [bento_segs[1]]
    tr_v4 = copy.deepcopy(vtrack_tpl); tr_v4["id"] = uid(); tr_v4["segments"] = [bento_segs[2]]
    tr_v5 = copy.deepcopy(vtrack_tpl); tr_v5["id"] = uid(); tr_v5["segments"] = [bento_segs[3]]

    # ==========================================================================
    # TRACK 6 — NATIVE EDITABLE SUBTITLES (`check_flag = 15`)
    # ==========================================================================
    def make_native_subtitle(parts: list[tuple[str, bool]], t0_s: float, t1_s: float,
                             pos_x: float = -0.10, pos_y: float = -0.50, pop_in: bool = False):
        full_text = "".join(p[0] for p in parts)
        styles = []
        cur = 0
        for chunk, is_emph in parts:
            ln = len(chunk)
            if ln == 0:
                continue
            fcol = GOLD_COL  if is_emph else WHITE_COL
            scol = DARK_STROKE if is_emph else NAVY_STROKE
            sw   = 0.068     if is_emph else 0.062
            sz   = 11.2      if is_emph else 10.6
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
            "font_size": 10.6,
            "font_path": FONT_SUB_PATH,
            "font_resource_id": FONT_SUB_ID,
            "text_color": "#ffffff",
            "border_color": "#0b203c",
            "border_width": 0.062,
            "letter_spacing": 0.0,
            "line_spacing": 0.03,
            "alignment": 1,
            "line_feed": 1,
            "line_max_width": 0.68,
            "force_apply_line_max_width": True,
            "background_style": 0,
            "has_shadow": False,
            "is_rich_text": len(styles) > 1,
            "check_flag": 15,
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.35), us(t1_s) - st_u)
        kfs = []
        if pop_in:
            kfs = [
                make_kf("KFTypeScaleX", [(0.0, 0.92), (0.16, 1.02), (0.26, 1.00)]),
                make_kf("KFTypeScaleY", [(0.0, 0.92), (0.16, 1.02), (0.26, 1.00)]),
            ]

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tm_id,
            "target_timerange": {"start": st_u, "duration": du_u},
            "extra_material_refs": [],
            "common_keyframes": kfs, "keyframe_refs": [],
        })
        ts["clip"]["transform"] = {"x": round(pos_x, 4), "y": round(pos_y, 4)}
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["rotation"] = 0.0
        ts["clip"]["alpha"] = 1.0
        ts["uniform_scale"] = {"on": True, "value": 1.0}
        return ts

    PUNCH_SUBS = {2.12, 7.82, 15.52, 38.82, 55.02, 67.78, 75.60}
    SUB_ITEMS = [
        (2.12,  4.55, [("Riêng các bạn ", False), ("tự đi tìm hiểu,", True)]),
        (4.57,  5.85, [("tôi khẳng định với các bạn luôn:", False)]),
        (5.87,  7.58, [("mất khoảng ", False), ("2 năm mò mẫm", True), ("\nmới quay lại đi tìm!", False)]),
        (7.82, 10.45, [("Tổng tiền bao nhiêu,\ncủa ", False), ("đơn vị nào,", True)]),
        (10.47, 13.15,[("AI báo cáo lại ngay 1 file\n", False), ("Google Sheet • Excel", True)]),
        (13.17, 14.55,[("ngon lành luôn!", True)]),
        (14.60, 15.18,[("Hay không?!", True)]),

        (15.52, 18.25,[("Những khách sỉ mua hàng\n", False), ("trong vòng 1 tháng,", True)]),
        (18.27, 20.55,[("mình ", False), ("chưa kịp liên hệ lại", True)]),
        (20.57, 22.74,[("hệ thống cũ ", False), ("không tự báo nhắc", True), ("\nđể chăm sóc khách!", False)]),
        (23.05, 25.45,[("Thậm chí cả ", False), ("bộ phận Kế toán:", True)]),
        (25.47, 27.65,[("làm dữ liệu ", False), ("các tháng, các quý,", True)]),
        (27.67, 29.62,[("xong tổng hợp ", False), ("báo cáo cuối năm...", True)]),
        (29.68, 32.00,[("AI lấy hết thông tin\n", False), ("từ bộ não số ra ngay!", True)]),
        (32.06, 35.10,[("Riêng doanh nghiệp F20\nchú ý ", False), ("bộ phận Sản xuất:", True)]),
        (35.12, 38.75,[("cho anh em quay & chuẩn hóa\n", False), ("toàn bộ quy trình sản xuất!", True)]),

        (38.82, 41.12,[("Hiểu chưa? ", False), ("Cá nhân hóa", True), ("\ntừng nhân sự một!", False)]),
        (41.16, 43.18,[("Bộ não AI của tôi\nđang ", False), ("kết nối chằng chịt luôn!", True)]),
        (43.22, 45.74,[("Đóng gói toàn bộ kiến thức,\n", False), ("cấu hình bộ não riêng!", True)]),
        (45.80, 48.35,[("Não của Nhi, của Hiền,\n", False), ("của Hảo hay của Lan...", True)]),
        (48.37, 50.30,[("các bạn ", False), ("ghi tên mình vào!", True)]),
        (50.36, 52.85,[("Dự án hay bất kỳ dữ liệu nào\n", False), ("trong não đã có,", True)]),
        (52.87, 54.95,[("AI sẽ ", False), ("tự động xử lý", True), (" cho mình!", False)]),
        (55.02, 57.54,[("Cực kỳ quan trọng — kể cả\n", False), ("phòng Marketing", True), (" làm lại ngay:", False)]),
        (57.58, 59.14,[("Chuyển sang tab ", False), ("Claude Code!", True)]),

        (59.20, 62.22,[("Ghi âm để AI thấu hiểu\n", False), ("đúng ngữ điệu của mình!", True)]),
        (62.28, 65.05,[("Khi viết nội dung hay lên bài,\n", False), ("AI lấy đúng chất giọng", True)]),
        (65.07, 67.46,[("của chính doanh nghiệp mình!", False)]),
        (67.78, 71.65,[("“Cách chỉ giải pháp như vậy\n", False), ("rất đúng với trọng tâm!”", True)]),
        (71.68, 75.55,[("“Chứ chỉ nói lý thuyết suông thôi\nthì ", False), ("không làm được!”", True)]),

        (75.60, 78.08,[("Ở đây nhưng ", False), ("đội ngũ AI\nvẫn đang cày 24/7!", True)]),
        (78.12, 78.88,[("Các bạn hình dung không?!", True)]),
    ]

    tr_sub = copy.deepcopy(ttrack_tpl)
    tr_sub["id"] = uid()
    tr_sub["segments"] = [
        make_native_subtitle(
            parts, t0, t1,
            pos_x=-0.10,
            pos_y=-0.51 if (38.80 <= t0 <= 43.20) else -0.49,
            pop_in=(t0 in PUNCH_SUBS)
        )
        for t0, t1, parts in SUB_ITEMS
    ]

    # ==========================================================================
    # TRACKS 7..11 — NATIVE HEADLINE HOOK & FLOATING CALLOUT TAGS (`check_flag=15`)
    # ==========================================================================
    def make_native_callout(
        text: str, t0_s: float, t1_s: float, pos_x: float, pos_y: float,
        size: float = 11.4, fill_col=WHITE_COL, stroke_col=F20_GREEN_COL,
        stroke_w: float = 0.068, drift_up: bool = True
    ):
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
            "line_spacing": 0.03,
            "alignment": 1,
            "line_feed": 1,
            "line_max_width": 0.76,
            "force_apply_line_max_width": True,
            "background_style": 0,
            "has_shadow": False,
            "is_rich_text": False,
            "check_flag": 15,
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.45), us(t1_s) - st_u)
        dur_s = du_u / 1e6

        kfs = [
            make_kf("KFTypeScaleX", [(0.0, 0.88), (min(0.20, dur_s * 0.3), 1.03), (min(0.34, dur_s * 0.5), 1.00)]),
            make_kf("KFTypeScaleY", [(0.0, 0.88), (min(0.20, dur_s * 0.3), 1.03), (min(0.34, dur_s * 0.5), 1.00)]),
        ]
        if drift_up:
            kfs.append(make_kf("KFTypePositionY", [(0.0, pos_y - 0.022), (min(0.28, dur_s * 0.4), pos_y), (dur_s, pos_y + 0.015)]))

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tm_id,
            "target_timerange": {"start": st_u, "duration": du_u},
            "extra_material_refs": [],
            "common_keyframes": kfs, "keyframe_refs": [],
        })
        ts["clip"]["transform"] = {"x": round(pos_x, 4), "y": round(pos_y, 4)}
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["rotation"] = 0.0
        ts["clip"]["alpha"] = 1.0
        ts["uniform_scale"] = {"on": True, "value": 1.0}
        return ts

    CALLOUT_ITEMS = [
        (0.12,  2.08, "ĐÀO TẠO AI THỰC CHIẾN",                   0.00, +0.56, 12.8, GOLD_COL,  DARK_STROKE,   True),
        (0.34,  2.08, "THỰC PHẨM F20 • CẦM TAY CHỈ VIỆC",        0.00, +0.43,  8.8, WHITE_COL, F20_GREEN_COL, False),

        (2.25,  5.60, "TỰ MÒ MẪM = MẤT 2 NĂM!",                 0.00, +0.56, 12.0, GOLD_COL,  DARK_STROKE,   True),
        (8.40, 12.90, "BÁO CÁO SHEET\n& EXCEL TỰ ĐỘNG",         -0.38, +0.48,  9.8, GOLD_COL,  DARK_STROKE,   True),

        (15.65, 19.80,"BÀI TOÁN CSKH\n& ĐƠN SỈ F20",             0.00, +0.55, 11.2, WHITE_COL, NAVY_STROKE,   True),
        (23.15, 27.50,"TỰ ĐỘNG HÓA\nKẾ TOÁN CUỐI NĂM",           0.00, +0.55, 11.2, GOLD_COL,  DARK_STROKE,   True),
        (32.20, 36.80,"CHUẨN HÓA QUY TRÌNH\nBỘ PHẬN SẢN XUẤT",   0.00, +0.55, 10.8, WHITE_COL, F20_GREEN_COL, True),

        (38.82, 43.15,"BỘ NÃO AI CÁ NHÂN HÓA F20",              -0.11, +0.64, 11.2, GOLD_COL,  DARK_STROKE,   False),
        (38.88, 43.15,"01 • LÃNH ĐẠO",                          -0.47, +0.19,  7.8, WHITE_COL, DARK_STROKE,   False),
        (39.06, 43.15,"02 • KÈM 1-1",                           +0.25, +0.19,  7.8, WHITE_COL, DARK_STROKE,   False),
        (39.24, 43.15,"03 • ĐỘI NGŨ",                           -0.47, -0.27,  7.8, WHITE_COL, DARK_STROKE,   False),
        (39.42, 43.15,"04 • NÃO SỐ AI",                         +0.25, -0.27,  7.8, WHITE_COL, DARK_STROKE,   False),

        (55.05, 59.10,"MARKETING × CLAUDE CODE",                 0.00, +0.56, 11.4, GOLD_COL,  DARK_STROKE,   True),

        (59.30, 64.20,"AI HỌC ĐÚNG\nNGỮ ĐIỆU RIÊNG",             0.00, +0.55, 11.2, WHITE_COL, F20_GREEN_COL, True),
        (67.90, 73.50,"ĐÚNG TRỌNG TÂM\nLÀM ĐƯỢC NGAY!",          0.00, +0.55, 11.4, GOLD_COL,  DARK_STROKE,   True),

        (75.65, 78.85,"ĐỘI NGŨ AI VẬN HÀNH 24/7",                0.00, +0.56, 11.6, GOLD_COL,  DARK_STROKE,   True),
        (79.00, 82.40,"CÔNG TY TNHH THỰC PHẨM F20",             -0.13, -0.35, 11.2, GOLD_COL,  DARK_STROKE,   True),
        (79.25, 82.40,"TIÊN PHONG CHUYỂN ĐỔI SỐ AI\nthucphamf20.com • 0706.001.626", -0.13, -0.49, 8.4, WHITE_COL, F20_GREEN_COL, False),
    ]

    callout_lanes: list[list[dict]] = []
    for t0, t1, txt, px, py, sz, fc, sc, dup in sorted(CALLOUT_ITEMS, key=lambda x: x[0]):
        sg = make_native_callout(txt, t0, t1, px, py, size=sz, fill_col=fc, stroke_col=sc, drift_up=dup)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for lane in callout_lanes:
            if lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                lane.append(sg)
                placed = True
                break
        if not placed:
            callout_lanes.append([sg])

    callout_tracks = []
    for lane in callout_lanes:
        tr_c = copy.deepcopy(ttrack_tpl)
        tr_c["id"] = uid()
        tr_c["segments"] = lane
        callout_tracks.append(tr_c)

    # ==========================================================================
    # AUDIO TRACKS — 3-STAGE DUCKED BGM (Zero Audio Keyframes!) + MICRO-SFX
    # ==========================================================================
    def add_audio_material(audio_path: Path, name_lbl: str, mtype: str = "sound"):
        if not audio_path.is_file():
            raise FileNotFoundError(f"Missing audio asset: {audio_path}")
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

    bgm_id, bgm_full_u = add_audio_material(BGM_PATH, "Corporate Background02 - F20 AI Training", mtype="music")
    u_intro_end = us(2.10)
    u_voice_end = us(78.90)
    bgm_segs = [
        # Intro Hook (0.00 - 2.10s): energetic 0.48
        make_audio_slice(bgm_id, 0,           0,           u_intro_end,               0.48, 300000, 180000),
        # Main Voice Pocket (2.10 - 78.90s): smooth ducked 0.22
        make_audio_slice(bgm_id, u_intro_end, u_intro_end, u_voice_end - u_intro_end, 0.22, 180000, 180000),
        # Outro Climax (78.90 - 82.50s): uplifting 0.54 w/ 1.3s fade-out!
        make_audio_slice(bgm_id, u_voice_end, u_voice_end, total_dur_u - u_voice_end, 0.54, 220000, 1300000),
    ]
    tr_bgm = copy.deepcopy(atrack_tpl)
    tr_bgm["id"] = uid()
    tr_bgm["segments"] = bgm_segs

    def make_sfx_seg(sfx_fn: str, lbl: str, t0_s: float, vol: float, max_dur_s: float):
        aid, du_full = add_audio_material(SFX_DIR / sfx_fn, lbl, mtype="sound")
        du = min(du_full, us(max_dur_s))
        return make_audio_slice(aid, 0, us(t0_s), du, vol, min(16000, du // 6), min(110000, du // 3))

    SFX_EVENTS = [
        (0.08,  "Whoosh - Title Swoosh (1s).mp3",                                              "Title Swoosh Intro",  0.12, 0.80),
        (0.70,  "Click & Máy Chữ - click (1s).mp3",                                            "Cut Tick 02",         0.09, 0.35),
        (1.40,  "Click & Máy Chữ - click (1s).mp3",                                            "Cut Tick 03",         0.09, 0.35),
        (2.15,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Hook Card Accent",    0.10, 0.65),
        (8.35,  "Whoosh - Title Swoosh (1s).mp3",                                              "PIP Excel Swoosh",    0.10, 0.70),
        (14.58, "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Hay Không",      0.10, 1.20),
        (23.10, "Whoosh - Title Swoosh (1s).mp3",                                              "Swoosh Kế Toán",      0.09, 0.65),
        (32.15, "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Card Sản Xuất",       0.10, 0.65),
        (38.78, "Whoosh - Title Swoosh (1s).mp3",                                              "Bento Reveal Air",    0.11, 0.75),
        (39.00, "Click & Máy Chữ - click (1s).mp3",                                            "Bento Cell 2",        0.10, 0.35),
        (39.18, "Click & Máy Chữ - click (1s).mp3",                                            "Bento Cell 3",        0.10, 0.35),
        (39.36, "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bento Cell 4 Bell",   0.09, 1.10),
        (55.00, "Whoosh - Title Swoosh (1s).mp3",                                              "Swoosh Claude Code",  0.10, 0.70),
        (67.85, "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Card Đúng Trọng Tâm", 0.10, 0.65),
        (78.95, "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Outro Brand Chime",   0.11, 1.50),
    ]

    sfx_lanes: list[list[dict]] = []
    for t0, fn, lbl, vol, mdur in sorted(SFX_EVENTS, key=lambda x: x[0]):
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
        tr_s = copy.deepcopy(atrack_tpl)
        tr_s["id"] = uid()
        tr_s["segments"] = lane
        sfx_tracks.append(tr_s)

    D["tracks"] = [
        tr_v0,
        tr_v1,
        tr_v2,
        tr_v3,
        tr_v4,
        tr_v5,
        tr_sub,
        *callout_tracks,
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

    # ==========================================================================
    # WRITE CLEAN CAPCUT v193.0.0 PROJECT FOLDER (ZERO STALE `draft.extra`!)
    # ==========================================================================
    out_dir = DRAFTS_ROOT / DRAFT_NAME
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy ONLY clean auxiliary files/folders (NEVER copy `draft.extra` or `.bak` or `template.tmp` from 1126!)
    for aux_fn in ("draft_agency_config.json", "draft_biz_config.json", "attachment_pc_common.json", "key_value.json", "performance_opt_info.json", "draft_settings"):
        if (TPL_1126_DIR / aux_fn).exists():
            shutil.copy2(TPL_1126_DIR / aux_fn, out_dir / aux_fn)
    for aux_dir in ("common_attachment", "Resources"):
        if (TPL_1126_DIR / aux_dir).exists():
            shutil.copytree(TPL_1126_DIR / aux_dir, out_dir / aux_dir)

    # Write clean `draft_virtual_store.json` (zero stale 1126 material IDs!)
    dvs = {
        "draft_materials": [],
        "draft_virtual_store": [
            {"type": 0, "value": [{"creation_time": 0, "display_name": "", "filter_type": 0, "id": "", "import_time": 0, "import_time_us": 0, "material_color_tag": "", "sort_sub_type": 0, "sort_type": 0, "subdraft_filter_type": 0}]},
            {"type": 1, "value": [{"child_id": e["id"], "parent_id": ""} for e in dm_entries]}
        ]
    }
    (out_dir / "draft_virtual_store.json").write_text(json.dumps(dvs, ensure_ascii=False), encoding="utf-8")

    # Write synchronized `timeline_layout.json` pointing to `main_tl_id`!
    tl_layout = {
        "dockItems": [{"dockIndex": 0, "ratio": 1, "timelineIds": [main_tl_id], "timelineNames": ["Dòng thời gian 01"]}],
        "layoutOrientation": 1
    }
    (out_dir / "timeline_layout.json").write_text(json.dumps(tl_layout, ensure_ascii=False), encoding="utf-8")

    # Generate crisp draft_cover.jpg
    cover_jpg = out_dir / "draft_cover.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "3.0", "-i", str(RAW_DIR / "IMG_5380.MOV"),
        "-frames:v", "1", "-vf", "scale=540:960", "-q:v", "3", str(cover_jpg)
    ], check=False)

    # Create complete sub-timeline folder `Timelines/<main_tl_id>/` matching HT-AV & SG!
    tl_root = out_dir / "Timelines"
    new_tl_dir = tl_root / main_tl_id
    new_tl_dir.mkdir(parents=True, exist_ok=True)
    if (out_dir / "attachment_pc_common.json").exists():
        shutil.copy2(out_dir / "attachment_pc_common.json", new_tl_dir / "attachment_pc_common.json")
    if (out_dir / "common_attachment").exists():
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
        tp.write_bytes(dc_bytes)

    # Write synchronized `Timelines/project.json` (matching HT-AV config!)
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

    # Write clean `draft_meta_info.json` (CRITICAL: draft_cover = "draft_cover.jpg"!)
    dmi = copy.deepcopy(dmi_1126)
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

    # Update `root_meta_info.json`
    rmi_path = APPDATA_ROOT / "root_meta_info.json"
    if rmi_path.exists():
        rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
        store = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_NAME]
        entry = copy.deepcopy(store[0]) if store else {}
        total_bytes = sum((RAW_DIR / fn).stat().st_size for fn in {Path(p).name for p in vmat_map})
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

    print(f"FIXED & VERIFIED CapCut v193.0.0 Project: {out_dir}")
    print(f"  draft_id == {draft_uuid} | main_tl_id == {main_tl_id} (100% synced across D['id'], project.json, timeline_layout.json)")
    print(f"  draft.extra removed : {not (out_dir / 'draft.extra').exists()}")

if __name__ == "__main__":
    main()
