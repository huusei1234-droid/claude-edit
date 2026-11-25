import copy, json, math, os, shutil, subprocess, sys, time, uuid

PROJ_DIR   = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
LAYERS_DIR = os.path.join(PROJ_DIR, "capcut_layers_v6")
STAGE_ROOT = os.path.join(PROJ_DIR, "capcut_stage_full_layers_v6")

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "FEEL_CHICKEN_2011_Full_Layers_V6"
DRAFT_ID   = "C77E91A2-84B3-4D19-AF32-9182E4410FA6"

CONAN_MP3  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Detective Conan Main Theme (Captured In Her Eyes Version).mp3"

sys.path.insert(0, PROJ_DIR)
from step10c_mix_and_export_fc_v3 import SFX_SPECS

FPS = 30.0

def uid():
    return str(uuid.uuid4()).upper()

def us_frame(sec):
    """Snap to exact 30fps frame boundary in microseconds so zero 1-us gaps or overlaps occur!"""
    f = int(round(float(sec) * FPS))
    return int(round(f * 1_000_000 / FPS))

def norm_fwd(p):
    return os.path.normpath(p).replace("\\", "/")

def probe_media(path):
    r = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_type,width,height:stream_side_data=rotation:format=duration",
        "-of", "json", path
    ], capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    vs = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    has_aud = any(s.get("codec_type") == "audio" for s in j.get("streams", []))
    w = int(vs.get("width") or 1080)
    h = int(vs.get("height") or 1920)
    rot = 0
    for sd in vs.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if abs(rot) in (90, 270):
        w, h = h, w
    dur = float(j.get("format", {}).get("duration", 0.0) or 0.0)
    return w, h, dur, has_aud

def make_kf_obj(kf_tpl, prop_type, points_sec_val):
    """points_sec_val = [(offset_sec_from_seg_start, float_val), ...]"""
    kf = copy.deepcopy(kf_tpl)
    kf["id"] = uid()
    kf["material_id"] = ""
    kf["property_type"] = prop_type
    pt_tpl = copy.deepcopy(kf_tpl["keyframe_list"][0])
    klist = []
    for off_s, val in points_sec_val:
        pt = copy.deepcopy(pt_tpl)
        pt["id"] = uid()
        pt["curveType"] = "Line"
        pt["time_offset"] = max(0, us_frame(off_s))
        pt["values"] = [float(val)]
        pt["left_control"] = {"x": 0.0, "y": 0.0}
        pt["right_control"] = {"x": 0.0, "y": 0.0}
        pt["string_value"] = ""
        pt["graphID"] = ""
        klist.append(pt)
    kf["keyframe_list"] = klist
    return kf

def make_pop_in_kfs(kf_tpl, seg_dur_s, s0=0.84, pop_dur=0.18, fade_out=0.14):
    kfs = [
        make_kf_obj(kf_tpl, "KFTypeScaleX", [(0.0, s0), (min(seg_dur_s * 0.5, pop_dur), 1.0)]),
        make_kf_obj(kf_tpl, "KFTypeScaleY", [(0.0, s0), (min(seg_dur_s * 0.5, pop_dur), 1.0)]),
    ]
    if seg_dur_s > 0.40:
        kfs.append(make_kf_obj(kf_tpl, "KFTypeAlpha", [
            (0.0, 0.0),
            (0.07, 1.0),
            (max(0.10, seg_dur_s - fade_out), 1.0),
            (seg_dur_s, 0.0)
        ]))
    return kfs

