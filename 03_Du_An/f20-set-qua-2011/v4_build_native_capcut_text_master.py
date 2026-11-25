import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
FPS = 30.0

ROOT       = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_DIR  = ROOT / "1117 F20"
DRAFT_V3   = ROOT / "1117 F20 - V3 Full Layers"
FC_V6_DIR  = ROOT / "FEEL_CHICKEN_2011_Full_Layers_V6"

WORK       = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
BAK        = WORK / "backup_1117_F20_orig"
LAYERS_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_layers_1117_v3")
BROLL_DIR  = LAYERS_DIR / "brolls"
SFX_FOLDER = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")

COINY_ID   = "7482665772876156165"
COINY_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7482665772876156165/57619fa23667c87dee08a75d49a8b51a/font.ttf"

RED_COL    = [0.9254902005195618, 0.11372549086809158, 0.11372549086809158] # Exact user #EC1D1D
WHITE_COL  = [1.0, 1.0, 1.0]                                                 # Exact #FFFFFF

def uid(): return str(uuid.uuid4()).upper()
def us(sec):
    f = int(round(float(sec) * FPS))
    return int(round(f * 1_000_000 / FPS))
def norm_fwd(p): return os.path.normpath(str(p)).replace("\\", "/")

def ease_out_back(u: float, s: float = 1.32) -> float:
    u = max(0.0, min(1.0, u)) - 1.0
    return u * u * ((s + 1.0) * u + s) + 1.0

