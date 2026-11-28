# -*- coding: utf-8 -*-
import json, math, os, shutil, sys, wave
from pathlib import Path

_omni_short_cache = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\Hang thu\AppData\Local"), "OmniVoice", "hf_cache")
os.environ["HF_HOME"] = _omni_short_cache
os.environ["HF_HUB_CACHE"] = _omni_short_cache
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import numpy as np
import torch
from faster_whisper import WhisperModel

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
OUT_VO_DIR = Path(r"d:\AI\full studio\output\htpm-couple-nlh-dk-v2-261125\c02_dieu_kinh_ht\06_Solo_Voiceover")
OUT_VO_DIR.mkdir(parents=True, exist_ok=True)

vs_proj = Path(r"d:\AI\full studio\voice-studio")
sys.path.insert(0, str(vs_proj / "backend"))
sys.path.insert(0, str(vs_proj))
from services.tts_backend import get_active_tts_backend

SEGMENTS = [
    ("vo_01", "Phụ nữ mình mỗi tháng đến kỳ dâu rụng thường đau bụng âm ỉ, người mệt lả đi nhưng vẫn ráng chu toàn công việc và gia đình.", "Phụ nữ mình mỗi tháng đến kỳ dâu rụng thường đau bụng âm ỉ, người mệt lả đi nhưng vẫn ráng chu toàn công việc và gia đình.", ["phụ nữ", "đau bụng"]),
    ("vo_02", "Khi khí huyết kém lưu thông, chu kỳ dễ thất thường, tay chân lạnh và sắc mặt cũng kém tươi tắn rạng rỡ.", "Khi khí huyết kém lưu thông, chu kỳ dễ thất thường, tay chân lạnh và sắc mặt cũng kém tươi tắn rạng rỡ.", ["khí huyết", "chu kỳ"]),
    ("vo_03", "Bí quyết để Hằng luôn êm dịu mỗi chu kỳ chính là đều đặn dùng Viên Uống Điều Kinh Hát Tê Hằng Thu.", "Bí quyết để Hằng luôn êm dịu mỗi chu kỳ chính là đều đặn dùng Viên Uống Điều Kinh HT Hằng Thu.", ["chu kỳ", "điều kinh", "hằng thu"]),
    ("vo_04", "Sự kết hợp từ Đương quy và Hương phụ giúp bổ huyết, lưu thông khí huyết, hỗ trợ điều hòa kinh nguyệt và giảm đau bụng khi hành kinh.", "Sự kết hợp từ Đương quy và Hương phụ giúp bổ huyết, lưu thông khí huyết, hỗ trợ điều hòa kinh nguyệt và giảm đau bụng khi hành kinh.", ["đương quy", "hương phụ", "bổ huyết"]),
    ("vo_05", "Khí huyết thông suốt để phụ nữ luôn hồng hào rạng rỡ, chị em nhắn ngay Điều Kinh Hát Tê cho Hằng Thu nhé.", "Khí huyết thông suốt để phụ nữ luôn hồng hào rạng rỡ, chị em nhắn ngay Điều Kinh HT cho Hằng Thu nhé.", ["hồng hào", "hằng thu"]),
]

def trim_and_normalize(tensor_or_arr, sample_rate):
    arr = tensor_or_arr.detach().to("cpu").float().numpy().squeeze().astype(np.float32) if hasattr(tensor_or_arr, "detach") else np.asarray(tensor_or_arr, dtype=np.float32).squeeze()
    if arr.ndim > 1:
        arr = arr.mean(axis=int(np.argmin(arr.shape)))
    abs_arr = np.abs(arr)
    peak = float(np.max(abs_arr)) if len(abs_arr) > 0 else 0.0
    if peak > 1e-4:
        arr = arr * (0.92 / peak)
        abs_arr = np.abs(arr)
    idx = np.where(abs_arr > 0.012)[0]
    if len(idx) > 10:
        arr = arr[max(0, int(idx[0]) - int(0.03 * sample_rate)):min(len(arr), int(idx[-1]) + int(0.055 * sample_rate))]
    return arr

