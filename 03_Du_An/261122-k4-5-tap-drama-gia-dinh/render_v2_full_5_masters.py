"""
Director's Cut V2 — Full-Length Multi-Location & Wide+Crowd+CloseUp Master Renderer (`render_v2_full_5_masters.py`):
- Assembles all 5 full-length episodes (`~102s`, `~172s`, `~170s`, `~110s`, `~95s` — 100 scenes total!) interleaving
  Wide Establishing Shots (`w*`), Crowded Public Sets (`Siêu thị đông người`, `Sảnh tập đoàn đông nhân viên`, `Đám cưới đông quan khách hai họ`),
  Medium Blocking Shots, and Tight Emotional Close-Ups (`s*`).
- Uses CUDA `Demucs` (`htdemucs --two-stems=vocals`) on RTX 3060 GPU for pure speech isolation (reuses cached `s*` stems!).
- Supports `silent` visual crowd/action shots (`v02_w08`, `v03_w06`) with smooth visual pacing (`3.8s`).
- Seamlessly loops (`aloop`) 2-Act BGM tracks across full 2–3 minute runtimes with Voice Pocket EQ (`1.5kHz` & `2.8kHz` -4.2dB) so music NEVER drops out early!
- Overwrites the 5 Final MP4s in K4 Drive, Cloud Master `04_Videos_Final`, and `D:\XUẤT CAPCUT`, plus syncs V2 QA Contact Sheets.
"""
import json, os, shutil, subprocess, sys, wave
import numpy as np

BASE_DIR   = r"d:\AI\full studio\output\k4-5-videos-261122"
BGM_DIR    = os.path.join(BASE_DIR, "bgm")
DEMUCS_DIR = os.path.join(BASE_DIR, "demucs_cache")
QC_DIR     = os.path.join(BASE_DIR, "qc_sheets_v2")
ART_DIR    = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
DEMUCS_PY  = r"D:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
LUT_PATH   = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"

K4_DRIVE_DIR     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu"
MASTER_CLOUD_DIR = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR = r"D:\XUẤT CAPCUT\K4 - Mẹ Chồng Nàng Dâu"
DU_AN_CLOUD_DIR  = r"G:\My Drive\AI_Full_Studio\03_Du_An\261122-k4-5-tap-drama-gia-dinh"

os.makedirs(DEMUCS_DIR, exist_ok=True)
os.makedirs(QC_DIR, exist_ok=True)

