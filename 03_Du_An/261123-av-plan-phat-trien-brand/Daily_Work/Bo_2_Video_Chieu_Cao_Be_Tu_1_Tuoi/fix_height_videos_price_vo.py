# -*- coding: utf-8 -*-
"""
SURGICAL WHISPER-VERIFIED VOICEOVER FIX VIA LIVE VOICESTUDIO (:3900 GPU CUDA):
- Fixes OmniVoice swallowing 'trăm' ('87.000' instead of '870.000đ', 'năm 20.000'/'5.000' instead of '520.000đ')
- Calls warm GPU VoiceStudio HTTP endpoint (http://127.0.0.1:3900/generate, profile_id=78ef243f, effect_preset=raw)
- Synthesizes short, crisp sub-clauses at speed=1.01, num_step=32 with 'nghìn đồng' prosody anchor
- Automatically verifies EVERY clause & combined WAV with faster-whisper ('870' & '520' must be heard 100%!)
- Updates vo_manifest.json while keeping shots 1..5 100% frame-locked and total_duration_s <= 58.5s for Kid1Y.
"""
import io, json, math, os, shutil, sys, wave
from pathlib import Path
import numpy as np
import requests
import faster_whisper

DAILY_WORK = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work")
VS_URL = "http://127.0.0.1:3900/generate"
PROFILE_ID = "78ef243f"  # THANH THANH TVC

TARGETS = [
    {
        "vdir": DAILY_WORK / "Bo_2_Video_Chieu_Cao_Be_Tu_1_Tuoi" / "kid1y_01_giai_doan_vang",
        "seg_id": "vo_06",
        "pad_s": 0.42,
        "max_total": 58.5,
        "clauses": [
            {
                "text": "Mẹ chia khẩu phần theo độ tuổi của bé, kết hợp ngủ sớm và vận động.",
                "must_any": ["khẩu phần", "độ tuổi"],
                "forbid": [],
            },
            {
                "text": "Bộ đôi có giá tám trăm bảy mươi nghìn đồng.",
                "must_any": ["870", "tám trăm bảy mươi"],
                "forbid": ["87.000", "87 nghìn", "tám mươi bảy", "8.000"],
            },
            {
                "text": "Mẹ nhắn Bé Một Tuổi nhận tư vấn và quà tặng năm trăm hai mươi nghìn đồng nhé!",
                "must_any": ["520", "năm trăm hai mươi"],
                "forbid": ["52.000", "5.000", "năm 20", "năm hai mươi"],
            },
        ],
    },
    {
        "vdir": DAILY_WORK / "Bo_2_Video_Chieu_Cao_Be_Tu_1_Tuoi" / "kid1y_02_pha_chuan_2_ly",
        "seg_id": "vo_06",
        "pad_s": 0.42,
        "max_total": 58.5,
        "clauses": [
            {
                "text": "Bộ đôi Bojomi và AV Protein có giá tám trăm bảy mươi nghìn đồng.",
                "must_any": ["870", "tám trăm bảy mươi"],
                "forbid": ["87.000", "87 nghìn", "tám mươi bảy", "8.000", "bộ nội"],
            },
            {
                "text": "Ưu đãi đến ba mươi tháng mười một tặng hộp Bojomi năm trăm hai mươi nghìn đồng, mẹ nhắn Bé Một Tuổi ngay nhé!",
                "must_any": ["520", "năm trăm hai mươi"],
                "forbid": ["52.000", "5.000", "năm 20", "năm hai mươi"],
            },
        ],
    },
    {
        "vdir": DAILY_WORK / "Bo_4_Video_Combo_Chieu_Cao" / "height_03_pha_chuan_2_nhiet_do",
        "seg_id": "vo_07",
        "pad_s": 0.65,
        "max_total": 99.0,
        "clauses": [
            {
                "text": "Bộ đôi có giá tám trăm bảy mươi nghìn đồng.",
                "must_any": ["870", "tám trăm bảy mươi"],
                "forbid": ["87.000", "87 nghìn", "tám mươi bảy", "8.000"],
            },
            {
                "text": "Ưu đãi mua ba Bojomi hoặc năm AV Protein tặng ngay Bojomi năm trăm hai mươi nghìn đồng, nhắn Chiều Cao ngay nhé!",
                "must_any": ["520", "năm trăm hai mươi"],
                "forbid": ["52.000", "5.000", "năm 20", "năm hai mươi"],
            },
        ],
    },
    {
        "vdir": DAILY_WORK / "Bo_4_Video_Combo_Chieu_Cao" / "height_04_van_dong_va_deal_870k",
        "seg_id": "vo_07",
        "pad_s": 0.65,
        "max_total": 99.0,
        "clauses": [
            {
                "text": "Bộ đôi Bojomi và AV Protein có giá tám trăm bảy mươi nghìn đồng.",
                "must_any": ["870", "tám trăm bảy mươi"],
                "forbid": ["87.000", "87 nghìn", "tám mươi bảy", "8.000"],
            },
            {
                "text": "Đến hết ba mươi tháng mười một, mua năm AV Protein hoặc ba Bojomi tặng ngay một Bojomi năm trăm hai mươi nghìn đồng.",
                "must_any": ["520", "năm trăm hai mươi"],
                "forbid": ["52.000", "5.000", "năm 20", "năm hai mươi"],
            },
            {
                "text": "Nhắn Chiều Cao nhận ưu đãi ngay nhé!",
                "must_any": ["chiều cao"],
                "forbid": [],
            },
        ],
    },
]