def save_wav(path, pcm_f32, sample_rate):
    pcm = np.clip(np.copy(pcm_f32), -1.0, 1.0)
    fi, fo = min(int(0.025 * sample_rate), len(pcm) // 4), min(int(0.045 * sample_rate), len(pcm) // 4)
    if fi > 0: pcm[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0: pcm[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    pcm16 = (pcm * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sample_rate)
        wf.writeframes(pcm16.tobytes())

def main():
    meta = json.loads((VOICE_BUNDLE_DIR / "profile_metadata.json").read_text(encoding="utf-8"))
    ref_audio = str(VOICE_BUNDLE_DIR / meta["ref_audio_filename"])
    ref_text = meta["ref_text"]
    backend = get_active_tts_backend()
    asr = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=6, download_root=r"C:\Users\Hang thu\.cache\huggingface\hub")

    manifest = []
    prev_shot_end = 0.0
    for idx, (seg_id, tts_text, disp_text, kw_list) in enumerate(SEGMENTS):
        best_path, best_dur, best_tr, best_sc = None, 0.0, "", -1
        for sd in [2028, 369]:
            torch.manual_seed(sd)
            wav_t = backend.generate(text=tts_text, ref_audio=ref_audio, ref_text=ref_text, language="vi", num_step=26, guidance_scale=2.0, speed=1.08)
            sr = int(getattr(backend, "sample_rate", 24000))
            arr = trim_and_normalize(wav_t, sr)
            cp = OUT_VO_DIR / f"{seg_id}_cand_{sd}.wav"
            save_wav(cp, arr, sr)
            segs_asr, _ = asr.transcribe(str(cp), language="vi", beam_size=1)
            tr = " ".join(s.text.strip() for s in segs_asr).strip()
            hits = sum(1 for k in kw_list if k in tr.lower())
            if hits > best_sc:
                best_sc, best_path, best_dur, best_tr = hits, cp, round(len(arr) / float(sr), 3), tr
            if hits == len(kw_list):
                break
        seg_path = OUT_VO_DIR / f"{seg_id}.wav"
        shutil.copy2(best_path, seg_path)
        for c in OUT_VO_DIR.glob(f"{seg_id}_cand_*.wav"):
            c.unlink(missing_ok=True)
        raw_shot_dur = best_dur + (0.85 if idx == 4 else 0.46)
        shot_dur_s = max(4.75 if idx == 4 else 3.50, round(math.ceil(raw_shot_dur * 4.0) / 4.0, 2))
        shot_start_s = 0.0 if idx == 0 else prev_shot_end
        manifest.append({
            "id": seg_id, "shot_id": f"DK3_S{idx+1:02d}",
            "tts_text": tts_text, "text": disp_text, "whisper_verified": best_tr,
            "shot_start_s": shot_start_s, "shot_duration_s": shot_dur_s,
            "shot_end_s": round(shot_start_s + shot_dur_s, 2),
            "start_s": round(shot_start_s + 0.18, 3), "duration_s": best_dur,
            "end_s": round(shot_start_s + 0.18 + best_dur, 3),
        })
        prev_shot_end = round(shot_start_s + shot_dur_s, 2)
        print(f"  [{seg_id}] {best_dur}s -> {best_tr}", flush=True)

    total_dur = manifest[-1]["shot_end_s"]
    assert total_dur <= 45.0, f"Exceeded 45s: {total_dur}"
    out_json = OUT_VO_DIR / "vo_manifest.json"
    out_json.write_text(json.dumps({
        "vid_key": "c02_dieu_kinh_ht",
        "sku": "SP01 — Điều Kinh HT (Chị Hằng Chia Sẻ Bí Quyết Dưỡng Khí Huyết)",
        "final_name": "261125 HTPM Điều Kinh HT bí quyết dưỡng khí huyết rạng rỡ của chị Hằng final.mp4",
        "total_duration_s": total_dur, "fps": 24, "segments": manifest,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SOLO DK VO DONE] total_duration_s = {total_dur}s", flush=True)

if __name__ == "__main__":
    main()
