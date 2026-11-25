import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path

ROOT      = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_DIR = ROOT / "1117 F20"
HTPM_DIR  = ROOT / "HTPM"
F20_261116 = Path(r"Z:\Máy tính khác\My Computer\F20\video gốc\261116")
DOC_DIR   = F20_261116 / r"Chi Oanh\dọc"
DJI_DIR   = F20_261116 / r"Chi Oanh\dji"
SFX_FOLDER = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")
CC_MUSIC  = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\music")
WORK      = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")

def uid(): return str(uuid.uuid4()).upper()
def us(sec): return int(round(float(sec) * 30.0) * 1_000_000 // 30)
def norm_fwd(p): return os.path.normpath(str(p)).replace("\\", "/")

# 0. Safety check & full backup of 1117 F20 before touching anything!
if not DRAFT_DIR.exists():
    raise FileNotFoundError(f"Cannot find CapCut project folder: {DRAFT_DIR}")
if (DRAFT_DIR / ".locked").exists():
    raise RuntimeError("1117 F20 currently has .locked! Ask user to exit to CapCut Home Screen first.")

bak = WORK / "backup_1117_F20_orig"
if not bak.exists():
    bak.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DRAFT_DIR / "draft_content.json", bak / "draft_content.json")
    shutil.copy2(DRAFT_DIR / "draft_meta_info.json", bak / "draft_meta_info.json")
    shutil.copytree(DRAFT_DIR / "Timelines", bak / "Timelines")
    print("Created complete backup of 1117 F20 in backup_1117_F20_orig!")

pj = json.loads((DRAFT_DIR / "Timelines" / "project.json").read_text(encoding="utf-8"))
tl_id = pj["main_timeline_id"]
tl_dc_path = DRAFT_DIR / "Timelines" / tl_id / "draft_content.json"

# Load from clean original backup so script is 100% idempotent if re-run!
D = json.loads((bak / "Timelines" / tl_id / "draft_content.json").read_text(encoding="utf-8"))
dc_htpm = json.loads((HTPM_DIR / "draft_content.json").read_text(encoding="utf-8"))
dm_htpm = json.loads((HTPM_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))

# Templates
vtrack_tpl = copy.deepcopy(D["tracks"][0])
vseg_tpl   = copy.deepcopy(D["tracks"][0]["segments"][0])
vmat_tpl   = copy.deepcopy(dc_htpm["materials"]["videos"][0])
dm_mat_tpl = copy.deepcopy(dm_htpm["draft_materials"][0]["value"][0])

ttrack_tpl = copy.deepcopy(D["tracks"][1])
tseg_tpl   = copy.deepcopy(D["tracks"][1]["segments"][36])
tmat_coiny = copy.deepcopy(next(x for x in D["materials"]["texts"] if x["id"] == D["tracks"][1]["segments"][0]["material_id"]))

atrack_tpl = copy.deepcopy(D["tracks"][5])
aseg_tpl   = copy.deepcopy(D["tracks"][5]["segments"][0])
amat_tpl   = copy.deepcopy(next(x for x in D["materials"]["audios"] if x["id"] == aseg_tpl["material_id"]))

v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
v_extra_tpl  = {
    k: copy.deepcopy(next(x for x in D["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"]))
    for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in D["materials"].get(k, []))
}
a_extra_keys = ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")
a_extra_tpl  = {
    k: copy.deepcopy(next(x for x in D["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"]))
    for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in D["materials"].get(k, []))
}

# Verified Animations
TEXT_ANIMS  = json.loads((WORK / "verified_text_anims.json").read_text(encoding="utf-8"))
VIDEO_ANIMS = json.loads((WORK / "verified_video_anims.json").read_text(encoding="utf-8"))

# Verified Rectangle Mask (for sleek rounded-corner PIP overlays!)
RECT_MASK_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef"
HAS_RECT_MASK  = Path(RECT_MASK_PATH).exists()

# Keep ONLY materials actually referenced by Track 0 (Main Video) and Track 6 (Main BGM), clearing old drifted texts/SFX cleanly!
track0_orig = copy.deepcopy(D["tracks"][0])
bgm_track_orig = copy.deepcopy(D["tracks"][6])
main_end_u = max(s["target_timerange"]["start"] + s["target_timerange"]["duration"] for s in track0_orig["segments"]) # 148,633,333 us

# Trim BGM track cleanly to main_end_u + smooth 1.5s fade-out so timeline doesn't hang 40s in black silence!
bgm_seg = bgm_track_orig["segments"][0]
bgm_seg["target_timerange"]["duration"] = main_end_u
bgm_seg["source_timerange"]["duration"] = main_end_u
bgm_seg["volume"] = 0.22
bgm_seg["last_nonzero_volume"] = 0.22
fade_bgm_id = uid()
D["materials"].setdefault("audio_fades", []).append({
    "fade_in_duration": 500000,
    "fade_out_duration": 1500000,
    "fade_type": 0,
    "id": fade_bgm_id,
    "type": "audio_fade"
})
bgm_seg["extra_material_refs"].append(fade_bgm_id)

used_ids = set()
for tr_keep in (track0_orig, bgm_track_orig):
    for s in tr_keep["segments"]:
        used_ids.add(s["material_id"])
        used_ids.update(s.get("extra_material_refs", []))

for k, val in list(D["materials"].items()):
    if isinstance(val, list):
        D["materials"][k] = [x for x in val if isinstance(x, dict) and x.get("id") in used_ids]

# Ensure Coiny font is registered in materials["fonts"]
COINY_ID   = "7482665772876156165"
COINY_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7482665772876156165/57619fa23667c87dee08a75d49a8b51a/font.ttf"
COINY_FONT_OBJ = {
    "category_id": "user", "category_name": "Recently used", "effect_id": COINY_ID,
    "file_uri": "", "id": uid(), "path": COINY_PATH,
    "request_id": "202611181407180000000000006295570", "resource_id": COINY_ID,
    "source_platform": 1, "team_id": "", "third_resource_id": "", "title": "Coiny"
}
if "fonts" in D["materials"]:
    D["materials"]["fonts"].append(COINY_FONT_OBJ)

