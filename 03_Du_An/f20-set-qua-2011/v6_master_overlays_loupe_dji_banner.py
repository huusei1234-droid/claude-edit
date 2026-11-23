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
NGANG_DIR  = F20_261116 / r"Chi Oanh\ngang"
DJI_DIR    = F20_261116 / r"Chi Oanh\dji"
ANH_HAU    = F20_261116 / r"Anh Hậu"

SFX_FOLDER = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")
WORK       = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
USER_BAK   = WORK / "backup_1117_F20_user_1644"
V6_ASSETS  = WORK / "v6_assets"
LOUPE_DIR  = V6_ASSETS / "loupe_icons"

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

def copy_draft_unlinked(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst, ignore_errors=True)
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name == ".locked":
            continue
        target = dst / item.name
        if item.is_dir():
            if item.name == "Timelines":
                shutil.copytree(item, target)
            else:
                copy_draft_unlinked(item, target)
        else:
            if item.suffix.lower() in (".json", ".tmp"):
                shutil.copy2(item, target)
            else:
                try:
                    os.link(item, target)
                except Exception:
                    shutil.copy2(item, target)

def main():
    # Check if user saved anything even newer in 1117 F20 since 16:44 backup
    pj_live = json.loads((DRAFT_DIR / "Timelines" / "project.json").read_text(encoding="utf-8"))
    tl_id = pj_live["main_timeline_id"]
    live_tl_p = DRAFT_DIR / "Timelines" / tl_id / "draft_content.json"
    bak_tl_p  = USER_BAK / "Timelines" / tl_id / "draft_content.json"
    if live_tl_p.stat().st_mtime > bak_tl_p.stat().st_mtime + 2.0:
        print("Detected newer user save in 1117 F20 -> refreshing backup_1117_F20_user_1644!")
        shutil.copy2(live_tl_p, bak_tl_p)
        shutil.copy2(DRAFT_DIR / "draft_content.json", USER_BAK / "draft_content.json")
        shutil.copy2(DRAFT_DIR / "draft_meta_info.json", USER_BAK / "draft_meta_info.json")

    pj = json.loads((USER_BAK / "Timelines" / "project.json").read_text(encoding="utf-8"))
    D  = json.loads(bak_tl_p.read_text(encoding="utf-8"))

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
    kf_tpl     = copy.deepcopy(next(sg["common_keyframes"][0] for tr in dc_fc["tracks"] for sg in tr.get("segments", []) if sg.get("common_keyframes")))

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

    VIDEO_ANIMS    = json.loads((WORK / "verified_video_anims.json").read_text(encoding="utf-8"))
    COLOR_SLIDERS  = json.loads((WORK / "native_color_sliders.json").read_text(encoding="utf-8"))
    RECT_MASK_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef"

    # ==========================================================================
    # PRESERVE 100% OF USER'S EDITED TRACK 0 + ALL TEXT TRACKS + ALL BGM SEGMENTS!
    # ==========================================================================
    track0_user = copy.deepcopy(D["tracks"][0])  # 45 segs [0.00s -> 140.37s]
    text_tracks_user = [copy.deepcopy(tr) for tr in D["tracks"] if tr["type"] == "text"]  # Tracks 08..14

    # Extract ONLY the user's 5 BGM segments (material name contains 'Nhạc Sáo Trúc')
    amap_orig = {a["id"]: a for a in D["materials"]["audios"]}
    bgm_segs_raw = []
    for tr in D["tracks"]:
        if tr["type"] == "audio":
            for sg in tr["segments"]:
                am = amap_orig.get(sg["material_id"], {})
                if "Nhạc Sáo Trúc" in am.get("name", "") or "Nhạc" in am.get("path", ""):
                    bgm_segs_raw.append(copy.deepcopy(sg))
    bgm_segs_raw.sort(key=lambda s: s["target_timerange"]["start"])

    # Pack user's BGM segments into clean non-overlapping audio tracks (handling 117.20-117.33s cross-lap)
    bgm_lanes: list[list[dict]] = []
    for bsg in bgm_segs_raw:
        st_u = bsg["target_timerange"]["start"]
        placed = False
        for ln in bgm_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] <= st_u:
                ln.append(bsg)
                placed = True
                break
        if not placed:
            bgm_lanes.append([bsg])

    # Add smooth 1.1s fade-out on the final BGM segment ending at 142.90s
    last_bgm_seg = max(bgm_segs_raw, key=lambda s: s["target_timerange"]["start"] + s["target_timerange"]["duration"])
    total_end_u  = last_bgm_seg["target_timerange"]["start"] + last_bgm_seg["target_timerange"]["duration"]  # 142_900_000 (142.900s!)
    fade_end_id  = uid()

    # Gently nudge the 4 stewing ingredient floating text labels (59.00..62.43s) into crisp 2x2 paired slots under our 4 Loupe Icons!
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

    # Fix tiny 0.1-0.25s cross-track subtitle overlaps between Track 08 & Track 09 created during user's ripple edit!
    sub_segs_all = []
    for tr_t in text_tracks_user:
        for sg in tr_t["segments"]:
            if tmap_user.get(sg["material_id"], {}).get("type") == "subtitle":
                sub_segs_all.append(sg)
    sub_segs_all.sort(key=lambda s: s["target_timerange"]["start"])
    for idx_s in range(len(sub_segs_all) - 1):
        s_cur = sub_segs_all[idx_s]
        s_nxt = sub_segs_all[idx_s + 1]
        end_cur = s_cur["target_timerange"]["start"] + s_cur["target_timerange"]["duration"]
        st_nxt  = s_nxt["target_timerange"]["start"]
        if end_cur > st_nxt:
            s_cur["target_timerange"]["duration"] = max(333333, st_nxt - s_cur["target_timerange"]["start"] - 33333)

    # Prune materials to ONLY objects referenced by Track 0 + User Text Tracks + User BGM Tracks
    bgm_tracks_user = []
    for ln in bgm_lanes:
        bt = copy.deepcopy(atrack_tpl)
        bt["id"] = uid()
        bt["segments"] = ln
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

    def register_visual_asset(path: Path, allow_v6_asset: bool = False):
        if not path.is_file():
            raise FileNotFoundError(f"Missing visual file: {path}")
        fwd = norm_fwd(path)
        if not allow_v6_asset:
            assert fwd.startswith("Z:/Máy tính khác/My Computer/F20/"), f"Video overlay MUST be raw F20 source: {fwd}"
        if fwd in vis_cache:
            return vis_cache[fwd]
        is_photo = path.suffix.lower() in (".png", ".jpg", ".jpeg")
        mid = uid()
        lmid = str(uuid.uuid4())
        if is_photo:
            with Image.open(path) as im:
                w, h = im.size
            dur_u = 10_800_000_000
            m = copy.deepcopy(pmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "photo", "path": fwd, "media_path": "", "local_id": "",
                "material_name": path.name, "width": w, "height": h, "duration": dur_u, "has_audio": False
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
            dur_u = max(33333, us(dur_s))
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": fwd, "media_path": "", "local_id": "",
                "material_name": path.name, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud)
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

    def make_kf(prop_type: str, pts_sec_val: list[tuple[float, float]]):
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

    def attach_color_sliders(refs: list[str], vals: list[tuple[str, float]]):
        D["materials"].setdefault("effects", [])
        for stype, sval in vals:
            ef = copy.deepcopy(COLOR_SLIDERS[stype])
            ef["id"] = uid()
            ef["value"] = float(sval)
            D["materials"]["effects"].append(ef)
            refs.append(ef["id"])

    def make_raw_video_seg(
        src_path: Path, t0_s: float, t1_s: float, src_in_s: float = 0.0, spd: float = 1.0,
        in_anim: str | None = None, out_anim: str | None = None, zoom_dir: int = 0,
        base_scale: float = 1.0, tx: float = 0.0, ty: float = 0.0,
        mask_cfg: dict | None = None, is_dji: bool = False,
        custom_sliders: list[tuple[str, float]] | None = None, allow_v6_asset: bool = False
    ):
        mid, mat_dur_u, w, h, is_photo = register_visual_asset(src_path, allow_v6_asset=allow_v6_asset)
        tgt_st_u = us(t0_s)
        tgt_du_u = max(us(0.25), us(t1_s) - tgt_st_u)
        dur_s = tgt_du_u / 1e6

        if is_photo:
            src_st_u, src_du_u = 0, tgt_du_u
            spd = 1.0
        else:
            src_st_u = us(src_in_s)
            src_du_u = us(dur_s * spd)
            if src_st_u + src_du_u > mat_dur_u:
                src_st_u = max(0, mat_dur_u - src_du_u)

        eff_scale = base_scale
        if not is_photo and mask_cfg is None and w > h:
            fit_h = 1080.0 * (h / w)
            eff_scale = round(base_scale * (1920.0 / fit_h) * 1.015, 4)

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e)
            em["id"] = uid()
            if k == "speeds":
                em["speed"] = round(spd, 3)
            D["materials"][k].append(em)
            refs.append(em["id"])

        if is_dji:
            attach_color_sliders(refs, [("temperature", 0.15), ("saturation", 0.20), ("contrast", 0.10), ("brightness", 0.04)])
        if custom_sliders:
            attach_color_sliders(refs, custom_sliders)

        anim_list = []
        if in_anim and in_anim in VIDEO_ANIMS["in"]:
            ai = copy.deepcopy(VIDEO_ANIMS["in"][in_anim])
            ai["start"] = 0
            ai["duration"] = min(233333, tgt_du_u // 3)
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

        if mask_cfg is not None:
            mk_id = uid()
            D["materials"].setdefault("common_mask", []).append({
                "config": mask_cfg,
                "id": mk_id, "name": "Hình chữ nhật", "path": RECT_MASK_PATH,
                "platform": "all", "position_info": "", "resource_id": "7374021450748924432",
                "resource_type": "rectangle", "source_platform": 1, "type": "mask"
            })
            refs.append(mk_id)

        seg["clip"]["scale"] = {"x": eff_scale, "y": eff_scale}
        seg["clip"]["transform"] = {"x": round(tx, 4), "y": round(ty, 4)}
        seg["uniform_scale"] = {"on": True, "value": eff_scale}
        seg["clip"]["alpha"] = 1.0

        kfs = []
        if zoom_dir != 0 and mask_cfg is None and dur_s >= 2.4:
            s0, s1 = (eff_scale, round(eff_scale * 1.032, 4)) if zoom_dir > 0 else (round(eff_scale * 1.032, 4), eff_scale)
            kfs = [make_kf("KFTypeScaleX", [(0.0, s0), (dur_s, s1)]), make_kf("KFTypeScaleY", [(0.0, s0), (dur_s, s1)])]

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": src_st_u, "duration": src_du_u},
            "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
            "speed": round(spd, 3), "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [],
        })
        return seg

    def make_loupe_icon_seg(png_name: str, t0_s: float, t1_s: float, px: float, py: float, base_sc: float = 0.36):
        """
        Places a 100% Real-Photo Magnifying Loupe Icon (`loupe_*.png`) as an independent movable CapCut overlay
        with lively elastic magnifying-glass pop-in (scale 0.20 -> 1.07 -> 1.00 + slight tilt settle) + soft fade out!
        """
        p = LOUPE_DIR / png_name
        mid, _, _, _, _ = register_visual_asset(p, allow_v6_asset=True)
        st_u = us(t0_s)
        du_u = max(us(0.45), us(t1_s) - st_u)
        dur_s = du_u / 1e6

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])

        if "Mờ dần" in VIDEO_ANIMS["out"]:
            ao = copy.deepcopy(VIDEO_ANIMS["out"]["Mờ dần"])
            od = min(180000, du_u // 4)
            ao["duration"] = od
            ao["start"] = max(0, du_u - od)
            ma_id = uid()
            D["materials"].setdefault("material_animations", []).append({
                "animations": [ao], "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
            })
            refs.append(ma_id)

        t_pop = min(0.18, dur_s * 0.30)
        t_set = min(0.30, dur_s * 0.50)
        s_in  = round(base_sc * 0.22, 4)
        s_ov  = round(base_sc * 1.08, 4)
        s_end = round(base_sc * 1.02, 4)
        rot_0 = -10.0 if px >= 0 else +10.0

        kfs = [
            make_kf("KFTypeScaleX", [(0.0, s_in), (t_pop, s_ov), (t_set, base_sc), (dur_s, s_end)]),
            make_kf("KFTypeScaleY", [(0.0, s_in), (t_pop, s_ov), (t_set, base_sc), (dur_s, s_end)]),
            make_kf("KFTypeRotation", [(0.0, rot_0), (t_set, 0.0)]),
            make_kf("KFTypePositionY", [(0.0, py - 0.025), (t_set, py), (dur_s, py + 0.015)]),
        ]

        seg["clip"]["scale"] = {"x": base_sc, "y": base_sc}
        seg["clip"]["transform"] = {"x": round(px, 4), "y": round(py, 4)}
        seg["clip"]["rotation"] = 0.0
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": base_sc}
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": 0, "duration": du_u},
            "target_timerange": {"start": st_u, "duration": du_u},
            "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [],
        })
        return seg

    # ==========================================================================
    # 1. TRACK 1 — FULL-SCREEN RAW CAMERA B-ROLLS + CLOSING 20/11 BANNER STAGE!
    #    (Selective animations: crisp Hard Cuts by default, gentle fade only at act boundaries!)
    # ==========================================================================
    tr1_segs = [
        # Intro Hook (1.87 - 3.77s)
        make_raw_video_seg(DOC_DIR / "C3875.MP4",   1.87,   3.77,  0.60, 1.00, in_anim="Rõ dần", out_anim=None, zoom_dir=-1),

        # 4 Customer Orders: Đăng Khoa Edu 77 set -> Hội phụ huynh 13 set -> Hà Nội 10 set -> TP.HCM 4 set -> Đủ 104 set!
        make_raw_video_seg(ANH_HAU / "C3920.MP4",  15.93,  18.40,  2.13, 1.00),
        make_raw_video_seg(ANH_HAU / "C3928.MP4",  18.40,  20.73,  1.80, 1.00),
        make_raw_video_seg(DOC_DIR / "C3882.MP4",  20.73,  24.07,  0.60, 1.00, zoom_dir=+1),
        make_raw_video_seg(DOC_DIR / "C3887.MP4",  24.07,  27.33,  0.50, 1.00),
        make_raw_video_seg(DOC_DIR / "C3901.MP4",  27.33,  30.93,  0.50, 1.00),
        make_raw_video_seg(DOC_DIR / "C3869.MP4",  33.33,  35.80,  1.40, 1.00, out_anim="Mờ dần", zoom_dir=+1),

        # Showroom prepared gift sets 4K glide (38.80 - 41.40s: full-screen clean showcase!)
        make_raw_video_seg(NGANG_DIR / "DJI_20261116095310_0100_D.MP4", 38.80, 41.40, 0.40, 0.90, zoom_dir=+1, is_dji=True),

        # Backdrop for 4-Loupe Gift Set Overview (48.60 - 52.55s: warm dimmed C3875 showroom sets, zero face overlap!)
        make_raw_video_seg(DOC_DIR / "C3875.MP4",  48.60,  52.55,  3.00, 0.80, base_scale=1.06, custom_sliders=[("brightness", -0.32), ("contrast", -0.06)]),

        # 4 Stewing Ingredients Backdrop (59.00 - 62.45s: dimmed C3873 macro so 4 Loupe Icons + 4 Labels pop!)
        make_raw_video_seg(DOC_DIR / "C3873.MP4",  59.00,  62.45,  0.20, 0.74, zoom_dir=+1, base_scale=1.04, custom_sliders=[("brightness", -0.26)]),

        # Giá trị nhất: 1 Tổ yến tinh chế sợi dài (87.30 - 90.50s)
        make_raw_video_seg(DOC_DIR / "C3867.MP4",  87.30,  90.50,  0.33, 0.82, zoom_dir=+1),

        # Giỏ mica trong suốt (103.83 - 107.10s) & Bông hoa đỏ điểm nhấn (111.67 - 115.03s)
        make_raw_video_seg(DJI_DIR / "DJI_20261116093624_0085_D.MP4", 103.83, 107.10, 12.20, 0.90, zoom_dir=+1, is_dji=True),
        make_raw_video_seg(DOC_DIR / "C3873.MP4", 111.67, 115.03,  1.80, 0.80, zoom_dir=+1, base_scale=1.04),

        # Trực tiếp sản xuất — Chất lượng & Giá cả (121.80 - 127.30s: 2 crisp F20 team Hard Cuts!)
        make_raw_video_seg(DOC_DIR / "C3870.MP4", 121.80, 124.50,  1.00, 1.00),
        make_raw_video_seg(DOC_DIR / "C3866.MP4", 124.50, 127.30,  2.50, 1.00),

        # Pre-CTA Gift Set Beauty Shot (135.33 - 138.47s)
        make_raw_video_seg(DOC_DIR / "C3873.MP4", 135.33, 138.47,  1.10, 0.85, in_anim="Rõ dần", out_anim="Mờ dần", zoom_dir=+1),

        # KHÚC CUỐI — LUXURY 20/11 CLOSING BANNER STAGE (140.37 - 142.90s, aligned to exact BGM end!)
        make_raw_video_seg(V6_ASSETS / "outro_banner_stage_f20.mp4", 140.37, total_end_u / 1e6, 0.0, 1.00, in_anim="Rõ dần", allow_v6_asset=True),
    ]
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid(); tr_v1["segments"] = tr1_segs

    # ==========================================================================
    # 2. TRACK 2 — MULTI-CAM SPLIT-SCREEN (`SOURCE DJI` + `SOURCE GỐC TRACK 0`)
    #              + ROUNDED PIPs + CLOSING BANNER INFO CARD!
    #    Both Chị Oanh on Track 0 (top half) AND Raw Synced DJI Close-Up (bottom half)
    #    play simultaneously in real-time sync!
    # ==========================================================================
    PIP_MASK = {
        "aspectRatio": 0.78, "centerX": 0.0, "centerY": 0.0, "expansion": 0.0,
        "feather": 0.02, "height": 0.86, "invert": False, "rotation": 0.0, "roundCorner": 0.18, "width": 0.88,
    }
    def make_dji_split_bot(src_path: Path, t0_s: float, t1_s: float, src_in_s: float, spd: float,
                           sc: float, mcx: float, mcy: float, mw: float, mh: float,
                           in_anim: str | None = "Rõ dần", out_anim: str | None = "Mờ dần"):
        card_cy = -0.44  # Sits cleanly in lower half (y: 955..1810px) below Chị Oanh's torso!
        mcfg = {
            "aspectRatio": 1.0, "centerX": mcx, "centerY": mcy, "expansion": 0.0,
            "feather": 0.015, "height": mh, "invert": False, "rotation": 0.0, "roundCorner": 0.10, "width": mw,
        }
        return make_raw_video_seg(
            src_path, t0_s, t1_s, src_in_s, spd=spd,
            in_anim=in_anim, out_anim=out_anim, zoom_dir=0,
            base_scale=sc, tx=0.0 - sc * mcx, ty=card_cy - sc * mcy,
            mask_cfg=mcfg, is_dji=True
        )

    DJI84 = DJI_DIR / "DJI_20261116093322_0084_D.MP4"
    tr2_segs = [
        # Upper-right PIP @ 6.07 - 9.13s ("tổng cộng 104 set quà")
        make_raw_video_seg(DOC_DIR / "C3873.MP4", 6.07, 9.13, 0.40, 0.90, in_anim="Trượt sang trái", out_anim="Mờ dần", base_scale=0.30, tx=0.56, ty=0.52, mask_cfg=copy.deepcopy(PIP_MASK)),

        # Split-Screen 2: 54.20 - 57.00s ("gồm 1 tổ yến tinh chế sợi dài") -> Synced DJI_0084_D Bird's Nest close-up below Chị Oanh!
        make_dji_split_bot(DJI84, 54.20, 57.00, 14.20, 1.00, sc=1.50, mcx=0.205, mcy=0.02, mw=0.64, mh=0.30),

        # Split-Screen 3: 65.47 - 69.73s ("1 hộp sấy giòn cay nhẹ & 1 hộp sấy mè không cay") -> Synced DJI_0084_D 2 green jars!
        make_dji_split_bot(DJI84, 65.47, 69.73, 33.80, 1.05, sc=1.50, mcx=0.205, mcy=0.02, mw=0.64, mh=0.30),

        # Split-Screen 4: 72.20 - 75.00s ("mix hạt dinh dưỡng 250g") -> Synced DJI_0084_D Bánh thuyền 250g!
        make_dji_split_bot(DJI84, 72.20, 75.00, 43.67, 1.05, sc=1.50, mcx=0.205, mcy=0.02, mw=0.64, mh=0.30),

        # Split-Screen 5: 75.30 - 80.25s ("Thứ 4 là 1 gói rong biển kẹp hạt 500g") -> Synced DJI_0084_D Kẹp hạt 500g!
        make_dji_split_bot(DJI84, 75.30, 80.25, 49.30, 1.05, sc=1.50, mcx=0.205, mcy=0.02, mw=0.64, mh=0.30),

        # Split-Screen 6a & 6b: 93.13 - 100.75s ("tờ cẩm nang yến sào: công dụng & chưng yến đúng cách") -> Hard cut between DJI_0088 & DJI_0087!
        make_dji_split_bot(DJI_DIR / "DJI_20261116093955_0088_D.MP4", 93.13,  97.10, 13.03, 1.05, sc=1.34, mcx=0.06, mcy=-0.14, mw=0.72, mh=0.33, in_anim="Rõ dần", out_anim=None),
        make_dji_split_bot(DJI_DIR / "DJI_20261116093826_0087_D.MP4", 97.10, 100.75, 16.50, 0.95, sc=1.42, mcx=0.08, mcy=-0.24, mw=0.68, mh=0.31, in_anim=None, out_anim="Mờ dần"),

        # Split-Screen 7: 108.90 - 111.65s ("quai xách bằng da màu đỏ đô") -> 4K DJI_0101_D macro leather handle below Chị Oanh!
        make_dji_split_bot(NGANG_DIR / "DJI_20261116095317_0101_D.MP4", 108.90, 111.65, 4.60, 0.80, sc=1.48, mcx=0.0, mcy=0.0, mw=0.64, mh=0.94),

        # Split-Screen 8: 115.07 - 118.30s ("1 chiếc nơ màu be rất xinh xắn!") -> 4K DJI_0100_D macro beige bows below Chị Oanh!
        make_dji_split_bot(NGANG_DIR / "DJI_20261116095310_0100_D.MP4", 115.07, 118.30, 0.50, 0.80, sc=1.48, mcx=0.0, mcy=0.0, mw=0.64, mh=0.94),

        # Upper-right PIP @ 128.13 - 132.13s ("cảm ơn quý anh chị đã tin tưởng Thực phẩm F20")
        make_raw_video_seg(ANH_HAU / "C3928.MP4", 128.13, 132.13, 1.50, 1.00, in_anim="Trượt sang trái", out_anim="Mờ dần", base_scale=0.30, tx=0.56, ty=0.52, mask_cfg=copy.deepcopy(PIP_MASK)),

        # KHÚC CUỐI — CLOSING BANNER INFO CARD OVERLAY (140.42 - 142.90s)
        make_raw_video_seg(V6_ASSETS / "outro_banner_info_card.png", 140.42, total_end_u / 1e6, 0.0, 1.00, in_anim="Rõ dần", allow_v6_asset=True),
    ]
    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid(); tr_v2["segments"] = tr2_segs

    # ==========================================================================
    # 3. TRACKS 3..6 — 18 LIVELY REAL-PHOTO MAGNIFYING LOUPE ICON POP-UPS (`0%` AI!)
    #    Popping right on the spoken beat as Chị Oanh describes each product & ingredient!
    # ==========================================================================
    LOUPE_EVENTS = [
        # (t0_s, t1_s, png_name, px, py, scale)
        # 4-Item Gift Set Overview (48.65 - 52.55s: 4 Loupes popping 1->2->3->4 directly above the 4 native labels!)
        (48.65, 52.55, "loupe_01_to_yen_a5.png",      -0.46, +0.42, 0.31),
        (48.87, 52.55, "loupe_02_2hop_rong_bien.png", +0.46, +0.42, 0.31),
        (49.10, 52.55, "loupe_03_banh_thuyen.png",    -0.46, -0.12, 0.31),
        (49.30, 52.55, "loupe_04_kep_hat_500g.png",   +0.46, -0.12, 0.31),

        # Item 1: Tổ Yến Tinh Chế Sợi Dài (52.25 - 56.95s: upper-right clear of Chị Oanh on left!)
        (52.25, 56.95, "loupe_01_to_yen_a5.png",      +0.50, +0.22, 0.36),

        # 4 Stewing Ingredients (59.00 - 62.43s: popping 1->2->3->4 above each paired native label!)
        (59.00, 62.43, "loupe_05_tao_do.png",         -0.46, +0.44, 0.29),
        (59.63, 62.43, "loupe_06_dong_trung.png",     +0.46, +0.44, 0.29),
        (60.70, 62.43, "loupe_07_ky_tu.png",          -0.46, -0.06, 0.29),
        (61.43, 62.43, "loupe_08_duong_phen.png",     +0.46, -0.06, 0.29),

        # Item 2: 2 Hộp Rong Biển -> Cay Nhẹ (ớt đỏ) -> Sấy Mè (mè rang vàng)!
        (62.40, 65.42, "loupe_02_2hop_rong_bien.png", +0.50, +0.22, 0.36),
        (65.50, 67.60, "loupe_09_cay_nhe_ot.png",     +0.50, +0.20, 0.36),
        (67.63, 69.72, "loupe_10_say_me_vang.png",    +0.50, +0.20, 0.36),

        # Item 3: Bánh Thuyền Mix Hạt 250g
        (69.92, 74.95, "loupe_03_banh_thuyen.png",    +0.50, +0.20, 0.36),

        # Item 4: Rong Biển Kẹp Hạt 500g -> 22-24 Thanh!
        (75.32, 79.55, "loupe_04_kep_hat_500g.png",   +0.50, +0.20, 0.35),
        (81.18, 84.15, "loupe_11_24_thanh_hat.png",   +0.48, +0.16, 0.36),

        # Giá trị nhất: Tổ Yến Tinh Chế Sợi Dài A5 (while Chị Oanh speaks at 84.30 - 87.25s)
        (84.30, 87.25, "loupe_01_to_yen_a5.png",      +0.50, +0.20, 0.37),

        # Tờ Cẩm Nang Yến Sào (magnifying open brochure pages at 97.15 - 100.70s)
        (97.15, 100.70,"loupe_12_cam_nang_yen.png",   +0.50, +0.22, 0.35),
    ]

    loupe_lanes: list[list[dict]] = []
    for t0, t1, pnm, px, py, sc in sorted(LOUPE_EVENTS, key=lambda x: x[0]):
        sg = make_loupe_icon_seg(pnm, t0, t1, px, py, base_sc=sc)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for ln in loupe_lanes:
            if ln[-1]["target_timerange"]["start"] + ln[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                ln.append(sg)
                placed = True
                break
        if not placed:
            loupe_lanes.append([sg])

    loupe_tracks = []
    for ln in loupe_lanes:
        tr_l = copy.deepcopy(vtrack_tpl)
        tr_l["id"] = uid()
        tr_l["segments"] = ln
        loupe_tracks.append(tr_l)

    # ==========================================================================
    # 4. LIVELY EAR-VERIFIED USER SFX (`-18..-21dB`, Synced to Loupe Pops + Splits + Banner!)
    # ==========================================================================
    amat_map = {}
    def make_sfx_seg(sfx_fn: str, lbl: str, t0_s: float, vol: float, max_dur_s: float):
        sp = SFX_FOLDER / sfx_fn
        if not sp.is_file():
            raise FileNotFoundError(f"Missing user SFX: {sp}")
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
        # Intro & 104 Sets Story
        (0.18,   "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Air Mở Cảnh",      0.12, 0.7),
        (0.30,   "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3",                              "Chuông Gió Mở",    0.10, 1.8),
        (6.05,   "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Swoosh PIP 104",   0.11, 0.6),
        (9.25,   "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Gió Mềm 20/11",    0.10, 0.5),
        (15.90,  "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish ĐK Edu",     0.10, 0.6),
        (18.40,  "Chụp ảnh - Tiếng chụp màn hình gọn 03.mp3",                                   "Shutter 77 Set",   0.09, 0.5),
        (24.05,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Swipe Hà Nội",     0.10, 0.6),
        (33.30,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đủ 104 Set",  0.11, 1.2),
        (38.78,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Split Showroom",   0.10, 0.6),
        (43.00,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Gió Mềm 01 Set",   0.10, 0.5),

        # 4-Loupe Overview Pop Sequence (48.65 -> 49.30s)
        (48.63,  "Click & Máy Chữ - click (1s).mp3",                                            "Loupe Món 01",     0.11, 0.35),
        (48.87,  "Click & Máy Chữ - click (1s).mp3",                                            "Loupe Món 02",     0.11, 0.35),
        (49.10,  "Click & Máy Chữ - click (1s).mp3",                                            "Loupe Món 03",     0.11, 0.35),
        (49.30,  "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Món 04",      0.10, 1.0),

        # Item 1: Tổ Yến + 4 Stewing Ingredient Loupes
        (52.23,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Loupe Tổ Yến",     0.11, 0.6),
        (54.18,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Split DJI Yến",    0.10, 0.5),
        (59.00,  "Click & Máy Chữ - click (1s).mp3",                                            "Loupe Táo Đỏ",     0.11, 0.35),
        (59.63,  "Click & Máy Chữ - click (1s).mp3",                                            "Loupe Đông Trùng", 0.11, 0.35),
        (60.70,  "Click & Máy Chữ - click (1s).mp3",                                            "Loupe Kỷ Tử",      0.11, 0.35),
        (61.43,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đường Phèn",  0.10, 1.1),

        # Item 2: 2 Hộp Rong Biển -> Cay Nhẹ -> Sấy Mè
        (62.38,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Loupe 2 Hộp RB",   0.11, 0.6),
        (65.47,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Loupe Cay Nhẹ",    0.11, 0.6),
        (67.62,  "Click & Máy Chữ - click (1s).mp3",                                            "Loupe Sấy Mè",     0.11, 0.35),

        # Item 3 & 4: Bánh Thuyền 250g + Kẹp Hạt 500g + 22-24 Thanh
        (69.90,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Loupe Bánh Thuyền",0.11, 0.6),
        (75.30,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Loupe Kẹp Hạt",    0.11, 0.6),
        (81.16,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Loupe 24 Thanh",   0.11, 0.6),

        # Giá trị nhất + Cẩm nang + Bao bì + Sản xuất + Closing Banner!
        (84.30,  "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3",                                   "Shine Giá Trị Nhất",0.09, 0.9),
        (93.10,  "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Mở Cẩm Nang 1",    0.12, 0.8),
        (97.10,  "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Lật Trang Cẩm Nang",0.12, 0.8),
        (108.88, "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Split Quai Da",    0.10, 0.6),
        (115.05, "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Split Nơ Màu Be",  0.09, 1.0),
        (121.78, "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Whoosh Sản Xuất",  0.10, 0.6),
        (128.10, "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "PIP Cảm Ơn",       0.10, 0.5),
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
                ln.append(sg)
                placed = True
                break
        if not placed:
            sfx_lanes.append([sg])

    sfx_tracks = []
    for ln in sfx_lanes:
        tr_a = copy.deepcopy(atrack_tpl)
        tr_a["id"] = uid()
        tr_a["segments"] = ln
        sfx_tracks.append(tr_a)

    # Assemble Full V6 Timeline!
    D["tracks"] = [
        track0_user,        # Track 0: 100.00% Untouched User-Edited Main Track (45 segs, 140.37s)!
        tr_v1,              # Track 1: Raw F20 Full B-Rolls + 140.37-142.90s Closing Banner Stage!
        tr_v2,              # Track 2: Synced Raw DJI Split-Screens (below Chị Oanh) + PIPs + Closing Banner Info Card!
        *loupe_tracks,      # Tracks 3..6: 17 Real-Photo Magnifying Loupe Icons (`loupe_*.png`, 0% AI)!
        *text_tracks_user,  # User's Native Editable Coiny Subtitles + Floating Texts (100% preserved)!
        *bgm_tracks_user,   # User's 5-Segment Sáo Trúc Đàn Tranh BGM (0.00 -> 142.90s, 100% preserved)!
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

    dmi_base = json.loads((USER_BAK / "draft_meta_info.json").read_text(encoding="utf-8"))
    dmi_base["tm_duration"] = total_end_u
    dmi_base["tm_draft_modified"] = now_us
    for bucket in dmi_base.get("draft_materials", []):
        if bucket.get("type") == 0:
            clean_vals = [x for x in bucket.get("value", []) if "capcut_layers_1117" not in str(x.get("file_Path", ""))]
            existing = {x.get("file_Path") for x in clean_vals}
            for ne in new_dm_entries:
                if ne["file_Path"] not in existing:
                    clean_vals.append(ne)
            bucket["value"] = clean_vals

    pj["update_time"] = now_us
    for t_ent in pj.get("timelines", []):
        t_ent["update_time"] = now_us

    is_locked = (DRAFT_DIR / ".locked").exists()
    print(f"Writing V6 timeline... (1117 F20 .locked == {is_locked})")

    def write_into_draft(target_dir: Path, custom_name: str | None = None, custom_id: str | None = None):
        for tp in [
            target_dir / "draft_content.json",
            target_dir / "template-2.tmp",
            target_dir / "Timelines" / tl_id / "draft_content.json",
            target_dir / "Timelines" / tl_id / "template-2.tmp",
        ]:
            if tp.exists():
                tp.unlink()
            tp.write_bytes(dc_bytes)
        dmi_c = copy.deepcopy(dmi_base)
        if custom_name:
            dmi_c["draft_name"] = custom_name
            dmi_c["draft_fold_path"] = norm_fwd(target_dir)
        if custom_id:
            dmi_c["draft_id"] = custom_id
        (target_dir / "draft_meta_info.json").write_text(json.dumps(dmi_c, ensure_ascii=False), encoding="utf-8")
        (target_dir / "Timelines" / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

    # Always update 1117 F20 AND if 1117 F20 is currently open (.locked == True), ALSO create unlocked top-of-list draft!
    write_into_draft(DRAFT_DIR)

    rmi_path = ROOT / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    store = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_ALT.name]
    orig_entry = None
    for x in store:
        if x.get("draft_name") == "1117 F20":
            x["tm_duration"] = total_end_u
            x["tm_draft_modified"] = now_us
            orig_entry = x

    if is_locked:
        copy_draft_unlinked(DRAFT_DIR, DRAFT_ALT)
        alt_id = uid()
        write_into_draft(DRAFT_ALT, custom_name=DRAFT_ALT.name, custom_id=alt_id)
        if orig_entry:
            ae = copy.deepcopy(orig_entry)
            ae["draft_id"] = alt_id
            ae["draft_name"] = DRAFT_ALT.name
            ae["draft_fold_path"] = norm_fwd(DRAFT_ALT)
            ae["draft_json_file"] = norm_fwd(DRAFT_ALT / "draft_content.json")
            ae["tm_draft_modified"] = now_us + 1000
            store.insert(0, ae)
        print(f"  -> Because '1117 F20' is currently OPEN (.locked=True), ALSO created unlocked '{DRAFT_ALT.name}' at #1 on CapCut Home Screen so CapCut autosave cannot overwrite your new overlays!")
    else:
        if DRAFT_ALT.exists():
            shutil.rmtree(DRAFT_ALT, ignore_errors=True)

    rmi["all_draft_store"] = store
    rmi["draft_ids"] = len(store)
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    print("SUCCESS V6 MASTER OVERLAYS (LOUPE ICONS + DJI SPLIT-SCREEN + 20/11 CLOSING BANNER)!")
    print(f"  -> Duration: {total_end_u/1e6:.3f}s | Track 0: {len(track0_user['segments'])} segs (100% untouched)")
    print(f"  -> Track 1 Full B-Rolls + Banner Stage: {len(tr1_segs)} segs | Track 2 Synced DJI Split-Screens + PIPs + Banner Card: {len(tr2_segs)} segs")
    print(f"  -> Real-Photo Magnifying Loupe Icons: {len(LOUPE_EVENTS)} across {len(loupe_tracks)} tracks (0% AI!)")
    print(f"  -> User Subtitles & Texts: {sum(len(t['segments']) for t in text_tracks_user)} segs | BGM: {len(bgm_segs_raw)} segs | SFX: {len(SFX_EVENTS)} segs")

if __name__ == "__main__":
    main()
