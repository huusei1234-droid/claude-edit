import copy, json, math, os, shutil, subprocess, time, uuid

OUT_DIR    = r"d:\AI\full studio\output\feelchicken-food-cinematic"
RAW_CACHE  = os.path.join(OUT_DIR, "raw_cache")
SFX_DIR    = os.path.join(RAW_CACHE, "sfx")
SHOTS_DIR  = os.path.join(OUT_DIR, "shots_graded")
TITLE_DIR  = os.path.join(OUT_DIR, "titles_alpha")
CHECK_DIR  = os.path.join(OUT_DIR, "check")
STAGE_ROOT = os.path.join(OUT_DIR, "capcut_stage")
OVL_SRC    = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k"

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "FEEL_CHICKEN_Food_Cinematic_Pro"
DRAFT_ID   = "F94A82E1-63D4-4B89-9E12-7745C280B3A9"

FPS = 30.0

def uid():
    return str(uuid.uuid4()).upper()

def us_frame(sec):
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

def build_alpha_fx_overlays():
    """Convert black-bg 4K bokeh & flare MP4s to true ProRes 4444 alpha MOVs so CapCut renders pure additive glow with zero dark veil!"""
    fx_dir = os.path.join(OUT_DIR, "fx_alpha")
    os.makedirs(fx_dir, exist_ok=True)
    specs = [
        ("ov_warm_ember_alpha.mov", os.path.join(OVL_SRC, "10_Warm_Ember_Food_Glow_9x16.mp4"), 10.0),
        ("ov_golden_bokeh_alpha.mov", os.path.join(OVL_SRC, "01_Golden_Dust_Bokeh_9x16.mp4"), 5.0),
    ]
    out_paths = {}
    for out_fn, src_mp4, dur_s in specs:
        out_p = os.path.join(fx_dir, out_fn)
        if not os.path.exists(out_p):
            # Luma-key to smooth alpha: alpha = max(R,G,B), keeping bright golden glow & 0 alpha on black!
            vf = (
                f"fps=30,scale=1080:1920,format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='clip(max(r(X,Y),max(g(X,Y),b(X,Y)))*1.15-12,0,255)'"
            )
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-t", f"{dur_s:.2f}", "-i", src_mp4,
                "-vf", vf, "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                out_p
            ], check=True)
        out_paths[out_fn] = out_p
    return out_paths