# ==============================================================================
# HELPER 1: PROBE & ADD REAL F20 VIDEO OVERLAYS + IN/OUT ANIMATIONS + MICRO-ZOOM
# ==============================================================================
MEDIA_PROBE_CACHE = {}
def probe_media(path: Path):
    sp = str(path)
    if sp not in MEDIA_PROBE_CACHE:
        r = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type,width,height:stream_side_data=rotation:format=duration",
            "-of", "json", sp
        ], capture_output=True, text=True, check=True)
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
        MEDIA_PROBE_CACHE[sp] = (w, h, dur, has_aud)
    return MEDIA_PROBE_CACHE[sp]

VMAT_MAP = {}
NEW_DM_ENTRIES = []
now_s = int(time.time())

def get_or_add_video_mat(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing F20 source: {path}")
    fwd = norm_fwd(path)
    if fwd in VMAT_MAP:
        return VMAT_MAP[fwd]
    w, h, dur_s, has_aud = probe_media(path)
    dur_u = us(dur_s)
    mid = uid()
    lmid = str(uuid.uuid4())
    m = copy.deepcopy(vmat_tpl)
    m.update({
        "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
        "type": "video", "path": fwd, "media_path": "", "local_id": "",
        "material_name": path.name, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud)
    })
    D["materials"]["videos"].append(m)

    dme = copy.deepcopy(dm_mat_tpl)
    dme.update({
        "id": lmid, "file_Path": fwd, "extra_info": path.name,
        "duration": dur_u, "width": w, "height": h,
        "metetype": "video", "item_source": 1,
        "import_time": now_s, "import_time_ms": now_s * 1000,
        "roughcut_time_range": {"start": 0, "duration": dur_u},
        "sub_time_range": {"start": -1, "duration": -1},
    })
    NEW_DM_ENTRIES.append(dme)
    VMAT_MAP[fwd] = (mid, dur_u, w, h)
    return mid, dur_u, w, h

