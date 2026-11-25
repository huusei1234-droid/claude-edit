"""
Tổng hợp Voiceover giọng 'THANH THANH TVC' trên GPU NVIDIA RTX 4070 CUDA
cho CẢ 2 Video USP Ngày 01 (24/11/2026) căn chuẩn lưới 24fps (0.25s = 6 frames).
"""
import os
import sys
import json
import math
import wave
import shutil
from pathlib import Path
import numpy as np

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
VS_PROJ = Path(r"d:\AI\full studio\voice-studio")

DAY_DIR = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_01_2411")

VIDEOS = {
    "video_01_av_protein": {
        "title": "AV Protein — Đạm Thực Vật 22,05g & L-Leucine (Ngày 01)",
        "final_name": "261124 AVPM AV Protein Dam Thuc Vat 22g final.mp4",
        "segments": [
            ("vo_01", "Sáng nay bạn ăn sáng cho đủ no, hay ăn cho đủ đạm?"),
            ("vo_02", "Nhiều người ăn sáng toàn tinh bột, mới mười giờ đã thấy uể oải, đói bụng và thiếu năng lượng."),
            ("vo_03", "Thử ngay AV Protein của An Vượng Pharma, thực phẩm bổ sung đạm thực vật từ đậu Hà Lan và gạo."),
            ("vo_04", "Mỗi hai gói cung cấp hai mươi hai phẩy không năm gam đạm cùng một nghìn sáu trăm ba mươi hai miligam L-Leucine hỗ trợ giữ cơ săn chắc."),
            ("vo_05", "Kết hợp chất xơ Inulin và lợi khuẩn B-3 êm bụng dễ tiêu, pha nước mát hai mươi đến bốn mươi độ chỉ ba mươi giây."),
            ("vo_06", "Vị thơm béo dễ uống, nhẹ bụng mỗi sáng, đồng hành cùng người tập luyện và người bận rộn."),
            ("vo_07", "AV Protein hộp hai mươi gói chỉ ba trăm năm mươi nghìn. Nhắn Đạm Sạch để nhận ưu đãi mua năm tặng một Bojomi nhé!"),
        ],
    },
    "video_02_combo_4sp": {
        "title": "Combo 4 Sản Phẩm An Vượng — Tặng Collamela 20 Gói 920K (Ngày 01)",
        "final_name": "261124 AVPM Combo 4 San Pham Tang Collamela 920k final.mp4",
        "segments": [
            ("vo_01", "Sinh nhật Droppii tám tuổi, An Vượng Pharma tung ưu đãi hời nhất tháng mười một!"),
            ("vo_02", "Buổi sáng nạp năng lượng cùng AV Protein đạm thực vật từ đậu Hà Lan và gạo, nhẹ bụng giữ dáng."),
            ("vo_03", "Chăm khung xương dẻo dai với Bojomi ngũ cốc dinh dưỡng vị Vani, bổ sung canxi tảo biển, D3 và K2 MK-7."),
            ("vo_04", "Bữa phụ ấm êm cùng Curcumilk Phyto công nghệ Phytosome Ý, dịu nhẹ tiêu hóa, không hăng mùi nghệ."),
            ("vo_05", "Buổi tối chăm da ẩm mịn với Collamela Collagen Tripeptide kết hợp HA, Vitamin C và Kẽm vị đào dễ uống."),
            ("vo_06", "Mua trọn Combo bốn sản phẩm hai triệu bốn trăm bốn mươi nghìn, tặng ngay một hộp Collamela hai mươi gói trị giá chín trăm hai mươi nghìn."),
            ("vo_07", "Ưu đãi áp dụng đến hết ngày ba mươi tháng mười một. Chọn đúng mã Combo trên App Droppii để nhận trọn quà nhé!"),
        ],
    },
}


def trim_and_normalize(tensor_or_arr, sample_rate):
    if hasattr(tensor_or_arr, "detach"):
        arr = tensor_or_arr.detach().to("cpu").float().numpy().squeeze().astype(np.float32)
    else:
        arr = np.asarray(tensor_or_arr, dtype=np.float32).squeeze()
    if arr.ndim > 1:
        arr = arr.mean(axis=int(np.argmin(arr.shape)))
    abs_arr = np.abs(arr)
    peak = float(np.max(abs_arr)) if len(abs_arr) > 0 else 0.0
    if peak > 1e-4:
        arr = arr * (0.92 / peak)
        abs_arr = np.abs(arr)
    idx = np.where(abs_arr > 0.012)[0]
    if len(idx) > 10:
        s0 = max(0, int(idx[0]) - int(0.035 * sample_rate))
        s1 = min(len(arr), int(idx[-1]) + int(0.065 * sample_rate))
        arr = arr[s0:s1]
    return arr


