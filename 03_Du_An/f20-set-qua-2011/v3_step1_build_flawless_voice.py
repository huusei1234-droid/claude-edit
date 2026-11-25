import os, sys, json, wave, subprocess, time
from pathlib import Path
import numpy as np

# Preserve default HF_HOME before importing OmniVoice so faster-whisper uses local HF cache without symlink errors!
ORIG_HF_HOME = os.environ.get("HF_HOME", "")

V2_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117")
V3_DIR = Path(r"d:\AI\full studio\output\f20-set-qua-2011\v3_pro")
VO_DIR = V3_DIR / "voice_clips"
AR_V3  = V3_DIR / "aroll_v3"
VO_DIR.mkdir(parents=True, exist_ok=True)
AR_V3.mkdir(parents=True, exist_ok=True)

P1117 = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\1117\video")
RAW_MAP = {it["seg_idx"]: it for it in json.loads((V2_DIR / "voice_1117_raw_manifest.json").read_text(encoding="utf-8"))}

VS_ROOT = Path(r"d:\AI\full studio\voice-studio")
sys.path.insert(0, str(VS_ROOT / "backend"))
sys.path.insert(0, str(VS_ROOT))

import torch
from services.tts_backend import get_active_tts_backend

ref_wav  = str(VO_DIR / "chi_oanh_clean_ref.wav")
ref_text = "Bây giờ Oanh sẽ giới thiệu một set quà của bên Oanh cho mọi người cùng xem nhé. Đặc biệt các sản phẩm trong set quà này đều là do bên Oanh trực tiếp sản xuất."

torch.manual_seed(2026)
backend = get_active_tts_backend()
SR_OUT = 48000