def make_kf_linear(prop_type: str, dur_u: int, v0: float, v1: float):
    return {
        "id": uid(),
        "material_id": "",
        "property_type": prop_type,
        "keyframe_list": [
            {"curveType": "Line", "graphID": "", "id": uid(), "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "time_offset": 0, "values": [v0]},
            {"curveType": "Line", "graphID": "", "id": uid(), "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "time_offset": dur_u, "values": [v1]},
        ]
    }

def make_video_overlay_seg(src_path: Path, t0_s: float, t1_s: float, src_in_s: float, spd: float = 1.0,
                           mode: str = "full", in_anim: str = "Rõ dần", zoom_dir: int = 1,
                           base_scale: float = 1.0, tx: float = 0.0, ty: float = 0.0):
    mid, mat_dur_u, w, h = get_or_add_video_mat(src_path)
    tgt_st_u = us(t0_s)
    tgt_du_u = max(us(0.20), us(t1_s) - tgt_st_u)
    src_st_u = us(src_in_s)
    src_du_u = us((t1_s - t0_s) * spd)
    if src_st_u + src_du_u > mat_dur_u:
        src_st_u = max(0, mat_dur_u - src_du_u)

    seg = copy.deepcopy(vseg_tpl)
    refs = []
    for k, tpl_e in v_extra_tpl.items():
        em = copy.deepcopy(tpl_e); em["id"] = uid()
        if k == "speeds":
            em["speed"] = round(spd, 3)
        D["materials"][k].append(em)
        refs.append(em["id"])

    # Attach smooth CapCut Video In + Out animations!
    anim_list = []
    if in_anim in VIDEO_ANIMS["in"]:
        ai = copy.deepcopy(VIDEO_ANIMS["in"][in_anim])
        ai["start"] = 0
        ai["duration"] = min(266666 if mode == "full" else 366666, tgt_du_u // 3)
        anim_list.append(ai)
    if "Mờ dần" in VIDEO_ANIMS["out"]:
        ao = copy.deepcopy(VIDEO_ANIMS["out"]["Mờ dần"])
        out_d = min(233333, tgt_du_u // 3)
        ao["duration"] = out_d
        ao["start"] = max(0, tgt_du_u - out_d)
        anim_list.append(ao)
    if anim_list:
        ma_id = uid()
        D["materials"].setdefault("material_animations", []).append({
            "animations": anim_list, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
        })
        refs.append(ma_id)

    kfs = []
    if mode == "full":
        seg["clip"]["scale"] = {"x": base_scale, "y": base_scale}
        seg["clip"]["transform"] = {"x": tx, "y": ty}
        seg["uniform_scale"] = {"on": True, "value": base_scale}
        if zoom_dir != 0 and tgt_du_u >= 1800000:
            s0, s1 = (base_scale, round(base_scale * 1.04, 4)) if zoom_dir > 0 else (round(base_scale * 1.04, 4), base_scale)
            kfs = [make_kf_linear("KFTypeScaleX", tgt_du_u, s0, s1), make_kf_linear("KFTypeScaleY", tgt_du_u, s0, s1)]
    elif mode in ("pip_tl", "pip_tr"):
        # Clean rounded-corner PIP card in upper-right / upper-left safe margin so Chị Oanh's face is NEVER covered!
        px = -0.48 if mode == "pip_tl" else 0.48
        py = 0.44
        sc = 0.34
        seg["clip"]["scale"] = {"x": sc, "y": sc}
        seg["clip"]["transform"] = {"x": px, "y": py}
        seg["uniform_scale"] = {"on": True, "value": sc}
        if HAS_RECT_MASK:
            mk_id = uid()
            D["materials"].setdefault("common_mask", []).append({
                "config": {"aspectRatio": 0.78, "centerX": 0.0, "centerY": 0.0, "expansion": 0.0, "feather": 0.02, "height": 0.86, "invert": False, "rotation": 0.0, "roundCorner": 0.18, "width": 0.88},
                "id": mk_id, "name": "Hình chữ nhật", "path": RECT_MASK_PATH,
                "platform": "all", "position_info": "", "resource_id": "7374021450748924432",
                "resource_type": "rectangle", "source_platform": 1, "type": "mask"
            })
            refs.append(mk_id)

    seg.update({
        "id": uid(), "material_id": mid,
        "source_timerange": {"start": src_st_u, "duration": src_du_u},
        "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
        "speed": round(spd, 3), "volume": 0.0, "last_nonzero_volume": 1.0,
        "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [],
    })
    seg["clip"]["alpha"] = 1.0
    return seg

# ==============================================================================
# HELPER 2: COINY RED-WITH-WHITE-STROKE SUBTITLES + KEYWORD EMPHASIS + IN/OUT ANIMS
# ==============================================================================
RED_REG  = [0.9254902, 0.1137255, 0.1137255]  # #EC1D1D (Exact user Coiny red!)
RED_DEEP = [0.8352941, 0.0392157, 0.0784314]  # #D50A14 (Rich deep emphasis crimson!)
WHITE    = [1.0, 1.0, 1.0]

def make_coiny_text_seg(parts: list[tuple[str, bool]], t0_s: float, t1_s: float,
                        pos_x: float = 0.0, pos_y: float = -0.60,
                        base_size: float = 10.2, emph_size: float = 13.2,
                        in_anim_name: str = "Chữ mờ dần hiện vào", out_anim_name: str = "Mờ dần",
                        pop_kf: bool = False):
    """parts = [(text_chunk, is_emphasized), ...]"""
    full_text = "".join(p[0] for p in parts)
    styles = []
    cur = 0
    for chunk, is_emph in parts:
        ln = len(chunk)
        if ln == 0:
            continue
        sz = emph_size if is_emph else base_size
        col = RED_DEEP if is_emph else RED_REG
        sw  = 0.095 if is_emph else 0.078
        styles.append({
            "fill": {"content": {"render_type": "solid", "solid": {"color": col}}},
            "font": {"id": COINY_ID, "path": COINY_PATH},
            "strokes": [{"content": {"render_type": "solid", "solid": {"color": WHITE}}, "width": sw, "mode": 0}],
            "shadows": [{
                "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
                "alpha": 0.52, "angle": -45.0, "diffuse": 0.42, "distance": 4.0, "feather": 0.45
            }],
            "size": sz,
            "useLetterColor": True,
            "range": [cur, cur + ln],
        })
        cur += ln

    tm = copy.deepcopy(tmat_coiny)
    tm_id = uid()
    f_copy = copy.deepcopy(COINY_FONT_OBJ); f_copy["id"] = uid()
    tm.update({
        "id": tm_id,
        "type": "subtitle",
        "recognize_text": full_text,
        "translate_original_text": full_text,
        "content": json.dumps({"text": full_text, "styles": styles}, ensure_ascii=False),
        "base_content": json.dumps({
            "text": full_text,
            "styles": [{
                "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": RED_REG}}},
                "font": {"id": COINY_ID, "path": COINY_PATH},
                "range": [0, len(full_text)],
                "size": base_size,
            }]
        }, ensure_ascii=False),
        "font_size": base_size,
        "font_path": COINY_PATH,
        "font_resource_id": COINY_ID,
        "fonts": [f_copy],
        "text_color": "#ec1d1d",
        "border_color": "#ffffff",
        "border_width": 0.08,
        "has_shadow": True,
        "shadow_color": "#000000",
        "shadow_alpha": 0.52,
        "shadow_smoothing": 0.45,
        "shadow_distance": 4.0,
        "alignment": 1,
        "line_feed": 1,
        "line_spacing": 0.04,
        "line_max_width": 0.78,
        "force_apply_line_max_width": True,
        "is_rich_text": len(styles) > 1,
        "check_flag": 31,
    })
    D["materials"]["texts"].append(tm)

    tgt_st_u = us(t0_s)
    tgt_du_u = max(us(0.35), us(t1_s) - tgt_st_u)

    # Build Text IN + OUT animation!
    anim_items = []
    if in_anim_name in TEXT_ANIMS["in"]:
        ai = copy.deepcopy(TEXT_ANIMS["in"][in_anim_name])
        ai["start"] = 0
        ai["duration"] = min(266666, tgt_du_u // 3)
        anim_items.append(ai)
    if out_anim_name in TEXT_ANIMS["out"]:
        ao = copy.deepcopy(TEXT_ANIMS["out"][out_anim_name])
        od = min(166666, tgt_du_u // 4)
        ao["duration"] = od
        ao["start"] = max(0, tgt_du_u - od)
        anim_items.append(ao)

    refs = []
    if anim_items:
        ma_id = uid()
        D["materials"].setdefault("material_animations", []).append({
            "animations": anim_items, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
        })
        refs.append(ma_id)

    kfs = []
    if pop_kf and tgt_du_u >= 500000:
        # Subtle punchy pop keyframe (0.92 -> 1.07 at 180ms -> 1.00 at 340ms) for hero emphasized phrases!
        for prop in ("KFTypeScaleX", "KFTypeScaleY"):
            kfs.append({
                "id": uid(), "material_id": "", "property_type": prop,
                "keyframe_list": [
                    {"curveType": "Line", "graphID": "", "id": uid(), "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "time_offset": 0, "values": [0.92]},
                    {"curveType": "Line", "graphID": "", "id": uid(), "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "time_offset": 166666, "values": [1.07]},
                    {"curveType": "Line", "graphID": "", "id": uid(), "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "time_offset": 333333, "values": [1.00]},
                ]
            })

    ts = copy.deepcopy(tseg_tpl)
    ts.update({
        "id": uid(), "material_id": tm_id,
        "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
        "extra_material_refs": refs,
        "common_keyframes": kfs, "keyframe_refs": [],
    })
    ts["clip"]["transform"] = {"x": pos_x, "y": pos_y}
    ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
    ts["uniform_scale"] = {"on": True, "value": 1.0}
    return ts

# ==============================================================================
# HELPER 3: TACTILE MICRO-SFX SEGMENTS
# ==============================================================================
AMAT_MAP = {}
def make_sfx_seg(sfx_path: Path, name: str, t0_s: float, vol: float = 0.34, max_dur_s: float = 1.1):
    fwd = norm_fwd(sfx_path)
    if fwd not in AMAT_MAP:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(sfx_path)], capture_output=True, text=True, check=True)
        d_s = float(json.loads(r.stdout)["format"]["duration"])
        d_u = us(d_s)
        aid = uid()
        am = copy.deepcopy(amat_tpl)
        am.update({
            "id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
            "name": name, "path": fwd, "duration": d_u, "type": "sound"
        })
        D["materials"]["audios"].append(am)
        AMAT_MAP[fwd] = (aid, d_u)
    aid, d_u = AMAT_MAP[fwd]
    du = min(d_u, us(max_dur_s))
    sg = copy.deepcopy(aseg_tpl)
    refs = []
    for k, tpl_e in a_extra_tpl.items():
        em = copy.deepcopy(tpl_e); em["id"] = uid()
        if k == "speeds": em["speed"] = 1.0
        D["materials"][k].append(em); refs.append(em["id"])
    sg.update({
        "id": uid(), "material_id": aid,
        "source_timerange": {"start": 0, "duration": du},
        "target_timerange": {"start": us(t0_s), "duration": du},
        "speed": 1.0, "volume": vol, "last_nonzero_volume": vol,
        "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []
    })
    return sg

# ==============================================================================
# 1. BUILD CURATED REAL F20 OVERLAY TRACKS (Matched 100% to Spoken Dialogue!)
# ==============================================================================
FULL_OVERLAYS = [
    # (src_path, t0_s, t1_s, src_in_s, spd, in_anim, zoom_dir, base_scale, tx, ty)
    # Intro dynamic 2-shot supplement (1.26 - 3.77s)
    (DOC_DIR / "C3909.MP4", 1.26,  2.52,  0.80, 1.00, "Rõ dần",  +1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3875.MP4", 2.52,  3.77,  0.80, 1.00, "Rõ dần",  -1, 1.00,  0.00, 0.00),

    # Nha Trang: 2 khách hàng -> Anh Hậu Đăng Khoa Edu 77 set -> Hội phụ huynh 13 set -> Hà Nội 10 set -> TP.HCM 4 set -> Tổng 104 set!
    (DOC_DIR / "C3910.MP4", 14.00, 16.35, 0.80, 1.00, "Rõ dần",  +1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3921.MP4", 16.35, 18.20, 0.80, 1.00, "Rõ dần",  -1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3932.MP4", 18.20, 20.00, 0.80, 1.00, "Rõ dần",  +1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3866.MP4", 20.20, 23.90, 3.00, 1.00, "Rõ dần",  -1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3892.MP4", 24.67, 27.85, 0.60, 1.00, "Rõ dần",  +1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3901.MP4", 27.90, 31.68, 0.50, 1.00, "Rõ dần",  -1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3875.MP4", 31.70, 34.20, 0.60, 1.00, "Rõ dần",  +1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3869.MP4", 34.20, 36.60, 1.50, 1.00, "Rõ dần",  -1, 1.00,  0.00, 0.00),

    # Secondary 3K vertical angle showing long row of prepared sets (41.60 - 44.85s)
    (DJI_DIR / "DJI_20261116110956_0104_D.MP4", 41.60, 44.85, 1.40, 1.00, "Rõ dần", +1, 1.00, 0.00, 0.00),

    # Multi-cam synced 3K Camera B centered on gift set as Chị Oanh introduces 1 set quà (46.80 - 50.80s, corr=0.736!)
    (DJI_DIR / "DJI_20261116093228_0082_D.MP4", 46.80, 50.80, 2.77, 1.05, "Rõ dần",  0, 1.22, -0.18, 0.00),

    # Detailed 4-Item Gift Set Walkthrough (52.20 - 85.40s):
    # - Inside gift basket macro glide (52.20 - 56.25s)
    (DOC_DIR / "C3873.MP4", 52.20, 56.25, 0.25, 0.74, "Rõ dần",  +1, 1.00,  0.00, 0.00),
    # - 1 Set Yến Sào + 1 Tổ Yến Sào Tinh Chế Sợi Dài (56.25 - 61.05s, 3K DJI 0083 centered on Bird's Nest box!)
    (DOC_DIR / "C3867.MP4", 56.25, 58.55, 0.60, 1.00, "Rõ dần",  -1, 1.00,  0.00, 0.00),
    (DJI_DIR / "DJI_20261116093255_0083_D.MP4", 58.55, 61.05, 6.80, 1.00, "Rõ dần",  0, 1.22, -0.18, 0.00),
    # - Nguyên liệu chưng: Táo đỏ, Đông trùng hạ thảo, Kỷ tử, Đường phèn (61.10 - 66.65s, strictly macro inside basket!)
    (DOC_DIR / "C3874.MP4", 61.10, 63.18, 0.25, 0.90, "Rõ dần",  +1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3873.MP4", 63.18, 66.65, 0.20, 0.76, "Rõ dần",  -1, 1.04,  0.00, 0.00),
    # - Thứ 2: 2 hộp Rong biển sấy giòn cay nhẹ & sấy mè không cay (66.70 - 74.45s, Multi-cam Camera B centered!)
    (DJI_DIR / "DJI_20261116093322_0084_D.MP4", 66.70, 70.60, 32.36, 1.05, "Rõ dần", 0, 1.22, -0.18, 0.00),
    (DJI_DIR / "DJI_20261116094254_0089_D.MP4", 70.60, 74.45, 0.70, 1.00, "Rõ dần", +1, 1.00,  0.00, 0.00),
    # - Thứ 3: 1 gói Bánh thuyền mix hạt dinh dưỡng 250g (74.80 - 79.95s, Multi-cam Camera B centered!)
    (DJI_DIR / "DJI_20261116093322_0084_D.MP4", 74.80, 79.95, 41.20, 1.05, "Rõ dần", 0, 1.22, -0.18, 0.00),
    # - Thứ 4: 1 gói Rong biển kẹp hạt 500g (80.25 - 85.40s, Multi-cam Camera B centered! Leaves 85.40-89.67s on Camera A!)
    (DJI_DIR / "DJI_20261116093322_0084_D.MP4", 80.25, 85.40, 47.24, 1.05, "Rõ dần", 0, 1.22, -0.18, 0.00),

    # Giá trị nhất là Set 1 Tổ Yến Sào Tinh Chế Sợi Dài (89.70 - 95.85s)
    (DJI_DIR / "DJI_20261116093322_0084_D.MP4", 89.70, 92.80, 14.20, 1.00, "Rõ dần", +1, 1.22, -0.18, 0.00),
    (DOC_DIR / "C3875.MP4", 92.80, 95.85, 3.20, 1.00, "Rõ dần",  -1, 1.00,  0.00, 0.00),

    # Tờ cẩm nang công dụng & hướng dẫn chưng yến (98.20 - 106.80s, Multi-cam Camera B macro synced corr=0.835!)
    (DJI_DIR / "DJI_20261116093955_0088_D.MP4", 98.20, 106.80, 12.62, 1.05, "Rõ dần", 0, 1.00,  0.00, 0.00),

    # Giỏ đựng quà chất liệu mica trong suốt (107.80 - 114.05s: C3908 + DJI 0085 @ 7.40s Chị Oanh centered holding clear mica bag!)
    (DOC_DIR / "C3908.MP4", 107.80, 111.00, 1.60, 1.00, "Rõ dần", +1, 1.00,  0.00, 0.00),
    (DJI_DIR / "DJI_20261116093624_0085_D.MP4", 111.00, 114.08, 7.40, 1.00, "Rõ dần", 0, 1.00,  0.00, 0.00),

    # Quai xách bằng da màu đỏ đô (116.00 - 119.10s: centered close-up of burgundy leather handle!)
    (DJI_DIR / "DJI_20261116093624_0085_D.MP4", 116.00, 119.10, 17.20, 1.00, "Rõ dần", 0, 1.00, 0.00, 0.00),

    # Thiết kế thêm bông hoa điểm nhấn & nơ màu be xinh xắn (119.55 - 126.20s: centered basket+flower & centered beige bow!)
    (DJI_DIR / "DJI_20261116093624_0085_D.MP4", 119.55, 122.90, 12.20, 1.00, "Rõ dần", +1, 1.00, 0.00, 0.00),
    (DJI_DIR / "DJI_20261116093624_0085_D.MP4", 122.90, 126.20, 20.65, 1.00, "Rõ dần",  0, 1.00, 0.00, 0.00),

    # Trực tiếp sản xuất — yên tâm chất lượng & giá cả (128.00 - 135.40s)
    (DOC_DIR / "C3882.MP4", 128.00, 131.80, 0.60, 1.00, "Rõ dần", +1, 1.00,  0.00, 0.00),
    (DOC_DIR / "C3870.MP4", 131.80, 135.40, 1.20, 1.00, "Rõ dần", -1, 1.00,  0.00, 0.00),

    # Đặt set quà lễ 20/11 (143.50 - 146.95s, then back to Chị Oanh smiling "inbox ngay cho Oanh nhé!")
    (DOC_DIR / "C3865.MP4", 143.50, 146.95, 1.50, 1.00, "Rõ dần", +1, 1.00,  0.00, 0.00),
]

# Floating Rounded PIP Overlays on Track 2 (Upper-right safe margin `pip_tr` — NEVER covers Chị Oanh's face!)
PIP_OVERLAYS = [
    # 6.35 - 9.40s: Gift basket PIP while Chị Oanh says "104 SET QUÀ cho các khách hàng đặt"
    (DOC_DIR / "C3908.MP4", 6.35,  9.40,  0.50, 1.00, "pip_tr", "Trượt sang trái"),
    # 38.60 - 41.50s: Gleaming gift sets PIP while Chị Oanh says "Đây là những SET QUÀ bên Oanh đã chuẩn bị xong"
    (DOC_DIR / "C3875.MP4", 38.60, 41.50, 0.80, 1.00, "pip_tr", "Trượt sang trái"),
    # 136.20 - 140.40s: Happy customer handover PIP while Chị Oanh thanks F20 customers!
    (DOC_DIR / "C3921.MP4", 136.20, 140.40, 1.00, 1.00, "pip_tr", "Trượt sang trái"),
]

tr_ov_full = copy.deepcopy(vtrack_tpl); tr_ov_full["id"] = uid(); tr_ov_full["segments"] = []
for sp, t0, t1, sin, spd, ia, zd, bsc, tx, ty in FULL_OVERLAYS:
    tr_ov_full["segments"].append(make_video_overlay_seg(
        sp, t0, t1, sin, spd=spd, mode="full", in_anim=ia, zoom_dir=zd, base_scale=bsc, tx=tx, ty=ty
    ))

tr_ov_pip = copy.deepcopy(vtrack_tpl); tr_ov_pip["id"] = uid(); tr_ov_pip["segments"] = []
for sp, t0, t1, sin, spd, md, ia in PIP_OVERLAYS:
    tr_ov_pip["segments"].append(make_video_overlay_seg(sp, t0, t1, sin, spd=spd, mode=md, in_anim=ia, zoom_dir=0))


# ==============================================================================
# 2. BUILD 100% FRAME-SYNCED COINY RED-WITH-WHITE-STROKE SUBTITLES & CALLOUTS!
#    Balanced 2-line TikTok Safe-Zone layout — zero edge clipping!
# ==============================================================================
SUB_ITEMS = [
    (4.56,  6.38,  [("Hôm nay bên Oanh\nđang chuẩn bị", False)], "Chữ mờ dần hiện vào", False),
    (6.40,  7.96,  [("104 SET QUÀ", True)], "Xoay lấp lánh", True),
    (7.98,  9.44,  [("cho các khách hàng đặt", False)], "Chữ mờ dần hiện vào", False),
    (9.46,  11.48, [("làm ", False), ("QUÀ BIẾU TẶNG\n", True), ("thầy cô giáo", False)], "Trượt sang phải", True),
    (11.50, 13.65, [("nhân dịp tri ân\nngày ", False), ("20/11", True)], "Bước sang trái", True),

    (13.96, 15.58, [("Ở ", False), ("NHA TRANG\n", True), ("có 2 khách hàng", False)], "Chữ mờ dần hiện vào", False),
    (15.64, 17.56, [("1 là ", False), ("ANH HẬU\n", True), ("Trung tâm luyện thi", False)], "Trượt sang phải", True),
    (17.58, 19.85, [("ĐĂNG KHOA EDU\n", True), ("đặt ", False), ("77 SET QUÀ", True)], "Xoay lấp lánh", True),
    (20.18, 22.45, [("Khách thứ 2 là\n", False), ("HỘI PHỤ HUYNH", True)], "Chữ mờ dần hiện vào", False),
    (22.47, 23.90, [("đặt ", False), ("13 SET QUÀ", True)], "Bước sang trái", True),
    (24.00, 26.85, [("1 bạn giáo viên\nở ", False), ("HÀ NỘI", True)], "Trượt sang phải", False),
    (26.87, 27.85, [("đặt ", False), ("10 SET QUÀ", True)], "Bước sang trái", True),
    (27.92, 30.54, [("và 1 bạn ở\n", False), ("TP. HỒ CHÍ MINH", True)], "Trượt sang phải", False),
    (30.56, 31.68, [("đặt ", False), ("4 SET QUÀ", True)], "Bước sang trái", True),

    (31.70, 34.36, [("Tổng sáng nay bên mình\nchuẩn bị", False)], "Chữ mờ dần hiện vào", False),
    (34.38, 36.55, [("ĐỦ 104 SET QUÀ\n", True), ("nha mọi người!", False)], "Xoay lấp lánh", True),

    (38.60, 40.62, [("Đây là những ", False), ("SET QUÀ\n", True), ("bên Oanh", False)], "Chữ mờ dần hiện vào", False),
    (40.64, 42.85, [("đã chuẩn bị xong\ntrong sáng nay ạ!", False)], "Chữ mờ dần hiện vào", False),

    (45.08, 47.72, [("Bây giờ Oanh giới thiệu\n", False), ("1 SET QUÀ", True)], "Trượt sang phải", True),
    (47.74, 49.55, [("của bên Oanh cho\nmọi người xem nhé!", False)], "Chữ mờ dần hiện vào", False),

    (52.00, 55.70, [("Một ", False), ("SET QUÀ TẶNG\n", True), ("bên trong gồm có:", False)], "Trượt sang phải", True),
    (56.25, 58.24, [("Đầu tiên là\n", False), ("1 SET YẾN SÀO", True)], "Bước sang trái", True),
    (58.26, 61.05, [("gồm ", False), ("1 TỔ YẾN TINH CHẾ\n", True), ("sợi dài • dòng tiêu chuẩn", False)], "Xoay lấp lánh", True),
    (61.10, 63.15, [("kèm theo đầy đủ\n", False), ("NGUYÊN LIỆU CHƯNG:", True)], "Trượt sang phải", True),
    (63.18, 66.64, [("TÁO ĐỎ • ĐÔNG TRÙNG\nKỶ TỬ • ĐƯỜNG PHÈN", True)], "Chữ mờ dần hiện vào", False),

    (66.66, 69.90, [("Thứ 2 là ", False), ("2 HỘP\nRONG BIỂN SẤY GIÒN", True)], "Bước sang trái", True),
    (70.12, 72.30, [("1 hộp ", False), ("SẤY GIÒN CAY NHẸ", True)], "Trượt sang phải", True),
    (72.42, 74.50, [("và 1 hộp\n", False), ("SẤY MÈ KHÔNG CAY", True)], "Trượt sang trái", True),

    (74.80, 77.65, [("Thứ 3 là 1 gói\n", False), ("BÁNH THUYỀN", True)], "Trượt sang phải", True),
    (77.67, 79.95, [("MIX HẠT DINH DƯỠNG\n250G", True)], "Bước sang trái", True),

    (80.28, 84.60, [("Thứ 4 là 1 gói\n", False), ("RONG BIỂN KẸP HẠT 500G", True)], "Trượt sang phải", True),
    (84.76, 86.30, [("Ở trong này thì sẽ có từ", False)], "Chữ mờ dần hiện vào", False),
    (86.32, 89.32, [("22 ĐẾN 24 THANH\n", True), ("bánh hạt dinh dưỡng!", False)], "Xoay lấp lánh", True),

    (89.36, 92.68, [("Sản phẩm ", False), ("GIÁ TRỊ NHẤT\n", True), ("trong set quà", False)], "Trượt sang phải", True),
    (92.70, 95.85, [("là ", False), ("1 TỔ YẾN TINH CHẾ\nSỢI DÀI", True)], "Xoay lấp lánh", True),

    (96.04, 100.20, [("Có chuẩn bị thêm\n", False), ("TỜ CẨM NANG YẾN SÀO", True)], "Trượt sang phải", True),
    (100.48, 103.85, [("gồm ", False), ("CÔNG DỤNG\nCỦA YẾN SÀO", True)], "Chữ mờ dần hiện vào", False),
    (103.95, 107.55, [("và hướng dẫn\n", False), ("CHƯNG YẾN ĐÚNG CÁCH", True)], "Bước sang trái", True),

    (107.84, 111.24, [("Tất cả được set trong\n", False), ("GIỎ ĐỰNG QUÀ", True)], "Trượt sang phải", False),
    (111.26, 114.08, [("chất liệu ", False), ("MICA TRONG SUỐT\n", True), ("như thế này!", False)], "Bước sang trái", True),
    (114.24, 117.36, [("Bên trên có\n", False), ("QUAI XÁCH BẰNG DA", True)], "Trượt sang phải", True),
    (117.38, 119.10, [("MÀU ĐỎ ĐÔ\n", True), ("rất là sang trọng ạ!", False)], "Xoay lấp lánh", True),
    (119.52, 122.90, [("Thiết kế thêm ", False), ("BÔNG HOA\n", True), ("tạo điểm nhấn", False)], "Trượt sang phải", True),
    (122.95, 126.15, [("và 1 chiếc ", False), ("NƠ MÀU BE\n", True), ("rất xinh xắn!", False)], "Bước sang trái", True),

    (127.52, 130.05, [("Đặc biệt các sản phẩm\ntrong set quà", False)], "Chữ mờ dần hiện vào", False),
    (130.08, 132.02, [("đều do bên Oanh\n", False), ("TRỰC TIẾP SẢN XUẤT", True)], "Xoay lấp lánh", True),
    (132.28, 135.40, [("nên cứ yên tâm về\n", False), ("CHẤT LƯỢNG & GIÁ CẢ!", True)], "Bước sang trái", True),

    (135.62, 138.00, [("Oanh xin gửi ", False), ("LỜI CẢM ƠN\n", True), ("tới quý anh chị", False)], "Chữ mờ dần hiện vào", False),
    (138.02, 140.50, [("đã tin tưởng đặt hàng\n", False), ("THỰC PHẨM F20", True)], "Xoay lấp lánh", True),
    (140.54, 144.42, [("Anh chị có nhu cầu đặt\n", False), ("SET QUÀ TẶNG", True)], "Trượt sang phải", True),
    (144.60, 147.00, [("làm quà biếu tặng\nnhân dịp lễ ", False), ("20/11", True)], "Bước sang trái", True),
    (147.02, 148.60, [("hãy ", False), ("INBOX NGAY\n", True), ("cho Oanh nhé!", False)], "Xoay lấp lánh", True),
]

tr_sub = copy.deepcopy(ttrack_tpl); tr_sub["id"] = uid(); tr_sub["segments"] = []
for t0, t1, parts, ia, pkf in SUB_ITEMS:
    tr_sub["segments"].append(make_coiny_text_seg(
        parts, t0, t1, pos_x=0.0, pos_y=-0.58,
        base_size=9.4, emph_size=11.6, in_anim_name=ia, out_anim_name="Mờ dần", pop_kf=pkf
    ))

# Callout Stack Tracks (Opening Hook 2-Tier + 4 Staggered Stewing Ingredients at exact 63.20..66.65s!)
tr_call1 = copy.deepcopy(ttrack_tpl); tr_call1["id"] = uid(); tr_call1["segments"] = [
    make_coiny_text_seg([("SET QUÀ TRI ÂN 20/11", True)], 0.15, 3.65, pos_x=0.0, pos_y=0.68, base_size=13.0, emph_size=13.8, in_anim_name="Xoay lấp lánh", pop_kf=True),
    make_coiny_text_seg([("01 • TÁO ĐỎ", True)],          63.20, 66.64, pos_x=0.0, pos_y=0.52, base_size=10.6, emph_size=11.2, in_anim_name="Trượt sang phải", pop_kf=True),
]
tr_call2 = copy.deepcopy(ttrack_tpl); tr_call2["id"] = uid(); tr_call2["segments"] = [
    make_coiny_text_seg([("Thực phẩm F20 × Yến sào SKA NEST", False)], 0.35, 3.65, pos_x=0.0, pos_y=0.55, base_size=8.8, emph_size=8.8, in_anim_name="Chữ mờ dần hiện vào", pop_kf=False),
    make_coiny_text_seg([("02 • ĐÔNG TRÙNG HẠ THẢO", True)],           63.82, 66.64, pos_x=0.0, pos_y=0.39, base_size=10.6, emph_size=11.2, in_anim_name="Trượt sang phải", pop_kf=True),
]
tr_call3 = copy.deepcopy(ttrack_tpl); tr_call3["id"] = uid(); tr_call3["segments"] = [
    make_coiny_text_seg([("03 • KỶ TỬ", True)],          65.10, 66.64, pos_x=0.0, pos_y=0.26, base_size=10.6, emph_size=11.2, in_anim_name="Trượt sang phải", pop_kf=True),
]
tr_call4 = copy.deepcopy(ttrack_tpl); tr_call4["id"] = uid(); tr_call4["segments"] = [
    make_coiny_text_seg([("04 • 01 HỘP ĐƯỜNG PHÈN", True)], 65.85, 66.64, pos_x=0.0, pos_y=0.13, base_size=10.6, emph_size=11.2, in_anim_name="Trượt sang phải", pop_kf=True),
]

# ==============================================================================
# 3. BUILD SYNCED TACTILE MICRO-SFX TRACKS (Pop / Whoosh / Chime — Zero Overlap!)
# ==============================================================================
SFX_POP    = SFX_FOLDER / "Pop - Hiện chữ nảy nhẹ gọn 02.mp3"
SFX_WHOOSH = SFX_FOLDER / "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"
SFX_COIN   = CC_MUSIC   / "9de8d4100d830a399f78d385847bfe72.mp3"
SFX_CLICK  = CC_MUSIC   / "d91f21d1c2b6ec21cf77a8d7185bdb47.mp3"

SFX_EVENTS_A = [
    (0.15,   SFX_POP,    "Pop Hook",   0.36),
    (6.38,   SFX_POP,    "Pop 104",    0.34),
    (11.50,  SFX_POP,    "Pop 20/11",  0.34),
    (16.30,  SFX_WHOOSH, "Whoosh B1",  0.28),
    (18.18,  SFX_POP,    "Pop 77 Set", 0.34),
    (22.47,  SFX_POP,    "Pop 13 Set", 0.32),
    (26.87,  SFX_POP,    "Pop 10 Set", 0.32),
    (30.56,  SFX_POP,    "Pop 4 Set",  0.32),
    (34.38,  SFX_POP,    "Pop 104",    0.36),
    (46.75,  SFX_WHOOSH, "Whoosh CamB",0.28),
    (52.15,  SFX_WHOOSH, "Whoosh Set", 0.28),
    (56.25,  SFX_POP,    "Pop Yen",    0.34),
    (63.20,  SFX_COIN,   "Ting 1",     0.32),
    (65.10,  SFX_COIN,   "Ting 3",     0.32),
    (66.66,  SFX_WHOOSH, "Whoosh RB",  0.28),
    (70.12,  SFX_CLICK,  "Click RB1",  0.40),
    (74.80,  SFX_WHOOSH, "Whoosh BT",  0.28),
    (80.25,  SFX_WHOOSH, "Whoosh KH",  0.28),
    (86.32,  SFX_POP,    "Pop 24Thanh",0.35),
    (92.70,  SFX_POP,    "Pop SoiDai", 0.35),
    (98.15,  SFX_WHOOSH, "Whoosh CN",  0.28),
    (111.26, SFX_POP,    "Pop Mica",   0.32),
    (115.60, SFX_POP,    "Pop QuaiDa", 0.35),
    (119.52, SFX_WHOOSH, "Whoosh Hoa", 0.28),
    (130.08, SFX_POP,    "Pop F20SX",  0.35),
    (138.02, SFX_POP,    "Pop F20",    0.34),
    (147.02, SFX_POP,    "Pop Inbox",  0.38),
]
SFX_EVENTS_B = [
    (63.82,  SFX_COIN,   "Ting 2",     0.32),
    (65.85,  SFX_COIN,   "Ting 4",     0.32),
    (72.42,  SFX_CLICK,  "Click RB2",  0.40),
    (122.95, SFX_POP,    "Pop NoBe",   0.33),
]

tr_sfx1 = copy.deepcopy(atrack_tpl); tr_sfx1["id"] = uid(); tr_sfx1["segments"] = [
    make_sfx_seg(p, nm, t0, vol=v) for t0, p, nm, v in SFX_EVENTS_A if p.is_file()
]
tr_sfx2 = copy.deepcopy(atrack_tpl); tr_sfx2["id"] = uid(); tr_sfx2["segments"] = [
    make_sfx_seg(p, nm, t0, vol=v) for t0, p, nm, v in SFX_EVENTS_B if p.is_file()
]

# ==============================================================================
# 4. ASSEMBLE ALL TRACKS WITH CLEAN LAYER WEIGHTS & WRITE BACK TO `1117 F20`!
# ==============================================================================
D["tracks"] = [
    track0_orig,     # Track 0: 100% UNCHANGED Main Video Timeline (0.00 -> 148.63s)!
    tr_ov_full,      # Track 1: 27 Real F20 B-Roll & Multi-Cam Camera-B Cutaways!
    tr_ov_pip,       # Track 2: 4 Rounded-Corner PIP Detail Cards!
    tr_sub,          # Track 3: 52 Synced Coiny Red-White Subtitles with Inline Emphasis & In/Out Anims!
    tr_call1,        # Track 4: Hook Title + Ingredient 1 Callout
    tr_call2,        # Track 5: Hook Subtitle + Ingredient 2 Callout
    tr_call3,        # Track 6: Ingredient 3 Callout
    tr_call4,        # Track 7: Ingredient 4 Callout
    bgm_track_orig,  # Track 8: Cheerful F20 Flute/Zither BGM (trimmed cleanly to 148.63s)
    tr_sfx1,         # Track 9: Tactile Micro-SFX Lane A
    tr_sfx2,         # Track 10: Tactile Micro-SFX Lane B
]
D["duration"] = main_end_u
D["update_time"] = now_s

for ti, tr in enumerate(D["tracks"]):
    for s in tr["segments"]:
        s["track_render_index"] = ti
        if tr["type"] == "video":
            s["render_index"] = ti
        elif tr["type"] == "text":
            s["render_index"] = 14000 + ti

dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
for target_p in [
    DRAFT_DIR / "draft_content.json",
    DRAFT_DIR / "template-2.tmp",
    tl_dc_path,
    tl_dc_path.parent / "template-2.tmp",
]:
    target_p.write_bytes(dc_bytes)

# Append newly imported F20 video materials into draft_meta_info.json Media Bin so CapCut shows them in "Phương tiện" too!
dmi_path = DRAFT_DIR / "draft_meta_info.json"
dmi = json.loads((bak / "draft_meta_info.json").read_text(encoding="utf-8"))
now_us = int(time.time() * 1_000_000)
dmi["tm_duration"] = main_end_u
dmi["tm_draft_modified"] = now_us
for bucket in dmi.get("draft_materials", []):
    if bucket.get("type") == 0:
        existing_paths = {x.get("file_Path") for x in bucket.get("value", [])}
        for ne in NEW_DM_ENTRIES:
            if ne["file_Path"] not in existing_paths:
                bucket["value"].append(ne)
dmi_path.write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

# Update Timelines/project.json update_time
pj["update_time"] = now_us
for t_ent in pj.get("timelines", []):
    t_ent["update_time"] = now_us
(DRAFT_DIR / "Timelines" / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

# Also update tm_duration & tm_draft_modified in root_meta_info.json
rmi_path = ROOT / "root_meta_info.json"
if rmi_path.exists():
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    for ent in rmi.get("all_draft_store", []):
        if ent.get("draft_name") == "1117 F20" or ent.get("draft_fold_path", "").endswith("1117 F20"):
            ent["tm_duration"] = main_end_u
            ent["tm_draft_modified"] = now_us
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

# Also sync a backup copy of completed `1117 F20` to 03_Du_An\f20-set-qua-2011
arch_cc = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011\1117_F20_CapCut_Backup")
arch_cc.mkdir(parents=True, exist_ok=True)
(arch_cc / "draft_content.json").write_bytes(dc_bytes)

print(f"SUCCESS: Upgraded '1117 F20' directly in CapCut!")
print(f"  - Track 0 (Main Video): {len(track0_orig['segments'])} segments (100.00% UNCHANGED, {main_end_u/1e6:.2f}s)")
print(f"  - Track 1 (Full Overlays): {len(tr_ov_full['segments'])} real F20 B-Roll & Multi-Cam DJI segments")
print(f"  - Track 2 (PIP Overlays): {len(tr_ov_pip['segments'])} rounded-corner PIP segments")
print(f"  - Track 3..7 (Coiny Red-White Subtitles & Callouts): {len(tr_sub['segments']) + 6} animated text segments")
print(f"  - Track 8..10 (BGM + Tactile SFX): 1 BGM + {len(tr_sfx1['segments']) + len(tr_sfx2['segments'])} SFX hits")
