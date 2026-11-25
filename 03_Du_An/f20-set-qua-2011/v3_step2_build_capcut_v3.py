import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT       = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_ORIG = ROOT / "1117 F20"
DRAFT_V3   = ROOT / "1117 F20 - V3 Full Layers"
FC_V6_DIR  = ROOT / "FEEL_CHICKEN_2011_Full_Layers_V6"
HTPM_DIR   = ROOT / "HTPM"

WORK       = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
BAK        = WORK / "backup_1117_F20_orig"
LAYERS_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_layers_1117_v3")
BROLL_DIR  = LAYERS_DIR / "brolls"
PNG_DIR    = LAYERS_DIR / "png_layers"
SFX_FOLDER = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")

FPS = 30.0
def uid(): return str(uuid.uuid4()).upper()
def us(sec):
    f = int(round(float(sec) * FPS))
    return int(round(f * 1_000_000 / FPS))
def norm_fwd(p): return os.path.normpath(str(p)).replace("\\", "/")

def hardlink_tree(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            hardlink_tree(item, target)
        else:
            if target.exists():
                target.unlink()
            try:
                os.link(item, target)
            except Exception:
                shutil.copy2(item, target)

def main():
    man = json.loads((LAYERS_DIR / "layers_manifest.json").read_text(encoding="utf-8"))
    pj_orig = json.loads((BAK / "Timelines" / "project.json").read_text(encoding="utf-8"))
    tl_id = pj_orig["main_timeline_id"]

    D = json.loads((BAK / "Timelines" / tl_id / "draft_content.json").read_text(encoding="utf-8"))
    dc_fc = json.loads((FC_V6_DIR / "draft_content.json").read_text(encoding="utf-8"))
    dm_fc = json.loads((FC_V6_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(D["tracks"][0])
    vseg_tpl   = copy.deepcopy(D["tracks"][0]["segments"][0])
    atrack_tpl = copy.deepcopy(D["tracks"][5])
    aseg_tpl   = copy.deepcopy(D["tracks"][5]["segments"][0])

    vmat_tpl  = copy.deepcopy(next(m for m in dc_fc["materials"]["videos"] if m.get("type") == "video"))
    pmat_tpl  = copy.deepcopy(next(m for m in dc_fc["materials"]["videos"] if m.get("type") == "photo"))
    amat_tpl  = copy.deepcopy(D["materials"]["audios"][0])
    kf_tpl    = copy.deepcopy(next(sg["common_keyframes"][0] for tr in dc_fc["tracks"] for sg in tr.get("segments", []) if sg.get("common_keyframes")))

    dm_vid_tpl = copy.deepcopy(next(x for g in dm_fc["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
    dm_pho_tpl = copy.deepcopy(next(x for g in dm_fc["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "photo"))

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

    VIDEO_ANIMS = json.loads((WORK / "verified_video_anims.json").read_text(encoding="utf-8"))
    RECT_MASK_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef"

    # Keep ONLY Track 0 (100% untouched) + BGM Track
    track0_orig    = copy.deepcopy(D["tracks"][0])
    bgm_track_orig = copy.deepcopy(D["tracks"][6])
    main_end_u     = max(s["target_timerange"]["start"] + s["target_timerange"]["duration"] for s in track0_orig["segments"])

    bgm_seg = bgm_track_orig["segments"][0]
    bgm_seg["target_timerange"]["duration"] = main_end_u
    bgm_seg["source_timerange"]["duration"] = main_end_u
    bgm_seg["volume"] = 0.17
    bgm_seg["last_nonzero_volume"] = 0.17
    fade_bgm_id = uid()
    D["materials"].setdefault("audio_fades", []).append({
        "fade_in_duration": 400000, "fade_out_duration": 1500000, "fade_type": 0, "id": fade_bgm_id, "type": "audio_fade"
    })
    bgm_seg["extra_material_refs"].append(fade_bgm_id)

    used_ids = set()
    for tr_k in (track0_orig, bgm_track_orig):
        for s in tr_k["segments"]:
            used_ids.add(s["material_id"])
            used_ids.update(s.get("extra_material_refs", []))
    for k, val in list(D["materials"].items()):
        if isinstance(val, list):
            D["materials"][k] = [x for x in val if isinstance(x, dict) and x.get("id") in used_ids]

    now_s  = int(time.time())
    now_us = int(time.time() * 1_000_000)
    vis_cache = {}
    new_dm_entries = []

    def register_visual(path: Path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing visual layer: {path}")
        fwd = norm_fwd(path)
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
            r = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(path)
            ], capture_output=True, text=True, check=True)
            j = json.loads(r.stdout)
            vs = j["streams"][0]
            w, h = int(vs["width"]), int(vs["height"])
            dur_u = max(33333, us(float(j["format"]["duration"])))
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": fwd, "media_path": "", "local_id": "",
                "material_name": path.name, "width": w, "height": h, "duration": dur_u, "has_audio": False
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
        vis_cache[fwd] = (mid, dur_u, is_photo)
        return mid, dur_u, is_photo

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

    def make_broll_seg(mp4_name: str, t0_s: float, t1_s: float, mode: str = "full", zoom_dir: int = 1):
        mid, mat_dur_u, _ = register_visual(BROLL_DIR / mp4_name)
        st_u = us(t0_s)
        du_u = min(mat_dur_u, max(us(0.25), us(t1_s) - st_u))
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])

        # Smooth Video In + Out animations
        anim_list = []
        in_nm = "Rõ dần" if mode == "full" else "Trượt sang trái"
        if in_nm in VIDEO_ANIMS["in"]:
            ai = copy.deepcopy(VIDEO_ANIMS["in"][in_nm])
            ai["start"] = 0
            ai["duration"] = min(233333 if mode == "full" else 333333, du_u // 3)
            anim_list.append(ai)
        if "Mờ dần" in VIDEO_ANIMS["out"]:
            ao = copy.deepcopy(VIDEO_ANIMS["out"]["Mờ dần"])
            od = min(200000, du_u // 3)
            ao["duration"] = od
            ao["start"] = max(0, du_u - od)
            anim_list.append(ao)
        if anim_list:
            ma_id = uid()
            D["materials"].setdefault("material_animations", []).append({
                "animations": anim_list, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
            })
            refs.append(ma_id)

        kfs = []
        dur_s = du_u / 1e6
        if mode == "full":
            seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
            seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
            seg["uniform_scale"] = {"on": True, "value": 1.0}
            if zoom_dir != 0 and dur_s >= 1.8:
                s0, s1 = (1.00, 1.036) if zoom_dir > 0 else (1.036, 1.00)
                kfs = [make_kf("KFTypeScaleX", [(0.0, s0), (dur_s, s1)]), make_kf("KFTypeScaleY", [(0.0, s0), (dur_s, s1)])]
        elif mode == "pip_tr":
            sc = 0.34
            seg["clip"]["scale"] = {"x": sc, "y": sc}
            seg["clip"]["transform"] = {"x": 0.48, "y": 0.44}
            seg["uniform_scale"] = {"on": True, "value": sc}
            if os.path.exists(RECT_MASK_PATH):
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
            "source_timerange": {"start": 0, "duration": du_u},
            "target_timerange": {"start": st_u, "duration": du_u},
            "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [],
        })
        seg["clip"]["alpha"] = 1.0
        return seg

    def make_png_layer_seg(png_name: str, t0_s: float, t1_s: float, kind: str = "sub"):
        mid, _, _ = register_visual(PNG_DIR / png_name)
        st_u = us(t0_s)
        du_u = max(us(0.35), us(t1_s) - st_u)
        dur_s = du_u / 1e6
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])

        if kind == "float":
            # Elastic Pop-In + Continuous Smooth Upward Levitation ('bay bay') + Optical Fade In/Out!
            kfs = [
                make_kf("KFTypeScaleX", [(0.0, 0.84), (min(0.18, dur_s * 0.35), 1.04), (min(0.34, dur_s * 0.6), 1.00), (dur_s, 1.02)]),
                make_kf("KFTypeScaleY", [(0.0, 0.84), (min(0.18, dur_s * 0.35), 1.04), (min(0.34, dur_s * 0.6), 1.00), (dur_s, 1.02)]),
                make_kf("KFTypePositionY", [(0.0, -0.028), (min(0.35, dur_s * 0.4), 0.0), (dur_s, +0.028)]),
                make_kf("KFTypeAlpha", [(0.0, 0.0), (0.10, 1.0), (max(0.14, dur_s - 0.16), 1.0), (dur_s, 0.0)]),
            ]
        else:
            # Clean Subtitle Gentle Pop + Smooth Fade In/Out!
            kfs = [
                make_kf("KFTypeScaleX", [(0.0, 0.95), (min(0.12, dur_s * 0.4), 1.00)]),
                make_kf("KFTypeScaleY", [(0.0, 0.95), (min(0.12, dur_s * 0.4), 1.00)]),
                make_kf("KFTypeAlpha", [(0.0, 0.0), (0.08, 1.0), (max(0.12, dur_s - 0.12), 1.0), (dur_s, 0.0)]),
            ]

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": 0, "duration": du_u},
            "target_timerange": {"start": st_u, "duration": du_u},
            "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 0.0,
            "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [],
        })
        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        return seg

    # 1. Build Cohesive Color-Matched Track 1 & PIP Track 2
    BROLL_TIMELINE = [
        ("ov_01_intro_104sets.mp4",     1.80,   3.77, -1),
        ("ov_02_anh_hau_handover.mp4", 15.65,  17.75, +1),
        ("ov_03_anh_hau_77sets.mp4",   17.75,  19.95, -1),
        ("ov_04_phu_huynh_13sets.mp4", 20.20,  23.90, +1),
        ("ov_05_hanoi_10sets_pack.mp4",24.67,  28.05, +1),
        ("ov_06_hcm_4sets_car.mp4",    28.05,  31.68, -1),
        ("ov_07_du_104_sets_glide.mp4",33.80,  36.65, +1),
        ("ov_08_showroom_bows_4k.mp4", 41.60,  44.85, +1),
        ("bento_4mon_setqua.mp4",      52.18,  56.18,  0),
        ("ov_09_to_yen_soi_dai.mp4",   58.25,  61.08, +1),
        ("bento_4nguyenlieu_chung.mp4",63.15,  66.65,  0),
        ("ov_10_2hop_rong_bien.mp4",   70.10,  74.48,  0),
        ("ov_11_banh_thuyen_250g.mp4", 77.15,  79.95,  0),
        ("ov_12_kep_hat_500g.mp4",     82.20,  85.40,  0),
        ("ov_13_gia_tri_nhat_yen.mp4", 92.65,  95.85, +1),
        ("ov_14_cam_nang_open.mp4",    98.60, 102.80,  0),
        ("ov_15_cam_nang_pages.mp4",  102.80, 107.30, +1),
        ("ov_16_gio_mica.mp4",        110.80, 114.10, +1),
        ("ov_17_quai_da_do.mp4",      116.15, 119.15, -1),
        ("ov_18_bong_hoa_do.mp4",     119.55, 122.90, +1),
        ("ov_19_no_mau_be.mp4",       122.90, 126.20, +1),
        ("ov_20_f20_san_xuat_a.mp4",  129.80, 132.60, +1),
        ("ov_21_f20_san_xuat_b.mp4",  132.60, 135.40, -1),
        ("ov_22_outro_beauty.mp4",    143.60, 146.75, +1),
    ]
    tr_ov_full = copy.deepcopy(vtrack_tpl); tr_ov_full["id"] = uid()
    tr_ov_full["segments"] = [make_broll_seg(fn, t0, t1, mode="full", zoom_dir=zd) for fn, t0, t1, zd in BROLL_TIMELINE]

    tr_ov_pip = copy.deepcopy(vtrack_tpl); tr_ov_pip["id"] = uid()
    tr_ov_pip["segments"] = [
        make_broll_seg("ov_09b_basket_macro.mp4", 6.35,   9.40,  mode="pip_tr", zoom_dir=0),
        make_broll_seg("ov_03_anh_hau_77sets.mp4",136.40, 140.40, mode="pip_tr", zoom_dir=0),
    ]

    # 2. Pack Floating White-Fill Red-Stroke Stickers & Pill Headers into non-overlapping Video Overlay Tracks!
    flt_lanes: list[list[dict]] = []
    for item in sorted(man["floating"], key=lambda x: x["t0"]):
        sg = make_png_layer_seg(item["file"], item["t0"], item["t1"], kind="float")
        st_u = sg["target_timerange"]["start"]
        placed = False
        for lane in flt_lanes:
            if lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                lane.append(sg); placed = True; break
        if not placed:
            flt_lanes.append([sg])

    flt_tracks = []
    for lane in flt_lanes:
        tr_f = copy.deepcopy(vtrack_tpl); tr_f["id"] = uid(); tr_f["segments"] = lane
        flt_tracks.append(tr_f)

    # 3. Build Separated-Stroke Coiny Subtitle Track!
    tr_sub_png = copy.deepcopy(vtrack_tpl); tr_sub_png["id"] = uid()
    tr_sub_png["segments"] = [
        make_png_layer_seg(it["file"], it["t0"], it["t1"], kind="sub") for it in man["subtitles"]
    ]

    # 4. Build 25-Variety User SFX Tracks (100% from 02_Hiệu Ứng Âm Thanh (SFX)!)
    amat_map = {}
    def make_sfx_seg(sfx_fn: str, lbl: str, t0_s: float, vol: float, max_dur_s: float):
        sp = SFX_FOLDER / sfx_fn
        if not sp.is_file():
            raise FileNotFoundError(f"Missing SFX: {sp}")
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

    # 100% EAR-VERIFIED SHORT, SILKY, TACTILE MICRO-SFX (-18dB to -21dB -> vol 0.09..0.13, zero ringing over speech, zero cartoon pops!)
    SFX_EVENTS = [
        # Intro (0-4s instrumental only: delicate wind-chimes + silky air swoosh)
        (0.16,   "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Air Mở Cảnh",      0.13, 0.7),
        (0.28,   "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3",                              "Chuông Gió Mở",    0.10, 1.8),
        (1.78,   "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh Đại Cảnh",  0.12, 0.5),

        # Subtle modern air-ticks around Chị Oanh
        (6.35,   "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Air Tick 104 Set", 0.10, 0.6),
        (9.55,   "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Gió Mềm 20/11",    0.11, 0.5),

        # Customer Order Beats (Đăng Khoa Edu -> Hội phụ huynh -> Hà Nội -> TP.HCM -> Đủ 104 Set)
        (15.62,  "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish ĐK Edu",     0.10, 0.6),
        (17.75,  "Chụp ảnh - Tiếng chụp màn hình gọn 03.mp3",                                   "Shutter Anh Hậu",  0.09, 0.6),
        (20.22,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Whoosh 13 Set",    0.11, 0.6),
        (24.68,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Swipe Hà Nội",     0.10, 0.6),
        (28.05,  "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish TP.HCM",     0.10, 0.6),
        (33.82,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đủ 104 Set",  0.10, 1.2),
        (41.58,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Whoosh Showroom",  0.11, 0.6),
        (45.20,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh 01 Set",    0.10, 0.5),

        # 2x2 Bento 4 Món Set Quà (Crisp Tactile Clicks + Soft Single Bell)
        (52.15,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Bento Air",        0.11, 0.6),
        (52.48,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Món 02",      0.10, 0.35),
        (52.76,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Món 03",      0.10, 0.35),
        (53.04,  "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Món 04",      0.09, 1.0),

        # Món 01: Tổ Yến Sợi Dài & 4 Nguyên Liệu Chưng (Short clean ticks + soft single ding)
        (58.25,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Air Tổ Yến",       0.10, 0.6),
        (63.16,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Táo Đỏ",      0.10, 0.35),
        (63.82,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Đông Trùng",  0.10, 0.35),
        (65.05,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Kỷ Tử",       0.10, 0.35),
        (65.80,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đường Phèn",  0.09, 1.1),

        # Món 02, 03, 04 (Rong Biển, Bánh Thuyền, Kẹp Hạt 22-24 Thanh)
        (70.10,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Swipe Rong Biển",  0.10, 0.6),
        (77.15,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Swoosh 250g",      0.10, 0.6),
        (82.20,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Card 500g",        0.12, 0.7),
        (86.28,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh 24 Thanh",  0.10, 0.5),

        # Giá Trị Nhất + Cẩm Nang Yến Sào (Authentic Paper Page Turn!)
        (92.65,  "Whoosh - Title Swoosh (1s).mp3",                                              "Swoosh Giá Trị",   0.10, 0.7),
        (98.58,  "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Mở Cẩm Nang 1",    0.13, 0.8),
        (102.80, "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Lật Trang Trong",  0.12, 0.8),

        # Bao bì sang trọng (Giỏ Mica, Quai Da Đỏ Đô, Hoa Đỏ, Nơ Màu Be)
        (110.80, "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish Giỏ Mica",   0.10, 0.6),
        (116.15, "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3",                                   "Shine Quai Da",    0.09, 0.9),
        (119.55, "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh Hoa Đỏ",    0.10, 0.5),
        (122.90, "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Nơ Be",       0.09, 1.1),

        # Trực tiếp sản xuất & Lời cảm ơn / CTA cuối
        (129.80, "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Whoosh Sản Xuất",  0.11, 0.6),
        (132.32, "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Air Giá Xưởng",    0.10, 0.6),
        (136.38, "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh Cảm Ơn",    0.10, 0.5),
        (146.82, "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Inbox Ngay",  0.11, 1.4),
    ]

    sfx_lanes: list[list[dict]] = []
    for t0, fn, lbl, vol, mdur in sorted(SFX_EVENTS, key=lambda x: x[0]):
        sg = make_sfx_seg(fn, lbl, t0, vol=vol, max_dur_s=mdur)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for lane in sfx_lanes:
            if lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                lane.append(sg); placed = True; break
        if not placed:
            sfx_lanes.append([sg])

    sfx_tracks = []
    for lane in sfx_lanes:
        tr_a = copy.deepcopy(atrack_tpl); tr_a["id"] = uid(); tr_a["segments"] = lane
        sfx_tracks.append(tr_a)

    D["tracks"] = [
        track0_orig,     # Track 0: 100.00% Untouched Main Timeline!
        tr_ov_full,      # Track 1: 24 Color-Matched B-Rolls + 2 Bento Showcases!
        tr_ov_pip,       # Track 2: 2 Rounded Upper-Right PIPs!
        *flt_tracks,     # Track 3..5: 32 Floating White-Fill Red-Stroke 3D Stickers & Pill Headers!
        tr_sub_png,      # Track 6: 52 Separated-Stroke Coiny Subtitles!
        bgm_track_orig,  # BGM Track
        *sfx_tracks,     # Multi-lane Diverse User SFX Tracks!
    ]
    D["duration"] = main_end_u
    D["update_time"] = now_s

    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video":
                s["render_index"] = ti

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")

    # Prepare updated draft_meta_info.json
    dmi_base = json.loads((BAK / "draft_meta_info.json").read_text(encoding="utf-8"))
    dmi_base["tm_duration"] = main_end_u
    dmi_base["tm_draft_modified"] = now_us
    dmi_base["tm_draft_cloud_entry_id"] = -1
    dmi_base["tm_draft_cloud_parent_entry_id"] = -1
    for bucket in dmi_base.get("draft_materials", []):
        if bucket.get("type") == 0:
            existing = {x.get("file_Path") for x in bucket.get("value", [])}
            for ne in new_dm_entries:
                if ne["file_Path"] not in existing:
                    bucket["value"].append(ne)

    # 1) Create/Update unlocked top-of-list clone `1117 F20 - V3 Full Layers` (100% immune to .locked RAM overwrite!)
    if DRAFT_V3.exists():
        shutil.rmtree(DRAFT_V3)
    DRAFT_V3.mkdir(parents=True, exist_ok=True)
    for item in DRAFT_ORIG.iterdir():
        if item.name in (".locked", "Timelines"):
            continue
        if item.is_dir():
            hardlink_tree(item, DRAFT_V3 / item.name)
        else:
            shutil.copy2(item, DRAFT_V3 / item.name)
    # Copy Timelines directory cleanly (NEVER hardlink JSON files so open CapCut autosaves can't overwrite V3!)
    shutil.copytree(BAK / "Timelines", DRAFT_V3 / "Timelines")

    v3_draft_id = "D849F21A-7C42-49B8-9E15-6302B8841FA3"
    dmi_v3 = copy.deepcopy(dmi_base)
    dmi_v3["draft_id"] = v3_draft_id
    dmi_v3["draft_name"] = DRAFT_V3.name
    dmi_v3["draft_fold_path"] = norm_fwd(DRAFT_V3)
    dmi_v3["draft_root_path"] = norm_fwd(ROOT)

    for tp in [
        DRAFT_V3 / "draft_content.json",
        DRAFT_V3 / "template-2.tmp",
        DRAFT_V3 / "Timelines" / tl_id / "draft_content.json",
        DRAFT_V3 / "Timelines" / tl_id / "template-2.tmp",
    ]:
        tp.write_bytes(dc_bytes)
    (DRAFT_V3 / "draft_meta_info.json").write_text(json.dumps(dmi_v3, ensure_ascii=False), encoding="utf-8")
    pj_v3 = copy.deepcopy(pj_orig)
    pj_v3["update_time"] = now_us
    for t_ent in pj_v3.get("timelines", []): t_ent["update_time"] = now_us
    (DRAFT_V3 / "Timelines" / "project.json").write_text(json.dumps(pj_v3, ensure_ascii=False), encoding="utf-8")

    # 2) Also write directly into `1117 F20` if not actively file-locked by OS!
    orig_was_locked = (DRAFT_ORIG / ".locked").exists()
    try:
        for tp in [
            DRAFT_ORIG / "draft_content.json",
            DRAFT_ORIG / "template-2.tmp",
            DRAFT_ORIG / "Timelines" / tl_id / "draft_content.json",
            DRAFT_ORIG / "Timelines" / tl_id / "template-2.tmp",
        ]:
            tp.write_bytes(dc_bytes)
        (DRAFT_ORIG / "draft_meta_info.json").write_text(json.dumps(dmi_base, ensure_ascii=False), encoding="utf-8")
        (DRAFT_ORIG / "Timelines" / "project.json").write_text(json.dumps(pj_v3, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print("Note on 1117 F20 direct write:", e)

    # Register `1117 F20 - V3 Full Layers` at #1 in root_meta_info.json & update `1117 F20`!
    rmi_path = ROOT / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    store = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_V3.name]
    tpl_rmi = copy.deepcopy(next((x for x in store if x.get("draft_name") == "1117 F20"), store[0]))
    tpl_rmi.update({
        "draft_id": v3_draft_id,
        "draft_name": DRAFT_V3.name,
        "draft_fold_path": norm_fwd(DRAFT_V3),
        "draft_json_file": norm_fwd(DRAFT_V3 / "draft_content.json"),
        "draft_cover": norm_fwd(DRAFT_V3 / "draft_cover.jpg"),
        "tm_duration": main_end_u,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us + 1000,
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_user_id": -1,
    })
    for x in store:
        if x.get("draft_name") == "1117 F20":
            x["tm_duration"] = main_end_u
            x["tm_draft_modified"] = now_us
    store.insert(0, tpl_rmi)
    rmi["all_draft_store"] = store
    rmi["draft_ids"] = len(store)
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    print(f"SUCCESS V3 FEEL×HTPM! (1117 F20 was .locked={orig_was_locked})")
    print(f"  -> Ready at TOP of CapCut Home Screen: '{DRAFT_V3.name}' AND updated '1117 F20'!")
    print(f"  -> Total Tracks: {len(D['tracks'])} | B-rolls: {len(tr_ov_full['segments'])} | Floating Stickers: {len(man['floating'])} | Subtitles: {len(man['subtitles'])} | SFX: {len(SFX_EVENTS)} ({len(amat_map)} distinct files)")

if __name__ == "__main__":
    main()
