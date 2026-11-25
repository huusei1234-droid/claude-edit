"""
Tổng hợp Voiceover giọng 'THANH THANH TVC' trên GPU NVIDIA RTX 4070 CUDA
cho Video 03 (Bojomi) và Video 04 (Collamela) bổ sung đủ 4 Video Ngày 01 (24/11/2026).
"""
import os, sys, json, math, wave, shutil
from pathlib import Path
import numpy as np

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
VS_PROJ = Path(r"d:\AI\full studio\voice-studio")
DAY_DIR = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_01_2411")

VIDEOS = {
    "video_03_bojomi": {
        "title": "Bojomi — Canxi Tảo Biển Aquamin F + D3 + K2 MK-7 (Ngày 01)",
        "final_name": "261124 AVPM Bojomi Canxi Tao Bien D3 K2 final.mp4",
        "segments": [
            ("vo_01", "Chọn Canxi đừng chỉ nhìn miligam, hãy hỏi nguồn gốc!"),
            ("vo_02", "Nhiều người uống Canxi mãi vẫn thấy nặng bụng, khó hấp thu vì thiếu bộ đôi dẫn đường."),
            ("vo_03", "Bojomi của An Vượng Pharma kết hợp Canxi tảo biển Aquamin F cùng Vitamin D3 và K2 MK-7."),
            ("vo_04", "Mỗi gói cung cấp bốn trăm mười bảy phẩy sáu miligam Canxi, bảy trăm bảy mươi chín phẩy bốn IU D3 và một trăm sáu mươi chín phẩy tám microgam K2 MK-7."),
            ("vo_05", "Bổ sung thêm hai trăm lẻ một phẩy bốn miligam Collagen, hương Vani thơm béo dễ uống, chỉ cần pha với hai trăm mililit nước ấm sáu mươi độ."),
            ("vo_06", "Đóng gói tiện lợi cho người lớn tuổi, dân văn phòng và cả gia đình chăm khung xương dẻo dai mỗi ngày."),
            ("vo_07", "Bojomi năm trăm hai mươi nghìn hộp mười bốn gói. Nhắn Canxi nhận ngay ưu đãi mua ba tặng một đến hết ba mươi tháng mười một nhé!"),
        ],
    },
    "video_04_collamela": {
        "title": "Collamela — Collagen Tripeptide + HA + C + Kẽm Đón Tết (Ngày 01)",
        "final_name": "261124 AVPM Collamela Collagen Tripeptide Don Tet final.mp4",
        "segments": [
            ("vo_01", "Sắp có tiệc cuối năm mới vội chăm da thì đã muộn rồi!"),
            ("vo_02", "Còn đúng sáu mươi ngày nữa là tới Tết, muốn làn da căng mướt rạng rỡ hãy nuôi dưỡng từ bên trong ngay hôm nay."),
            ("vo_03", "Collamela của An Vượng Pharma ứng dụng Collagen Tripeptide phân tử nhỏ giúp cơ thể dễ dàng hấp thu."),
            ("vo_04", "Mỗi hai gói cung cấp hai nghìn năm trăm ba mươi miligam Collagen, hai mươi lăm phẩy sáu mươi tám miligam HA cùng Vitamin C và Kẽm."),
            ("vo_05", "Vị đào thanh mát hoàn toàn không tanh, chỉ cần pha một trăm mililit nước mát uống ngon mỗi ngày."),
            ("vo_06", "Kết hợp ngủ sớm và uống đều đặn để làn da luôn ẩm mịn, đàn hồi và tươi tắn suốt mùa lễ hội."),
            ("vo_07", "Ưu đãi sinh nhật Droppii: mua hai hộp hai mươi gói tặng ngay một hộp mười gói bốn trăm tám mươi nghìn. Nhắn Da Đẹp nhận tư vấn ngay nhé!"),
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
        arr = arr[max(0, int(idx[0]) - int(0.035 * sr)) : min(len(arr), int(idx[-1]) + int(0.065 * sr))]
    return arr


def save_wav(path, pcm_f32, sr):
    pcm = np.clip(np.copy(pcm_f32), -1.0, 1.0)
    fi = min(int(0.025 * sr), len(pcm) // 4)
    fo = min(int(0.045 * sr), len(pcm) // 4)
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
        vdir = DAY_DIR / vkey
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
                speed=float(params.get("speed", 1.07)),
            )
            sr = int(getattr(backend, "sample_rate", 24000))
            arr = trim_and_normalize(wav_t, sr)
            dur_s = round(len(arr) / float(sr), 3)
            seg_path = vo_dir / f"{seg_id}.wav"
            save_wav(seg_path, arr, sr)
            shutil.copy2(seg_path, hf_aud / f"{seg_id}.wav")

            shot_dur_s = max(3.25, round(math.ceil((dur_s + 0.56) * 4.0) / 4.0, 2))
            shot_start_s = 0.0 if idx == 0 else prev_end
            manifest.append({
                "id": seg_id, "text": text, "path": str(seg_path),
                "shot_start_s": shot_start_s, "shot_duration_s": shot_dur_s,
                "shot_end_s": round(shot_start_s + shot_dur_s, 2),
                "start_s": round(shot_start_s + 0.22, 3), "duration_s": dur_s,
                "end_s": round(shot_start_s + 0.22 + dur_s, 3),
            })
            prev_end = round(shot_start_s + shot_dur_s, 2)
            print(f"  {seg_id}: vo={dur_s:.2f}s | shot={shot_start_s:.2f}..{prev_end:.2f}s ({shot_dur_s:.2f}s)", flush=True)

        min_end = max(5.25, round(math.ceil((manifest[-1]["duration_s"] + 1.05) * 4.0) / 4.0, 2))
        if manifest[-1]["shot_duration_s"] < min_end:
            manifest[-1]["shot_duration_s"] = min_end
            manifest[-1]["shot_end_s"] = round(manifest[-1]["shot_start_s"] + min_end, 2)
        total_dur = manifest[-1]["shot_end_s"]
        (vo_dir / "vo_manifest.json").write_text(json.dumps({
            "video_key": vkey, "title": vcfg["title"], "final_name": vcfg["final_name"],
            "voice_profile_name": meta["name"], "sample_rate": sr,
            "total_duration_s": total_dur, "segments": manifest,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"DONE {vkey} -> total={total_dur:.2f}s", flush=True)

if __name__ == "__main__":
    main()