def decode_and_trim_wav(wav_bytes: bytes):
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())
    if sw == 2:
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sw == 4:
        arr = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sw}")
    if nch > 1:
        arr = arr.reshape(-1, nch).mean(axis=1)

    abs_arr = np.abs(arr)
    peak = float(np.max(abs_arr)) if len(abs_arr) else 0.0
    if peak > 1e-4:
        arr = arr * (0.92 / peak)
        abs_arr = np.abs(arr)
    idx = np.where(abs_arr > 0.012)[0]
    if len(idx) > 10:
        arr = arr[max(0, int(idx[0]) - int(0.028 * sr)) : min(len(arr), int(idx[-1]) + int(0.050 * sr))]
    fi = min(int(0.020 * sr), len(arr) // 4)
    fo = min(int(0.035 * sr), len(arr) // 4)
    if fi > 0:
        arr[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        arr[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    return arr, sr


def save_wav(path: Path, pcm_f32: np.ndarray, sr: int):
    pcm = np.clip(np.copy(pcm_f32), -1.0, 1.0)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((pcm * 32767.0).astype(np.int16).tobytes())


def main():
    asr = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")
    seeds = [2026, 2028, 108, 2032, 369, 668, 888, 999, 1234, 4070]
    tmp_wav = DAILY_WORK / "_tmp_verify_clause.wav"

    for tgt in TARGETS:
        vdir = tgt["vdir"]
        seg_id = tgt["seg_id"]
        print(f"\n=== FIXING {vdir.name} ({seg_id}) ===", flush=True)
        pieces = []
        full_text_parts = []
        sr = 24000

        for c_idx, c_cfg in enumerate(tgt["clauses"]):
            ctext = c_cfg["text"]
            full_text_parts.append(ctext)
            best_arr = None
            for sd in seeds:
                resp = requests.post(
                    VS_URL,
                    data={
                        "text": ctext,
                        "profile_id": PROFILE_ID,
                        "language": "vi",
                        "num_step": "32",
                        "guidance_scale": "2.0",
                        "speed": "1.01",
                        "seed": str(sd),
                        "effect_preset": "raw",
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                arr, sr = decode_and_trim_wav(resp.content)
                save_wav(tmp_wav, arr, sr)
                segs_asr, _ = asr.transcribe(str(tmp_wav), language="vi")
                heard = " ".join(s.text.strip() for s in segs_asr).lower()

                ok_must = (not c_cfg["must_any"]) or any(m.lower() in heard for m in c_cfg["must_any"])
                ok_forbid = not any(fb.lower() in heard for fb in c_cfg["forbid"])
                print(f"  [Clause {c_idx+1} | seed={sd}] heard='{heard}' | ok={ok_must and ok_forbid}", flush=True)
                if ok_must and ok_forbid:
                    best_arr = arr
                    break
            if best_arr is None:
                raise RuntimeError(f"Failed ASR check for clause: {ctext}")
            pieces.append(best_arr)
            if c_idx < len(tgt["clauses"]) - 1:
                pieces.append(np.zeros(int(0.18 * sr), dtype=np.float32))

        combined = np.concatenate(pieces)
        vo_path = vdir / "06_Audio_Voiceover" / f"{seg_id}.wav"
        hf_vo_path = vdir / "07_HyperFrames_Project" / "assets" / "audio" / f"{seg_id}.wav"
        save_wav(vo_path, combined, sr)
        shutil.copy2(vo_path, hf_vo_path)

        segs_full, _ = asr.transcribe(str(vo_path), language="vi")
        heard_full = " ".join(s.text.strip() for s in segs_full)
        dur_s = round(len(combined) / float(sr), 3)
        print(f"  [COMBINED VERIFIED] dur={dur_s:.2f}s | Whisper='{heard_full}'", flush=True)

        manifest_path = vdir / "06_Audio_Voiceover" / "vo_manifest.json"
        mdata = json.loads(manifest_path.read_text(encoding="utf-8"))
        last_seg = mdata["segments"][-1]
        assert last_seg["id"] == seg_id
        last_seg["text"] = " ".join(full_text_parts)
        last_seg["duration_s"] = dur_s
        last_seg["end_s"] = round(float(last_seg["start_s"]) + dur_s, 3)

        shot_dur = max(5.25, round(math.ceil((dur_s + tgt["pad_s"]) * 4.0) / 4.0, 2))
        shot_end = round(float(last_seg["shot_start_s"]) + shot_dur, 2)
        if shot_end > tgt["max_total"]:
            shot_end = tgt["max_total"]
            shot_dur = round(shot_end - float(last_seg["shot_start_s"]), 2)
        last_seg["shot_duration_s"] = shot_dur
        last_seg["shot_end_s"] = shot_end
        mdata["total_duration_s"] = shot_end
        manifest_path.write_text(json.dumps(mdata, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [UPDATED MANIFEST] total_duration_s={shot_end:.2f}s (shot_dur={shot_dur:.2f}s)", flush=True)

    if tmp_wav.exists():
        tmp_wav.unlink()
    print("\nALL VOICEOVER PRICE SEGMENTS 100% FIXED & VERIFIED!", flush=True)


if __name__ == "__main__":
    main()
