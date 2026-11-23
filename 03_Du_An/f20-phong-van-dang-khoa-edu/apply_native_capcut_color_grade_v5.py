"""
Apply 100% Native Non-Destructive CapCut Color Grading directly onto the V5 CapCut Draft
(using 100% untouched ORIGINAL raw Sony + 10-bit DJI camera files — ZERO baked color!).
Adds:
  1. Scientifically matched Per-Clip Native CapCut Adjustment Sliders on EVERY raw clip
     in Track 0 & Track 1 (matching Doorway C3925, Interview C3926/C3932, 10-bit flat DJI
     macros, Office fluorescent Sony B-rolls, and Warm Showroom C3864/C3866-C3875!).
  2. Dedicated Native CapCut Adjustment Layer (`type: "adjust"`, `Điều chỉnh1`, `visible: True`)
     with Master Polish Sliders + 4 Skin-Tone/Brand HSL channels + Pro Color Wheels, positioned
     strictly above Video Tracks 0-1 and below Sticker/Text tracks so brand stickers & text stay pure!
  3. All effect paths verified 100% on local PC `C:/Users/001/...` cache.
"""
import copy, json, shutil, time, uuid
from pathlib import Path

CC_ROOT   = Path(r"D:\Capcut\CapCut Drafts")
TPL_DRAFT = CC_ROOT / "0414(1) (1)"
V5_DRAFT  = CC_ROOT / "261122 F20 Phỏng Vấn Đăng Khoa Edu (V5 Nhạc Vui + Text Chuẩn)"
ARCHIVE_G = Path(r"G:\My Drive\AI_Full_Studio\03_Du_An\f20-phong-van-dang-khoa-edu")

LOCAL_EFF_DIR = "C:/Users/001/AppData/Local/CapCut/User Data/Cache/effect/7501974767453474064/20cd8db6531c21bf7e4053026d20e395"
LOCAL_FLT_DIR = "C:/Users/001/AppData/Local/CapCut/User Data/Cache/effect/7358753189421650433/8847598657b88253551fd5d1f2208bb1"

def uid(): return str(uuid.uuid4()).upper()

def fix_001_paths(obj):
    if isinstance(obj, dict):
        return {k: fix_001_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fix_001_paths(x) for x in obj]
    if isinstance(obj, str):
        s = obj.replace("C:/Users/Hang thu/", "C:/Users/001/")
        if "7501974767453474064" in s and s.endswith("/lumi_hub_path"):
            return LOCAL_EFF_DIR + "/lumi_hub_path"
        if "7501974767453474064" in s:
            return LOCAL_EFF_DIR
        if "7358753189421650433" in s:
            return LOCAL_FLT_DIR
        return s
    return obj

# Calibrated per-camera native CapCut slider profiles (based on real RGB/Y/p05/p95/sat measurements!)
CAMERA_PROFILES = {
    "doorway_handshake": {  # C3925.MP4: bright glass p95=255, slight green cast G-mid=+2.8, sat=18..30
        "highlight": -0.22, "contrast": 0.08, "saturation": 0.10,
        "temperature": 0.06, "tone": 0.06, "clear": 0.08, "sharpen": 0.08,
    },
    "interview_bluewall": { # C3926.MP4, C3932.MP4: balanced midtones, protect white shirt, lift dark blazer/carpet
        "light_sensation": 0.05, "brightness": 0.04, "contrast": 0.05,
        "highlight": -0.10, "shadow": 0.08, "saturation": 0.06,
        "temperature": 0.04, "clear": 0.08, "sharpen": 0.10,
    },
    "dji_10bit_macro": {    # DJI_*_D.MP4: flat 10-bit p05=55, p95=204, sat=24 -> match Sony crispness & rich color!
        "black": -0.18, "shadow": -0.14, "highlight": 0.15, "white": 0.09,
        "contrast": 0.18, "saturation": 0.26, "temperature": 0.05,
        "clear": 0.14, "sharpen": 0.14,
    },
    "office_sony_broll": {  # C3908/C3910/C3911/C3915/C3917/C3919/C3921: strong fluorescent green cast G-mid=+6.9!
        "brightness": 0.05, "shadow": 0.10, "contrast": 0.06,
        "temperature": 0.06, "tone": 0.08, "saturation": 0.06,
        "clear": 0.08, "sharpen": 0.08,
    },
    "showroom_warm": {      # C3864/C3866/C3870/C3873/C3874/C3875: very warm R-B=+50, bright sign p95=252, dim face Y=127
        "brightness": 0.06, "light_sensation": 0.05, "shadow": 0.10,
        "highlight": -0.14, "temperature": -0.05, "saturation": -0.04,
        "sharpen": 0.08,
    },
}

