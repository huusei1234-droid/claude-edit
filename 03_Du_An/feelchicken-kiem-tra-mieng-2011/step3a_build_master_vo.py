import json, os, subprocess, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
VOICE_DIR = os.path.join(PROJ_DIR, "voice")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
os.makedirs(STEMS_DIR, exist_ok=True)

SR = 48000
FPS = 30.0

def decode_mono_f32(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32).copy()

def apply_micro_fade(arr, fi_s=0.035, fo_s=0.065):
    out = arr.copy()
    ni = min(len(out) // 3, int(round(fi_s * SR)))
    no = min(len(out) // 3, int(round(fo_s * SR)))
    if ni > 2:
        out[:ni] *= np.linspace(0.0, 1.0, ni, dtype=np.float32)
    if no > 2:
        out[-no:] *= np.linspace(1.0, 0.0, no, dtype=np.float32)
    return out

def snap_frames(dur_s):
    return int(round(dur_s * FPS))

# Load raw word timestamps & cloned lines metadata
raw_w = json.load(open(os.path.join(PROJ_DIR, "raw_word_timestamps.json"), encoding="utf-8"))
clone_m = json.load(open(os.path.join(VOICE_DIR, "cloned_lines_meta.json"), encoding="utf-8"))

# Prepare 6 clean voice segments normalized to consistent speech loudness (-15.5 LUFS)
vo_eq_real  = "highpass=f=90,lowpass=f=13500,afftdn=nf=-22,equalizer=f=3200:t=q:w=1.2:g=1.5,loudnorm=I=-15.5:TP=-1.2:LRA=8"
vo_eq_clone = "highpass=f=85,lowpass=f=13500,equalizer=f=280:t=q:w=1.1:g=1.4,equalizer=f=3200:t=q:w=1.2:g=1.2,loudnorm=I=-15.5:TP=-1.2:LRA=8"

# S1: Opening skit (s1_skit.mp4 = 5.00s = 150 frames, C3938 [3.20 .. 8.20s])
a_s1 = apply_micro_fade(decode_mono_f32(os.path.join(AROLL_DIR, "s1_skit.mp4"), af=vo_eq_real))
f_s1 = 150
n_s1 = int(round(f_s1 / FPS * SR))
a_s1 = np.pad(a_s1, (0, max(0, n_s1 - len(a_s1))))[:n_s1]

# S2: Anh Khang sitting at table (s2_table.mp4 = 9.04s = 271 frames, C3942 [2.12 .. 11.16s])
a_s2 = apply_micro_fade(decode_mono_f32(os.path.join(AROLL_DIR, "s2_table.mp4"), af=vo_eq_real))
f_s2 = 271
n_s2 = int(round(f_s2 / FPS * SR))
a_s2 = np.pad(a_s2, (0, max(0, n_s2 - len(a_s2))))[:n_s2]

# S3: Cloned Line 1 ("20/11 sắp tới rồi, Feel Chicken muốn đưa mọi người trở về một chút ký ức học trò với chương trình KIỂM TRA MIỆNG – TRẢ LỜI ĐÚNG, NHẬN QUÀ NGAY!")
# Add 0.14s breath before + 0.18s after
a_s3_core = apply_micro_fade(decode_mono_f32(clone_m["lines"]["line_prog_full"]["wav"], af=vo_eq_clone))
pad_pre_s3 = int(0.14 * SR)
pad_post_s3 = int(0.18 * SR)
a_s3_raw = np.concatenate([np.zeros(pad_pre_s3, dtype=np.float32), a_s3_core, np.zeros(pad_post_s3, dtype=np.float32)])
f_s3 = snap_frames(len(a_s3_raw) / SR)
n_s3 = int(round(f_s3 / FPS * SR))
a_s3 = np.pad(a_s3_raw, (0, max(0, n_s3 - len(a_s3_raw))))[:n_s3]

# S4: Real Voice ("Hàng loạt câu hỏi từ kiến thức học đường đến những câu đố mẹo siêu lắt léo đang chờ mọi người chinh phục!")
a_s4_core = apply_micro_fade(decode_mono_f32(os.path.join(AROLL_DIR, "s4_questions_vo.wav"), af=vo_eq_real))
pad_pre_s4 = int(0.10 * SR)
pad_post_s4 = int(0.18 * SR)
a_s4_raw = np.concatenate([np.zeros(pad_pre_s4, dtype=np.float32), a_s4_core, np.zeros(pad_post_s4, dtype=np.float32)])
f_s4 = snap_frames(len(a_s4_raw) / SR)
n_s4 = int(round(f_s4 / FPS * SR))
a_s4 = np.pad(a_s4_raw, (0, max(0, n_s4 - len(a_s4_raw))))[:n_s4]

# S5: Real Video + Voice ("Trả lời đúng, có quà, mà toàn là quà ngon thôi nha! Chương trình áp dụng cho tất cả mọi người khi đến với Feel Chicken từ ngày hôm nay cho đến hết ngày 20 tháng 11!")
# Trim trailing "ạ" breath cleanly at 8.70s (261 frames) so pacing stays snappy!
f_s5 = 261  # 8.70s (covers C3956 [1.86 .. 10.56s])
n_s5 = int(round(f_s5 / FPS * SR))
a_s5_full = decode_mono_f32(os.path.join(AROLL_DIR, "s5_gifts.mp4"), af=vo_eq_real)
a_s5 = apply_micro_fade(np.pad(a_s5_full, (0, max(0, n_s5 - len(a_s5_full))))[:n_s5])

# S6A: Cloned Line 2 ("20/11 này! Rủ hội bạn đến ôn lại kiến thức, xem ai còn xứng đáng danh hiệu học sinh giỏi nào!")
a_s6a_core = apply_micro_fade(decode_mono_f32(clone_m["lines"]["line_outro"]["wav"], af=vo_eq_clone))
pad_pre_s6a = int(0.12 * SR)
pad_post_s6a = int(0.14 * SR)
a_s6a_raw = np.concatenate([np.zeros(pad_pre_s6a, dtype=np.float32), a_s6a_core, np.zeros(pad_post_s6a, dtype=np.float32)])
f_s6a = snap_frames(len(a_s6a_raw) / SR)
n_s6a = int(round(f_s6a / FPS * SR))
a_s6a = np.pad(a_s6a_raw, (0, max(0, n_s6a - len(a_s6a_raw))))[:n_s6a]

# S6B: Real Anh Khang two-thumbs-up punchy tag ("Đến với Feel Chicken ngay thôi!" + 0.45s end-card tail -> 2.30s = 69 frames, holding last frame gently)
f_s6b = 69  # 2.30s
n_s6b = int(round(f_s6b / FPS * SR))
a_s6b_raw = apply_micro_fade(decode_mono_f32(os.path.join(AROLL_DIR, "s6_thumbs.mp4"), af=vo_eq_real))
a_s6b = np.pad(a_s6b_raw, (0, max(0, n_s6b - len(a_s6b_raw))))[:n_s6b]

# Concatenate full master voiceover
segments_meta = []
cur_f = 0
all_audio = []
for seg_id, f_cnt, arr in [
    ("s1_skit",      f_s1,  a_s1),
    ("s2_table",     f_s2,  a_s2),
    ("s3_program",   f_s3,  a_s3),
    ("s4_questions", f_s4,  a_s4),
    ("s5_gifts",     f_s5,  a_s5),
    ("s6a_outro",    f_s6a, a_s6a),
    ("s6b_thumbs",   f_s6b, a_s6b),
]:
    t0 = round(cur_f / FPS, 4)
    t1 = round((cur_f + f_cnt) / FPS, 4)
    segments_meta.append({"id": seg_id, "f0": cur_f, "f1": cur_f + f_cnt, "t0": t0, "t1": t1, "dur": round(f_cnt / FPS, 4)})
    cur_f += f_cnt
    all_audio.append(arr)

vo_mono = np.concatenate(all_audio)
total_frames = cur_f
total_dur = round(total_frames / FPS, 4)
target_samples = int(round(total_dur * SR))
vo_mono = np.pad(vo_mono, (0, max(0, target_samples - len(vo_mono))))[:target_samples]
vo_stereo = np.column_stack([vo_mono, vo_mono])

vo_master_p = os.path.join(STEMS_DIR, "01_Voice_Master.wav")
pcm16 = (np.clip(vo_stereo, -0.99, 0.99) * 32767.0).astype(np.int16)
with wave.open(vo_master_p, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(pcm16.tobytes())

# Build 100% spelling-verified word timeline mapped to global video time!
s_map = {x["id"]: x for x in segments_meta}

def shift_and_clean(words_in, base_offset, replacements):
    out = []
    i = 0
    while i < len(words_in):
        w = words_in[i]["w"]
        s = round(words_in[i]["s"] + base_offset, 3)
        e = round(words_in[i]["e"] + base_offset, 3)
        # Multi-word brand/spelling merges
        merged = False
        for span_len, match_seq, new_tokens in replacements:
            if i + span_len <= len(words_in):
                cand = [words_in[i + k]["w"].lower().strip(".,?!") for k in range(span_len)]
                if cand == match_seq:
                    e_end = round(words_in[i + span_len - 1]["e"] + base_offset, 3)
                    dur_sp = max(0.08, e_end - s)
                    for ti, nt in enumerate(new_tokens):
                        ts0 = round(s + dur_sp * (ti / len(new_tokens)), 3)
                        ts1 = round(s + dur_sp * ((ti + 1) / len(new_tokens)), 3)
                        out.append({"w": nt, "s": ts0, "e": ts1})
                    i += span_len
                    merged = True
                    break
        if not merged:
            out.append({"w": w, "s": s, "e": e})
            i += 1
    return out

# S2 words: C3942 cut starts at 2.12s (skip "1, 2, 3, action" < 2.15s and "Đưa cho đây" > 11.15s)
w_s2_src = [x for x in raw_w["C3942.MP4"] if 2.14 <= x["s"] <= 11.10]
w_s2 = shift_and_clean(w_s2_src, s_map["s2_table"]["t0"] - 2.12, [
    (1, ["khen"], ["Khang"]),
    (3, ["rung", "cầm", "cặp"], ["run", "cầm", "cập!"]),
    (1, ["bê"], ["ba"]),
    (2, ["luôn", "á"], ["luôn", "á!"]),
])

# S3 words: Cloned line_prog_full starts at s3.t0 + 0.14s
w_s3 = shift_and_clean(clone_m["lines"]["line_prog_full"]["words"], s_map["s3_program"]["t0"] + 0.14, [
    (3, ["20", "tháng", "11"], ["20/11"]),
    (2, ["phil", "chicken"], ["Feel", "Chicken"]),
    (3, ["kiểm", "tra", "miệng"], ["KIỂM", "TRA", "MIỆNG"]),
    (3, ["trả", "lời", "đúng"], ["TRẢ", "LỜI", "ĐÚNG,"]),
    (3, ["nhận", "quà", "ngay"], ["NHẬN", "QUÀ", "NGAY!"]),
])

# S4 words: C3960 starts at s4.t0 + 0.10s
w_s4 = shift_and_clean(raw_w["C3960.MP4"], s_map["s4_questions"]["t0"] + 0.10, [
    (1, ["lọt"], ["loạt"]),
    (2, ["lắc", "léo"], ["lắt", "léo"]),
    (1, ["phục"], ["phục!"]),
])

# S5 words: C3956 cut starts at 1.86s (keep words <= 10.40s to exclude trailing breath 'ạ')
w_s5_src = [x for x in raw_w["C3956.MP4"] if 1.88 <= x["s"] <= 10.40]
w_s5 = shift_and_clean(w_s5_src, s_map["s5_gifts"]["t0"] - 1.86, [
    (1, ["trả"], ["Trả"]),
    (1, ["còn"], ["toàn"]),
    (1, ["nha"], ["nha!"]),
    (1, ["chương"], ["Chương"]),
    (2, ["ép", "dụng"], ["áp", "dụng"]),
    (3, ["với", "chiếc", "cần"], ["Feel", "Chicken"]),
    (3, ["20", "tháng", "11"], ["20/11!"]),
])

# S6A words: Cloned line_outro starts at s6a.t0 + 0.12s
w_s6a = shift_and_clean(clone_m["lines"]["line_outro"]["words"], s_map["s6a_outro"]["t0"] + 0.12, [
    (4, ["20", "tháng", "11", "này"], ["20/11", "này!"]),
    (1, ["thức"], ["thức,"]),
    (1, ["xem"], ["xem"]),
    (3, ["học", "sinh", "giỏi"], ["HỌC", "SINH", "GIỎI"]),
    (1, ["nào"], ["nào!"]),
])

# S6B words: C3957 cut starts at 1.40s
w_s6b_src = [x for x in raw_w["C3957.MP4"] if x["s"] >= 1.42]
w_s6b = shift_and_clean(w_s6b_src, s_map["s6b_thumbs"]["t0"] - 1.40, [
    (3, ["phil", "chit", "kinh"], ["Feel", "Chicken"]),
    (1, ["thôi"], ["thôi!"]),
])

all_words = w_s2 + w_s3 + w_s4 + w_s5 + w_s6a + w_s6b

timeline = {
    "fps": FPS,
    "total_frames": total_frames,
    "total_dur": total_dur,
    "segments": segments_meta,
    "words": all_words,
}
with open(os.path.join(PROJ_DIR, "timeline_master.json"), "w", encoding="utf-8") as f:
    json.dump(timeline, f, ensure_ascii=False, indent=2)

print("=== TIMELINE MASTER BUILT ===")
for sm in segments_meta:
    print(f"  {sm['id']:14s}: frames {sm['f0']:4d}..{sm['f1']:4d} | {sm['t0']:6.2f}s .. {sm['t1']:6.2f}s (dur={sm['dur']:.2f}s)")
print(f"Total duration: {total_dur:.2f}s ({total_frames} frames), verified words: {len(all_words)}")
print("Sample cleaned transcript:", " ".join(w["w"] for w in all_words))
