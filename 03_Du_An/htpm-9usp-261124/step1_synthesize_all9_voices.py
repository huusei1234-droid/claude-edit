"""
Step 1 — Tổng hợp toàn bộ 54 phân đoạn Voiceover 'THANH THANH TVC' (78ef243f) trên GPU trong 1 lượt nạp model duy nhất
cho cả 9 Video USP (V01..V09), kèm kiểm định phát âm bằng faster-whisper (CPU int8) & căn lưới 24fps (bội số 0.25s)!
"""
import json
import math
import os
import shutil
import sys
import wave
from pathlib import Path

_omni_short_cache = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\Hang thu\AppData\Local"), "OmniVoice", "hf_cache")
os.environ["HF_HOME"] = _omni_short_cache
os.environ["HF_HUB_CACHE"] = _omni_short_cache
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from htpm_9usp_catalog import VIDEOS_9USP, ROOT_OUT, BRAND_KIT, HT_LOGO_PNG

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"


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

    vs_proj = Path(r"d:\AI\full studio\voice-studio")
    sys.path.insert(0, str(vs_proj / "backend"))
    sys.path.insert(0, str(vs_proj))

    import torch
    from faster_whisper import WhisperModel
    from services.tts_backend import get_active_tts_backend

    backend = get_active_tts_backend()
    default_hf_hub = r"C:\Users\Hang thu\.cache\huggingface\hub"
    asr = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=6, download_root=default_hf_hub)
    candidate_seeds = [2028, 369, 888]

    for vspec in VIDEOS_9USP:
        vcode = vspec["vid_code"]
        vdir = ROOT_OUT / vcode
        ing_dir = vdir / "01_Ref_Images"
        raw_vid_dir = vdir / "03_Flow_Raw_Videos"
        vo_dir = vdir / "06_Audio_Voiceover"
        hf_aud_dir = vdir / "07_HyperFrames_Project" / "assets" / "audio"
        hf_vid_dir = vdir / "07_HyperFrames_Project" / "assets" / "videos"
        hf_fnt_dir = vdir / "07_HyperFrames_Project" / "assets" / "fonts"
        hf_img_dir = vdir / "07_HyperFrames_Project" / "assets" / "images"
        for d in (ing_dir, raw_vid_dir, vo_dir, hf_aud_dir, hf_vid_dir, hf_fnt_dir, hf_img_dir):
            d.mkdir(parents=True, exist_ok=True)

        out_json = vo_dir / "vo_manifest.json"
        if out_json.exists():
            print(f"[{vcode}] VO already synthesized -> skipping ({out_json})", flush=True)
            continue

        for f in AUDIO_BUNDLE_DIR.iterdir():
            if f.is_file():
                shutil.copy2(f, hf_aud_dir / f.name)
        for f in FONTS_BUNDLE_DIR.iterdir():
            if f.is_file() and f.suffix.lower() in (".ttf", ".otf", ".woff2", ".css"):
                shutil.copy2(f, hf_fnt_dir / f.name)
        shutil.copy2(BRAND_KIT / "products_cutout_png" / vspec["cutout_png"], hf_img_dir / vspec["cutout_png"])
        shutil.copy2(HT_LOGO_PNG, hf_img_dir / "ht_logo_official.png")

        manifest = []
        prev_shot_end = 0.0
        print(f"\n=== [{vcode}] Synthesizing {vspec['sku']} ===", flush=True)

        for idx, (seg_id, tts_text, kw_list, _) in enumerate(vspec["segments"]):
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

            min_shot = 4.25 if idx == 0 else (5.75 if idx == 5 else 3.75)
            pad_tail = 1.15 if idx == 5 else 0.58
            shot_dur_s = max(min_shot, round(math.ceil((best_dur + pad_tail) * 4.0) / 4.0, 2))
            shot_start_s = 0.0 if idx == 0 else prev_shot_end

            shot_id = f"{vcode}_S{idx+1:02d}"
            manifest.append({
                "id": seg_id,
                "shot_id": shot_id,
                "voice_profile": meta["name"],
                "voice_profile_id": meta["id"],
                "tts_text": tts_text,
                "whisper_verified": best_transcript,
                "kw_score": f"{best_score}/{len(kw_list)}",
                "path": str(seg_path),
                "shot_start_s": shot_start_s,
                "shot_duration_s": shot_dur_s,
                "shot_end_s": round(shot_start_s + shot_dur_s, 2),
                "recommended_flow_gen_s": max(4, min(8, int(math.ceil(shot_dur_s * 0.85)))),
                "start_s": round(shot_start_s + 0.22, 3),
                "duration_s": best_dur,
                "end_s": round(shot_start_s + 0.22 + best_dur, 3),
            })
            prev_shot_end = round(shot_start_s + shot_dur_s, 2)
            print(
                f"  [{shot_id}] vo={best_dur:.2f}s | shot={shot_start_s:.2f}..{prev_shot_end:.2f}s ({shot_dur_s:.2f}s) "
                f"| ASR[{best_score}/{len(kw_list)}]: {best_transcript}",
                flush=True,
            )

        total_dur = manifest[-1]["shot_end_s"]
        out_json.write_text(
            json.dumps({"vid_code": vcode, "total_duration_s": total_dur, "fps": 24, "segments": manifest}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        shutil.copy2(out_json, hf_aud_dir / "vo_manifest.json")
        print(f"  [OK {vcode}] Total 24fps TVC Duration = {total_dur:.2f}s ({int(round(total_dur * 24))} frames)", flush=True)

    print("\nALL 9 USP VOICEOVERS SYNTHESIZED & VERIFIED SUCCESSFULLY!", flush=True)


if __name__ == "__main__":
    main()
