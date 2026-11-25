import copy, json, os, shutil, subprocess, time, uuid

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
TEMPLATE_NAME = "LT PLUS HẰNG THU - Video Mẫu"
OUT_NAME = "BOJOMI_AnVuong_TalkingHead_v1"

PROJ_DIR = r"d:\AI\full studio\output\av-protein-talking-head"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")

FONT_SUB_ID = "7542214368361057553"
FONT_SUB_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7542214368361057553/d376267c892ee3a53654ae93a78dcfb7/font.ttf"
FONT_BOLD_ID = "7517455788122705168"
FONT_BOLD_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7517455788122705168/91d28cfa5e7db054f4872f1ae2417ac2/Montserrat-Bold.otf"

def uid():
    return str(uuid.uuid4()).upper()

def us(sec):
    return int(round(sec * 30.0) / 30.0 * 1_000_000)

def probe_video(path):
    j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "json", path
    ], text=True))
    w = int(j["streams"][0]["width"])
    h = int(j["streams"][0]["height"])
    dur = float(j["format"]["duration"])
    return w, h, dur

def kf_pair(prop, dur_us, v0, v1):
    return {
        "id": uid(),
        "material_id": "",
        "property_type": prop,
        "keyframe_list": [
            {
                "id": uid(), "curveType": "Line", "time_offset": 0,
                "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
                "values": [float(v0)], "string_value": "", "graphID": ""
            },
            {
                "id": uid(), "curveType": "Line", "time_offset": int(dur_us),
                "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
                "values": [float(v1)], "string_value": "", "graphID": ""
            }
        ]
    }

