import copy, json, math, os, shutil, subprocess, time, uuid

OUT        = r"d:\AI\full studio\output\f20-set-qua-2011"
MEDIA      = os.path.join(OUT, "capcut_media")
DRAFTS_DIR = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"
F20_DIR    = os.path.join(DRAFTS_DIR, "F20 vd 1")
BAK_DIR    = os.path.join(OUT, "capcut_backup")

FONT_DEFAULT_ID   = "7542214368361057553"
FONT_DEFAULT_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7542214368361057553/d376267c892ee3a53654ae93a78dcfb7/font.ttf"
FONT_MONTS_ID     = "7517455788122705168"
FONT_MONTS_PATH   = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7517455788122705168/91d28cfa5e7db054f4872f1ae2417ac2/Montserrat-Bold.otf"
FONT_OSWALD_ID    = "7182504807289065985"
FONT_OSWALD_PATH  = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7182504807289065985/0a5333de6f4d592cb2d2390d68b31efb/Oswald-Bold.ttf"

def uid():
    return str(uuid.uuid4()).upper()

def us(sec):
    return int(round(float(sec) * 30.0) * 1_000_000 // 30)

def probe_dur_s(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def make_scale_keyframes(dur_us, s0, s1):
    out = []
    for prop in ("KFTypeScaleX", "KFTypeScaleY"):
        out.append({
            "id": uid(),
            "material_id": "",
            "property_type": prop,
            "keyframe_list": [
                {
                    "id": uid(), "curveType": "Line", "time_offset": 0,
                    "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
                    "values": [float(s0)], "string_value": "", "graphID": ""
                },
                {
                    "id": uid(), "curveType": "Line", "time_offset": int(dur_us),
                    "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
                    "values": [float(s1)], "string_value": "", "graphID": ""
                }
            ]
        })
    return out

def build_rich_styles(full_text, highlights, base_rgb, hi_rgb, font_id, font_path, size_val, stroke_w=0.08):
    # Compute non-overlapping character ranges for highlights vs normal text
    n = len(full_text)
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
    if n == 0:
        return []
    cur_flag = is_hi[0]
    s_i = 0
    for i in range(1, n):
        if is_hi[i] != cur_flag:
            spans.append((s_i, i, cur_flag))
            s_i = i
            cur_flag = is_hi[i]
    spans.append((s_i, n, cur_flag))

    styles = []
    for r0, r1, hi in spans:
        col = hi_rgb if hi else base_rgb
        st = {
            "fill": {"content": {"render_type": "solid", "solid": {"color": list(col)}}},
            "font": {"path": font_path, "id": font_id},
            "size": float(size_val),
            "bold": True,
            "useLetterColor": True,
            "strokes": [{
                "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
                "width": float(stroke_w),
                "mode": 0
            }],
            "shadows": [{
                "thickness_projection_angle": -45,
                "thickness_projection_enable": False,
                "diffuse": 0.15,
                "alpha": 0.72,
                "distance": 6,
                "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
                "angle": -45,
                "thickness_projection_distance": 0
            }],
            "range": [r0, r1]
        }
        styles.append(st)
    return styles

def main():
    orig_dc = json.load(open(os.path.join(BAK_DIR, "draft_content.json.orig"), encoding="utf-8"))
    orig_dm = json.load(open(os.path.join(BAK_DIR, "draft_meta_info.json.orig"), encoding="utf-8"))
    native_tpl = json.load(open(os.path.join(OUT, "capcut_native_templates.json"), encoding="utf-8"))
    aroll_plan = json.load(open(os.path.join(OUT, "aroll_frame_plan.json"), encoding="utf-8"))
    sub_data   = json.load(open(os.path.join(OUT, "subtitles_and_titles.json"), encoding="utf-8"))
    aud_man    = json.load(open(os.path.join(OUT, "audio_assets_manifest.json"), encoding="utf-8"))

    # Extract templates from F20 vd 1's own schema
    vtrack_tpl = copy.deepcopy(orig_dc["tracks"][0])
    vseg_tpl   = copy.deepcopy(orig_dc["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(orig_dc["materials"]["videos"][0])
    atrack_tpl = copy.deepcopy(orig_dc["tracks"][1])
    aseg_tpl   = copy.deepcopy(orig_dc["tracks"][1]["segments"][0])
    amat_tpl   = copy.deepcopy(orig_dc["materials"]["audios"][0])

    extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl = {k: copy.deepcopy(next(x for x in orig_dc["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in extra_keys}
    a_extra_keys = tuple(k for k in extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in orig_dc["materials"].get(k, [])))
    a_extra_tpl = {k: copy.deepcopy(next(x for x in orig_dc["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys}

    tmat_tpl = native_tpl["text_mat"]
    tseg_tpl = native_tpl["text_seg"]

    TOTAL_DUR = 112.433333
    TOTAL_US  = us(TOTAL_DUR)

    D = copy.deepcopy(orig_dc)
    D["fps"] = 30.0
    D["duration"] = TOTAL_US
    D["canvas_config"] = {"ratio": "9:16", "width": 1080, "height": 1920, "background": None}
    D["tracks"] = []
    D["materials"] = {k: [] for k in orig_dc["materials"]}
    for k in ("texts", "common_mask", "transitions", "material_animations", "audio_fades", "videos", "audios"):
        D["materials"].setdefault(k, [])

    # Helper: register video material & create video segment
    vmat_cache = {}
    def add_video_mat(path, name=None):
        p_norm = path.replace("\\", "/")
        if p_norm in vmat_cache:
            return vmat_cache[p_norm]
        dur_u = us(probe_dur_s(path))
        vm = copy.deepcopy(vmat_tpl)
        mid = uid()
        vm.update({
            "id": mid, "type": "video", "path": p_norm,
            "material_name": name or os.path.basename(path),
            "width": 1080, "height": 1920, "duration": dur_u, "has_audio": True
        })
        D["materials"]["videos"].append(vm)
        vmat_cache[p_norm] = (mid, dur_u)
        return mid, dur_u

    def make_video_seg(path, t0_s, t1_s, src_in_s=0.0, vol=0.0, zoom_pair=None, pos_xy=(0.0, 0.0), scale_val=1.0, rect_mask=False, anim_in=None, anim_out=True, trans_type=None, render_idx=0):
        mid, _ = add_video_mat(path)
        dur_u = us(t1_s - t0_s)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k in extra_keys:
            em = copy.deepcopy(v_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])

        # Optional PIP Rectangle Mask
        if rect_mask:
            mm = copy.deepcopy(native_tpl["mask_mat"])
            mm["id"] = uid()
            mm.update({
                "name": "Hình chữ nhật",
                "resource_type": "rectangle",
                "resource_id": "7374021450748924432",
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef",
                "config": {
                    "width": 0.88, "height": 0.86, "centerX": 0.0, "centerY": 0.0,
                    "rotation": 0.0, "feather": 0.06, "expansion": 0.0,
                    "roundCorner": 0.14, "invert": False, "aspectRatio": 1.0
                }
            })
            D["materials"]["common_mask"].append(mm)
            refs.append(mm["id"])

        # Optional Video In/Out Animation
        anims_list = []
        if anim_in == "slide_left":
            anims_list.append({
                "id": "6798332871267324423", "resource_id": "6798332871267324423",
                "third_resource_id": "6798332871267324423", "type": "in", "name": "Trượt sang trái",
                "start": 0, "duration": min(dur_u // 3, 433333),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798332871267324423/667952e8cf6918f62e16b8e6dfc2fef2",
                "platform": "all", "source_platform": 1, "panel": "video", "material_type": "video",
                "category_id": "in", "category_name": "in", "anim_adjust_params": None, "request_id": ""
            })
        if anim_out and dur_u >= 900000:
            od = min(dur_u // 4, 366666)
            anims_list.append({
                "id": "6798320902548230669", "resource_id": "6798320902548230669",
                "third_resource_id": "6798320902548230669", "type": "out", "name": "Mờ dần",
                "start": dur_u - od, "duration": od,
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798320902548230669/c6f05ce62355b537be762550040bfc08",
                "platform": "all", "source_platform": 1, "panel": "video", "material_type": "video",
                "category_id": "out", "category_name": "out", "anim_adjust_params": None, "request_id": ""
            })
        if anims_list:
            am_obj = {"id": uid(), "type": "sticker_animation", "animations": anims_list, "multi_language_current": "none"}
            D["materials"]["material_animations"].append(am_obj)
            refs.append(am_obj["id"])

        if trans_type == "ket_hop":
            tm = copy.deepcopy(native_tpl["trans_mat"])
            tm.update({
                "id": uid(), "name": "Kết hợp",
                "effect_id": "6724845717472416269", "resource_id": "6724845717472416269",
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6724845717472416269/7b53f4c008c4c684fccf8c7d4d46cc92",
                "duration": 400000, "is_overlap": True
            })
            D["materials"]["transitions"].append(tm)
            refs.append(tm["id"])

        kfs = make_scale_keyframes(dur_u, zoom_pair[0], zoom_pair[1]) if zoom_pair else []

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": us(src_in_s), "duration": dur_u},
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "speed": 1.0, "volume": float(vol), "last_nonzero_volume": 1.0,
            "extra_material_refs": refs,
            "common_keyframes": kfs, "keyframe_refs": [],
            "render_index": render_idx
        })
        seg["clip"]["scale"] = {"x": float(scale_val), "y": float(scale_val)}
        seg["clip"]["transform"] = {"x": float(pos_xy[0]), "y": float(pos_xy[1])}
        seg["clip"]["alpha"] = 1.0
        return seg

    # ==================================================================
    # TRACK 0: Clean A-Roll Main Video (13 Frame-Accurate Segments + Micro-Zoom & Dynamic Framing!)
    # ==================================================================
    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    aroll_seg_dir = os.path.join(MEDIA, "aroll_segs")
    zoom_presets = [
        (1.00, 1.06), (1.05, 1.00), (1.00, 1.06), (1.02, 1.07),
        (1.00, 1.06), (1.06, 1.00), (1.02, 1.09), (1.00, 1.06),
        (1.08, 1.13), (1.00, 1.06), (1.05, 1.08), (1.06, 1.00), (1.00, 1.07)
    ]
    trans_indices = {0, 3, 5, 8, 11}
    for seg_info in aroll_plan:
        idx = seg_info["idx"]
        p_seg = os.path.join(aroll_seg_dir, f"aroll_{idx:02d}_{seg_info['fn'][:-4]}.mp4")
        zp = zoom_presets[idx % len(zoom_presets)]
        tt = "ket_hop" if idx in trans_indices else None
        tr_v0["segments"].append(make_video_seg(
            p_seg, seg_info["t0"], seg_info["t1"], src_in_s=0.0, vol=0.0,
            zoom_pair=zp, anim_out=False, trans_type=tt, render_idx=0
        ))
    D["tracks"].append(tr_v0)

    # ==================================================================
    # TRACK 1: 17 Dynamic B-Rolls & 6 Luxury Product Showcases (Zero Static Stretches!)
    # ==================================================================
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid(); tr_v1["segments"] = []
    broll_overlays = [
        # Explosive 3-shot Hook B-rolls
        (  1.45,   2.85, "broll_01_dolly_sets.mp4",                0.0, (1.00, 1.07), None,         False),
        (  2.85,   4.35, "broll_02_rotating_tower.mp4",            0.0, (1.06, 1.00), None,         True),
        # Luxury Product Showcases #1 - #4
        ( 15.95,  25.35, "showcase_01_yensao_ingredients.mp4",     0.0, None,         "slide_left", True),
        ( 28.55,  33.65, "showcase_02_rongbien_doi.mp4",           0.0, None,         "slide_left", True),
        ( 35.80,  39.70, "showcase_03_banhthuyen_250g.mp4",        0.0, None,         "slide_left", True),
        ( 42.20,  46.60, "showcase_04_rongbien_kephat_500g.mp4",   0.0, None,         "slide_left", True),
        # Mica Gift Basket + Red Leather Handle + Ribbon & Flowers B-rolls
        ( 50.00,  52.30, "broll_03_arrange_table.mp4",             0.0, (1.00, 1.06), None,         False),
        ( 52.30,  54.65, "broll_04_mica_sunlit.mp4",               0.0, (1.05, 1.00), None,         True),
        ( 57.20,  61.75, "broll_05_quai_da_macro.mp4",             0.0, (1.00, 1.07), "slide_left", True),
        ( 63.20,  67.20, "broll_06_hoa_no_macro.mp4",              0.0, (1.06, 1.00), "slide_left", True),
        # Luxury Showcase #5: Glowing SKA NEST Bird's Nest
        ( 71.75,  76.72, "showcase_05_to_yen_cao_cap.mp4",         0.0, None,         "slide_left", True),
        # Cẩm Nang Yến Sào Close-Up Angle (breaks 13.5s static stretch!)
        ( 80.40,  85.10, "broll_08_cam_nang_close.mp4",            0.0, (1.02, 1.08), None,         True),
        # F20 Direct Factory Production & Packing 3-Shot Wave Pacing Montage!
        ( 93.10,  95.00, "broll_09_factory_pack1.mp4",             0.0, (1.00, 1.06), None,         False),
        ( 95.00,  96.80, "broll_10_factory_carton.mp4",            0.0, (1.05, 1.00), None,         False),
        ( 96.80,  98.50, "broll_11_delivery_car.mp4",              0.0, (1.00, 1.07), None,         True),
        # Customer Gift Handover + Luxury End-Card #6
        (101.35, 105.20, "broll_12_handover_gift.mp4",             0.0, (1.00, 1.06), "slide_left", True),
        (105.85, 112.43, "showcase_06_outro_endcard.mp4",          0.0, None,         "slide_left", False),
    ]
    for t0, t1, fn, sin, zp, ain, aout in broll_overlays:
        tr_v1["segments"].append(make_video_seg(
            os.path.join(MEDIA, fn), t0, t1, src_in_s=sin, vol=0.0,
            zoom_pair=zp, anim_in=ain, anim_out=aout, render_idx=100
        ))
    D["tracks"].append(tr_v1)

    # ==================================================================
    # TRACK 2: Corner PIP Overlays (Rectangle Mask + Slide-In)
    # ==================================================================
    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid(); tr_v2["segments"] = []
    pip_specs = [
        (11.80, 15.55, "broll_07_inside_bag_pip.mp4", (0.48, -0.16), 0.44),
        (46.85, 49.85, "broll_04_mica_sunlit.mp4",    (0.48, -0.16), 0.44),
        (85.45, 89.80, "broll_07_inside_bag_pip.mp4", (0.48, -0.16), 0.42),
    ]
    for t0, t1, fn, pos_xy, sc_v in pip_specs:
        tr_v2["segments"].append(make_video_seg(
            os.path.join(MEDIA, fn), t0, t1, src_in_s=0.2, vol=0.0,
            pos_xy=pos_xy, scale_val=sc_v, rect_mask=True, anim_in="slide_left", anim_out=True, render_idx=200
        ))
    D["tracks"].append(tr_v2)

    # ==================================================================
    # HELPER FOR NATIVE EDITABLE TEXT TRACKS
    # ==================================================================
    def make_text_seg(txt, t0_s, t1_s, pos_y, font_id, font_path, fsz, base_rgb, hi_rgb=None, highlights=None, bg_pill=False, anim_kind="fade", track_ridx=14000):
        dur_u = us(t1_s - t0_s)
        tm = copy.deepcopy(tmat_tpl)
        tid = uid()
        hi_rgb = hi_rgb or base_rgb
        highlights = highlights or []
        styles = build_rich_styles(txt, highlights, base_rgb, hi_rgb, font_id, font_path, fsz, stroke_w=0.08)
        content_json = json.dumps({"text": txt, "styles": styles}, ensure_ascii=False)

        tm.update({
            "id": tid, "type": "text", "name": txt[:30],
            "recognize_task_id": "", "recognize_text": "",
            "content": content_json, "base_content": content_json,
            "words": {"start_time": [], "end_time": [], "text": []},
            "current_words": {"start_time": [], "end_time": [], "text": []},
            "font_size": float(fsz), "font_path": font_path, "font_resource_id": font_id,
            "italic_degree": 0, "alignment": 1, "line_max_width": 0.88,
            "has_shadow": True, "shadow_alpha": 0.75, "shadow_distance": 5.0,
            "border_alpha": 1.0, "border_color": "#000000", "border_width": 0.08,
            "background_style": 1 if bg_pill else 0,
            "background_color": "#14080C",
            "background_alpha": 0.45 if bg_pill else 0.0,
            "background_round_radius": 0.28 if bg_pill else 0.0,
            "background_width": 0.12, "background_height": 0.10,
            "fonts": [{
                "id": uid(), "resource_id": font_id, "effect_id": font_id,
                "third_resource_id": "", "category_id": "user", "category_name": "Đã sử dụng gần đây",
                "source_platform": 1, "path": font_path, "title": "Montserrat", "team_id": "", "file_uri": "", "request_id": ""
            }]
        })
        D["materials"]["texts"].append(tm)

        # Text Animation
        anims = []
        if anim_kind == "hook_typewriter":
            anims.append({
                "id": "7210980292243231233", "resource_id": "7210980292243231233", "type": "in", "name": "Máy chữ",
                "category_id": "text", "category_name": "text", "start": 0, "duration": min(dur_u // 2, 750000),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7210980292243231233/6828d67634e66ace1e76c4eb7cc2f8e6",
                "platform": "all", "material_type": "sticker"
            })
        elif anim_kind == "gold_dust":
            anims.append({
                "id": "7331632775948145153", "resource_id": "7331632775948145153", "type": "in", "name": "Bụi vàng",
                "category_id": "text", "category_name": "text", "start": 0, "duration": min(dur_u // 2, 633333),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7331632775948145153/25d1da238cd78c05757f2d6036dec895",
                "platform": "all", "material_type": "sticker"
            })
        elif anim_kind == "text_fade_in":
            anims.append({
                "id": "7648937403646004500", "resource_id": "7648937403646004500", "type": "in", "name": "Chữ mờ dần hiện vào",
                "category_id": "text", "category_name": "text", "start": 0, "duration": min(dur_u // 3, 500000),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7648937403646004500/495e55b3bcd1f6420b6e4b1b44ed1fc8",
                "platform": "all", "material_type": "sticker"
            })
        else:  # sub_fast_fade
            anims.append({
                "id": "6923135604519604737", "resource_id": "6923135604519604737", "type": "in", "name": "Mờ",
                "category_id": "text", "category_name": "text", "start": 0, "duration": min(dur_u // 4, 200000),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6923135604519604737/a5f4d3998c0648ec65c03251506bd0a0",
                "platform": "all", "material_type": "sticker"
            })

        od = min(dur_u // 4, 200000 if anim_kind == "sub_fast" else 366666)
        anims.append({
            "id": "6798320902548230669", "resource_id": "6798320902548230669", "type": "out", "name": "Mờ dần",
            "category_id": "out", "category_name": "out", "start": max(0, dur_u - od), "duration": od,
            "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798320902548230669/c6f05ce62355b537be762550040bfc08",
            "platform": "all", "material_type": "sticker"
        })
        am_id = uid()
        D["materials"]["material_animations"].append({"id": am_id, "type": "sticker_animation", "animations": anims, "multi_language_current": "none"})

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tid,
            "source_timerange": None,
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "extra_material_refs": [am_id],
            "common_keyframes": [], "keyframe_refs": [],
            "render_index": track_ridx
        })
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["transform"] = {"x": 0.0, "y": float(pos_y)}
        return ts

    # Track 3: Tier 1 Golden Brand Titles (#FFD400 at Y = 0.77)
    tr_t1 = {"id": uid(), "type": "text", "attribute": 0, "flag": 0, "is_default_name": True, "name": "", "segments": []}
    # Track 4: Tier 2 Staggered White Sub-Descriptions (#FFFFFF delayed +0.28s at Y = 0.67)
    tr_t2 = {"id": uid(), "type": "text", "attribute": 0, "flag": 0, "is_default_name": True, "name": "", "segments": []}

    GOLD_RGB  = (1.0, 0.835, 0.0)
    WHITE_RGB = (1.0, 1.0, 1.0)
    for item in sub_data["top_titles"]:
        is_hk = item.get("hook", False)
        tr_t1["segments"].append(make_text_seg(
            item["tier1"], item["t0"], item["t1"], pos_y=0.77,
            font_id=FONT_OSWALD_ID if is_hk else FONT_MONTS_ID,
            font_path=FONT_OSWALD_PATH if is_hk else FONT_MONTS_PATH,
            fsz=13.0 if is_hk else 10.5,
            base_rgb=GOLD_RGB, bg_pill=True,
            anim_kind="hook_typewriter" if is_hk else "gold_dust", track_ridx=14001
        ))
        t2_in = min(item["t1"] - 0.5, item["t0"] + 0.28)
        tr_t2["segments"].append(make_text_seg(
            item["tier2"], t2_in, item["t1"], pos_y=0.67,
            font_id=FONT_MONTS_ID, font_path=FONT_MONTS_PATH,
            fsz=9.5 if is_hk else 7.8,
            base_rgb=WHITE_RGB, bg_pill=False,
            anim_kind="text_fade_in", track_ridx=14002
        ))
    D["tracks"].append(tr_t1)
    D["tracks"].append(tr_t2)

    # Track 5: 43 Continuous Proofread Spoken Subtitles (Text Sub at Y = -0.62, Keyword Gold Highlight!)
    tr_sub = {"id": uid(), "type": "text", "attribute": 0, "flag": 0, "is_default_name": True, "name": "", "segments": []}
    for t0_s, t1_s, txt, kws in sub_data["subtitles"]:
        tr_sub["segments"].append(make_text_seg(
            txt, t0_s, t1_s, pos_y=-0.62,
            font_id=FONT_MONTS_ID, font_path=FONT_MONTS_PATH,
            fsz=8.6, base_rgb=WHITE_RGB, hi_rgb=GOLD_RGB, highlights=kws,
            bg_pill=True, anim_kind="sub_fast", track_ridx=14005
        ))
    D["tracks"].append(tr_sub)

    # ==================================================================
    # HELPER FOR NATIVE AUDIO TRACKS (Voice, BGM Ducking, 4 SFX Tracks!)
    # ==================================================================
    amat_cache = {}
    def add_audio_mat(path, name, a_type="extract_music"):
        p_norm = path.replace("\\", "/")
        if p_norm in amat_cache:
            return amat_cache[p_norm]
        dur_u = us(probe_dur_s(path))
        am = copy.deepcopy(amat_tpl)
        aid = uid()
        am.update({"id": aid, "type": a_type, "name": name, "path": p_norm, "duration": dur_u})
        D["materials"]["audios"].append(am)
        amat_cache[p_norm] = (aid, dur_u)
        return aid, dur_u

    def make_audio_seg(path, name, t0_s, dur_s=None, src_in_s=0.0, vol=1.0, micro_fade=False, fade_in_us=0, fade_out_us=0, a_type="sound"):
        aid, mat_dur_u = add_audio_mat(path, name, a_type=a_type)
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
            D["materials"]["audio_fades"].append({
                "id": fid, "type": "audio_fade", "fade_type": 0,
                "fade_in_duration": int(fi_u), "fade_out_duration": int(fo_u)
            })
            arefs.append(fid)

        aseg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": us(src_in_s), "duration": dur_u},
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "speed": 1.0, "volume": float(vol), "last_nonzero_volume": 1.0,
            "extra_material_refs": arefs, "common_keyframes": [], "keyframe_refs": []
        })
        return aseg

    # Track 6: Clean Studio-EQ Voiceover (Segmented cleanly across 13 blocks with Micro-Fade + vol 1.22!)
    tr_vo = copy.deepcopy(atrack_tpl); tr_vo["id"] = uid(); tr_vo["segments"] = []
    vo_p = os.path.join(MEDIA, "01_Voice_Clean_Master.wav")
    for seg_info in aroll_plan:
        tr_vo["segments"].append(make_audio_seg(
            vo_p, "01_Voice_Chị_Oanh_Clean", seg_info["t0"], dur_s=seg_info["dur"],
            src_in_s=seg_info["t0"], vol=1.22, micro_fade=True, a_type="extract_music"
        ))
    D["tracks"].append(tr_vo)

    # Track 7: BGM with Dynamic Ducking (Intro boost -> Voice Pocket 0.28 -> Outro boost!)
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["segments"] = []
    bgm_p = aud_man["bgm"]
    bgm_regions = [
        (  0.00,   4.60, 0.44, 400000, 200000),  # Hook upbeat intro
        (  4.60,  68.85, 0.27, 200000, 200000),  # Duck cleanly under product tour
        ( 68.85, 108.50, 0.28, 200000, 200000),  # Emotional SKA NEST + Gratitude
        (108.50, 112.43, 0.46, 300000, 900000),  # Warm Outro swell & smooth fade out
    ]
    for b0, b1, bvol, fi_u, fo_u in bgm_regions:
        tr_bgm["segments"].append(make_audio_seg(
            bgm_p, "02_BGM_SetQua_2011", b0, dur_s=(b1 - b0),
            src_in_s=b0, vol=bvol, fade_in_us=fi_u, fade_out_us=fo_u, a_type="music"
        ))
    D["tracks"].append(tr_bgm)

    # Load SFX bank paths
    SFX = aud_man["sfx"]
    def add_non_overlapping_sfx_tracks(cue_list):
        # Automatically packs cues into minimal non-overlapping CapCut audio tracks!
        cue_list = sorted(cue_list, key=lambda x: x[0])
        lanes = []  # list of (end_us, track_obj)
        for t_s, skey, vol in cue_list:
            if skey not in SFX:
                continue
            sp = SFX[skey]
            seg = make_audio_seg(sp["path"], sp["name"], t_s, dur_s=sp["dur"], src_in_s=0.0, vol=vol, micro_fade=True, a_type="sound")
            s_start = seg["target_timerange"]["start"]
            s_end   = s_start + seg["target_timerange"]["duration"] + 33333
            placed = False
            for li, (l_end, tr_obj) in enumerate(lanes):
                if s_start >= l_end:
                    tr_obj["segments"].append(seg)
                    lanes[li] = (s_end, tr_obj)
                    placed = True
                    break
            if not placed:
                nt = copy.deepcopy(atrack_tpl); nt["id"] = uid(); nt["segments"] = [seg]
                lanes.append((s_end, nt))
        for _, tr_obj in lanes:
            D["tracks"].append(tr_obj)
        return len(cue_list), len(lanes)

    # Curated Commercial SFX Cues:
    # A. Transitions, Risers, Reveals & Camera Shutters (Synced to every scene & B-roll cut!)
    trans_cues = [
        (  0.04, "magic_reveal", 0.62),
        (  1.42, "whoosh_tvc",   0.52),
        (  2.82, "shutter",      0.48),
        (  4.75, "deep_woosh",   0.50),
        ( 10.28, "whoosh_tvc",   0.48),
        ( 11.78, "whoosh_pip",   0.45),  # PIP 1 slide in
        ( 14.80, "riser_metal",  0.34),  # Pre-riser into Showcase 1
        ( 15.92, "magic_reveal", 0.56),  # Showcase 1: SKA NEST Bird's Nest
        ( 20.65, "swoosh_soft",  0.46),  # Crossfade to 4 ingredients
        ( 25.32, "whoosh_tvc",   0.45),
        ( 28.50, "deep_woosh",   0.50),  # Showcase 2: Dual Seaweed Jars
        ( 28.70, "shutter",      0.42),
        ( 33.62, "swoosh_soft",  0.44),
        ( 35.76, "whoosh_tvc",   0.50),  # Showcase 3: Bánh Thuyền Mix Hạt
        ( 35.95, "shutter",      0.42),
        ( 39.68, "swoosh_soft",  0.42),
        ( 42.16, "whoosh_tvc",   0.50),  # Showcase 4: Rong Biển Kẹp Hạt 500g
        ( 42.35, "shutter",      0.42),
        ( 46.82, "whoosh_pip",   0.45),  # PIP 2 slide in
        ( 49.95, "deep_woosh",   0.50),  # Enter Mica Basket B-roll
        ( 52.26, "whoosh_tvc",   0.46),
        ( 54.62, "swoosh_soft",  0.42),
        ( 57.16, "whoosh_tvc",   0.50),  # Macro Leather Handle
        ( 63.16, "whoosh_tvc",   0.48),  # Macro Flowers & Ribbon
        ( 68.85, "star_sparkle", 0.50),  # "Giá trị nhất của set quà"
        ( 70.60, "riser_metal",  0.35),  # Pre-riser into Glowing Tổ Yến
        ( 71.72, "magic_reveal", 0.60),  # Showcase 5: Glowing Tổ Yến SKA NEST
        ( 76.70, "whoosh_tvc",   0.46),
        ( 80.36, "whoosh_tvc",   0.46),  # Close-up Cẩm Nang
        ( 85.42, "whoosh_pip",   0.44),  # PIP 3 slide in
        ( 90.26, "deep_woosh",   0.50),  # F20 Direct Factory
        ( 93.06, "whoosh_tvc",   0.48),
        ( 94.96, "swoosh_soft",  0.45),
        ( 96.76, "whoosh_tvc",   0.48),
        ( 98.56, "star_sparkle", 0.48),  # Gratitude section
        (101.32, "whoosh_tvc",   0.48),  # Customer Handover B-roll
        (105.80, "magic_reveal", 0.58),  # Luxury End-Card Đặt Quà 20/11
    ]

    # B. Text Titles, Ingredient Pills, Weight Badges & Subtitle Keyword Pops!
    text_sfx_cues = [
        (  0.08, "typewriter",   0.48),  # Hook typewriter
        (  0.36, "pop_tvc",      0.52),  # Hook sub-line
        (  4.48, "whoosh_pip",   0.44),  # Intro badge
        ( 10.32, "pop_tvc",      0.48),  # Món 01 title
        ( 15.96, "ting_quick",   0.46),  # SKA NEST title
        # 4 Ingredient Pills popping in Showcase 1!
        ( 21.48, "pop_tvc",      0.50),  # Táo đỏ
        ( 22.38, "pop_soft",     0.50),  # Đông trùng hạ thảo
        ( 23.68, "pop_tvc",      0.50),  # Kỷ tử
        ( 24.45, "ting_quick",   0.48),  # 1 hộp đường phèn
        # Món 02 + 2 Flavor Callouts
        ( 25.48, "pop_tvc",      0.48),
        ( 28.82, "pop_soft",     0.48),  # Cay nhẹ
        ( 31.32, "ting_quick",   0.46),  # Sấy mè không cay
        # Món 03 + 250g badge
        ( 33.78, "pop_tvc",      0.48),
        ( 36.12, "ting_quick",   0.46),
        # Món 04 + 500g + 22-24 thanh
        ( 40.08, "pop_tvc",      0.48),
        ( 42.48, "pop_soft",     0.48),
        ( 44.58, "ting_quick",   0.50),  # 22-24 thanh
        # Packaging Titles (Mica, Quai da, Hoa & nơ)
        ( 50.04, "notif_bell",   0.46),
        ( 56.92, "pop_tvc",      0.46),
        ( 61.88, "ting_quick",   0.46),
        # SKA NEST Core Value + Cẩm nang + Hướng dẫn chưng yến
        ( 72.10, "ting_quick",   0.50),
        ( 76.84, "notif_bell",   0.48),
        ( 85.40, "ting_quick",   0.46),
        # F20 Factory + Gratitude + End-Card Hotline!
        ( 90.34, "notif_bell",   0.48),
        ( 95.15, "ting_quick",   0.46),
        ( 98.70, "pop_tvc",      0.45),
        (106.10, "notif_bell",   0.56),  # Hotline/Zalo reveal chime
        (109.25, "ting_quick",   0.52),  # Lễ 20/11 inbox ngay!
    ]
    # Also add subtle telop touch every ~3rd subtitle phrase opening so Text Sub feels responsive & alive!
    for idx_s, (st_s, _, _, _) in enumerate(sub_data["subtitles"]):
        if idx_s % 2 == 0:
            text_sfx_cues.append((st_s + 0.02, "pop_telop", 0.24))

    n_tc, n_tl = add_non_overlapping_sfx_tracks(trans_cues)
    n_xc, n_xl = add_non_overlapping_sfx_tracks(text_sfx_cues)
    print(f"Packed {n_tc} Transition SFX into {n_tl} tracks, and {n_xc} Text/UI SFX into {n_xl} tracks!")

    # ==================================================================
    # SAVE BACKUP DRAFT + WRITE DIRECTLY INTO "F20 vd 1" + SYNC TIMELINES!
    # ==================================================================
    # 1. Create standalone backup draft "F20 vd 1 - Bản Nháp Gốc" once so user never loses old 05:58 assembly
    bak_draft_name = "F20 vd 1 - Bản Nháp Gốc"
    bak_draft_dir  = os.path.join(DRAFTS_DIR, bak_draft_name)
    if not os.path.exists(bak_draft_dir):
        os.makedirs(bak_draft_dir, exist_ok=True)
        shutil.copy2(os.path.join(BAK_DIR, "draft_content.json.orig"), os.path.join(bak_draft_dir, "draft_content.json"))
        bm = copy.deepcopy(orig_dm)
        bm["draft_id"] = uid()
        bm["draft_name"] = bak_draft_name
        bm["draft_fold_path"] = bak_draft_dir.replace("\\", "/")
        json.dump(bm, open(os.path.join(bak_draft_dir, "draft_meta_info.json"), "w", encoding="utf-8"), ensure_ascii=False)
        if os.path.exists(os.path.join(F20_DIR, "draft_cover.jpg")):
            shutil.copy2(os.path.join(F20_DIR, "draft_cover.jpg"), os.path.join(bak_draft_dir, "draft_cover.jpg"))

    # 2. Write upgraded draft_content.json into F20 vd 1 root AND fresh Timelines/<tl_id>!
    cover_jpg = os.path.join(F20_DIR, "draft_cover.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", os.path.join(MEDIA, "showcase_06_outro_endcard.mp4"), "-frames:v", "1", cover_jpg], check=True)

    dc_json_str = json.dumps(D, ensure_ascii=False)
    open(os.path.join(F20_DIR, "draft_content.json"), "w", encoding="utf-8").write(dc_json_str)
    # Remove root template-2.tmp if present so CapCut doesn't restore stale tmp
    for stale in ["template-2.tmp", "template.tmp"]:
        sp = os.path.join(F20_DIR, stale)
        if os.path.exists(sp):
            os.remove(sp)

    # Clean old Timelines subdirs & write clean fresh main timeline (zero stale mini_draft.json patch override!)
    tl_root = os.path.join(F20_DIR, "Timelines")
    if os.path.exists(tl_root):
        for entry in os.listdir(tl_root):
            ep = os.path.join(tl_root, entry)
            if os.path.isdir(ep):
                shutil.rmtree(ep)
    os.makedirs(tl_root, exist_ok=True)
    new_tl_id = uid()
    new_tl_dir = os.path.join(tl_root, new_tl_id)
    os.makedirs(new_tl_dir, exist_ok=True)
    open(os.path.join(new_tl_dir, "draft_content.json"), "w", encoding="utf-8").write(dc_json_str)
    shutil.copy2(cover_jpg, os.path.join(new_tl_dir, "draft_cover.jpg"))

    now_us = int(time.time() * 1_000_000)
    proj_j = {
        "config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False},
        "create_time": now_us, "id": new_tl_id, "main_timeline_id": new_tl_id,
        "timelines": [{"create_time": now_us, "id": new_tl_id, "is_marked_delete": False, "name": "Bản Hoàn Thiện Pro", "update_time": now_us}],
        "update_time": now_us, "version": 0
    }
    json.dump(proj_j, open(os.path.join(tl_root, "project.json"), "w", encoding="utf-8"), ensure_ascii=False)

    # Update draft_meta_info.json & root_meta_info.json duration/timestamp
    M = copy.deepcopy(orig_dm)
    M["tm_duration"] = TOTAL_US
    M["tm_draft_modified"] = now_us
    M["draft_cover"] = "draft_cover.jpg"
    json.dump(M, open(os.path.join(F20_DIR, "draft_meta_info.json"), "w", encoding="utf-8"), ensure_ascii=False)

    rm_path = os.path.join(DRAFTS_DIR, "root_meta_info.json")
    if os.path.exists(rm_path):
        shutil.copy2(rm_path, os.path.join(BAK_DIR, "root_meta_info.json.bak"))
        rm = json.load(open(rm_path, encoding="utf-8"))
        for item in rm.get("all_draft_store", []):
            if item.get("draft_name") == "F20 vd 1":
                item["tm_duration"] = TOTAL_US
                item["tm_draft_modified"] = now_us
        json.dump(rm, open(rm_path, "w", encoding="utf-8"), ensure_ascii=False)

    print(f"SUCCESSFULLY UPGRADED CapCut Project 'F20 vd 1' ({TOTAL_DUR:.2f}s, {len(D['tracks'])} tracks)!")

if __name__ == "__main__":
    main()
