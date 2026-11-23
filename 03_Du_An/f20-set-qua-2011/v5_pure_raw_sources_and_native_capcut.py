import copy, json, os, shutil, subprocess, time, uuid
from pathlib import Path

W, H = 1080, 1920
FPS = 30.0

ROOT       = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_DIR  = ROOT / "1117 F20"
HTPM_DIR   = ROOT / "HTPM"
FC_V6_DIR  = ROOT / "FEEL_CHICKEN_2011_Full_Layers_V6"

F20_261116 = Path(r"Z:\Máy tính khác\My Computer\F20\video gốc\261116")
DOC_DIR    = F20_261116 / r"Chi Oanh\dọc"
NGANG_DIR  = F20_261116 / r"Chi Oanh\ngang"
DJI_DIR    = F20_261116 / r"Chi Oanh\dji"
ANH_HAU    = F20_261116 / r"Anh Hậu"

SFX_FOLDER = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")
WORK       = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
BAK        = WORK / "backup_1117_F20_orig"

COINY_ID   = "7482665772876156165"
COINY_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7482665772876156165/57619fa23667c87dee08a75d49a8b51a/font.ttf"

RED_COL    = [0.9254902005195618, 0.11372549086809158, 0.11372549086809158]  # #EC1D1D
WHITE_COL  = [1.0, 1.0, 1.0]                                                  # #FFFFFF

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


