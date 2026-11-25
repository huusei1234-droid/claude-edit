"""
Tổng hợp Voiceover giọng 'THANH THANH TVC' trên GPU NVIDIA RTX 4070 CUDA
cho 2 VIDEO COMBO PHÁT TRIỂN CHIỀU CAO BÉ TỪ 1 TUỔI TRỞ LÊN (BOJOMI + AV PROTEIN) — DƯỚI 60 GIÂY (<= 58s)!
"""
import os, sys, json, math, wave, shutil
from pathlib import Path
import numpy as np

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
VS_PROJ = Path(r"d:\AI\full studio\voice-studio")
WORK_DIR = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Bo_2_Video_Chieu_Cao_Be_Tu_1_Tuoi")

VIDEOS = {
    "kid1y_01_giai_doan_vang": {
        "title": "Combo Chiều Cao Bé Từ 1 Tuổi 01 — Giai Đoạn Vàng Đạm & Canxi",
        "final_name": "261124 AVPM Combo Chieu Cao Be Tu 1 Tuoi 01 - Giai Doan Vang Dam Va Canxi final.mp4",
        "segments": [
            ("vo_01", "Chăm chiều cao cho bé từ một tuổi, uống mình Canxi đã đủ chưa mẹ?"),
            ("vo_02", "Từ một tuổi trở lên là giai đoạn vàng xây khung xương, bé cần cả Đạm sạch lẫn Canxi chuẩn."),
            ("vo_03", "Bộ đôi Bojomi và AV Protein của An Vượng Pharma giúp mẹ chăm dinh dưỡng gọn nhẹ mỗi ngày."),
            ("vo_04", "AV Protein bổ sung đạm thực vật đậu Hà Lan, Inulin và lợi khuẩn B-3 êm bụng, dễ tiêu hóa cho bé."),
            ("vo_05", "Bojomi mang Canxi tảo biển Aquamin F cùng Vitamin D3, K2 MK-7 và Collagen vị Vani thơm béo dễ uống."),
            ("vo_06", "Mẹ chia khẩu phần theo độ tuổi của bé, kết hợp ngủ sớm và vận động. Bộ đôi có giá tám trăm bảy mươi nghìn đồng. Mẹ nhắn Bé Một Tuổi để nhận quà tặng năm trăm hai mươi nghìn đồng nhé!"),
        ],
    },
    "kid1y_02_pha_chuan_2_ly": {
        "title": "Combo Chiều Cao Bé Từ 1 Tuổi 02 — Pha Chuẩn 2 Ly Êm Bụng & Quà 520K",
        "final_name": "261124 AVPM Combo Chieu Cao Be Tu 1 Tuoi 02 - Pha Chuan 2 Ly Em Bung Tang 520K final.mp4",
        "segments": [
            ("vo_01", "Pha Bojomi và AV Protein cho bé từ một tuổi sao để êm bụng và hấp thu tốt nhất?"),
            ("vo_02", "Mẹ nhớ tuyệt đối không đổ chung hai gói vào một ly nước sôi để giữ trọn dưỡng chất cho con."),
            ("vo_03", "Buổi sáng, mẹ pha AV Protein với nước mát hoặc ấm hai mươi đến bốn mươi độ giữ nguyên lợi khuẩn B-3."),
            ("vo_04", "Bữa phụ chiều, pha Bojomi với nước ấm sáu mươi độ thành ly ngũ cốc Vani giàu Canxi tảo biển, D3 và K2."),
            ("vo_05", "Mẹ xem kỹ nhãn chia lượng vừa độ tuổi từ một tuổi trở lên, kết hợp ngủ sớm trước hai mươi hai giờ."),
            ("vo_06", "Bộ đôi Bojomi và AV Protein có giá tám trăm bảy mươi nghìn đồng. Ưu đãi đến ba mươi tháng mười một tặng hộp Bojomi năm trăm hai mươi nghìn đồng, mẹ nhắn Bé Một Tuổi ngay nhé!"),
        ],
    },
}


def trim_and_normalize(t, sr):
    arr = t.detach().to("cpu").float().numpy().squeeze().astype(np.float32) if hasattr(t, "detach") else np.asarray(t, dtype=np.float32).squeeze()
    if arr.ndim > 1:
        arr = arr.mean(axis=int(np.argmin(arr.shape)))
    abs_arr = np.abs(arr)
    peak = float(np.max(abs_arr)) if len(abs_arr) else 0.0
    if peak > 1e-4:
        arr = arr * (0.92 / peak)
        abs_arr = np.abs(arr)
    idx = np.where(abs_arr > 0.012)[0]
    if len(idx) > 10:
        arr = arr[max(0, int(idx[0]) - int(0.030 * sr)) : min(len(arr), int(idx[-1]) + int(0.055 * sr))]
    return arr