def main():
    fx_movs = build_alpha_fx_overlays()
    manifest = json.load(open(os.path.join(OUT_DIR, "shots_manifest.json"), encoding="utf-8"))

    # Load native CapCut v193.0.0 templates from existing CapCut project on this machine
    d_f20 = os.path.join(DRAFTS_DIR, "FEEL_CHICKEN_2011_Full_Layers_V6")
    if not os.path.exists(os.path.join(d_f20, "draft_content.json")):
        d_f20 = os.path.join(DRAFTS_DIR, "F20 vd 1")
    dc_f20 = json.load(open(os.path.join(d_f20, "draft_content.json"), encoding="utf-8"))
    dm_f20 = json.load(open(os.path.join(d_f20, "draft_meta_info.json"), encoding="utf-8"))

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
    amat_tpl  = copy.deepcopy(dc_f20["materials"]["audios"][0])
    afade_tpl = copy.deepcopy(dc_f20["materials"]["audio_fades"][0])

    dm_vid_tpl = copy.deepcopy(next(x for g in dm_f20["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
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
        w, h, dur_s, has_aud = probe_media(path)
        dur_u = max(33333, us_frame(dur_s))
        mid = uid()
        lmid = str(uuid.uuid4())
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
        referenced_bytes += os.path.getsize(path)
        mat_cache[fwd] = (mid, dur_u)
        return mid, dur_u

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
        referenced_bytes += os.path.getsize(path)
        mat_cache[fwd] = (mid, dur_u)
        return mid, dur_u

    def make_vseg(path, tl_s, dur_s, src_s=0.0, render_idx=0, alpha=1.0, kfs=None):
        mid, mat_dur_u = register_visual_mat(path)
        st_u = us_frame(src_s)
        du_u = min(us_frame(dur_s), max(33333, mat_dur_u - st_u))
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
            "common_keyframes": kfs or [], "keyframe_refs": [],
            "render_index": render_idx, "track_render_index": 0, "visible": True,
        })
        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        seg["clip"]["alpha"] = float(alpha)
        seg["clip"]["rotation"] = 0.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        return seg

    def make_aseg(path, tl_s, dur_s, src_s=0.0, vol=1.0, fi_us=33333, fo_us=66666, kfs=None):
        mid, mat_dur_u = register_audio_mat(path)
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
            "common_keyframes": kfs or [], "keyframe_refs": [],
            "render_index": 0, "track_render_index": 1, "visible": True,
        })
        return seg

    # ==========================================================================
    # 1. TRACK V0: 23 GRADED CINEMA SHOTS (SEAMLESS 0.00 -> 38.50s, 0 GAPS!)
    # ==========================================================================
    tr_v0 = copy.deepcopy(vtrack_tpl)
    tr_v0["id"] = uid()
    tr_v0["segments"] = []
    cur_u = 0
    for item in manifest:
        dur_s = item["frames"] / FPS
        seg = make_vseg(item["path"], cur_u / 1e6, dur_s, src_s=0.0, render_idx=0, alpha=1.0)
        seg["target_timerange"]["start"] = cur_u
        tr_v0["segments"].append(seg)
        cur_u += seg["target_timerange"]["duration"]
    total_dur_u = cur_u
    D["tracks"].append(tr_v0)

    # ==========================================================================
    # 2. TRACK V1: WARM EMBER GOLDEN BOKEH OVERLAY (ALPHA PRORES 4444)
    # ==========================================================================
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid(); tr_v1["segments"] = []
    ember_mov = fx_movs["ov_warm_ember_alpha.mov"]
    for (es, ed, al) in [(8.95, 18.72, 0.34), (29.07, 38.50, 0.36)]:
        kfs_e = [make_kf_obj(kf_tpl, "KFTypeAlpha", [(0.0, 0.0), (0.35, al), (max(0.4, (ed-es)-0.45), al), (ed-es, 0.0)])]
        tr_v1["segments"].append(make_vseg(ember_mov, es, min(9.8, ed-es), 0.0, render_idx=100, alpha=al, kfs=kfs_e))
    D["tracks"].append(tr_v1)

    # ==========================================================================
    # 3. TRACK V2: 24K GOLDEN DUST BOKEH OVERLAY (ALPHA PRORES 4444)
    # ==========================================================================
    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid(); tr_v2["segments"] = []
    flare_mov = fx_movs["ov_golden_bokeh_alpha.mov"]
    for (fs, fd, al) in [(0.00, 3.80, 0.36), (8.85, 10.60, 0.40), (28.95, 31.10, 0.40), (34.45, 38.50, 0.36)]:
        kfs_f = [make_kf_obj(kf_tpl, "KFTypeAlpha", [(0.0, 0.0), (0.25, al), (max(0.3, (fd-fs)-0.40), al), (fd-fs, 0.0)])]
        tr_v2["segments"].append(make_vseg(flare_mov, fs, min(4.8, fd-fs), 0.0, render_idx=200, alpha=al, kfs=kfs_f))
    D["tracks"].append(tr_v2)

    # ==========================================================================
    # 4. TRACK V3: 9 ANIMATED 5-STOP METALLIC GOLD CINEMA TITLES (PRORES 4444)
    # ==========================================================================
    tr_v3 = copy.deepcopy(vtrack_tpl); tr_v3["id"] = uid(); tr_v3["segments"] = []
    title_specs = [
        ("T01_hook.mov",    0.15,  3.85),
        ("T02_craft.mov",   4.25,  8.75),
        ("T03_crispy.mov",  8.98, 14.95),
        ("T04_cheese.mov", 15.30, 18.60),
        ("T05_sauces.mov", 18.85, 23.40),
        ("T06_sides.mov",  23.62, 26.52),
        ("T07_crunch.mov", 26.68, 28.98),
        ("T08_feast.mov",  29.12, 34.32),
        ("T09_endcard.mov",34.49, 38.50),
    ]
    for t_fn, ts0, ts1 in title_specs:
        tr_v3["segments"].append(make_vseg(os.path.join(TITLE_DIR, t_fn), ts0, ts1 - ts0, 0.0, render_idx=300, alpha=1.0))
    D["tracks"].append(tr_v3)

    # ==========================================================================
    # 5. MULTI-TRACK AUDIO: BGM + FOOD ASMR + 2 CHECKERBOARD SFX LANES
    # ==========================================================================
    # Track A0: BGM Tasty Food (38s)
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid()
    tr_bgm["segments"] = [make_aseg(os.path.join(RAW_CACHE, "BGM_Tasty_Food_38s.mp3"), 0.0, 38.50, 0.0, vol=0.82, fi_us=120000, fo_us=450000)]
    D["tracks"].append(tr_bgm)

    # Track A1: Food ASMR (Frying Oil Sizzle, Sauce Glaze, Crispy Drumstick Crunch)
    tr_asmr = copy.deepcopy(atrack_tpl); tr_asmr["id"] = uid()
    asmr_events = [
        (os.path.join(SFX_DIR, "asmr_frying_pan.mp3"),    0.00, 1.60, 1.00, 0.50),
        (os.path.join(SFX_DIR, "asmr_frying_pan.mp3"),    8.90, 6.20, 2.50, 0.48),
        (os.path.join(SFX_DIR, "asmr_sauce_sticky.mp3"), 16.85, 1.75, 1.50, 0.30),
        (os.path.join(SFX_DIR, "asmr_liquid_pour.mp3"),  21.88, 1.70, 0.10, 0.38),
        (os.path.join(SFX_DIR, "asmr_crispy_crunch.mp3"),26.80, 1.00, 0.00, 0.62),
        (os.path.join(SFX_DIR, "asmr_crispy_crunch.mp3"),27.92, 1.15, 0.00, 0.92),
    ]
    tr_asmr["segments"] = [make_aseg(p, ts, du, ss, vol=v, fi_us=40000, fo_us=150000) for (p, ts, du, ss, v) in asmr_events]
    D["tracks"].append(tr_asmr)

    # Tracks A2..A3: Studio SFX packed cleanly with zero overlap!
    sfx_events = [
        (os.path.join(SFX_DIR, "sfx_magic_reveal.mp3"),   0.05, 2.20, 0.38),
        (os.path.join(SFX_DIR, "sfx_deep_woosh.mp3"),     2.45, 1.60, 0.32),
        (os.path.join(SFX_DIR, "sfx_text_swoosh.mp3"),    4.22, 0.90, 0.30),
        (os.path.join(SFX_DIR, "sfx_riser_metallic.mp3"), 6.50, 2.50, 0.42),
        (os.path.join(SFX_DIR, "sfx_whoosh_low_hit.mp3"), 8.88, 2.80, 0.50),
        (os.path.join(SFX_DIR, "sfx_whoosh_cine.mp3"),   15.18, 1.60, 0.34),
        (os.path.join(SFX_DIR, "sfx_deep_woosh.mp3"),    18.62, 1.80, 0.38),
        (os.path.join(SFX_DIR, "sfx_text_swoosh.mp3"),   23.56, 0.90, 0.30),
        (os.path.join(SFX_DIR, "sfx_whoosh_cine.mp3"),   26.52, 1.50, 0.32),
        (os.path.join(SFX_DIR, "sfx_riser_metallic.mp3"),26.65, 2.45, 0.35),
        (os.path.join(SFX_DIR, "sfx_whoosh_low_hit.mp3"),28.98, 2.80, 0.52),
        (os.path.join(SFX_DIR, "sfx_deep_woosh.mp3"),    34.38, 1.80, 0.38),
        (os.path.join(SFX_DIR, "sfx_shimmer_gold.mp3"),  34.68, 2.40, 0.40),
        (os.path.join(SFX_DIR, "sfx_chime_warm.mp3"),    35.05, 2.20, 0.34),
    ]
    sfx_lanes = []
    for p, ts, du, v in sorted(sfx_events, key=lambda x: x[1]):
        seg = make_aseg(p, ts, du, 0.0, vol=v, fi_us=33333, fo_us=120000)
        st_u = seg["target_timerange"]["start"]
        en_u = st_u + seg["target_timerange"]["duration"]
        placed = False
        for lane in sfx_lanes:
            if st_u >= lane[0] + 33333:
                lane[1].append(seg)
                lane[0] = en_u
                placed = True
                break
        if not placed:
            sfx_lanes.append([en_u, [seg]])

    for _, segs in sfx_lanes:
        tr_s = copy.deepcopy(atrack_tpl); tr_s["id"] = uid(); tr_s["segments"] = segs
        D["tracks"].append(tr_s)

    D["duration"] = total_dur_u

    # ==========================================================================
    # 6. PACKAGE & DEPLOY TO CAPCUT DESKTOP
    # ==========================================================================
    stage_dir = os.path.join(STAGE_ROOT, DRAFT_NAME)
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    os.makedirs(os.path.join(stage_dir, "video"), exist_ok=True)
    os.makedirs(os.path.join(stage_dir, "Resources"), exist_ok=True)

    cover_jpg = os.path.join(stage_dir, "draft_cover.jpg")
    shutil.copy2(os.path.join(CHECK_DIR, "qc23_S20.jpg"), cover_jpg)

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for fn_dc in ("draft_content.json", "template-2.tmp"):
        open(os.path.join(stage_dir, fn_dc), "wb").write(dc_bytes)

    open(os.path.join(stage_dir, "draft_settings"), "w", encoding="utf-8").write(
        f"[General]\ncloud_last_modify_platform=windows\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=240\nreal_edit_keys=18\n"
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
        "draft_id": DRAFT_ID, "draft_name": DRAFT_NAME,
        "draft_fold_path": norm_fwd(local_draft_dir), "draft_root_path": norm_fwd(DRAFTS_DIR),
        "draft_cover": "draft_cover.jpg", "draft_new_version": "164.0.0",
        "tm_duration": total_dur_u, "tm_draft_create": now_us, "tm_draft_modified": now_us,
        "draft_timeline_materials_size_": referenced_bytes,
        "cloud_draft_cover": False, "cloud_draft_sync": False, "draft_cloud_last_action_download": False,
        "tm_draft_cloud_completed": "", "tm_draft_cloud_entry_id": -1, "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1, "tm_draft_cloud_space_id": -1, "tm_draft_cloud_user_id": -1,
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

    # STRICT INTEGRITY AUDIT (0 missing files, 0 overlaps!)
    missing = [m["path"] for m in D["materials"]["videos"] + D["materials"]["audios"] if not os.path.exists(m["path"])]
    overlaps = 0
    for ti, tr in enumerate(D["tracks"]):
        segs = sorted(tr["segments"], key=lambda s: s["target_timerange"]["start"])
        for a, b in zip(segs, segs[1:]):
            if a["target_timerange"]["start"] + a["target_timerange"]["duration"] > b["target_timerange"]["start"]:
                overlaps += 1

    print(f"CAPCUT PRO DRAFT DEPLOYED: {local_draft_dir}")
    print(f"  Duration : {total_dur_u/1e6:.2f}s | Total Tracks: {len(D['tracks'])} (4 Visual + {len(D['tracks'])-4} Audio)")
    print(f"  Audit    : Missing files = {len(missing)} | Track overlaps = {overlaps}")

if __name__ == "__main__":
    main()
