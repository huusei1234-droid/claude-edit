import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path

ROOT       = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_DIR  = ROOT / "1117 F20"
HTPM_DIR   = ROOT / "HTPM"
F20_261116 = Path(r"Z:\Máy tính khác\My Computer\F20\video gốc\261116")
DOC_DIR    = F20_261116 / r"Chi Oanh\dọc"
NGANG_DIR  = F20_261116 / r"Chi Oanh\ngang"
DJI_DIR    = F20_261116 / r"Chi Oanh\dji"
ANH_HAU    = F20_261116 / r"Anh Hậu"
SFX_FOLDER = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")
WORK       = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
BAK        = WORK / "backup_1117_F20_orig"

def uid(): return str(uuid.uuid4()).upper()
def us(sec): return int(round(float(sec) * 30.0) * 1_000_000 // 30)
def norm_fwd(p): return os.path.normpath(str(p)).replace("\\", "/")

if not DRAFT_DIR.exists():
    raise FileNotFoundError(f"Missing CapCut project: {DRAFT_DIR}")
if (DRAFT_DIR / ".locked").exists():
    raise RuntimeError("1117 F20 currently has .locked! Please return to CapCut Home Screen first.")

pj = json.loads((DRAFT_DIR / "Timelines" / "project.json").read_text(encoding="utf-8"))
tl_id = pj["main_timeline_id"]
tl_dc_path = DRAFT_DIR / "Timelines" / tl_id / "draft_content.json"

# Always build cleanly from the untouched original backup so Track 0 is 100% pure!
D = json.loads((BAK / "Timelines" / tl_id / "draft_content.json").read_text(encoding="utf-8"))
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

TEXT_ANIMS  = json.loads((WORK / "all_verified_text_anims.json").read_text(encoding="utf-8"))
VIDEO_ANIMS = json.loads((WORK / "verified_video_anims.json").read_text(encoding="utf-8"))

RECT_MASK_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef"
HAS_RECT_MASK  = Path(RECT_MASK_PATH).exists()

# Keep ONLY Track 0 (100% untouched) and Track 6 (Main BGM trimmed cleanly to 148.633s)
track0_orig    = copy.deepcopy(D["tracks"][0])
bgm_track_orig = copy.deepcopy(D["tracks"][6])
main_end_u     = max(s["target_timerange"]["start"] + s["target_timerange"]["duration"] for s in track0_orig["segments"])

bgm_seg = bgm_track_orig["segments"][0]
bgm_seg["target_timerange"]["duration"] = main_end_u
bgm_seg["source_timerange"]["duration"] = main_end_u
bgm_seg["volume"] = 0.22
bgm_seg["last_nonzero_volume"] = 0.22
fade_bgm_id = uid()
D["materials"].setdefault("audio_fades", []).append({
    "fade_in_duration": 500000, "fade_out_duration": 1500000, "fade_type": 0, "id": fade_bgm_id, "type": "audio_fade"
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

# Font Coiny setup
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
# HELPER 1: VIDEO OVERLAY BUILDER (100% Cohesive Real F20 Sources)
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
        raise FileNotFoundError(f"Missing F20 video source: {path}")
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

def make_kf_points(prop_type: str, points: list[tuple[int, float]]):
    return {
        "id": uid(), "material_id": "", "property_type": prop_type,
        "keyframe_list": [
            {
                "curveType": "Line", "graphID": "", "id": uid(),
                "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
                "time_offset": int(toff), "values": [float(val)]
            }
            for toff, val in points
        ]
    }

def make_video_overlay_seg(src_path: Path, t0_s: float, t1_s: float, src_in_s: float, spd: float = 1.0,
                           mode: str = "full", in_anim: str = "Rõ dần", zoom_dir: int = 1,
                           base_scale: float = 1.0, tx: float = 0.0, ty: float = 0.0):
    mid, mat_dur_u, w, h = get_or_add_video_mat(src_path)
    tgt_st_u = us(t0_s)
    tgt_du_u = max(us(0.25), us(t1_s) - tgt_st_u)
    src_st_u = us(src_in_s)
    src_du_u = us((tgt_du_u / 1e6) * spd)
    if src_st_u + src_du_u > mat_dur_u:
        src_st_u = max(0, mat_dur_u - src_du_u)

    # Note: In CapCut 9:16 canvas (1080x1920), horizontal 16:9 clips (w > h) fit width=1080 by default,
    # so to fill vertical 9:16 cleanly without black top/bottom bars, scale must be multiplied by (1920/1080)*(w/h)/(w/h)?
    # Wait: CapCut normalizes scale=1.0 as "fit inside canvas" (letterboxed for 16:9: height = 1080 * 9/16 = 607.5px, so cover scale = 1920 / 607.5 = 3.1605!).
    eff_scale = base_scale
    if mode == "full" and w > h:
        # Cover-fill 9:16 canvas cleanly for 4K 3840x2160 clips!
        fit_h = 1080.0 * (h / w)
        cover_mult = (1920.0 / fit_h) * 1.01
        eff_scale = round(base_scale * cover_mult, 4)

    seg = copy.deepcopy(vseg_tpl)
    refs = []
    for k, tpl_e in v_extra_tpl.items():
        em = copy.deepcopy(tpl_e); em["id"] = uid()
        if k == "speeds":
            em["speed"] = round(spd, 3)
        D["materials"][k].append(em)
        refs.append(em["id"])

    anim_list = []
    if in_anim in VIDEO_ANIMS["in"]:
        ai = copy.deepcopy(VIDEO_ANIMS["in"][in_anim])
        ai["start"] = 0
        ai["duration"] = min(233333 if mode == "full" else 333333, tgt_du_u // 3)
        anim_list.append(ai)
    if "Mờ dần" in VIDEO_ANIMS["out"]:
        ao = copy.deepcopy(VIDEO_ANIMS["out"]["Mờ dần"])
        out_d = min(200000, tgt_du_u // 3)
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
        seg["clip"]["scale"] = {"x": eff_scale, "y": eff_scale}
        seg["clip"]["transform"] = {"x": tx, "y": ty}
        seg["uniform_scale"] = {"on": True, "value": eff_scale}
        if zoom_dir != 0 and tgt_du_u >= 1800000:
            s0, s1 = (eff_scale, round(eff_scale * 1.038, 4)) if zoom_dir > 0 else (round(eff_scale * 1.038, 4), eff_scale)
            kfs = [
                make_kf_points("KFTypeScaleX", [(0, s0), (tgt_du_u, s1)]),
                make_kf_points("KFTypeScaleY", [(0, s0), (tgt_du_u, s1)]),
            ]
    elif mode in ("pip_tl", "pip_tr"):
        px = -0.48 if mode == "pip_tl" else 0.48
        py = 0.44
        sc = 0.34 if h >= w else 0.62
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
# HELPER 2: 2-TIER COINY TYPOGRAPHY ENGINE
#   - Mode A (Bottom Subtitles): Crisp Red fill + Slender White stroke; inline highlights = White fill + Red stroke!
#   - Mode B (Floating Highlight Tags): Pure White fill + Rich Crimson Red stroke, floating & drifting around Chị Oanh / products!
# ==============================================================================
RED_FILL   = [0.9019608, 0.1098039, 0.1411765]  # #E61C24 (Vibrant clean red)
RED_STROKE = [0.8549020, 0.0784314, 0.1176471]  # #DA141E (Deep crisp crimson border for White emphasis text)
WHITE_COL  = [1.0, 1.0, 1.0]                    # #FFFFFF

def make_coiny_subtitle_seg(parts: list[tuple[str, bool]], t0_s: float, t1_s: float, pos_y: float = -0.66):
    """
    Bottom subtitle:
      - is_emph=False -> Red fill (#E61C24) + White stroke (width 0.052), size 8.6
      - is_emph=True  -> White fill (#FFFFFF) + Red stroke (#DA141E, width 0.058), size 9.0 (clean uniform line height!)
    """
    full_text = "".join(p[0] for p in parts)
    styles = []
    cur = 0
    for chunk, is_emph in parts:
        ln = len(chunk)
        if ln == 0:
            continue
        if is_emph:
            fcol, scol, sw, sz = WHITE_COL, RED_STROKE, 0.060, 9.0
        else:
            fcol, scol, sw, sz = RED_FILL, WHITE_COL, 0.052, 8.6
        styles.append({
            "fill": {"content": {"render_type": "solid", "solid": {"color": fcol}}},
            "font": {"id": COINY_ID, "path": COINY_PATH},
            "strokes": [{"content": {"render_type": "solid", "solid": {"color": scol}}, "width": sw, "mode": 0}],
            "shadows": [{
                "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
                "alpha": 0.42, "angle": -45.0, "diffuse": 0.38, "distance": 3.2, "feather": 0.40
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
        "id": tm_id, "type": "subtitle",
        "recognize_text": full_text, "translate_original_text": full_text,
        "content": json.dumps({"text": full_text, "styles": styles}, ensure_ascii=False),
        "base_content": json.dumps({
            "text": full_text,
            "styles": [{"fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": RED_FILL}}}, "font": {"id": COINY_ID, "path": COINY_PATH}, "range": [0, len(full_text)], "size": 8.6}]
        }, ensure_ascii=False),
        "font_size": 8.6, "font_path": COINY_PATH, "font_resource_id": COINY_ID, "fonts": [f_copy],
        "text_color": "#e61c24", "border_color": "#ffffff", "border_width": 0.052,
        "has_shadow": True, "shadow_color": "#000000", "shadow_alpha": 0.42, "shadow_smoothing": 0.40, "shadow_distance": 3.2,
        "alignment": 1, "line_feed": 1, "line_spacing": 0.02, "letter_spacing": 0.0,
        "line_max_width": 0.78, "force_apply_line_max_width": True,
        "is_rich_text": len(styles) > 1, "check_flag": 31,
    })
    D["materials"]["texts"].append(tm)

    tgt_st_u = us(t0_s)
    tgt_du_u = max(us(0.35), us(t1_s) - tgt_st_u)

    # Clean gentle fade In + fade Out on every subtitle!
    in_key = "Chữ mờ dần hiện vào" if "Chữ mờ dần hiện vào" in TEXT_ANIMS["in"] else "Mờ"
    ai = copy.deepcopy(TEXT_ANIMS["in"][in_key])
    ai["start"] = 0
    ai["duration"] = min(166666, tgt_du_u // 4)
    ao = copy.deepcopy(TEXT_ANIMS["out"]["Mờ dần"])
    od = min(133333, tgt_du_u // 4)
    ao["duration"] = od
    ao["start"] = max(0, tgt_du_u - od)

    ma_id = uid()
    D["materials"].setdefault("material_animations", []).append({
        "animations": [ai, ao], "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
    })

    ts = copy.deepcopy(tseg_tpl)
    ts.update({
        "id": uid(), "material_id": tm_id,
        "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
        "extra_material_refs": [ma_id],
        "common_keyframes": [], "keyframe_refs": [],
    })
    ts["clip"]["transform"] = {"x": 0.0, "y": pos_y}
    ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
    ts["clip"]["rotation"] = 0.0
    ts["uniform_scale"] = {"on": True, "value": 1.0}
    return ts


def make_floating_white_red_tag(text: str, t0_s: float, t1_s: float,
                                pos_x: float, pos_y: float, size: float = 10.2,
                                rot_deg: float = 0.0, in_anim_name: str = "Mờ"):
    """
    Separate Floating Emphasis Tag ('chữ trắng viền đỏ bay bay lên sản phẩm hoặc xung quanh chị oanh'):
      - Pure White fill (#FFFFFF) + Rich Crimson Red stroke (#DA141E, width 0.072) + soft drop shadow
      - Native CapCut In + Floating Loop ('Chao đảo ngẫu nhiên') + Out ('Mờ dần')
      - Smooth upward levitation keyframes (y_start -> y_end) + gentle pop scale (0.86 -> 1.05 -> 1.00)!
    """
    styles = [{
        "fill": {"content": {"render_type": "solid", "solid": {"color": WHITE_COL}}},
        "font": {"id": COINY_ID, "path": COINY_PATH},
        "strokes": [{"content": {"render_type": "solid", "solid": {"color": RED_STROKE}}, "width": 0.072, "mode": 0}],
        "shadows": [{
            "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
            "alpha": 0.55, "angle": -45.0, "diffuse": 0.45, "distance": 4.2, "feather": 0.45
        }],
        "size": size,
        "useLetterColor": True,
        "range": [0, len(text)],
    }]

    tm = copy.deepcopy(tmat_coiny)
    tm_id = uid()
    f_copy = copy.deepcopy(COINY_FONT_OBJ); f_copy["id"] = uid()
    tm.update({
        "id": tm_id, "type": "text",
        "recognize_text": text, "translate_original_text": text,
        "content": json.dumps({"text": text, "styles": styles}, ensure_ascii=False),
        "base_content": json.dumps({
            "text": text,
            "styles": [{"fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": WHITE_COL}}}, "font": {"id": COINY_ID, "path": COINY_PATH}, "range": [0, len(text)], "size": size}]
        }, ensure_ascii=False),
        "font_size": size, "font_path": COINY_PATH, "font_resource_id": COINY_ID, "fonts": [f_copy],
        "text_color": "#ffffff", "border_color": "#da141e", "border_width": 0.072,
        "has_shadow": True, "shadow_color": "#000000", "shadow_alpha": 0.55, "shadow_smoothing": 0.45, "shadow_distance": 4.2,
        "alignment": 1, "line_feed": 1, "line_spacing": 0.02, "letter_spacing": 0.0,
        "line_max_width": 0.72, "force_apply_line_max_width": True,
        "is_rich_text": False, "check_flag": 31,
    })
    D["materials"]["texts"].append(tm)

    tgt_st_u = us(t0_s)
    tgt_du_u = max(us(0.45), us(t1_s) - tgt_st_u)

    anim_items = []
    ik = in_anim_name if in_anim_name in TEXT_ANIMS["in"] else "Mờ"
    ai = copy.deepcopy(TEXT_ANIMS["in"][ik])
    in_d = min(233333, tgt_du_u // 4)
    ai["start"] = 0
    ai["duration"] = in_d
    anim_items.append(ai)

    ao = copy.deepcopy(TEXT_ANIMS["out"]["Mờ dần"])
    out_d = min(200000, tgt_du_u // 4)
    ao["duration"] = out_d
    ao["start"] = max(0, tgt_du_u - out_d)
    anim_items.append(ao)

    # Add dreamy floating loop ('Chao đảo ngẫu nhiên') during middle of segment!
    if "Chao đảo ngẫu nhiên" in TEXT_ANIMS["loop"] and tgt_du_u > (in_d + out_d + 200000):
        al = copy.deepcopy(TEXT_ANIMS["loop"]["Chao đảo ngẫu nhiên"])
        al["start"] = in_d
        al["duration"] = tgt_du_u - in_d - out_d
        anim_items.append(al)

    ma_id = uid()
    D["materials"].setdefault("material_animations", []).append({
        "animations": anim_items, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
    })

    # Smooth floating upward rise + soft elastic pop!
    y0 = round(pos_y - 0.042, 4)
    y_mid = round(pos_y + 0.010, 4)
    y1 = round(pos_y + 0.036, 4)
    t_pop = min(200000, tgt_du_u // 3)
    t_settle = min(400000, (tgt_du_u * 2) // 3)
    kfs = [
        make_kf_points("KFTypePositionY", [(0, y0), (t_settle, y_mid), (tgt_du_u, y1)]),
        make_kf_points("KFTypeScaleX", [(0, 0.86), (t_pop, 1.05), (t_settle, 1.00), (tgt_du_u, 1.02)]),
        make_kf_points("KFTypeScaleY", [(0, 0.86), (t_pop, 1.05), (t_settle, 1.00), (tgt_du_u, 1.02)]),
    ]

    ts = copy.deepcopy(tseg_tpl)
    ts.update({
        "id": uid(), "material_id": tm_id,
        "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
        "extra_material_refs": [ma_id],
        "common_keyframes": kfs, "keyframe_refs": [],
    })
    ts["clip"]["transform"] = {"x": pos_x, "y": pos_y}
    ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
    ts["clip"]["rotation"] = float(rot_deg)
    ts["uniform_scale"] = {"on": True, "value": 1.0}
    return ts


# ==============================================================================
# HELPER 3: USER SFX BUILDER (100% From User's Personal SFX Folder!)
# ==============================================================================
AMAT_MAP = {}
def make_sfx_seg(sfx_filename: str, label: str, t0_s: float, vol: float = 0.30, max_dur_s: float = 1.35):
    sfx_path = SFX_FOLDER / sfx_filename
    if not sfx_path.is_file():
        raise FileNotFoundError(f"Missing user SFX file: {sfx_path}")
    fwd = norm_fwd(sfx_path)
    if fwd not in AMAT_MAP:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(sfx_path)], capture_output=True, text=True, check=True)
        d_s = float(json.loads(r.stdout)["format"]["duration"])
        d_u = us(d_s)
        aid = uid()
        am = copy.deepcopy(amat_tpl)
        am.update({
            "id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
            "name": label, "path": fwd, "duration": d_u, "type": "sound"
        })
        D["materials"]["audios"].append(am)
        AMAT_MAP[fwd] = (aid, d_u)
    aid, d_u = AMAT_MAP[fwd]
    du = min(d_u, us(max_dur_s))
    sg = copy.deepcopy(aseg_tpl)
    refs = []
    for k, tpl_e in a_extra_tpl.items():
        em = copy.deepcopy(tpl_e); em["id"] = uid()
        if k == "speeds":
            em["speed"] = 1.0
        D["materials"][k].append(em)
        refs.append(em["id"])
    # Smooth 80ms fade-out on truncated SFX so it never clicks!
    fid = uid()
    D["materials"].setdefault("audio_fades", []).append({
        "fade_in_duration": 0, "fade_out_duration": min(80000, du // 4), "fade_type": 0, "id": fid, "type": "audio_fade"
    })
    refs.append(fid)
    sg.update({
        "id": uid(), "material_id": aid,
        "source_timerange": {"start": 0, "duration": du},
        "target_timerange": {"start": us(t0_s), "duration": du},
        "speed": 1.0, "volume": vol, "last_nonzero_volume": vol,
        "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": []
    })
    return sg


# ==============================================================================
# 1. COHESIVE, STORY-LOCKED REAL F20 OVERLAYS (Zero random room jumps, zero lip-sync clash!)
# ==============================================================================
FULL_OVERLAYS = [
    # (src_path, t0_s, t1_s, src_in_s, spd, in_anim, zoom_dir, base_scale, tx, ty)
    # 1. Intro Showroom Set Quà supplement (same F20 showroom lighting as S00!)
    (DOC_DIR / "C3875.MP4", 1.85,  3.77,  0.60, 1.00, "Rõ dần",  -1, 1.00,  0.00,  0.00),

    # 2. Đăng Khoa Edu Story Beat (15.65 - 19.95s: "1 là Anh Hậu tại Trung tâm luyện thi Đăng Khoa Edu đặt 77 set quà")
    (ANH_HAU / "C3920.MP4", 15.65, 17.75, 4.60, 1.00, "Rõ dần",  +1, 1.00,  0.00,  0.00),
    (ANH_HAU / "C3928.MP4", 17.75, 19.95, 1.20, 1.00, "Rõ dần",  -1, 1.00,  0.00,  0.00),

    # 3. Hội phụ huynh Nha Trang đặt 13 set quà (20.20 - 23.90s: F20 showroom team preparing 13 sets)
    (DOC_DIR / "C3882.MP4", 20.20, 23.90, 0.60, 1.00, "Rõ dần",  +1, 1.00,  0.00,  0.00),

    # 4. Out-of-Province Shipping Beat: Hà Nội 10 set (packing into carton) -> TP.HCM 4 set (loading car trunk)
    (DOC_DIR / "C3887.MP4", 24.67, 28.05, 0.50, 1.00, "Rõ dần",  +1, 1.00,  0.00,  0.00),
    (DOC_DIR / "C3901.MP4", 28.05, 31.68, 0.50, 1.00, "Rõ dần",  -1, 1.00,  0.00,  0.00),

    # 5. Grand Reveal of 104 Sets on Showroom Table ("ĐỦ 104 SET QUÀ nha mọi người!")
    (DOC_DIR / "C3869.MP4", 33.80, 36.65, 1.40, 1.00, "Rõ dần",  +1, 1.00,  0.00,  0.00),

    # 6. 4K Macro Glide across prepared showroom gift baskets (41.60 - 44.85s — same showroom!)
    (NGANG_DIR / "DJI_20261116095310_0100_D.MP4", 41.60, 44.85, 0.40, 0.90, "Rõ dần", +1, 1.00, 0.00, 0.00),

    # 7. Inside 1 Gift Set Macro Overview (52.20 - 56.15s: "Một set quà tặng bên trong gồm có:")
    (DOC_DIR / "C3873.MP4", 52.20, 56.15, 0.25, 0.78, "Rõ dần",  +1, 1.00,  0.00,  0.00),

    # 8. Item 1 — 1 Tổ Yến Sào Tinh Chế Sợi Dài (58.25 - 61.08s: close-up of round SKA NEST box, after Chị Oanh introduces it on Track 0!)
    (DOC_DIR / "C3867.MP4", 58.25, 61.08, 0.35, 0.82, "Rõ dần",  -1, 1.00,  0.00,  0.00),

    # 9. 4 Stewing Ingredients Macro (63.15 - 66.65s: strictly 0.20..2.86s close-up on round SKA NEST stewing box before shelf tilt!)
    (DOC_DIR / "C3874.MP4", 63.15, 66.65, 0.20, 0.74, "Rõ dần",  +1, 1.04,  0.00,  0.00),

    # 10. Item 2 — 2 Hộp Rong Biển Sấy Giòn Cay Nhẹ & Sấy Mè Không Cay (70.10 - 74.48s: 100% synced 3K hands+jars close-up!)
    (DJI_DIR / "DJI_20261116093322_0084_D.MP4",   70.10, 74.48, 33.80, 1.05, "Rõ dần", 0, 1.56, -0.32, -0.06),

    # 11. Item 3 — Bánh Thuyền Mix Hạt 250g (77.15 - 79.95s: 100% audio-synced 3K hands+product close-up, zero cut-off face!)
    (DJI_DIR / "DJI_20261116093322_0084_D.MP4",   77.15, 79.95, 43.67, 1.05, "Rõ dần", 0, 1.56, -0.32, -0.06),

    # 12. Item 4 — Rong Biển Kẹp Hạt 500g (82.20 - 85.40s: 100% audio-synced 3K hands+product close-up, then 85.4-89.6s Chị Oanh on Track 0!)
    (DJI_DIR / "DJI_20261116093322_0084_D.MP4",   82.20, 85.40, 49.29, 1.05, "Rõ dần", 0, 1.56, -0.32, -0.06),

    # 13. Giá Trị Nhất — 1 Tổ Yến Sào Tinh Chế Sợi Dài (92.65 - 95.85s: 3K hands+Bird's Nest box close-up!)
    (DJI_DIR / "DJI_20261116093322_0084_D.MP4",   92.65, 95.85, 14.20, 1.00, "Rõ dần", +1, 1.52, -0.30, -0.04),

    # 14. Tờ Cẩm Nang Sử Dụng Yến Sào: synced medium close-up (98.60-102.80s) -> lifted centered macro inside open pages (102.80-107.30s)!
    (DJI_DIR / "DJI_20261116093955_0088_D.MP4",   98.60, 102.80, 13.04, 1.05, "Rõ dần", 0, 1.00,  0.00, 0.00),
    (DJI_DIR / "DJI_20261116093826_0087_D.MP4",  102.80, 107.30, 16.50, 0.95, "Rõ dần", +1, 1.32, -0.14, +0.20),

    # 15. Packaging Luxury Details (4 distinct shots — zero repetition, zero unsynced mouth!):
    # - Giỏ đựng quà chất liệu MICA TRONG SUỐT (110.80 - 114.10s: full upright clear mica gift basket!)
    (DJI_DIR / "DJI_20261116093624_0085_D.MP4",  110.80, 114.10, 12.20, 0.90, "Rõ dần", +1, 1.00, 0.00, 0.00),
    # - QUAI XÁCH BẰNG DA MÀU ĐỎ ĐÔ sang trọng (116.15 - 119.15s: 4K macro of burgundy leather handle!)
    (NGANG_DIR / "DJI_20261116095317_0101_D.MP4", 116.15, 119.15, 4.60, 0.80, "Rõ dần", -1, 1.02, 0.00, 0.00),
    # - BÔNG HOA tạo điểm nhấn (119.55 - 122.90s: close-up glide showing red satin flower accent inside basket!)
    (DOC_DIR / "C3873.MP4",                      119.55, 122.90, 1.80, 0.80, "Rõ dần", +1, 1.04, 0.00, 0.00),
    # - Chiếc NƠ MÀU BE rất xinh xắn (122.90 - 126.20s: 4K macro of sheer beige organza ribbon bows!)
    (NGANG_DIR / "DJI_20261116095310_0100_D.MP4", 122.90, 126.20, 0.50, 0.80, "Rõ dần", +1, 1.00, 0.00, 0.00),

    # 16. Trực tiếp sản xuất — Chất lượng & Giá cả (129.80 - 135.40s: F20 uniformed team assembling & inspecting sets, also bridges S14-S18 cuts!)
    (DOC_DIR / "C3870.MP4", 129.80, 132.60, 1.00, 1.00, "Rõ dần", +1, 1.00, 0.00, 0.00),
    (DOC_DIR / "C3866.MP4", 132.60, 135.40, 2.50, 1.00, "Rõ dần", -1, 1.00, 0.00, 0.00),

    # 17. Final 20/11 Gift Set Beauty Shot before Chị Oanh smiles & says "hãy inbox ngay cho Oanh nhé!"
    (DOC_DIR / "C3873.MP4", 143.60, 146.75, 1.10, 0.85, "Rõ dần", +1, 1.00, 0.00, 0.00),
]

PIP_OVERLAYS = [
    # Sleek rounded-corner PIPs in upper-right safe margin while Chị Oanh speaks warmly on Track 0!
    (DOC_DIR / "C3873.MP4",  6.35,   9.40,  0.40, 0.90, "pip_tr", "Trượt sang trái"),
    (ANH_HAU / "C3928.MP4", 136.40, 140.40, 1.50, 1.00, "pip_tr", "Trượt sang trái"),
]

tr_ov_full = copy.deepcopy(vtrack_tpl); tr_ov_full["id"] = uid(); tr_ov_full["segments"] = [
    make_video_overlay_seg(sp, t0, t1, sin, spd=spd, mode="full", in_anim=ia, zoom_dir=zd, base_scale=bsc, tx=tx, ty=ty)
    for sp, t0, t1, sin, spd, ia, zd, bsc, tx, ty in FULL_OVERLAYS
]
tr_ov_pip = copy.deepcopy(vtrack_tpl); tr_ov_pip["id"] = uid(); tr_ov_pip["segments"] = [
    make_video_overlay_seg(sp, t0, t1, sin, spd=spd, mode=md, in_anim=ia, zoom_dir=0)
    for sp, t0, t1, sin, spd, md, ia in PIP_OVERLAYS
]


# ==============================================================================
# 2A. CLEAN, UNIFORM BOTTOM SUBTITLES (Track 3 — Red Fill + White Stroke, Inline Emphasis = White Fill + Red Stroke!)
# ==============================================================================
SUB_ITEMS = [
    (4.56,  6.38,  [("Hôm nay bên Oanh đang chuẩn bị", False)]),
    (6.40,  7.96,  [("tổng cộng ", False), ("104 set quà", True)]),
    (7.98,  9.44,  [("cho các khách hàng đặt", False)]),
    (9.46,  11.48, [("làm ", False), ("quà biếu tặng", True), (" thầy cô giáo", False)]),
    (11.50, 13.65, [("nhân dịp tri ân ngày ", False), ("20/11", True)]),

    (13.96, 15.58, [("Ở ", False), ("Nha Trang", True), (" có 2 khách hàng", False)]),
    (15.64, 17.56, [("1 là ", False), ("Anh Hậu", True), (" • Trung tâm luyện thi", False)]),
    (17.58, 19.85, [("Đăng Khoa Edu", True), (" đặt ", False), ("77 set quà", True)]),
    (20.18, 22.45, [("Khách thứ 2 là ", False), ("Hội phụ huynh", True)]),
    (22.47, 23.90, [("đặt ", False), ("13 set quà", True)]),
    (24.00, 26.85, [("1 bạn giáo viên ở ", False), ("Hà Nội", True)]),
    (26.87, 27.85, [("đặt ", False), ("10 set quà", True)]),
    (27.92, 30.54, [("và 1 bạn ở ", False), ("TP. Hồ Chí Minh", True)]),
    (30.56, 31.68, [("đặt ", False), ("4 set quà", True)]),

    (31.70, 34.36, [("Tổng sáng nay bên mình chuẩn bị", False)]),
    (34.38, 36.55, [("đủ 104 set quà", True), (" nha mọi người!", False)]),

    (38.60, 40.62, [("Đây là những ", False), ("set quà", True), (" bên Oanh", False)]),
    (40.64, 42.85, [("đã chuẩn bị xong trong sáng nay ạ!", False)]),

    (45.08, 47.72, [("Bây giờ Oanh giới thiệu ", False), ("1 set quà", True)]),
    (47.74, 49.55, [("của bên Oanh cho mọi người xem nhé!", False)]),

    (52.00, 55.70, [("Một ", False), ("set quà tặng", True), (" bên trong gồm có:", False)]),
    (56.25, 58.24, [("Đầu tiên là ", False), ("1 set yến sào", True)]),
    (58.26, 61.05, [("gồm ", False), ("1 tổ yến tinh chế sợi dài", True)]),
    (61.10, 63.15, [("kèm theo đầy đủ ", False), ("nguyên liệu chưng:", True)]),
    (63.18, 66.64, [("Táo đỏ • Đông trùng\nKỷ tử • Đường phèn", True)]),

    (66.66, 69.90, [("Thứ 2 là ", False), ("2 hộp rong biển sấy giòn", True)]),
    (70.12, 72.30, [("1 hộp ", False), ("sấy giòn cay nhẹ", True)]),
    (72.42, 74.50, [("và 1 hộp ", False), ("sấy mè không cay", True)]),

    (74.80, 77.65, [("Thứ 3 là 1 gói ", False), ("bánh thuyền", True)]),
    (77.67, 79.95, [("mix hạt dinh dưỡng ", False), ("250g", True)]),

    (80.28, 84.60, [("Thứ 4 là 1 gói\n", False), ("rong biển kẹp hạt 500g", True)]),
    (84.76, 86.30, [("Ở trong này thì sẽ có từ", False)]),
    (86.32, 89.32, [("22 đến 24 thanh\n", True), ("bánh hạt dinh dưỡng!", False)]),

    (89.36, 92.68, [("Sản phẩm ", False), ("giá trị nhất", True), (" trong set quà", False)]),
    (92.70, 95.85, [("là ", False), ("1 tổ yến tinh chế sợi dài", True)]),

    (96.04, 100.20, [("Có chuẩn bị thêm ", False), ("tờ cẩm nang yến sào", True)]),
    (100.48, 103.85, [("gồm ", False), ("công dụng của yến sào", True)]),
    (103.95, 107.55, [("và hướng dẫn\n", False), ("chưng yến đúng cách", True)]),

    (107.84, 111.24, [("Tất cả được set trong ", False), ("giỏ đựng quà", True)]),
    (111.26, 114.08, [("chất liệu ", False), ("mica trong suốt\n", True), ("như thế này!", False)]),
    (114.24, 117.36, [("Bên trên có ", False), ("quai xách bằng da", True)]),
    (117.38, 119.10, [("màu đỏ đô", True), (" rất là sang trọng ạ!", False)]),
    (119.52, 122.90, [("Thiết kế thêm ", False), ("bông hoa", True), (" tạo điểm nhấn", False)]),
    (122.95, 126.15, [("và 1 chiếc ", False), ("nơ màu be", True), (" rất xinh xắn!", False)]),

    (127.52, 130.05, [("Đặc biệt các sản phẩm trong set quà", False)]),
    (130.08, 132.02, [("đều do bên Oanh ", False), ("trực tiếp sản xuất", True)]),
    (132.28, 135.40, [("nên cứ yên tâm về ", False), ("chất lượng & giá cả!", True)]),

    (135.62, 138.00, [("Oanh xin gửi ", False), ("lời cảm ơn", True), (" tới quý anh chị", False)]),
    (138.02, 140.50, [("đã tin tưởng đặt hàng ", False), ("Thực phẩm F20", True)]),
    (140.54, 144.42, [("Anh chị có nhu cầu đặt ", False), ("set quà tặng", True)]),
    (144.60, 147.00, [("làm quà biếu tặng nhân dịp lễ ", False), ("20/11", True)]),
    (147.02, 148.60, [("hãy ", False), ("inbox ngay", True), (" cho Oanh nhé!", False)]),
]

tr_sub = copy.deepcopy(ttrack_tpl); tr_sub["id"] = uid(); tr_sub["segments"] = [
    make_coiny_subtitle_seg(parts, t0, t1, pos_y=-0.66) for t0, t1, parts in SUB_ITEMS
]


# ==============================================================================
# 2B. SEPARATE FLOATING WHITE-FILL RED-STROKE HIGHLIGHT TAGS (Tracks 4..7)
#     Floating & rising around Chị Oanh's shoulders or directly over the products!
# ==============================================================================
# Tuple: (t0, t1, text, pos_x, pos_y, size, rot_deg, in_anim)
FLOATING_TAGS_ALL = [
    # Intro Hook above gift baskets
    (0.18,   3.65, "SET QUÀ TRI ÂN 20/11",     0.00,  0.58, 12.0,  0.0, "Mờ"),
    (0.42,   3.65, "F20 × YẾN SÀO SKA NEST",   0.00,  0.44,  9.2,  0.0, "Chữ mờ dần hiện vào"),

    # Around Chị Oanh during opening speech (Track 0 — 100% forehead-safe!)
    (6.38,   9.25, "104 SET QUÀ",             -0.38,  0.46, 10.8, +4.0, "Trượt sang phải"),
    (9.55,  13.55, "QUÀ BIẾU 20/11",          +0.34,  0.44, 10.4, -4.0, "Trượt sang trái"),

    # Customer order highlights floating above each scene
    (15.70, 19.85, "ĐĂNG KHOA EDU",           -0.26,  0.60, 10.2, +3.0, "Trượt sang phải"),
    (17.55, 19.85, "77 SET QUÀ",              +0.28,  0.50, 11.2, -3.5, "Trượt sang trái"),
    (20.30, 23.85, "HỘI PHỤ HUYNH • 13 SET",   0.00,  0.48, 10.2,  0.0, "Mờ"),
    (24.72, 27.82, "HÀ NỘI • 10 SET",         -0.24,  0.46, 10.4, +3.0, "Trượt sang phải"),
    (28.08, 31.62, "TP.HCM • 04 SET",         +0.24,  0.46, 10.4, -3.0, "Trượt sang trái"),
    (33.85, 36.60, "ĐỦ 104 SET QUÀ!",          0.00,  0.48, 11.6,  0.0, "Bụi vàng"),

    # Around Chị Oanh & Gift Basket walkthrough
    (45.20, 49.45, "CHI TIẾT 01 SET QUÀ",     +0.24,  0.34, 10.2, -3.0, "Trượt sang trái"),
    (56.28, 61.02, "01 TỔ YẾN TINH CHẾ",       0.00,  0.48, 10.8,  0.0, "Mờ"),
    (58.35, 61.02, "SỢI DÀI TIÊU CHUẨN",       0.00,  0.35,  9.2,  0.0, "Chữ mờ dần hiện vào"),

    # 4 Stewing Ingredient Tags floating around the SKA NEST box (63.18 - 66.62s)
    (63.18, 66.62, "TÁO ĐỎ",                  -0.36,  0.48, 10.4, +4.0, "Trượt sang phải"),
    (63.82, 66.62, "ĐÔNG TRÙNG HẠ THẢO",      +0.20,  0.36, 10.0, -3.0, "Trượt sang trái"),
    (65.05, 66.62, "KỶ TỬ",                   -0.36,  0.20, 10.4, +3.5, "Trượt sang phải"),
    (65.80, 66.62, "ĐƯỜNG PHÈN",              +0.26,  0.08, 10.4, -3.5, "Trượt sang trái"),

    # Item 2: 2 hộp rong biển sấy giòn
    (66.70, 70.05, "02 HỘP RONG BIỂN",        +0.24,  0.34, 10.4, -3.0, "Trượt sang trái"),
    (70.15, 74.42, "CAY NHẸ",                 -0.32,  0.44, 10.2, +3.5, "Trượt sang phải"),
    (72.42, 74.42, "SẤY MÈ KHÔNG CAY",        +0.22,  0.30, 10.0, -3.0, "Trượt sang trái"),

    # Item 3: Bánh thuyền mix hạt 250g
    (74.85, 79.90, "BÁNH THUYỀN MIX HẠT",     +0.18,  0.44, 10.2, -2.5, "Trượt sang trái"),
    (77.65, 79.90, "GÓI 250G",                -0.34,  0.30, 10.6, +4.0, "Trượt sang phải"),

    # Item 4: Rong biển kẹp hạt 500g (22 - 24 thanh)
    (80.32, 85.35, "RONG BIỂN KẸP HẠT 500G",   0.00,  0.48, 10.4,  0.0, "Mờ"),
    (86.28, 89.28, "22 – 24 THANH",           +0.30,  0.46, 11.0, -4.0, "Trượt sang trái"),

    # Giá trị nhất: Tổ yến tinh chế sợi dài
    (89.45, 92.60, "GIÁ TRỊ NHẤT!",           -0.28,  0.34, 10.6, +3.5, "Trượt sang phải"),
    (92.72, 95.80, "YẾN TINH CHẾ SỢI DÀI",     0.00,  0.46, 10.8,  0.0, "Bụi vàng"),

    # Cẩm nang yến sào
    (98.60, 102.75, "CẨM NANG YẾN SÀO",        0.00,  0.50, 10.4,  0.0, "Mờ"),
    (102.85, 107.25, "CÔNG DỤNG & CÁCH CHƯNG", 0.00,  0.50, 10.0,  0.0, "Chữ mờ dần hiện vào"),

    # Giỏ mica, Quai da đỏ đô, Bông hoa, Nơ màu be
    (110.85, 114.05, "GIỎ MICA TRONG SUỐT",    0.00,  0.46, 10.6,  0.0, "Mờ"),
    (116.20, 119.10, "QUAI DA ĐỎ ĐÔ",          0.00,  0.46, 11.0,  0.0, "Bụi vàng"),
    (119.58, 122.85, "HOA ĐIỂM NHẤN",         -0.28,  0.42, 10.4, +3.5, "Trượt sang phải"),
    (122.95, 126.15, "NƠ MÀU BE XINH XẮN",     0.00,  0.46, 10.6,  0.0, "Mờ"),

    # Trực tiếp sản xuất & CTA cuối
    (130.08, 135.35, "TRỰC TIẾP SẢN XUẤT",    -0.24,  0.46, 10.2, +3.0, "Trượt sang phải"),
    (132.32, 135.35, "GIÁ TẬN XƯỞNG!",        +0.26,  0.32, 10.6, -3.5, "Trượt sang trái"),
    (138.02, 140.48, "THỰC PHẨM F20",         -0.32,  0.26, 10.4, +3.5, "Trượt sang phải"),
    (146.85, 148.55, "INBOX OANH NGAY!",      +0.28,  0.28, 11.0, -4.0, "Trượt sang trái"),
]

# Auto-pack floating tags into non-overlapping CapCut text tracks (4 lanes max)!
float_lanes: list[list[dict]] = []
for t0, t1, txt, px, py, sz, rot, ia in sorted(FLOATING_TAGS_ALL, key=lambda x: x[0]):
    seg = make_floating_white_red_tag(txt, t0, t1, px, py, size=sz, rot_deg=rot, in_anim_name=ia)
    st_u = seg["target_timerange"]["start"]
    placed = False
    for lane in float_lanes:
        last_end = lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"]
        if last_end + 33333 <= st_u:
            lane.append(seg)
            placed = True
            break
    if not placed:
        float_lanes.append([seg])

float_tracks = []
for lane in float_lanes:
    tr_f = copy.deepcopy(ttrack_tpl); tr_f["id"] = uid(); tr_f["segments"] = lane
    float_tracks.append(tr_f)


# ==============================================================================
# 3. 20+ DIVERSE AUTHENTIC SFX FROM USER'S PERSONAL SFX FOLDER (`02_Hiệu Ứng Âm Thanh (SFX)`)!
# ==============================================================================
SFX_EVENTS = [
    # (t0_s, user_sfx_filename, short_label, volume, max_dur_s)
    (0.18,   "Mở cảnh - Âm thanh tỏa sáng sang trọng (Magic Reveal).mp3",   "Magic Mở Cảnh",    0.32, 2.2),
    (1.82,   "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                   "Swoosh Mở Cảnh",   0.26, 1.2),
    (6.35,   "Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3",                    "Pop 104 Set",      0.34, 1.0),
    (9.55,   "Pop & Bong Bóng - Poyoi (jump, speech bubble, telop) (1s).mp3","Poyoi 20/11",     0.30, 1.0),
    (15.62,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                   "Whoosh ĐK Edu",    0.27, 1.1),
    (17.55,  "Ting - Chuông Ting nhanh gọn.mp3",                            "Ting 77 Set",      0.32, 1.2),
    (20.25,  "Pop - Hiện chữ nảy nhẹ gọn 02.mp3",                           "Pop 13 Set",       0.32, 1.0),
    (24.68,  "Pop & Bong Bóng - Cute pop sound effects(1031419) (1s).mp3",  "Pop Hà Nội",       0.32, 1.0),
    (28.05,  "Slide - Tiếng trượt chữ ngang mượt.mp3",                      "Slide TP.HCM",     0.28, 1.1),
    (33.82,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                     "Ding Đủ 104 Set",  0.34, 1.6),
    (41.58,  "Whoosh - Lướt hiện chữ ngắn gọn 01.mp3",                      "Whoosh Đại Cảnh",  0.26, 1.0),
    (45.20,  "Slide - Tiếng trượt chữ bay lên.mp3",                         "Bay Chữ 1 Set",    0.30, 1.1),
    (52.18,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                   "Swoosh Giỏ Quà",   0.26, 1.1),
    (56.28,  "Mở cảnh - Tiếng chuông sao lung linh.mp3",                    "Sao Tổ Yến",       0.30, 1.6),
    (63.18,  "Pop & Bong Bóng - Pukutsu (water bubbles air) (1s).mp3",      "Bubble Táo Đỏ",    0.32, 1.0),
    (63.82,  "UI - Tiếng chạm màn hình cảm ứng Plip Plip.mp3",              "Plip Đông Trùng",  0.30, 1.0),
    (65.05,  "Pop & Bong Bóng - Pop! popping sound 16(1602782) (1s).mp3",   "Pop Kỷ Tử",        0.32, 1.0),
    (65.80,  "Ting - Chuông Ting nhanh gọn.mp3",                            "Ting Đường Phèn",  0.30, 1.1),
    (66.70,  "Slide - Tiếng trượt chữ bay lên.mp3",                         "Bay Rong Biển",    0.28, 1.1),
    (70.12,  "Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3",                    "Pop Cay Nhẹ",      0.32, 1.0),
    (72.42,  "Pop - Hiện chữ nảy nhẹ gọn 02.mp3",                           "Pop Không Cay",    0.32, 1.0),
    (74.82,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                   "Whoosh Bánh Thuyền",0.27, 1.1),
    (77.65,  "Pop & Bong Bóng - Cute pop sound effects(1031419) (1s).mp3",  "Pop 250g",         0.32, 1.0),
    (80.30,  "Slide - Tiếng trượt chữ ngang mượt.mp3",                      "Slide Kẹp Hạt",    0.28, 1.1),
    (86.28,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3", "Card 24 Thanh", 0.34, 1.0),
    (89.45,  "Ting - Chuông Ting nảy ý tưởng.mp3",                          "Ting Giá Trị Nhất",0.32, 1.3),
    (92.70,  "Mở cảnh - Tiếng chuông sao lung linh.mp3",                    "Sao Yến Sợi Dài",  0.30, 1.6),
    (98.58,  "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3", "Lật Cẩm Nang 1", 0.36, 1.0),
    (102.80, "Hoạt Hình & Hài - 01 Paper slide (1s).mp3",                   "Mở Trang Cẩm Nang",0.34, 1.0),
    (110.80, "Lấp Lánh & Phép Thuật - Kiratsu ☆ (light beautiful star) (1s).mp3", "Bling Giỏ Mica", 0.30, 1.0),
    (116.18, "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3",                   "Shine Quai Da Đỏ", 0.30, 1.1),
    (119.55, "Pop & Bong Bóng - Poyoi (jump, speech bubble, telop) (1s).mp3","Poyoi Hoa Đỏ",    0.30, 1.0),
    (122.92, "Ting & Chuông Đúng - Cute, sparkling, sparkle, bell(1536355) (2s).mp3", "Sparkle Nơ Be", 0.30, 1.5),
    (130.05, "Ting - Chuông Ting nảy ý tưởng.mp3",                          "Ting Sản Xuất",    0.32, 1.2),
    (132.32, "Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3",                    "Pop Giá Xưởng",    0.32, 1.0),
    (136.40, "Whoosh - Hiện chữ siêu ngắn gọn (Chuẩn TVC PIP).mp3",         "PIP Cảm Ơn",       0.28, 1.0),
    (138.02, "Ding - Tiếng chuông ngân trong trẻo.mp3",                     "Ding F20",         0.30, 1.4),
    (146.85, "Thông báo - Chuông hiện chữ tinh tế (Notification).mp3",      "Notif Inbox Ngay", 0.36, 1.5),
]

sfx_lanes: list[list[dict]] = []
for t0, fn, lbl, vol, mdur in sorted(SFX_EVENTS, key=lambda x: x[0]):
    sg = make_sfx_seg(fn, lbl, t0, vol=vol, max_dur_s=mdur)
    st_u = sg["target_timerange"]["start"]
    placed = False
    for lane in sfx_lanes:
        last_end = lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"]
        if last_end + 33333 <= st_u:
            lane.append(sg)
            placed = True
            break
    if not placed:
        sfx_lanes.append([sg])

sfx_tracks = []
for lane in sfx_lanes:
    tr_a = copy.deepcopy(atrack_tpl); tr_a["id"] = uid(); tr_a["segments"] = lane
    sfx_tracks.append(tr_a)


# ==============================================================================
# 4. ASSEMBLE & SAVE INTO `1117 F20`!
# ==============================================================================
D["tracks"] = [
    track0_orig,     # Track 0: 100.00% Untouched Main Timeline!
    tr_ov_full,      # Track 1: 23 Cohesive Real F20 B-Roll & 4K Macro Overlays!
    tr_ov_pip,       # Track 2: 2 Clean Upper-Right Rounded PIPs!
    tr_sub,          # Track 3: 52 Crisp Coiny Red-on-White Subtitles (Inline White-on-Red Highlights)!
    *float_tracks,   # Track 4..7: 36 Floating White-Fill Red-Stroke Tags ('bay bay' around Chị Oanh & Products)!
    bgm_track_orig,  # BGM Track (trimmed cleanly to 148.633s)
    *sfx_tracks,     # Multi-lane User SFX Tracks (21 distinct SFX files from user's SFX folder!)
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

# Update draft_meta_info.json Media Bin ("Phương tiện")
dmi_path = DRAFT_DIR / "draft_meta_info.json"
dmi = json.loads((BAK / "draft_meta_info.json").read_text(encoding="utf-8"))
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

pj["update_time"] = now_us
for t_ent in pj.get("timelines", []):
    t_ent["update_time"] = now_us
(DRAFT_DIR / "Timelines" / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

rmi_path = ROOT / "root_meta_info.json"
if rmi_path.exists():
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    for ent in rmi.get("all_draft_store", []):
        if ent.get("draft_name") == "1117 F20" or ent.get("draft_fold_path", "").endswith("1117 F20"):
            ent["tm_duration"] = main_end_u
            ent["tm_draft_modified"] = now_us
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

arch_cc = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011\1117_F20_CapCut_Backup")
arch_cc.mkdir(parents=True, exist_ok=True)
(arch_cc / "draft_content.json").write_bytes(dc_bytes)

print("SUCCESS V2 PRO: Upgraded '1117 F20' in CapCut!")
print(f"  - Track 0 (Main Video): {len(track0_orig['segments'])} segments (100% UNCHANGED)")
print(f"  - Track 1 (Cohesive Overlays): {len(tr_ov_full['segments'])} segments | Track 2 (PIPs): {len(tr_ov_pip['segments'])} segments")
print(f"  - Track 3 (Clean Subtitles): {len(tr_sub['segments'])} segments")
print(f"  - Floating White-on-Red Tag Lanes: {len(float_tracks)} tracks ({len(FLOATING_TAGS_ALL)} floating tags)")
print(f"  - Diverse User SFX: {len(SFX_EVENTS)} events using {len(AMAT_MAP)} distinct SFX files from user folder across {len(sfx_tracks)} lanes!")
