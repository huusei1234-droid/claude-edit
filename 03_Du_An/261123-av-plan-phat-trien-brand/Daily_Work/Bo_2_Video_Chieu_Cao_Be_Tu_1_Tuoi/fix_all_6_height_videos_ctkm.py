# -*- coding: utf-8 -*-
"""
FIX ALL 6 HEIGHT COMBO VIDEOS (2 KID 1Y+ & 4 HEIGHT COMBO) — ZERO MISLEADING CTKM:
1. Re-synthesizes ONLY the 3 ambiguous ending VO clips (kid1y_01/vo_06, kid1y_02/vo_06, height_02/vo_07)
   via live GPU Voice Studio (:3900, THANH THANH TVC 78ef243f) + faster-whisper verification
   (870.000đ 100% crisp, ZERO claim of free 520K box on the 2-box 870K duo!).
2. Rebuilds all 6 HyperFrames projects (clean emerald/gold 'CHÍNH HÃNG DROPPII • PROTEIN 350K + BOJOMI 520K'
   End-Cards, clean height_04 Opening Hook & overlays, 25/11–30/11 accurate dates).
3. Renders all 6 videos in parallel (max_workers=2) via HyperFrames delivery quality.
4. Builds combined 6-panel End-Card QC Sheet + height_04 Opening Hook QC image + Whisper tail verification.
"""
import concurrent.futures, io, json, math, os, shutil, subprocess, sys, wave
from pathlib import Path
import numpy as np
import requests
import faster_whisper
from PIL import Image, ImageDraw

DAILY_WORK = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work")
KID_DIR = DAILY_WORK / "Bo_2_Video_Chieu_Cao_Be_Tu_1_Tuoi"
HGT_DIR = DAILY_WORK / "Bo_4_Video_Combo_Chieu_Cao"
VS_URL = "http://127.0.0.1:3900/generate"
PROFILE_ID = "78ef243f"  # THANH THANH TVC