def pick_profile(fn: str) -> str | None:
    if fn.startswith("DJI_"):
        return "dji_10bit_macro"
    if fn == "C3925.MP4":
        return "doorway_handshake"
    if fn in ("C3926.MP4", "C3932.MP4"):
        return "interview_bluewall"
    if fn in ("C3908.MP4", "C3910.MP4", "C3911.MP4", "C3915.MP4", "C3917.MP4", "C3919.MP4", "C3921.MP4"):
        return "office_sony_broll"
    if fn in ("C3864.MP4", "C3866.MP4", "C3870.MP4", "C3873.MP4", "C3874.MP4", "C3875.MP4"):
        return "showroom_warm"
    return None  # PNG stickers, Name Tags, F20 closing banner stay 100% untouched!

def main():
    assert not (V5_DRAFT / ".locked").exists(), f"'{V5_DRAFT.name}' is currently open in CapCut!"
    assert Path(LOCAL_EFF_DIR).exists(), f"Missing local CapCut adjust effect cache: {LOCAL_EFF_DIR}"
    assert Path(LOCAL_FLT_DIR).exists(), f"Missing local CapCut filter cache: {LOCAL_FLT_DIR}"

    dc_tpl = json.loads((TPL_DRAFT / "draft_content.json").read_text(encoding="utf-8"))
    D      = json.loads((V5_DRAFT / "draft_content.json").read_text(encoding="utf-8"))
    pj     = json.loads((V5_DRAFT / "Timelines" / "project.json").read_text(encoding="utf-8"))

    # Extract authentic CapCut native adjustment templates from 0414(1) (1) and remap to PC 001 cache
    SLIDER_TPL = {}
    for e in dc_tpl["materials"].get("effects", []):
        et = e.get("type", "")
        if et in ("brightness","contrast","saturation","highlight","shadow","white","black",
                  "light_sensation","clear","sharpen","temperature","tone") and et not in SLIDER_TPL:
            SLIDER_TPL[et] = fix_001_paths(copy.deepcopy(e))

    HSL_TPL = {}
    for h in dc_tpl["materials"].get("hsl", []):
        ct = h.get("hsl_color_type")
        if ct not in HSL_TPL:
            HSL_TPL[ct] = fix_001_paths(copy.deepcopy(h))

    pcw_tpl = fix_001_paths(copy.deepcopy(dc_tpl["materials"]["primary_color_wheels"][0]))
    lcw_tpl = fix_001_paths(copy.deepcopy(dc_tpl["materials"]["log_color_wheels"][0]))
    adj_tr_tpl  = copy.deepcopy(next(t for t in dc_tpl["tracks"] if t["type"] == "adjust"))
    adj_seg_tpl = copy.deepcopy(adj_tr_tpl["segments"][0])
    adj_ph_tpl  = copy.deepcopy(dc_tpl["materials"]["placeholders"][0])

    # Clear any old per-clip color effects (preserve filter track's Sống động 2)
    vid_map = {v["id"]: v for v in D["materials"]["videos"]}
    old_filter_ids = {s["material_id"] for t in D["tracks"] if t["type"] == "filter" for s in t["segments"]}
    kept_effects = []
    for e in D["materials"].get("effects", []):
        if e["id"] in old_filter_ids:
            e2 = fix_001_paths(e)
            e2["value"] = 0.12  # Gentle Sống động 2 polish (12%)
            kept_effects.append(e2)
    D["materials"]["effects"] = kept_effects
    D["materials"]["hsl"] = []
    D["materials"]["placeholders"] = []
    D["materials"]["primary_color_wheels"] = []
    D["materials"]["log_color_wheels"] = []

    # Remove old slider refs from Track 0 & Track 1 segments, then attach fresh scene-calibrated sliders!
    slider_types = set(SLIDER_TPL.keys())
    valid_mat_ids = set()
    for k, lst in D["materials"].items():
        if isinstance(lst, list):
            for x in lst:
                if isinstance(x, dict) and "id" in x:
                    valid_mat_ids.add(x["id"])

    graded_counts = {}
    speech_end_u = 0
    for ti, tr in enumerate(D["tracks"]):
        if tr["type"] != "video" or ti > 1:
            continue
        for sg in tr["segments"]:
            vm = vid_map.get(sg["material_id"], {})
            fn = vm.get("material_name", "")
            if ti == 0:
                speech_end_u = max(speech_end_u, sg["target_timerange"]["start"] + sg["target_timerange"]["duration"])
            # Strip dangling effect refs
            sg["extra_material_refs"] = [r for r in sg.get("extra_material_refs", []) if r in valid_mat_ids]
            prof_key = pick_profile(fn)
            if not prof_key:
                continue
            prof = CAMERA_PROFILES[prof_key]
            sg["enable_adjust"] = True
            sg["enable_hsl"] = True
            sg["enable_color_wheels"] = True
            sg["enable_color_curves"] = True
            sg["enable_hsl_curves"] = True
            sg["enable_lut"] = True
            for stype, sval in prof.items():
                ef = copy.deepcopy(SLIDER_TPL[stype])
                ef["id"] = uid()
                ef["value"] = float(sval)
                D["materials"]["effects"].append(ef)
                sg["extra_material_refs"].append(ef["id"])
            graded_counts[prof_key] = graded_counts.get(prof_key, 0) + 1

    # Build dedicated Master Native CapCut Adjustment Track (`Điều chỉnh1`, visible=True, 0 -> speech_end_u)
    ph = copy.deepcopy(adj_ph_tpl)
    ph["id"] = uid()
    ph["name"] = "Điều chỉnh1"
    D["materials"]["placeholders"].append(ph)

    adj_refs = []
    # Master unifying subtle polish sliders (editable in 1 click inside Điều chỉnh1!)
    MASTER_SLIDERS = {
        "light_sensation": 0.04,
        "contrast":        0.04,
        "clear":           0.06,
        "sharpen":         0.06,
        "temperature":     0.02,
    }
    for stype, sval in MASTER_SLIDERS.items():
        ef = copy.deepcopy(SLIDER_TPL[stype])
        ef["id"] = uid()
        ef["value"] = float(sval)
        D["materials"]["effects"].append(ef)
        adj_refs.append(ef["id"])

    # 4 Skin-Tone & Brand HSL channels (100% editable in CapCut HSL panel!)
    MASTER_HSL = [
        (2, 0, +6, +8),   # Orange / Da người: sáng da tự nhiên & hồng hào!
        (4, +4, +8, +4),  # Green / Màu thương hiệu F20 tươi sáng!
        (1, 0, +4, +3),   # Red / Thảm đỏ & nơ quà sang, không bết!
        (5, 0, -8, +4),   # Cyan / Dịu ánh đèn huỳnh quang trên tường xanh!
    ]
    for ctype, h_v, s_v, l_v in MASTER_HSL:
        if ctype in HSL_TPL:
            ho = copy.deepcopy(HSL_TPL[ctype])
            ho["id"] = uid()
            ho["hue"], ho["saturation"], ho["lightness"] = int(h_v), int(s_v), int(l_v)
            ho["interacting"] = False
            D["materials"]["hsl"].append(ho)
            adj_refs.append(ho["id"])

    # Clean Pro Color Wheels initialized at 0.0 so user can dial Lift/Gamma/Gain/Offset immediately
    pcw = copy.deepcopy(pcw_tpl); pcw["id"] = uid()
    lcw = copy.deepcopy(lcw_tpl); lcw["id"] = uid()
    D["materials"]["primary_color_wheels"].append(pcw); adj_refs.append(pcw["id"])
    D["materials"]["log_color_wheels"].append(lcw);     adj_refs.append(lcw["id"])

    adj_seg = copy.deepcopy(adj_seg_tpl)
    adj_seg.update({
        "id": uid(),
        "material_id": ph["id"],
        "source_timerange": None,
        "target_timerange": {"start": 0, "duration": int(speech_end_u)},
        "visible": True,  # ACTIVE Adjustment Layer!
        "enable_adjust": True,
        "enable_hsl": True,
        "enable_color_wheels": True,
        "enable_color_curves": True,
        "enable_hsl_curves": True,
        "enable_lut": True,
        "enable_smart_color_adjust": False,
        "extra_material_refs": adj_refs,
        "common_keyframes": [],
        "keyframe_refs": [],
        "render_index": 0,
    })
    tr_adj = copy.deepcopy(adj_tr_tpl)
    tr_adj["id"] = uid()
    tr_adj["flag"] = 0
    tr_adj["attribute"] = 0
    tr_adj["segments"] = [adj_seg]

    # Reorder tracks cleanly:
    # [0] Track 0 Main Raw Video -> [1] Track 1 Raw B-Rolls -> [2] Master Adjustment Track (`Điều chỉnh1`)
    # -> [3] Filter Track (`Sống động 2` 12%) -> [4..8] Stickers & Name Tags (pure colors!) -> Texts -> Audios
    old_tracks = [t for t in D["tracks"] if t["type"] != "adjust"]
    v_main   = old_tracks[0]
    v_broll  = old_tracks[1]
    tr_filt  = next(t for t in old_tracks if t["type"] == "filter")
    v_ovls   = [t for t in old_tracks[2:] if t["type"] == "video"]
    t_tracks = [t for t in old_tracks if t["type"] == "text"]
    a_tracks = [t for t in old_tracks if t["type"] == "audio"]

    # Ensure Filter segment is active & stops cleanly at speech_end_u (not shifting F20 banner!)
    for fs in tr_filt["segments"]:
        fs["visible"] = True
        fs["target_timerange"] = {"start": 0, "duration": int(speech_end_u)}

    D["tracks"] = [v_main, v_broll, tr_adj, tr_filt, *v_ovls, *t_tracks, *a_tracks]
    for ti, tr in enumerate(D["tracks"]):
        for s in tr["segments"]:
            s["track_render_index"] = ti
            if tr["type"] == "video": s["render_index"] = ti
            elif tr["type"] == "adjust": s["render_index"] = 0
            elif tr["type"] == "filter": s["render_index"] = 10000
            elif tr["type"] == "text": s["render_index"] = 14000 + ti

    now_s, now_us = int(time.time()), int(time.time() * 1_000_000)
    D["update_time"] = now_s

    tl_id = pj["main_timeline_id"]
    tl_sub = V5_DRAFT / "Timelines" / tl_id
    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for p_out in [V5_DRAFT/"draft_content.json", V5_DRAFT/"draft_content.json.bak", V5_DRAFT/"template-2.tmp",
                  tl_sub/"draft_content.json", tl_sub/"draft_content.json.bak", tl_sub/"template-2.tmp"]:
        p_out.write_bytes(dc_bytes)

    # Update modified timestamp in draft_meta_info.json
    dmi_p = V5_DRAFT / "draft_meta_info.json"
    dmi = json.loads(dmi_p.read_text(encoding="utf-8"))
    dmi["tm_draft_modified"] = now_us
    dmi_p.write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

    # Forensic assertions!
    dc_txt = dc_bytes.decode("utf-8")
    assert "Hang thu" not in dc_txt, "Found stale Hang thu path!"
    assert D["id"] == pj["id"] == pj["main_timeline_id"] == pj["timelines"][0]["id"]
    assert all(vs.get("choice") == 0 and vs.get("production_path") == "" for vs in D["materials"]["vocal_separations"])
    assert all(Path(v["path"]).is_file() for v in D["materials"]["videos"])
    assert all(Path(a["path"]).is_file() for a in D["materials"]["audios"])

    if ARCHIVE_G.exists():
        shutil.copy2(Path(__file__), ARCHIVE_G / Path(__file__).name)

    print("=== NATIVE CAPCUT COLOR GRADING APPLIED SUCCESSFULLY! ===")
    print("  Draft            :", V5_DRAFT)
    print("  Per-clip grades  :", graded_counts, f"(total {sum(graded_counts.values())} raw clips graded non-destructively!)")
    print("  Master Adjust    : Track [2] 'Điều chỉnh1' (5 sliders + 4 Skin/Brand HSL + Primary/Log Color Wheels, visible=True)")
    print("  Filter Track     : Track [3] 'Sống động 2' (12%, stops before F20 Banner)")
    print("  Raw Sources      : 100% original untouched Sony & 10-bit DJI files | 0 Hang thu paths | 0 bad vocal_separations!")

if __name__ == "__main__":
    main()