EPISODE_V2_TIMELINES = {
    # ==================== EPISODE 1: 18 SCENES (~102s — Source: 102.7s) ====================
    "v01": {
        "title": "Mẹ chỉ có một vợ tự chọn đi",
        "shots": [
            ("w01", "voice"),  # WIDE: Hiếu walks into Khôi's house visiting Bà Mận
            ("s02", "voice"),  # CU: Hiếu asks Khôi how he takes care of mom
            ("s01", "voice"),  # MCU: Mỹ snaps 1 meal a day is lucky
            ("w02", "voice"),  # MED-WIDE: Hiếu confronts Mỹ in dining room
            ("s03", "voice"),  # CU: Khôi defends wife, says mom has no pension
            ("w03", "voice"),  # WIDE ACTION: Khôi blocks door arguing with Hiếu
            ("s04", "voice"),  # MCU: Hiếu leads Bà Mận out, cuts ties with brother
            ("w04", "voice"),  # WIDE: Hiếu's luxury apartment, Trang enters asking who came
            ("w05", "voice"),  # MED-WIDE: Trang sarcastically remarks Hiếu cooked for mom
            ("s05", "voice"),  # MCU: Trang demands mom leave tomorrow morning
            ("s06", "voice"),  # CU: Hiếu explains she is his birth mother
            ("w06", "voice"),  # WIDE: Trang stands hands-on-hips threatening to kick Bà Mận out
            ("w07", "voice"),  # CU: Hiếu snaps "Đủ rồi!"
            ("s07", "voice"),  # CU: Trang ultimatum "Mẹ đi hoặc em đi!"
            ("s08", "voice"),  # CU: Hiếu points to door "Mẹ chỉ có một!"
            ("w08", "voice"),  # WIDE CLIMAX: Hiếu points at door across living room, Trang yells back
            ("w09", "voice"),  # CU: Hiếu final rebuke "Mọi người sẽ ủng hộ tôi!"
            ("s09", "voice"),  # MCU CTA: Hiếu & Bà Mận ask audience
        ],
        "pivot_scene": "w07",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.22),
        "bgm_act2": ("dram_ltk.mp3", 0.0, 0.22),
    },

    # ==================== EPISODE 2: 26 SCENES (~172s — Source: 194.0s) ====================
    "v02": {
        "title": "Bố chồng thu thẻ lương dạy con thương vợ",
        "shots": [
            # Act 1: Garden Watering Vegetables
            ("w01", "voice"),  # WIDE GARDEN: Ông Tấn watering vegetables, Thảo approaches
            ("w02", "voice"),  # CU GARDEN: Thảo asks about mom's birthday gift & clothes
            ("w03", "voice"),  # CU GARDEN: Ông Tấn asks why not ask husband Tuấn
            ("w04", "voice"),  # WIDE GARDEN: Ông Tấn hands hose to Thảo, goes out for a walk
            ("w05", "voice"),  # MED GARDEN: Thảo waters vegetables sighing sadly
            # Act 2: Crowded Supermarket
            ("w06", "voice"),  # WIDE CROWD SUPERMARKET: Ông Tấn pushes cart among shoppers
            ("w07", "voice"),  # MED CROWD SUPERMARKET: Ông Tấn inspects premium gift box
            ("w08", "silent"), # WIDE CROWD SUPERMARKET: Ông Tấn pushes full cart happily
            # Act 3: Living Room Arrival
            ("w09", "voice"),  # WIDE LIVING ROOM: Tuấn arrives carrying bags calling Thảo
            ("s03", "voice"),  # MCU: Tuấn says gifts are for his dad, not her mom
            ("w10", "voice"),  # CU: Thảo hurt & disappointed
            ("w11", "voice"),  # WIDE 3-SHOT: Ông Tấn returns from supermarket & sits on sofa
            ("s04", "voice"),  # CU: Tuấn brags how filial he is
            ("w12", "voice"),  # MED 2-SHOT: Ông Tấn pivots "What about your wife's parents?"
            # Act 4: Full Lecture & Salary Card Confiscation
            ("s05", "voice"),  # CU: Ông Tấn "Did her parents sell their daughter?!"
            ("s06", "voice"),  # CU: Ông Tấn "3 meals a day, 365 days unpaid housework!"
            ("w13", "voice"),  # WIDE 3-SHOT: Tuấn makes excuses standing before sofa
            ("w14", "voice"),  # CU: Ông Tấn "Husband and wife are one body!"
            ("s07", "voice"),  # MCU: Ông Tấn confiscates Tuấn's salary card for Thảo!
            ("w15", "voice"),  # CU: Tuấn whines "I'm your real son, why side with an outsider?!"
            ("w16", "voice"),  # MED-WIDE CLIMAX: Ông Tấn stands up towering over Tuấn
            ("s08", "voice"),  # MCU: Filial piety to in-laws is a man's responsibility
            # Act 5: Awakening, Supermarket Gifts & Courtyard Send-off
            ("w17", "voice"),  # CU: Tuấn apologizes & promises to take Thảo home immediately
            ("w18", "voice"),  # WIDE LIVING ROOM: Ông Tấn hands all supermarket gifts + envelope to Thảo
            ("w19", "voice"),  # WIDE GARDEN PORCH: Ông Tấn waves goodbye telling them to stay 2 days
            ("s09", "voice"),  # CU CTA: Ông Tấn asks audience
        ],
        "pivot_scene": "s05",
        "bgm_act1": ("dram_quiet_tension.mp3", 2.0, 0.21),
        "bgm_act2": ("piano_warm_family.mp3", 6.0, 0.24),
    },

    # ==================== EPISODE 3: 25 SCENES (~170s — Source: 196.6s) ====================
    "v03": {
        "title": "Mẹ kế chủ tịch làm chủ cho con chồng",
        "shots": [
            # Act 1: Crowded Corporate Lobby & Security Guard Hùng
            ("w01", "voice"),  # WIDE CROWD LOBBY: Sơn & An show old photo to guard Hùng
            ("w02", "voice"),  # MED CROWD LOBBY: Guard Hùng shoves/insults poor siblings
            ("w03", "voice"),  # WIDE CROWD LOBBY: Chairwoman Cô Lan steps out scolding Hùng
            ("w04", "voice"),  # CU LOBBY: Guard Hùng bows & reports
            ("w05", "voice"),  # MED CROWD LOBBY: Cô Lan recognizes husband's youth photo
            ("w06", "silent"), # WIDE CROWD LOBBY: Cô Lan leads An & Sơn toward elevator
            # Act 2: Chairwoman Office Inquiry
            ("w07", "voice"),  # WIDE OFFICE: Cô Lan asks why they came after 20+ years
            ("s01", "voice"),  # MCU: Sơn & An explain they aren't scammers
            ("w08", "voice"),  # CU: Sơn explains divorce & sister's severe heart illness
            ("s02", "voice"),  # CU: Cô Lan calls husband & promises justice
            # Act 3: Tearful Father Reunion & 15-Year Child Support Theft
            ("w09", "voice"),  # WIDE OFFICE: Father Ông Khải rushes in grasping Sơn's shoulders
            ("s03", "voice"),  # MCU: Ông Khải weeps over construction shirt & pale An
            ("s04", "voice"),  # CU: An cries recounting stepfather & heart surgery need
            ("s05", "voice"),  # CU: Ông Khải stunned—he sent 15M every month for 15 years!
            ("w10", "voice"),  # CU: Sơn reveals ex-wife & stepfather kept every penny
            ("w11", "voice"),  # MED OFFICE: Cô Lan furious at the ex-wife's cruelty
            ("w12", "voice"),  # MED OFFICE: Ông Khải offers 20M envelope to Sơn
            ("s06", "voice"),  # CU: Sơn proudly refuses money so dad won't feel awkward
            # Act 4: Bird's Nest Porridge Doorway Stop & Grand Family Reunion
            ("w13", "voice"),  # WIDE DOORWAY: Cô Lan blocks exit holding tray of bird's-nest porridge!
            ("s07", "voice"),  # CU: Cô Lan reveals lawyer lawsuit + VIP heart surgery room!
            ("w14", "voice"),  # MED: Cô Lan gently chides husband—finding kids is greatest blessing
            ("s08", "voice"),  # MCU: "Bánh đúc có xương" — invites both kids to move in!
            ("w15", "voice"),  # WIDE REUNION: Sơn & An bow deeply in gratitude
            ("w16", "voice"),  # MED: Ông Khải holds Cô Lan's hands thanking his kind wife
            ("s09", "voice"),  # CU CTA: Cô Lan asks audience
        ],
        "pivot_scene": "w13",
        "bgm_act1": ("sad_ltk_piano.mp3", 8.0, 0.24),
        "bgm_act2": ("piano_warm_family.mp3", 10.0, 0.25),
    },

    # ==================== EPISODE 4: 16 SCENES (~110s — Source: 113.2s) ====================
    "v04": {
        "title": "Mẹ quê vượt ngàn cây số tìm con gái",
        "shots": [
            ("w01", "voice"),  # WIDE GATE: Bà Sen carrying cloth bundle arrives, Tú steps out
            ("s01", "voice"),  # MCU: Bà Sen traveled 3 days/nights looking for Lam
            ("s02", "voice"),  # CU: Tú stunned—Lam said she was an orphan at their wedding!
            ("w02", "voice"),  # MED-WIDE GATE: Checking paper address written by village girl
            ("s03", "voice"),  # CU: Bà Sen weeps—daughter was ashamed of poor rural parents
            ("w03", "voice"),  # WIDE GATE: Tú asks mother's full name & pulls out phone
            ("s04", "voice"),  # CU: Tú calls Lam ordering her home immediately!
            ("w04", "voice"),  # WIDE COURTYARD: Lam rushes in & freezes seeing her mother
            ("s05", "voice"),  # CU: Lam cries apologizing for her foolish vanity
            ("w05", "voice"),  # MED FOYER: Tú corrects himself from "Bác" to "Mẹ"!
            ("s06", "voice"),  # CU: Bà Sen explains father fell ill missing daughter
            ("w06", "voice"),  # MED-WIDE FOYER: Tú hands cash & bank card, Bà Sen hesitates
            ("s07", "voice"),  # MCU: Tú promises to bring both parents to live with them
            ("w07", "voice"),  # WIDE FOYER: Tú carries bundle & escorts mother-in-law inside
            ("w08", "voice"),  # WIDE LIVING ROOM: Seating Bà Sen on luxury sofa behind marble/wood wall
            ("s08", "voice"),  # CU CTA: Tú asks audience
        ],
        "pivot_scene": "w05",
        "bgm_act1": ("sad_ltk_piano.mp3", 5.0, 0.24),
        "bgm_act2": ("piano_warm_family.mp3", 10.0, 0.25),
    },

    # ==================== EPISODE 5: 15 SCENES (~95s — Full Crowded Wedding Drama) ====================
    "v05": {
        "title": "Đòi 2 tỷ sính lễ ngay trước cổng cưới",
        "shots": [
            ("w01", "voice"),  # WIDE CROWD WEDDING: Groom Quân walks up to white bridal car among guests
            ("w02", "voice"),  # MED CAR INTERIOR: Bride Kiều & Bridesmaid Nhung whisper inside car
            ("s01", "voice"),  # CU: Kiều demands extra 2 billion VND before stepping out
            ("s02", "voice"),  # CU: Quân shocked—500M & wedding gold already given, guests waiting
            ("w03", "voice"),  # WIDE CROWD WEDDING: Nhung blocks car door before stunned wedding crowd
            ("s03", "voice"),  # MCU: Nhung arrogantly lectures groom
            ("s04", "voice"),  # CU: Kiều counts 1-to-3 ultimatum
            ("w04", "voice"),  # MED CROWD: Quân pleads one last time to discuss after ceremony
            ("w05", "voice"),  # WIDE CROWD CAR DOOR: Kiều crosses arms refusing flatly in front of crowd
            ("s05", "voice"),  # CU TWIST: Quân smirks & flips the table!
            ("w06", "voice"),  # WIDE CROWD CLIMAX: Quân shuts car door & waves driver to turn around!
            ("s06", "voice"),  # CU: Quân cancels wedding & invites guests to celebrate dodging a bullet!
            ("w07", "voice"),  # WIDE CROWD: Kiều panics jumping out of car as Quân walks into hall
            ("s07", "voice"),  # MCU: Kiều furiously blames Nhung for ruining her rich wedding
            ("s08", "voice"),  # CU CTA: Quân asks audience
        ],
        "pivot_scene": "s05",
        "bgm_act1": ("dram_quiet_tension.mp3", 3.0, 0.22),
        "bgm_act2": ("dram_ltk.mp3", 0.0, 0.23),
    },
}

