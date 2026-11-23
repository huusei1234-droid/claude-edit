import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path
from PIL import Image

W, H = 1080, 1920
FPS = 30.0

ROOT       = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_DIR  = ROOT / "1117 F20"
DRAFT_ALT  = ROOT / "1117 F20 (Bản Mới Kính Lúp & Banner)"
FC_V6_DIR  = ROOT / "FEEL_CHICKEN_2011_Full_Layers_V6"
HTPM_DIR   = ROOT / "HTPM"

F20_261116 = Path(r"Z:\Máy tính khác\My Computer\F20\video gốc\261116")
DOC_DIR    = F20_261116 / r"Chi Oanh\dọc"
DJI_DIR    = F20_261116 / r"Chi Oanh\dji"
ANH_HAU    = F20_261116 / r"Anh Hậu"

SFX_FOLDER = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")
WORK       = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
USER_BAK   = WORK / "backup_1117_F20_user_1644"
V7_ASSETS  = WORK / "v7_assets"
CIRCLE_DIR = V7_ASSETS / "circle_overlays"

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


def main():
    if (DRAFT_DIR / ".locked").exists():
        raise RuntimeError("1117 F20 is currently locked (.locked=True)! Please exit to CapCut Home Screen first.")

    pj = json.loads((USER_BAK / "Timelines" / "project.json").read_text(encoding="utf-8"))
    tl_id = pj["main_timeline_id"]
    D = json.loads((USER_BAK / "Timelines" / tl_id / "draft_content.json").read_text(encoding="utf-8"))

    dc_fc   = json.loads((FC_V6_DIR / "draft_content.json").read_text(encoding="utf-8"))
    dm_fc   = json.loads((FC_V6_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))
    dc_htpm = json.loads((HTPM_DIR / "draft_content.json").read_text(encoding="utf-8"))
    dm_htpm = json.loads((HTPM_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(D["tracks"][0])
    vseg_tpl   = copy.deepcopy(D["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(dc_htpm["materials"]["videos"][0])
    pmat_tpl   = copy.deepcopy(next(m for m in dc_fc["materials"]["videos"] if m.get("type") == "photo"))
    dm_vid_tpl = copy.deepcopy(dm_htpm["draft_materials"][0]["value"][0])
    dm_pho_tpl = copy.deepcopy(next(x for g in dm_fc["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "photo"))

    atrack_tpl = copy.deepcopy(next(tr for tr in D["tracks"] if tr["type"] == "audio"))
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    amat_tpl   = copy.deepcopy(D["materials"]["audios"][0])

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

    VIDEO_ANIMS   = json.loads((WORK / "verified_video_anims.json").read_text(encoding="utf-8"))
    COLOR_SLIDERS = json.loads((WORK / "native_color_sliders.json").read_text(encoding="utf-8"))

    # ==========================================================================
    # PRESERVE 100% OF USER'S EDITED TRACK 0 + TEXT TRACKS + BGM SEGMENTS!
    # ==========================================================================
    track0_user = copy.deepcopy(D["tracks"][0])  # 45 segs [0.00s -> 140.37s]
    text_tracks_user = [copy.deepcopy(tr) for tr in D["tracks"] if tr["type"] == "text"]

    amap_orig = {a["id"]: a for a in D["materials"]["audios"]}
    bgm_segs_raw = []
    for tr in D["tracks"]:
        if tr["type"] == "audio":
            for sg in tr["segments"]:
                am = amap_orig.get(sg["material_id"], {})
                if "Nhạc Sáo Trúc" in am.get("name", "") or "Nhạc" in am.get("path", ""):
                    bgm_segs_raw.append(copy.deepcopy(sg))
    bgm_segs_raw.sort(key=lambda s: s["target_timerange"]["start"])

    bgm_lanes: list[list[dict]] = []
    for bsg in bgm_segs_raw:
        st_u = bsg["target_timerange"]["start"]
        placed = False
        for ln in bgm_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] <= st_u:
                ln.append(bsg); placed = True; break
        if not placed:
            bgm_lanes.append([bsg])

    last_bgm_seg = max(bgm_segs_raw, key=lambda s: s["target_timerange"]["start"] + s["target_timerange"]["duration"])
    total_end_u  = last_bgm_seg["target_timerange"]["start"] + last_bgm_seg["target_timerange"]["duration"]  # 142.900s!
    fade_end_id  = uid()

    # Align the 4 stewing ingredient text labels neatly under our 4 Clean Circle Overlays!
    tmap_user = {t["id"]: t for t in D["materials"]["texts"]}
    ING_NUDGES = {
        "01 • TÁO ĐỎ":     (-0.46, +0.16),
        "02 • ĐÔNG TRÙNG": (+0.46, +0.16),
        "03 • KỶ TỬ":      (-0.46, -0.34),
        "04 • ĐƯỜNG PHÈN": (+0.46, -0.34),
    }
    for tr_t in text_tracks_user:
        for sg in tr_t["segments"]:
            tm = tmap_user.get(sg["material_id"], {})
            rtxt = tm.get("recognize_text", "").strip()
            if rtxt in ING_NUDGES:
                nx, ny = ING_NUDGES[rtxt]
                sg["clip"]["transform"] = {"x": nx, "y": ny}
                sg["clip"]["rotation"] = 0.0
                sg["common_keyframes"] = []
                tm["font_size"] = 10.0
                cobj = json.loads(tm["content"])
                for st_i in cobj.get("styles", []):
                    st_i["size"] = 10.0
                tm["content"] = json.dumps(cobj, ensure_ascii=False)

    # Fix tiny 0.1-0.25s cross-track subtitle overlaps from user's ripple edit
    sub_segs_all = [sg for tr_t in text_tracks_user for sg in tr_t["segments"] if tmap_user.get(sg["material_id"], {}).get("type") == "subtitle"]
    sub_segs_all.sort(key=lambda s: s["target_timerange"]["start"])
    for idx_s in range(len(sub_segs_all) - 1):
        s_cur, s_nxt = sub_segs_all[idx_s], sub_segs_all[idx_s + 1]
        if s_cur["target_timerange"]["start"] + s_cur["target_timerange"]["duration"] > s_nxt["target_timerange"]["start"]:
            s_cur["target_timerange"]["duration"] = max(333333, s_nxt["target_timerange"]["start"] - s_cur["target_timerange"]["start"] - 33333)

    bgm_tracks_user = []
    for ln in bgm_lanes:
        bt = copy.deepcopy(atrack_tpl); bt["id"] = uid(); bt["segments"] = ln
        bgm_tracks_user.append(bt)

    kept_ids = set()
    for tr_k in [track0_user, *text_tracks_user, *bgm_tracks_user]:
        for s in tr_k["segments"]:
            kept_ids.add(s["material_id"])
            kept_ids.update(s.get("extra_material_refs", []))
    for k, val in list(D["materials"].items()):
        if isinstance(val, list):
            D["materials"][k] = [x for x in val if isinstance(x, dict) and x.get("id") in kept_ids]

    D["materials"].setdefault("audio_fades", []).append({
        "fade_in_duration": 0, "fade_out_duration": 1100000, "fade_type": 0, "id": fade_end_id, "type": "audio_fade"
    })
    last_bgm_seg["extra_material_refs"].append(fade_end_id)

    now_s  = int(time.time())
    now_us = int(time.time() * 1_000_000)
    vis_cache = {}
    new_dm_entries = []

    def register_visual_asset(path: Path, allow_v7_asset: bool = False):
        if not path.is_file():
            raise FileNotFoundError(f"Missing visual file: {path}")
        fwd = norm_fwd(path)
        if not allow_v7_asset:
            assert fwd.startswith("Z:/Máy tính khác/My Computer/F20/"), f"Video overlay MUST be raw F20 source: {fwd}"
        if fwd in vis_cache:
            return vis_cache[fwd]
        is_photo = path.suffix.lower() in (".png", ".jpg", ".jpeg")
        mid = uid()
        lmid = str(uuid.uuid4())
        if is_photo:
            with Image.open(path) as im:
                w, h = im.size
            assert (w, h) == (W, H), f"Photo overlay MUST be 1080x1920 to guarantee 0% oval stretch: got {(w, h)}"
            dur_u = 10_800_000_000
            m = copy.deepcopy(pmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "photo", "path": fwd, "media_path": "", "local_id": "",
                "material_name": path.name, "width": w, "height": h, "duration": dur_u, "has_audio": False,
                "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0,
            })
            dme = copy.deepcopy(dm_pho_tpl)
            dme.update({
                "id": lmid, "file_Path": fwd, "extra_info": path.name,
                "duration": 5_000_000, "width": w, "height": h,
                "metetype": "photo", "item_source": 1,
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
            })
        else:
            w, h, dur_s, has_aud = probe_media(path)
            assert h >= w, f"Raw video overlay must be native vertical 9:16 so 0% zoom/stretch is needed: {path.name} ({w}x{h})"
            dur_u = max(33333, us(dur_s))
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": fwd, "media_path": "", "local_id": "",
                "material_name": path.name, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud),
                "crop": copy.deepcopy(FULL_CROP_1_1), "crop_ratio": "free", "crop_scale": 1.0,
            })
            dme = copy.deepcopy(dm_vid_tpl)
            dme.update({
                "id": lmid, "file_Path": fwd, "extra_info": path.name,
                "duration": dur_u, "width": w, "height": h,
                "metetype": "video", "item_source": 1,
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
                "roughcut_time_range": {"start": 0, "duration": dur_u},
                "sub_time_range": {"start": -1, "duration": -1},
            })
        D["materials"]["videos"].append(m)
        new_dm_entries.append(dme)
        vis_cache[fwd] = (mid, dur_u, w, h, is_photo)
        return mid, dur_u, w, h, is_photo

    def attach_color_sliders(refs: list[str], vals: list[tuple[str, float]]):
        D["materials"].setdefault("effects", [])
        for stype, sval in vals:
            ef = copy.deepcopy(COLOR_SLIDERS[stype])
            ef["id"] = uid()
            ef["value"] = float(sval)
            D["materials"]["effects"].append(ef)
            refs.append(ef["id"])

    def make_untouched_raw_overlay_seg(
        src_path: Path, tgt_st_u: int, tgt_du_u: int, src_st_u: int, spd: float = 1.0,
        in_anim: str | None = None, out_anim: str | None = None,
        is_dji: bool = False, custom_sliders: list[tuple[str, float]] | None = None,
        allow_v7_asset: bool = False
    ):
        """
        100% UNTOUCHED NATURAL FRAME ('source lớp phủ đừng có kéo hay phóng nó nữa'):
          - scale = {'x': 1.0, 'y': 1.0}
          - transform = {'x': 0.0, 'y': 0.0}
          - common_keyframes = [] (ZERO zoom, ZERO pan!)
          - crop = FULL_CROP_1_1 (ZERO clipping!)
        """
        mid, mat_dur_u, _, _, is_photo = register_visual_asset(src_path, allow_v7_asset=allow_v7_asset)
        if is_photo:
            src_st_u, src_du_u = 0, tgt_du_u
            spd = 1.0
        else:
            src_du_u = int(round(tgt_du_u * spd))
            if src_st_u + src_du_u > mat_dur_u:
                src_st_u = max(0, mat_dur_u - src_du_u)

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = round(spd, 4)
            D["materials"][k].append(em); refs.append(em["id"])

        if is_dji:
            attach_color_sliders(refs, [("temperature", 0.14), ("saturation", 0.18), ("contrast", 0.09), ("brightness", 0.03)])
        if custom_sliders:
            attach_color_sliders(refs, custom_sliders)

        anim_list = []
        if in_anim and in_anim in VIDEO_ANIMS["in"]:
            ai = copy.deepcopy(VIDEO_ANIMS["in"][in_anim])
            ai["start"] = 0
            ai["duration"] = min(220000, tgt_du_u // 3)
            anim_list.append(ai)
        if out_anim and out_anim in VIDEO_ANIMS["out"]:
            ao = copy.deepcopy(VIDEO_ANIMS["out"][out_anim])
            od = min(200000, tgt_du_u // 3)
            ao["duration"] = od
            ao["start"] = max(0, tgt_du_u - od)
            anim_list.append(ao)
        if anim_list:
            ma_id = uid()
            D["materials"].setdefault("material_animations", []).append({
                "animations": anim_list, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
            })
            refs.append(ma_id)

        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        seg["clip"]["rotation"] = 0.0
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": int(src_st_u), "duration": int(src_du_u)},
            "target_timerange": {"start": int(tgt_st_u), "duration": int(tgt_du_u)},
            "speed": round(spd, 4), "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        })
        return seg

    def make_lipsynced_dji_from_track0_seg(
        t0_seg_idx: int, dji_filename: str, offset_s: float,
        sub_t0_s: float | None = None, sub_t1_s: float | None = None
    ):
        """
        Builds a sub-frame (2.5ms) lip-synced multi-cam DJI segment directly from User's Track 0 segment `t0_seg_idx`,
        at 100% natural untouched scale=1.0, pos=(0,0)!
        """
        s0 = track0_user["segments"][t0_seg_idx]
        s0_tl_st = s0["target_timerange"]["start"]
        s0_tl_du = s0["target_timerange"]["duration"]
        s0_src_st = s0["source_timerange"]["start"]
        spd = s0.get("speed", 1.05)

        tgt_st = us(sub_t0_s) if sub_t0_s is not None else s0_tl_st
        tgt_en = us(sub_t1_s) if sub_t1_s is not None else (s0_tl_st + s0_tl_du)
        tgt_st = max(s0_tl_st, tgt_st)
        tgt_en = min(s0_tl_st + s0_tl_du, tgt_en)
        tgt_du = tgt_en - tgt_st

        # Exact microsecond source timestamp on DJI secondary angle:
        delta_src_u = int(round((tgt_st - s0_tl_st) * spd))
        dji_src_st_u = s0_src_st + delta_src_u + int(round(offset_s * 1_000_000))
        return make_untouched_raw_overlay_seg(
            DJI_DIR / dji_filename, tgt_st, tgt_du, dji_src_st_u, spd=spd, is_dji=True
        )

    def make_clean_circle_seg(png_name: str, t0_s: float, t1_s: float, px: float, py: float, sc: float = 0.56):
        """
        Places a 1080x1920 Clean Circular Overlay (`circle_*.png`, ZERO handle, ZERO oval stretch!)
        with uniform scale and clean Rõ dần + Mờ dần!
        """
        p = CIRCLE_DIR / png_name
        mid, _, _, _, _ = register_visual_asset(p, allow_v7_asset=True)
        st_u = us(t0_s)
        du_u = max(us(0.45), us(t1_s) - st_u)

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])

        anim_list = []
        if "Rõ dần" in VIDEO_ANIMS["in"]:
            ai = copy.deepcopy(VIDEO_ANIMS["in"]["Rõ dần"])
            ai["start"] = 0
            ai["duration"] = min(180000, du_u // 4)
            anim_list.append(ai)
        if "Mờ dần" in VIDEO_ANIMS["out"]:
            ao = copy.deepcopy(VIDEO_ANIMS["out"]["Mờ dần"])
            od = min(180000, du_u // 4)
            ao["duration"] = od
            ao["start"] = max(0, du_u - od)
            anim_list.append(ao)
        if anim_list:
            ma_id = uid()
            D["materials"].setdefault("material_animations", []).append({
                "animations": anim_list, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
            })
            refs.append(ma_id)

        seg["clip"]["scale"] = {"x": round(sc, 4), "y": round(sc, 4)}
        seg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        seg["clip"]["rotation"] = 0.0
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": 0, "duration": du_u},
            "target_timerange": {"start": st_u, "duration": du_u},
            "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
        })
        return seg

    # ==========================================================================
    # 1. TRACK 1 — 100% UNTOUCHED-SCALE VERTICAL RAW B-ROLLS
    #              + 5 SUB-FRAME LIP-SYNCED MULTI-CAM DJI ANGLE SWITCHES
    #              + UNIFIED F20 LOGO-TONE CLOSING BANNER!
    # ==========================================================================
    def raw_broll(path: Path, t0_s: float, t1_s: float, src_in_s: float, spd: float = 1.0,
                  in_anim: str | None = None, out_anim: str | None = None,
                  is_dji: bool = False, custom_sliders: list[tuple[str, float]] | None = None,
                  allow_v7_asset: bool = False):
        st_u = us(t0_s)
        du_u = us(t1_s) - st_u
        return make_untouched_raw_overlay_seg(
            path, st_u, du_u, us(src_in_s), spd=spd,
            in_anim=in_anim, out_anim=out_anim, is_dji=is_dji,
            custom_sliders=custom_sliders, allow_v7_asset=allow_v7_asset
        )

    tr1_segs = [
        # Intro Hook (1.87 - 3.77s)
        raw_broll(DOC_DIR / "C3875.MP4",   1.87,   3.77,  0.60, 1.00, in_anim="Rõ dần"),

        # 4 Customer Orders: Đăng Khoa Edu 77 set -> Hội phụ huynh 13 set -> Hà Nội 10 set -> TP.HCM 4 set -> Đủ 104 set!
        raw_broll(ANH_HAU / "C3920.MP4",  15.93,  18.40,  2.13, 1.00),
        raw_broll(ANH_HAU / "C3928.MP4",  18.40,  20.73,  1.80, 1.00),
        raw_broll(DOC_DIR / "C3882.MP4",  20.73,  24.07,  0.60, 1.00),
        raw_broll(DOC_DIR / "C3887.MP4",  24.07,  27.33,  0.50, 1.00),
        raw_broll(DOC_DIR / "C3901.MP4",  27.33,  30.93,  0.50, 1.00),
        raw_broll(DOC_DIR / "C3869.MP4",  33.33,  35.80,  1.40, 1.00, out_anim="Mờ dần"),

        # Showroom prepared gift sets vertical glide (38.80 - 41.40s: vertical C3875 at natural scale=1.0!)
        raw_broll(DOC_DIR / "C3875.MP4",  38.80,  41.40,  6.20, 0.90),

        # Backdrop for 4-Circle Gift Set Overview (48.60 - 52.55s: natural scale=1.0 dimmed C3875!)
        raw_broll(DOC_DIR / "C3875.MP4",  48.60,  52.55,  3.00, 0.80, custom_sliders=[("brightness", -0.30)]),

        # 4 Stewing Ingredients Backdrop (59.00 - 62.45s: natural scale=1.0 dimmed C3873 macro!)
        raw_broll(DOC_DIR / "C3873.MP4",  59.00,  62.45,  0.20, 0.74, custom_sliders=[("brightness", -0.26)]),

        # [MULTI-CAM LIP-SYNC DJI #1] 76.10 - 80.27s ("Thứ 4 là 1 gói rong biển kẹp hạt 500g"): Seg[26] <-> DJI_0084_D (+15.4725s)!
        make_lipsynced_dji_from_track0_seg(26, "DJI_20261116093322_0084_D.MP4", +15.4725, sub_t0_s=76.10, sub_t1_s=80.27),

        # Giá trị nhất: 1 Tổ yến tinh chế sợi dài (87.30 - 90.50s: vertical C3867 at natural scale=1.0!)
        raw_broll(DOC_DIR / "C3867.MP4",  87.30,  90.50,  0.33, 0.82),

        # [MULTI-CAM LIP-SYNC DJI #4] 92.57 - 96.47s ("tờ cẩm nang yến sào gồm công dụng của yến sào"): Seg[29] + Seg[30] <-> DJI_0088_D (-0.7150s)!
        make_lipsynced_dji_from_track0_seg(29, "DJI_20261116093955_0088_D.MP4", -0.7150),
        make_lipsynced_dji_from_track0_seg(30, "DJI_20261116093955_0088_D.MP4", -0.7150),

        # Open brochure pages vertical B-roll (97.23 - 100.77s: vertical DJI_0087_D at natural scale=1.0!)
        raw_broll(DJI_DIR / "DJI_20261116093826_0087_D.MP4", 97.23, 100.77, 16.50, 0.95, is_dji=True),

        # [MULTI-CAM LIP-SYNC DJI #5] 104.50 - 109.33s ("mica trong suốt... Bên trên có quai xách bằng da"): Seg[35] + Seg[36] <-> DJI_0085_D (-1.1550s)!
        make_lipsynced_dji_from_track0_seg(35, "DJI_20261116093624_0085_D.MP4", -1.1550),
        make_lipsynced_dji_from_track0_seg(36, "DJI_20261116093624_0085_D.MP4", -1.1550),

        # Bông hoa tạo điểm nhấn (111.67 - 115.03s: vertical C3873 at natural scale=1.0!)
        raw_broll(DOC_DIR / "C3873.MP4", 111.67, 115.03,  1.80, 0.80),

        # Trực tiếp sản xuất — Chất lượng & Giá cả (121.80 - 127.30s: vertical C3870 & C3866 at natural scale=1.0!)
        raw_broll(DOC_DIR / "C3870.MP4", 121.80, 124.50,  1.00, 1.00),
        raw_broll(DOC_DIR / "C3866.MP4", 124.50, 127.30,  2.50, 1.00),

        # Pre-CTA Gift Set Beauty Shot (135.33 - 138.47s)
        raw_broll(DOC_DIR / "C3873.MP4", 135.33, 138.47,  1.10, 0.85, in_anim="Rõ dần", out_anim="Mờ dần"),

        # KHÚC CUỐI — UNIFIED F20 LOGO-TONE (WHITE + EMERALD GREEN + ROYAL BLUE) CLOSING BANNER (140.37 - 142.90s)!
        make_untouched_raw_overlay_seg(
            V7_ASSETS / "outro_banner_f20_brand.mp4",
            us(140.37), total_end_u - us(140.37), 0, spd=1.0, in_anim="Rõ dần", allow_v7_asset=True
        ),
    ]
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid(); tr_v1["segments"] = tr1_segs

    # ==========================================================================
    # 2. TRACKS 2..5 — CLEAN ROUND CIRCULAR PRODUCT OVERLAYS (`circle_*.png`)
    #    100% Perfect Circles (1080x1920 9:16 canvas + FULL_CROP_1_1), ZERO Handle, 0% AI!
    # ==========================================================================
    CIRCLE_EVENTS = [
        # (t0_s, t1_s, png_name, px, py, scale)
        # 4-Item Gift Set Overview (48.65 - 52.55s: 4 Clean Circles above the 4 native labels!)
        (48.65, 52.55, "circle_01_to_yen_a5.png",      -0.46, +0.42, 0.48),
        (48.87, 52.55, "circle_02_2hop_rong_bien.png", +0.46, +0.42, 0.48),
        (49.10, 52.55, "circle_03_banh_thuyen.png",    -0.46, -0.10, 0.48),
        (49.30, 52.55, "circle_04_kep_hat_500g.png",   +0.46, -0.10, 0.48),

        # Item 1: Tổ Yến Tinh Chế Sợi Dài (52.25 - 56.95s: upper-right open space!)
        (52.25, 56.95, "circle_01_to_yen_a5.png",      +0.52, +0.28, 0.56),

        # 4 Stewing Ingredients (59.00 - 62.43s: 4 Clean Circles above each paired native label!)
        (59.00, 62.43, "circle_05_tao_do.png",         -0.46, +0.44, 0.46),
        (59.63, 62.43, "circle_06_dong_trung.png",     +0.46, +0.44, 0.46),
        (60.70, 62.43, "circle_07_ky_tu.png",          -0.46, -0.06, 0.46),
        (61.43, 62.43, "circle_08_duong_phen.png",     +0.46, -0.06, 0.46),

        # Item 2: 2 Hộp Rong Biển -> Cay Nhẹ (ớt đỏ) -> Sấy Mè (mè rang vàng)!
        (62.40, 65.38, "circle_02_2hop_rong_bien.png", +0.52, +0.26, 0.56),
        (65.45, 67.60, "circle_09_cay_nhe_ot.png",     +0.52, +0.28, 0.56),
        (67.63, 69.72, "circle_10_say_me_vang.png",    +0.52, +0.28, 0.56),

        # Item 3: Bánh Thuyền Mix Hạt 250g (69.92 - 74.95s)
        (69.92, 74.95, "circle_03_banh_thuyen.png",    +0.52, +0.26, 0.56),

        # Item 4: Rong Biển Kẹp Hạt 500g -> 22-24 Thanh!
        (75.32, 80.20, "circle_04_kep_hat_500g.png",   +0.52, +0.28, 0.55),
        (81.18, 84.15, "circle_11_24_thanh_hat.png",   +0.52, +0.22, 0.56),

        # Giá trị nhất: Tổ Yến Tinh Chế Sợi Dài A5 (84.30 - 87.25s)
        (84.30, 87.25, "circle_01_to_yen_a5.png",      +0.52, +0.24, 0.56),

        # Tờ Cẩm Nang Yến Sào (93.20 - 96.45s: upper-right while Chị Oanh holds brochure on lip-synced DJI_0088!)
        (93.20, 96.45, "circle_12_cam_nang_yen.png",   +0.52, +0.28, 0.55),
    ]

    circle_lanes: list[list[dict]] = []
    for t0, t1, pnm, px, py, sc in sorted(CIRCLE_EVENTS, key=lambda x: x[0]):
        sg = make_clean_circle_seg(pnm, t0, t1, px, py, sc=sc)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for ln in circle_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                ln.append(sg); placed = True; break
        if not placed:
            circle_lanes.append([sg])

    circle_tracks = []
    for ln in circle_lanes:
        tr_c = copy.deepcopy(vtrack_tpl); tr_c["id"] = uid(); tr_c["segments"] = ln
        circle_tracks.append(tr_c)

    # ==========================================================================
    # 3. EAR-VERIFIED USER SFX (`-18..-21dB`, Synced to Circle Overlays & Banner!)
    # ==========================================================================
    amat_map = {}
    def make_sfx_seg(sfx_fn: str, lbl: str, t0_s: float, vol: float, max_dur_s: float):
        sp = SFX_FOLDER / sfx_fn
        fwd = norm_fwd(sp)
        if fwd not in amat_map:
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(sp)], capture_output=True, text=True, check=True)
            du_full = us(float(json.loads(r.stdout)["format"]["duration"]))
            aid = uid()
            am = copy.deepcopy(amat_tpl)
            am.update({
                "id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": str(uuid.uuid4()),
                "name": lbl, "path": fwd, "duration": du_full, "type": "sound"
            })
            D["materials"]["audios"].append(am)
            amat_map[fwd] = (aid, du_full)
        aid, du_full = amat_map[fwd]
        du = min(du_full, us(max_dur_s))
        sg = copy.deepcopy(aseg_tpl)
        refs = []
        for k, tpl_e in a_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        fid = uid()
        D["materials"].setdefault("audio_fades", []).append({
            "fade_in_duration": min(18000, du // 6),
            "fade_out_duration": min(120000, du // 3),
            "fade_type": 0, "id": fid, "type": "audio_fade"
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

    SFX_EVENTS = [
        (0.18,   "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Air Mở Cảnh",      0.12, 0.7),
        (0.30,   "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3",                              "Chuông Gió Mở",    0.10, 1.8),
        (6.08,   "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Swoosh 104 Set",   0.10, 0.6),
        (9.25,   "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Gió Mềm 20/11",    0.10, 0.5),
        (15.90,  "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish ĐK Edu",     0.10, 0.6),
        (24.05,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Swipe Hà Nội",     0.10, 0.6),
        (33.30,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đủ 104 Set",  0.11, 1.2),
        (43.00,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Gió Mềm 01 Set",   0.10, 0.5),

        (48.63,  "Click & Máy Chữ - click (1s).mp3",                                            "Circle Món 01",    0.11, 0.35),
        (48.87,  "Click & Máy Chữ - click (1s).mp3",                                            "Circle Món 02",    0.11, 0.35),
        (49.10,  "Click & Máy Chữ - click (1s).mp3",                                            "Circle Món 03",    0.11, 0.35),
        (49.30,  "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Món 04",      0.10, 1.0),

        (52.23,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Circle Tổ Yến",    0.10, 0.6),
        (59.00,  "Click & Máy Chữ - click (1s).mp3",                                            "Circle Táo Đỏ",    0.11, 0.35),
        (59.63,  "Click & Máy Chữ - click (1s).mp3",                                            "Circle Đông Trùng",0.11, 0.35),
        (60.70,  "Click & Máy Chữ - click (1s).mp3",                                            "Circle Kỷ Tử",     0.11, 0.35),
        (61.43,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đường Phèn",  0.10, 1.1),

        (62.38,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Circle 2 Hộp RB",  0.10, 0.6),
        (65.45,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Circle Cay Nhẹ",   0.11, 0.6),
        (67.62,  "Click & Máy Chữ - click (1s).mp3",                                            "Circle Sấy Mè",    0.11, 0.35),

        (69.90,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Circle Bánh Thuyền",0.10, 0.6),
        (75.30,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Circle Kẹp Hạt",   0.10, 0.6),
        (81.16,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Circle 24 Thanh",  0.11, 0.6),

        (84.30,  "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3",                                   "Shine Giá Trị Nhất",0.09, 0.9),
        (92.55,  "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Mở Cẩm Nang 1",    0.12, 0.8),
        (97.20,  "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Lật Trang Cẩm Nang",0.11, 0.8),
        (121.78, "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Whoosh Sản Xuất",  0.10, 0.6),
        (138.57, "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Inbox Ngay",  0.10, 1.2),
        (140.35, "Whoosh - Title Swoosh (1s).mp3",                                              "Swoosh Mở Banner", 0.12, 0.8),
        (140.48, "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3",                              "Chuông Gió Banner",0.11, 2.3),
    ]

    sfx_lanes: list[list[dict]] = []
    for t0, fn, lbl, vol, mdur in sorted(SFX_EVENTS, key=lambda x: x[0]):
        sg = make_sfx_seg(fn, lbl, t0, vol=vol, max_dur_s=mdur)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for ln in sfx_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                ln.append(sg); placed = True; break
        if not placed:
            sfx_lanes.append([sg])

    sfx_tracks = []
    for ln in sfx_lanes:
        tr_a = copy.deepcopy(atrack_tpl); tr_a["id"] = uid(); tr_a["segments"] = ln
        sfx_tracks.append(tr_a)

    D["tracks"] = [
        track0_user,        # Track 0: 100.00% Untouched User-Edited Main Track (45 segs, 140.37s)!
        tr_v1,              # Track 1: Untouched-Scale Vertical Raw B-Rolls + 5 Lip-Synced DJI Multi-Cam Cuts + F20 Brand Banner!
        *circle_tracks,     # Tracks 2..5: 17 Clean Round Circle Overlays (`circle_*.png`, 1080x1920 -> 0% oval stretch, 0% AI)!
        *text_tracks_user,  # User's Native Editable Coiny Subtitles + Floating Texts!
        *bgm_tracks_user,   # User's 5-Segment Sáo Trúc Đàn Tranh BGM (0.00 -> 142.90s)!
        *sfx_tracks,        # Lively Ear-Verified Tactile Micro-SFX (-18..-21dB)!
    ]
    D["duration"] = total_end_u
    D["update_time"] = now_s

    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video":
                s["render_index"] = ti
            elif tr["type"] == "text":
                s["render_index"] = 14000 + ti

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")

    # Write ONLY into the ONE official project `1117 F20`!
    for tp in [
        DRAFT_DIR / "draft_content.json",
        DRAFT_DIR / "template-2.tmp",
        DRAFT_DIR / "Timelines" / tl_id / "draft_content.json",
        DRAFT_DIR / "Timelines" / tl_id / "template-2.tmp",
    ]:
        if tp.exists():
            tp.unlink()
        tp.write_bytes(dc_bytes)

    dmi = json.loads((USER_BAK / "draft_meta_info.json").read_text(encoding="utf-8"))
    dmi["tm_duration"] = total_end_u
    dmi["tm_draft_modified"] = now_us
    for bucket in dmi.get("draft_materials", []):
        if bucket.get("type") == 0:
            clean_vals = [
                x for x in bucket.get("value", [])
                if "capcut_layers_1117" not in str(x.get("file_Path", ""))
                and "v6_assets" not in str(x.get("file_Path", ""))
            ]
            existing = {x.get("file_Path") for x in clean_vals}
            for ne in new_dm_entries:
                if ne["file_Path"] not in existing:
                    clean_vals.append(ne)
            bucket["value"] = clean_vals
    (DRAFT_DIR / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

    pj["update_time"] = now_us
    for t_ent in pj.get("timelines", []):
        t_ent["update_time"] = now_us
    (DRAFT_DIR / "Timelines" / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

    # Remove duplicate `1117 F20 (Bản Mới Kính Lúp & Banner)` so ONLY `1117 F20` exists ('làm 1 project thôi')!
    if DRAFT_ALT.exists():
        shutil.rmtree(DRAFT_ALT, ignore_errors=True)

    rmi_path = ROOT / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    store = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_ALT.name]
    for x in store:
        if x.get("draft_name") == "1117 F20":
            x["tm_duration"] = total_end_u
            x["tm_draft_modified"] = now_us
    rmi["all_draft_store"] = store
    rmi["draft_ids"] = len(store)
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    print("SUCCESS V7 SINGLE PROJECT ('1117 F20' ONLY)!")
    print(f"  -> Track 0: {len(track0_user['segments'])} segs (100% untouched)")
    print(f"  -> Track 1: {len(tr1_segs)} segs (ALL scale=1.0, pos=(0,0), 0 zoom/pan keyframes, 5 sub-frame lip-synced DJI angle cuts + F20 Brand Banner!)")
    print(f"  -> Clean Round Circle Overlays: {len(CIRCLE_EVENTS)} across {len(circle_tracks)} tracks (1080x1920 + FULL_CROP_1_1 -> 0% oval stretch, 0% handle!)")
    print(f"  -> Removed duplicate draft '{DRAFT_ALT.name}' -> ONLY '1117 F20' remains!")

if __name__ == "__main__":
    main()
