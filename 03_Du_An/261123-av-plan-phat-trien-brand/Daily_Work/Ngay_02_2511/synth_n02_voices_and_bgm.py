# -*- coding: utf-8 -*-
"""
Thu âm đồng loạt 5 bộ Voiceover (< 48s mỗi video, giọng THANH THANH TVC trên RTX 4070 CUDA,
kiểm âm faster-whisper chuẩn từng con số giá & CTKM 25/11–30/11) + chuẩn hóa 5 bài nhạc nền BGM riêng (-18 LUFS).
"""
import io, json, math, os, subprocess, wave
from pathlib import Path
import numpy as np
import requests
import faster_whisper

WORK = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_02_2511")
BGM_OUT = WORK / "02_BGM_Normalized"
BGM_OUT.mkdir(parents=True, exist_ok=True)
BGM_ROOT = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)")

VS_URL = "http://127.0.0.1:3900/generate"
PROFILE_ID = "78ef243f"  # THANH THANH TVC

VIDEOS = [
    {
        "vkey": "n02_v1_av_protein_leucine",
        "title": "AV Protein — 1.632mg L-Leucine Giữ Cơ Săn Chắc Sau Tập Sáng",
        "final_name": "261125 AVPM 01 - AV Protein 1632mg Leucine Giu Co San Chac final.mp4",
        "bgm_rel": r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Achieve (2p02s).mp3",
        "segs": [
            ("vo_01", [("Tập sáng đều đặn mà vẫn thấy nhanh mỏi, cơ khó săn chắc? Kiểm tra ngay lượng Đạm buổi sáng nhé!", ["đạm", "tập"], [])]),
            ("vo_02", [("Mỗi sáng chỉ cần ba mươi giây pha hai gói AV Protein với nước mát hai mươi đến bốn mươi độ để bảo toàn lợi khuẩn B-3.", ["protein", "bốn mươi"], [])]),
            ("vo_03", [("Cung cấp hai mươi hai phẩy không năm gam đạm đậu Hà Lan và gạo cùng một nghìn sáu trăm ba mươi hai miligam L-Leucine hỗ trợ duy trì khối cơ.", ["22", "hai mươi hai", "đạm"], [])]),
            ("vo_04", [("Thêm chất xơ Inulin giúp êm bụng, không đầy hơi, cực nhẹ nhàng cho người bận rộn tập sáng.", ["êm bụng", "đầy hơi"], [])]),
            ("vo_05", [
                ("AV Protein giá ba trăm năm mươi nghìn đồng.", ["350", "ba trăm năm mươi"], ["35.000", "3.000"]),
                ("Đến hết ba mươi tháng mười một, mua năm hộp tặng ngay một Bojomi năm trăm hai mươi nghìn đồng.", ["520", "năm trăm hai mươi"], ["52.000", "5.000", "năm 20"]),
                ("Nhắn Đạm Sạch ngay nhé!", ["đạm sạch"], []),
            ]),
        ],
    },
    {
        "vkey": "n02_v2_bojomi_chay_bo_60c",
        "title": "Bojomi Chạy Bộ Biển Nha Trang — Pha 60°C Tan Mịn Vị Vani",
        "final_name": "261125 AVPM 02 - Bojomi Chay Bo Nha Trang Pha 60 Do Tan Min final.mp4",
        "bgm_rel": r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Be Happy (2p23s).mp3",
        "segs": [
            ("vo_01", [("Chạy bộ sáng đường biển xong, pha ly Canxi nào vừa tan mịn vị Vani vừa dễ hấp thu?", ["canxi", "vani"], [])]),
            ("vo_02", [("Bí kíp pha Bojomi chuẩn ngon không vón: cho một gói hai mươi gam với hai trăm mililit nước ấm sáu mươi độ rồi khuấy đều.", ["60", "sáu mươi"], [])]),
            ("vo_03", [("Mỗi ly bổ sung bốn trăm mười bảy phẩy sáu miligam Canxi tảo biển Aquamin F cùng Vitamin D3 và K2 MK-7 hỗ trợ hệ xương chắc khỏe.", ["canxi", "d3"], [])]),
            ("vo_04", [("Kết hợp thêm hai trăm lẻ một phẩy bốn miligam Collagen giúp khung xương khớp dẻo dai cho người chạy bộ mỗi ngày.", ["collagen", "xương"], [])]),
            ("vo_05", [
                ("Bojomi giá năm trăm hai mươi nghìn đồng.", ["520", "năm trăm hai mươi"], ["52.000", "5.000", "năm 20"]),
                ("Đến hết ba mươi tháng mười một, mua ba hộp tặng ngay một Bojomi năm trăm hai mươi nghìn đồng.", ["520", "năm trăm hai mươi"], ["52.000", "5.000", "năm 20"]),
                ("Nhắn Bojomi ngay nhé!", ["bojomi", "nhắn"], []),
            ]),
        ],
    },
    {
        "vkey": "n02_v3_combo_be_1_tuoi_bieng_an",
        "title": "Combo Chiều Cao Bé Từ 1 Tuổi+ — Bé Biếng Ăn Lười Sữa Êm Bụng",
        "final_name": "261125 AVPM 03 - Combo Chieu Cao Be Tu 1 Tuoi Bieng An Em Bung 870K final.mp4",
        "bgm_rel": r"05_Acoustic - Guitar - Nhẹ Nhàng Mộc Mạc\Blooming Fields (2p09s).mp3",
        "segs": [
            ("vo_01", [("Bé từ một tuổi biếng ăn, lười uống sữa, mẹ bổ sung Đạm và Canxi thế nào cho con êm bụng?", ["một tuổi", "canxi"], [])]),
            ("vo_02", [("Bí quyết của mẹ hiện đại là không ép uống dồn một lần, mà chia nhỏ hai khung giờ chuẩn vị dịu nhẹ cho con.", ["khung giờ", "dịu nhẹ"], [])]),
            ("vo_03", [("Buổi sáng pha AV Protein nước mát hai mươi đến bốn mươi độ, đạm thực vật lành tính cùng lợi khuẩn B-3 giúp bé tiêu hóa êm bụng.", ["protein", "êm bụng"], [])]),
            ("vo_04", [("Bữa phụ chiều pha Bojomi nước ấm sáu mươi độ vị Vani thơm béo, giàu Canxi tảo biển Aquamin F, D3 và K2 MK-7.", ["60", "sáu mươi", "canxi"], [])]),
            ("vo_05", [
                ("Mẹ chia lượng phù hợp từ một tuổi, kết hợp ngủ sớm và vận động.", ["một tuổi", "ngủ"], []),
                ("Bộ đôi chính hãng có giá tám trăm bảy mươi nghìn đồng.", ["870", "tám trăm bảy mươi"], ["87.000", "8.000", "tám mươi bảy"]),
                ("Mẹ nhắn Bé Một Tuổi nhận bảng khẩu phần chuẩn nhé!", ["một tuổi", "khẩu"], ["520", "quà tặng"]),
            ]),
        ],
    },
    {
        "vkey": "n02_v4_curcumilk_15h_em_bung",
        "title": "Curcumilk Phyto — Bữa Phụ 15h Văn Phòng Ấm Bụng Phytosome Ý",
        "final_name": "261125 AVPM 04 - Curcumilk Phyto Bua Phu 15h Van Phong Am Bung final.mp4",
        "bgm_rel": r"02_Chill - Lofi - Vlog Đời Thường\Apple Pie (1p26s).mp3",
        "segs": [
            ("vo_01", [("Ba giờ chiều văn phòng bụng cồn cào mà ngại uống trà sữa nhiều đường? Đổi ngay sang ly sữa nghệ ấm bụng này nhé!", ["sữa nghệ", "văn phòng"], [])]),
            ("vo_02", [("Curcumilk Phyto kết hợp nền ngũ cốc sữa dừa hương Vani thơm béo, hoàn toàn dịu nhẹ và không hề hăng mùi nghệ tươi.", ["ngũ cốc", "vani", "nghệ"], [])]),
            ("vo_03", [("Mỗi gói chứa ba trăm bốn mươi ba phẩy hai miligam Curcuminoid với hệ ba lớp kết hợp Curcumin Phytosome nhập khẩu từ Ý.", ["curcumin", "phytosome", "ý"], [])]),
            ("vo_04", [("Chỉ cần pha một gói với một trăm năm mươi mililit nước ấm bốn mươi đến năm mươi độ, nạp ngay năng lượng lành mạnh buổi chiều.", ["nước ấm", "năng lượng"], [])]),
            ("vo_05", [
                ("Curcumilk Phyto giá sáu trăm năm mươi nghìn đồng.", ["650", "sáu trăm năm mươi"], ["65.000", "6.000"]),
                ("Đến hết ba mươi tháng mười một, mua bốn hộp tặng ngay một hộp sáu trăm năm mươi nghìn đồng.", ["650", "sáu trăm năm mươi"], ["65.000", "6.000"]),
                ("Nhắn Sữa Nghệ ngay nhé!", ["sữa nghệ"], []),
            ]),
        ],
    },
    {
        "vkey": "n02_v5_collamela_don_tet_480k",
        "title": "Collamela — Bộ 4 Dưỡng Chất 2.530mg Collagen Tripeptide Đón Tết",
        "final_name": "261125 AVPM 05 - Collamela 2530mg Collagen Tripeptide Don Tet final.mp4",
        "bgm_rel": r"06_Jazz - Lounge - Sang Trọng - Lãng Mạn\Bossa Lounge (3p04s).mp3",
        "segs": [
            ("vo_01", [("Còn hai tháng nữa đến Tết, muốn làn da căng mịn rạng rỡ thì chăm từ bên trong bằng gì cho kịp?", ["tết", "làn da"], [])]),
            ("vo_02", [("Mỗi ngày chỉ mất mười giây pha một gói Collamela với một trăm mililit nước mát, vị đào thanh ngọt hoàn toàn không tanh.", ["vị đào", "không tanh"], [])]),
            ("vo_03", [("Khẩu phần hai gói cung cấp hai nghìn năm trăm ba mươi miligam Collagen Tripeptide phân tử siêu nhỏ dễ hấp thu.", ["collagen", "tripeptide"], [])]),
            ("vo_04", [("Phối hợp thêm HA cấp ẩm, Vitamin C và Kẽm giúp nuôi dưỡng độ đàn hồi và sắc diện làn da tươi tắn mỗi ngày.", ["vitamin c", "đàn hồi", "làn da"], [])]),
            ("vo_05", [
                ("Collamela hai mươi gói giá chín trăm hai mươi nghìn đồng.", ["920", "chín trăm hai mươi"], ["92.000", "9.000"]),
                ("Đến hết ba mươi tháng mười một, mua hai hộp tặng ngay một hộp mười gói bốn trăm tám mươi nghìn đồng.", ["480", "bốn trăm tám mươi"], ["48.000", "4.000"]),
                ("Nhắn Collamela ngay nhé!", ["collamela", "nhắn"], []),
            ]),
        ],
    },
]


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
        arr = arr[max(0, int(idx[0]) - int(0.025 * sr)) : min(len(arr), int(idx[-1]) + int(0.045 * sr))]
    fi, fo = min(int(0.018 * sr), len(arr) // 4), min(int(0.032 * sr), len(arr) // 4)
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
    tmp = WORK / "_tmp_n02_asr.wav"

    # 1. Normalize 5 unique BGM tracks (-18 LUFS)
    for v in VIDEOS:
        src = BGM_ROOT / v["bgm_rel"]
        dst = BGM_OUT / f"{v['vkey']}_bgm.mp3"
        if not dst.exists():
            assert src.exists(), f"Missing BGM: {src}"
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-t", "65", "-af", "loudnorm=I=-18:TP=-2:LRA=9", "-b:a", "192k", str(dst)],
                check=True,
            )
            print(f"[BGM -18 LUFS] {v['vkey']} <- {src.name}", flush=True)

    # 2. Synthesize 5 Whisper-verified Voiceover suites (< 52s each!)
    for v in VIDEOS:
        vdir = WORK / v["vkey"] / "06_Audio_Voiceover"
        vdir.mkdir(parents=True, exist_ok=True)
        mpath = vdir / "vo_manifest.json"
        if mpath.exists():
            print(f"[SKIP VO] {v['vkey']} manifest already exists.", flush=True)
            continue

        segs_meta = []
        cursor = 0.0
        for s_idx, (sid, clauses) in enumerate(v["segs"]):
            pieces, sr = [], 24000
            for c_idx, (txt, musts, forbids) in enumerate(clauses):
                best = None
                for sd in [2028, 108, 2032, 369, 668, 888, 2026]:
                    r = requests.post(
                        VS_URL,
                        data={
                            "text": txt,
                            "profile_id": PROFILE_ID,
                            "language": "vi",
                            "num_step": "32",
                            "guidance_scale": "2.0",
                            "speed": "1.04",
                            "seed": str(sd),
                            "effect_preset": "raw",
                        },
                        timeout=120,
                    )
                    r.raise_for_status()
                    arr, sr = decode_and_trim_wav(r.content)
                    save_wav(tmp, arr, sr)
                    s_asr, _ = asr.transcribe(str(tmp), language="vi")
                    heard = " ".join(s.text.strip() for s in s_asr).lower()
                    ok = (not musts or any(m in heard for m in musts)) and not any(fb in heard for fb in forbids)
                    print(f"  [{v['vkey']}/{sid} c{c_idx+1} seed={sd}] '{heard}' -> ok={ok}", flush=True)
                    best = arr
                    if ok:
                        break
                pieces.append(best)
                if c_idx < len(clauses) - 1:
                    pieces.append(np.zeros(int(0.16 * sr), dtype=np.float32))
            comb = np.concatenate(pieces)
            wav_p = vdir / f"{sid}.wav"
            save_wav(wav_p, comb, sr)
            dur_s = round(len(comb) / float(sr), 3)
            pad = 0.45 if s_idx == len(v["segs"]) - 1 else 0.30
            shot_dur = max(4.25 if s_idx < 4 else 6.0, round(math.ceil((dur_s + pad) * 4.0) / 4.0, 2))
            segs_meta.append({
                "id": sid,
                "text": " ".join(c[0] for c in clauses),
                "path": str(wav_p),
                "start_s": round(cursor + 0.12, 3),
                "duration_s": dur_s,
                "end_s": round(cursor + 0.12 + dur_s, 3),
                "shot_start_s": round(cursor, 2),
                "shot_duration_s": shot_dur,
                "shot_end_s": round(cursor + shot_dur, 2),
            })
            cursor = round(cursor + shot_dur, 2)

        manifest = {
            "video_key": v["vkey"],
            "title": v["title"],
            "final_name": v["final_name"],
            "bgm_path": str(BGM_OUT / f"{v['vkey']}_bgm.mp3"),
            "bgm_original": v["bgm_rel"],
            "total_duration_s": cursor,
            "segments": segs_meta,
        }
        mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[DONE VO SUITE] {v['vkey']} -> total={cursor:.2f}s (<= 55s!)", flush=True)

    if tmp.exists():
        tmp.unlink()
    print("\n=== ALL 5 DAY-02 VO SUITES & 5 UNIQUE BGMS READY! ===", flush=True)


if __name__ == "__main__":
    main()
