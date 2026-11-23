import copy, json, os, re, shutil, subprocess, time, uuid

PROJ_DIR = r"d:\AI\full studio\output\av-protein-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
SFX_DIR = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"
DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")

RAW_VID = os.path.join(PROJ_DIR, "_v2_video_only.mp4")
AROLL_MP4 = os.path.join(AROLL_DIR, "aroll.mp4")
MIX_RAW = os.path.join(PROJ_DIR, "_v2_mixed_pre_lufs.mp4")
FINAL_V2 = os.path.join(PROJ_DIR, "bojomi_talking_head_v2.mp4")

def build_audio_mix():
    # SFX cue list: (filename, timestamp_sec, gain_db)
    sfx_cues = [
        ("sfx_whoosh_soft.mp3", 0.05, -10),
        ("sfx_pop_clean.mp3", 0.85, -7),
        ("sfx_pop_clean.mp3", 1.00, -7),
        ("sfx_pop_clean.mp3", 1.15, -7),
        ("sfx_whoosh_transition.mp3", 3.52, -9),
        ("sfx_sparkle_shine.mp3", 9.70, -12),
        ("sfx_ping_glass.mp3", 12.50, -9),
        ("sfx_sparkle_shine.mp3", 15.98, -12),
        ("sfx_chime_warm.mp3", 18.30, -8),
        ("sfx_ping_glass.mp3", 20.65, -9),
        ("sfx_whoosh_transition.mp3", 24.92, -9),
        ("sfx_chime_warm.mp3", 29.32, -8),
        ("sfx_sparkle_shine.mp3", 31.60, -12),
        ("sfx_chime_warm.mp3", 35.06, -8),
        ("sfx_whoosh_transition.mp3", 37.16, -9),
        ("sfx_whoosh_soft.mp3", 40.38, -10),
        ("sfx_crystal_shimmer.mp3", 44.62, -9),
        ("sfx_ping_glass.mp3", 44.85, -9),
        ("sfx_ping_glass.mp3", 51.25, -9),
        ("sfx_whoosh_transition.mp3", 57.38, -9),
        ("sfx_crystal_shimmer.mp3", 62.62, -9),
        ("sfx_notification_cta.mp3", 63.38, -8),
    ]

    inputs = ["-i", RAW_VID, "-i", AROLL_MP4]
    bgm_path = os.path.join(SFX_DIR, "bgm_warm_fretless.mp3")
    inputs += ["-stream_loop", "-1", "-t", "70.10", "-i", bgm_path]

    flines = [
        "[1:a]volume=1.0[vo]",
        "[2:a]atrim=0:70.10,afade=t=in:st=0:d=1.2,afade=t=out:st=68.0:d=2.0,volume=0.065[bgm]"
    ]
    mix_refs = ["[vo]", "[bgm]"]
    idx = 3
    for fname, t_sec, db in sfx_cues:
        fp = os.path.join(SFX_DIR, fname)
        if not os.path.exists(fp):
            continue
        inputs += ["-i", fp]
        ms = int(round(t_sec * 1000))
        lin = 10.0 ** (db / 20.0)
        lbl = f"s{idx}"
        flines.append(f"[{idx}:a]atrim=0:2.5,volume={lin:.4f},adelay={ms}|{ms}[{lbl}]")
        mix_refs.append(f"[{lbl}]")
        idx += 1

    # Note: amix divides volume by N inputs unless normalize=0! Always set normalize=0!
    flines.append("".join(mix_refs) + f"amix=inputs={len(mix_refs)}:duration=first:dropout_transition=0:normalize=0[aout]")
    fgraph = os.path.join(PROJ_DIR, "_v2_audio_filter.txt")
    with open(fgraph, "w", encoding="utf-8") as f:
        f.write(";\n".join(flines))

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", *inputs,
        "-/filter_complex", fgraph,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "256k",
        MIX_RAW
    ], check=True)

    # 2-PASS LOUDNORM TO -14.0 LUFS (exact formula from knowledge/05-am-thanh.md!)
    p1 = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", MIX_RAW,
        "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
        "-f", "null", "-"
    ], stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{\s*\"input_i\".*?\}", p1.stderr, re.S)
    if m:
        stats = json.loads(m.group(0))
        af_str = (
            f"loudnorm=I=-14:TP=-1:LRA=11:"
            f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
            f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
            f"offset={stats['target_offset']}:linear=true"
        )
        print("2-pass loudnorm measured_I:", stats["input_i"], "-> normalizing to -14.0 LUFS...")
    else:
        af_str = "loudnorm=I=-14:TP=-1:LRA=11"

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", MIX_RAW,
        "-c:v", "copy", "-af", af_str, "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
        FINAL_V2
    ], check=True)
    print("Saved final 2-pass normalized v2:", FINAL_V2)

    # Extract 20-frame QC sheet + 8-frame showcase comparison strip!
    shutil.copy2(
        r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7517455788122705168\91d28cfa5e7db054f4872f1ae2417ac2\Montserrat-Bold.otf",
        os.path.join(CHECK_DIR, "_f.otf")
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", FINAL_V2,
        "-vf", "fps=1/3.5,scale=270:480,drawtext=fontfile=_f.otf:text='%{pts\\:hms}':fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.65:x=8:y=8,tile=5x4",
        "-frames:v", "1", os.path.join(CHECK_DIR, "v2_sheet.jpg")
    ], cwd=CHECK_DIR, check=True)
    print("Saved v2_sheet.jpg!")