def main():
    if not DRAFT_DIR.exists():
        raise FileNotFoundError(f"Missing CapCut project: {DRAFT_DIR}")
    if (DRAFT_DIR / ".locked").exists():
        raise RuntimeError("1117 F20 currently has .locked! Please return to CapCut Home Screen first.")

    pj = json.loads((BAK / "Timelines" / "project.json").read_text(encoding="utf-8"))
    tl_id = pj["main_timeline_id"]
    D = json.loads((BAK / "Timelines" / tl_id / "draft_content.json").read_text(encoding="utf-8"))

    dc_htpm = json.loads((HTPM_DIR / "draft_content.json").read_text(encoding="utf-8"))
    dm_htpm = json.loads((HTPM_DIR / "draft_meta_info.json").read_text(encoding="utf-8"))
    dc_fc   = json.loads((FC_V6_DIR / "draft_content.json").read_text(encoding="utf-8"))

    # Native templates cloned directly from user's own CapCut projects
    vtrack_tpl = copy.deepcopy(D["tracks"][0])
    vseg_tpl   = copy.deepcopy(D["tracks"][0]["segments"][0])
    vmat_tpl   = copy.deepcopy(dc_htpm["materials"]["videos"][0])
    dm_mat_tpl = copy.deepcopy(dm_htpm["draft_materials"][0]["value"][0])
    kf_tpl     = copy.deepcopy(next(sg["common_keyframes"][0] for tr in dc_fc["tracks"] for sg in tr.get("segments", []) if sg.get("common_keyframes")))

    ttrack_tpl = copy.deepcopy(D["tracks"][1])
    tseg_tpl   = copy.deepcopy(D["tracks"][1]["segments"][36])
    tmat_tpl   = copy.deepcopy(D["materials"]["texts"][0])  # Exact check_flag=15 Coiny template

    atrack_tpl = copy.deepcopy(D["tracks"][5])
    aseg_tpl   = copy.deepcopy(D["tracks"][5]["segments"][0])
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

    TEXT_ANIMS    = json.loads((WORK / "all_verified_text_anims.json").read_text(encoding="utf-8"))
    VIDEO_ANIMS   = json.loads((WORK / "verified_video_anims.json").read_text(encoding="utf-8"))
    COLOR_SLIDERS = json.loads((WORK / "native_color_sliders.json").read_text(encoding="utf-8"))
    RECT_MASK_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef"

    # Keep ONLY Track 0 (100% untouched) + BGM Track
    track0_orig    = copy.deepcopy(D["tracks"][0])
    bgm_track_orig = copy.deepcopy(D["tracks"][6])
    main_end_u     = max(s["target_timerange"]["start"] + s["target_timerange"]["duration"] for s in track0_orig["segments"])

    bgm_seg = bgm_track_orig["segments"][0]
    bgm_seg["target_timerange"]["duration"] = main_end_u
    bgm_seg["source_timerange"]["duration"] = main_end_u
    bgm_seg["volume"] = 0.18
    bgm_seg["last_nonzero_volume"] = 0.18
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
    vmat_map = {}
    new_dm_entries = []

    def get_or_add_raw_video(src_path: Path):
        if not src_path.is_file():
            raise FileNotFoundError(f"Missing original F20 video source: {src_path}")
        fwd = norm_fwd(src_path)
        assert fwd.startswith("Z:/Máy tính khác/My Computer/F20/"), f"Non-raw source forbidden: {fwd}"
        if fwd in vmat_map:
            return vmat_map[fwd]
        w, h, dur_s, has_aud = probe_media(src_path)
        dur_u = max(33333, us(dur_s))
        mid = uid()
        lmid = str(uuid.uuid4())
        m = copy.deepcopy(vmat_tpl)
        m.update({
            "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
            "type": "video", "path": fwd, "media_path": "", "local_id": "",
            "material_name": src_path.name, "width": w, "height": h, "duration": dur_u, "has_audio": bool(has_aud)
        })
        D["materials"]["videos"].append(m)

        dme = copy.deepcopy(dm_mat_tpl)
        dme.update({
            "id": lmid, "file_Path": fwd, "extra_info": src_path.name,
            "duration": dur_u, "width": w, "height": h,
            "metetype": "video", "item_source": 1,
            "create_time": now_s, "import_time": now_s, "import_time_ms": now_us,
            "roughcut_time_range": {"start": 0, "duration": dur_u},
            "sub_time_range": {"start": -1, "duration": -1},
        })
        new_dm_entries.append(dme)
        vmat_map[fwd] = (mid, dur_u, w, h)
        return mid, dur_u, w, h

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

    def attach_dji_color_sliders(refs: list[str]):
        """
        Attaches CapCut's native editable Color Adjustment sliders ('Tùy chỉnh')
        so flat DJI clips match warm Sony Track 0 AND user can edit sliders freely in CapCut!
        """
        attach_color_sliders(refs, [
            ("temperature", 0.15),  # Warm up cool D-Log to match Sony showroom warmth
            ("saturation",  0.20),  # Natural vibrancy (never oversaturated)
            ("contrast",    0.10),  # Clean shadow/midtone contrast
            ("brightness",  0.04),  # Subtle lift
        ])

    def make_raw_overlay_seg(
        src_path: Path, t0_s: float, t1_s: float, src_in_s: float, spd: float = 1.0,
        in_anim: str | None = None, out_anim: str | None = None,
        zoom_dir: int = 0, base_scale: float = 1.0, tx: float = 0.0, ty: float = 0.0,
        mask_cfg: dict | None = None, is_dji: bool = False, custom_sliders: list[tuple[str, float]] | None = None
    ):
        mid, mat_dur_u, w, h = get_or_add_raw_video(src_path)
        tgt_st_u = us(t0_s)
        tgt_du_u = max(us(0.25), us(t1_s) - tgt_st_u)
        src_st_u = us(src_in_s)
        src_du_u = us((tgt_du_u / 1e6) * spd)
        if src_st_u + src_du_u > mat_dur_u:
            src_st_u = max(0, mat_dur_u - src_du_u)
        dur_s = tgt_du_u / 1e6

        # Auto-compute cover scale for horizontal 16:9 4K sources when used full-screen on 9:16 canvas
        eff_scale = base_scale
        if mask_cfg is None and w > h:
            fit_h = 1080.0 * (h / w)
            cover_mult = (1920.0 / fit_h) * 1.015
            eff_scale = round(base_scale * cover_mult, 4)

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
            attach_dji_color_sliders(refs)
        if custom_sliders:
            attach_color_sliders(refs, custom_sliders)

        # Selective animations ONLY when explicitly requested!
        anim_list = []
        if in_anim and in_anim in VIDEO_ANIMS["in"]:
            ai = copy.deepcopy(VIDEO_ANIMS["in"][in_anim])
            ai["start"] = 0
            ai["duration"] = min(233333 if mask_cfg is None else 266666, tgt_du_u // 3)
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
        if zoom_dir != 0 and mask_cfg is None and dur_s >= 2.6:
            s0, s1 = (eff_scale, round(eff_scale * 1.032, 4)) if zoom_dir > 0 else (round(eff_scale * 1.032, 4), eff_scale)
            kfs = [
                make_kf("KFTypeScaleX", [(0.0, s0), (dur_s, s1)]),
                make_kf("KFTypeScaleY", [(0.0, s0), (dur_s, s1)]),
            ]

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": src_st_u, "duration": src_du_u},
            "target_timerange": {"start": tgt_st_u, "duration": tgt_du_u},
            "speed": round(spd, 3), "volume": 0.0, "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [],
        })
        return seg

    # ==========================================================================
    # 1. TRACK 1 — 24 FULL-SCREEN RAW CAMERA OVERLAYS (Hard-Cut First!)
    #    - 21/24 clips use clean Hard Cuts (in_anim=None, out_anim=None) — zero Track 0 flash!
    #    - Only 3 boundary moments (1.85s intro, 33.80s end of Act 1, 143.60s outro beauty) use gentle fade!
    # ==========================================================================
    FULL_RAW_OVERLAYS = [
        # (src_path, t0_s, t1_s, src_in_s, spd, in_anim, out_anim, zoom_dir, base_scale, tx, ty, is_dji)
        # Opening Hook: showroom gift sets -> hard cut cleanly to Chị Oanh at 3.77s
        (DOC_DIR / "C3875.MP4",                        1.85,   3.77,  0.60, 1.00, "Rõ dần", None,     -1, 1.00,  0.00,  0.00, False),

        # Nha Trang Orders: Đăng Khoa Edu 77 sets (2-shot sequence -> 100% crisp Hard Cuts!)
        (ANH_HAU / "C3920.MP4",                       15.65,  17.75,  4.60, 1.00, None,     None,      0, 1.00,  0.00,  0.00, False),
        (ANH_HAU / "C3928.MP4",                       17.75,  19.95,  1.20, 1.00, None,     None,      0, 1.00,  0.00,  0.00, False),

        # Hội Phụ Huynh 13 sets + Hà Nội 10 sets + TP.HCM 4 sets (crisp Hard Cuts!)
        (DOC_DIR / "C3882.MP4",                       20.20,  23.90,  0.60, 1.00, None,     None,     +1, 1.00,  0.00,  0.00, False),
        (DOC_DIR / "C3887.MP4",                       24.67,  28.05,  0.50, 1.00, None,     None,      0, 1.00,  0.00,  0.00, False),
        (DOC_DIR / "C3901.MP4",                       28.05,  31.68,  0.50, 1.00, None,     None,      0, 1.00,  0.00,  0.00, False),

        # Climax of Act 1 ("Đủ 104 set quà nha mọi người!") -> soft dissolve out to Act 2
        (DOC_DIR / "C3869.MP4",                       33.80,  36.65,  1.40, 1.00, None,     "Mờ dần", +1, 1.00,  0.00,  0.00, False),

        # Showroom prepared gift sets 4K macro glide
        (NGANG_DIR / "DJI_20261116095310_0100_D.MP4", 41.60,  44.85,  0.40, 0.90, None,     None,     +1, 1.00,  0.00,  0.00, True),

        # Backdrop for 4-cell Raw 2x2 Bento Grid ("Một set quà tặng bên trong gồm có:")
        (DOC_DIR / "C3875.MP4",                       52.18,  56.18,  3.00, 0.80, None,     None,      0, 1.06,  0.00,  0.00, False),

        # Item 1: 1 Tổ yến tinh chế sợi dài + 4 Nguyên liệu chưng macro inside basket
        (DJI_DIR / "DJI_20261116093322_0084_D.MP4",   58.25,  61.08, 14.20, 1.00, None,     None,      0, 1.54, -0.30, -0.05, True),
        (DOC_DIR / "C3873.MP4",                       63.15,  66.65,  0.20, 0.74, None,     None,     +1, 1.04,  0.00,  0.00, False),

        # Item 2, 3, 4: Multi-cam synced close-ups on hands + products (steady Hard Cuts!)
        (DJI_DIR / "DJI_20261116093322_0084_D.MP4",   70.10,  74.48, 33.80, 1.05, None,     None,      0, 1.56, -0.32, -0.06, True),
        (DJI_DIR / "DJI_20261116093322_0084_D.MP4",   77.15,  79.95, 43.67, 1.05, None,     None,      0, 1.56, -0.32, -0.06, True),
        (DJI_DIR / "DJI_20261116093322_0084_D.MP4",   82.20,  85.40, 49.29, 1.05, None,     None,      0, 1.56, -0.32, -0.06, True),

        # Giá trị nhất trong set quà: 1 Tổ yến tinh chế sợi dài (distinct Sony macro shot!)
        (DOC_DIR / "C3867.MP4",                       92.65,  95.85,  0.35, 0.82, None,     None,     +1, 1.00,  0.00,  0.00, False),

        # Tờ cẩm nang yến sào: synced opening -> lifted centered macro of open pages (lifted cleanly above subtitle!)
        (DJI_DIR / "DJI_20261116093955_0088_D.MP4",   98.60, 102.80, 13.04, 1.05, None,     None,      0, 1.00,  0.00,  0.00, True),
        (DJI_DIR / "DJI_20261116093826_0087_D.MP4",  102.80, 107.30, 16.50, 0.95, None,     None,     +1, 1.34, -0.14, +0.28, True),

        # 4 Packaging Details: Giỏ mica -> Quai da đỏ đô -> Bông hoa -> Nơ màu be (crisp Hard Cuts!)
        (DJI_DIR / "DJI_20261116093624_0085_D.MP4",  110.80, 114.10, 12.20, 0.90, None,     None,     +1, 1.00,  0.00,  0.00, True),
        (NGANG_DIR / "DJI_20261116095317_0101_D.MP4",116.15, 119.15,  4.60, 0.80, None,     None,      0, 1.02,  0.00,  0.00, True),
        (DOC_DIR / "C3873.MP4",                      119.55, 122.90,  1.80, 0.80, None,     None,     +1, 1.04,  0.00,  0.00, False),
        (NGANG_DIR / "DJI_20261116095310_0100_D.MP4",122.90, 126.20,  0.50, 0.80, None,     None,     +1, 1.00,  0.00,  0.00, True),

        # Trực tiếp sản xuất — Chất lượng & Giá cả (2-shot F20 team sequence -> Hard Cuts!)
        (DOC_DIR / "C3870.MP4",                      129.80, 132.60,  1.00, 1.00, None,     None,      0, 1.00,  0.00,  0.00, False),
        (DOC_DIR / "C3866.MP4",                      132.60, 135.40,  2.50, 1.00, None,     None,      0, 1.00,  0.00,  0.00, False),

        # Closing Gift Set Beauty Shot -> gentle fade back to Chị Oanh's closing CTA
        (DOC_DIR / "C3873.MP4",                      143.60, 146.75,  1.10, 0.85, "Rõ dần", "Mờ dần", +1, 1.00,  0.00,  0.00, False),
    ]

    tr_ov_full = copy.deepcopy(vtrack_tpl)
    tr_ov_full["id"] = uid()
    tr_ov_full["segments"] = [
        make_raw_overlay_seg(
            sp, t0, t1, sin, spd=spd, in_anim=ia, out_anim=oa, zoom_dir=zd,
            base_scale=bsc, tx=tx, ty=ty, is_dji=is_dji,
            custom_sliders=[("brightness", -0.35), ("contrast", -0.08)] if abs(t0 - 52.18) < 0.05 else None
        )
        for sp, t0, t1, sin, spd, ia, oa, zd, bsc, tx, ty, is_dji in FULL_RAW_OVERLAYS
    ]

    # ==========================================================================
    # 2. TRACKS 2..5 — RAW FLOATING PIPs + 4-TRACK EDITABLE RAW 2x2 BENTO GRID!
    #    Every single PIP and Bento card is a real raw Z:\...\F20\*.MP4 clip!
    # ==========================================================================
    PIP_MASK = {
        "aspectRatio": 0.78, "centerX": 0.0, "centerY": 0.0, "expansion": 0.0,
        "feather": 0.02, "height": 0.86, "invert": False, "rotation": 0.0,
        "roundCorner": 0.18, "width": 0.88,
    }
    BENTO_MASK = {
        "aspectRatio": 0.75, "centerX": 0.205, "centerY": 0.038, "expansion": 0.0,
        "feather": 0.01, "height": 0.365, "invert": False, "rotation": 0.0,
        "roundCorner": 0.16, "width": 0.61,
    }
    bento_sc = 0.71
    # seg.transform = target_card_center - bento_sc * mask_center
    bento_specs = [
        # (t0_s, src_in_s, card_cx, card_cy)
        (52.18, 14.20, -0.46, +0.35),  # Cell 1 (Top-Left): Tổ Yến Sào
        (52.40, 33.80, +0.46, +0.35),  # Cell 2 (Top-Right): 2 Hộp Rong Biển
        (52.62, 43.67, -0.46, -0.19),  # Cell 3 (Bottom-Left): Bánh Thuyền 250g
        (52.84, 49.29, +0.46, -0.19),  # Cell 4 (Bottom-Right): Rong Biển Kẹp Hạt 500g
    ]
    bento_segs = [
        make_raw_overlay_seg(
            DJI_DIR / "DJI_20261116093322_0084_D.MP4",
            t0_b, 56.18, sin_b, spd=1.00,
            in_anim="Rõ dần", out_anim="Mờ dần", zoom_dir=0,
            base_scale=bento_sc,
            tx=ccx - bento_sc * BENTO_MASK["centerX"],
            ty=ccy - bento_sc * BENTO_MASK["centerY"],
            mask_cfg=copy.deepcopy(BENTO_MASK), is_dji=True
        )
        for t0_b, sin_b, ccx, ccy in bento_specs
    ]

    pip_intro = make_raw_overlay_seg(
        DOC_DIR / "C3873.MP4", 6.35, 9.40, 0.40, spd=0.90,
        in_anim="Trượt sang trái", out_anim="Mờ dần", zoom_dir=0,
        base_scale=0.30, tx=0.56, ty=0.52, mask_cfg=copy.deepcopy(PIP_MASK), is_dji=False
    )
    pip_outro = make_raw_overlay_seg(
        ANH_HAU / "C3928.MP4", 136.40, 140.40, 1.50, spd=1.00,
        in_anim="Trượt sang trái", out_anim="Mờ dần", zoom_dir=0,
        base_scale=0.30, tx=0.56, ty=0.52, mask_cfg=copy.deepcopy(PIP_MASK), is_dji=False
    )

    # Track 2 holds the 2 corner PIPs + Bento Cell 1; Tracks 3, 4, 5 hold Bento Cells 2, 3, 4!
    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid(); tr_v2["segments"] = [pip_intro, bento_segs[0], pip_outro]
    tr_v3 = copy.deepcopy(vtrack_tpl); tr_v3["id"] = uid(); tr_v3["segments"] = [bento_segs[1]]
    tr_v4 = copy.deepcopy(vtrack_tpl); tr_v4["id"] = uid(); tr_v4["segments"] = [bento_segs[2]]
    tr_v5 = copy.deepcopy(vtrack_tpl); tr_v5["id"] = uid(); tr_v5["segments"] = [bento_segs[3]]

    # ==========================================================================
    # 3. NATIVE EDITABLE CAPCUT SUBTITLES (`check_flag = 15`, Selective Animation!)
    #    - 45/52 conversational subtitles have ZERO In/Out animation (steady, zero blinking!)
    #    - Only 7 key punchline/hook lines get subtle In ('Chữ mờ dần hiện vào' 0.18s)
    # ==========================================================================
    def make_native_coiny_subtitle(parts: list[tuple[str, bool]], t0_s: float, t1_s: float,
                                   pos_y: float = -0.58, in_anim: str | None = None, out_anim: str | None = None):
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
            "check_flag": 15,  # Clean Fill + Stroke ONLY (zero black box!)
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.35), us(t1_s) - st_u)

        refs = []
        anims = []
        if in_anim and in_anim in TEXT_ANIMS["in"]:
            ai = copy.deepcopy(TEXT_ANIMS["in"][in_anim])
            ai["start"] = 0
            ai["duration"] = min(180000, du_u // 4)
            anims.append(ai)
        if out_anim and out_anim in TEXT_ANIMS["out"]:
            ao = copy.deepcopy(TEXT_ANIMS["out"][out_anim])
            od = min(180000, du_u // 4)
            ao["duration"] = od
            ao["start"] = max(0, du_u - od)
            anims.append(ao)
        if anims:
            ma_id = uid()
            D["materials"].setdefault("material_animations", []).append({
                "animations": anims, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
            })
            refs.append(ma_id)

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tm_id,
            "target_timerange": {"start": st_u, "duration": du_u},
            "extra_material_refs": refs,
            "common_keyframes": [], "keyframe_refs": [],
        })
        ts["clip"]["transform"] = {"x": 0.0, "y": pos_y}
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["rotation"] = 0.0
        ts["uniform_scale"] = {"on": True, "value": 1.0}
        return ts

    PUNCHLINE_SUB_STARTS = {4.56, 17.58, 34.38, 52.00, 92.70, 130.08, 147.02}
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

    tr_sub = copy.deepcopy(ttrack_tpl)
    tr_sub["id"] = uid()
    tr_sub["segments"] = [
        make_native_coiny_subtitle(
            parts, t0, t1,
            pos_y=-0.65 if (abs(t0 - 52.00) < 0.05 or 100.0 <= t0 <= 107.6) else -0.58,
            in_anim="Chữ mờ dần hiện vào" if t0 in PUNCHLINE_SUB_STARTS else None,
            out_anim="Mờ dần" if abs(t0 - 147.02) < 0.05 else None
        )
        for t0, t1, parts in SUB_ITEMS
    ]

    # ==========================================================================
    # 4. SEPARATE NATIVE FLOATING WHITE-ON-RED CALLOUTS (`check_flag = 15`)
    #    Clean, purposeful animations (zero flashy 'Bụi vàng'; floating loop only on hero tags around Chị Oanh!)
    # ==========================================================================
    def make_native_floating_tag(
        text: str, t0_s: float, t1_s: float, pos_x: float, pos_y: float,
        size: float = 13.0, rot_deg: float = 0.0, in_anim: str = "Mờ",
        use_float_loop: bool = False, drift_up: bool = True
    ):
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
            "check_flag": 15,
        })
        D["materials"]["texts"].append(tm)

        st_u = us(t0_s)
        du_u = max(us(0.45), us(t1_s) - st_u)
        dur_s = du_u / 1e6

        anim_items = []
        ik = in_anim if in_anim in TEXT_ANIMS["in"] else "Mờ"
        ai = copy.deepcopy(TEXT_ANIMS["in"][ik])
        in_d = min(200000, du_u // 4)
        ai["start"] = 0
        ai["duration"] = in_d
        anim_items.append(ai)

        ao = copy.deepcopy(TEXT_ANIMS["out"]["Mờ dần"])
        out_d = min(180000, du_u // 4)
        ao["duration"] = out_d
        ao["start"] = max(0, du_u - out_d)
        anim_items.append(ao)

        if use_float_loop and "Chao đảo ngẫu nhiên" in TEXT_ANIMS["loop"] and du_u > (in_d + out_d + 250000):
            al = copy.deepcopy(TEXT_ANIMS["loop"]["Chao đảo ngẫu nhiên"])
            al["start"] = in_d
            al["duration"] = du_u - in_d - out_d
            anim_items.append(al)

        ma_id = uid()
        D["materials"].setdefault("material_animations", []).append({
            "animations": anim_items, "id": ma_id, "multi_language_current": "none", "type": "sticker_animation"
        })

        kfs = []
        if drift_up:
            kfs = [
                make_kf("KFTypePositionY", [(0.0, pos_y - 0.028), (min(0.32, dur_s * 0.45), pos_y), (dur_s, pos_y + 0.024)]),
                make_kf("KFTypeScaleX", [(0.0, 0.90), (min(0.20, dur_s * 0.35), 1.03), (min(0.36, dur_s * 0.6), 1.00)]),
                make_kf("KFTypeScaleY", [(0.0, 0.90), (min(0.20, dur_s * 0.35), 1.03), (min(0.36, dur_s * 0.6), 1.00)]),
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

    FLOATING_TAGS = [
        # (t0, t1, text, px, py, size, rot, in_anim, use_float_loop, drift_up)
        # Intro Title
        (0.20,   3.65, "SET QUÀ TRI ÂN 20/11",       0.00,  0.60, 14.2,  0.0, "Mờ",                  False, True),
        (0.45,   3.65, "THỰC PHẨM F20 × SKA NEST",   0.00,  0.46, 11.0,  0.0, "Chữ mờ dần hiện vào", False, False),

        # Floating around Chị Oanh on Track 0 (Hero Floating Callouts!)
        (6.38,   9.25, "104 SET QUÀ!",              -0.38,  0.46, 13.5, +4.0, "Trượt sang phải",     True,  True),
        (9.55,  13.55, "QUÀ BIẾU 20/11",            +0.34,  0.44, 13.0, -4.0, "Trượt sang trái",     True,  True),

        # Customer Order Highlights
        (15.70, 19.85, "ĐĂNG KHOA EDU • 77 SET",     0.00,  0.56, 13.0,  0.0, "Mờ",                  False, True),
        (20.30, 23.85, "HỘI PHỤ HUYNH • 13 SET",     0.00,  0.52, 12.5,  0.0, "Mờ",                  False, True),
        (24.72, 27.82, "HÀ NỘI • 10 SET",           -0.24,  0.50, 13.0, +3.0, "Trượt sang phải",     False, True),
        (28.08, 31.62, "TP.HCM • 04 SET",           +0.24,  0.50, 13.0, -3.0, "Trượt sang trái",     False, True),
        (33.82, 36.60, "ĐỦ 104 SET QUÀ!",            0.00,  0.52, 14.5,  0.0, "Mờ",                  True,  True),

        # Walk-in intro to 1 Set Quà (around Chị Oanh)
        (45.20, 49.45, "CHI TIẾT 01 SET QUÀ",       +0.28,  0.42, 12.5, -3.0, "Trượt sang trái",     True,  True),

        # 2x2 Raw Bento Grid Labels (52.18 - 56.15s: steady crisp labels centered on each cell!)
        (52.18, 56.15, "04 MÓN TRONG 01 SET QUÀ",    0.00,  0.76, 12.6,  0.0, "Mờ",                  False, False),
        (52.22, 56.15, "01 • TỔ YẾN",               -0.46,  0.14,  9.6,  0.0, "Chữ mờ dần hiện vào", False, False),
        (52.44, 56.15, "02 • RONG BIỂN",            +0.46,  0.14,  9.6,  0.0, "Chữ mờ dần hiện vào", False, False),
        (52.66, 56.15, "03 • BÁNH THUYỀN",          -0.46, -0.40,  9.2,  0.0, "Chữ mờ dần hiện vào", False, False),
        (52.88, 56.15, "04 • KẸP HẠT",              +0.46, -0.40,  9.6,  0.0, "Chữ mờ dần hiện vào", False, False),

        # Product Highlights floating above products / around Chị Oanh
        (58.28, 61.05, "01 TỔ YẾN SỢI DÀI",          0.00,  0.52, 13.2,  0.0, "Mờ",                  False, True),
        (63.18, 66.62, "01 • TÁO ĐỎ",               -0.34,  0.52, 12.2, +3.0, "Chữ mờ dần hiện vào", False, True),
        (63.82, 66.62, "02 • ĐÔNG TRÙNG",           +0.28,  0.38, 12.2, -3.0, "Chữ mờ dần hiện vào", False, True),
        (65.05, 66.62, "03 • KỶ TỬ",                -0.34,  0.22, 12.2, +3.0, "Chữ mờ dần hiện vào", False, True),
        (65.80, 66.62, "04 • ĐƯỜNG PHÈN",           +0.28,  0.08, 12.2, -3.0, "Chữ mờ dần hiện vào", False, True),

        (70.15, 74.45, "CAY NHẸ & SẤY MÈ",           0.00,  0.52, 12.8,  0.0, "Mờ",                  False, True),
        (77.20, 79.92, "BÁNH THUYỀN • 250G",         0.00,  0.52, 12.8,  0.0, "Mờ",                  False, True),
        (82.25, 85.35, "RONG BIỂN KẸP HẠT • 500G",   0.00,  0.52, 12.2,  0.0, "Mờ",                  False, True),
        (86.28, 89.28, "22 – 24 THANH!",            +0.30,  0.46, 13.5, -4.0, "Trượt sang trái",     True,  True),

        (89.45, 92.62, "GIÁ TRỊ NHẤT!",             -0.30,  0.44, 13.5, +3.5, "Trượt sang phải",     True,  True),
        (92.68, 95.82, "YẾN TINH CHẾ SỢI DÀI",       0.00,  0.52, 13.0,  0.0, "Mờ",                  False, True),
        (98.62, 102.75,"CẨM NANG YẾN SÀO",           0.00,  0.54, 12.8,  0.0, "Mờ",                  False, True),
        (102.85,107.25,"CÔNG DỤNG & CÁCH CHƯNG",     0.00,  0.56, 12.2,  0.0, "Chữ mờ dần hiện vào", False, False),

        (110.82,114.08,"GIỎ MICA TRONG SUỐT",        0.00,  0.54, 13.0,  0.0, "Mờ",                  False, True),
        (116.18,119.12,"QUAI XÁCH DA ĐỎ ĐÔ",         0.00,  0.54, 13.2,  0.0, "Mờ",                  False, True),
        (119.56,122.88,"HOA ĐỎ ĐIỂM NHẤN",           0.00,  0.52, 12.8,  0.0, "Mờ",                  False, True),
        (122.92,126.18,"NƠ MÀU BE XINH XẮN",         0.00,  0.54, 12.8,  0.0, "Mờ",                  False, True),

        (129.85,135.35,"TRỰC TIẾP SẢN XUẤT • GIÁ XƯỞNG", 0.00, 0.52, 12.0, 0.0, "Mờ",                False, True),
        (146.82,148.58,"INBOX OANH NGAY!",          +0.28,  0.44, 13.5, -4.0, "Trượt sang trái",     True,  True),
    ]

    float_lanes: list[list[dict]] = []
    for t0, t1, txt, px, py, sz, rot, ia, ufl, dup in sorted(FLOATING_TAGS, key=lambda x: x[0]):
        sg = make_native_floating_tag(txt, t0, t1, px, py, size=sz, rot_deg=rot, in_anim=ia, use_float_loop=ufl, drift_up=dup)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for lane in float_lanes:
            if lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                lane.append(sg)
                placed = True
                break
        if not placed:
            float_lanes.append([sg])

    float_tracks = []
    for lane in float_lanes:
        tr_f = copy.deepcopy(ttrack_tpl)
        tr_f["id"] = uid()
        tr_f["segments"] = lane
        float_tracks.append(tr_f)

    # ==========================================================================
    # 5. PURPOSEFUL EAR-VERIFIED USER SFX (`-18..-21dB`, Zero Overuse!)
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
            em = copy.deepcopy(tpl_e)
            em["id"] = uid()
            if k == "speeds":
                em["speed"] = 1.0
            D["materials"][k].append(em)
            refs.append(em["id"])
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
        (0.18,   "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Air Mở Cảnh",      0.12, 0.7),
        (0.30,   "Ting & Chuông Đúng - Chimes 6115_04_1 (7s).mp3",                              "Chuông Gió Mở",    0.10, 1.8),
        (6.35,   "Whoosh - Fast Swoosh Pop 01 (1s).mp3",                                        "Air PIP 104 Set",  0.10, 0.6),
        (9.55,   "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Gió Mềm 20/11",    0.10, 0.5),
        (15.65,  "Whoosh - Swish Sound 1(1695850) (1s).mp3",                                    "Swish ĐK Edu",     0.10, 0.6),
        (24.67,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Swipe Hà Nội",     0.10, 0.6),
        (33.82,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đủ 104 Set",  0.10, 1.2),
        (45.20,  "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh 01 Set",    0.10, 0.5),
        (52.16,  "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Bento Air",        0.11, 0.6),
        (52.40,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Món 02",      0.10, 0.35),
        (52.62,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Món 03",      0.10, 0.35),
        (52.84,  "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Món 04",      0.09, 1.0),
        (63.16,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Táo Đỏ",      0.10, 0.35),
        (63.82,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Đông Trùng",  0.10, 0.35),
        (65.05,  "Click & Máy Chữ - click (1s).mp3",                                            "Tick Kỷ Tử",       0.10, 0.35),
        (65.80,  "Ding - Tiếng chuông ngân trong trẻo.mp3",                                     "Ding Đường Phèn",  0.09, 1.1),
        (70.10,  "Whoosh - Fuwa short wind noise swipe etc(222764) (1s).mp3",                   "Swipe Rong Biển",  0.10, 0.6),
        (82.20,  "Đời Thường & ASMR - The sound that deals with the Shap Schat card (1s).mp3",  "Card 500g",        0.11, 0.7),
        (89.45,  "Whoosh - Title Swoosh (1s).mp3",                                              "Swoosh Giá Trị",   0.10, 0.7),
        (98.58,  "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Mở Cẩm Nang 1",    0.12, 0.8),
        (102.80, "Đời Thường & ASMR - Paper page turn sound 1 scene change swipe (1s).mp3",     "Lật Trang Trong",  0.11, 0.8),
        (116.15, "Lấp Lánh & Phép Thuật - Shine_03 (1s).mp3",                                   "Shine Quai Da",    0.09, 0.9),
        (129.80, "Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3",                                   "Whoosh Sản Xuất",  0.10, 0.6),
        (136.38, "Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3",                                   "Swoosh PIP Cảm Ơn",0.10, 0.5),
        (146.82, "Ting & Chuông Đúng - Bell sound title animation(954662) (2s).mp3",            "Bell Inbox Ngay",  0.11, 1.4),
    ]

    sfx_lanes: list[list[dict]] = []
    for t0, fn, lbl, vol, mdur in sorted(SFX_EVENTS, key=lambda x: x[0]):
        sg = make_sfx_seg(fn, lbl, t0, vol=vol, max_dur_s=mdur)
        st_u = sg["target_timerange"]["start"]
        placed = False
        for lane in sfx_lanes:
            if lane[-1]["target_timerange"]["start"] + lane[-1]["target_timerange"]["duration"] + 33333 <= st_u:
                lane.append(sg)
                placed = True
                break
        if not placed:
            sfx_lanes.append([sg])

    sfx_tracks = []
    for lane in sfx_lanes:
        tr_a = copy.deepcopy(atrack_tpl)
        tr_a["id"] = uid()
        tr_a["segments"] = lane
        sfx_tracks.append(tr_a)

    D["tracks"] = [
        track0_orig,     # Track 0: 100.00% Untouched Main Video!
        tr_ov_full,      # Track 1: 24 Raw Camera Overlays (21 Hard Cuts + 3 Boundary Fades + Native DJI Color Sliders)!
        tr_v2,           # Track 2: 2 Raw PIPs + Raw Bento Cell 1!
        tr_v3,           # Track 3: Raw Bento Cell 2!
        tr_v4,           # Track 4: Raw Bento Cell 3!
        tr_v5,           # Track 5: Raw Bento Cell 4!
        tr_sub,          # Track 6: 52 Native Editable Coiny Subtitles (45 steady + 7 punchline In)!
        *float_tracks,   # Tracks 7..10: 34 Native Editable White-on-Red Floating Callouts!
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

    # Unlink before writing so OS hardlinks can never cross-contaminate
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
            # Keep ONLY original Track 0 / BGM entries + our 100% raw Z:\...\F20 entries!
            clean_vals = [
                x for x in bucket.get("value", [])
                if "capcut_layers_1117" not in str(x.get("file_Path", ""))
            ]
            existing = {x.get("file_Path") for x in clean_vals}
            for ne in new_dm_entries:
                if ne["file_Path"] not in existing:
                    clean_vals.append(ne)
            bucket["value"] = clean_vals
    (DRAFT_DIR / "draft_meta_info.json").write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

    pj["update_time"] = now_us
    for t_ent in pj.get("timelines", []):
        t_ent["update_time"] = now_us
    (DRAFT_DIR / "Timelines" / "project.json").write_text(json.dumps(pj, ensure_ascii=False), encoding="utf-8")

    rmi_path = ROOT / "root_meta_info.json"
    rmi = json.loads(rmi_path.read_text(encoding="utf-8"))
    for x in rmi.get("all_draft_store", []):
        if x.get("draft_name") == "1117 F20":
            x["tm_duration"] = main_end_u
            x["tm_draft_modified"] = now_us
    rmi_path.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    print("SUCCESS V5 PURE RAW SOURCES & SELECTIVE ANIMATIONS -> Updated '1117 F20'!")
    print(f"  -> Track 0: {len(track0_orig['segments'])} segs (100.00% untouched)")
    print(f"  -> Overlay Videos: {len(tr_ov_full['segments'])} full-screen + 2 PIPs + 4 Bento cells = 30 segs (100% raw Z:/Máy tính khác/My Computer/F20/... MP4s!)")
    print(f"  -> Track 1 Animations: 21/24 Hard Cuts (0 anim) + 3 boundary fades")
    print(f"  -> Subtitles: {len(tr_sub['segments'])} native Coiny (45 steady + 7 punchline In, check_flag=15)")
    print(f"  -> Floating White-on-Red Callouts: {len(FLOATING_TAGS)} native Coiny across {len(float_tracks)} tracks (check_flag=15)")
    print(f"  -> SFX: {len(SFX_EVENTS)} ear-verified user SFX (-18..-21dB)")

if __name__ == "__main__":
    main()
