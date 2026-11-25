import copy, json, os, shutil, subprocess, time, uuid

PROJ_DIR   = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
STAGE_ROOT = os.path.join(PROJ_DIR, "capcut_stage_colorgrade_v3")
DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
BASE_NAME  = "FEEL_CHICKEN_KiemTraMieng_2011_Kute"

FC_GOC      = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC"
THU_MUC_MOI = os.path.join(FC_GOC, "16-11-2026", "Thư mục mới")
DIR_1611    = os.path.join(FC_GOC, "16-11-2026")
BROLL_2610  = os.path.join(FC_GOC, "261015")
BROLL_2609  = os.path.join(FC_GOC, "260927")
BROLL_0603  = os.path.join(FC_GOC, "20260603")

def uid():
    return str(uuid.uuid4()).upper()

def us(sec):
    return int(round(float(sec) * 30.0) * 1_000_000 // 30)

def norm_fwd(p):
    return os.path.normpath(p).replace("\\", "/")

def probe_capcut_media(path):
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

def main():
    # Exact V3 1-Track Raw-Source-Only sequence from FILE GỐC for instant synchronized color grading!
    RAW_CLIPS = [
        (os.path.join(THU_MUC_MOI, "C3938.MP4"),    3.20, 4.567), # Cảnh 1: Khang đập bàn gọi Thành (đã cắt sát 00:05)
        (os.path.join(THU_MUC_MOI, "C3942.MP4"),    2.22, 8.900), # Cảnh 2: Khang ngồi bàn kể chuyện kiểm tra miệng
        (os.path.join(BROLL_0603,  "C9598.MP4"),    0.80, 2.340), # Cảnh 3A: Khách gọi món tại quầy Feel Chicken
        (os.path.join(BROLL_0603,  "C9616.MP4"),    1.40, 2.340), # Cảnh 3A: Bàn tiệc Feel Chicken
        (os.path.join(DIR_1611,    "C3960.MP4"),    0.00, 5.880), # Cảnh 4: Khang giới thiệu bộ câu hỏi (đã cắt sát 00:28)
        (os.path.join(THU_MUC_MOI, "C3956.MP4"),    1.88, 1.560), # Cảnh 5A: Khang "Trả lời đúng — CÓ QUÀ!"
        (os.path.join(BROLL_0603,  "C9604.MP4"),    1.20, 1.550), # Cảnh 5B: Mâm gà sốt Hàn Quốc thực tế
        (os.path.join(BROLL_2610,  "C3490.MP4"),    1.00, 1.560), # Cảnh 5B: Mâm gà 4 vị + tokbokki thực tế
        (os.path.join(THU_MUC_MOI, "C3956.MP4"),    6.55, 4.230), # Cảnh 5C: Khang đọc trọn "cho đến hết ngày 20/11!"
        (os.path.join(BROLL_2609,  "IMG_6494.MOV"), 0.50, 1.750), # Cảnh 6A: Xé đùi gà giòn tan
        (os.path.join(BROLL_2609,  "IMG_6495.MOV"), 1.30, 1.700), # Cảnh 6A: Cận bạn trẻ cắn gà giòn tan
        (os.path.join(THU_MUC_MOI, "C3957.MP4"),    1.40, 1.800), # Cảnh 6B: Khang giơ ngón cái chốt câu cuối
        (os.path.join(BROLL_0603,  "C9596.MP4"),    0.40, 2.400), # Cảnh 6C: Mặt tiền quán Feel Chicken từ FILE GỐC
    ]
    for p, _, _ in RAW_CLIPS:
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Missing raw file: {p}")

    existing_dir = os.path.join(DRAFTS_DIR, BASE_NAME)
    locked = os.path.exists(os.path.join(existing_dir, ".locked"))
    dc_existing = os.path.join(existing_dir, "draft_content.json")
    # Protect user color edits if touched after 11:38 AM local!
    user_edited = False
    if os.path.exists(dc_existing):
        lt = time.localtime(os.path.getmtime(dc_existing))
        if (lt.tm_hour, lt.tm_min) > (11, 38):
            user_edited = True

    if locked or user_edited:
        draft_name = "FEEL_CHICKEN_KiemTraMieng_2011_V3_SourceGoc"
        draft_id   = "8DE712A3-5F21-4891-BDE8-7142C288109A"
    else:
        draft_name = BASE_NAME
        draft_id   = "6BC500C1-3D15-4024-ACD6-9534A199398F"

    stage_dir = os.path.join(STAGE_ROOT, draft_name)
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    os.makedirs(os.path.join(stage_dir, "video"), exist_ok=True)
    os.makedirs(os.path.join(stage_dir, "Resources"), exist_ok=True)

    d1117_dir = os.path.join(DRAFTS_DIR, "1117")
    dc_1117   = json.load(open(os.path.join(d1117_dir, "draft_content.json"), encoding="utf-8"))
    dc_htpm   = json.load(open(os.path.join(DRAFTS_DIR, "HTPM", "draft_content.json"), encoding="utf-8"))
    dm_htpm   = json.load(open(os.path.join(DRAFTS_DIR, "HTPM", "draft_meta_info.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(next(tr for tr in dc_1117["tracks"] if tr["type"] == "video"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    vmat_tpl   = copy.deepcopy(dc_htpm["materials"]["videos"][0])
    dm_mat_tpl = copy.deepcopy(dm_htpm["draft_materials"][0]["value"][0])

    extra_keys  = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl = {k: copy.deepcopy(next(x for x in dc_1117["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_1117["materials"].get(k, []))}

    tl_id  = uid()
    now_s  = int(time.time())
    now_us = int(time.time() * 1_000_000)

    D = copy.deepcopy(dc_1117)
    D.update({
        "id": tl_id, "name": draft_name, "fps": 30.0, "duration": 0,
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_1117["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })

    vmat_cache = {}
    draft_mat_entries = []
    referenced_bytes = 0

    def add_raw_video(src_path):
        nonlocal referenced_bytes
        fwd_p = norm_fwd(src_path)
        if fwd_p in vmat_cache:
            return vmat_cache[fwd_p]
        fn = os.path.basename(src_path)
        w, h, dur_s, has_aud = probe_capcut_media(src_path)
        dur_u = us(dur_s)
        mid = uid()
        lmid = str(uuid.uuid4())
        m = copy.deepcopy(vmat_tpl)
        m.update({
            "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
            "type": "video", "path": fwd_p, "media_path": "", "local_id": "",
            "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud)
        })
        D["materials"]["videos"].append(m)

        dme = copy.deepcopy(dm_mat_tpl)
        dme.update({
            "id": lmid, "file_Path": fwd_p, "extra_info": fn,
            "duration": dur_u, "width": w, "height": h,
            "metetype": "video", "item_source": 1,
            "import_time": now_s, "import_time_ms": now_s * 1000,
            "roughcut_time_range": {"start": 0, "duration": dur_u},
            "sub_time_range": {"start": -1, "duration": -1},
        })
        draft_mat_entries.append(dme)
        try:
            referenced_bytes += os.path.getsize(src_path)
        except Exception:
            pass
        vmat_cache[fwd_p] = (mid, dur_u)
        return mid, dur_u

    tr_v0 = copy.deepcopy(vtrack_tpl)
    tr_v0["id"] = uid()
    tr_v0["segments"] = []

    cur_u = 0
    for src_p, in_s, dur_s in RAW_CLIPS:
        mid, mat_dur_u = add_raw_video(src_p)
        in_u = us(in_s)
        du_u = min(us(dur_s), mat_dur_u - in_u)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": in_u, "duration": du_u},
            "target_timerange": {"start": cur_u, "duration": du_u},
            "speed": 1.0, "volume": 1.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [],
            "render_index": 0, "track_render_index": 0,
        })
        seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": 1.0}
        tr_v0["segments"].append(seg)
        cur_u += du_u

    D["tracks"] = [tr_v0]
    D["duration"] = cur_u

    cover_jpg = os.path.join(stage_dir, "draft_cover.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "0.6",
        "-i", os.path.join(BROLL_0603, "C9596.MP4"),
        "-frames:v", "1", "-vf", "scale=540:960:force_original_aspect_ratio=increase,crop=540:960", cover_jpg
    ], check=True)

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for fn_dc in ("draft_content.json", "template-2.tmp"):
        open(os.path.join(stage_dir, fn_dc), "wb").write(dc_bytes)

    open(os.path.join(stage_dir, "draft_settings"), "w", encoding="utf-8").write(
        f"[General]\ncloud_last_modify_platform=windows\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=60\nreal_edit_keys=1\n"
    )
    open(os.path.join(stage_dir, "key_value.json"), "w", encoding="utf-8").write("{}")
    open(os.path.join(stage_dir, "draft_biz_config.json"), "w", encoding="utf-8").write("")
    for aux in ["draft_agency_config.json", "performance_opt_info.json", "timeline_layout.json", "attachment_pc_common.json"]:
        sp = os.path.join(d1117_dir, aux)
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

    local_draft_dir = os.path.join(DRAFTS_DIR, draft_name)
    M = copy.deepcopy(dm_htpm)
    M.update({
        "draft_id": draft_id,
        "draft_name": draft_name,
        "draft_fold_path": norm_fwd(local_draft_dir),
        "draft_root_path": norm_fwd(DRAFTS_DIR),
        "draft_cover": "draft_cover.jpg",
        "draft_new_version": "164.0.0",
        "tm_duration": cur_u,
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
            {"type": 0, "value": draft_mat_entries},
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
    stores = [s for s in rm.get("all_draft_store", []) if s.get("draft_name") != draft_name and s.get("draft_id") != draft_id]
    tpl_entry = copy.deepcopy(stores[0]) if stores else {}
    tpl_entry.update({
        "cloud_draft_cover": False, "cloud_draft_sync": False, "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "", "draft_cloud_template_id": "", "draft_cloud_tutorial_info": "", "draft_cloud_videocut_purchase_info": "",
        "draft_cover": norm_fwd(local_draft_dir) + "/draft_cover.jpg",
        "draft_fold_path": norm_fwd(local_draft_dir),
        "draft_id": draft_id,
        "draft_is_ai_shorts": False, "draft_is_cloud_temp_draft": False, "draft_is_infinite_canvas_draft": False,
        "draft_is_invisible": False, "draft_is_pippit_draft": False, "draft_is_web_article_video": False,
        "draft_json_file": norm_fwd(local_draft_dir) + "/draft_content.json",
        "draft_name": draft_name, "draft_new_version": "164.0.0",
        "draft_root_path": norm_fwd(DRAFTS_DIR),
        "draft_timeline_materials_size": referenced_bytes,
        "streaming_edit_draft_ready": True,
        "tm_draft_cloud_completed": "", "tm_draft_cloud_entry_id": -1, "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1, "tm_draft_cloud_space_id": -1, "tm_draft_cloud_user_id": -1,
        "tm_draft_create": now_us, "tm_draft_modified": now_us, "tm_draft_removed": 0,
        "tm_duration": cur_u,
    })
    rm["all_draft_store"] = [tpl_entry] + stores
    json.dump(rm, open(rm_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"Updated V3 1-Track Raw-Source CapCut Draft -> {draft_name} ({len(RAW_CLIPS)} raw segments, {cur_u/1e6:.2f}s)!", flush=True)

if __name__ == "__main__":
    main()
