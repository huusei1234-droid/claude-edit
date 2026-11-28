# -*- coding: utf-8 -*-
"""
Apply Today's (25/11/2026) Complete Client + Min Ngọc Feedback directly to:
  "1124 - Mövenpick 7 Năm (Full Hiệu Ứng)"
Preserving 100% of all user's manual edits up to 25/11 14:38!

Exact edits applied:
1. Ý 1 (S26, 47.17s -> 61.50s):
   - Replace IMG_4913.MOV ("source con nhỏ bên ngoài") with raw IMG_5024.MOV ("source có thằng đang nghe đt")
     src=2.60s + 14.70s @ speed=1.0256x -> exact 14.33s (cleanly trims off off-camera "Okay", full phone call!)
   - Confident luxury framing + smooth Ken Burns (scale 1.14 -> 1.22, pos.y=+0.02)
   - Mute noisy raw lobby audio on S26 (vol=0.0); place Demucs-cleaned & child-scream-removed
     Giong_hat_IMG_5024.wav on Track 13 (aligned 47.17s -> 61.50s) + gently raise BGM ducking floor
     during 50s..61.5s (0.26 -> 0.42) so audio feels rich & seamless.
   - Replace mismatched female English subtitles ("Sir Jeffrey...") at 48.80s..59.87s with clean accurate
     subtitle matching his actual audible closing line ("...and I will inform my colleagues / to assist you.").
2. Ý 2 (Track 2 S0, 62.33s -> 73.90s, bottom-left of 4-panel grid):
   - Replace IMG_5024.MOV with raw IMG_5046.MOV (already in draft, dur=10.07s),
     src=0.00 + 10.066s @ smooth constant speed 0.8703x -> exact 11.57s, vol=0.0 (no clash with IMG_4875).
3. Bonus (Nhung 11:04 "Nhớ cà mụn cho bé này nha"):
   - Point Track 0 S27 (61.50s -> 73.90s, top-left of 4-panel grid) to skin-retouched
     IMG_4913_retouched_s27.mp4 (eyes/brows/lips/hair 100% protected, natural cheek blemish removal),
     adjusting source_timerange start (15.77s -> 0.77s) & S27 keyframe time_offsets (-15.0s) seamlessly!
4. Ý 3 (S29, 75.30s -> 76.93s — "1p15s đổi ảnh"):
   - Replace IMG_4575.HEIC with HD IMG_PCCC_NEW.jpg (1200x1600, smiling yellow fire-suit man giving 2 thumbs up),
     FULL_CROP_1_1 reset (0% bottom crop bug), centered below chapter title (scale 1.46 -> 1.54, pos=(0.0, -0.07 -> -0.09)).
5. Ý 4 (S25, 46.00s -> 47.17s — "zoom vào lấy cảnh tay đưa thư"):
   - Apply smooth tight zoom-in keyframes directly on IMG_4934.MOV focused squarely on the hands passing
     the white envelope (scale 2.55 -> 2.80, transform (-0.22, +0.34) -> (-0.26, +0.38)).
6. Ý 5 (Insert new Zalo 00:04 wish video into "đoạn lời chúc"):
   - Insert wish_new_front_office.mp4 (3.40s, src 0.15s -> 3.55s) at 143.47s (right after S49 Russian boy
     and right before S50 full-team cheer Clip ghép3!), with smooth Ken Burns 1.00 -> 1.07,
     clean festive transitions (Kết hợp 0.37s in, Chói lòa 1 0.33s out), Demucs-cleaned Giong_hat_wish_new.wav
     on Track 13 (volume matched + 33ms/67ms micro-fades), and matching native Champagne Gold subtitle
     "Happy Birthday / Mövenpick Resort Cam Ranh!".
   - Ripple-shift EVERY segment & keyframe >= 143.45s across ALL 20 tracks cleanly by +3.40s (+3,400,000 us),
     extend BGM Track 12 cleanly by +3.40s (well within 189.30s BGM length!), shift BGM finale swell keyframes
     by +3.40s (in BGM source-time!), and update draft duration, draft_meta_info.json & root_meta_info.json!
"""

import copy
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CAPCUT_ROOT = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "1124 - Mövenpick 7 Năm (Full Hiệu Ứng)"
DRAFT_DIR = CAPCUT_ROOT / DRAFT_NAME
RMI_PATH = CAPCUT_ROOT / "root_meta_info.json"
PLACEHOLDER = "##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##"
SCRATCH = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\2260024d-5ff1-4155-897f-9516b8703802\scratch")

FULL_CROP_1_1 = {
    "lower_left_x": 0.0,
    "lower_left_y": 1.0,
    "lower_right_x": 1.0,
    "lower_right_y": 1.0,
    "upper_left_x": 0.0,
    "upper_left_y": 0.0,
    "upper_right_x": 1.0,
    "upper_right_y": 0.0,
}


def uid():
    return str(uuid.uuid4()).upper()


def s2u(sec: float) -> int:
    return int(round(sec * 1_000_000))


def probe_media(path: Path):
    r = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration:stream=codec_type,width,height",
            "-of", "json", str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(r.stdout)
    dur_us = int(round(float(info["format"]["duration"]) * 1_000_000))
    w, h = 0, 0
    for st in info.get("streams", []):
        if st.get("codec_type") == "video":
            w, h = int(st.get("width", 0)), int(st.get("height", 0))
            break
    return dur_us, w, h


