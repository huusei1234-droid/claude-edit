import copy, json, os, shutil, subprocess, sys, time, uuid

PROJ_DIR   = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
STAGE_ROOT = os.path.join(PROJ_DIR, "capcut_stage_raw")
DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "FEEL_CHICKEN_KiemTraMieng_2011_Kute"

# Direct Source Folders on Z:\
THU_MUC_MOI = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC\16-11-2026\Thư mục mới"
BROLL_2610  = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC\261015"
BROLL_2609  = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC\260927"
TLH_ROOT    = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH"
TLH_SFX_DIR = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
AUDIO_OUT_Z = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC\16-11-2026\Audio_Da_Xu_Ly_2011"
SKILL_AUDIO = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"

FONT_MONTS_ID   = "7517455788122705168"
FONT_MONTS_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7517455788122705168/91d28cfa5e7db054f4872f1ae2417ac2/Montserrat-Bold.otf"
FONT_OSWALD_ID  = "7182504807289065985"
FONT_OSWALD_PATH= "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7182504807289065985/0a5333de6f4d592cb2d2390d68b31efb/Oswald-Bold.ttf"

sys.path.insert(0, PROJ_DIR)
from step3b_render_fc_kute import build_caption_groups, GOLD_KEYWORDS, CORAL_KEYWORDS

def uid():
    return str(uuid.uuid4()).upper()

