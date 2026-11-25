import json, os, subprocess, wave
import numpy as np

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
VOICE_DIR = os.path.join(PROJ_DIR, "voice")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems")
FC_GOC    = r"Z:\Máy tính khác\My Computer\feel chicken\FILE GỐC"
THU_MUC   = os.path.join(FC_GOC, "16-11-2026", "Thư mục mới")
LUU_PATH  = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Lưu ngày địa chỉ lại nhé .mp4"

SR = 48000
FPS = 30.0

def cut_v3_clip(src_p, ss, dur, out_name, with_audio=False, audio_af="pan=mono|c0=c1,highpass=f=90"):
    out_p = os.path.join(AROLL_DIR, out_name)
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", src_p,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
    ]
    if with_audio:
        cmd += ["-af", audio_af, "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "256k"]
    else:
        cmd += ["-an"]
    cmd += ["-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out_p]
    subprocess.run(cmd, check=True)
    print(f"Prepared {out_name} ({dur:.3f}s)", flush=True)
    return out_p

def decode_mono_f32(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.check_output(cmd), dtype=np.float32).copy()

def apply_micro_fade(arr, fi_s=0.025, fo_s=0.040):
    out = arr.copy()
    ni = min(len(out) // 4, int(round(fi_s * SR)))
    no = min(len(out) // 4, int(round(fo_s * SR)))
    if ni > 2:
        out[:ni] *= np.linspace(0.0, 1.0, ni, dtype=np.float32)
    if no > 2:
        out[-no:] *= np.linspace(1.0, 0.0, no, dtype=np.float32)
    return out

def main():
    # 1. Re-cut tight A-rolls (fixing 00:05 excess frames, 00:28 excess frames, 00:37 full "20/11", and tight C3957 + C3471 storefront!)
    p_s1  = cut_v3_clip(os.path.join(THU_MUC, "C3938.MP4"), 3.20, 4.567, "s1_skit_v3.mp4",  with_audio=True, audio_af="pan=mono|c0=0.45*c0+0.75*c1,highpass=f=95")
    p_s2  = cut_v3_clip(os.path.join(THU_MUC, "C3942.MP4"), 2.22, 8.900, "s2_table_v3.mp4", with_audio=True, audio_af="pan=mono|c0=c1,highpass=f=90")
    p_s5  = cut_v3_clip(os.path.join(THU_MUC, "C3956.MP4"), 1.88, 8.900, "s5_gifts_v3.mp4", with_audio=True, audio_af="pan=mono|c0=c1,highpass=f=95")
    p_s6b = cut_v3_clip(os.path.join(THU_MUC, "C3957.MP4"), 1.40, 1.800, "s6b_thumbs_v3.mp4", with_audio=True, audio_af="pan=mono|c0=c1,highpass=f=95")

    # Tight C3960 voice [0.00 .. 5.88s] -> zero trailing dead frames at 00:28!
    p_s4_vo = os.path.join(AROLL_DIR, "s4_questions_vo_v3.wav")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "0.00", "-t", "5.88",
        "-i", os.path.join(FC_GOC, "16-11-2026", "C3960.MP4"),
        "-af", "pan=mono|c0=c1,highpass=f=90,loudnorm=I=-16:TP=-1.5:LRA=9",
        "-ar", "48000", "-ac", "1", p_s4_vo
    ], check=True)

    # 2. Prepare 100% Real Feel Chicken B-rolls (for Scene 3A, Scene 5 food, Scene 6A crispy chicken bites, Scene 6C storefront!)
    cut_v3_clip(LUU_PATH,                                     11.75, 2.50, "broll_luu_students.mp4")
    cut_v3_clip(os.path.join(FC_GOC, "20260603", "C9616.MP4"), 1.40, 2.50, "broll_c9616_table.mp4")
    cut_v3_clip(os.path.join(FC_GOC, "20260603", "C9604.MP4"), 1.20, 2.20, "broll_c9604_serve.mp4")
    cut_v3_clip(os.path.join(FC_GOC, "261015",   "C3490.MP4"), 1.00, 2.20, "broll_c3490_platter.mp4")
    cut_v3_clip(os.path.join(FC_GOC, "261015",   "C3492.MP4"), 0.50, 2.00, "broll_c3492_dip.mp4")
    cut_v3_clip(os.path.join(FC_GOC, "260927",   "IMG_6494.MOV"), 0.50, 2.00, "broll_img6494_pull.mp4")
    cut_v3_clip(os.path.join(FC_GOC, "260927",   "IMG_6495.MOV"), 1.30, 2.00, "broll_img6495_bite.mp4")
    cut_v3_clip(os.path.join(FC_GOC, "261015",   "C3471.MP4"), 0.00, 2.40, "broll_c3471_front.mp4")

    # 3. Build Master V3 Voiceover & Exact Word Timestamps!
    raw_w   = json.load(open(os.path.join(PROJ_DIR, "raw_word_timestamps.json"), encoding="utf-8"))
    clone_m = json.load(open(os.path.join(VOICE_DIR, "cloned_lines_meta.json"), encoding="utf-8"))

    vo_eq_real  = "highpass=f=90,lowpass=f=13500,afftdn=nf=-22,equalizer=f=3200:t=q:w=1.2:g=1.5,loudnorm=I=-15.5:TP=-1.2:LRA=8"
    vo_eq_clone = "highpass=f=85,lowpass=f=13500,equalizer=f=280:t=q:w=1.1:g=1.4,equalizer=f=3200:t=q:w=1.2:g=1.2,loudnorm=I=-15.5:TP=-1.2:LRA=8"

    def fit_frames(arr, f_cnt):
        n = int(round((f_cnt / FPS) * SR))
        return np.pad(arr, (0, max(0, n - len(arr))))[:n]

    f_s1  = 137  # 4.5667s (tight! zero extra frames at 00:05!)
    a_s1  = fit_frames(apply_micro_fade(decode_mono_f32(p_s1, af=vo_eq_real)), f_s1)

    f_s2  = 267  # 8.9000s (C3942 [2.22 .. 11.12s])
    a_s2  = fit_frames(apply_micro_fade(decode_mono_f32(p_s2, af=vo_eq_real)), f_s2)

    a_s3_core = apply_micro_fade(decode_mono_f32(clone_m["lines"]["line_prog_full"]["wav"], af=vo_eq_clone))
    a_s3_raw  = np.concatenate([np.zeros(int(0.10 * SR), np.float32), a_s3_core, np.zeros(int(0.12 * SR), np.float32)])
    f_s3  = int(round((len(a_s3_raw) / SR) * FPS))
    a_s3  = fit_frames(a_s3_raw, f_s3)

    a_s4_core = apply_micro_fade(decode_mono_f32(p_s4_vo, af=vo_eq_real))
    a_s4_raw  = np.concatenate([np.zeros(int(0.06 * SR), np.float32), a_s4_core, np.zeros(int(0.04 * SR), np.float32)])
    f_s4  = int(round((len(a_s4_raw) / SR) * FPS))  # 5.9667s (tight! zero extra frames at 00:28!)
    a_s4  = fit_frames(a_s4_raw, f_s4)

    f_s5  = 267  # 8.9000s (C3956 [1.88 .. 10.78s] -> includes 100% of "20 tháng 11"!)
    a_s5  = fit_frames(apply_micro_fade(decode_mono_f32(p_s5, af=vo_eq_real), fo_s=0.045), f_s5)

    a_s6a_core = apply_micro_fade(decode_mono_f32(clone_m["lines"]["line_outro"]["wav"], af=vo_eq_clone))
    a_s6a_raw  = np.concatenate([np.zeros(int(0.10 * SR), np.float32), a_s6a_core, np.zeros(int(0.10 * SR), np.float32)])
    f_s6a = int(round((len(a_s6a_raw) / SR) * FPS))
    a_s6a = fit_frames(a_s6a_raw, f_s6a)

    f_s6b = 54   # 1.8000s (C3957 [1.40 .. 3.20s] -> cuts IMMEDIATELY as Khang finishes "ngay thôi!")
    a_s6b = fit_frames(apply_micro_fade(decode_mono_f32(p_s6b, af=vo_eq_real), fo_s=0.035), f_s6b)

    f_s6c = 72   # 2.4000s (Real Feel Chicken Storefront Exterior shot at the end!)
    a_s6c = np.zeros(int(round((f_s6c / FPS) * SR)), dtype=np.float32)

    segments_meta = []
    cur_f = 0
    all_audio = []
    for seg_id, f_cnt, arr in [
        ("s1_skit",       f_s1,  a_s1),
        ("s2_table",      f_s2,  a_s2),
        ("s3_program",    f_s3,  a_s3),
        ("s4_questions",  f_s4,  a_s4),
        ("s5_gifts",      f_s5,  a_s5),
        ("s6a_outro",     f_s6a, a_s6a),
        ("s6b_thumbs",    f_s6b, a_s6b),
        ("s6c_storefront",f_s6c, a_s6c),
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

    vo_v3_p = os.path.join(STEMS_DIR, "01_Voice_Master_V3.wav")
    pcm16 = (np.clip(vo_stereo, -0.99, 0.99) * 32767.0).astype(np.int16)
    with wave.open(vo_v3_p, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm16.tobytes())

    s_map = {x["id"]: x for x in segments_meta}

    def shift_and_clean(words_in, base_offset, replacements):
        out = []
        i = 0
        while i < len(words_in):
            w = words_in[i]["w"]
            s = round(words_in[i]["s"] + base_offset, 3)
            e = round(words_in[i]["e"] + base_offset, 3)
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

    w_s2_src = [x for x in raw_w["C3942.MP4"] if 2.22 <= x["s"] <= 11.10]
    w_s2 = shift_and_clean(w_s2_src, s_map["s2_table"]["t0"] - 2.22, [
        (1, ["khen"], ["Khang"]),
        (3, ["rung", "cầm", "cặp"], ["rung", "cầm", "cập!"]),
        (1, ["bê"], ["ba"]),
        (2, ["luôn", "á"], ["luôn", "á!"]),
    ])

    w_s3 = shift_and_clean(clone_m["lines"]["line_prog_full"]["words"], s_map["s3_program"]["t0"] + 0.10, [
        (3, ["20", "tháng", "11"], ["20/11"]),
        (2, ["phil", "chicken"], ["Feel", "Chicken"]),
        (3, ["kiểm", "tra", "miệng"], ["KIỂM", "TRA", "MIỆNG"]),
        (3, ["trả", "lời", "đúng"], ["TRẢ", "LỜI", "ĐÚNG,"]),
        (3, ["nhận", "quà", "ngay"], ["NHẬN", "QUÀ", "NGAY!"]),
    ])

    w_s4 = shift_and_clean(raw_w["C3960.MP4"], s_map["s4_questions"]["t0"] + 0.06, [
        (1, ["lọt"], ["loạt"]),
        (2, ["lắc", "léo"], ["lắt", "léo"]),
        (1, ["phục"], ["phục!"]),
    ])

    # Include full "20 tháng 11" up to 10.62s!
    w_s5_src = [x for x in raw_w["C3956.MP4"] if 1.88 <= x["s"] <= 10.45]
    w_s5 = shift_and_clean(w_s5_src, s_map["s5_gifts"]["t0"] - 1.88, [
        (1, ["trả"], ["Trả"]),
        (1, ["còn"], ["toàn"]),
        (1, ["nha"], ["nha!"]),
        (1, ["chương"], ["Chương"]),
        (2, ["ép", "dụng"], ["áp", "dụng"]),
        (3, ["với", "chiếc", "cần"], ["Feel", "Chicken"]),
        (3, ["20", "tháng", "11"], ["20/11!"]),
    ])

    w_s6a = shift_and_clean(clone_m["lines"]["line_outro"]["words"], s_map["s6a_outro"]["t0"] + 0.10, [
        (4, ["20", "tháng", "11", "này"], ["20/11", "này!"]),
        (1, ["thức"], ["thức,"]),
        (3, ["học", "sinh", "giỏi"], ["HỌC", "SINH", "GIỎI"]),
        (1, ["nào"], ["nào!"]),
    ])

    w_s6b_src = [x for x in raw_w["C3957.MP4"] if 1.70 <= x["s"] <= 3.15]
    w_s6b = shift_and_clean(w_s6b_src, s_map["s6b_thumbs"]["t0"] - 1.40, [
        (3, ["phil", "chit", "kinh"], ["Feel", "Chicken"]),
        (1, ["thôi"], ["thôi!"]),
    ])

    tm_v3 = {
        "fps": FPS,
        "total_frames": total_frames,
        "total_dur": total_dur,
        "segments": segments_meta,
        "words": w_s2 + w_s3 + w_s4 + w_s5 + w_s6a + w_s6b,
    }
    json.dump(tm_v3, open(os.path.join(PROJ_DIR, "timeline_master_v3.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("Saved timeline_master_v3.json! Segments:", flush=True)
    for s in segments_meta:
        print(f"  {s['id']:16s}: {s['t0']:6.3f}s .. {s['t1']:6.3f}s ({s['dur']:5.3f}s, {s['f1']-s['f0']}f)", flush=True)

if __name__ == "__main__":
    main()