def make_kf_point(t_us: int, val: float) -> dict:
    return {
        "id": uid(),
        "curveType": "Line",
        "time_offset": int(t_us),
        "left_control": {"x": 0.0, "y": 0.0},
        "right_control": {"x": 0.0, "y": 0.0},
        "values": [round(float(val), 4)],
        "string_value": "",
        "graphID": "",
    }


def set_ken_burns(seg: dict, sc0: float, sc1: float, px0: float, py0: float, px1: float, py1: float):
    sr = seg.get("source_timerange") or {"start": 0, "duration": seg["target_timerange"]["duration"]}
    t0 = int(sr["start"])
    t1 = int(sr["start"] + sr["duration"])
    clip = seg.setdefault("clip", {})
    rot = float(clip.get("rotation", 0.0))
    clip["scale"] = {"x": round(sc0, 4), "y": round(sc0, 4)}
    clip["transform"] = {"x": round(px0, 4), "y": round(py0, 4)}
    seg["uniform_scale"] = {"on": True, "value": 1.0}

    px_pts = [make_kf_point(t0, px0)]
    if abs(px1 - px0) > 1e-4:
        px_pts.append(make_kf_point(t1, px1))
    py_pts = [make_kf_point(t0, py0)]
    if abs(py1 - py0) > 1e-4:
        py_pts.append(make_kf_point(t1, py1))

    seg["common_keyframes"] = [
        {"id": uid(), "material_id": "", "property_type": "KFTypePositionX", "keyframe_list": px_pts},
        {"id": uid(), "material_id": "", "property_type": "KFTypePositionY", "keyframe_list": py_pts},
        {"id": uid(), "material_id": "", "property_type": "KFTypeScaleX", "keyframe_list": [make_kf_point(t0, sc0), make_kf_point(t1, sc1)]},
        {"id": uid(), "material_id": "", "property_type": "KFTypeRotation", "keyframe_list": [make_kf_point(t0, rot)]},
    ]


def set_segment_speed(seg: dict, new_speed: float, mats: dict):
    """Update both seg['speed'] and its referenced speeds material object."""
    seg["speed"] = round(float(new_speed), 6)
    spmap = {s["id"]: s for s in mats.get("speeds", [])}
    found = False
    for r in seg.get("extra_material_refs", []):
        if r in spmap:
            spmap[r]["speed"] = round(float(new_speed), 6)
            found = True
    if not found:
        sid = uid()
        mats.setdefault("speeds", []).append({"id": sid, "type": "speed", "mode": 0, "speed": round(float(new_speed), 6), "curve_speed": None})
        seg.setdefault("extra_material_refs", []).append(sid)


def rebuild_clean_5024_audio():
    """Put dynaudnorm BEFORE child-scream ducking so 2.6s..6.8s stays cleanly silenced!"""
    voc_5024 = SCRATCH / "demucs_out" / "htdemucs" / "IMG_5024" / "vocals.wav"
    dst_wav = DRAFT_DIR / "materials" / "audio" / "feedback_1125" / "Giong_hat_IMG_5024.wav"
    # 1) Normalize voice cleanly first
    # 2) Then mute 0..6.8s (kid scream during VO) and smooth fade-in 6.8..7.5s, keeping 7.5..17.6s clear!
    vol_expr = "if(lt(t,6.8), 0.0, if(lt(t,7.5), (t-6.8)/0.7, 1.0))"
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(voc_5024),
            "-af", f"highpass=f=140,lowpass=f=4000,afftdn=nf=-24,dynaudnorm=f=180:g=11:m=5,loudnorm=I=-18:TP=-2.0:LRA=10,volume='{vol_expr}':eval=frame",
            "-ar", "44100", "-ac", "2", str(dst_wav),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    # Save mp3 preview for ear check
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(dst_wav), "-ss", "2.6", "-t", "14.7", "-acodec", "libmp3lame", "-q:a", "2", str(SCRATCH / "verify_5024_vocal_v2.mp3")],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print("[Audio] Rebuilt clean child-scream-free Giong_hat_IMG_5024.wav")
    return dst_wav