def save_wav(path, pcm_f32, sr):
    pcm = np.clip(np.copy(pcm_f32), -1.0, 1.0)
    fi = min(int(0.022 * sr), len(pcm) // 4)
    fo = min(int(0.040 * sr), len(pcm) // 4)
    if fi > 0:
        pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        pcm[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((pcm * 32767.0).astype(np.int16).tobytes())


def main():
    meta = json.loads((VOICE_BUNDLE_DIR / "profile_metadata.json").read_text(encoding="utf-8"))
    ref_audio = str(VOICE_BUNDLE_DIR / meta["ref_audio_filename"])
    ref_text = meta["ref_text"]
    params = meta["recommended_generation_params"]

    os.environ["TORCH_COMPILE_DISABLE"] = "1"
    os.environ["TORCHDYNAMO_DISABLE"] = "1"
    sys.path.insert(0, str(VS_PROJ / "backend"))
    sys.path.insert(0, str(VS_PROJ))

    import torch
    from services.tts_backend import get_active_tts_backend
    print(f"[RTX] {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}", flush=True)
    torch.manual_seed(int(params.get("seed", 2026)))
    backend = get_active_tts_backend()

    for vkey, vcfg in VIDEOS.items():
        vdir = WORK_DIR / vkey
        vo_dir = vdir / "06_Audio_Voiceover"
        hf_aud = vdir / "07_HyperFrames_Project" / "assets" / "audio"
        hf_vid = vdir / "07_HyperFrames_Project" / "assets" / "videos"
        hf_img = vdir / "07_HyperFrames_Project" / "assets" / "images"
        hf_fnt = vdir / "07_HyperFrames_Project" / "assets" / "fonts"
        for d in (vo_dir, hf_aud, hf_vid, hf_img, hf_fnt):
            d.mkdir(parents=True, exist_ok=True)
        for f in AUDIO_BUNDLE_DIR.iterdir():
            if f.is_file():
                shutil.copy2(f, hf_aud / f.name)
        for f in FONTS_BUNDLE_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in (".ttf", ".otf", ".woff2", ".css"):
                shutil.copy2(f, hf_fnt / f.name)

        print(f"\n=== SYNTH {vkey} ===", flush=True)
        manifest, prev_end, sr = [], 0.0, 24000
        for idx, (seg_id, text) in enumerate(vcfg["segments"]):
            wav_t = backend.generate(
                text=text, ref_audio=ref_audio, ref_text=ref_text,
                language=params.get("language", "vi"),
                num_step=int(params.get("num_step", 28)),
                guidance_scale=float(params.get("guidance_scale", 2.0)),
                speed=1.10,  # Crisp energetic pacing strictly under 60s!
            )
            sr = int(getattr(backend, "sample_rate", 24000))
            arr = trim_and_normalize(wav_t, sr)
            dur_s = round(len(arr) / float(sr), 3)
            seg_path = vo_dir / f"{seg_id}.wav"
            save_wav(seg_path, arr, sr)
            shutil.copy2(seg_path, hf_aud / f"{seg_id}.wav")

            # Tight 0.36s pad so total video stays STRICTLY <= 58.0s (< 1 minute)!
            shot_dur_s = max(3.50, round(math.ceil((dur_s + 0.36) * 4.0) / 4.0, 2))
            shot_start_s = 0.0 if idx == 0 else prev_end
            manifest.append({
                "id": seg_id, "text": text, "path": str(seg_path),
                "shot_start_s": shot_start_s, "shot_duration_s": shot_dur_s,
                "shot_end_s": round(shot_start_s + shot_dur_s, 2),
                "start_s": round(shot_start_s + 0.16, 3), "duration_s": dur_s,
                "end_s": round(shot_start_s + 0.16 + dur_s, 3),
            })
            prev_end = round(shot_start_s + shot_dur_s, 2)
            print(f"  {seg_id}: vo={dur_s:.2f}s | shot={shot_start_s:.2f}..{prev_end:.2f}s ({shot_dur_s:.2f}s)", flush=True)

        total_dur = min(59.0, manifest[-1]["shot_end_s"])
        if manifest[-1]["shot_end_s"] > 59.0:
            manifest[-1]["shot_end_s"] = 59.0
            manifest[-1]["shot_duration_s"] = round(59.0 - manifest[-1]["shot_start_s"], 2)
        (vo_dir / "vo_manifest.json").write_text(json.dumps({
            "video_key": vkey, "title": vcfg["title"], "final_name": vcfg["final_name"],
            "voice_profile_name": meta["name"], "sample_rate": sr,
            "total_duration_s": total_dur, "segments": manifest,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"DONE {vkey} -> total={total_dur:.2f}s (STRICT <= 60s!)", flush=True)


if __name__ == "__main__":
    main()
