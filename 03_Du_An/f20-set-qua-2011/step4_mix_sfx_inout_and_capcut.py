import copy, json, math, os, shutil, subprocess, sys, time, uuid, wave
import numpy as np

V2_DIR     = r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117"
OUT_ROOT   = r"d:\AI\full studio\output\f20-set-qua-2011"
SFX_DIR    = os.path.join(V2_DIR, "sfx_v2")
BAK_DIR    = os.path.join(OUT_ROOT, "capcut_backup")
DRAFTS_DIR = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"

DRAFT_NAME  = "F20_SetQua_2011_V2_Pro"
PLACEHOLDER = "##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##"

FONT_MONTS_ID   = "7517455788122705168"
FONT_MONTS_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7517455788122705168/91d28cfa5e7db054f4872f1ae2417ac2/Montserrat-Bold.otf"
FONT_OSWALD_ID  = "7182504807289065985"
FONT_OSWALD_PATH= "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7182504807289065985/0a5333de6f4d592cb2d2390d68b31efb/Oswald-Bold.ttf"

SR = 48000

def uid():
    return str(uuid.uuid4()).upper()

def us(sec):
    return int(round(float(sec) * 30.0) * 1_000_000 // 30)

def probe_dur_s(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def decode_stereo_f32(path, dur_limit=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if dur_limit:
        cmd += ["-t", f"{dur_limit:.4f}"]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()

def save_wav_16(path, stereo_arr):
    clipped = np.clip(stereo_arr, -0.99, 0.99)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

# ======================================================================
# 1. BUILD COMPLETE IN & OUT SFX EVENT SCHEDULE
# ======================================================================
def build_sfx_events(sub_plan):
    events = []  # (time_s, sfx_key, gain_linear, role="in"|"out")

    # A. Panoramic Opening Montage (0.00s - 4.20s)
    events.append((0.02, "riser_open",   0.28, "in"))
    events.append((0.12, "magic_reveal", 0.34, "in"))
    events.append((1.45, "whoosh_tvc",   0.26, "in"))
    events.append((2.85, "deep_swish",   0.26, "in"))
    events.append((3.82, "swoosh_out",   0.20, "out"))

    # B. All 13 Top 2-Tier Brand Headers -> Explicit IN + Explicit OUT!
    for h in sub_plan["top_headers"]:
        if h["start"] > 0.5:
            events.append((h["start"], h.get("sfx_in", "whoosh_tvc"), 0.25, "in"))
        events.append((max(0.1, h["end"] - 0.26), h.get("sfx_out", "swoosh_out"), 0.19, "out"))

    # C. Món 01/04: 4 Shimmering Crystal Bird's Nest Bubbles -> Water Bubble IN + Fairy Shimmer OUT!
    for bt in (58.85, 59.82, 61.12, 61.82):
        events.append((bt, "bubble_in", 0.34, "in"))
    events.append((61.86, "ting_quick", 0.22, "in"))
    events.append((62.66, "fairy_out",  0.28, "out"))

    # D. Món 02/04, 03/04, 04/04 Floating Callout Pills -> Pop IN + Swoosh OUT!
    for t_in, t_out, k_in in [
        (66.05, 68.42, "pop_tvc"),
        (68.70, 70.82, "pop_tvc"),
        (73.20, 76.35, "pop_tvc"),
        (82.85, 86.45, "notif_bell"),
    ]:
        events.append((t_in,  k_in,         0.24, "in"))
        events.append((t_out, "swoosh_out", 0.18, "out"))

    # E. Major Visual Cut / Camera Punch Transitions + End-Card
    for ct in (9.20, 18.20, 22.10, 28.85, 37.60, 46.80, 54.10, 90.60, 95.60, 114.60, 121.60, 129.60, 140.40):
        events.append((ct, "whoosh_pip", 0.20, "in"))
    events.append((147.58, "magic_reveal", 0.34, "in"))
    events.append((147.85, "star_sparkle", 0.28, "in"))

    # F. Subtitle Emphasis "Nhấn Nhá" Pops (IN) + Phrase Resolution Swooshes (OUT)!
    last_pop_t = -9.0
    for idx, sub in enumerate(sub_plan["subtitles"]):
        for em in sub["emphasis"]:
            tp = em["t_pop"]
            if tp - last_pop_t >= 0.42:
                sfx_k = "ting_quick" if ("104" in em["text"] or "77" in em["text"] or "F20" in em["text"] or "20/11" in em["text"]) else (
                        "pop_tvc" if em["style"] == "ruby" else "pop_soft")
                gain = 0.19 if sfx_k == "ting_quick" else 0.17
                events.append((tp, sfx_k, gain, "in"))
                last_pop_t = tp
        # Add subtle airy out-swoosh at end of key sentences (every 2nd-3rd subtitle or before pause)
        next_start = sub_plan["subtitles"][idx + 1]["start"] if idx + 1 < len(sub_plan["subtitles"]) else 149.0
        if (next_start - sub["end"] >= 0.08) or (idx % 2 == 1):
            events.append((max(0.1, sub["end"] - 0.16), "swoosh_soft", 0.13, "out"))

    events.sort(key=lambda x: x[0])
    return events

# ======================================================================
# 2. MIX & MASTER -14.0 LUFS BROADCAST AUDIO + MUX FINAL MP4
# ======================================================================
def mix_and_mux_master(tl_data, sfx_events):
    total_dur = tl_data["total_dur"]
    n_tot = int(round(total_dur * SR))

    voice = decode_stereo_f32(os.path.join(V2_DIR, "01_Voice_1117_Master.wav"), total_dur)
    if len(voice) < n_tot:
        voice = np.vstack([voice, np.zeros((n_tot - len(voice), 2), dtype=np.float32)])
    voice = voice[:n_tot]

    bgm = decode_stereo_f32(os.path.join(V2_DIR, "02_BGM_1117_Seamless.mp3"), total_dur)
    if len(bgm) < n_tot:
        bgm = np.vstack([bgm, np.zeros((n_tot - len(bgm), 2), dtype=np.float32)])
    bgm = bgm[:n_tot]

    # Smooth dynamic ducking envelope (0.52 on Panoramic Intro & End-Card, 0.25 under speech!)
    win = int(0.05 * SR)
    n_w = n_tot // win
    v_rms = np.sqrt(np.mean(voice[:n_w * win].reshape(n_w, win, 2) ** 2, axis=(1, 2)))
    speaking = (v_rms > 0.012).astype(np.float32)
    # Dilate speaking window by 0.25s ahead & 0.35s after so music ducks BEFORE syllable starts
    ker = np.ones(12, dtype=np.float32) / 12.0
    duck_u = np.clip(np.convolve(speaking, ker, mode="same") * 1.8, 0.0, 1.0)
    # Smooth envelope
    duck_u = np.convolve(duck_u, np.ones(8, dtype=np.float32) / 8.0, mode="same")
    gain_w = 0.50 * (1.0 - duck_u) + 0.24 * duck_u
    gain_sample = np.interp(np.linspace(0, n_w - 1, n_tot), np.arange(n_w), gain_w).astype(np.float32)[:, None]

    # Load normalized SFX bank
    sfx_bank = {}
    for fn in os.listdir(SFX_DIR):
        if fn.endswith(".mp3"):
            key = fn[:-4]
            arr = decode_stereo_f32(os.path.join(SFX_DIR, fn))
            pk = float(np.max(np.abs(arr))) if len(arr) else 1.0
            if pk > 1e-4:
                arr = arr / pk
            sfx_bank[key] = arr

    sfx_bus = np.zeros((n_tot, 2), dtype=np.float32)
    placed = 0
    for ts, skey, gain, role in sfx_events:
        if skey not in sfx_bank:
            continue
        sp = sfx_bank[skey]
        i0 = int(round(ts * SR))
        if i0 < 0 or i0 >= n_tot:
            continue
        i1 = min(n_tot, i0 + len(sp))
        sfx_bus[i0:i1] += sp[:i1 - i0] * float(gain)
        placed += 1
    print(f"Mixed {placed} In & Out SFX events onto stereo SFX bus!")

    raw_mix = voice * 1.18 + bgm * gain_sample + np.clip(sfx_bus, -0.65, 0.65)
    pre_wav = os.path.join(V2_DIR, "_pre_loudnorm.wav")
    save_wav_16(pre_wav, raw_mix * 0.78)

    # Broadcast -14.0 LUFS loudnorm
    master_aac = os.path.join(V2_DIR, "_master_14lufs.m4a")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", pre_wav,
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11.0",
        "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "256k",
        master_aac
    ], check=True)

    # Verify integrated LUFS
    ebur = subprocess.run(["ffmpeg", "-nostats", "-i", master_aac, "-filter_complex", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    for ln in ebur.stderr.splitlines():
        if "I:" in ln and "LUFS" in ln:
            print("Broadcast Loudness Check:", ln.strip())

    raw_vid = os.path.join(V2_DIR, "_f20_v2_video_only.mp4")
    final_local = os.path.join(V2_DIR, "F20_SET_QUA_2011_V2_FINAL.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", raw_vid, "-i", master_aac,
        "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart",
        final_local
    ], check=True)
    print("Muxed Final Master MP4:", final_local)

    # Sync Final MP4 to all 3 required destinations!
    dest_files = [
        r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\f20-set-qua-2011_FINAL.mp4",
        r"D:\XUẤT CAPCUT\F20_SET_QUA_2011_FINAL.mp4",
        r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\F20_SET_QUA_2011_FINAL.mp4",
    ]
    for dp in dest_files:
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.copy2(final_local, dp)
        print("  -> Synced MP4 to:", dp)
    return final_local

# ======================================================================
# 3. BUILD 100% PORTABLE MULTI-TRACK CAPCUT DRAFT (F20_SetQua_2011_V2_Pro)
# ======================================================================
def make_rhythm_keyframes_for_segment(seg_t0, seg_t1, zoom_beats):
    """Generates multi-point KFTypeScaleX/Y keyframes inside [seg_t0, seg_t1] synced to spoken emphasis!"""
    dur_s = seg_t1 - seg_t0
    pts = [(0.0, 1.00)]
    for z0, zp, zh, z1, pk in zoom_beats:
        # Check overlap with segment
        if z1 <= seg_t0 + 0.05 or z0 >= seg_t1 - 0.05:
            continue
        for t_abs, val in [(z0, 1.01), (zp, pk), (zh, pk), (z1, 1.01)]:
            if seg_t0 + 0.04 < t_abs < seg_t1 - 0.04:
                pts.append((round(t_abs - seg_t0, 3), round(val, 4)))
    if len(pts) == 1:
        # Gentle micro-zoom breathing so no clip is ever static
        pts.append((round(dur_s, 3), 1.05))
    else:
        pts.append((round(dur_s, 3), 1.01))
    pts.sort(key=lambda x: x[0])

    out = []
    for prop in ("KFTypeScaleX", "KFTypeScaleY"):
        klist = []
        for off_s, val in pts:
            klist.append({
                "id": uid(), "curveType": "Line", "time_offset": us(off_s),
                "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
                "values": [float(val)], "string_value": "", "graphID": ""
            })
        out.append({"id": uid(), "material_id": "", "property_type": prop, "keyframe_list": klist})
    return out

def make_linear_scale_kf(dur_us, s0, s1):
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

def build_emphasized_capcut_styles(full_text, emph_list):
    """Upgraded CapCut multi-span styles: emphasized spans get +28% larger font size, Montserrat-Bold & Gold/Ruby color!"""
    n = len(full_text)
    if n == 0:
        return []
    marks = [None] * n
    for em in emph_list:
        kw = em["text"]
        start = 0
        while True:
            idx = full_text.lower().find(kw.lower(), start)
            if idx < 0:
                break
            for k in range(idx, min(n, idx + len(kw))):
                marks[k] = em["style"]
            start = idx + len(kw)

    spans = []
    cur = marks[0]
    s_i = 0
    for i in range(1, n):
        if marks[i] != cur:
            spans.append((s_i, i, cur))
            s_i = i
            cur = marks[i]
    spans.append((s_i, n, cur))

    styles = []
    for r0, r1, st in spans:
        if st == "gold":
            col = [1.0, 0.84, 0.08]
            sz = 10.6
            f_id, f_path = FONT_MONTS_ID, FONT_MONTS_PATH
        elif st == "ruby":
            col = [1.0, 0.34, 0.45]
            sz = 10.6
            f_id, f_path = FONT_MONTS_ID, FONT_MONTS_PATH
        else:
            col = [1.0, 1.0, 1.0]
            sz = 8.2
            f_id, f_path = FONT_OSWALD_ID, FONT_OSWALD_PATH
        styles.append({
            "fill": {"content": {"render_type": "solid", "solid": {"color": col}}},
            "font": {"path": f_path, "id": f_id},
            "size": float(sz), "bold": True, "useLetterColor": True,
            "strokes": [{"content": {"render_type": "solid", "solid": {"color": [0.08, 0.04, 0.03]}}, "width": 0.09, "mode": 0}],
            "shadows": [{
                "thickness_projection_angle": -45, "thickness_projection_enable": False,
                "diffuse": 0.18, "alpha": 0.80, "distance": 6,
                "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
                "angle": -45, "thickness_projection_distance": 0
            }],
            "range": [r0, r1]
        })
    return styles

def build_portable_capcut_v2(tl_data, sub_plan, sfx_events, master_vid_only):
    stage_dir = os.path.join(V2_DIR, DRAFT_NAME)
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    vid_sub = os.path.join(stage_dir, "video")
    aud_sub = os.path.join(stage_dir, "audio")
    os.makedirs(vid_sub, exist_ok=True)
    os.makedirs(aud_sub, exist_ok=True)

    # Also slice composite showcase clips (Món 1 Full Tổ Yến + 4 Bubbles, Món 2 Twin Seaweed Jars, End-Card)
    # straight from _f20_v2_video_only.mp4? Wait: _f20_v2_video_only.mp4 has subtitles/headers baked in, so for CapCut
    # editable tracks, let's render ONLY a clean bubble-composited Bird's Nest showcase & clean End-Card clip WITHOUT subtitles,
    # while keeping all other Flow AI videos & B-rolls 100% clean raw video so CapCut native text tracks sit cleanly on top!
    from step3_render_master_v2 import ClipFrameBank, draw_birds_nest_bubbles, draw_brand_endcard
    bank = ClipFrameBank()
    vis_sched = json.load(open(os.path.join(V2_DIR, "visual_schedule_v2.json"), encoding="utf-8"))["overlays"]

    # Render clean Bird's Nest + 4 Crystal Bubbles video clip (54.10s - 63.10s = 9.00s = 270 frames, NO subtitles/headers!)
    clean_ty_bubbles = os.path.join(V2_DIR, "capcut_clean_to_yen_bubbles.mp4")
    v1_src = [ov[2] for ov in vis_sched if ov[6] == "flow_full_to_yen_bubbles"][0]
    p_ty = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", clean_ty_bubbles
    ], stdin=subprocess.PIPE)
    for fi in range(270):
        t = 54.10 + fi / 30.0
        im = bank.get_frame(v1_src, fi / 30.0, speed=0.68, zoom=1.11 + 0.04 * (fi / 270.0), crop_flow_star=True).convert("RGBA")
        draw_birds_nest_bubbles(im, t)
        p_ty.stdin.write(im.convert("RGB").tobytes())
    p_ty.stdin.close(); p_ty.wait()

    # Render clean Luxury End-Card clip (147.60s - 150.67s = 92 frames)
    clean_endcard = os.path.join(V2_DIR, "capcut_clean_endcard.mp4")
    ec_src = [ov[2] for ov in vis_sched if ov[6] == "endcard_backdrop"][0]
    from PIL import ImageFilter
    p_ec = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", clean_endcard
    ], stdin=subprocess.PIPE)
    for fi in range(92):
        t = 147.60 + fi / 30.0
        im = bank.get_frame(ec_src, fi / 30.0, speed=0.75, zoom=1.08).filter(ImageFilter.GaussianBlur(radius=14)).convert("RGBA")
        draw_brand_endcard(im, max(147.61, t))
        p_ec.stdin.write(im.convert("RGB").tobytes())
    p_ec.stdin.close(); p_ec.wait()

    orig_dc    = json.load(open(os.path.join(BAK_DIR, "draft_content.json.orig"), encoding="utf-8"))
    native_tpl = json.load(open(os.path.join(OUT_ROOT, "capcut_native_templates.json"), encoding="utf-8"))
    base_vid_mat = copy.deepcopy(orig_dc["materials"]["videos"][0])
    base_aud_mat = copy.deepcopy(orig_dc["materials"]["audios"][0])
    base_vid_seg = copy.deepcopy(orig_dc["tracks"][0]["segments"][0])
    base_aud_seg = copy.deepcopy(orig_dc["tracks"][1]["segments"][0])
    for s in (base_vid_seg, base_aud_seg):
        s["extra_material_refs"] = []
        s["common_keyframes"] = []
        s["enable_adjust"] = True
        s["visible"] = True

    dc = copy.deepcopy(orig_dc)
    dc["id"] = uid()
    dc["canvas_config"] = {"width": 1080, "height": 1920, "ratio": "9:16"}
    dc["fps"] = 30.0
    for k in list(dc["materials"].keys()):
        if isinstance(dc["materials"][k], list):
            dc["materials"][k] = []

    bundled_v = {}
    def add_vid_mat(src_p, name_hint=None):
        ap = os.path.abspath(src_p)
        if ap in bundled_v:
            return bundled_v[ap]
        bn = name_hint or os.path.basename(ap)
        dst = os.path.join(vid_sub, bn)
        if not os.path.exists(dst):
            shutil.copy2(ap, dst)
        dur_u = us(probe_dur_s(dst))
        m = copy.deepcopy(base_vid_mat)
        m["id"] = uid()
        m["path"] = f"{PLACEHOLDER}/video/{bn}".replace("\\", "/")
        m["material_name"] = bn
        m["width"] = 1080; m["height"] = 1920; m["duration"] = dur_u; m["type"] = "video"
        m["has_audio"] = False
        dc["materials"]["videos"].append(m)
        bundled_v[ap] = (m["id"], dur_u)
        return m["id"], dur_u

    bundled_a = {}
    def add_aud_mat(src_p, cat="sound"):
        ap = os.path.abspath(src_p)
        if ap in bundled_a:
            return bundled_a[ap]
        bn = os.path.basename(ap)
        dst = os.path.join(aud_sub, bn)
        if not os.path.exists(dst):
            shutil.copy2(ap, dst)
        dur_u = us(probe_dur_s(dst))
        m = copy.deepcopy(base_aud_mat)
        m["id"] = uid()
        m["path"] = f"{PLACEHOLDER}/audio/{bn}".replace("\\", "/")
        m["name"] = os.path.splitext(bn)[0]
        m["duration"] = dur_u
        m["type"] = "music" if cat == "music" else "sound"
        m["category_name"] = "local"
        dc["materials"]["audios"].append(m)
        bundled_a[ap] = (m["id"], dur_u)
        return m["id"], dur_u

    def add_spd(val=1.0):
        sp = {"curve_speed": None, "id": uid(), "mode": 0, "speed": float(val), "type": "speed"}
        dc["materials"]["speeds"].append(sp)
        return sp["id"]

    def add_fade(fi_us, fo_us):
        fd = {"fade_in_duration": int(fi_us), "fade_out_duration": int(fo_us), "id": uid(), "type": "audio_fade"}
        dc["materials"]["audio_fades"].append(fd)
        return fd["id"]

    def add_trans(idx=0):
        tr = copy.deepcopy(native_tpl["transitions"][idx % len(native_tpl["transitions"])])
        tr["id"] = uid()
        tr["duration"] = 333333
        tr["is_overlap"] = False
        dc["materials"]["transitions"].append(tr)
        return tr["id"]

    def make_vseg(src_p, t0_s, dur_s, kfs=None, trans_i=None):
        mid, mdur = add_vid_mat(src_p)
        du = us(dur_s)
        spd = 1.0
        src_du = du
        if mdur < du:
            # Slow down smoothly if source is shorter than target slot (zero missing frames!)
            spd = max(0.45, round((mdur / float(du)) * 0.96, 3))
            src_du = min(mdur, int(round(du * spd)))
        seg = copy.deepcopy(base_vid_seg)
        seg["id"] = uid()
        seg["material_id"] = mid
        seg["target_timerange"] = {"start": us(t0_s), "duration": du}
        seg["source_timerange"] = {"start": 0, "duration": src_du}
        seg["speed"] = spd
        seg["volume"] = 0.0
        seg["clip"] = {
            "alpha": 1.0, "flip": {"horizontal": False, "vertical": False},
            "rotation": 0.0, "scale": {"x": 1.0, "y": 1.0}, "transform": {"x": 0.0, "y": 0.0}
        }
        refs = [add_spd(spd)]
        if trans_i is not None:
            refs.append(add_trans(trans_i))
        seg["extra_material_refs"] = refs
        seg["common_keyframes"] = kfs or []
        return seg

    # Track 0: Main Video (3 Panoramic Intro Clips + 14 Clean 1117 A-Roll Clips with Rhythm Zoom Keyframes + Clean End-Card!)
    main_segs = []
    for i, ic in enumerate(tl_data["intro_clips"]):
        du = us(ic["dur"])
        s0, s1 = (1.00, 1.05) if i % 2 == 0 else (1.05, 1.00)
        main_segs.append(make_vseg(ic["path"], ic["start"], ic["dur"], make_linear_scale_kf(du, s0, s1), trans_i=0 if i == 2 else None))

    for i, ac in enumerate(tl_data["aroll_clips"]):
        kfs = make_rhythm_keyframes_for_segment(ac["start"], ac["end"], sub_plan["rhythm_zooms"])
        main_segs.append(make_vseg(ac["video_path"], ac["start"], ac["dur"], kfs, trans_i=(i if i in (3, 8, 11, 13) else None)))

    # Append 2.20s clean End-Card hold on Track 0 so Track 0 has zero black gap!
    main_segs.append(make_vseg(clean_endcard, tl_data["voice_end"], tl_data["outro_dur"], make_linear_scale_kf(us(tl_data["outro_dur"]), 1.00, 1.02)))

    # Track 1: B-Roll & Flow AI Product Showcases (covering 100% of speech splices!)
    broll_segs = []
    for s0, s1, vp, spd, z0, z1, tag in vis_sched:
        if tag.startswith("intro_"):
            continue
        use_p = clean_ty_bubbles if tag == "flow_full_to_yen_bubbles" else (clean_endcard if tag == "endcard_backdrop" else vp)
        du = us(s1 - s0)
        broll_segs.append(make_vseg(use_p, s0, s1 - s0, make_linear_scale_kf(du, z0, z1)))

    # Text Track 0: Upgraded Emphasized Subtitles ("Nhấn nhá" + In/Out Animations!)
    def make_tseg(txt, styles, t0_s, t1_s, pos_y, anim_i=0):
        tm = copy.deepcopy(native_tpl["text_mat"])
        tid = uid()
        tm["id"] = tid
        tm["content"] = json.dumps({"styles": styles, "text": txt}, ensure_ascii=False)
        tm["font_id"] = FONT_MONTS_ID; tm["font_path"] = FONT_MONTS_PATH
        dc["materials"]["texts"].append(tm)

        am = copy.deepcopy(native_tpl["text_anim"])
        aid = uid()
        am["id"] = aid
        anims = []
        if native_tpl.get("anim_ins"):
            ai = copy.deepcopy(native_tpl["anim_ins"][anim_i % len(native_tpl["anim_ins"])])
            ai["start"] = 0; ai["duration"] = min(233333, us((t1_s - t0_s) * 0.30))
            anims.append(ai)
        if native_tpl.get("anim_outs"):
            ao = copy.deepcopy(native_tpl["anim_outs"][0])
            du_tot = us(t1_s - t0_s)
            od = min(200000, int(du_tot * 0.25))
            ao["start"] = max(0, du_tot - od); ao["duration"] = od
            anims.append(ao)
        am["animations"] = anims
        dc["materials"]["material_animations"].append(am)

        tsg = copy.deepcopy(native_tpl["text_seg"])
        tsg["id"] = uid()
        tsg["material_id"] = tid
        tsg["target_timerange"] = {"start": us(t0_s), "duration": max(100000, us(t1_s - t0_s))}
        tsg["clip"]["transform"] = {"x": 0.0, "y": float(pos_y)}
        tsg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        tsg["extra_material_refs"] = [aid]
        tsg["common_keyframes"] = []
        return tsg

    sub_segs = []
    for i, sb in enumerate(sub_plan["subtitles"]):
        lines = [l for l in (sb["line1"], sb["line2"]) if l.strip()]
        full_t = "\n".join(lines)
        st_list = build_emphasized_capcut_styles(full_t, sb["emphasis"])
        sub_segs.append(make_tseg(full_t, st_list, sb["start"], sb["end"], pos_y=-0.62, anim_i=i))

    # Text Track 1 & 2: 2-Tier Luxury Brand Headers + Callout Pills!
    t1_segs, t2_segs = [], []
    for i, hd in enumerate(sub_plan["top_headers"]):
        st1 = build_emphasized_capcut_styles(hd["t1"], [{"text": hd["t1"], "style": "gold"}])
        t1_segs.append(make_tseg(hd["t1"], st1, hd["start"], hd["end"], pos_y=0.78, anim_i=i))
        if hd.get("t2"):
            st2 = build_emphasized_capcut_styles(hd["t2"], [])
            t2_segs.append(make_tseg(hd["t2"], st2, hd["start"] + 0.22, hd["end"], pos_y=0.69, anim_i=i+1))

    # Audio Track 0: BGM (150.67s seamless)
    bgm_mid, bgm_du = add_aud_mat(os.path.join(V2_DIR, "02_BGM_1117_Seamless.mp3"), cat="music")
    bgm_seg = copy.deepcopy(base_aud_seg)
    bgm_seg["id"] = uid(); bgm_seg["material_id"] = bgm_mid
    bgm_seg["target_timerange"] = {"start": 0, "duration": us(tl_data["total_dur"])}
    bgm_seg["source_timerange"] = {"start": 0, "duration": min(bgm_du, us(tl_data["total_dur"]))}
    bgm_seg["volume"] = 0.28
    bgm_seg["extra_material_refs"] = [add_spd(1.0), add_fade(600000, 1800000)]

    # Audio Track 1 & 2: Checkerboard Voiceover (14 clean clips with 33ms/55ms micro-fades!)
    vo_t1, vo_t2 = [], []
    for i, ac in enumerate(tl_data["aroll_clips"]):
        vmid, vdu = add_aud_mat(ac["wav_path"], cat="sound")
        du = us(ac["dur"])
        vseg = copy.deepcopy(base_aud_seg)
        vseg["id"] = uid(); vseg["material_id"] = vmid
        vseg["target_timerange"] = {"start": us(ac["start"]), "duration": du}
        vseg["source_timerange"] = {"start": 0, "duration": min(vdu, du)}
        vseg["volume"] = 1.28
        vseg["extra_material_refs"] = [add_spd(1.0), add_fade(33333, 55555)]
        (vo_t1 if i % 2 == 0 else vo_t2).append(vseg)

    # Audio Track 3 (SFX IN) & Audio Track 4 (SFX OUT) — strictly non-overlapping per track!
    sfx_in_segs, sfx_out_segs = [], []
    last_in_end, last_out_end = 0, 0
    for ts, skey, gain, role in sfx_events:
        sp = os.path.join(SFX_DIR, f"{skey}.mp3")
        if not os.path.exists(sp):
            continue
        smid, sdu = add_aud_mat(sp, cat="sound")
        st_u = us(ts)
        du_u = min(sdu, us(1.6))
        sseg = copy.deepcopy(base_aud_seg)
        sseg["id"] = uid(); sseg["material_id"] = smid
        sseg["target_timerange"] = {"start": st_u, "duration": du_u}
        sseg["source_timerange"] = {"start": 0, "duration": du_u}
        sseg["volume"] = round(min(0.85, gain * 1.9), 3)
        sseg["extra_material_refs"] = [add_spd(1.0), add_fade(15000, 45000)]
        if role == "in" and st_u >= last_in_end:
            sfx_in_segs.append(sseg)
            last_in_end = st_u + du_u + 15000
        elif role == "out" and st_u >= last_out_end:
            sfx_out_segs.append(sseg)
            last_out_end = st_u + du_u + 15000
        elif st_u >= last_out_end:
            sfx_out_segs.append(sseg)
            last_out_end = st_u + du_u + 15000

    def mk_trk(ttype, segs):
        return {"attribute": 0, "flag": 0, "id": uid(), "is_default_name": True, "name": "", "segments": segs, "type": ttype}

    dc["tracks"] = [
        mk_trk("video", main_segs),
        mk_trk("video", broll_segs),
        mk_trk("text",  sub_segs),
        mk_trk("text",  t1_segs),
        mk_trk("text",  t2_segs),
        mk_trk("audio", [bgm_seg]),
        mk_trk("audio", vo_t1),
        mk_trk("audio", vo_t2),
        mk_trk("audio", sfx_in_segs),
        mk_trk("audio", sfx_out_segs),
    ]
    tot_us = us(tl_data["total_dur"])
    dc["duration"] = tot_us

    dc_json = json.dumps(dc, ensure_ascii=False, separators=(",", ":"))
    for fn in ("draft_content.json", "draft_info.json", "template.tmp", "template-2.tmp"):
        with open(os.path.join(stage_dir, fn), "w", encoding="utf-8") as f:
            f.write(dc_json)

    # Cover & Donor Metadata (clean portable registration at #1 in CapCut!)
    shutil.copy2(os.path.join(V2_DIR, "keyframes_916", "f20-k6-gio-mica.jpg"), os.path.join(stage_dir, "draft_cover.jpg"))
    donor_dir = os.path.join(DRAFTS_DIR, "FEEL_CHICKEN_KiemTraMieng_2011_Kute")
    now_us = int(time.time() * 1_000_000)
    cap_dst = os.path.join(DRAFTS_DIR, DRAFT_NAME)

    if os.path.exists(os.path.join(donor_dir, "draft_meta_info.json")):
        dmi = json.load(open(os.path.join(donor_dir, "draft_meta_info.json"), encoding="utf-8"))
    else:
        dmi = json.load(open(os.path.join(BAK_DIR, "draft_meta_info.json.orig"), encoding="utf-8"))
    dmi["draft_id"] = dc["id"]
    dmi["draft_name"] = DRAFT_NAME
    dmi["draft_fold_path"] = cap_dst.replace("\\", "/")
    dmi["draft_root_path"] = DRAFTS_DIR
    dmi["draft_cover"] = "draft_cover.jpg"
    dmi["tm_duration"] = tot_us
    dmi["tm_draft_create"] = now_us
    dmi["tm_draft_modified"] = now_us
    dmi["draft_materials"] = [{"type": t, "value": []} for t in (0, 1, 2, 3, 6, 7, 8)]
    with open(os.path.join(stage_dir, "draft_meta_info.json"), "w", encoding="utf-8") as f:
        json.dump(dmi, f, ensure_ascii=False, separators=(",", ":"))

    for aux in ("draft_agency_config.json", "draft_biz_config.json", "draft_virtual_store.json", "key_value.json", "performance_opt_info.json"):
        sp = os.path.join(donor_dir, aux)
        if os.path.exists(sp):
            shutil.copy2(sp, os.path.join(stage_dir, aux))

    # Audit draft via capcut_pro_engine.py!
    eng_p = r"Z:\Drive của tôi\AI_Full_Studio\01_Skills\capcut-pro-editor\scripts\capcut_pro_engine.py"
    if os.path.exists(eng_p):
        aud = subprocess.run([sys.executable, eng_p, "audit", os.path.join(stage_dir, "draft_content.json")], capture_output=True, text=True)
        print("CapCut Pro Engine Audit:\n", aud.stdout.strip())

    # Copy portable draft to all 3 destinations!
    for dst_folder in [
        cap_dst,
        rf"Z:\Máy tính khác\My Computer\Document HT Media\TLH\{DRAFT_NAME}",
        rf"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-set-qua-2011\{DRAFT_NAME}",
    ]:
        if os.path.exists(dst_folder):
            shutil.rmtree(dst_folder)
        os.makedirs(os.path.dirname(dst_folder), exist_ok=True)
        shutil.copytree(stage_dir, dst_folder)
        print("  -> Deployed Portable CapCut Draft to:", dst_folder)

    # Register at #1 in root_meta_info.json
    rmi_path = os.path.join(DRAFTS_DIR, "root_meta_info.json")
    if os.path.exists(rmi_path):
        rmi = json.load(open(rmi_path, encoding="utf-8"))
        stores = [x for x in rmi.get("all_draft_store", []) if x.get("draft_name") != DRAFT_NAME]
        entry = copy.deepcopy(stores[0]) if stores else {}
        entry.update({
            "draft_cloud_last_action_download": False,
            "draft_cover": f"{cap_dst}/draft_cover.jpg".replace("\\", "/"),
            "draft_fold_path": cap_dst.replace("\\", "/"),
            "draft_id": dc["id"],
            "draft_is_invisible": False,
            "draft_json_file": f"{cap_dst}/draft_content.json".replace("\\", "/"),
            "draft_name": DRAFT_NAME,
            "draft_root_path": DRAFTS_DIR,
            "tm_draft_create": now_us,
            "tm_draft_modified": now_us + 1000,
            "tm_duration": tot_us,
        })
        rmi["all_draft_store"] = [entry] + stores
        with open(rmi_path, "w", encoding="utf-8") as f:
            json.dump(rmi, f, ensure_ascii=False, separators=(",", ":"))
        print(f"Registered {DRAFT_NAME} at #1 in CapCut Desktop!")

def main():
    tl_data  = json.load(open(os.path.join(V2_DIR, "timeline_1117_master.json"), encoding="utf-8"))
    sub_plan = json.load(open(os.path.join(V2_DIR, "subtitles_v2_plan.json"), encoding="utf-8"))
    sfx_ev   = build_sfx_events(sub_plan)
    final_mp4 = mix_and_mux_master(tl_data, sfx_ev)
    build_portable_capcut_v2(tl_data, sub_plan, sfx_ev, os.path.join(V2_DIR, "_f20_v2_video_only.mp4"))
    print("ALL DONE! Final MP4:", final_mp4)

if __name__ == "__main__":
    main()