def main():
    assert not (DRAFT_DIR / ".locked").exists(), "CapCut draft is currently LOCKED! Close draft in CapCut first."

    # Rebuild 5024 clean vocal with ducking AFTER normalization
    wav_5024_path = rebuild_clean_5024_audio()

    # Verify all required feedback assets exist inside draft
    pccc_path = DRAFT_DIR / "materials" / "video" / "feedback_1125" / "IMG_PCCC_NEW.jpg"
    wish_vid_path = DRAFT_DIR / "materials" / "video" / "feedback_1125" / "wish_new_front_office.mp4"
    wish_wav_path = DRAFT_DIR / "materials" / "audio" / "feedback_1125" / "Giong_hat_wish_new.wav"
    s27_smooth_path = DRAFT_DIR / "materials" / "video" / "feedback_1125" / "IMG_4913_retouched_s27.mp4"
    for p in (pccc_path, wish_vid_path, wish_wav_path, s27_smooth_path, wav_5024_path):
        assert p.exists(), f"Missing prepared asset: {p}"

    # Backup current draft_content.json (from 11/25 14:38) before editing!
    dc_path = DRAFT_DIR / "draft_content.json"
    bak_path = DRAFT_DIR / "draft_content.json.bak_before_feedback_1125"
    if not bak_path.exists():
        shutil.copy2(dc_path, bak_path)
        print(f"[Backup] Saved original pre-feedback draft to {bak_path.name}")
    else:
        # Always load from the clean pre-feedback backup so script is 100% idempotent!
        print(f"[Idempotent] Loading from clean backup {bak_path.name}")
        dc_path_load = bak_path
    dc_path_load = bak_path

    D = json.loads(dc_path_load.read_text(encoding="utf-8"))
    mats = D["materials"]
    tracks = D["tracks"]

    t0 = tracks[0]["segments"]
    assert len(t0) == 55, f"Expected 55 segments on Track 0, got {len(t0)}"

    vmap = {v["id"]: v for v in mats["videos"]}
    amap = {a["id"]: a for a in mats["audios"]}
    tmap = {t["id"]: t for t in mats["texts"]}

    # Verify anchor segments before mutating
    assert vmap[t0[25]["material_id"]]["material_name"] == "IMG_4934.MOV"
    assert vmap[t0[26]["material_id"]]["material_name"] == "IMG_4913.MOV"
    assert vmap[t0[27]["material_id"]]["material_name"] == "IMG_4913.MOV"
    assert vmap[t0[29]["material_id"]]["material_name"] == "IMG_4575.HEIC"
    assert vmap[tracks[2]["segments"][0]["material_id"]]["material_name"] == "IMG_5024.MOV"
    assert vmap[t0[49]["material_id"]]["material_name"] == "IMG_4391.MOV"
    assert vmap[t0[50]["material_id"]]["material_name"] == "Clip ghép3"

    # Templates
    tpl_vid_mat = copy.deepcopy(vmap[t0[48]["material_id"]])  # clean 1080x1920 video material template
    tpl_photo_mat = copy.deepcopy(vmap[t0[31]["material_id"]])  # clean photo material template (IMG_5647.jpg)
    tpl_aud_mat = copy.deepcopy(amap[tracks[13]["segments"][29]["material_id"]])  # clean isolated vocal audio template
    tpl_aud_seg = copy.deepcopy(tracks[13]["segments"][29])
    tpl_sub_seg = copy.deepcopy(tracks[7]["segments"][35])  # Track 7 S35: "Happy Birthday / Mövenpick Resort Cam Ranh!"
    tpl_sub_mat = copy.deepcopy(tmap[tpl_sub_seg["material_id"]])
    tpl_trans = copy.deepcopy(mats["transitions"][0])

    # ==================================================================
    # EDIT 1 (Ý 4): S25 (46.00s -> 47.17s) IMG_4934.MOV — Zoom tight on hands passing envelope!
    # ==================================================================
    seg25 = t0[25]
    # Verified visually on coordinate grid: hands & white envelope sit at px=+0.10, py=-0.12
    # Zoom 2.55 -> 2.80 with transform (-0.22, +0.34) -> (-0.26, +0.38) keeps hands & envelope dead center!
    set_ken_burns(seg25, 2.55, 2.80, -0.22, 0.34, -0.26, 0.38)
    print("[1/6] Ý 4: Zoomed S25 (IMG_4934.MOV 46.00->47.17s) tight onto hands passing envelope")

    # ==================================================================
    # EDIT 2 (Ý 1): S26 (47.17s -> 61.50s) Replace IMG_4913.MOV with raw IMG_5024.MOV!
    # ==================================================================
    seg26 = t0[26]
    orig_5024_mat = copy.deepcopy(vmap[tracks[2]["segments"][0]["material_id"]])
    mat_5024_s26 = copy.deepcopy(orig_5024_mat)
    mat_5024_s26["id"] = uid()
    mat_5024_s26["crop"] = copy.deepcopy(FULL_CROP_1_1)
    mat_5024_s26["crop_ratio"] = "free"
    mat_5024_s26["crop_scale"] = 1.0
    mats["videos"].append(mat_5024_s26)
    vmap[mat_5024_s26["id"]] = mat_5024_s26

    seg26["material_id"] = mat_5024_s26["id"]
    # Trim off initial 2.60s ("Okay"), use full phone call 2.60s..17.30s (14.70s) @ 1.02558x -> exact 14.333334s!
    seg26["source_timerange"] = {"start": s2u(2.60), "duration": s2u(14.70)}
    s26_dur_us = seg26["target_timerange"]["duration"]
    s26_speed = s2u(14.70) / s26_dur_us
    set_segment_speed(seg26, s26_speed, mats)
    # Mute raw noisy lobby audio on video track (we add Demucs-cleaned Giong_hat_IMG_5024.wav on Track 13!)
    seg26["volume"] = 0.0
    seg26["last_nonzero_volume"] = 1.0
    # Confident luxury push-in framing (stays cleanly below "05 · SERVICE CENTER" title at Y=+0.59)
    set_ken_burns(seg26, 1.14, 1.24, 0.0, 0.02, 0.0, 0.03)

    # Add cleaned Demucs vocal for IMG_5024 on Track 13 right in the open gap 48.57s..61.50s (start=47.17s? No! T13 S12 ends 48.57s!)
    # Notice Track 13 S12 ends at 48.57s, S13 starts at 61.50s -> clean 48.60s..61.50s window (12.90s)!
    # At timeline 47.17s -> src=2.60s; at timeline 51.40s (= 4.23s after 47.17s) -> src = 2.60 + 4.23 * 1.0256 = 6.94s (right when child scream ends and his clear English voice begins!)
    dur_5024_wav, _, _ = probe_media(wav_5024_path)
    aud_5024_mat = copy.deepcopy(tpl_aud_mat)
    aud_5024_mat["id"] = uid()
    aud_5024_mat["type"] = "extract_music"
    aud_5024_mat["name"] = "Giọng hát_IMG_5024.MOV"
    aud_5024_mat["duration"] = dur_5024_wav
    aud_5024_mat["path"] = f"{PLACEHOLDER}/materials/audio/feedback_1125/Giong_hat_IMG_5024.wav"
    aud_5024_mat["local_material_id"] = str(uuid.uuid4())
    mats["audios"].append(aud_5024_mat)

    spd_a5024 = uid()
    mats["speeds"].append({"id": spd_a5024, "type": "speed", "mode": 0, "speed": round(s26_speed, 6), "curve_speed": None})
    ph_a5024 = uid()
    mats["placeholder_infos"].append({"id": ph_a5024, "type": "placeholder_info", "error_path": "", "error_text": "", "meta_type": "none", "res_path": "", "res_text": ""})
    bt_a5024 = uid()
    mats["beats"].append({"id": bt_a5024, "type": "beats", "ai_beats": {"beat_speed_infos": [], "beats_path": "", "beats_url": "", "melody_path": "", "melody_percents": [0.6], "melody_url": ""}, "enable_ai_beats": False, "gear": 404, "gear_count": 0, "mode": 404, "user_beats": [], "user_delete_ai_beats": None})
    scm_a5024 = uid()
    mats["sound_channel_mappings"].append({"id": scm_a5024, "type": "", "audio_channel_mapping": 0, "is_config_open": False})
    vs_a5024 = uid()
    mats["vocal_separations"].append({"id": vs_a5024, "type": "vocal_separation", "choice": 0, "production_path": "", "removed_sounds": [], "time_range": None})
    fd_a5024 = uid()
    mats["audio_fades"].append({"id": fd_a5024, "type": "audio_fade", "fade_type": 0, "fade_in_duration": 300_000, "fade_out_duration": 200_000})

    # Place synced with S26 from timeline 51.30s -> 61.50s (dur=10.20s, src = 2.60 + (51.30-47.1667)*s26_speed = 6.84s, src_dur = 10.46s)
    t_start_a5024 = s2u(51.30)
    t_dur_a5024 = s2u(61.50) - t_start_a5024
    s_start_a5024 = s2u(2.60 + (51.30 - 47.166666) * s26_speed)
    s_dur_a5024 = int(round(t_dur_a5024 * s26_speed))
    seg_a5024 = copy.deepcopy(tpl_aud_seg)
    seg_a5024["id"] = uid()
    seg_a5024["material_id"] = aud_5024_mat["id"]
    seg_a5024["target_timerange"] = {"start": t_start_a5024, "duration": t_dur_a5024}
    seg_a5024["source_timerange"] = {"start": s_start_a5024, "duration": s_dur_a5024}
    seg_a5024["speed"] = round(s26_speed, 6)
    seg_a5024["volume"] = 1.65
    seg_a5024["last_nonzero_volume"] = 1.65
    seg_a5024["common_keyframes"] = []
    seg_a5024["extra_material_refs"] = [spd_a5024, ph_a5024, bt_a5024, scm_a5024, vs_a5024, fd_a5024]
    tracks[13]["segments"].append(seg_a5024)
    tracks[13]["segments"].sort(key=lambda s: s["target_timerange"]["start"])

    # Gently lift BGM floor during 50s..61.5s from 0.26 -> 0.42 so the phone-call scene sounds full & polished
    bgm_seg = tracks[12]["segments"][0]
    for kf in bgm_seg.get("common_keyframes", []):
        if kf.get("property_type") == "KFTypeVolume":
            for pt in kf["keyframe_list"]:
                ts = pt["time_offset"] / 1e6
                if 49.8 <= ts <= 64.5 and abs(pt["values"][0] - 0.2631) < 0.05:
                    pt["values"] = [0.42]

    # Update Track 7 subtitles at 48.80s..59.87s (remove mismatched female "Sir Jeffrey..." lines,
    # add 1 clean accurate subtitle matching his clearly audible closing English line at 57.50s..60.80s!)
    old_s26_sub_ids = set()
    kept_t7 = []
    for seg in tracks[7]["segments"]:
        st = seg["target_timerange"]["start"] / 1e6
        if 48.5 <= st <= 60.5:
            old_s26_sub_ids.add(seg["material_id"])
            continue
        kept_t7.append(seg)

    # Create accurate subtitle for IMG_5024's clear closing line ("...and I will inform my colleagues / to assist you.")
    sub_5024_mat = copy.deepcopy(tpl_sub_mat)
    sub_5024_mat["id"] = uid()
    txt_5024 = "\"...and I will inform my colleagues\nto assist you.\""
    sub_5024_content = json.loads(sub_5024_mat["content"])
    # Preserve exact font/size/stroke/shadow from template style[0]
    base_st = copy.deepcopy(sub_5024_content["styles"][0])
    hl_st = copy.deepcopy(sub_5024_content["styles"][-1]) if len(sub_5024_content["styles"]) > 1 else copy.deepcopy(base_st)
    # Highlight "to assist you." in Warm Champagne Gold [1.0, 0.878, 0.510]
    idx_hl = txt_5024.find("to assist you.")
    st1 = copy.deepcopy(base_st)
    st1["range"] = [0, idx_hl]
    st1["fill"]["content"]["solid"]["color"] = [1.0, 1.0, 1.0]
    st2 = copy.deepcopy(base_st)
    st2["range"] = [idx_hl, len(txt_5024)]
    st2["fill"]["content"]["solid"]["color"] = [1.0, 0.878, 0.510]
    sub_5024_mat["content"] = json.dumps({"text": txt_5024, "styles": [st1, st2]}, ensure_ascii=False)
    sub_5024_mat["recognize_text"] = txt_5024
    sub_5024_mat["check_flag"] = 15
    sub_5024_mat["background_style"] = 0
    mats["texts"].append(sub_5024_mat)

    sub_5024_seg = copy.deepcopy(tpl_sub_seg)
    sub_5024_seg["id"] = uid()
    sub_5024_seg["material_id"] = sub_5024_mat["id"]
    sub_5024_seg["target_timerange"] = {"start": s2u(57.20), "duration": s2u(3.60)}
    # Clone animation ref cleanly
    anim_5024 = {"id": uid(), "type": "sticker_animation", "animations": [], "multi_language_current": "none"}
    mats["material_animations"].append(anim_5024)
    sub_5024_seg["extra_material_refs"] = [anim_5024["id"]]
    kept_t7.append(sub_5024_seg)
    kept_t7.sort(key=lambda s: s["target_timerange"]["start"])
    tracks[7]["segments"] = kept_t7
    mats["texts"] = [t for t in mats["texts"] if t["id"] not in old_s26_sub_ids]
    print("[2/6] Ý 1: Replaced S26 with IMG_5024.MOV + Demucs clean vocal + accurate subtitle")

    # ==================================================================
    # EDIT 3 (Ý 2): Track 2 S0 (62.33s -> 73.90s, bottom-left of 4-grid) -> IMG_5046.MOV!
    # ==================================================================
    seg_t2s0 = tracks[2]["segments"][0]
    orig_5046_mat = copy.deepcopy(vmap[t0[28]["material_id"]])
    mat_5046_grid = copy.deepcopy(orig_5046_mat)
    mat_5046_grid["id"] = uid()
    mat_5046_grid["crop"] = copy.deepcopy(FULL_CROP_1_1)
    mat_5046_grid["crop_ratio"] = "free"
    mat_5046_grid["crop_scale"] = 1.0
    mats["videos"].append(mat_5046_grid)
    vmap[mat_5046_grid["id"]] = mat_5046_grid

    dur_5046_us = mat_5046_grid["duration"]  # 10,066,666 us (10.07s)
    t2s0_dur_us = seg_t2s0["target_timerange"]["duration"]  # 11,566,667 us (11.57s)
    spd_5046 = dur_5046_us / t2s0_dur_us  # ~0.8703x smooth slow-mo!
    seg_t2s0["material_id"] = mat_5046_grid["id"]
    seg_t2s0["source_timerange"] = {"start": 0, "duration": dur_5046_us}
    set_segment_speed(seg_t2s0, spd_5046, mats)
    seg_t2s0["volume"] = 0.0  # mute so IMG_4875 live voice stays crystal clear
    seg_t2s0["last_nonzero_volume"] = 1.0
    print(f"[3/6] Ý 2: Replaced Track 2 S0 (bottom-left 4-grid) with IMG_5046.MOV @ {spd_5046:.4f}x")

    # ==================================================================
    # EDIT 4 (Bonus Nhung 11:04 "Nhớ cà mụn cho bé này nha"):
    # Point Track 0 S27 (61.50s -> 73.90s, top-left of 4-grid) to skin-retouched IMG_4913_retouched_s27.mp4!
    # ==================================================================
    seg27 = t0[27]
    dur_s27_us, w_s27, h_s27 = probe_media(s27_smooth_path)
    mat_4913_ret = copy.deepcopy(vmap[seg27["material_id"]])
    mat_4913_ret["id"] = uid()
    mat_4913_ret["material_name"] = "IMG_4913_retouched_s27.mp4"
    mat_4913_ret["path"] = f"{PLACEHOLDER}/materials/video/feedback_1125/IMG_4913_retouched_s27.mp4"
    mat_4913_ret["duration"] = dur_s27_us
    mat_4913_ret["width"] = w_s27
    mat_4913_ret["height"] = h_s27
    mat_4913_ret["local_material_id"] = str(uuid.uuid4())
    mat_4913_ret["crop"] = copy.deepcopy(FULL_CROP_1_1)
    mats["videos"].append(mat_4913_ret)
    vmap[mat_4913_ret["id"]] = mat_4913_ret

    # Retouched clip starts at 15.00s of original IMG_4913.MOV -> shift S27 source_start & keyframe time_offsets by -15.0s!
    offset_us = s2u(15.0)
    seg27["material_id"] = mat_4913_ret["id"]
    seg27["source_timerange"]["start"] = max(0, seg27["source_timerange"]["start"] - offset_us)
    for kf in seg27.get("common_keyframes", []):
        for pt in kf.get("keyframe_list", []):
            pt["time_offset"] = max(0, pt["time_offset"] - offset_us)
    print("[4/6] Bonus: Applied natural skin-retouched IMG_4913_retouched_s27.mp4 to S27 (top-left 4-grid)")

    # ==================================================================
    # EDIT 5 (Ý 3 — 1p15s): S29 (75.30s -> 76.93s) Replace IMG_4575.HEIC with HD IMG_PCCC_NEW.jpg!
    # ==================================================================
    seg29 = t0[29]
    mat_pccc = copy.deepcopy(tpl_photo_mat)
    mat_pccc["id"] = uid()
    mat_pccc["type"] = "photo"
    mat_pccc["material_name"] = "IMG_PCCC_NEW.jpg"
    mat_pccc["path"] = f"{PLACEHOLDER}/materials/video/feedback_1125/IMG_PCCC_NEW.jpg"
    mat_pccc["width"] = 1200
    mat_pccc["height"] = 1600
    mat_pccc["duration"] = 10_800_000_000  # standard CapCut 3h photo material duration
    mat_pccc["local_material_id"] = str(uuid.uuid4())
    mat_pccc["crop"] = copy.deepcopy(FULL_CROP_1_1)
    mat_pccc["crop_ratio"] = "free"
    mat_pccc["crop_scale"] = 1.0
    mats["videos"].append(mat_pccc)
    vmap[mat_pccc["id"]] = mat_pccc

    seg29["material_id"] = mat_pccc["id"]
    seg29["source_timerange"] = {"start": 0, "duration": seg29["target_timerange"]["duration"]}
    set_segment_speed(seg29, 1.0, mats)
    # Center smiling fire-suit man cleanly below "06 · FRONT OFFICE LIFE" title with 0% black bars & smooth push-in!
    set_ken_burns(seg29, 1.46, 1.54, 0.0, -0.07, 0.0, -0.09)
    print("[5/6] Ý 3: Replaced S29 (1p15s) with HD IMG_PCCC_NEW.jpg (FULL_CROP_1_1 + centered Ken Burns)")

    # ==================================================================
    # EDIT 6 (Ý 5 — Insert new Zalo 00:04 wish video into "đoạn lời chúc" at 143.47s!)
    # ==================================================================
    INSERT_AT_US = t0[50]["target_timerange"]["start"]  # 143,466,666 us (exact boundary between S49 and S50!)
    WISH_SRC_START_US = s2u(0.15)
    WISH_DUR_US = s2u(3.40)  # 0.15s -> 3.55s of 3.633s clip: captures full wish + clapping + heart hands + smile!
    SHIFT_US = WISH_DUR_US

    # 6A. Ripple-shift ALL segments & keyframes >= INSERT_AT_US - 50ms across ALL 20 tracks!
    shifted_segs = 0
    for ti, tr in enumerate(tracks):
        if ti == 12:
            # BGM Track 12: extend duration & shift finale swell keyframes in source-time!
            bgm_s = tr["segments"][0]
            bgm_spd = float(bgm_s.get("speed", 1.0))
            bgm_s["target_timerange"]["duration"] += SHIFT_US
            bgm_s["source_timerange"]["duration"] += int(round(SHIFT_US * bgm_spd))
            for kf in bgm_s.get("common_keyframes", []):
                if kf.get("property_type") == "KFTypeVolume":
                    for pt in kf["keyframe_list"]:
                        # Only shift keyframes in the finale (> 140s source time)
                        if pt["time_offset"] >= s2u(140.0):
                            pt["time_offset"] += int(round(SHIFT_US * bgm_spd))
            continue

        for seg in tr["segments"]:
            st = seg["target_timerange"]["start"]
            if st >= INSERT_AT_US - 50_000:
                seg["target_timerange"]["start"] += SHIFT_US
                shifted_segs += 1

    # 6B. Create new video material & Track 0 segment for wish_new_front_office.mp4
    dur_wish_vid, w_wish, h_wish = probe_media(wish_vid_path)
    mat_wish_vid = copy.deepcopy(tpl_vid_mat)
    mat_wish_vid["id"] = uid()
    mat_wish_vid["type"] = "video"
    mat_wish_vid["material_name"] = "wish_new_front_office.mp4"
    mat_wish_vid["path"] = f"{PLACEHOLDER}/materials/video/feedback_1125/wish_new_front_office.mp4"
    mat_wish_vid["duration"] = dur_wish_vid
    mat_wish_vid["width"] = w_wish
    mat_wish_vid["height"] = h_wish
    mat_wish_vid["local_material_id"] = str(uuid.uuid4())
    mat_wish_vid["crop"] = copy.deepcopy(FULL_CROP_1_1)
    mat_wish_vid["crop_ratio"] = "free"
    mat_wish_vid["crop_scale"] = 1.0
    mats["videos"].append(mat_wish_vid)

    # Clone S48 segment structure cleanly (neutral scale 1.0, full color/helper refs)
    seg_wish = copy.deepcopy(t0[48])
    seg_wish["id"] = uid()
    seg_wish["material_id"] = mat_wish_vid["id"]
    seg_wish["target_timerange"] = {"start": INSERT_AT_US, "duration": WISH_DUR_US}
    seg_wish["source_timerange"] = {"start": WISH_SRC_START_US, "duration": WISH_DUR_US}
    seg_wish["volume"] = 0.0  # muted on video track; clean Demucs vocal placed on Track 13 just like S37..S48!
    seg_wish["last_nonzero_volume"] = 1.0
    # Create fresh helper material refs (speed, canvas, placeholder, scm, vocal_sep) so nothing shares IDs with S48!
    spd_w = uid()
    mats["speeds"].append({"id": spd_w, "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None})
    cnv_w = uid()
    mats["canvases"].append({"id": cnv_w, "type": "canvas_color", "album_image": "", "blur": 0.0, "color": "", "image": "", "image_id": "", "image_name": "", "source_platform": 0, "team_id": ""})
    ph_w = uid()
    mats["placeholder_infos"].append({"id": ph_w, "type": "placeholder_info", "error_path": "", "error_text": "", "meta_type": "none", "res_path": "", "res_text": ""})
    scm_w = uid()
    mats["sound_channel_mappings"].append({"id": scm_w, "type": "none", "audio_channel_mapping": 0, "is_config_open": False})
    vs_w = uid()
    mats["vocal_separations"].append({"id": vs_w, "type": "vocal_separation", "choice": 0, "production_path": "", "removed_sounds": [], "time_range": None})

    # Add festive transition "Chói lòa 1" (0.33s) from our new wish into S50 Clip ghép3!
    choi_loa_path = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6726707814028284423/a3fd6266c293496fd9480884a93fb90e"
    assert os.path.exists(choi_loa_path), "Missing Chói lòa 1 transition cache"
    tr_wish_out = copy.deepcopy(tpl_trans)
    tr_wish_out["id"] = uid()
    tr_wish_out["name"] = "Chói lòa 1"
    tr_wish_out["effect_id"] = "6726707814028284423"
    tr_wish_out["resource_id"] = "6726707814028284423"
    tr_wish_out["path"] = choi_loa_path
    tr_wish_out["duration"] = s2u(0.33)
    tr_wish_out["is_overlap"] = True
    mats["transitions"].append(tr_wish_out)

    seg_wish["extra_material_refs"] = [spd_w, cnv_w, ph_w, scm_w, vs_w, tr_wish_out["id"]]
    set_ken_burns(seg_wish, 1.00, 1.07, 0.0, 0.0, 0.0, 0.0)

    # Insert into Track 0 at index 50 (right after S49, before S50 Clip ghép3!)
    t0.insert(50, seg_wish)

    # 6C. Add Demucs-cleaned wish vocal on Track 13 (matching S37..S48 style & loudness!)
    dur_wish_wav, _, _ = probe_media(wish_wav_path)
    aud_wish_mat = copy.deepcopy(tpl_aud_mat)
    aud_wish_mat["id"] = uid()
    aud_wish_mat["type"] = "extract_music"
    aud_wish_mat["name"] = "Giọng hát_wish_new_front_office.mp4"
    aud_wish_mat["duration"] = dur_wish_wav
    aud_wish_mat["path"] = f"{PLACEHOLDER}/materials/audio/feedback_1125/Giong_hat_wish_new.wav"
    aud_wish_mat["local_material_id"] = str(uuid.uuid4())
    mats["audios"].append(aud_wish_mat)

    spd_aw = uid()
    mats["speeds"].append({"id": spd_aw, "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None})
    ph_aw = uid()
    mats["placeholder_infos"].append({"id": ph_aw, "type": "placeholder_info", "error_path": "", "error_text": "", "meta_type": "none", "res_path": "", "res_text": ""})
    bt_aw = uid()
    mats["beats"].append({"id": bt_aw, "type": "beats", "ai_beats": {"beat_speed_infos": [], "beats_path": "", "beats_url": "", "melody_path": "", "melody_percents": [0.6], "melody_url": ""}, "enable_ai_beats": False, "gear": 404, "gear_count": 0, "mode": 404, "user_beats": [], "user_delete_ai_beats": None})
    scm_aw = uid()
    mats["sound_channel_mappings"].append({"id": scm_aw, "type": "", "audio_channel_mapping": 0, "is_config_open": False})
    vs_aw = uid()
    mats["vocal_separations"].append({"id": vs_aw, "type": "vocal_separation", "choice": 0, "production_path": "", "removed_sounds": [], "time_range": None})
    fd_aw = uid()
    mats["audio_fades"].append({"id": fd_aw, "type": "audio_fade", "fade_type": 0, "fade_in_duration": 33333, "fade_out_duration": 66666})

    seg_aw = copy.deepcopy(tpl_aud_seg)
    seg_aw["id"] = uid()
    seg_aw["material_id"] = aud_wish_mat["id"]
    seg_aw["target_timerange"] = {"start": INSERT_AT_US, "duration": WISH_DUR_US}
    seg_aw["source_timerange"] = {"start": WISH_SRC_START_US, "duration": WISH_DUR_US}
    seg_aw["speed"] = 1.0
    seg_aw["volume"] = 1.60  # normalized -15 LUFS vocal boosted nicely to match adjacent wishes
    seg_aw["last_nonzero_volume"] = 1.60
    seg_aw["common_keyframes"] = []
    seg_aw["extra_material_refs"] = [spd_aw, ph_aw, bt_aw, scm_aw, vs_aw, fd_aw]
    tracks[13]["segments"].append(seg_aw)
    tracks[13]["segments"].sort(key=lambda s: s["target_timerange"]["start"])

    # 6D. Add matching native Champagne Gold subtitle on Track 7 for the new wish!
    sub_w_mat = copy.deepcopy(tpl_sub_mat)
    sub_w_mat["id"] = uid()
    txt_w = "Happy Birthday\nMövenpick Resort Cam Ranh!"
    sub_w_content = json.loads(sub_w_mat["content"])
    base_ws = copy.deepcopy(sub_w_content["styles"][0])
    idx_m = txt_w.find("Mövenpick")
    ws1 = copy.deepcopy(base_ws)
    ws1["range"] = [0, idx_m]
    ws1["fill"]["content"]["solid"]["color"] = [1.0, 1.0, 1.0]
    ws2 = copy.deepcopy(base_ws)
    ws2["range"] = [idx_m, len(txt_w)]
    ws2["fill"]["content"]["solid"]["color"] = [1.0, 0.878, 0.510]
    sub_w_mat["content"] = json.dumps({"text": txt_w, "styles": [ws1, ws2]}, ensure_ascii=False)
    sub_w_mat["recognize_text"] = txt_w
    sub_w_mat["check_flag"] = 15
    sub_w_mat["background_style"] = 0
    mats["texts"].append(sub_w_mat)

    anim_w = {"id": uid(), "type": "sticker_animation", "animations": [], "multi_language_current": "none"}
    mats["material_animations"].append(anim_w)

    sub_w_seg = copy.deepcopy(tpl_sub_seg)
    sub_w_seg["id"] = uid()
    sub_w_seg["material_id"] = sub_w_mat["id"]
    sub_w_seg["target_timerange"] = {"start": INSERT_AT_US + s2u(0.15), "duration": s2u(3.10)}
    sub_w_seg["extra_material_refs"] = [anim_w["id"]]
    tracks[7]["segments"].append(sub_w_seg)
    tracks[7]["segments"].sort(key=lambda s: s["target_timerange"]["start"])

    # Update master draft duration!
    max_end = max(
        seg["target_timerange"]["start"] + seg["target_timerange"]["duration"]
        for tr in tracks
        for seg in tr["segments"]
    )
    D["duration"] = max_end
    print(f"[6/6] Ý 5: Inserted new wish clip at 143.47s (+3.40s), shifted {shifted_segs} downstream segments cleanly. New duration: {max_end/1e6:.2f}s")

    # ==================================================================
    # WRITE SYNCHRONIZED ROOT + ACTIVE SUB-TIMELINE + META + ROOT_META
    # ==================================================================
    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    pj = json.loads((DRAFT_DIR / "Timelines" / "project.json").read_text(encoding="utf-8"))
    tl_id = pj["main_timeline_id"]
    tl_sub = DRAFT_DIR / "Timelines" / tl_id

    for out_p in [
        DRAFT_DIR / "draft_content.json",
        DRAFT_DIR / "template-2.tmp",
        tl_sub / "draft_content.json",
        tl_sub / "template-2.tmp",
    ]:
        if out_p.exists():
            out_p.unlink()
        out_p.write_bytes(dc_bytes)

    mini_p = tl_sub / "attachment" / "patch" / "mini_draft.json"
    if mini_p.exists():
        mini_p.unlink()

    # Register new local assets in draft_meta_info.json + update duration & modified timestamp
    now_us = int(time.time() * 1_000_000)
    now_s = int(time.time())
    dmi_path = DRAFT_DIR / "draft_meta_info.json"
    dmi = json.loads(dmi_path.read_text(encoding="utf-8"))
    dmi["tm_draft_modified"] = now_us
    dmi["tm_duration"] = max_end

    new_meta_assets = [
        ("./materials/video/feedback_1125/IMG_PCCC_NEW.jpg", "IMG_PCCC_NEW.jpg", "photo", 0, 1200, 1600),
        ("./materials/video/feedback_1125/wish_new_front_office.mp4", "wish_new_front_office.mp4", "video", dur_wish_vid, w_wish, h_wish),
        ("./materials/video/feedback_1125/IMG_4913_retouched_s27.mp4", "IMG_4913_retouched_s27.mp4", "video", dur_s27_us, w_s27, h_s27),
        ("./materials/audio/feedback_1125/Giong_hat_wish_new.wav", "Giong_hat_wish_new.wav", "music", dur_wish_wav, 0, 0),
        ("./materials/audio/feedback_1125/Giong_hat_IMG_5024.wav", "Giong_hat_IMG_5024.wav", "music", dur_5024_wav, 0, 0),
    ]
    for blk in dmi.get("draft_materials", []):
        if blk.get("type") == 0:
            val_list = blk.setdefault("value", [])
            existing_paths = {x.get("file_Path") for x in val_list}
            for relp, fname, mtype, duru, ww, hh in new_meta_assets:
                if relp not in existing_paths:
                    val_list.append(
                        {
                            "ai_group_type": "",
                            "create_time": 0,
                            "duration": duru,
                            "enter_from": 0,
                            "extra_info": fname,
                            "file_Path": relp,
                            "height": hh,
                            "id": uid(),
                            "import_time": now_s,
                            "import_time_ms": -1,
                            "item_source": 1,
                            "material_color_tag": "",
                            "md5": "",
                            "metetype": mtype,
                            "roughcut_time_range": {"duration": -1, "start": -1},
                            "sub_time_range": {"duration": -1, "start": -1},
                            "type": 0,
                            "width": ww,
                        }
                    )
            break
    dmi_path.write_text(json.dumps(dmi, ensure_ascii=False), encoding="utf-8")

    # Update root_meta_info.json duration & timestamp for this project
    if RMI_PATH.exists():
        rmi = json.loads(RMI_PATH.read_text(encoding="utf-8"))
        for entry in rmi.get("all_draft_store", []):
            if entry.get("draft_name") == DRAFT_NAME:
                entry["tm_duration"] = max_end
                entry["tm_draft_modified"] = now_us
                break
        RMI_PATH.write_text(json.dumps(rmi, ensure_ascii=False), encoding="utf-8")

    print("\nSUCCESS! Synchronized all 4 JSON files + meta_info + root_meta_info!")


if __name__ == "__main__":
    main()