def save_wav(path, pcm_f32, sample_rate):
    pcm = np.clip(np.copy(pcm_f32), -1.0, 1.0)
    fi = min(int(0.025 * sample_rate), len(pcm) // 4)
    fo = min(int(0.045 * sample_rate), len(pcm) // 4)
    if fi > 0:
        pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        pcm[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    pcm16 = (pcm * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16.tobytes())


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
    print(f"[RTX] PyTorch {torch.__version__} | CUDA={torch.cuda.is_available()} | GPU={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}", flush=True)
    from services.tts_backend import get_active_tts_backend

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

        # Copy BGM + 10 Studio SFX + TVC Vietnamese Fonts
        if AUDIO_BUNDLE_DIR.exists():
            for f in AUDIO_BUNDLE_DIR.iterdir():
                if f.is_file():
                    shutil.copy2(f, hf_aud / f.name)
        if FONTS_BUNDLE_DIR.exists():
            for f in FONTS_BUNDLE_DIR.iterdir():
                if f.is_file() and f.suffix.lower() in (".ttf", ".otf", ".woff2", ".css"):
                    shutil.copy2(f, hf_fnt / f.name)

        print(f"\n=== SYNTHESIZING {vkey} ({vcfg['title']}) ===", flush=True)
        manifest = []
        prev_end = 0.0
        sr = 24000

        for idx, (seg_id, text) in enumerate(vcfg["segments"]):
            wav_t = backend.generate(
                text=text,
                ref_audio=ref_audio,
                ref_text=ref_text,
                language=params.get("language", "vi"),
                num_step=int(params.get("num_step", 28)),
                guidance_scale=float(params.get("guidance_scale", 2.0)),
                speed=float(params.get("speed", 1.06)),
            )
            sr = int(getattr(backend, "sample_rate", 24000))
            arr = trim_and_normalize(wav_t, sr)
            dur_s = round(len(arr) / float(sr), 3)

            seg_path = vo_dir / f"{seg_id}.wav"
            save_wav(seg_path, arr, sr)
            shutil.copy2(seg_path, hf_aud / f"{seg_id}.wav")

            raw_shot = dur_s + 0.56
            shot_dur_s = max(3.0, round(math.ceil(raw_shot * 4.0) / 4.0, 2))
            shot_start_s = 0.0 if idx == 0 else prev_end
            flow_s = max(3, min(8, int(math.ceil(shot_dur_s * 0.85))))

            manifest.append({
                "id": seg_id,
                "text": text,
                "path": str(seg_path),
                "shot_start_s": shot_start_s,
                "shot_duration_s": shot_dur_s,
                "shot_end_s": round(shot_start_s + shot_dur_s, 2),
                "recommended_flow_gen_s": flow_s,
                "start_s": round(shot_start_s + 0.22, 3),
                "duration_s": dur_s,
                "end_s": round(shot_start_s + 0.22 + dur_s, 3),
            })
            prev_end = round(shot_start_s + shot_dur_s, 2)
            print(f"  {seg_id}: vo={dur_s:.2f}s | shot={shot_start_s:.2f}..{prev_end:.2f}s ({shot_dur_s:.2f}s -> Flow {flow_s}s)", flush=True)

        # End-Card >= 5.25s with ~1.05s musical outro tail
        min_end = max(5.25, round(math.ceil((manifest[-1]["duration_s"] + 1.05) * 4.0) / 4.0, 2))
        if manifest[-1]["shot_duration_s"] < min_end:
            manifest[-1]["shot_duration_s"] = min_end
            manifest[-1]["shot_end_s"] = round(manifest[-1]["shot_start_s"] + min_end, 2)

        total_dur_s = manifest[-1]["shot_end_s"]
        full_tl = np.zeros(int(round(total_dur_s * sr)), dtype=np.float32)
        for m in manifest:
            with wave.open(m["path"], "rb") as wf:
                a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
            st_i = int(round(m["start_s"] * sr))
            en_i = min(len(full_tl), st_i + len(a))
            full_tl[st_i:en_i] = a[:en_i - st_i]
        full_wav = vo_dir / f"{vkey.upper()}_FULL_VO.wav"
        save_wav(full_wav, full_tl, sr)

        (vo_dir / "vo_manifest.json").write_text(
            json.dumps({
                "video_key": vkey,
                "title": vcfg["title"],
                "final_name": vcfg["final_name"],
                "voice_profile_name": meta["name"],
                "voice_profile_id": meta["id"],
                "sample_rate": sr,
                "total_duration_s": total_dur_s,
                "segments": manifest,
                "full_wav": str(full_wav),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"DONE {vkey} -> total={total_dur_s:.2f}s ({len(manifest)} shots @ 24fps)", flush=True)


if __name__ == "__main__":
    main()