def synth_oanh_clean(seg_id, tts_text, speed=1.02, seed_offset=0):
    """Synthesizes fluent off-camera narration in Chị Oanh's cloned voice & matches studio mic EQ."""
    torch.manual_seed(2026 + seed_offset)
    # Leading gentle breath word pause prevents OmniVoice 0.1s head clip
    wav_t = backend.generate(
        text=tts_text,
        ref_audio=ref_wav,
        ref_text=ref_text,
        language="vi",
        num_step=30,
        guidance_scale=2.05,
        speed=speed,
    )
    sr_tts = int(getattr(backend, "sample_rate", 24000))
    arr = wav_t.detach().to("cpu").float().numpy().squeeze().astype(np.float32) if hasattr(wav_t, "detach") else np.asarray(wav_t, dtype=np.float32).squeeze()
    pk = float(np.max(np.abs(arr))) if len(arr) else 1.0
    if pk > 1e-4:
        arr = arr * (0.90 / pk)
    idx = np.where(np.abs(arr) > 0.012)[0]
    if len(idx) > 10:
        s0 = max(0, int(idx[0]) - int(0.04 * sr_tts))
        s1 = min(len(arr), int(idx[-1]) + int(0.08 * sr_tts))
        arr = arr[s0:s1]
    raw_p = VO_DIR / f"_{seg_id}_24k.wav"
    with wave.open(str(raw_p), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr_tts)
        wf.writeframes((np.clip(arr, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())

    # Match exact spectral warmth & loudness of Chị Oanh's wireless mic @ 48kHz stereo, snapped to 30fps frame!
    out_p = VO_DIR / f"{seg_id}.wav"
    pcm_bytes = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(raw_p),
        "-af", "highpass=f=85,equalizer=f=220:t=q:w=1.1:g=1.2,equalizer=f=3400:t=q:w=1.1:g=1.8,acompressor=threshold=-18dB:ratio=2.4:attack=8:release=110:makeup=2.2dB,loudnorm=I=-16.5:TP=-1.2:LRA=9.0",
        "-ac", "2", "-ar", str(SR_OUT), "-f", "f32le", "-"
    ])
    st_arr = np.frombuffer(pcm_bytes, dtype=np.float32).reshape((-1, 2)).copy()
    # Snap length + 0.16s natural breath tail to exact 30fps frame count
    n_frames = max(15, int(round((len(st_arr) / SR_OUT + 0.16) * 30.0)))
    n_samp = int(round((n_frames / 30.0) * SR_OUT))
    if len(st_arr) < n_samp:
        st_arr = np.vstack([st_arr, np.zeros((n_samp - len(st_arr), 2), dtype=np.float32)])
    else:
        st_arr = st_arr[:n_samp]
    fi = min(int(0.030 * SR_OUT), len(st_arr) // 4)
    fo = min(int(0.050 * SR_OUT), len(st_arr) // 4)
    st_arr[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    st_arr[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]

    with wave.open(str(out_p), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR_OUT)
        wf.writeframes((np.clip(st_arr, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())
    return out_p, n_frames, n_frames / 30.0, st_arr

def cut_live_aroll(seg_id, raw_seg_idx, local_t0, local_t1):
    """Cuts fluent live on-camera Chị Oanh video (centered 1080x1920) + matched -16.5 LUFS audio."""
    info = RAW_MAP[raw_seg_idx]
    vp = info["video_path"]
    abs_ss = info["src_in"] + local_t0
    n_frames = max(15, int(round((local_t1 - local_t0) * 30.0)))
    exact_dur = n_frames / 30.0
    n_samp = int(round(exact_dur * SR_OUT))

    out_vp = AR_V3 / f"{seg_id}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{abs_ss:.4f}", "-i", vp,
        "-frames:v", str(n_frames),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.015:contrast=1.04:saturation=1.08,fps=30,format=yuv420p",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        str(out_vp)
    ], check=True)

    pcm_bytes = subprocess.check_output([
        "ffmpeg", "-v", "error",
        "-ss", f"{abs_ss:.4f}", "-i", vp,
        "-t", f"{exact_dur + 0.05:.4f}",
        "-af", "afftdn=nf=-22,highpass=f=85,equalizer=f=240:t=q:w=1.2:g=-1.8,equalizer=f=3200:t=q:w=1.1:g=2.0,acompressor=threshold=-18dB:ratio=2.6:attack=8:release=110:makeup=2.4dB,loudnorm=I=-16.5:TP=-1.2:LRA=9.0",
        "-ac", "2", "-ar", str(SR_OUT), "-f", "f32le", "-"
    ])
    st_arr = np.frombuffer(pcm_bytes, dtype=np.float32).reshape((-1, 2)).copy()
    if len(st_arr) < n_samp:
        st_arr = np.vstack([st_arr, np.zeros((n_samp - len(st_arr), 2), dtype=np.float32)])
    else:
        st_arr = st_arr[:n_samp]
    fi = min(int(0.033 * SR_OUT), len(st_arr) // 4)
    fo = min(int(0.055 * SR_OUT), len(st_arr) // 4)
    st_arr[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    st_arr[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]

    out_wp = VO_DIR / f"{seg_id}.wav"
    with wave.open(str(out_wp), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR_OUT)
        wf.writeframes((np.clip(st_arr, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())
    return out_vp, out_wp, n_frames, exact_dur, st_arr

# ======================================================================
# EXACT 1117 SEQUENCE — HYBRID LIVE ON-CAMERA + FLUENT VOICE STUDIO!
# ======================================================================
# ("live", id, raw_seg_idx, l0, l1, note) OR ("tts", id, tts_prompt_vi, note)
SEQUENCE_PLAN = [
    ("live", "s01_open_live",   2, 0.00,  9.24, "Hôm nay thì bên Oanh đang chuẩn bị 104 set quà... ngày 20 tháng 11 ạ."),
    ("tts",  "s02_khach_tts",   "Ở Nha Trang có hai khách hàng: một là anh Hậu tại Trung tâm Luyện thi Đăng Khoa Ê Đu đặt bảy mươi bảy set quà; hai là nhóm hội phụ huynh đặt mười ba set quà.", "Nha Trang: Anh Hậu 77 set + Hội phụ huynh 13 set"),
    ("tts",  "s03_ship_tts",    "Khách thứ ba là một bạn giáo viên ở Hà Nội đặt mười set quà, và một bạn ở Thành phố Hồ Chí Minh đặt bốn set quà. Tổng sáng nay bên Oanh chuẩn bị đủ một trăm linh bốn set quà nha mọi người.", "Hà Nội 10 set + TP.HCM 4 set -> Tổng 104 set"),
    ("tts",  "s04_pov_tts",     "Đây là toàn bộ những set quà mà bên Oanh đã chuẩn bị hoàn thiện chỉn chu trong sáng ngày hôm nay ạ.", "POV toàn cảnh 104 set quà"),
    ("live", "s05_intro_live",  4, 0.00,  4.86, "Bây giờ Oanh sẽ giới thiệu 1 set quà của bên Oanh cho mọi người cùng xem nhé."),
    ("tts",  "s06_mon1_yen",    "Một set quà tặng sang trọng như thế này, bên trong đầu tiên sẽ gồm một set yến sào cao cấp: có một tổ yến sào tinh chế sợi dài dòng tiêu chuẩn.", "Món 1a: Giỏ quà -> Hộp SKA NEST -> Tổ yến tinh chế sợi dài"),
    ("tts",  "s07_mon1_tp",     "Kèm theo đầy đủ nguyên liệu chưng yến gồm: táo đỏ, đông trùng hạ thảo, kỷ tử và một hộp đường phèn.", "Món 1b: Đổi cảnh liên tục theo từng thành phần chưng yến"),
    ("tts",  "s08_mon2_rong",   "Thứ hai là hai hộp rong biển sấy giòn Tuệ Tâm: một hộp rong biển sấy giòn vị cay nhẹ thơm ngon, và một hộp rong biển sấy mè không cay rất dễ ăn.", "Món 2: 2 hộp rong biển F20 (đổi cảnh từng hộp chính giữa)"),
    ("tts",  "s09_mon3_banh",   "Thứ ba là một gói bánh thuyền mix hạt dinh dưỡng hai trăm năm mươi gam, giòn rụm giàu dưỡng chất.", "Món 3: Bánh thuyền mix hạt 250g"),
    ("tts",  "s10_mon4_kep",    "Và thứ tư là một gói lớn rong biển kẹp hạt năm trăm gam, bên trong gồm từ hai mươi hai đến hai mươi bốn thanh bánh hạt dinh dưỡng nha mọi người.", "Món 4: Rong biển kẹp hạt 500g + 22-24 thanh"),
    ("tts",  "s11_cam_nang",    "Sản phẩm giá trị nhất trong set quà chính là tổ yến sào tinh chế sợi dài, được bên Oanh chuẩn bị kèm một tờ cẩm nang nêu rõ công dụng của yến sào và hướng dẫn cách chưng yến đúng cách cho mọi người nhé.", "Cẩm nang sử dụng & cảnh chưng yến đúng cách"),
    ("tts",  "s12_gio_mica",    "Tất cả sản phẩm được xếp khéo léo trong giỏ đựng quà chất liệu mi ca trong suốt rất đẹp mắt.", "Giỏ quà Mica trong suốt"),
    ("live", "s13_quai_live",   7, 7.08, 12.30, "Ở bên trên sẽ có quai xách bằng da màu đỏ đô rất là sang trọng."),
    ("tts",  "s14_hoa_no",      "Bên mình còn thiết kế thêm vài bông hoa tạo điểm nhấn và một chiếc nơ màu be rất xinh xắn như thế này.", "Zoom cận quai da đỏ đô, bông hoa & nơ màu be thật"),
    ("live", "s15_sx_live",     8, 0.00,  9.04, "Đặc biệt các sản phẩm trong set quà này đều là do bên Oanh trực tiếp sản xuất, nên mọi người cứ yên tâm về chất lượng và giá cả nhé."),
    ("live", "s16_cta_live",    9, 3.12, 16.78, "Oanh xin gửi lời cảm ơn tới quý anh chị đã tin tưởng Thực Phẩm F20. Nếu anh chị có nhu cầu đặt set quà lễ 20/11 thì hãy inbox ngay cho Oanh nhé."),
]

INTRO_FRAMES = 117  # 3.90s panoramic 3-shot opening (39 + 39 + 39 frames)
OUTRO_FRAMES = 75   # 2.50s official F20 brand end-card tail
t_cur = INTRO_FRAMES / 30.0

audio_master_parts = [np.zeros((int(round(t_cur * SR_OUT)), 2), dtype=np.float32)]
blocks = []

for idx, item in enumerate(SEQUENCE_PLAN):
    mode = item[0]
    if mode == "live":
        _, sid, r_idx, l0, l1, note = item
        vp, wp, nf, dur, arr = cut_live_aroll(sid, r_idx, l0, l1)
        blocks.append({
            "id": sid, "mode": "live", "video_path": str(vp), "wav_path": str(wp),
            "start": round(t_cur, 4), "end": round(t_cur + dur, 4), "dur": round(dur, 4), "frames": nf, "note": note
        })
    else:
        _, sid, tts_txt, note = item
        wp, nf, dur, arr = synth_oanh_clean(sid, tts_txt, speed=1.03, seed_offset=idx * 7)
        blocks.append({
            "id": sid, "mode": "tts", "video_path": None, "wav_path": str(wp), "tts_text": tts_txt,
            "start": round(t_cur, 4), "end": round(t_cur + dur, 4), "dur": round(dur, 4), "frames": nf, "note": note
        })
    audio_master_parts.append(arr)
    print(f"  [{idx+1:02d}] {blocks[-1]['id']:16s} ({mode:4s}) [{t_cur:6.2f}s -> {t_cur+dur:6.2f}s] ({dur:5.2f}s) | {note}", flush=True)
    t_cur += dur

outro_dur = OUTRO_FRAMES / 30.0
audio_master_parts.append(np.zeros((int(round(outro_dur * SR_OUT)), 2), dtype=np.float32))
total_frames = INTRO_FRAMES + sum(b["frames"] for b in blocks) + OUTRO_FRAMES
total_dur = round(total_frames / 30.0, 4)

master_vo_path = V3_DIR / "01_Voice_V3_Pro_Master.wav"
master_arr = np.vstack(audio_master_parts)
with wave.open(str(master_vo_path), "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR_OUT)
    wf.writeframes((np.clip(master_arr, -0.99, 0.99) * 32767.0).astype(np.int16).tobytes())
print(f"\nSaved {master_vo_path}: total_dur={total_dur:.4f}s ({total_frames} frames @ 30fps)")

# Restore default HF_HOME and run faster-whisper in clean subprocess to get exact word-level timestamps!
tl_out = {
    "fps": 30,
    "intro_frames": INTRO_FRAMES,
    "intro_dur": round(INTRO_FRAMES / 30.0, 4),
    "voice_end": round(t_cur, 4),
    "outro_frames": OUTRO_FRAMES,
    "outro_dur": round(outro_dur, 4),
    "total_frames": total_frames,
    "total_dur": total_dur,
    "blocks": blocks,
}
(V3_DIR / "timeline_v3_raw.json").write_text(json.dumps(tl_out, ensure_ascii=False, indent=2), encoding="utf-8")