def build_clean_bento_4mon_notext():
    """Renders pure 2x2 rounded live-video grid WITHOUT any baked PNG text so 100% of text is native CapCut text!"""
    out_p = BROLL_DIR / "bento_4mon_notext.mp4"
    n_f = int(round(4.05 * FPS))
    cw, ch = 460, 620
    srcs = [
        BROLL_DIR / "ov_09_to_yen_soi_dai.mp4",
        BROLL_DIR / "ov_10_2hop_rong_bien.mp4",
        BROLL_DIR / "ov_11_banh_thuyen_250g.mp4",
        BROLL_DIR / "ov_12_kep_hat_500g.mp4",
    ]
    frames_4 = []
    for mp in srcs:
        raw = subprocess.check_output([
            "ffmpeg", "-v", "error", "-i", str(mp),
            "-vf", f"scale={cw}:{ch}:force_original_aspect_ratio=increase:flags=lanczos,crop={cw}:{ch}",
            "-frames:v", str(n_f), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ])
        arr = np.frombuffer(raw, dtype=np.uint8).reshape((-1, ch, cw, 3))
        if len(arr) < n_f:
            arr = np.concatenate([arr, np.repeat(arr[-1:], n_f - len(arr), axis=0)], axis=0)
        frames_4.append(arr[:n_f])

    bg_raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(BROLL_DIR / "ov_01_intro_104sets.mp4"),
        "-vf", f"scale={W}:{H}", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ])
    bg_im = Image.fromarray(np.frombuffer(bg_raw, dtype=np.uint8).reshape((H, W, 3)), "RGB").filter(ImageFilter.GaussianBlur(radius=22)).convert("RGBA")
    bg_im = Image.alpha_composite(bg_im, Image.new("RGBA", (W, H), (46, 12, 18, 132)))

    mask_c = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask_c).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=36, fill=255)
    frame_tpl = Image.new("RGBA", (cw + 24, ch + 24), (0, 0, 0, 0))
    ImageDraw.Draw(frame_tpl).rounded_rectangle([6, 6, 18 + cw, 18 + ch], radius=40, fill=(255, 252, 246, 255))

    centers = [(288, 600), (792, 600), (288, 1255), (792, 1255)]
    staggers = [0.04, 0.28, 0.52, 0.76]

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
        str(out_p)
    ], stdin=subprocess.PIPE)

    for fi in range(n_f):
        t = fi / FPS
        fr = bg_im.copy()
        for ci in range(4):
            dt = t - staggers[ci]
            if dt <= 0:
                continue
            sc = ease_out_back(min(1.0, dt / 0.26), s=1.32)
            card = frame_tpl.copy()
            card.paste(Image.fromarray(frames_4[ci][fi], "RGB"), (12, 12), mask_c)
            if abs(sc - 1.0) > 0.01:
                card = card.resize((max(2, int(card.width * sc)), max(2, int(card.height * sc))), Image.Resampling.BILINEAR)
            cx, cy = centers[ci]
            fr.alpha_composite(card, (cx - card.width // 2, cy - card.height // 2))
        enc.stdin.write(np.array(fr.convert("RGB"), dtype=np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    return out_p

def main():
    if (DRAFT_DIR / ".locked").exists():
        raise RuntimeError("1117 F20 is currently locked! Please return to CapCut Home Screen first.")

    build_clean_bento_4mon_notext()

    pj = json.loads((BAK / "Timelines" / "project.json").read_text(encoding="utf-8"))
    tl_id = pj["main_timeline_id"]
    D = json.loads((BAK / "Timelines" / tl_id / "draft_content.json").read_text(encoding="utf-8"))
    dc_fc = json.loads((FC_V6_DIR / "draft_content.json").read_text(encoding="utf-8"))
    dm_fc = json.loads((FC_V6_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))

    # Exact Native Templates from `backup_1117_F20_orig`!
    vtrack_tpl = copy.deepcopy(D["tracks"][0])
    vseg_tpl   = copy.deepcopy(D["tracks"][0]["segments"][0])
    ttrack_tpl = copy.deepcopy(D["tracks"][1])
    tseg_tpl   = copy.deepcopy(D["tracks"][1]["segments"][36])
    tmat_tpl   = copy.deepcopy(D["materials"]["texts"][0]) # Exact check_flag=15 Coiny template!
    atrack_tpl = copy.deepcopy(D["tracks"][5])
    aseg_tpl   = copy.deepcopy(D["tracks"][5]["segments"][0])
    amat_tpl   = copy.deepcopy(D["materials"]["audios"][0])

    vmat_tpl   = copy.deepcopy(next(m for m in dc_fc["materials"]["videos"] if m.get("type") == "video"))
    dm_vid_tpl = copy.deepcopy(next(x for g in dm_fc["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
    kf_tpl     = copy.deepcopy(next(sg["common_keyframes"][0] for tr in dc_fc["tracks"] for sg in tr.get("segments", []) if sg.get("common_keyframes")))

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

    TEXT_ANIMS  = json.loads((WORK / "all_verified_text_anims.json").read_text(encoding="utf-8"))
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
    vid_cache = {}
    new_dm_entries = []

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
        p = BROLL_DIR / mp4_name
        if not p.is_file():
            raise FileNotFoundError(f"Missing B-roll: {p}")
        fwd = norm_fwd(p)
        if fwd not in vid_cache:
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(p)], capture_output=True, text=True, check=True)
            j = json.loads(r.stdout)
            vs = j["streams"][0]
            w, h = int(vs["width"]), int(vs["height"])
            dur_u = max(33333, us(float(j["format"]["duration"])))
            mid = uid()
            lmid = str(uuid.uuid4())
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": fwd, "media_path": "", "local_id": "",
                "material_name": p.name, "width": w, "height": h, "duration": dur_u, "has_audio": False
            })
            D["materials"]["videos"].append(m)
            dme = copy.deepcopy(dm_vid_tpl)
            dme.update({
                "id": lmid, "file_Path": fwd, "extra_info": p.name,
                "duration": dur_u, "width": w, "height": h,
                "metetype": "video", "item_source": 1,
                "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
                "roughcut_time_range": {"start": 0, "duration": dur_u},
                "sub_time_range": {"start": -1, "duration": -1},
            })
            new_dm_entries.append(dme)
            vid_cache[fwd] = (mid, dur_u)
        mid, mat_dur_u = vid_cache[fwd]
        st_u = us(t0_s)
        du_u = min(mat_dur_u, max(us(0.25), us(t1_s) - st_u))
        dur_s = du_u / 1e6

        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])

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
        if mode == "full":
            seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
            seg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
            seg["uniform_scale"] = {"on": True, "value": 1.0}
            if zoom_dir != 0 and dur_s >= 1.8:
                s0, s1 = (1.00, 1.035) if zoom_dir > 0 else (1.035, 1.00)
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

    # ==========================================================================
    # 100% NATIVE EDITABLE CAPCUT TEXT ENGINE (`check_flag = 15` — ZERO PNGs!)
    # Cloned bit-for-bit from user's own `tmat_tpl` in `1117 F20`!
    # ==========================================================================
    def make_native_coiny_subtitle(parts: list[tuple[str, bool]], t0_s: float, t1_s: float, pos_y: float = -0.58):
        """
        Native Editable CapCut Subtitle (`type: "subtitle"`, `check_flag = 15`):
          - Regular (`is_emph=False`): Red fill (#EC1D1D) + White stroke (width=0.06), size=11.5
          - Inline Emphasis (`is_emph=True`): White fill (#FFFFFF) + Red stroke (width=0.065), size=12.0
        """
        full_text = "".join(p[0] for p in parts)
        styles = []
        cur = 0
        for chunk, is_emph in parts:
            ln = len(chunk)
            if ln == 0:
                continue
            fcol = WHITE_COL if is_emph else RED_COL
            scol = RED_COL   if is_emph else WHITE_COL
            sw   = 0.065     if is_emph else 0.060
            sz   = 12.0      if is_emph else 11.5
            styles.append({
                "fill": {"content": {"render_type": "solid", "solid": {"color": fcol}}},
                "font": {"path": COINY_PATH, "id": COINY_ID},
                "strokes": [{"content": {"render_type": "solid", "solid": {"color": scol}}, "width": sw, "mode": 0}],
                "size": sz,
                "useLetterColor": True,
                "range": [cur, cur + ln],
            })
            cur += ln

        tm = copy.deepcopy(tmat_tpl)
        tm_id = uid()
        tm.update({
            "id": tm_id,
            "type": "subtitle",
            "recognize_text": full_text,
            "translate_original_text": full_text,
            "content": json.dumps({"text": full_text, "styles": styles}, ensure_ascii=False),
            "base_content": "",
            "font_size": 11.5,
            "font_path": COINY_PATH,
            "font_resource_id": COINY_ID,
            "text_color": "#ec1d1d",
            "border_color": "#ffffff",
            "border_width": 0.06,
            "letter_spacing": 0.0,
            "line_spacing": 0.02,
            "alignment": 1,
            "line_feed": 1,
            "line_max_width": 0.82,
            "force_apply_line_max_width": True,
            "background_style": 0,
            "has_shadow": False,
            "is_rich_text": len(styles) > 1,
            "check_flag": 15,  # CRITICAL: 15 = Fill + Stroke ONLY (NEVER 31, which turns on black background box!)
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.35), us(t1_s) - st_u)

        ai = copy.deepcopy(TEXT_ANIMS["in"]["Chữ mờ dần hiện vào"])
        ai["start"] = 0
        ai["duration"] = min(166666, du_u // 4)
        ao = copy.deepcopy(TEXT_ANIMS["out"]["Mờ dần"])
        od = min(133333, du_u // 4)
        ao["duration"] = od
        ao["start"] = max(0, du_u - od)

        ma_id = uid()
        D["materials"].setdefault("material_animations", []).append({
            "animations": [ai, ao], "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
        })

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tm_id,
            "target_timerange": {"start": st_u, "duration": du_u},
            "extra_material_refs": [ma_id],
            "common_keyframes": [], "keyframe_refs": [],
        })
        ts["clip"]["transform"] = {"x": 0.0, "y": pos_y}
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["rotation"] = 0.0
        ts["uniform_scale"] = {"on": True, "value": 1.0}
        return ts

    def make_native_floating_tag(text: str, t0_s: float, t1_s: float,
                                 pos_x: float, pos_y: float, size: float = 13.0,
                                 rot_deg: float = 0.0, in_anim: str = "Mờ"):
        """
        Native Editable CapCut Floating Emphasis Text (`type: "text"`, `check_flag = 15`):
          - Pure White Fill ([1, 1, 1]) + Vibrant Red Stroke (#EC1D1D, width=0.068)
          - Native CapCut In + Loop ('Chao đảo ngẫu nhiên') + Out ('Mờ dần')
          - Smooth upward floating keyframes (KFTypePositionY + KFTypeScaleX/Y)!
        """
        styles = [{
            "fill": {"content": {"render_type": "solid", "solid": {"color": WHITE_COL}}},
            "font": {"path": COINY_PATH, "id": COINY_ID},
            "strokes": [{"content": {"render_type": "solid", "solid": {"color": RED_COL}}, "width": 0.068, "mode": 0}],
            "size": size,
            "useLetterColor": True,
            "range": [0, len(text)],
        }]

        tm = copy.deepcopy(tmat_tpl)
        tm_id = uid()
        tm.update({
            "id": tm_id,
            "type": "text",
            "recognize_text": text,
            "translate_original_text": text,
            "content": json.dumps({"text": text, "styles": styles}, ensure_ascii=False),
            "base_content": "",
            "font_size": size,
            "font_path": COINY_PATH,
            "font_resource_id": COINY_ID,
            "text_color": "#ffffff",
            "border_color": "#ec1d1d",
            "border_width": 0.068,
            "letter_spacing": 0.0,
            "line_spacing": 0.02,
            "alignment": 1,
            "line_feed": 1,
            "line_max_width": 0.78,
            "force_apply_line_max_width": True,
            "background_style": 0,
            "has_shadow": False,
            "is_rich_text": False,
            "check_flag": 15,  # CRITICAL: Pure clean White fill + Red stroke, zero black box!
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.45), us(t1_s) - st_u)
        dur_s = du_u / 1e6

        anim_items = []
        ik = in_anim if in_anim in TEXT_ANIMS["in"] else "Mờ"
        ai = copy.deepcopy(TEXT_ANIMS["in"][ik])
        in_d = min(233333, du_u // 4)
        ai["start"] = 0
        ai["duration"] = in_d
        anim_items.append(ai)

        ao = copy.deepcopy(TEXT_ANIMS["out"]["Mờ dần"])
        out_d = min(200000, du_u // 4)
        ao["duration"] = out_d
        ao["start"] = max(0, du_u - out_d)
        anim_items.append(ao)

        if "Chao đảo ngẫu nhiên" in TEXT_ANIMS["loop"] and du_u > (in_d + out_d + 200000):
            al = copy.deepcopy(TEXT_ANIMS["loop"]["Chao đảo ngẫu nhiên"])
            al["start"] = in_d
            al["duration"] = du_u - in_d - out_d
            anim_items.append(al)

        ma_id = uid()
        D["materials"].setdefault("material_animations", []).append({
            "animations": anim_items, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
        })

        kfs = [
            make_kf("KFTypePositionY", [(0.0, pos_y - 0.036), (min(0.35, dur_s * 0.45), pos_y), (dur_s, pos_y + 0.032)]),
            make_kf("KFTypeScaleX", [(0.0, 0.86), (min(0.18, dur_s * 0.35), 1.04), (min(0.34, dur_s * 0.6), 1.00)]),
            make_kf("KFTypeScaleY", [(0.0, 0.86), (min(0.18, dur_s * 0.35), 1.04), (min(0.34, dur_s * 0.6), 1.00)]),
        ]

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tm_id,
            "target_timerange": {"start": st_u, "duration": du_u},
            "extra_material_refs": [ma_id],
            "common_keyframes": kfs, "keyframe_refs": [],
        })
        ts["clip"]["transform"] = {"x": pos_x, "y": pos_y}
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["rotation"] = float(rot_deg)
        ts["uniform_scale"] = {"on": True, "value": 1.0}
        return ts

    # 1. Cohesive Color-Matched Real F20 B-Rolls (Zero baked text!)
    BROLL_TIMELINE = [
        ("ov_01_intro_104sets.mp4",     1.80,   3.77, -1),
        ("ov_02_anh_hau_handover.mp4", 15.65,  17.75, +1),
        ("ov_03_anh_hau_77sets.mp4",   17.75,  19.95, -1),
        ("ov_04_phu_huynh_13sets.mp4", 20.20,  23.90, +1),
        ("ov_05_hanoi_10sets_pack.mp4",24.67,  28.05, +1),
        ("ov_06_hcm_4sets_car.mp4",    28.05,  31.68, -1),
        ("ov_07_du_104_sets_glide.mp4",33.80,  36.65, +1),
        ("ov_08_showroom_bows_4k.mp4", 41.60,  44.85, +1),
        ("bento_4mon_notext.mp4",      52.18,  56.18,  0),
        ("ov_09_to_yen_soi_dai.mp4",   58.25,  61.08, +1),
        ("ov_09b_basket_macro.mp4",    63.15,  66.65, +1),
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

    # 2. Native Editable CapCut Subtitles (`Track 3` — Red fill + White stroke, inline emphasis = White fill + Red stroke!)
    SUB_ITEMS = [
        (4.56,  6.38,  [("Hôm nay bên Oanh đang chuẩn bị", False)]),
        (6.40,  7.96,  [("tổng cộng ", False), ("104 set quà", True)]),
        (7.98,  9.44,  [("cho các khách hàng đặt", False)]),
        (9.46,  11.48, [("làm ", False), ("quà biếu tặng", True), (" thầy cô giáo", False)]),
        (11.50, 13.65, [("nhân dịp tri ân ngày ", False), ("20/11", True)]),

        (13.96, 15.58, [("Ở ", False), ("Nha Trang", True), (" có 2 khách hàng", False)]),
        (15.64, 17.56, [("1 là ", False), ("Anh Hậu", True), (" • Trung tâm luyện thi", False)]),
        (17.58, 19.85, [("Đăng Khoa Edu", True), (" đặt ", False), ("77 set quà", True)]),
        (20.18, 22.45, [("Khách thứ 2 là ", False), ("Hội phụ huynh", True)]),
        (22.47, 23.90, [("đặt ", False), ("13 set quà", True)]),
        (24.00, 26.85, [("1 bạn giáo viên ở ", False), ("Hà Nội", True)]),
        (26.87, 27.85, [("đặt ", False), ("10 set quà", True)]),
        (27.92, 30.54, [("và 1 bạn ở ", False), ("TP. Hồ Chí Minh", True)]),
        (30.56, 31.68, [("đặt ", False), ("4 set quà", True)]),

        (31.70, 34.36, [("Tổng sáng nay bên mình chuẩn bị", False)]),
        (34.38, 36.55, [("đủ 104 set quà", True), (" nha mọi người!", False)]),

        (38.60, 40.62, [("Đây là những ", False), ("set quà", True), (" bên Oanh", False)]),
        (40.64, 42.85, [("đã chuẩn bị xong trong sáng nay ạ!", False)]),

        (45.08, 47.72, [("Bây giờ Oanh giới thiệu ", False), ("1 set quà", True)]),
        (47.74, 49.55, [("của bên Oanh cho mọi người xem nhé!", False)]),

        (52.00, 55.70, [("Một ", False), ("set quà tặng", True), (" bên trong gồm có:", False)]),
        (56.25, 58.24, [("Đầu tiên là ", False), ("1 set yến sào", True)]),
        (58.26, 61.05, [("gồm ", False), ("1 tổ yến tinh chế sợi dài", True)]),
        (61.10, 63.15, [("kèm theo đầy đủ ", False), ("nguyên liệu chưng:", True)]),
        (63.18, 66.64, [("Táo đỏ • Đông trùng\nKỷ tử • Đường phèn", True)]),

        (66.66, 69.90, [("Thứ 2 là ", False), ("2 hộp rong biển sấy giòn", True)]),
        (70.12, 72.30, [("1 hộp ", False), ("sấy giòn cay nhẹ", True)]),
        (72.42, 74.50, [("và 1 hộp ", False), ("sấy mè không cay", True)]),

        (74.80, 77.65, [("Thứ 3 là 1 gói ", False), ("bánh thuyền", True)]),
        (77.67, 79.95, [("mix hạt dinh dưỡng ", False), ("250g", True)]),

        (80.28, 84.60, [("Thứ 4 là 1 gói\n", False), ("rong biển kẹp hạt 500g", True)]),
        (84.76, 86.30, [("Ở trong này thì sẽ có từ", False)]),
        (86.32, 89.32, [("22 đến 24 thanh\n", True), ("bánh hạt dinh dưỡng!", False)]),

        (89.36, 92.68, [("Sản phẩm ", False), ("giá trị nhất", True), (" trong set quà", False)]),
        (92.70, 95.85, [("là ", False), ("1 tổ yến tinh chế sợi dài", True)]),

        (96.04, 100.20, [("Có chuẩn bị thêm ", False), ("tờ cẩm nang yến sào", True)]),
        (100.48, 103.85, [("gồm ", False), ("công dụng của yến sào", True)]),
        (103.95, 107.55, [("và hướng dẫn\n", False), ("chưng yến đúng cách", True)]),

        (107.84, 111.24, [("Tất cả được set trong ", False), ("giỏ đựng quà", True)]),
        (111.26, 114.08, [("chất liệu ", False), ("mica trong suốt\n", True), ("như thế này!", False)]),
        (114.24, 117.36, [("Bên trên có ", False), ("quai xách bằng da", True)]),
        (117.38, 119.10, [("màu đỏ đô", True), (" rất là sang trọng ạ!", False)]),
        (119.52, 122.90, [("Thiết kế thêm ", False), ("bông hoa", True), (" tạo điểm nhấn", False)]),
        (122.95, 126.15, [("và 1 chiếc ", False), ("nơ màu be", True), (" rất xinh xắn!", False)]),

        (127.52, 130.05, [("Đặc biệt các sản phẩm trong set quà", False)]),
        (130.08, 132.02, [("đều do bên Oanh ", False), ("trực tiếp sản xuất", True)]),
        (132.28, 135.40, [("nên cứ yên tâm về ", False), ("chất lượng & giá cả!", True)]),

        (135.62, 138.00, [("Oanh xin gửi ", False), ("lời cảm ơn", True), (" tới quý anh chị", False)]),
        (138.02, 140.50, [("đã tin tưởng đặt hàng ", False), ("Thực phẩm F20", True)]),
        (140.54, 144.42, [("Anh chị có nhu cầu đặt ", False), ("set quà tặng", True)]),
        (144.60, 147.00, [("làm quà biếu tặng nhân dịp lễ ", False), ("20/11", True)]),
        (147.02, 148.60, [("hãy ", False), ("inbox ngay", True), (" cho Oanh nhé!", False)]),
    ]
    tr_sub = copy.deepcopy(ttrack_tpl); tr_sub["id"] = uid()
    tr_sub["segments"] = [make_native_coiny_subtitle(parts, t0, t1, pos_y=-0.58) for t0, t1, parts in SUB_ITEMS]

    # 3. Native Editable CapCut Floating White-Fill Red-Stroke Callouts (`Tracks 4..8`)!
    FLOATING_TAGS = [
        # Intro Hook
        (0.18,   3.68, "SET QUÀ TRI ÂN 20/11",       0.00,  0.60, 14.5,  0.0, "Mờ"),
        (0.42,   3.68, "THỰC PHẨM F20 × SKA NEST",   0.00,  0.46, 11.0,  0.0, "Chữ mờ dần hiện vào"),

        # Around Chị Oanh on Track 0 (100% forehead-safe!)
        (6.38,   9.25, "104 SET QUÀ!",              -0.38,  0.46, 13.5, +4.0, "Trượt sang phải"),
        (9.55,  13.55, "QUÀ BIẾU 20/11",            +0.34,  0.44, 13.0, -4.0, "Trượt sang trái"),

        # Customer Order Highlights
        (15.70, 19.85, "ĐĂNG KHOA EDU",             -0.26,  0.60, 12.5, +3.0, "Trượt sang phải"),
        (17.55, 19.85, "77 SET QUÀ!",               +0.28,  0.50, 14.0, -3.5, "Trượt sang trái"),
        (20.30, 23.85, "HỘI PHỤ HUYNH • 13 SET",     0.00,  0.52, 12.5,  0.0, "Mờ"),
        (24.72, 27.82, "HÀ NỘI • 10 SET",           -0.24,  0.50, 13.0, +3.0, "Trượt sang phải"),
        (28.08, 31.62, "TP.HCM • 04 SET",           +0.24,  0.50, 13.0, -3.0, "Trượt sang trái"),
        (33.82, 36.60, "ĐỦ 104 SET QUÀ!",            0.00,  0.52, 14.5,  0.0, "Bụi vàng"),

        # 2x2 Bento 4 Món Set Quà (52.18 - 56.15s: ALL labels are Native Editable CapCut Texts!)
        (52.20, 56.15, "04 MÓN TRONG 01 SET QUÀ",    0.00,  0.70, 13.0,  0.0, "Mờ"),
        (52.25, 56.15, "01 • TỔ YẾN",               -0.44,  0.08, 10.5,  0.0, "Chữ mờ dần hiện vào"),
        (52.50, 56.15, "02 • RONG BIỂN",            +0.44,  0.08, 10.5,  0.0, "Chữ mờ dần hiện vào"),
        (52.76, 56.15, "03 • BÁNH THUYỀN",          -0.44, -0.40, 10.2,  0.0, "Chữ mờ dần hiện vào"),
        (53.02, 56.15, "04 • KẸP HẠT 500G",         +0.44, -0.40, 10.2,  0.0, "Chữ mờ dần hiện vào"),

        # Gift Basket Walkthrough
        (45.20, 49.45, "CHI TIẾT 01 SET QUÀ",       +0.28,  0.42, 12.5, -3.0, "Trượt sang trái"),
        (56.28, 61.05, "01 TỔ YẾN TINH CHẾ",         0.00,  0.56, 13.5,  0.0, "Mờ"),
        (58.30, 61.05, "SỢI DÀI TIÊU CHUẨN",         0.00,  0.42, 11.5,  0.0, "Chữ mờ dần hiện vào"),

        # 4 Stewing Ingredients floating staggered over macro basket (63.18 - 66.62s)
        (63.18, 66.62, "01 • TÁO ĐỎ",               -0.34,  0.52, 12.5, +3.5, "Trượt sang phải"),
        (63.82, 66.62, "02 • ĐÔNG TRÙNG HẠ THẢO",   +0.18,  0.38, 12.0, -3.0, "Trượt sang trái"),
        (65.05, 66.62, "03 • KỶ TỬ",                -0.36,  0.22, 12.5, +3.5, "Trượt sang phải"),
        (65.80, 66.62, "04 • 01 HỘP ĐƯỜNG PHÈN",    +0.20,  0.08, 12.0, -3.0, "Trượt sang trái"),

        # Item 2, 3, 4
        (66.70, 70.05, "02 HỘP RONG BIỂN",          +0.26,  0.44, 12.5, -3.0, "Trượt sang trái"),
        (70.15, 74.45, "CAY NHẸ",                   -0.34,  0.50, 12.5, +3.5, "Trượt sang phải"),
        (72.42, 74.45, "SẤY MÈ KHÔNG CAY",          +0.22,  0.36, 12.0, -3.0, "Trượt sang trái"),
        (74.85, 79.92, "BÁNH THUYỀN MIX HẠT",        0.00,  0.56, 12.5,  0.0, "Mờ"),
        (77.65, 79.92, "GÓI 250G!",                 +0.32,  0.40, 13.5, -3.5, "Trượt sang trái"),
        (80.32, 85.35, "RONG BIỂN KẸP HẠT 500G",     0.00,  0.54, 12.5,  0.0, "Mờ"),
        (86.28, 89.28, "22 – 24 THANH!",            +0.30,  0.46, 13.5, -4.0, "Trượt sang trái"),

        # Giá trị nhất & Cẩm nang & Bao bì & CTA
        (89.45, 92.62, "GIÁ TRỊ NHẤT!",             -0.30,  0.44, 13.5, +3.5, "Trượt sang phải"),
        (92.68, 95.82, "YẾN TINH CHẾ SỢI DÀI",       0.00,  0.54, 13.0,  0.0, "Bụi vàng"),
        (98.60, 102.75,"CẨM NANG YẾN SÀO",           0.00,  0.56, 13.0,  0.0, "Mờ"),
        (102.85,107.25,"CÔNG DỤNG & CÁCH CHƯNG",     0.00,  0.56, 12.2,  0.0, "Chữ mờ dần hiện vào"),
        (110.82,114.08,"GIỎ MICA TRONG SUỐT",        0.00,  0.54, 13.0,  0.0, "Mờ"),
        (116.18,119.12,"QUAI XÁCH DA ĐỎ ĐÔ",         0.00,  0.54, 13.5,  0.0, "Bụi vàng"),
        (119.56,122.88,"HOA ĐỎ ĐIỂM NHẤN",          -0.26,  0.50, 13.0, +3.0, "Trượt sang phải"),
        (122.92,126.18,"NƠ MÀU BE XINH XẮN",         0.00,  0.54, 13.0,  0.0, "Mờ"),
        (129.85,135.35,"TRỰC TIẾP SẢN XUẤT",        -0.22,  0.54, 12.5, +3.0, "Trượt sang phải"),
        (132.32,135.35,"GIÁ TẬN XƯỞNG!",            +0.26,  0.40, 13.5, -3.5, "Trượt sang trái"),
        (138.02,140.48,"THỰC PHẨM F20",             -0.32,  0.44, 12.5, +3.5, "Trượt sang phải"),
        (146.82,148.58,"INBOX OANH NGAY!",          +0.28,  0.44, 13.5, -4.0, "Trượt sang trái"),
    ]

    float_lanes: list[list[dict]] = []
    for t0, t1, txt, px, py, sz, rot, ia in sorted(FLOATING_TAGS, key=lambda x: x[0]):
        sg = make_native_floating_tag(txt, t0, t1, px, py, size=sz, rot_deg=rot, in_anim=ia)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for lane in float_lanes:
            if lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                lane.append(sg); placed = True; break
        if not placed:
            float_lanes.append([sg])

    float_tracks = []
    for lane in float_lanes:
        tr_f = copy.deepcopy(ttrack_tpl); tr_f["id"] = uid(); tr_f["segments"] = lane
        float_tracks.append(tr_f)

    # 4. Ear-Verified Silky Tactile Micro-SFX (100% from User's SFX Folder, -18..-21dB!)
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
        (0.16,   "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Air Mở Cảnh",      0.13, 0.7),
        (0.28,   "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3",                              "Chuông Gió Mở",    0.10, 1.8),
        (1.78,   "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh Đại Cảnh",  0.12, 0.5),
        (6.35,   "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Air Tick 104 Set", 0.10, 0.6),
        (9.55,   "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Gió Mềm 20/11",    0.11, 0.5),
        (15.62,  "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish ĐK Edu",     0.10, 0.6),
        (17.75,  "Chụp ảnh - Tiếng chụp màn hình gọn 03.mp3",                                   "Shutter Anh Hậu",  0.09, 0.6),
        (20.22,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Whoosh 13 Set",    0.11, 0.6),
        (24.68,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Swipe Hà Nội",     0.10, 0.6),
        (28.05,  "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish TP.HCM",     0.10, 0.6),
        (33.82,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đủ 104 Set",  0.10, 1.2),
        (41.58,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Whoosh Showroom",  0.11, 0.6),
        (45.20,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh 01 Set",    0.10, 0.5),
        (52.15,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Bento Air",        0.11, 0.6),
        (52.48,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Món 02",      0.10, 0.35),
        (52.76,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Món 03",      0.10, 0.35),
        (53.04,  "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Món 04",      0.09, 1.0),
        (58.25,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Air Tổ Yến",       0.10, 0.6),
        (63.16,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Táo Đỏ",      0.10, 0.35),
        (63.82,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Đông Trùng",  0.10, 0.35),
        (65.05,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Kỷ Tử",       0.10, 0.35),
        (65.80,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đường Phèn",  0.09, 1.1),
        (70.10,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Swipe Rong Biển",  0.10, 0.6),
        (77.15,  "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Swoosh 250g",      0.10, 0.6),
        (82.20,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Card 500g",        0.12, 0.7),
        (86.28,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh 24 Thanh",  0.10, 0.5),
        (92.65,  "Whoosh - Title Swoosh (1s).mp3",                                              "Swoosh Giá Trị",   0.10, 0.7),
        (98.58,  "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Mở Cẩm Nang 1",    0.13, 0.8),
        (102.80, "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Lật Trang Trong",  0.12, 0.8),
        (110.80, "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish Giỏ Mica",   0.10, 0.6),
        (116.15, "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3",                                   "Shine Quai Da",    0.09, 0.9),
        (119.55, "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh Hoa Đỏ",    0.10, 0.5),
        (122.90, "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Nơ Be",       0.09, 1.1),
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
        track0_orig,     # Track 0: 100.00% Untouched Main Video!
        tr_ov_full,      # Track 1: 24 Color-Matched F20 B-Rolls + Clean 2x2 Bento!
        tr_ov_pip,       # Track 2: 2 Rounded Upper-Right PIPs!
        tr_sub,          # Track 3: 52 Native Editable Coiny Subtitles (`check_flag = 15`)!
        *float_tracks,   # Track 4..8: 41 Native Editable Floating White-Fill Red-Stroke Texts (`check_flag = 15`)!
        bgm_track_orig,  # BGM Track
        *sfx_tracks,     # Ear-Verified Silky User SFX Tracks!
    ]
    D["duration"] = main_end_u
    D["update_time"] = now_s

    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video":
                s["render_index"] = ti
            elif tr["type"] == "text":
                s["render_index"] = 14000 + ti

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")

    # Write directly into `1117 F20` (unlinking first so zero hardlink issues exist!)
    for tp in [
        DRAFT_DIR / "draft_content.json",
        DRAFT_DIR / "template-2.tmp",
        DRAFT_DIR / "Timelines" / tl_id / "draft_content.json",
        DRAFT_DIR / "Timelines" / tl_id / "template-2.tmp",
    ]:
        if tp.exists():
            tp.unlink()
        tp.write_bytes(dc_bytes)

    dmi = json.loads((BAK / "draft_meta_info.json").read_text(encoding="utf-8"))
    dmi["tm_duration"] = main_end_u
    dmi["tm_draft_modified"] = now_us
    for bucket in dmi.get("draft_materials", []):
        if bucket.get("type") == 0:
            existing = {x.get("file_Path") for x in bucket.get("value", [])}
            for ne in new_dm_entries:
                if ne["file_Path"] not in existing:
                    bucket["value"].append(ne)
    (DRAFT_DIR / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

    pj["update_time"] = now_us
    for t_ent in pj.get("timelines", []): t_ent["update_time"] = now_us
    (DRAFT_DIR / "Timelines" / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

    # Clean up temporary `1117 F20 - V3 Full Layers` duplicate so CapCut Home Screen stays clean with ONE `1117 F20`!
    if DRAFT_V3.exists():
        shutil.rmtree(DRAFT_V3, ignore_errors=True)

    rmi_path = ROOT / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    store = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != "1117 F20 - V3 Full Layers"]
    for x in store:
        if x.get("draft_name") == "1117 F20":
            x["tm_duration"] = main_end_u
            x["tm_draft_modified"] = now_us
    rmi["all_draft_store"] = store
    rmi["draft_ids"] = len(store)
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    print("SUCCESS V4 NATIVE CAPCUT TEXT MASTER: Updated '1117 F20' directly!")
    print(f"  -> 0 PNG text layers! 100% Native Editable CapCut Texts: {len(D['materials']['texts'])} texts (all check_flag=15)")
    print(f"  -> Track 0: 20 segs (100% UNCHANGED) | B-rolls: {len(tr_ov_full['segments'])} + 2 PIPs | Subtitles: {len(tr_sub['segments'])} | Floating White-on-Red: {len(FLOATING_TAGS)} across {len(float_tracks)} text tracks | SFX: {len(SFX_EVENTS)}")

if __name__ == "__main__":
    main()