def main():
    t0 = time.time()
    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master_v5.json"), encoding="utf-8"))
    segs_tm = {s["id"]: s for s in tm["segments"]}
    sub_man = json.load(open(os.path.join(LAYERS_DIR, "subtitles_manifest.json"), encoding="utf-8"))

    # Load authentic v193.0.0 templates from CapCut projects on this machine
    d_f20  = os.path.join(DRAFTS_DIR, "F20 vd 1")
    dc_f20 = json.load(open(os.path.join(d_f20, "draft_content.json"), encoding="utf-8"))
    dm_f20 = json.load(open(os.path.join(d_f20, "draft_meta_info.json"), encoding="utf-8"))
    dc_av  = json.load(open(os.path.join(DRAFTS_DIR, "AV thu2 10-doan-mp3", "draft_content.json"), encoding="utf-8"))
    dm_av  = json.load(open(os.path.join(DRAFTS_DIR, "AV thu2 10-doan-mp3", "draft_meta_info.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(dc_f20["tracks"][0])
    atrack_tpl = copy.deepcopy(next(tr for tr in dc_f20["tracks"] if tr["type"] == "audio"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])

    kf_tpl = None
    for tr in dc_f20["tracks"]:
        for sg in tr.get("segments", []):
            if sg.get("common_keyframes"):
                kf_tpl = copy.deepcopy(sg["common_keyframes"][0])
                break
        if kf_tpl:
            break

    vmat_tpl  = copy.deepcopy(next(m for m in dc_f20["materials"]["videos"] if m.get("type") == "video"))
    pmat_tpl  = copy.deepcopy(next(m for m in dc_av["materials"]["videos"] if m.get("type") == "photo"))
    amat_tpl  = copy.deepcopy(dc_f20["materials"]["audios"][0])
    afade_tpl = copy.deepcopy(dc_f20["materials"]["audio_fades"][0])

    dm_vid_tpl = copy.deepcopy(next(x for g in dm_f20["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
    dm_pho_tpl = copy.deepcopy(next(x for g in dm_av["draft_materials"]  for x in g.get("value", []) if x.get("metetype") == "photo"))
    dm_aud_tpl = copy.deepcopy(next(x for g in dm_f20["draft_materials"] for x in g.get("value", []) if x.get("metetype") in ("music", "audio", "sound")) if any(x.get("metetype") in ("music","audio","sound") for g in dm_f20["draft_materials"] for x in g.get("value",[])) else dm_vid_tpl)

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_f20["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_f20["materials"].get(k, []))}

    a_extra_keys = ("speeds", "placeholder_infos", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_f20["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_f20["materials"].get(k, []))}

    tl_id  = uid()
    now_s  = int(time.time())
    now_us = int(time.time() * 1_000_000)

    D = copy.deepcopy(dc_f20)
    D.update({
        "id": tl_id, "name": DRAFT_NAME, "fps": 30.0, "duration": 0,
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_f20["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })

    mat_cache = {}
    dm_entries_type0 = []
    referenced_bytes = 0

    def register_visual_mat(path):
        nonlocal referenced_bytes
        fwd = norm_fwd(path)
        if fwd in mat_cache:
            return mat_cache[fwd]
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing visual asset: {path}")
        fn = os.path.basename(path)
        is_photo = path.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        mid = uid()
        lmid = str(uuid.uuid4())
        if is_photo:
            from PIL import Image
            with Image.open(path) as im:
                w, h = im.size
            dur_u = 10_800_000_000
            m = copy.deepcopy(pmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "photo", "path": fwd, "media_path": "", "local_id": "",
                "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": False
            })
            dme = copy.deepcopy(dm_pho_tpl)
            dme.update({
                "id": lmid, "file_Path": fwd, "extra_info": fn,
                "duration": 5_000_000, "width": w, "height": h,
                "metetype": "photo", "item_source": 1,
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
            })
        else:
            w, h, dur_s, has_aud = probe_media(path)
            dur_u = max(33333, us_frame(dur_s))
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": fwd, "media_path": "", "local_id": "",
                "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud)
            })
            dme = copy.deepcopy(dm_vid_tpl)
            dme.update({
                "id": lmid, "file_Path": fwd, "extra_info": fn,
                "duration": dur_u, "width": w, "height": h,
                "metetype": "video", "item_source": 1,
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
                "roughcut_time_range": {"start": 0, "duration": dur_u},
                "sub_time_range": {"start": -1, "duration": -1},
            })
        D["materials"]["videos"].append(m)
        dm_entries_type0.append(dme)
        try:
            referenced_bytes += os.path.getsize(path)
        except Exception:
            pass
        mat_cache[fwd] = (mid, dur_u, is_photo)
        return mid, dur_u, is_photo

    def register_audio_mat(path):
        nonlocal referenced_bytes
        fwd = norm_fwd(path)
        if fwd in mat_cache:
            return mat_cache[fwd]
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Missing audio asset: {path}")
        fn = os.path.basename(path)
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
        dur_u = max(33333, us_frame(float(r.stdout.strip() or 1.0)))
        mid = uid()
        lmid = str(uuid.uuid4())
        m = copy.deepcopy(amat_tpl)
        m.update({
            "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
            "type": "extract_music", "name": os.path.splitext(fn)[0], "path": fwd,
            "duration": dur_u, "music_id": "", "effect_id": "", "resource_id": "", "source_platform": 0
        })
        D["materials"]["audios"].append(m)
        dme = copy.deepcopy(dm_aud_tpl)
        dme.update({
            "id": lmid, "file_Path": fwd, "extra_info": fn,
            "duration": dur_u, "width": 0, "height": 0,
            "metetype": "music", "item_source": 1,
            "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
        })
        dm_entries_type0.append(dme)
        try:
            referenced_bytes += os.path.getsize(path)
        except Exception:
            pass
        mat_cache[fwd] = (mid, dur_u, False)
        return mid, dur_u, False

    def make_vseg(path, tl_s, dur_s, src_s=0.0, render_idx=0, scale=1.0, tx=0.0, ty=0.0, alpha=1.0, kfs=None):
        mid, mat_dur_u, is_photo = register_visual_mat(path)
        st_u = 0 if is_photo else us_frame(src_s)
        du_u = us_frame(dur_s)
        if not is_photo:
            du_u = min(du_u, max(33333, mat_dur_u - st_u))
        tt_u = us_frame(tl_s)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": st_u, "duration": du_u},
            "target_timerange": {"start": tt_u, "duration": du_u},
            "speed": 1.0, "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs,
            "common_keyframes": kfs or [],
            "keyframe_refs": [],
            "render_index": render_idx, "track_render_index": 0,
            "visible": True,
        })
        seg["clip"]["scale"] = {"x": float(scale), "y": float(scale)}
        seg["clip"]["transform"] = {"x": float(tx), "y": float(ty)}
        seg["clip"]["alpha"] = float(alpha)
        seg["clip"]["rotation"] = 0.0
        seg["uniform_scale"] = {"on": True, "value": float(scale)}
        return seg

    def make_aseg(path, tl_s, dur_s, src_s=0.0, vol=1.0, fi_us=33333, fo_us=66666):
        mid, mat_dur_u, _ = register_audio_mat(path)
        st_u = us_frame(src_s)
        du_u = min(us_frame(dur_s), max(33333, mat_dur_u - st_u))
        tt_u = max(0, us_frame(tl_s))
        seg = copy.deepcopy(aseg_tpl)
        refs = []
        for k, tpl_e in a_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        if fi_us > 0 or fo_us > 0:
            af = copy.deepcopy(afade_tpl)
            af.update({
                "id": uid(),
                "fade_in_duration": min(du_u // 3, int(fi_us)),
                "fade_out_duration": min(du_u // 3, int(fo_us))
            })
            D["materials"]["audio_fades"].append(af)
            refs.append(af["id"])
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": st_u, "duration": du_u},
            "target_timerange": {"start": tt_u, "duration": du_u},
            "speed": 1.0, "volume": float(vol), "last_nonzero_volume": float(max(0.05, vol)),
            "extra_material_refs": refs,
            "common_keyframes": [], "keyframe_refs": [],
            "render_index": 0, "track_render_index": 1,
            "visible": True,
        })
        return seg

    # ==========================================================================
    # 1. TRACK V0: CONTINUOUS MAIN BASE TRACK (0.00 .. 48.47s, ZERO GAPS!)
    # ==========================================================================
    tr_v0 = copy.deepcopy(vtrack_tpl)
    tr_v0["id"] = uid()
    tr_v0["segments"] = []

    # Step keyframes on Main Track (S1 slap + Thành zoom, S2 Khang, S5 Khang, S6B Khang)
    s1_kfs = [
        make_kf_obj(kf_tpl, "KFTypeScaleX",    [(0.0, 1.02), (1.37, 1.02), (1.53, 1.16), (3.03, 1.16), (3.36, 1.98), (4.53, 2.12)]),
        make_kf_obj(kf_tpl, "KFTypeScaleY",    [(0.0, 1.02), (1.37, 1.02), (1.53, 1.16), (3.03, 1.16), (3.36, 1.98), (4.53, 2.12)]),
        make_kf_obj(kf_tpl, "KFTypePositionX", [(0.0, 0.00), (3.03, -0.06), (3.36, -0.49), (4.53, -0.49)]),
        make_kf_obj(kf_tpl, "KFTypePositionY", [(0.0, 0.00), (3.03, +0.04), (3.36, +0.07), (4.53, +0.07)]),
    ]
    s2_kfs = [
        make_kf_obj(kf_tpl, "KFTypeScaleX", [(0.0, 1.12), (0.77, 1.12), (0.97, 1.18), (4.90, 1.12)]),
        make_kf_obj(kf_tpl, "KFTypeScaleY", [(0.0, 1.12), (0.77, 1.12), (0.97, 1.18), (4.90, 1.12)]),
    ]
    s5a_kfs = [
        make_kf_obj(kf_tpl, "KFTypeScaleX", [(0.0, 1.00), (0.85, 1.00), (1.03, 1.07)]),
        make_kf_obj(kf_tpl, "KFTypeScaleY", [(0.0, 1.00), (0.85, 1.00), (1.03, 1.07)]),
    ]
    s5c_kfs = [
        make_kf_obj(kf_tpl, "KFTypeScaleX", [(0.0, 1.00), (2.77, 1.00), (2.97, 1.07)]),
        make_kf_obj(kf_tpl, "KFTypeScaleY", [(0.0, 1.00), (2.77, 1.00), (2.97, 1.07)]),
    ]
    s6b_kfs = [
        make_kf_obj(kf_tpl, "KFTypeScaleX", [(0.0, 1.00), (0.92, 1.00), (1.10, 1.06)]),
        make_kf_obj(kf_tpl, "KFTypeScaleY", [(0.0, 1.00), (0.92, 1.00), (1.10, 1.06)]),
    ]

    main_clips = [
        # (path, tl_s, dur_s, scale, tx, ty, kfs)
        (os.path.join(AROLL_DIR, "v5_cc_s1_skit.mp4"),                  0.000, 4.567, 1.02,  0.00,  0.00, s1_kfs),
        (os.path.join(AROLL_DIR, "v5_cc_s2_table.mp4"),                 4.567, 8.900, 1.12, -0.10, +0.12, s2_kfs),
        (os.path.join(MEDIA_DIR, "FC_v5_kute_teachers_2011_vid.mp4"),  13.467, 2.333, 1.10,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s3_c1381.mp4"),                15.800, 1.167, 1.00,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s3_c1385.mp4"),                16.967, 1.167, 1.00,  0.00,  0.00, None),
        (os.path.join(LAYERS_DIR,"bg_dark_neon_cs1.png"),              18.133, 3.833, 1.00,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s4_jar_shake.mp4"),            21.967, 2.133, 1.01,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s4_jar_draw.mp4"),             24.100, 3.833, 1.08, +0.11,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s5a_khang.mp4"),               27.933, 1.567, 1.00,  0.00,  0.00, s5a_kfs),
        (os.path.join(AROLL_DIR, "v5_cc_s5b_c1395.mp4"),               29.500, 1.100, 1.02,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s5b_0327.mp4"),                30.600, 1.133, 1.02,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s5b_0339.mp4"),                31.733, 1.133, 1.02,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s5c_khang.mp4"),               32.867, 3.967, 1.00,  0.00,  0.00, s5c_kfs),
        (os.path.join(MEDIA_DIR, "FC_v4_cs1_crowded_static_vid.mp4"),  36.833, 2.733, 1.00,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s6a_6494.mp4"),                39.567, 1.600, 1.16, +0.18,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s6a_6495.mp4"),                41.167, 1.600, 1.01,  0.00,  0.00, None),
        (os.path.join(AROLL_DIR, "v5_cc_s6b_thumbs.mp4"),              42.767, 1.800, 1.00,  0.00,  0.00, s6b_kfs),
        (os.path.join(AROLL_DIR, "v5_cc_s6c_storefront.mp4"),          44.567, 3.900, 1.00,  0.00,  0.00, None),
    ]

    cur_v0_u = 0
    for p, _, dur_s, sc, tx, ty, kfs in main_clips:
        seg = make_vseg(p, cur_v0_u / 1e6, dur_s, src_s=0.0, render_idx=0, scale=sc, tx=tx, ty=ty, kfs=kfs)
        seg["target_timerange"]["start"] = cur_v0_u
        tr_v0["segments"].append(seg)
        cur_v0_u += seg["target_timerange"]["duration"]

    total_dur_u = cur_v0_u
    D["tracks"].append(tr_v0)

    # ==========================================================================
    # 2. MULTI-LAYER OVERLAY TRACKS ("THÊM ĐẦY ĐỦ LỚP PHỦ NHÉ"!)
    # ==========================================================================
    # Each tuple: (z_tier, path, tl_s, dur_s, pop_anim, custom_kfs)
    overlay_items = [
        # --- Z-TIER 1: Cutaway B-Rolls & Behind-Head Studio Aura + Fireworks ---
        (1, os.path.join(MEDIA_DIR,  "FC_v2_meme_pray_vid.mp4"),          6.100, 3.367, False, None),
        (1, os.path.join(MEDIA_DIR,  "FC_v6_real_vn_classroom_vid.mp4"), 11.500, 1.967, False, None),
        (1, os.path.join(LAYERS_DIR, "ov_s3a_kawaii_hearts.mov"),        13.467, 2.333, False, None),
        (1, os.path.join(LAYERS_DIR, "ov_s3b_fireworks.mov"),            18.133, 3.800, False, None),
        (1, os.path.join(LAYERS_DIR, "ov_s5a_behind_head_aura.mov"),     27.933, 1.567, False, None),
        (1, os.path.join(LAYERS_DIR, "ov_s5c_behind_head_aura.mov"),     32.867, 3.967, False, None),
        (1, os.path.join(LAYERS_DIR, "ov_s6c_fireworks.mov"),            44.567, 3.900, False, None),

        # --- Z-TIER 2: RVM Foreground Cutout Anh Khang (sits IN FRONT OF Behind-Head Aura!) ---
        (2, os.path.join(LAYERS_DIR, "fg_s5a_khang_cutout.mov"),         27.933, 1.567, False, s5a_kfs),
        (2, os.path.join(LAYERS_DIR, "fg_s5c_khang_cutout.mov"),         32.867, 3.967, False, s5c_kfs),

        # --- Z-TIER 3: Top Headers, POV Banner & Green Chalkboard ---
        (3, os.path.join(LAYERS_DIR, "ov_s1_hdr.png"),                    0.100, 2.933, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s2_pov.png"),                    6.100, 3.367, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s2_nost_hdr.png"),              11.500, 1.967, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s3a_header_2011.png"),          13.467, 4.667, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s3b_chalkboard.png"),           18.133, 3.833, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s4_hdr_jar.png"),               21.967, 2.133, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s4_hdr_100.png"),               24.100, 3.833, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s5b_hdr.png"),                  29.500, 3.367, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s5c_hdr.png"),                  32.867, 3.967, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s6a_cert.png"),                 36.933, 5.767, True,  None),
        (3, os.path.join(LAYERS_DIR, "ov_s6c_top_logo_cta.png"),         44.567, 3.900, True,  None),

        # --- Z-TIER 4..9: Speech Bubbles, Impact Badges, 6 Stacked Quiz Cards, Callout Pills & Ultra-Kute End-Card! ---
        (4, os.path.join(LAYERS_DIR, "ov_s1_bub_khang.png"),              1.400, 1.633, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s1_qmarks.png"),                 3.133, 1.433, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s2_hoixua.png"),                 6.100, 1.933, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s2_ktm1.png"),                   8.033, 1.433, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s2_ktm2.png"),                  11.467, 2.000, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_quiz_card_01.png"),             25.300, 2.633, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s5a_tld.png"),                  27.933, 0.867, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s5a_coqua.png"),                28.800, 0.700, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s5b_pill1.png"),                29.533, 1.067, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s5b_pill2.png"),                30.633, 1.100, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s5b_pill3.png"),                31.767, 1.100, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s6a_pull_callouts.png"),        39.600, 1.567, True,  None),
        (4, os.path.join(LAYERS_DIR, "ov_s6a_bite_gionrum.mov"),         41.167, 1.600, False, None),
        (4, os.path.join(LAYERS_DIR, "ov_s6c_kute_endcard.mov"),         44.567, 3.900, False, None),

        (5, os.path.join(LAYERS_DIR, "ov_s1_ram.png"),                    1.400, 0.633, True,  None),
        (5, os.path.join(LAYERS_DIR, "ov_s1_bub_thanh.png"),              3.733, 0.800, True,  None),
        (5, os.path.join(LAYERS_DIR, "ov_s2_rung.png"),                   8.767, 0.700, True,  None),
        (5, os.path.join(LAYERS_DIR, "ov_s2_boihoi.png"),                12.233, 1.233, True,  None),
        (5, os.path.join(LAYERS_DIR, "ov_quiz_card_02.png"),             25.667, 2.267, True,  None),

        (6, os.path.join(LAYERS_DIR, "ov_quiz_card_03.png"),             26.067, 1.867, True,  None),
        (7, os.path.join(LAYERS_DIR, "ov_quiz_card_04.png"),             26.433, 1.500, True,  None),
        (8, os.path.join(LAYERS_DIR, "ov_quiz_card_05.png"),             26.800, 1.133, True,  None),
        (9, os.path.join(LAYERS_DIR, "ov_quiz_card_06.png"),             27.200, 0.733, True,  None),
    ]

    # --- Z-TIER 10: 20 Individual Kawaii Bubble Subtitle Overlay Clips! ---
    for sm in sub_man:
        overlay_items.append((
            10,
            os.path.join(LAYERS_DIR, sm["file"]),
            sm["t0"],
            max(0.20, sm["t1"] - sm["t0"]),
            True,
            None
        ))

    # Group by z_tier in ascending order and pack onto non-overlapping overlay tracks!
    overlay_tracks_built = 0
    for zt in sorted(set(x[0] for x in overlay_items)):
        tier_items = sorted([x for x in overlay_items if x[0] == zt], key=lambda x: us_frame(x[2]))
        lanes = []  # each lane = [last_end_us, [segs]]
        for _, p, tl_s, dur_s, pop_anim, ckfs in tier_items:
            r_idx = zt * 100
            kfs = ckfs if ckfs is not None else (make_pop_in_kfs(kf_tpl, dur_s) if pop_anim else [])
            seg = make_vseg(p, tl_s, dur_s, src_s=0.0, render_idx=r_idx, kfs=kfs)
            st_u = seg["target_timerange"]["start"]
            en_u = st_u + seg["target_timerange"]["duration"]
            placed = False
            for ln in lanes:
                if st_u >= ln[0]:
                    ln[1].append(seg)
                    ln[0] = en_u
                    placed = True
                    break
            if not placed:
                lanes.append([en_u, [seg]])

        for li, (_, seg_list) in enumerate(lanes):
            tr_ov = copy.deepcopy(vtrack_tpl)
            tr_ov["id"] = uid()
            r_idx_lane = zt * 100 + li * 10
            for s in seg_list:
                s["render_index"] = r_idx_lane
            tr_ov["segments"] = seg_list
            D["tracks"].append(tr_ov)
            overlay_tracks_built += 1

    # ==========================================================================
    # 3. MULTI-TRACK AUDIO: CONAN BGM + 2 CHECKERBOARD VO TRACKS + NON-OVERLAPPING SFX TRACKS!
    # ==========================================================================
    # Audio Track A0: Detective Conan Main Theme BGM (exact match to user's CapCut placement & volume!)
    tr_bgm = copy.deepcopy(atrack_tpl)
    tr_bgm["id"] = uid()
    tr_bgm["segments"] = [
        make_aseg(CONAN_MP3, 0.000, total_dur_u / 1e6, src_s=0.000, vol=0.36, fi_us=66666, fo_us=900000)
    ]
    D["tracks"].append(tr_bgm)

    # Audio Tracks A1 & A2: Checkerboard Voiceover Stems (Micro-Fade Anti-Pop!)
    tr_vo1 = copy.deepcopy(atrack_tpl); tr_vo1["id"] = uid(); tr_vo1["segments"] = []
    tr_vo2 = copy.deepcopy(atrack_tpl); tr_vo2["id"] = uid(); tr_vo2["segments"] = []
    vo_idx = 0
    for s in tm["segments"]:
        if s["id"] == "s6c_storefront":
            continue
        wp = os.path.join(LAYERS_DIR, f"vo_{s['id']}.wav")
        aseg = make_aseg(wp, s["t0"], s["dur"], src_s=0.0, vol=1.22, fi_us=33333, fo_us=66666)
        if vo_idx % 2 == 0:
            tr_vo1["segments"].append(aseg)
        else:
            tr_vo2["segments"].append(aseg)
        vo_idx += 1
    D["tracks"].append(tr_vo1)
    D["tracks"].append(tr_vo2)

    # Audio Tracks A3..Ak: Synchronized Studio SFX Tracks!
    s2_0  = segs_tm["s2_table"]["t0"]
    s3_0  = segs_tm["s3_program"]["t0"]
    s4_0  = segs_tm["s4_questions"]["t0"]
    s5_0  = segs_tm["s5_gifts"]["t0"]
    s6a_0 = segs_tm["s6a_outro"]["t0"]
    s6b_0 = segs_tm["s6b_thumbs"]["t0"]
    s6c_0 = segs_tm["s6c_storefront"]["t0"]

    sfx_cues = [
        ("tlh_star_open", 0.12, 0.42),
        ("tlh_slap_crisp",1.40, 0.85),
        ("tlh_thud_wood", 1.40, 0.80),
        ("tlh_whip_turn", 3.06, 0.65),
        ("tlh_vine_boom", 3.10, 0.55),
        ("tlh_crickets",  3.18, 0.38),
        ("tlh_boing",     3.40, 0.52),

        ("tlh_whoosh_tvc",s2_0,        0.48),
        ("tlh_whip_turn", s2_0 + 1.53, 0.58),
        ("tlh_pop1",      s2_0 + 3.48, 0.58),
        ("tlh_boing",     s2_0 + 4.20, 0.55),
        ("sk_whoosh",     s2_0 + 4.91, 0.45),
        ("sk_shimmer",    s2_0 + 6.95, 0.48),

        ("tlh_star_open", s3_0 + 0.05, 0.48),
        ("tlh_swoosh",    s3_0 + 2.34, 0.44),
        ("tlh_swoosh",    s3_0 + 3.51, 0.44),
        ("tlh_whoosh_tvc",s3_0 + 4.68, 0.55),
        ("tlh_fireworks", s3_0 + 4.72, 0.52),
        ("tlh_yay_kids",  s3_0 + 4.82, 0.65),
        ("tlh_wow_anime", s3_0 + 6.15, 0.55),

        ("sk_whoosh",     s4_0 + 0.04, 0.45),
        ("tlh_swoosh",    s4_0 + 2.13, 0.48),
        ("tlh_pop1",      s4_0 + 3.32, 0.54),
        ("tlh_pop2",      s4_0 + 3.70, 0.54),
        ("tlh_pop1",      s4_0 + 4.08, 0.54),
        ("tlh_notif",     s4_0 + 4.46, 0.54),
        ("tlh_pop2",      s4_0 + 4.84, 0.54),
        ("tlh_boing",     s4_0 + 5.22, 0.60),

        ("tlh_whoosh_tvc",s5_0 + 0.04, 0.46),
        ("tlh_ting",      s5_0 + 0.88, 0.62),
        ("tlh_yeah_cheer",s5_0 + 0.92, 0.48),
        ("sk_whoosh",     s5_0 + 1.56, 0.46),
        ("tlh_swoosh",    s5_0 + 2.68, 0.44),
        ("tlh_swoosh",    s5_0 + 3.80, 0.44),
        ("sk_whoosh",     s5_0 + 4.92, 0.46),
        ("tlh_ting",      s5_0 + 7.72, 0.58),

        ("tlh_whoosh_tvc",s6a_0 + 0.04, 0.46),
        ("tlh_swoosh",    s6a_0 + 2.72, 0.48),
        ("tlh_swoosh",    s6a_0 + 4.32, 0.50),
        ("tlh_boing",     s6a_0 + 4.38, 0.58),
        ("tlh_wow_anime", s6a_0 + 4.55, 0.50),
        ("tlh_pop1",      s6b_0 + 0.04, 0.48),
        ("tlh_whoosh_tvc",s6c_0 + 0.02, 0.52),
        ("tlh_star_open", s6c_0 + 0.08, 0.50),
        ("tlh_yay_kids",  s6c_0 + 0.18, 0.48),
    ]

    sfx_lanes = []
    for key, ts, vol in sorted(sfx_cues, key=lambda x: us_frame(x[1])):
        if key not in SFX_SPECS:
            continue
        spath, st0, st1, _ = SFX_SPECS[key]
        if not os.path.isfile(spath):
            continue
        dur_sfx = max(0.25, st1 - st0)
        aseg = make_aseg(spath, ts, dur_sfx, src_s=st0, vol=vol, fi_us=15000, fo_us=33333)
        st_u = aseg["target_timerange"]["start"]
        en_u = st_u + aseg["target_timerange"]["duration"]
        placed = False
        for ln in sfx_lanes:
            if st_u >= ln[0]:
                ln[1].append(aseg)
                ln[0] = en_u
                placed = True
                break
        if not placed:
            sfx_lanes.append([en_u, [aseg]])

    for _, aseg_list in sfx_lanes:
        tr_s = copy.deepcopy(atrack_tpl)
        tr_s["id"] = uid()
        tr_s["segments"] = aseg_list
        D["tracks"].append(tr_s)

    D["duration"] = total_dur_u

    # ==========================================================================
    # 4. PACKAGE & DEPLOY TO CAPCUT DESKTOP (v193.0.0 NATIVE MULTI-TIMELINE STRUCTURE!)
    # ==========================================================================
    stage_dir = os.path.join(STAGE_ROOT, DRAFT_NAME)
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    os.makedirs(os.path.join(stage_dir, "video"), exist_ok=True)
    os.makedirs(os.path.join(stage_dir, "Resources"), exist_ok=True)

    cover_jpg = os.path.join(stage_dir, "draft_cover.jpg")
    shutil.copy2(os.path.join(PROJ_DIR, "check", "fc_v5_test_03.jpg"), cover_jpg)

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for fn_dc in ("draft_content.json", "template-2.tmp"):
        open(os.path.join(stage_dir, fn_dc), "wb").write(dc_bytes)

    open(os.path.join(stage_dir, "draft_settings"), "w", encoding="utf-8").write(
        f"[General]\ncloud_last_modify_platform=windows\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=180\nreal_edit_keys=12\n"
    )
    open(os.path.join(stage_dir, "key_value.json"), "w", encoding="utf-8").write("{}")
    open(os.path.join(stage_dir, "draft_biz_config.json"), "w", encoding="utf-8").write("")
    for aux in ["draft_agency_config.json", "performance_opt_info.json", "timeline_layout.json", "attachment_pc_common.json"]:
        sp = os.path.join(d_f20, aux)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(stage_dir, aux))

    ca_dir = os.path.join(stage_dir, "common_attachment")
    os.makedirs(ca_dir, exist_ok=True)
    open(os.path.join(ca_dir, "attachment_pc_timeline.json"), "w", encoding="utf-8").write(
        '{"reference_lines_config":{"horizontal_lines":[],"is_lock":false,"is_visible":false,"vertical_lines":[]},"safe_area_type":0}'
    )
    open(os.path.join(ca_dir, "attachment_action_scene.json"), "w", encoding="utf-8").write(
        '{"action_scene":{"removed_segments":[],"segment_infos":[]}}'
    )
    json.dump({
        "draft_materials": [],
        "draft_virtual_store": [
            {"type": 0, "value": [{"creation_time": 0, "display_name": "", "filter_type": 0, "id": "", "import_time": 0, "import_time_us": 0, "material_color_tag": "", "sort_sub_type": 0, "sort_type": 0, "subdraft_filter_type": 0}]},
            {"type": 1, "value": []}
        ]
    }, open(os.path.join(stage_dir, "draft_virtual_store.json"), "w", encoding="utf-8"))

    tl_root = os.path.join(stage_dir, "Timelines")
    tl_sub  = os.path.join(tl_root, tl_id)
    os.makedirs(tl_sub, exist_ok=True)
    for fn_dc in ("draft_content.json", "template-2.tmp"):
        open(os.path.join(tl_sub, fn_dc), "wb").write(dc_bytes)
    shutil.copy2(cover_jpg, os.path.join(tl_sub, "draft_cover.jpg"))
    if os.path.isfile(os.path.join(stage_dir, "attachment_pc_common.json")):
        shutil.copy2(os.path.join(stage_dir, "attachment_pc_common.json"), os.path.join(tl_sub, "attachment_pc_common.json"))
    shutil.copytree(ca_dir, os.path.join(tl_sub, "common_attachment"), dirs_exist_ok=True)

    json.dump({
        "config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False},
        "create_time": now_us, "id": tl_id, "main_timeline_id": tl_id,
        "timelines": [{"create_time": now_us, "id": tl_id, "is_marked_delete": False, "name": "Dòng thời gian 01", "update_time": now_us}],
        "update_time": now_us, "version": 0
    }, open(os.path.join(tl_root, "project.json"), "w", encoding="utf-8"), ensure_ascii=False)

    local_draft_dir = os.path.join(DRAFTS_DIR, DRAFT_NAME)
    M = copy.deepcopy(dm_f20)
    M.update({
        "draft_id": DRAFT_ID,
        "draft_name": DRAFT_NAME,
        "draft_fold_path": norm_fwd(local_draft_dir),
        "draft_root_path": norm_fwd(DRAFTS_DIR),
        "draft_cover": "draft_cover.jpg",
        "draft_new_version": "164.0.0",
        "tm_duration": total_dur_u,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "draft_timeline_materials_size_": referenced_bytes,
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "draft_materials": [
            {"type": 0, "value": dm_entries_type0},
            {"type": 1, "value": []}, {"type": 2, "value": []}, {"type": 3, "value": []},
            {"type": 6, "value": []}, {"type": 7, "value": []}, {"type": 8, "value": []}
        ]
    })
    json.dump(M, open(os.path.join(stage_dir, "draft_meta_info.json"), "w", encoding="utf-8"), ensure_ascii=False)

    if os.path.exists(local_draft_dir):
        shutil.rmtree(local_draft_dir)
    shutil.copytree(stage_dir, local_draft_dir)

    rm_path = os.path.join(DRAFTS_DIR, "root_meta_info.json")
    rm = json.load(open(rm_path, encoding="utf-8"))
    stores = [s for s in rm.get("all_draft_store", []) if s.get("draft_name") != DRAFT_NAME and s.get("draft_id") != DRAFT_ID]
    tpl_entry = copy.deepcopy(stores[0]) if stores else {}
    tpl_entry.update({
        "cloud_draft_cover": False, "cloud_draft_sync": False, "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "", "draft_cloud_template_id": "", "draft_cloud_tutorial_info": "", "draft_cloud_videocut_purchase_info": "",
        "draft_cover": norm_fwd(local_draft_dir) + "/draft_cover.jpg",
        "draft_fold_path": norm_fwd(local_draft_dir),
        "draft_id": DRAFT_ID,
        "draft_is_ai_shorts": False, "draft_is_cloud_temp_draft": False, "draft_is_infinite_canvas_draft": False,
        "draft_is_invisible": False, "draft_is_pippit_draft": False, "draft_is_web_article_video": False,
        "draft_json_file": norm_fwd(local_draft_dir) + "/draft_content.json",
        "draft_name": DRAFT_NAME, "draft_new_version": "164.0.0",
        "draft_root_path": norm_fwd(DRAFTS_DIR),
        "draft_timeline_materials_size": referenced_bytes,
        "streaming_edit_draft_ready": True,
        "tm_draft_cloud_completed": "", "tm_draft_cloud_entry_id": -1, "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1, "tm_draft_cloud_space_id": -1, "tm_draft_cloud_user_id": -1,
        "tm_draft_create": now_us, "tm_draft_modified": now_us, "tm_draft_removed": 0,
        "tm_duration": total_dur_u,
    })
    rm["all_draft_store"] = [tpl_entry] + stores
    json.dump(rm, open(rm_path, "w", encoding="utf-8"), ensure_ascii=False)

    print(f"SUCCESS! Built Full Multi-Layer CapCut Pro Draft: {DRAFT_NAME}", flush=True)
    print(f"  Total Duration : {total_dur_u / 1e6:.2f}s ({len(D['tracks'])} tracks total)", flush=True)
    print(f"  Overlay Tracks : {overlay_tracks_built} independent visual overlay tracks ({len(overlay_items)} overlay layers!)", flush=True)
    print(f"  Audio Tracks   : 1 Conan BGM + 2 Checkerboard VO + {len(sfx_lanes)} SFX tracks!", flush=True)

if __name__ == "__main__":
    main()