def kf_alpha_fade(dur_us, fade_us=233333):
    f = min(fade_us, dur_us // 3)
    return {
        "id": uid(),
        "material_id": "",
        "property_type": "KFTypeAlpha",
        "keyframe_list": [
            {"id": uid(), "curveType": "Line", "time_offset": 0, "left_control": {"x":0.0,"y":0.0}, "right_control": {"x":0.0,"y":0.0}, "values": [0.0], "string_value": "", "graphID": ""},
            {"id": uid(), "curveType": "Line", "time_offset": int(f), "left_control": {"x":0.0,"y":0.0}, "right_control": {"x":0.0,"y":0.0}, "values": [1.0], "string_value": "", "graphID": ""},
            {"id": uid(), "curveType": "Line", "time_offset": int(max(f+1, dur_us - f)), "left_control": {"x":0.0,"y":0.0}, "right_control": {"x":0.0,"y":0.0}, "values": [1.0], "string_value": "", "graphID": ""},
            {"id": uid(), "curveType": "Line", "time_offset": int(dur_us), "left_control": {"x":0.0,"y":0.0}, "right_control": {"x":0.0,"y":0.0}, "values": [0.0], "string_value": "", "graphID": ""}
        ]
    }

def build():
    tpl_dir = os.path.join(DRAFTS_DIR, TEMPLATE_NAME)
    out_dir = os.path.join(DRAFTS_DIR, OUT_NAME)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    T = json.load(open(os.path.join(tpl_dir, "draft_content.json"), encoding="utf-8"))
    TM = json.load(open(os.path.join(tpl_dir, "draft_meta_info.json"), encoding="utf-8"))

    vseg_tpl = next(s for tr in T["tracks"] if tr["type"] == "video" for s in tr["segments"])
    extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    tmat_tpl = {k: next(x for x in T["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"]) for k in extra_keys}
    vmat_tpl = next(x for x in T["materials"]["videos"] if x["id"] == vseg_tpl["material_id"])

    txseg_tpl = next(s for tr in T["tracks"] if tr["type"] == "text" for s in tr["segments"])
    txmat_tpl = next(x for x in T["materials"]["texts"] if x["id"] == txseg_tpl["material_id"])
    anim_tpl = next(x for x in T["materials"]["material_animations"] if x["id"] in txseg_tpl["extra_material_refs"])
    vtrack_tpl = next(tr for tr in T["tracks"] if tr["type"] == "video")
    ttrack_tpl = next(tr for tr in T["tracks"] if tr["type"] == "text")

    D = copy.deepcopy(T)
    draft_id = uid()
    D.update({
        "id": draft_id,
        "name": OUT_NAME,
        "fps": 30.0,
        "tracks": [],
        "materials": {k: [] for k in T["materials"]},
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None}
    })

    video_mat_cache = {}
    def ensure_video_mat(fpath):
        norm_p = os.path.abspath(fpath).replace("\\", "/")
        if norm_p in video_mat_cache:
            return video_mat_cache[norm_p]
        w, h, dur = probe_video(fpath)
        m = copy.deepcopy(vmat_tpl)
        m.update({
            "id": uid(),
            "type": "video",
            "path": norm_p,
            "material_name": os.path.basename(norm_p),
            "width": w,
            "height": h,
            "duration": us(dur),
            "has_audio": True
        })
        D["materials"]["videos"].append(m)
        video_mat_cache[norm_p] = (m["id"], w, h, dur)
        return video_mat_cache[norm_p]

    def make_video_seg(fpath, src_st, dur_s, dst_st, vol=0.0, scale=1.0, tx=0.0, ty=0.0,
                       add_audio_fade=False, zoom_pair=None, alpha_fade=False, slide_in=False, rect_mask=False, render_idx=0):
        mid, w, h, full_dur = ensure_video_mat(fpath)
        dur_u = us(dur_s)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k in extra_keys:
            em = copy.deepcopy(tmat_tpl[k])
            em["id"] = uid()
            if k == "speeds":
                em["speed"] = 1.0
            D["materials"][k].append(em)
            refs.append(em["id"])

        if add_audio_fade:
            fid = uid()
            D["materials"]["audio_fades"].append({
                "id": fid, "type": "audio_fade", "fade_type": 0,
                "fade_in_duration": 33333, "fade_out_duration": 66666
            })
            refs.append(fid)

        if slide_in:
            aid = uid()
            am = copy.deepcopy(anim_tpl)
            am["id"] = aid
            am["animations"] = [
                {
                    "id": "6798332871267324423", "resource_id": "6798332871267324423",
                    "type": "in", "name": "Trượt sang trái", "category_id": "in", "category_name": "in",
                    "duration": 400000, "start": 0,
                    "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798332871267324423/667952e8cf6918f62e16b8e6dfc2fef2",
                    "platform": "all", "material_type": "video"
                },
                {
                    "id": "6798320902548230669", "resource_id": "6798320902548230669",
                    "type": "out", "name": "Mờ dần", "category_id": "out", "category_name": "out",
                    "duration": 366666, "start": max(0, dur_u - 366666),
                    "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798320902548230669/c6f05ce62355b537be762550040bfc08",
                    "platform": "all", "material_type": "video"
                }
            ]
            D["materials"]["material_animations"].append(am)
            refs.append(aid)

        if rect_mask:
            mk_id = uid()
            D["materials"].setdefault("common_mask", []).append({
                "id": mk_id, "type": "mask", "category": "video", "category_name": "", "category_id": "",
                "panel": "", "is_old_version": False,
                "resource_id": "7374021450748924432",
                "constant_material_id": uid(),
                "name": "Hình chữ nhật",
                "resource_type": "rectangle",
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef",
                "position_info": "",
                "config": {
                    "width": 0.94, "height": 0.94, "centerX": 0.0, "centerY": 0.0,
                    "rotation": 0.0, "feather": 0.02, "expansion": 0.0,
                    "roundCorner": 0.18, "invert": False, "aspectRatio": 1.0
                },
                "text_config": {"content": "", "font_name": "", "font_path": "", "font_resource_id": "", "font_size": 15.0, "bold_width": 0.0, "italic_degree": 0, "has_underline": False, "line_gap": 0.0, "char_spacing": 0.0, "align_type": 15, "scale": 1.0},
                "platform": "all", "loader_work_space": "", "track_segment": "", "contour_path": None, "source_platform": 0
            })
            refs.append(mk_id)

        kfs = []
        if zoom_pair:
            z0, z1 = zoom_pair
            kfs.append(kf_pair("KFTypeScaleX", dur_u, z0, z1))
            kfs.append(kf_pair("KFTypeScaleY", dur_u, z0, z1))
        if alpha_fade:
            kfs.append(kf_alpha_fade(dur_u))

        seg.update({
            "id": uid(),
            "material_id": mid,
            "source_timerange": {"start": us(src_st), "duration": dur_u},
            "target_timerange": {"start": us(dst_st), "duration": dur_u},
            "speed": 1.0,
            "volume": float(vol),
            "last_nonzero_volume": 1.0,
            "extra_material_refs": refs,
            "common_keyframes": kfs,
            "keyframe_refs": [],
            "render_index": render_idx,
            "clip": {
                "scale": {"x": float(scale), "y": float(scale)},
                "rotation": 0.0,
                "rotation3d": [],
                "transform": {"x": float(tx), "y": float(ty)},
                "flip": {"vertical": False, "horizontal": False},
                "alpha": 1.0
            },
            "uniform_scale": {"on": True, "value": float(scale)}
        })
        return seg

    def make_text_seg(text, dst_st, dur_s, color_rgb, size, tx, ty, bold=False, fade_anim=True, stroke_w=0.08, render_idx=14000):
        dur_u = us(dur_s)
        tm = copy.deepcopy(txmat_tpl)
        tid = uid()
        fid = FONT_BOLD_ID if bold else FONT_SUB_ID
        fpath = FONT_BOLD_PATH if bold else FONT_SUB_PATH
        content_obj = {
            "text": text,
            "styles": [{
                "fill": {"content": {"render_type": "solid", "solid": {"color": list(color_rgb)}}},
                "font": {"path": fpath, "id": fid},
                "size": float(size),
                "range": [0, len(text)],
                "strokes": [{"content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}}, "width": float(stroke_w), "mode": 0}],
                "useLetterColor": True
            }]
        }
        tm.update({
            "id": tid,
            "content": json.dumps(content_obj, ensure_ascii=False),
            "base_content": text,
            "font_id": fid,
            "font_path": fpath,
            "font_size": float(size),
            "global_alpha": 1.0
        })
        D["materials"]["texts"].append(tm)

        am = copy.deepcopy(anim_tpl)
        aid = uid()
        am["id"] = aid
        if fade_anim:
            in_id = "7648937403646004500" if bold else "6923135604519604737"
            in_name = "Chữ mờ dần hiện vào" if bold else "Mờ"
            in_path = (
                "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7648937403646004500/495e55b3bcd1f6420b6e4b1b44ed1fc8"
                if bold else
                "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6923135604519604737/a5f4d3998c0648ec65c03251506bd0a0"
            )
            am["animations"] = [
                {
                    "id": in_id, "resource_id": in_id, "type": "in", "name": in_name,
                    "category_id": "text", "category_name": "text",
                    "duration": min(366666, dur_u // 3), "start": 0,
                    "path": in_path, "platform": "all", "material_type": "sticker"
                },
                {
                    "id": "6798320902548230669", "resource_id": "6798320902548230669",
                    "type": "out", "name": "Mờ dần", "category_id": "out", "category_name": "out",
                    "duration": min(333333, dur_u // 3), "start": max(0, dur_u - min(333333, dur_u // 3)),
                    "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798320902548230669/c6f05ce62355b537be762550040bfc08",
                    "platform": "all", "material_type": "sticker"
                }
            ]
        else:
            am["animations"] = []
        D["materials"]["material_animations"].append(am)

        seg = copy.deepcopy(txseg_tpl)
        seg.update({
            "id": uid(),
            "material_id": tid,
            "source_timerange": None,
            "target_timerange": {"start": us(dst_st), "duration": dur_u},
            "extra_material_refs": [aid],
            "common_keyframes": [],
            "keyframe_refs": [],
            "render_index": render_idx,
            "clip": {
                "scale": {"x": 1.0, "y": 1.0},
                "rotation": 0.0,
                "rotation3d": [],
                "transform": {"x": float(tx), "y": float(ty)},
                "flip": {"vertical": False, "horizontal": False},
                "alpha": 1.0
            }
        })
        return seg

    # === TRACK 0: MAIN A-ROLL (10 editable sentence cuts from raw_trim30_lufs.mp4, or aroll.mp4) ===
    # Create loudness-normalized raw_trim30_lufs.mp4 so every cut in CapCut already sits at -14 LUFS!
    trim_src = os.path.join(AROLL_DIR, "raw_trim30.mp4")
    trim_lufs = os.path.join(AROLL_DIR, "raw_trim30_lufs.mp4")
    if not os.path.exists(trim_lufs):
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", trim_src,
            "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
            trim_lufs
        ], check=True)

    edl = json.load(open(os.path.join(AROLL_DIR, "aroll.edl.json"), encoding="utf-8"))
    total_dur = float(edl["out_duration"])

    tr0 = copy.deepcopy(vtrack_tpl); tr0["id"] = uid(); tr0["segments"] = []
    toggle = False
    for r in edl["keep"]:
        s0, s1, o0 = r["src_start"], r["src_end"], r["out_start"]
        dur_s = s1 - s0
        zp = None
        if dur_s >= 2.2:
            zp = (1.00, 1.06) if not toggle else (1.06, 1.00)
            toggle = not toggle
        tr0["segments"].append(make_video_seg(
            trim_lufs, s0, dur_s, o0, vol=1.18, scale=1.0,
            add_audio_fade=True, zoom_pair=zp, render_idx=0
        ))
    D["tracks"].append(tr0)

    # === TRACK 1: FULL-SCREEN 9:16 AI B-ROLL CLIPS ===
    tr1 = copy.deepcopy(vtrack_tpl); tr1["id"] = uid(); tr1["segments"] = []
    broll_plan = [
        ("broll_c02.mp4", 0.0, 5.6, 3.55, (1.01, 1.07)),
        ("broll_c05.mp4", 0.0, 4.3, 24.94, (1.01, 1.06)),
        ("broll_c06.mp4", 0.0, 3.3, 37.18, (1.06, 1.01)),
        ("broll_c09.mp4", 0.3, 5.1, 57.40, (1.01, 1.06)),
    ]
    for fname, src_in, dur_s, dst_st, zp in broll_plan:
        fp = os.path.join(MEDIA_DIR, fname)
        if os.path.exists(fp):
            _, _, vdur = probe_video(fp)
            use_in = src_in if vdur > src_in + 1.0 else 0.0
            use_dur = min(dur_s, max(0.5, vdur - use_in))
            tr1["segments"].append(make_video_seg(
                fp, use_in, use_dur, dst_st, vol=0.0, scale=1.02,
                zoom_pair=zp, alpha_fade=True, render_idx=1000
            ))
    D["tracks"].append(tr1)

    # === TRACK 2: FLOATING 3D AI ICONS & AUTHENTIC PACKSHOT PIP (Face-Safe Upper-Right Zone) ===
    tr2 = copy.deepcopy(vtrack_tpl); tr2["id"] = uid(); tr2["segments"] = []
    pip_plan = [
        # (file, dur, dst_start, scale, tx, ty, rect_mask)
        ("hook_01_clean.mp4", 1.48, 0.30, 0.40, 0.54, 0.54, True),
        ("hook_02_clean.mp4", 1.62, 1.82, 0.40, 0.54, 0.54, True),
        ("icon_c04_clean.mp4", 4.20, 20.65, 0.40, 0.54, 0.54, True),
        ("icon_c07_clean.mp4", 3.90, 40.45, 0.40, 0.54, 0.54, True),
        ("icon_c08_clean.mp4", 6.20, 44.80, 0.40, 0.54, 0.54, True),
        ("packshot_c08_clean.mp4", 5.95, 51.30, 0.40, 0.54, 0.54, True),
    ]
    for fname, dur_s, dst_st, sc, tx, ty, rmask in pip_plan:
        fp = os.path.join(MEDIA_DIR, fname)
        if os.path.exists(fp):
            tr2["segments"].append(make_video_seg(
                fp, 0.0, dur_s, dst_st, vol=0.0, scale=sc, tx=tx, ty=ty,
                slide_in=True, rect_mask=rmask, render_idx=2000
            ))
    D["tracks"].append(tr2)

    # === TRACK 3 & TRACK 4: DUAL-TIER PHARMACIST TYPOGRAPHY (Staggered +0.20s) ===
    WHITE = [1.0, 1.0, 1.0]
    GOLD = [1.0, 0.83137255, 0.0]
    MINT_CREAM = [0.88, 0.98, 0.93]

    dual_titles = [
        # (start, end, small_label, big_keyword)
        (0.25, 1.78, "MUỐN CON PHÁT TRIỂN", "CAO LỚN"),
        (1.82, 3.42, "ĐÃ QUAN TÂM ĐÚNG", "BỮA ĂN HẰNG NGÀY?"),
        (3.60, 9.45, "THỰC TRẠNG SINH HOẠT", "ĂN THẤT THƯỜNG • LỊCH KÍN"),
        (10.00, 15.30, "BỐ MẸ BĂN KHOĂN", "ĐÃ ĐỦ DINH DƯỠNG CHƯA?"),
        (20.60, 24.85, "XEM XÉT 3 YẾU TỐ", "CHẾ ĐỘ ĂN • ĐỘ TUỔI • NHU CẦU"),
        (25.00, 29.25, "DƯỠNG CHẤT CHO XƯƠNG", "CANXI & VITAMIN D"),
        (29.50, 34.40, "GÓC NHÌN KHOA HỌC", "CẦN ĐÚNG CƠ CHẾ HẤP THU"),
        (34.60, 40.30, "BOJOMI AN VƯỢNG", "CANXI TỪ TẢO BIỂN"),
        (40.45, 44.40, "CÔNG THỨC HIỆP ĐỒNG", "VITAMIN D3 + K2 + COLLAGEN"),
        (44.80, 51.15, "HÀM LƯỢNG TRONG 1 GÓI", "418mg CANXI TẢO BIỂN"),
        (51.30, 57.30, "ĐỊNH LƯỢNG RÕ RÀNG", "779 IU D3 • 170mcg K2 MK7"),
        (57.45, 62.50, "TIỆN LỢI MỖI NGÀY", "1 GÓI • ĐỦ DINH DƯỠNG XƯƠNG"),
        (62.80, 69.80, "NHẬN BẢNG THÀNH PHẦN", "NHẮN: DINH DƯỠNG CHO CON"),
    ]
    tr3 = copy.deepcopy(ttrack_tpl); tr3["id"] = uid(); tr3["segments"] = []
    tr4 = copy.deepcopy(ttrack_tpl); tr4["id"] = uid(); tr4["segments"] = []
    for st, en, t_small, t_big in dual_titles:
        dur1 = max(0.8, en - st)
        tr3["segments"].append(make_text_seg(t_small, st, dur1, MINT_CREAM, 6.8, 0.0, -0.57, bold=True, fade_anim=True, render_idx=14000))
        st2 = min(en - 0.5, st + 0.20)
        dur2 = max(0.6, en - st2)
        tr4["segments"].append(make_text_seg(t_big, st2, dur2, GOLD, 9.6, 0.0, -0.67, bold=True, fade_anim=True, render_idx=15000))
    D["tracks"].append(tr3)
    D["tracks"].append(tr4)

    # === TRACK 5: CONTINUOUS VIETNAMESE SUBTITLES (Word-Synced Phrases, <= 7 words/phrase, Y = -0.74) ===
    atr = json.load(open(os.path.join(AROLL_DIR, "aroll_direct.json"), encoding="utf-8"))
    all_words = [w for s in atr["segments"] for w in s["words"]]
    phrases = []
    cur = []
    for w in all_words:
        cur.append(w)
        txt_len = sum(len(x["word"]) + 1 for x in cur)
        has_punc = w["word"].endswith((",", ".", "?"))
        if len(cur) >= 7 or txt_len >= 34 or has_punc:
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)

    tr5 = copy.deepcopy(ttrack_tpl); tr5["id"] = uid(); tr5["segments"] = []
    for i, pw in enumerate(phrases):
        pst = pw[0]["start"]
        pen = pw[-1]["end"]
        if i + 1 < len(phrases):
            nxt = phrases[i + 1][0]["start"]
            if nxt - pen < 0.35:
                pen = max(pst + 0.35, nxt - 0.04)
        dur_p = max(0.35, pen - pst)
        line = " ".join(x["word"] for x in pw).upper()
        tr5["segments"].append(make_text_seg(line, pst, dur_p, WHITE, 6.0, 0.0, -0.79, bold=False, fade_anim=True, render_idx=16000))
    D["tracks"].append(tr5)

    # === TRACK 6: FIXED LEGAL DISCLAIMER AT BOTTOM (Y = -0.91) ===
    tr6 = copy.deepcopy(ttrack_tpl); tr6["id"] = uid(); tr6["segments"] = []
    tr6["segments"].append(make_text_seg(
        "Thực phẩm bổ sung • Không phải là thuốc, không thay thế thuốc chữa bệnh",
        0.0, total_dur, [0.90, 0.90, 0.90], 4.4, 0.0, -0.91, bold=False, fade_anim=False, stroke_w=0.06, render_idx=17000
    ))
    D["tracks"].append(tr6)

    D["duration"] = us(total_dur)

    # Write new CapCut 191.0.0 draft folder (including Timelines/<tl_id>/draft_content.json!)
    os.makedirs(out_dir, exist_ok=True)
    for aux in ["draft_settings", "draft_agency_config.json", "draft_biz_config.json", "draft_virtual_store.json", "key_value.json", "performance_opt_info.json", "timeline_layout.json"]:
        sp = os.path.join(tpl_dir, aux)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(out_dir, aux))

    # Cover image from Hook frame
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "1.0", "-i", trim_lufs, "-frames:v", "1",
        os.path.join(out_dir, "draft_cover.jpg")
    ], check=True)

    with open(os.path.join(out_dir, "draft_content.json"), "w", encoding="utf-8") as f:
        json.dump(D, f, ensure_ascii=False)

    # Mirror into Timelines/<tl_id>/draft_content.json
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
        tp["id"] = uid()
        tp["create_time"] = now_us
        tp["update_time"] = now_us
        tp["main_timeline_id"] = tl_id
        if tp.get("timelines"):
            tp["timelines"] = [tp["timelines"][0]]
            tp["timelines"][0]["id"] = tl_id
            tp["timelines"][0]["create_time"] = now_us
            tp["timelines"][0]["update_time"] = now_us
        with open(os.path.join(tl_root, "project.json"), "w", encoding="utf-8") as f:
            json.dump(tp, f, ensure_ascii=False)

    now_us = int(time.time() * 1_000_000)
    M = copy.deepcopy(TM)
    M.update({
        "draft_id": draft_id,
        "draft_name": OUT_NAME,
        "draft_fold_path": out_dir.replace("\\", "/"),
        "draft_root_path": DRAFTS_DIR.replace("\\", "/"),
        "draft_cover": "draft_cover.jpg",
        "tm_duration": D["duration"],
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "draft_timeline_materials_size_": 0
    })
    with open(os.path.join(out_dir, "draft_meta_info.json"), "w", encoding="utf-8") as f:
        json.dump(M, f, ensure_ascii=False)

    print(f"Created CapCut Draft: {out_dir}")
    print(f"Tracks: {len(D['tracks'])} | Videos: {len(D['materials']['videos'])} | Texts: {len(D['materials']['texts'])} | Duration: {total_dur:.2f}s")

if __name__ == "__main__":
    build()