def us(sec):
    return int(round(float(sec) * 30.0) * 1_000_000 // 30)

def norm_fwd(p):
    return os.path.normpath(p).replace("\\", "/")

def probe_capcut_media(path):
    """Probes media and swaps width/height when rotation is +-90/270, matching CapCut v193.0.0 native behavior!"""
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

def build_rich_styles(full_text, highlights, base_rgb, hi_rgb, font_id, font_path, size_val, stroke_w=0.08):
    n = len(full_text)
    if n == 0:
        return []
    is_hi = [False] * n
    for kw in highlights:
        if not kw:
            continue
        start = 0
        while True:
            idx = full_text.lower().find(kw.lower(), start)
            if idx < 0:
                break
            for k in range(idx, min(n, idx + len(kw))):
                is_hi[k] = True
            start = idx + len(kw)
    spans = []
    cur_f = is_hi[0]
    s_i = 0
    for i in range(1, n):
        if is_hi[i] != cur_f:
            spans.append((s_i, i, cur_f))
            s_i = i
            cur_f = is_hi[i]
    spans.append((s_i, n, cur_f))

    styles = []
    for r0, r1, hi in spans:
        col = hi_rgb if hi else base_rgb
        styles.append({
            "fill": {"content": {"render_type": "solid", "solid": {"color": list(col)}}},
            "font": {"path": font_path, "id": font_id},
            "size": float(size_val), "bold": True, "useLetterColor": True,
            "strokes": [{"content": {"render_type": "solid", "solid": {"color": [0.10, 0.04, 0.06]}}, "width": float(stroke_w), "mode": 0}],
            "shadows": [{
                "thickness_projection_angle": -45, "thickness_projection_enable": False,
                "diffuse": 0.16, "alpha": 0.80, "distance": 6,
                "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
                "angle": -45, "thickness_projection_distance": 0
            }],
            "range": [r0, r1]
        })
    return styles

def make_scale_keyframes(dur_us, s0, s1):
    out = []
    for prop in ("KFTypeScaleX", "KFTypeScaleY"):
        out.append({
            "id": uid(), "material_id": "", "property_type": prop,
            "keyframe_list": [
                {"id": uid(), "curveType": "Line", "time_offset": 0, "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "values": [float(s0)], "string_value": "", "graphID": ""},
                {"id": uid(), "curveType": "Line", "time_offset": int(dur_us), "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "values": [float(s1)], "string_value": "", "graphID": ""},
            ]
        })
    return out

def main():
    # 0. Back up user's current CapCut draft before touching anything!
    local_draft_dir = os.path.join(DRAFTS_DIR, DRAFT_NAME)
    bak_dir = os.path.join(PROJ_DIR, "backup_user_draft_1105")
    if os.path.exists(local_draft_dir):
        os.makedirs(bak_dir, exist_ok=True)
        for fn in ("draft_content.json", "draft_meta_info.json"):
            sp = os.path.join(local_draft_dir, fn)
            if os.path.isfile(sp):
                shutil.copy2(sp, os.path.join(bak_dir, fn))
        print("Backed up current CapCut draft JSONs ->", bak_dir, flush=True)

    # 1. Stage processed Voiceover WAVs + 2 C-Major BGMs cleanly into Z:\...\16-11-2026\Audio_Da_Xu_Ly_2011
    os.makedirs(AUDIO_OUT_Z, exist_ok=True)
    ui_dir = os.path.join(PROJ_DIR, "capcut_ui_assets")
    for fn in sorted(os.listdir(ui_dir)):
        if fn.startswith("vo_") and fn.endswith(".wav"):
            shutil.copy2(os.path.join(ui_dir, fn), os.path.join(AUDIO_OUT_Z, fn))
    for bgm_fn in ("bgm_warm_fretless.mp3", "bgm_sunny_carefree.mp3"):
        shutil.copy2(os.path.join(SKILL_AUDIO, bgm_fn), os.path.join(AUDIO_OUT_Z, bgm_fn))
    for sfx_fn in ("sfx_sparkle_shine.mp3", "sfx_crystal_shimmer.mp3", "sfx_whoosh_soft.mp3"):
        shutil.copy2(os.path.join(SKILL_AUDIO, sfx_fn), os.path.join(AUDIO_OUT_Z, sfx_fn))
    print("Synced clean Voice & BGM stems ->", AUDIO_OUT_Z, flush=True)

    # 2. Verify every single raw video & meme image exists on Z:\
    RAW = {
        "C3938":     os.path.join(THU_MUC_MOI, "C3938.MP4"),
        "C3942":     os.path.join(THU_MUC_MOI, "C3942.MP4"),
        "C3948":     os.path.join(THU_MUC_MOI, "C3948.MP4"),
        "C3956":     os.path.join(THU_MUC_MOI, "C3956.MP4"),
        "C3957":     os.path.join(THU_MUC_MOI, "C3957.MP4"),
        "LUU_NGAY":  os.path.join(TLH_ROOT,    "Lưu ngày địa chỉ lại nhé .mp4"),
        "MEME_1":    os.path.join(TLH_ROOT,    "Meme_KiemTraMieng_01_NuaLop.jpg"),
        "MEME_2":    os.path.join(TLH_ROOT,    "Meme_KiemTraMieng_02_DuaThu5.jpg"),
        "C3471":     os.path.join(BROLL_2610,  "C3471.MP4"),
        "C3488":     os.path.join(BROLL_2610,  "C3488.MP4"),
        "C3489":     os.path.join(BROLL_2610,  "C3489.MP4"),
        "C3490":     os.path.join(BROLL_2610,  "C3490.MP4"),
        "C3492":     os.path.join(BROLL_2610,  "C3492.MP4"),
        "C3494":     os.path.join(BROLL_2610,  "C3494.MP4"),
        "IMG_6494":  os.path.join(BROLL_2609,  "IMG_6494.MOV"),
        "IMG_6498":  os.path.join(BROLL_2609,  "IMG_6498.MOV"),
    }
    for k, p in RAW.items():
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Missing required raw source [{k}]: {p}")
    print(f"Verified all {len(RAW)} raw source files exist on Z:\\!", flush=True)

    # 3. Prepare clean staging directory (NO copied pre-cut videos inside video/!)
    stage_dir = os.path.join(STAGE_ROOT, DRAFT_NAME)
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    os.makedirs(os.path.join(stage_dir, "video"), exist_ok=True)
    os.makedirs(os.path.join(stage_dir, "Resources"), exist_ok=True)

    # Load verified v193.0.0 donor templates (HTPM + 1117 + 261106 Vlog F20 + TVC WinHair CS2 + ĐIỀU KINH 1-sao chép)
    d1117_dir = os.path.join(DRAFTS_DIR, "1117")
    dc_1117   = json.load(open(os.path.join(d1117_dir, "draft_content.json"), encoding="utf-8"))
    dc_htpm   = json.load(open(os.path.join(DRAFTS_DIR, "HTPM", "draft_content.json"), encoding="utf-8"))
    dm_htpm   = json.load(open(os.path.join(DRAFTS_DIR, "HTPM", "draft_meta_info.json"), encoding="utf-8"))
    dc_f20    = json.load(open(os.path.join(DRAFTS_DIR, "261106 Vlog buổi tranning F20", "draft_content.json"), encoding="utf-8"))
    dc_wh     = json.load(open(os.path.join(DRAFTS_DIR, "TVC WinHair CS2 - ban Reels_v2 (1)", "draft_content.json"), encoding="utf-8"))
    dc_dk     = json.load(open(os.path.join(DRAFTS_DIR, "ĐIỀU KINH 1-sao chép", "draft_content.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(next(tr for tr in dc_1117["tracks"] if tr["type"] == "video"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    vmat_tpl   = copy.deepcopy(dc_htpm["materials"]["videos"][0])
    pmat_tpl   = copy.deepcopy(next(x for x in dc_dk["materials"]["videos"] if x.get("type") == "photo"))

    atrack_tpl = copy.deepcopy(next(tr for tr in dc_1117["tracks"] if tr["type"] == "audio" and tr.get("segments")))
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    amat_tpl   = copy.deepcopy(next(x for x in dc_1117["materials"]["audios"] if x["id"] == aseg_tpl["material_id"]))

    ttrack_tpl = copy.deepcopy(next(tr for tr in dc_f20["tracks"] if tr["type"] == "text" and tr.get("segments")))
    tseg_tpl   = copy.deepcopy(ttrack_tpl["segments"][0])
    tmat_tpl   = copy.deepcopy(next(x for x in dc_f20["materials"]["texts"] if x["id"] == tseg_tpl["material_id"]))
    mask_tpl   = copy.deepcopy(dc_wh["materials"]["common_mask"][0])
    trans_tpl  = copy.deepcopy(dc_wh["materials"]["transitions"][0])

    extra_keys   = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_1117["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_1117["materials"].get(k, []))}
    a_extra_keys = tuple(k for k in extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_1117["materials"].get(k, [])))
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_1117["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys}

    # Exact timeline matching user's 45.733s edit (snapped to 30fps grid: 1372 frames = 45.733333s)
    TOTAL_DUR = 1372 / 30.0
    TOTAL_US  = us(TOTAL_DUR)

    tl_id    = uid()
    draft_id = "6BC500C1-3D15-4024-ACD6-9534A199398F"
    now_s    = int(time.time())
    now_us   = int(time.time() * 1_000_000)

    D = copy.deepcopy(dc_1117)
    D.update({
        "id": tl_id, "name": DRAFT_NAME, "fps": 30.0, "duration": TOTAL_US,
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_1117["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })
    for k in ("texts", "common_mask", "transitions", "material_animations", "audio_fades", "videos", "audios"):
        D["materials"].setdefault(k, [])

    vmat_cache = {}
    draft_mat_entries = []
    dm_mat_item_tpl = copy.deepcopy(dm_htpm["draft_materials"][0]["value"][0])
    referenced_bytes = 0

    def add_raw_visual_mat(src_path, is_photo=False):
        nonlocal referenced_bytes
        fwd_p = norm_fwd(src_path)
        if fwd_p in vmat_cache:
            return vmat_cache[fwd_p]
        fn = os.path.basename(src_path)
        w, h, dur_s, has_aud = probe_capcut_media(src_path)
        dur_u = 10800000000 if is_photo else us(dur_s)
        mid = uid()
        lmid = str(uuid.uuid4())
        if is_photo:
            m = copy.deepcopy(pmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "photo", "path": fwd_p, "media_path": "", "local_id": "",
                "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": False
            })
        else:
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": fwd_p, "media_path": "", "local_id": "",
                "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud)
            })
        D["materials"]["videos"].append(m)

        dme = copy.deepcopy(dm_mat_item_tpl)
        dme.update({
            "id": lmid, "file_Path": fwd_p, "extra_info": fn,
            "duration": 5000000 if is_photo else dur_u, "width": w, "height": h,
            "metetype": "photo" if is_photo else "video", "item_source": 1,
            "import_time": now_s, "import_time_ms": now_s * 1000,
            "roughcut_time_range": {"start": 0, "duration": 5000000 if is_photo else dur_u},
            "sub_time_range": {"start": -1, "duration": -1},
        })
        draft_mat_entries.append(dme)
        try:
            referenced_bytes += os.path.getsize(src_path)
        except Exception:
            pass
        vmat_cache[fwd_p] = (mid, dur_u, is_photo)
        return mid, dur_u, is_photo

    def make_visual_seg(src_path, t0_s, t1_s, src_in_s=0.0, is_photo=False, vol=0.0, zoom_pair=None, pos_xy=(0.0, 0.0), scale_val=1.0, rect_mask=False, anim_in=None, anim_out=False, trans_ket_hop=False, render_idx=0):
        mid, mat_dur_u, _ = add_raw_visual_mat(src_path, is_photo=is_photo)
        dur_u = us(t1_s) - us(t0_s)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])

        if rect_mask:
            mm = copy.deepcopy(mask_tpl)
            mm.update({
                "id": uid(), "name": "Hình chữ nhật", "resource_type": "rectangle",
                "resource_id": "7374021450748924432", "source_platform": 1,
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef",
                "config": {
                    "width": 0.94, "height": 0.92, "centerX": 0.0, "centerY": 0.0,
                    "rotation": 0.0, "feather": 0.02, "expansion": 0.0,
                    "roundCorner": 0.12, "invert": False, "aspectRatio": 1.0
                }
            })
            D["materials"]["common_mask"].append(mm)
            refs.append(mm["id"])

        anims = []
        if anim_in == "slide_left":
            anims.append({
                "id": "6798332871267324423", "resource_id": "6798332871267324423", "third_resource_id": "6798332871267324423",
                "type": "in", "name": "Trượt sang trái", "start": 0, "duration": min(dur_u // 3, 333333),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798332871267324423/667952e8cf6918f62e16b8e6dfc2fef2",
                "platform": "all", "source_platform": 1, "panel": "video", "material_type": "video",
                "category_id": "in", "category_name": "in", "anim_adjust_params": None, "request_id": ""
            })
        elif anim_in == "fade_in":
            anims.append({
                "id": "6923135604519604737", "resource_id": "6923135604519604737", "third_resource_id": "6923135604519604737",
                "type": "in", "name": "Mờ", "start": 0, "duration": min(dur_u // 3, 266666),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6923135604519604737/a5f4d3998c0648ec65c03251506bd0a0",
                "platform": "all", "source_platform": 1, "panel": "video", "material_type": "video",
                "category_id": "in", "category_name": "in", "anim_adjust_params": None, "request_id": ""
            })
        if anim_out and dur_u >= 700000:
            od = min(dur_u // 4, 266666)
            anims.append({
                "id": "6798320902548230669", "resource_id": "6798320902548230669", "third_resource_id": "6798320902548230669",
                "type": "out", "name": "Mờ dần", "start": dur_u - od, "duration": od,
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798320902548230669/c6f05ce62355b537be762550040bfc08",
                "platform": "all", "source_platform": 1, "panel": "video", "material_type": "video",
                "category_id": "out", "category_name": "out", "anim_adjust_params": None, "request_id": ""
            })
        if anims:
            am_obj = {"id": uid(), "type": "sticker_animation", "animations": anims, "multi_language_current": "none"}
            D["materials"]["material_animations"].append(am_obj)
            refs.append(am_obj["id"])

        if trans_ket_hop:
            trm = copy.deepcopy(trans_tpl)
            trm.update({
                "id": uid(), "name": "Kết hợp", "source_platform": 1,
                "effect_id": "6724845717472416269", "resource_id": "6724845717472416269", "third_resource_id": "6724845717472416269",
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6724845717472416269/7b53f4c008c4c684fccf8c7d4d46cc92",
                "duration": 333333, "is_overlap": False
            })
            D["materials"]["transitions"].append(trm)
            refs.append(trm["id"])

        kfs = make_scale_keyframes(dur_u, zoom_pair[0], zoom_pair[1]) if zoom_pair else []
        src_start_u = 0 if is_photo else us(src_in_s)
        if not is_photo and src_start_u + dur_u > mat_dur_u:
            raise ValueError(f"Clip {os.path.basename(src_path)} source range {src_start_u/1e6:.2f}..{(src_start_u+dur_u)/1e6:.2f}s exceeds material dur {mat_dur_u/1e6:.2f}s!")

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": src_start_u, "duration": dur_u},
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "speed": 1.0, "volume": float(vol), "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [], "render_index": render_idx
        })
        seg["clip"]["scale"] = {"x": float(scale_val), "y": float(scale_val)}
        seg["clip"]["transform"] = {"x": float(pos_xy[0]), "y": float(pos_xy[1])}
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": float(scale_val)}
        return seg

    # ==========================================================================
    # TRACK 0: 100% RAW FILMED SOURCE CLIPS FROM FOLDER (0.00s -> 45.733s)
    # ==========================================================================
    # Wave Pacing + Exact Lip-Sync to C3938, C3942, C3948, C3956, C3957 + Lưu ngày địa chỉ lại nhé.mp4 + Real B-Rolls!
    main_plan = [
        # 1. Opening Skit: Anh Khang walks to counter -> "Thành! Lên bảng kiểm tra miệng!" -> "Em... em..."
        (RAW["C3938"],    0.0000,  5.0000,  3.2000, (1.00, 1.06), True),
        # 2. Table Talk: "Có ai như Khang không? Hồi xưa khi mà đi học á, nghe đến chữ kiểm tra miệng là run cầm cập..."
        (RAW["C3942"],    5.0000, 14.0333,  2.1200, (1.00, 1.05), True),
        # 3A. Program Intro: C3948 dolly-back reveal of FEEL CHICKEN storefront sign as Khang introduces 20/11
        (RAW["C3948"],   14.0333, 16.5333,  1.8000, (1.00, 1.05), False),
        # 3B. Real Feel Chicken students & storefront from "Lưu ngày địa chỉ lại nhé .mp4" (clean unsubtitled window 11.65..14.52s)
        (RAW["LUU_NGAY"],16.5333, 19.4000, 11.6500, (1.01, 1.06), False),
        # 3C. Real Feel Chicken 4-flavor crispy feast + customer pulling crispy drumstick on "NHẬN QUÀ NGAY!"
        (RAW["C3490"],   19.4000, 21.0667,  1.0000, (1.02, 1.08), False),
        (RAW["IMG_6494"],21.0667, 22.6333,  0.5000, (1.00, 1.06), True),
        # 4. Questions ("Hàng loạt câu hỏi từ kiến thức học đường đến những câu đố mẹo siêu lắt léo..."): Real Feel Chicken B-rolls
        (RAW["C3488"],   22.6333, 25.8000,  0.8000, (1.01, 1.07), False),
        (RAW["C3494"],   25.8000, 28.8667,  2.0000, (1.02, 1.08), True),
        # 5. Gifts & 20/11 Dates: Raw C3956 [1.86..10.46s] lip-synced 100% to VO_s5_gifts!
        (RAW["C3956"],   28.8667, 37.4667,  1.8600, (1.00, 1.05), True),
        # 6A. Outro ("20/11 này! Rủ hội bạn đến ôn lại kiến thức, xem ai còn xứng đáng danh hiệu học sinh giỏi nào!"):
        #     Friends enjoying Feel Chicken + CS2 Storefront + "Lưu ngày địa chỉ lại nhé .mp4" CS1 Neon Sign & Address!
        (RAW["IMG_6498"],37.4667, 39.3667,  0.4000, (1.01, 1.06), False),
        (RAW["C3471"],   39.3667, 41.2667,  1.5000, (1.00, 1.06), False),
        (RAW["LUU_NGAY"],41.2667, 43.4333, 81.5500, (1.00, 1.05), False),
        # 6B. Final Punchy Tag: Raw C3957 [1.40..3.70s] Anh Khang 2 thumbs up "Đến với Feel Chicken ngay thôi!"
        (RAW["C3957"],   43.4333, 45.7333,  1.4000, (1.00, 1.05), False),
    ]
    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    for sp, t0, t1, sin, zp, tr_kh in main_plan:
        tr_v0["segments"].append(make_visual_seg(sp, t0, t1, src_in_s=sin, vol=0.0, zoom_pair=zp, trans_ket_hop=tr_kh, render_idx=0))
    D["tracks"].append(tr_v0)

    # ==========================================================================
    # TRACK 1: 2 CLASSROOM "KIỂM TRA MIỆNG" MEMES + REAL FOOD B-ROLL CUTAWAYS
    # ==========================================================================
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid(); tr_v1["segments"] = [
        # Meme 1 on "nghe đến chữ kiểm tra miệng là run cầm cập!"
        make_visual_seg(RAW["MEME_1"], 8.5333, 11.1333, is_photo=True, zoom_pair=(0.78, 0.83), pos_xy=(0.0, 0.28), scale_val=0.80, rect_mask=True, anim_in="slide_left", anim_out=False, render_idx=100),
        # Meme 2 on "còn bây giờ nghe đến ba chữ kiểm tra miệng là thấy bồi hồi ghê luôn á!"
        make_visual_seg(RAW["MEME_2"], 11.1333, 13.9000, is_photo=True, zoom_pair=(0.78, 0.83), pos_xy=(0.0, 0.28), scale_val=0.80, rect_mask=True, anim_in="fade_in", anim_out=True, render_idx=100),
        # Real Food B-roll cutaways during "mà toàn là quà ngon thôi nha!" (29.10..33.30s), then reveals Khang at 33.30..37.47s!
        make_visual_seg(RAW["C3492"],  29.1000, 31.2667, src_in_s=0.5000, vol=0.0, zoom_pair=(1.00, 1.07), anim_in="fade_in", anim_out=False, render_idx=100),
        make_visual_seg(RAW["C3489"],  31.2667, 33.3000, src_in_s=0.4000, vol=0.0, zoom_pair=(1.01, 1.07), anim_in="fade_in", anim_out=True, render_idx=100),
    ]
    D["tracks"].append(tr_v1)

    # ==========================================================================
    # TRACKS 2 & 3: NATIVE EDITABLE CAPCUT TITLES & SUBTITLES (PRO DNA, NO RASTER PNGS!)
    # ==========================================================================
    def make_text_seg(txt, t0_s, t1_s, pos_y, font_id, font_path, fsz, base_rgb, hi_rgb=None, highlights=None, bg_pill=False, bg_hex="#D92642", anim_kind="sub_fast", track_ridx=14000):
        dur_u = us(t1_s) - us(t0_s)
        tm_o = copy.deepcopy(tmat_tpl)
        tid = uid()
        styles = build_rich_styles(txt, highlights or [], base_rgb, hi_rgb or base_rgb, font_id, font_path, fsz, stroke_w=0.08)
        content_json = json.dumps({"text": txt, "styles": styles}, ensure_ascii=False)
        tm_o.update({
            "id": tid, "type": "text", "name": txt[:30],
            "recognize_task_id": "", "recognize_text": "",
            "content": content_json, "base_content": content_json,
            "words": {"start_time": [], "end_time": [], "text": []},
            "current_words": {"start_time": [], "end_time": [], "text": []},
            "font_size": float(fsz), "font_path": font_path, "font_resource_id": font_id,
            "italic_degree": 0, "alignment": 1, "line_max_width": 0.88,
            "has_shadow": True, "shadow_alpha": 0.80, "shadow_distance": 5.0,
            "border_alpha": 1.0, "border_color": "#1A080C", "border_width": 0.08,
            "background_style": 1 if bg_pill else 0, "background_color": bg_hex,
            "background_alpha": 0.86 if bg_pill else 0.0, "background_round_radius": 0.35 if bg_pill else 0.0,
            "background_width": 0.14, "background_height": 0.12,
            "fonts": [{
                "id": uid(), "resource_id": font_id, "effect_id": font_id, "third_resource_id": "",
                "category_id": "user", "category_name": "Đã sử dụng gần đây", "source_platform": 1,
                "path": font_path, "title": "Montserrat", "team_id": "", "file_uri": "", "request_id": ""
            }]
        })
        D["materials"]["texts"].append(tm_o)

        anim_map = {
            "gold_dust":    ("7331632775948145153", "Bụi vàng",            min(dur_u // 2, 550000), "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7331632775948145153/25d1da238cd78c05757f2d6036dec895"),
            "text_fade_in": ("7648937403646004500", "Chữ mờ dần hiện vào", min(dur_u // 3, 400000), "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7648937403646004500/495e55b3bcd1f6420b6e4b1b44ed1fc8"),
            "sub_fast":     ("6923135604519604737", "Mờ",                  min(dur_u // 4, 166666), "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6923135604519604737/a5f4d3998c0648ec65c03251506bd0a0"),
        }
        aid_in, aname_in, adur_in, apath_in = anim_map.get(anim_kind, anim_map["sub_fast"])
        od = min(dur_u // 4, 166666 if anim_kind == "sub_fast" else 300000)
        anims = [
            {"id": aid_in, "resource_id": aid_in, "third_resource_id": aid_in, "source_platform": 1, "type": "in", "name": aname_in, "category_id": "text", "category_name": "text", "start": 0, "duration": adur_in, "path": apath_in, "platform": "all", "panel": "", "material_type": "sticker", "anim_adjust_params": None, "request_id": ""},
            {"id": "6798320902548230669", "resource_id": "6798320902548230669", "third_resource_id": "6798320902548230669", "source_platform": 1, "type": "out", "name": "Mờ dần", "category_id": "out", "category_name": "out", "start": max(0, dur_u - od), "duration": od, "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798320902548230669/c6f05ce62355b537be762550040bfc08", "platform": "all", "panel": "", "material_type": "sticker", "anim_adjust_params": None, "request_id": ""},
        ]
        am_id = uid()
        D["materials"]["material_animations"].append({"id": am_id, "type": "sticker_animation", "animations": anims, "multi_language_current": "none"})

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tid, "source_timerange": None,
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "extra_material_refs": [am_id], "common_keyframes": [], "keyframe_refs": [], "render_index": track_ridx
        })
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["transform"] = {"x": 0.0, "y": float(pos_y)}
        return ts

    GOLD_RGB, WHITE_RGB, CORAL_RGB = (1.0, 0.831, 0.0), (1.0, 1.0, 1.0), (1.0, 0.38, 0.48)

    tr_headers = {"id": uid(), "type": "text", "attribute": 0, "flag": 0, "is_default_name": False, "name": "Tiêu đề chính", "segments": [
        make_text_seg("THÀNH! LÊN BẢNG KIỂM TRA MIỆNG!",      1.35,  3.45,  0.66, FONT_OSWALD_ID, FONT_OSWALD_PATH, 11.5, GOLD_RGB, bg_pill=True, bg_hex="#E62E48", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("EM... EM... RUN QUÁ!!",                3.55,  4.88, -0.42, FONT_MONTS_ID,  FONT_MONTS_PATH,   9.5, WHITE_RGB, bg_pill=True, bg_hex="#2678C4", anim_kind="sub_fast", track_ridx=14001),
        make_text_seg("CHƯƠNG TRÌNH 20/11 • FEEL CHICKEN",   14.10, 18.80,  0.74, FONT_MONTS_ID,  FONT_MONTS_PATH,   8.0, GOLD_RGB, bg_pill=True, bg_hex="#E62E48", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("KIỂM TRA MIỆNG\nTRẢ LỜI ĐÚNG – NHẬN QUÀ NGAY!", 18.90, 22.55, 0.68, FONT_OSWALD_ID, FONT_OSWALD_PATH, 11.0, GOLD_RGB, bg_pill=True, bg_hex="#1E5E46", anim_kind="gold_dust", track_ridx=14001),
        make_text_seg("100 CÂU HỎI HỌC ĐƯỜNG & ĐỐ MẸO",      22.70, 28.80,  0.74, FONT_MONTS_ID,  FONT_MONTS_PATH,   8.0, GOLD_RGB, bg_pill=True, bg_hex="#E62E48", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("TOÀN QUÀ NGON TỪ FEEL CHICKEN!",      28.95, 33.25,  0.74, FONT_MONTS_ID,  FONT_MONTS_PATH,   8.2, GOLD_RGB, bg_pill=True, bg_hex="#E62E48", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("SĂN DANH HIỆU HỌC SINH GIỎI 20/11!",  37.55, 43.35,  0.74, FONT_MONTS_ID,  FONT_MONTS_PATH,   8.0, GOLD_RGB, bg_pill=True, bg_hex="#E62E48", anim_kind="gold_dust", track_ridx=14001),
        make_text_seg("CS1: 38 Nguyễn Đình Chiểu • CS2: 35 Trần Hữu Duyệt", 43.45, 45.70, -0.78, FONT_MONTS_ID, FONT_MONTS_PATH, 7.2, GOLD_RGB, bg_pill=True, bg_hex="#C81E38", anim_kind="text_fade_in", track_ridx=14001),
    ]}
    D["tracks"].append(tr_headers)

    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master.json"), encoding="utf-8"))
    # Shift s6a & s6b words by -0.10s to match user's 37.467s..45.733s edit!
    adj_words = []
    for w in tm["words"]:
        ws, we = float(w["s"]), float(w["e"])
        if ws >= 37.50:
            ws = round(ws - 0.10, 3)
            we = round(min(TOTAL_DUR - 0.04, we - 0.10), 3)
        elif we > 37.33:
            we = 37.33
        if we - ws >= 0.05:
            adj_words.append({"w": w["w"], "s": ws, "e": we})

    cap_groups = build_caption_groups(adj_words)
    tr_subs = {"id": uid(), "type": "text", "attribute": 0, "flag": 0, "is_default_name": False, "name": "Phụ đề thoại", "segments": []}
    all_hi_words = list(GOLD_KEYWORDS | CORAL_KEYWORDS)
    prev_end_u = 0
    for g in cap_groups:
        gt0, gt1 = g["t0"], min(TOTAL_DUR - 0.03, g["t1"])
        if us(gt0) < prev_end_u:
            gt0 = prev_end_u / 1_000_000.0
        if gt1 - gt0 < 0.18:
            continue
        full_txt = "\n".join(" ".join(w[0] for w in ln) for ln in g["lines"]).upper()
        ts_seg = make_text_seg(full_txt, gt0, gt1, -0.56, FONT_MONTS_ID, FONT_MONTS_PATH, 9.2, WHITE_RGB, hi_rgb=GOLD_RGB, highlights=all_hi_words, bg_pill=False, anim_kind="sub_fast", track_ridx=14005)
        prev_end_u = ts_seg["target_timerange"]["start"] + ts_seg["target_timerange"]["duration"] + 33333
        tr_subs["segments"].append(ts_seg)
    D["tracks"].append(tr_subs)

    # ==========================================================================
    # AUDIO TRACKS 4..8: DIRECT Z:\ PATHS FOR VOICE + 2-HALF BGM + KAWAII SFX!
    # ==========================================================================
    amat_cache = {}
    def add_audio_mat(src_path, disp_name, a_type="extract_music"):
        fwd_p = norm_fwd(src_path)
        if fwd_p in amat_cache:
            return amat_cache[fwd_p]
        _, _, dur_s, _ = probe_capcut_media(src_path)
        dur_u = max(66666, us(dur_s))
        am = copy.deepcopy(amat_tpl)
        aid = uid()
        lmid = str(uuid.uuid4())
        am.update({
            "id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
            "type": a_type, "name": disp_name, "path": fwd_p,
            "duration": dur_u, "category_name": "local", "wave_points": []
        })
        D["materials"]["audios"].append(am)
        amat_cache[fwd_p] = (aid, dur_u)
        return aid, dur_u

    def make_audio_seg(src_path, disp_name, t0_s, dur_s=None, src_in_s=0.0, vol=1.0, micro_fade=True, fade_in_us=0, fade_out_us=0, a_type="sound"):
        aid, mat_dur_u = add_audio_mat(src_path, disp_name, a_type=a_type)
        avail_u = max(33333, mat_dur_u - us(src_in_s))
        dur_u = min(avail_u, us(dur_s)) if dur_s is not None else avail_u
        if us(t0_s) + dur_u > TOTAL_US:
            dur_u = max(33333, TOTAL_US - us(t0_s))
        aseg = copy.deepcopy(aseg_tpl)
        arefs = []
        for k in a_extra_keys:
            em = copy.deepcopy(a_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); arefs.append(em["id"])
        fi_u = 33333 if micro_fade else fade_in_us
        fo_u = 66666 if micro_fade else fade_out_us
        if fi_u > 0 or fo_u > 0:
            fid = uid()
            D["materials"]["audio_fades"].append({"id": fid, "type": "audio_fade", "fade_type": 0, "fade_in_duration": int(fi_u), "fade_out_duration": int(fo_u)})
            arefs.append(fid)
        aseg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": us(src_in_s), "duration": dur_u},
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "speed": 1.0, "volume": float(vol), "last_nonzero_volume": 1.0,
            "extra_material_refs": arefs, "common_keyframes": [], "keyframe_refs": []
        })
        return aseg

    # Voice Anh Khang (preserving user's exact 7-segment edit at 10:49:41!)
    vo_plan = [
        ("vo_s1_skit.wav",      "VO_01_C3938_MoDau",       0.0000, 5.0000),
        ("vo_s2_table.wav",     "VO_02_C3942_NgoiBan",     5.0000, 9.0333),
        ("vo_s3_program.wav",   "VO_03_ChuongTrinh_2011", 14.0333, 8.6000),
        ("vo_s4_questions.wav", "VO_04_C3960_CauHoi",     22.6333, 6.2333),
        ("vo_s5_gifts.wav",     "VO_05_C3956_QuaNgon",    28.8667, 8.4667),
        ("vo_s6a_outro.wav",    "VO_06a_HocSinhGioi",     37.4667, 5.9667),
        ("vo_s6b_thumbs.wav",   "VO_06b_C3957_Chot",      43.4333, 2.3000),
    ]
    tr_vo = copy.deepcopy(atrack_tpl); tr_vo["id"] = uid(); tr_vo["name"] = "Voice Anh Khang"; tr_vo["segments"] = []
    for vfn, vdisp, vt0, vdur in vo_plan:
        tr_vo["segments"].append(make_audio_seg(os.path.join(AUDIO_OUT_Z, vfn), vdisp, vt0, dur_s=vdur, vol=1.22, micro_fade=True, a_type="extract_music"))
    D["tracks"].append(tr_vo)

    # 2-Half Cute C-Major BGM Track
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["name"] = "BGM Kute 2 Nửa"; tr_bgm["segments"] = [
        make_audio_seg(os.path.join(AUDIO_OUT_Z, "bgm_warm_fretless.mp3"), "BGM_1_KyUcHocTro", 0.0000, dur_s=19.4000, src_in_s=0.0, vol=0.28, micro_fade=False, fade_in_us=400000, fade_out_us=600000, a_type="music"),
        make_audio_seg(os.path.join(AUDIO_OUT_Z, "bgm_sunny_carefree.mp3"), "BGM_2_KiemTraMieng_Kute", 19.4000, dur_s=(TOTAL_DUR - 19.4000), src_in_s=0.0, vol=0.30, micro_fade=False, fade_in_us=500000, fade_out_us=900000, a_type="music"),
    ]
    D["tracks"].append(tr_bgm)

    # Kawaii SFX Tracks pointing directly to Z:\...\02_Hiệu Ứng Âm Thanh (SFX)
    tlh_idx = {}
    if os.path.exists(TLH_SFX_DIR):
        for r, _, fs in os.walk(TLH_SFX_DIR):
            for fn in fs:
                tlh_idx[fn] = os.path.join(r, fn)

    sfx_files = {
        "star_open": tlh_idx.get("Mở cảnh - Tiếng chuông sao lung linh.mp3"),
        "pop1":      tlh_idx.get("Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3"),
        "pop2":      tlh_idx.get("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),
        "boing":     tlh_idx.get("Hoạt hình - Lò xo nảy Boing Boing.mp3"),
        "ting":      tlh_idx.get("Ting - Chuông Ting nảy ý tưởng.mp3"),
        "notif":     tlh_idx.get("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"),
        "whoosh_tvc":tlh_idx.get("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"),
        "swoosh":    tlh_idx.get("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),
        "sparkle":   os.path.join(AUDIO_OUT_Z, "sfx_sparkle_shine.mp3"),
        "shimmer":   os.path.join(AUDIO_OUT_Z, "sfx_crystal_shimmer.mp3"),
        "whoosh_sk": os.path.join(AUDIO_OUT_Z, "sfx_whoosh_soft.mp3"),
    }

    sfx_cues = [
        (0.13, "star_open", 1.5, 0.55), (1.37, "pop1", 0.37, 0.62), (1.47, "boing", 0.53, 0.45),
        (3.57, "pop2", 0.30, 0.58), (5.00, "whoosh_tvc", 0.53, 0.55),
        (8.53, "whoosh_sk", 0.50, 0.55), (8.60, "boing", 0.53, 0.52),     # Meme 1 pop!
        (11.13, "pop1", 0.37, 0.58),                                      # Meme 2 pop!
        (14.07, "swoosh", 0.40, 0.52), (16.53, "pop2", 0.30, 0.55),
        (19.40, "whoosh_tvc", 0.53, 0.62), (19.50, "sparkle", 1.40, 0.55), (19.57, "ting", 0.93, 0.55),
        (22.67, "whoosh_sk", 0.50, 0.50), (25.80, "notif", 0.47, 0.58),
        (28.87, "whoosh_tvc", 0.53, 0.55), (29.10, "sparkle", 1.30, 0.50), (31.27, "swoosh", 0.40, 0.50),
        (37.50, "whoosh_tvc", 0.53, 0.55), (37.73, "shimmer", 1.40, 0.55),
        (41.27, "notif", 0.47, 0.55), (43.47, "star_open", 1.50, 0.58),
    ]

    lanes = []
    for ts, sk, dlim, svol in sorted(sfx_cues, key=lambda x: x[0]):
        sp = sfx_files.get(sk)
        if not sp or not os.path.exists(sp):
            continue
        seg = make_audio_seg(sp, f"SFX_{sk}", ts, dur_s=dlim, vol=svol, micro_fade=True, a_type="sound")
        st_u = seg["target_timerange"]["start"]
        en_u = st_u + seg["target_timerange"]["duration"] + 33333
        placed = False
        for li, (l_end, tr_obj) in enumerate(lanes):
            if st_u >= l_end:
                tr_obj["segments"].append(seg)
                lanes[li] = (en_u, tr_obj)
                placed = True
                break
        if not placed:
            nt = copy.deepcopy(atrack_tpl); nt["id"] = uid(); nt["segments"] = [seg]
            lanes.append((en_u, nt))
    for _, tr_obj in lanes:
        D["tracks"].append(tr_obj)

    for idx_tr, tr_obj in enumerate(D["tracks"]):
        for sg in tr_obj.get("segments", []):
            sg["track_render_index"] = idx_tr

    # ==========================================================================
    # WRITE NATIVE v193.0.0 CAPCUT DRAFT FILES
    # ==========================================================================
    cover_jpg = os.path.join(stage_dir, "draft_cover.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "3.2", "-i", RAW["C3948"],
        "-frames:v", "1", "-vf", "scale=540:960", cover_jpg
    ], check=True)

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for fn_dc in ("draft_content.json", "template-2.tmp"):
        open(os.path.join(stage_dir, fn_dc), "wb").write(dc_bytes)

    open(os.path.join(stage_dir, "draft_settings"), "w", encoding="utf-8").write(
        f"[General]\ncloud_last_modify_platform=windows\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=180\nreal_edit_keys=1\n"
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

    # Timelines/<tl_id> WITH IDENTICAL ID == dc["id"]
    tl_root = os.path.join(stage_dir, "Timelines")
    tl_sub  = os.path.join(tl_root, tl_id)
    os.makedirs(tl_sub, exist_ok=True)
    for fn_dc in ("draft_content.json", "template-2.tmp"):
        open(os.path.join(tl_sub, fn_dc), "wb").write(dc_bytes)
    shutil.copy2(cover_jpg, os.path.join(tl_sub, "draft_cover.jpg"))
    if os.path.isfile(os.path.join(stage_dir, "attachment_pc_common.json")):
        shutil.copy2(os.path.join(stage_dir, "attachment_pc_common.json"), os.path.join(tl_sub, "attachment_pc_common.json"))
    shutil.copytree(ca_dir, os.path.join(tl_sub, "common_attachment"), dirs_exist_ok=True)

    proj_j = {
        "config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False},
        "create_time": now_us, "id": tl_id, "main_timeline_id": tl_id,
        "timelines": [{"create_time": now_us, "id": tl_id, "is_marked_delete": False, "name": "Dòng thời gian 01", "update_time": now_us}],
        "update_time": now_us, "version": 0
    }
    json.dump(proj_j, open(os.path.join(tl_root, "project.json"), "w", encoding="utf-8"), ensure_ascii=False)

    M = copy.deepcopy(dm_htpm)
    M.update({
        "draft_id": draft_id,
        "draft_name": DRAFT_NAME,
        "draft_fold_path": norm_fwd(local_draft_dir),
        "draft_root_path": norm_fwd(DRAFTS_DIR),
        "draft_cover": "draft_cover.jpg",
        "draft_new_version": "164.0.0",
        "tm_duration": TOTAL_US,
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
    print(f"Staged 100% Raw-Source CapCut Draft ({len(D['tracks'])} tracks, {len(D['materials']['videos'])} external raw videos/photos)!", flush=True)

    # Close CapCut cleanly before deploying so .locked releases and root_meta_info reloads!
    capcut_exe = None
    try:
        out_p = subprocess.check_output(["powershell", "-NoProfile", "-Command", "(Get-Process CapCut -ErrorAction SilentlyContinue | Select-Object -First 1).Path"], text=True).strip()
        if out_p and os.path.exists(out_p):
            capcut_exe = out_p
    except Exception:
        pass
    if not capcut_exe:
        for cand in [
            os.path.expandvars(r"%LOCALAPPDATA%\CapCut\Apps\9.8.0.4213\CapCut.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\CapCut\Apps\CapCut.exe"),
        ]:
            if os.path.exists(cand):
                capcut_exe = cand
                break

    subprocess.run(["taskkill", "/IM", "CapCut.exe", "/F"], capture_output=True)
    time.sleep(2.2)

    if os.path.exists(local_draft_dir):
        shutil.rmtree(local_draft_dir)
    shutil.copytree(stage_dir, local_draft_dir)

    # Update root_meta_info.json
    rm_path = os.path.join(DRAFTS_DIR, "root_meta_info.json")
    rm = json.load(open(rm_path, encoding="utf-8"))
    stores = [s for s in rm.get("all_draft_store", []) if s.get("draft_name") != DRAFT_NAME and s.get("draft_id") != draft_id]
    tpl_entry = copy.deepcopy(stores[0]) if stores else {}
    tpl_entry.update({
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": norm_fwd(local_draft_dir) + "/draft_cover.jpg",
        "draft_fold_path": norm_fwd(local_draft_dir),
        "draft_id": draft_id,
        "draft_is_ai_shorts": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_infinite_canvas_draft": False,
        "draft_is_invisible": False,
        "draft_is_pippit_draft": False,
        "draft_is_web_article_video": False,
        "draft_json_file": norm_fwd(local_draft_dir) + "/draft_content.json",
        "draft_name": DRAFT_NAME,
        "draft_new_version": "164.0.0",
        "draft_root_path": norm_fwd(DRAFTS_DIR),
        "draft_timeline_materials_size": referenced_bytes,
        "streaming_edit_draft_ready": True,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "tm_draft_removed": 0,
        "tm_duration": TOTAL_US,
    })
    rm["all_draft_store"] = [tpl_entry] + stores
    json.dump(rm, open(rm_path, "w", encoding="utf-8"), ensure_ascii=False)
    print("Deployed FEEL_CHICKEN_KiemTraMieng_2011_Kute & updated root_meta_info.json!", flush=True)

    # Relaunch CapCut Desktop
    if capcut_exe and os.path.exists(capcut_exe):
        subprocess.Popen([capcut_exe], cwd=os.path.dirname(capcut_exe))
        print("Relaunched CapCut Desktop:", capcut_exe, flush=True)

    # Sync updated CapCut Draft + build script to Google Drive 03_Du_An
    drive_proj = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-kiem-tra-mieng-2011"
    os.makedirs(drive_proj, exist_ok=True)
    drive_draft = os.path.join(drive_proj, DRAFT_NAME)
    if os.path.exists(drive_draft):
        shutil.rmtree(drive_draft)
    shutil.copytree(stage_dir, drive_draft)
    shutil.copy2(__file__, os.path.join(drive_proj, os.path.basename(__file__)))
    print("Synced Raw-Source CapCut Draft & script ->", drive_proj, flush=True)

if __name__ == "__main__":
    main()