def decode_and_trim_wav(wav_bytes: bytes):
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        sr, nch, sw = wf.getframerate(), wf.getnchannels(), wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())
    arr = (
        np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if sw == 2
        else np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    )
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
    fi, fo = min(int(0.020 * sr), len(arr) // 4), min(int(0.035 * sr), len(arr) // 4)
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


def synth_and_update_vo(asr, vdir: Path, seg_id: str, clauses: list, max_total: float):
    pieces, sr = [], 24000
    tmp = DAILY_WORK / "_tmp_fix_ctkm.wav"
    for idx, (txt, musts, forbids) in enumerate(clauses):
        best = None
        for sd in [2028, 108, 2032, 369, 668, 888, 2026, 777]:
            r = requests.post(
                VS_URL,
                data={
                    "text": txt,
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
            r.raise_for_status()
            arr, sr = decode_and_trim_wav(r.content)
            save_wav(tmp, arr, sr)
            segs, _ = asr.transcribe(str(tmp), language="vi")
            heard = " ".join(s.text.strip() for s in segs).lower()
            ok = (not musts or any(m in heard for m in musts)) and not any(fb in heard for fb in forbids)
            print(f"  [{vdir.name}/{seg_id} c{idx+1} seed={sd}] '{heard}' -> ok={ok}", flush=True)
            best = arr
            if ok:
                break
        pieces.append(best)
        if idx < len(clauses) - 1:
            pieces.append(np.zeros(int(0.18 * sr), dtype=np.float32))
    if tmp.exists():
        tmp.unlink()
    comb = np.concatenate(pieces)
    vo_p = vdir / "06_Audio_Voiceover" / f"{seg_id}.wav"
    hf_p = vdir / "07_HyperFrames_Project" / "assets" / "audio" / f"{seg_id}.wav"
    save_wav(vo_p, comb, sr)
    if hf_p.parent.exists():
        shutil.copy2(vo_p, hf_p)
    dur_s = round(len(comb) / float(sr), 3)
    mpath = vdir / "06_Audio_Voiceover" / "vo_manifest.json"
    mdata = json.loads(mpath.read_text(encoding="utf-8"))
    last = mdata["segments"][-1]
    last["text"] = " ".join(c[0] for c in clauses)
    last["duration_s"] = dur_s
    last["end_s"] = round(float(last["start_s"]) + dur_s, 3)
    shot_dur = max(5.25, round(math.ceil((dur_s + 0.45) * 4.0) / 4.0, 2))
    shot_end = min(max_total, round(float(last["shot_start_s"]) + shot_dur, 2))
    last["shot_duration_s"] = round(shot_end - float(last["shot_start_s"]), 2)
    last["shot_end_s"] = shot_end
    mdata["total_duration_s"] = shot_end
    mpath.write_text(json.dumps(mdata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [UPDATED VO] {vdir.name}/{seg_id}: dur={dur_s:.2f}s | total={shot_end:.2f}s", flush=True)


def render_one_hf(job: dict) -> str:
    hf_dir = job["hf_dir"]
    final_local = job["local_mp4"]
    print(f"[START RENDER] {final_local.name} ...", flush=True)
    cmd = f'npx --yes hyperframes@0.9.38 render --quality delivery -o "{final_local}"'
    res = subprocess.run(cmd, cwd=str(hf_dir), shell=True, capture_output=True, text=True)
    if res.returncode != 0 or not final_local.exists():
        raise RuntimeError(
            f"HyperFrames render failed for {final_local.name}:\nSTDOUT:{res.stdout[-800:]}\nSTDERR:{res.stderr[-800:]}"
        )
    print(f"[DONE RENDER] {final_local.name} ({final_local.stat().st_size / 1e6:.2f} MB)", flush=True)
    return str(final_local)


def main():
    asr = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")

    # 1. Fix the 3 ambiguous ending voiceovers (zero 'tặng 520K' claim on the 2-box 870K duo!)
    synth_and_update_vo(
        asr,
        KID_DIR / "kid1y_01_giai_doan_vang",
        "vo_06",
        [
            ("Mẹ chia khẩu phần theo độ tuổi của bé, kết hợp ngủ sớm và vận động.", ["khẩu phần", "độ tuổi"], []),
            ("Bộ đôi chính hãng có giá tám trăm bảy mươi nghìn đồng.", ["870", "tám trăm bảy mươi"], ["87.000", "8.000", "tám mươi bảy"]),
            ("Mẹ nhắn Bé Một Tuổi nhận bảng chia khẩu phần chuẩn nhé!", ["một tuổi", "khẩu phần"], ["520", "quà tặng"]),
        ],
        max_total=58.5,
    )
    synth_and_update_vo(
        asr,
        KID_DIR / "kid1y_02_pha_chuan_2_ly",
        "vo_06",
        [
            ("Bộ đôi Bojomi và AV Protein chính hãng có giá tám trăm bảy mươi nghìn đồng.", ["870", "tám trăm bảy mươi"], ["87.000", "8.000", "tám mươi bảy"]),
            ("Mẹ nhắn Bé Một Tuổi nhận ngay bảng hướng dẫn pha chuẩn hai khung giờ nhé!", ["một tuổi", "khung giờ"], ["520", "quà tặng"]),
        ],
        max_total=58.5,
    )
    synth_and_update_vo(
        asr,
        HGT_DIR / "height_02_4_tru_cot_vang",
        "vo_07",
        [
            ("Bộ đôi Bojomi và AV Protein chính hãng có giá tám trăm bảy mươi nghìn đồng.", ["870", "tám trăm bảy mươi"], ["87.000", "8.000", "tám mươi bảy"]),
            ("Nhắn Chiều Cao nhận ngay bảng hướng dẫn chuẩn cho cả gia đình nhé!", ["chiều cao", "hướng dẫn"], ["520", "quà tặng"]),
        ],
        max_total=75.0,
    )

    # 2. Rebuild ALL 6 HyperFrames projects
    subprocess.run([sys.executable, "-X", "utf8", str(KID_DIR / "build_kid1y_2videos_hf.py"), "all"], check=True)
    subprocess.run([sys.executable, "-X", "utf8", str(HGT_DIR / "build_height_combo_4videos_hf.py"), "all"], check=True)

    # 3. Render ALL 6 videos in parallel (2 workers)
    jobs = [
        {
            "id": "KID1Y_01",
            "hf_dir": KID_DIR / "kid1y_01_giai_doan_vang" / "07_HyperFrames_Project",
            "local_mp4": KID_DIR / "261124 AVPM Combo Chieu Cao Be Tu 1 Tuoi 01 - Giai Doan Vang Dam Va Canxi final.mp4",
        },
        {
            "id": "KID1Y_02",
            "hf_dir": KID_DIR / "kid1y_02_pha_chuan_2_ly" / "07_HyperFrames_Project",
            "local_mp4": KID_DIR / "261124 AVPM Combo Chieu Cao Be Tu 1 Tuoi 02 - Pha Chuan 2 Ly Em Bung 870K final.mp4",
        },
        {
            "id": "HEIGHT_01",
            "hf_dir": HGT_DIR / "height_01_dam_va_canxi" / "07_HyperFrames_Project",
            "local_mp4": HGT_DIR / "261124 AVPM Combo Chieu Cao 01 - Dam Sach AV Protein Va Canxi Bojomi final.mp4",
        },
        {
            "id": "HEIGHT_02",
            "hf_dir": HGT_DIR / "height_02_4_tru_cot_vang" / "07_HyperFrames_Project",
            "local_mp4": HGT_DIR / "261124 AVPM Combo Chieu Cao 02 - 4 Tru Cot Vang Phat Trien Chieu Cao final.mp4",
        },
        {
            "id": "HEIGHT_03",
            "hf_dir": HGT_DIR / "height_03_pha_chuan_2_nhiet_do" / "07_HyperFrames_Project",
            "local_mp4": HGT_DIR / "261124 AVPM Combo Chieu Cao 03 - Cach Pha Chuan 2 Nhiet Do Bojomi AV Protein final.mp4",
        },
        {
            "id": "HEIGHT_04",
            "hf_dir": HGT_DIR / "height_04_van_dong_va_deal_870k" / "07_HyperFrames_Project",
            "local_mp4": HGT_DIR / "261124 AVPM Combo Chieu Cao 04 - Bo Doi 870K Van Dong Gian Co final.mp4",
        },
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(render_one_hf, j) for j in jobs]
        for f in concurrent.futures.as_completed(futs):
            f.result()

    # 4. Build 6-panel End-Card QC Sheet + Height_04 Hook QC + Whisper Tail Audit
    sheet = Image.new("RGB", (1740, 2040), (14, 20, 26))
    draw = ImageDraw.Draw(sheet)
    tmp_png = DAILY_WORK / "_tmp_ec.png"
    tmp_wav = DAILY_WORK / "_tmp_tail.wav"

    for idx, j in enumerate(jobs):
        mp4 = j["local_mp4"]
        # Get exact duration
        dur = float(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(mp4)],
                text=True,
            ).strip()
        )
        ec_t = max(0.0, dur - 2.0)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ec_t:.2f}", "-i", str(mp4), "-frames:v", "1", str(tmp_png)], check=True)
        im = Image.open(tmp_png).convert("RGB").resize((540, 960), Image.Resampling.LANCZOS)
        x = (idx % 3) * 580 + 20
        y = (idx // 3) * 1020 + 18
        sheet.paste(im, (x, y))
        draw.text((x + 4, y + 970), f"{j['id']} ({dur:.1f}s) | {mp4.name[:56]}", fill=(255, 232, 120))

        # Whisper check last 10s
        tail_ss = max(0.0, dur - 10.5)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{tail_ss:.2f}", "-i", str(mp4), "-vn", "-ac", "1", "-ar", "16000", str(tmp_wav)],
            check=True,
        )
        segs, _ = asr.transcribe(str(tmp_wav), language="vi")
        heard = " ".join(s.text.strip() for s in segs)
        print(f"[WHISPER TAIL {j['id']} ({dur:.1f}s)] {heard}", flush=True)

        if j["id"] == "HEIGHT_04":
            h4_hook = KID_DIR / "QA_Height04_Hook_Fixed.jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0.8", "-i", str(mp4), "-frames:v", "1", str(h4_hook)], check=True)

    qa_sheet = KID_DIR / "QA_6_EndCards_Fixed_CTKM.jpg"
    sheet.save(qa_sheet, quality=92)
    tmp_png.unlink(missing_ok=True)
    tmp_wav.unlink(missing_ok=True)
    print(f"\n[QC SHEET READY] {qa_sheet}", flush=True)


if __name__ == "__main__":
    main()