def probe_video(p):
    j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration", "-of", "json", p
    ]).decode("utf-8"))
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])

def detect_letterbox_bars(mp4_path, w, h, t_mid):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", f"{t_mid:.2f}", "-i", mp4_path,
        "-frames:v", "1", "-pix_fmt", "gray", "-f", "rawvideo", "-"
    ])
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w))
    row_means = arr.mean(axis=1)
    top_b = 0
    while top_b < h // 5 and row_means[top_b] < 16.0:
        top_b += 1
    bot_b = 0
    while bot_b < h // 5 and row_means[h - 1 - bot_b] < 16.0:
        bot_b += 1
    top_b = ((top_b + 1) // 2) * 2 if top_b >= 4 else 0
    bot_b = ((bot_b + 1) // 2) * 2 if bot_b >= 4 else 0
    return top_b, bot_b

def run_demucs_vocals(mp4_path, tag_key):
    out_wav = os.path.join(DEMUCS_DIR, f"{tag_key}_vocals.wav")
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 20_000:
        return out_wav
    raw_wav = os.path.join(DEMUCS_DIR, f"{tag_key}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4_path, "-vn", "-ac", "2", "-ar", "44100", raw_wav], check=True)
    subprocess.run([
        DEMUCS_PY, "-m", "demucs.separate",
        "-n", "htdemucs", "--two-stems=vocals", "-d", "cuda",
        "-o", DEMUCS_DIR, raw_wav
    ], check=True)
    sep_voc = os.path.join(DEMUCS_DIR, "htdemucs", tag_key, "vocals.wav")
    shutil.copy2(sep_voc, out_wav)
    return out_wav

def detect_speech_bounds(vocals_wav, total_dur, min_ss=0.06, pre_pad=0.22, post_pad=0.28):
    with wave.open(vocals_wav, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        pcm = pcm.reshape(-1, nch).mean(axis=1)
    win = int(sr * 0.025)
    nf = len(pcm) // win
    if nf < 4:
        return min_ss, max(min_ss + 2.0, total_dur - 0.08)
    rms = np.sqrt(np.mean(pcm[:nf * win].reshape(nf, win) ** 2, axis=1))
    min_idx = int(min_ss / 0.025)
    peak = float(np.max(rms[min_idx:])) if min_idx < len(rms) else float(np.max(rms))
    thr = max(0.012, peak * 0.10)
    active = np.where(rms[min_idx:] >= thr)[0] + min_idx
    if len(active) == 0:
        return min_ss, max(min_ss + 2.5, total_dur - 0.10)
    t_first = active[0] * 0.025
    t_last  = (active[-1] + 1) * 0.025
    ss = max(min_ss, t_first - pre_pad)
    to = min(total_dur - 0.04, t_last + post_pad)
    if to - ss < 2.2:
        to = min(total_dur - 0.04, ss + 2.6)
    return round(ss, 3), round(to, 3)

def deliver_episode(src_mp4, vn_title):
    fname = f"261122 K4 {vn_title} final.mp4"
    targets = [
        ("brand_path", K4_DRIVE_DIR),
        ("master_cloud_path", MASTER_CLOUD_DIR),
        ("local_path", LOCAL_CAPCUT_DIR),
    ]
    out = {"filename": fname}
    for key, tdir in targets:
        os.makedirs(tdir, exist_ok=True)
        dst = os.path.join(tdir, fname)
        shutil.copy2(src_mp4, dst)
        out[key] = dst
    print(f"  [DELIVERED FULL V2] -> {out['brand_path']}", flush=True)
    return out

def render_episode_v2(ep_id):
    meta = EPISODE_V2_TIMELINES[ep_id]
    out_w, out_h = 1080, 1920
    target_ar = 9.0 / 16.0

    ep_dir = os.path.join(BASE_DIR, ep_id)
    raw_dir = os.path.join(ep_dir, "raw_9x16")
    norm_dir = os.path.join(ep_dir, "norm_v2_9x16")
    os.makedirs(norm_dir, exist_ok=True)

    print(f"\n==================== RENDERING FULL V2 {ep_id.upper()} ({len(meta['shots'])} scenes) — {meta['title']} ====================", flush=True)
    norm_files = []
    timeline_log = []
    cum_t = 0.0
    lut_ff = LUT_PATH.replace("\\", "/").replace(":", "\\:")

    for idx, (sid, mode) in enumerate(meta["shots"], 1):
        src = os.path.join(raw_dir, f"{sid}.mp4")
        if not os.path.exists(src):
            raise FileNotFoundError(f"Missing raw clip: {src}")
        w, h, total_dur = probe_video(src)

        if mode == "voice":
            voc_wav = run_demucs_vocals(src, f"{ep_id}_9x16_{sid}")
            # Give wide shots slightly more visual breathing room before/after speech (0.32s) so audience enjoys the room & blocking!
            is_wide = sid.startswith("w")
            pre_p  = 0.34 if is_wide else 0.16
            post_p = 0.36 if is_wide else 0.24
            ss, to = detect_speech_bounds(voc_wav, total_dur, min_ss=0.06, pre_pad=pre_p, post_pad=post_p)
        else:
            ss = 0.15
            to = min(total_dur - 0.10, 4.15)

        dur = round(to - ss, 3)

        vf_parts = []
        if w == 720 and h == 1280:
            vf_parts.append("delogo=x=570:y=1130:w=62:h=62")
        top_b, bot_b = detect_letterbox_bars(src, w, h, (ss + to) * 0.5)
        ch_crop = h - top_b - bot_b
        cw_crop, cx_crop, cy_crop = w, 0, top_b
        cur_ar = cw_crop / float(max(1, ch_crop))
        if abs(cur_ar - target_ar) > 0.015:
            if cur_ar > target_ar:
                cw_crop = int(round(ch_crop * target_ar / 2) * 2)
                cx_crop = (w - cw_crop) // 2
            else:
                new_ch = int(round(cw_crop / target_ar / 2) * 2)
                cy_crop = top_b + (ch_crop - new_ch) // 2
                ch_crop = new_ch
        if cw_crop != w or ch_crop != h or cx_crop != 0 or cy_crop != 0:
            vf_parts.append(f"crop={cw_crop}:{ch_crop}:{cx_crop}:{cy_crop}")

        if os.path.exists(LUT_PATH):
            vf_parts.append(f"lut3d=file='{lut_ff}':interp=tetrahedral")
        vf_parts += [
            f"scale={out_w}:{out_h}:flags=lanczos",
            "eq=contrast=1.02:saturation=1.04",
            "unsharp=3:3:0.30:3:3:0.0",
            "fps=30",
            "format=yuv420p",
        ]
        vf = ",".join(vf_parts)

        dst = os.path.join(norm_dir, f"{idx:02d}_{sid}.mp4")
        fo_st = max(0.05, dur - 0.05)
        if mode == "voice":
            voc_wav = run_demucs_vocals(src, f"{ep_id}_9x16_{sid}")
            af = (
                f"highpass=f=85,lowpass=f=13500,"
                f"loudnorm=I=-14.5:TP=-1.2:LRA=7,"
                f"afade=t=in:st=0:d=0.04,afade=t=out:st={fo_st:.3f}:d=0.05"
            )
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", src,
                "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", voc_wav,
                "-vf", vf, "-af", af, "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", dst
            ], check=True)
        else:
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", src,
                "-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
                "-vf", vf, "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", dst
            ], check=True)

        _, _, real_d = probe_video(dst)
        timeline_log.append({"scene": sid, "start": round(cum_t, 2), "end": round(cum_t + real_d, 2), "dur": round(real_d, 2)})
        print(f"  [{idx:02d}_{sid}] {cum_t:6.2f}s -> {cum_t + real_d:6.2f}s ({real_d:.2f}s)", flush=True)
        cum_t += real_d
        norm_files.append(dst)

    concat_txt = os.path.join(ep_dir, "concat_v2_9x16.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for nf in norm_files:
            cf.write(f"file '{nf}'\n")

    vo_master = os.path.join(ep_dir, "vo_master_v2_9x16.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", vo_master], check=True)
    _, _, vid_total = probe_video(vo_master)

    # Locate pivot timestamp
    pivot_t = vid_total * 0.55
    for item in timeline_log:
        if item["scene"] == meta["pivot_scene"]:
            pivot_t = item["start"]
            break
    outro_fo = max(1.0, vid_total - 2.2)

    b1_fn, b1_off, b1_vol = meta["bgm_act1"]
    b2_fn, b2_off, b2_vol = meta["bgm_act2"]
    b1_path = os.path.join(BGM_DIR, b1_fn)
    b2_path = os.path.join(BGM_DIR, b2_fn)

    b1_len = max(4.0, pivot_t + 1.0)
    b2_start = max(0.0, pivot_t - 0.4)
    b2_delay_ms = int(round(b2_start * 1000))
    b2_len = max(4.0, vid_total - b2_start + 1.0)

    # Seamless loop (-stream_loop -1) so 2–3 minute episodes have continuous uninterrupted BGM!
    fc_bgm = (
        f"[1:a]atrim={b1_off:.2f}:{b1_off + b1_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume={b1_vol:.2f},afade=t=in:st=0:d=0.6,afade=t=out:st={max(0.5, b1_len - 1.5):.3f}:d=1.5[b1];"
        f"[2:a]atrim={b2_off:.2f}:{b2_off + b2_len:.3f},asetpts=PTS-STARTPTS,"
        f"volume={b2_vol:.2f},afade=t=in:st=0:d=1.2,adelay={b2_delay_ms}|{b2_delay_ms}[b2];"
        f"[b1][b2]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"
        f"atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,"
        f"highpass=f=95,lowpass=f=9500,"
        f"equalizer=f=1500:t=q:w=1.2:g=-4.2,equalizer=f=2800:t=q:w=1.2:g=-4.2,"
        f"afade=t=out:st={outro_fo:.3f}:d=2.0[bgm_clean];"
        f"[0:a][bgm_clean]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.93[aout]"
    )

    final_local = os.path.join(ep_dir, f"261122 K4 {meta['title']} v2 final.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", vo_master,
        "-stream_loop", "-1", "-i", b1_path,
        "-stream_loop", "-1", "-i", b2_path,
        "-filter_complex", fc_bgm, "-map", "0:v:0", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "224k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", final_local
    ], check=True)

    # Build multi-column QA Contact Sheet showing all 15-26 scenes (Wide + Crowd + Close-Up interleaved!)
    cols = 5 if len(norm_files) >= 18 else 4
    tw, th = 216, 384
    thumbs = []
    for i, nf in enumerate(norm_files, 1):
        _, _, d = probe_video(nf)
        t = os.path.join(QC_DIR, f"{ep_id}_s{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{d*0.50:.2f}", "-i", nf, "-vf", f"scale={tw}:{th}", "-frames:v", "1", t], check=True)
        thumbs.append(t)
    rows = (len(thumbs) + cols - 1) // cols
    while len(thumbs) < cols * rows:
        pad_t = os.path.join(QC_DIR, f"{ep_id}_pad{len(thumbs)}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x14161c:s={tw}x{th}", "-frames:v", "1", pad_t], check=True)
        thumbs.append(pad_t)
    inp = []
    for t in thumbs:
        inp += ["-i", t]
    layout = "|".join(f"{(i%cols)*tw}_{(i//cols)*th}" for i in range(len(thumbs)))
    qa_sheet = os.path.join(QC_DIR, f"QA_V2_{ep_id}_9x16.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", f"xstack=inputs={len(thumbs)}:layout={layout}", "-frames:v", "1", qa_sheet], check=True)
    shutil.copy2(qa_sheet, os.path.join(ART_DIR, f"QA_V2_{ep_id}_9x16.jpg"))

    delivered = deliver_episode(final_local, meta["title"])
    print(f"=== {ep_id.upper()} V2 MASTER COMPLETE: {vid_total:.2f}s ({len(norm_files)} scenes) ===", flush=True)
    return {
        "episode": ep_id,
        "scenes_count": len(norm_files),
        "duration": round(vid_total, 2),
        "qa_sheet": qa_sheet,
        **delivered,
    }

if __name__ == "__main__":
    eps = sys.argv[1:] if len(sys.argv) > 1 else ["v01", "v02", "v03", "v04", "v05"]
    out = [render_episode_v2(ep) for ep in eps]
    rep = os.path.join(BASE_DIR, "delivery_v2_full_report.json")
    json.dump(out, open(rep, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if os.path.isdir(r"G:\My Drive\AI_Full_Studio\03_Du_An"):
        os.makedirs(DU_AN_CLOUD_DIR, exist_ok=True)
        for fn in ["build_v2_full_director_batches.py", "render_v2_full_5_masters.py", "delivery_v2_full_report.json"]:
            sp = os.path.join(BASE_DIR, fn)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(DU_AN_CLOUD_DIR, fn))
        for qfn in os.listdir(QC_DIR):
            if qfn.startswith("QA_V2_"):
                shutil.copy2(os.path.join(QC_DIR, qfn), os.path.join(DU_AN_CLOUD_DIR, qfn))
    print("ALL V2 FULL-LENGTH EPISODES DELIVERED!", flush=True)
