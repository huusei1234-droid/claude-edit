"""
Ngày 01 (24/11/2026) — Tổng hợp Voiceover 'THANH THANH TVC' (78ef243f) trên GPU RTX 4070
cho Video USP SP02: Viên Đặt Phụ Khoa LT Plus Hằng Thu (8 phân đoạn căn lưới 24fps = bội số 0.25s)
kèm tự động chấm điểm phát âm bằng faster-whisper (CPU int8) chọn seed rõ chữ nhất!
"""
import json
import math
import os
import shutil
import sys
import wave
from pathlib import Path

# Point HF cache to VoiceStudio's Windows short-cache BEFORE any huggingface_hub import freezes constants!
_omni_short_cache = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\Hang thu\AppData\Local"), "OmniVoice", "hf_cache")
os.environ["HF_HOME"] = _omni_short_cache
os.environ["HF_HUB_CACHE"] = _omni_short_cache
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import numpy as np

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"

PROJECT_SLUG = "htpm-d01-ltplus-261124"
PROJ_DIR = Path(r"d:\AI\full studio\output") / PROJECT_SLUG

# (seg_id, tts_text, display_text, key_check_words)
SEGMENTS = [
    (
        "vo_01",
        "Càng âm thầm tự tra triệu chứng trên mạng, chị càng thấy rối bời và hoang mang?",
        "Càng âm thầm tự tra triệu chứng trên mạng, chị càng thấy rối bời và hoang mang?",
        ["triệu chứng", "hoang mang"],
    ),
    (
        "vo_02",
        "Ngồi văn phòng suốt tám tiếng, cảm giác ẩm ướt, ra dịch nhiều hay mùi khó nói cứ âm thầm lấy đi sự tự tin của chị.",
        "Ngồi văn phòng suốt 8 tiếng, cảm giác ẩm ướt, ra dịch nhiều hay mùi khó nói cứ âm thầm lấy đi sự tự tin của chị.",
        ["văn phòng", "tự tin"],
    ),
    (
        "vo_03",
        "Khi vùng nhạy cảm mất cân bằng, nếu chỉ vội vàng che giấu bên ngoài thì cảm giác khó chịu rất dễ quay trở lại.",
        "Khi vùng nhạy cảm mất cân bằng, nếu chỉ vội vàng che giấu bên ngoài thì cảm giác khó chịu rất dễ quay trở lại.",
        ["cân bằng", "trở lại"],
    ),
    (
        "vo_04",
        "Hiểu cơ thể để thương mình đúng cách, chị chọn đồng hành cùng Viên Đặt Phụ Khoa Lờ Tê Plus Hằng Thu.",
        "Hiểu cơ thể để thương mình đúng cách, chị chọn đồng hành cùng Viên Đặt Phụ Khoa LT Plus Hằng Thu.",
        ["đồng hành", "hằng thu"],
    ),
    (
        "vo_05",
        "Lờ Tê Plus hỗ trợ kháng khuẩn, làm sạch dịch nhầy êm dịu, khử mùi hôi và duy trì độ ẩm cùng pê hát tự nhiên.",
        "LT Plus hỗ trợ kháng khuẩn, làm sạch dịch nhầy êm dịu, khử mùi hôi và duy trì độ ẩm cùng pH tự nhiên.",
        ["kháng khuẩn", "khử mùi", "tự nhiên"],
    ),
    (
        "vo_06",
        "Sự hòa quyện từ Hoàng bá, Kim ngân hoa, Trầu không, Trà xanh và A xít Lắc tích giúp nâng niu vùng nhạy cảm thật lành tính.",
        "Sự hòa quyện từ Hoàng bá, Kim ngân hoa, Trầu không, Trà xanh và Acid Lactic giúp nâng niu vùng nhạy cảm thật lành tính.",
        ["hoàng bá", "trầu không", "lành tính"],
    ),
    (
        "vo_07",
        "Cảm giác sạch thoáng, êm ái từ bên trong để chị luôn nhẹ nhõm, rạng rỡ suốt ngày dài và trọn vẹn hạnh phúc.",
        "Cảm giác sạch thoáng, êm ái từ bên trong để chị luôn nhẹ nhõm, rạng rỡ suốt ngày dài và trọn vẹn hạnh phúc.",
        ["sạch thoáng", "rạng rỡ", "hạnh phúc"],
    ),
    (
        "vo_08",
        "Nhắn ngay Lờ Tê Plus để được Hằng Thu tư vấn riêng tư và kín đáo cho chị nhé.",
        "Nhắn ngay LT Plus để được Hằng Thu tư vấn riêng tư và kín đáo cho chị nhé.",
        ["hằng thu", "tư vấn", "kín đáo"],
    ),
]


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
    ing_dir = PROJ_DIR / "01_ChatGPT_Ingredients"
    raw_vid_dir = PROJ_DIR / "03_Flow_Raw_Videos"
    vo_dir = PROJ_DIR / "06_Audio_Voiceover"
    hf_aud_dir = PROJ_DIR / "07_HyperFrames_Project" / "assets" / "audio"
    hf_vid_dir = PROJ_DIR / "07_HyperFrames_Project" / "assets" / "videos"
    hf_fnt_dir = PROJ_DIR / "07_HyperFrames_Project" / "assets" / "fonts"
    post_dir = PROJ_DIR / "09_Bai_Thiet_Ke_Gel_Phu_Khang"
    for d in (ing_dir, raw_vid_dir, vo_dir, hf_aud_dir, hf_vid_dir, hf_fnt_dir, post_dir):
        d.mkdir(parents=True, exist_ok=True)

    if AUDIO_BUNDLE_DIR.exists():
        for f in AUDIO_BUNDLE_DIR.iterdir():
            if f.is_file():
                shutil.copy2(f, hf_aud_dir / f.name)

    if FONTS_BUNDLE_DIR.exists():
        for f in FONTS_BUNDLE_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in (".ttf", ".otf", ".woff2", ".css"):
                shutil.copy2(f, hf_fnt_dir / f.name)

    meta = json.loads((VOICE_BUNDLE_DIR / "profile_metadata.json").read_text(encoding="utf-8"))
    ref_audio = str(VOICE_BUNDLE_DIR / meta["ref_audio_filename"])
    ref_text = meta["ref_text"]
    params = meta["recommended_generation_params"]

    vs_proj = Path(r"d:\AI\full studio\voice-studio")
    sys.path.insert(0, str(vs_proj / "backend"))
    sys.path.insert(0, str(vs_proj))

    import torch
    from faster_whisper import WhisperModel
    from services.tts_backend import get_active_tts_backend

    backend = get_active_tts_backend()
    default_hf_hub = r"C:\Users\Hang thu\.cache\huggingface\hub"
    asr = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=6, download_root=default_hf_hub)
    candidate_seeds = [2028, 369, 888, 1688]

    manifest = []
    prev_shot_end = 0.0

    for idx, (seg_id, tts_text, disp_text, kw_list) in enumerate(SEGMENTS):
        best_path = None
        best_dur = 0.0
        best_transcript = ""
        best_score = -1

        for sd in candidate_seeds:
            torch.manual_seed(sd)
            wav_t = backend.generate(
                text=tts_text,
                ref_audio=ref_audio,
                ref_text=ref_text,
                language=params.get("language", "vi"),
                num_step=int(params.get("num_step", 28)),
                guidance_scale=float(params.get("guidance_scale", 2.0)),
                speed=float(params.get("speed", 1.05)),
            )
            sr = int(getattr(backend, "sample_rate", 24000))
            arr = trim_and_normalize(wav_t, sr)
            cand_path = vo_dir / f"{seg_id}_cand_{sd}.wav"
            save_wav(cand_path, arr, sr)

            segs_asr, _ = asr.transcribe(str(cand_path), language="vi", beam_size=3)
            trans_txt = " ".join(s.text.strip() for s in segs_asr).strip()
            low_txt = trans_txt.lower()
            hits = sum(1 for k in kw_list if k in low_txt)
            if hits > best_score:
                best_score = hits
                best_path = cand_path
                best_dur = round(len(arr) / float(sr), 3)
                best_transcript = trans_txt
            if hits == len(kw_list):
                break

        seg_path = vo_dir / f"{seg_id}.wav"
        shutil.copy2(best_path, seg_path)
        shutil.copy2(seg_path, hf_aud_dir / f"{seg_id}.wav")
        for c in vo_dir.glob(f"{seg_id}_cand_*.wav"):
            c.unlink(missing_ok=True)

        raw_shot_dur = best_dur + 0.58
        shot_dur_s = max(3.50, round(math.ceil(raw_shot_dur * 4.0) / 4.0, 2))
        shot_start_s = 0.0 if idx == 0 else prev_shot_end

        manifest.append({
            "id": seg_id,
            "shot_id": f"LT_S{idx+1:02d}",
            "voice_profile": meta["name"],
            "voice_profile_id": meta["id"],
            "tts_text": tts_text,
            "text": disp_text,
            "whisper_verified": best_transcript,
            "kw_score": f"{best_score}/{len(kw_list)}",
            "path": str(seg_path),
            "shot_start_s": shot_start_s,
            "shot_duration_s": shot_dur_s,
            "shot_end_s": round(shot_start_s + shot_dur_s, 2),
            "recommended_flow_gen_s": max(4, min(8, int(math.ceil(shot_dur_s) + 1))),
            "start_s": round(shot_start_s + 0.24, 3),
            "duration_s": best_dur,
            "end_s": round(shot_start_s + 0.24 + best_dur, 3),
        })
        prev_shot_end = round(shot_start_s + shot_dur_s, 2)
        print(
            f"  {seg_id} ({manifest[-1]['shot_id']}): voice={best_dur:.2f}s | shot={shot_start_s:.2f}..{prev_shot_end:.2f}s "
            f"({shot_dur_s:.2f}s -> Flow {manifest[-1]['recommended_flow_gen_s']}s) | ASR[{best_score}/{len(kw_list)}]: {best_transcript}",
            flush=True,
        )

    min_end_dur = max(5.50, round(math.ceil((manifest[-1]["duration_s"] + 1.15) * 4.0) / 4.0, 2))
    if manifest[-1]["shot_duration_s"] < min_end_dur:
        manifest[-1]["shot_duration_s"] = min_end_dur
        manifest[-1]["shot_end_s"] = round(manifest[-1]["shot_start_s"] + min_end_dur, 2)
        manifest[-1]["recommended_flow_gen_s"] = max(4, min(8, int(math.ceil(min_end_dur) + 1)))

    total_dur = manifest[-1]["shot_end_s"]
    out_json = vo_dir / "vo_manifest.json"
    out_json.write_text(
        json.dumps({"total_duration_s": total_dur, "fps": 24, "segments": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    shutil.copy2(out_json, hf_aud_dir / "vo_manifest.json")
    print(f"\n[OK] Total 24fps LT Plus TVC Duration: {total_dur:.2f}s ({int(round(total_dur * 24))} frames) -> {out_json}", flush=True)


if __name__ == "__main__":
    main()