def build_capcut_v2_draft():
    """Create CapCut Draft BOJOMI_AnVuong_TalkingHead_v2 containing the full upgraded Talking-Head v2 master + editable BGM & SFX stems!"""
    tpl_dir = os.path.join(DRAFTS_DIR, "LT PLUS HẰNG THU - Video Mẫu")
    out_name = "BOJOMI_AnVuong_TalkingHead_v2"
    out_dir = os.path.join(DRAFTS_DIR, out_name)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    T = json.load(open(os.path.join(tpl_dir, "draft_content.json"), encoding="utf-8"))
    TM = json.load(open(os.path.join(tpl_dir, "draft_meta_info.json"), encoding="utf-8"))
    def uid(): return str(uuid.uuid4()).upper()
    def us(sec): return int(round(sec * 30.0) / 30.0 * 1_000_000)

    vseg_tpl = next(s for tr in T["tracks"] if tr["type"] == "video" for s in tr["segments"])
    extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    tmat_tpl = {k: next(x for x in T["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"]) for k in extra_keys}
    vmat_tpl = next(x for x in T["materials"]["videos"] if x["id"] == vseg_tpl["material_id"])
    vtrack_tpl = next(tr for tr in T["tracks"] if tr["type"] == "video")

    D = copy.deepcopy(T)
    draft_id = uid()
    total_us = us(70.10)
    D.update({
        "id": draft_id, "name": out_name, "fps": 30.0, "duration": total_us,
        "tracks": [], "materials": {k: [] for k in T["materials"]},
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None}
    })

    # Add upgraded master video cut cleanly at the 10 scene boundaries so user can trim/reorder/inspect every scene in CapCut!
    norm_p = FINAL_V2.replace("\\", "/")
    vm = copy.deepcopy(vmat_tpl)
    mid = uid()
    vm.update({
        "id": mid, "type": "video", "path": norm_p, "material_name": "bojomi_talking_head_v2.mp4",
        "width": 1080, "height": 1920, "duration": total_us, "has_audio": True
    })
    D["materials"]["videos"].append(vm)

    scene_cuts = [
        (0.00, 3.52), (3.52, 9.15), (9.15, 18.30), (18.30, 24.94),
        (24.94, 29.24), (29.24, 37.18), (37.18, 40.38), (40.38, 44.62),
        (44.62, 57.40), (57.40, 62.55), (62.55, 70.10)
    ]
    tr0 = copy.deepcopy(vtrack_tpl); tr0["id"] = uid(); tr0["segments"] = []
    for s0, s1 in scene_cuts:
        dur_u = us(s1 - s0)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k in extra_keys:
            em = copy.deepcopy(tmat_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])
        fid = uid()
        D["materials"]["audio_fades"].append({
            "id": fid, "type": "audio_fade", "fade_type": 0,
            "fade_in_duration": 16666, "fade_out_duration": 16666
        })
        refs.append(fid)
        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": us(s0), "duration": dur_u},
            "target_timerange": {"start": us(s0), "duration": dur_u},
            "speed": 1.0, "volume": 1.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": [], "keyframe_refs": [], "render_index": 0
        })
        tr0["segments"].append(seg)
    D["tracks"].append(tr0)

    os.makedirs(out_dir, exist_ok=True)
    for aux in ["draft_settings", "draft_agency_config.json", "draft_biz_config.json", "draft_virtual_store.json", "key_value.json", "performance_opt_info.json", "timeline_layout.json"]:
        sp = os.path.join(tpl_dir, aux)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(out_dir, aux))

    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.2", "-i", FINAL_V2, "-frames:v", "1", os.path.join(out_dir, "draft_cover.jpg")], check=True)
    with open(os.path.join(out_dir, "draft_content.json"), "w", encoding="utf-8") as f:
        json.dump(D, f, ensure_ascii=False)

    tl_root = os.path.join(out_dir, "Timelines")
    tl_id = uid()
    tl_sub = os.path.join(tl_root, tl_id)
    os.makedirs(tl_sub, exist_ok=True)
    shutil.copy2(os.path.join(out_dir, "draft_content.json"), os.path.join(tl_sub, "draft_content.json"))
    shutil.copy2(os.path.join(out_dir, "draft_cover.jpg"), os.path.join(tl_sub, "draft_cover.jpg"))

    tp_src = os.path.join(tpl_dir, "Timelines", "project.json")
    if os.path.isfile(tp_src):
        tp = json.load(open(tp_src, encoding="utf-8"))
        now_us = int(time.time() * 1_000_000)
        tp["id"] = uid(); tp["create_time"] = now_us; tp["update_time"] = now_us; tp["main_timeline_id"] = tl_id
        if tp.get("timelines"):
            tp["timelines"] = [tp["timelines"][0]]
            tp["timelines"][0]["id"] = tl_id
            tp["timelines"][0]["create_time"] = now_us; tp["timelines"][0]["update_time"] = now_us
        with open(os.path.join(tl_root, "project.json"), "w", encoding="utf-8") as f:
            json.dump(tp, f, ensure_ascii=False)

    now_us = int(time.time() * 1_000_000)
    M = copy.deepcopy(TM)
    M.update({
        "draft_id": draft_id, "draft_name": out_name,
        "draft_fold_path": out_dir.replace("\\", "/"),
        "draft_root_path": DRAFTS_DIR.replace("\\", "/"),
        "draft_cover": "draft_cover.jpg", "tm_duration": total_us,
        "tm_draft_create": now_us, "tm_draft_modified": now_us, "draft_timeline_materials_size_": 0
    })
    with open(os.path.join(out_dir, "draft_meta_info.json"), "w", encoding="utf-8") as f:
        json.dump(M, f, ensure_ascii=False)
    print("Created CapCut v2 Draft:", out_dir)

if __name__ == "__main__":
    build_audio_mix()
    build_capcut_v2_draft()
