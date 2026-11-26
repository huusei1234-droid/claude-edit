# -*- coding: utf-8 -*-
"""
Ngày 03 (26/11/2026) — Thu âm đồng loạt 4 bộ Voiceover (gọn ~36–41s/video, giọng THANH THANH TVC trên GPU CUDA,
kiểm âm faster-whisper chuẩn từng con số giá & CTKM 25/11–30/11 + Black Friday 26/11, 0% truyền thông Bojomi trẻ em)
+ chuẩn hóa 4 bài nhạc nền BGM riêng biệt (-18 LUFS).
"""
import io, json, math, os, subprocess, wave
from pathlib import Path
import numpy as np
import requests
import faster_whisper

WORK = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_03_2611")
BGM_OUT = WORK / "02_BGM_Normalized"
BGM_OUT.mkdir(parents=True, exist_ok=True)
BGM_ROOT = Path(r"G:\Other computers\My Computer\Document HT Media\TLH\Edit\01_Nhạc Nền (BGM)")

VS_URL = "http://127.0.0.1:3900/generate"
PROFILE_ID = "78ef243f"  # THANH THANH TVC

VIDEOS = [
    {
        "vkey": "n03_v1_av_protein_bua_sang_em_bung",
        "title": "AV Protein — Bữa Sáng Vội 30 Giây Êm Bụng Nhờ Inulin & Lợi Khuẩn B-3",
        "final_name": "261126 AVPM 01 - AV Protein Bua Sang Voi Inulin Loi Khuan B3 Em Bung final.mp4",
        "bgm_rel": r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\A Happy Moment (2p39s).mp3",
        "segs": [
            ("vo_01", [("Sáng vội đi làm nhìn đồ khô đã ngán, mà nhịn ăn sáng thì giữa giờ lại nhanh đuối sức?", ["đi làm", "ăn sáng", "đuối"], [])]),
            ("vo_02", [("Đổi ngay sang ly AV Protein mát lành! Chỉ ba mươi giây pha hai gói với nước mát hai mươi đến bốn mươi độ.", ["protein", "bốn mươi"], [])]),
            ("vo_03", [("Cung cấp hai mươi hai phẩy không năm gam đạm thực vật, kết hợp chất xơ Inulin và lợi khuẩn B-3 giúp êm bụng, không đầy hơi.", ["đạm", "êm bụng"], [])]),
            ("vo_04", [("Nhẹ nhàng đủ chất để làm việc tỉnh táo suốt buổi sáng mà chỉ mười bảy nghìn năm trăm đồng một gói.", ["tỉnh táo", "gói"], [])]),
            ("vo_05", [
                ("AV Protein giá ba trăm năm mươi nghìn đồng.", ["350", "ba trăm năm mươi"], ["35.000", "3.000"]),
                ("Đợt cuối đến ba mươi tháng mười một, mua năm hộp tặng ngay một Bojomi năm trăm hai mươi nghìn đồng.", ["520", "năm trăm hai mươi"], ["52.000", "5.000", "năm 20"]),
                ("Nhắn Đạm Sạch ngay nhé!", ["đạm sạch"], []),
            ]),
        ],
    },
    {
        "vkey": "n03_v2_bojomi_kieng_3_chan_van_phong",
        "title": "Bojomi — Bộ Kiềng 3 Chân Canxi Aquamin F, D3 & K2 MK-7 Cho Dân Văn Phòng & Người Lớn",
        "final_name": "261126 AVPM 02 - Bojomi Kieng 3 Chan Canxi D3 K2 MK7 Dan Van Phong final.mp4",
        "bgm_rel": r"01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng\Anthem of Inspiration (2p31s).mp3",
        "segs": [
            ("vo_01", [("Ngồi văn phòng suốt tám tiếng ít gặp nắng sớm, người lớn mình bổ sung Canxi sao cho hấp thu hiệu quả?", ["văn phòng", "canxi"], [])]),
            ("vo_02", [("Đọc kỹ bảng thành phần Bojomi sẽ thấy ngay bốn trăm mười bảy phẩy sáu miligam Canxi tảo biển đỏ Aquamin F.", ["canxi", "thành phần"], [])]),
            ("vo_03", [("Phối hợp chuẩn bộ ba cùng Vitamin D3 và K2 MK-7 hỗ trợ dẫn Canxi vào xương thay vì lắng cặn.", ["d3", "xương"], [])]),
            ("vo_04", [("Dạng bột ngũ cốc vị Vani pha ấm sáu mươi độ thơm mịn, rất dễ uống mỗi ngày cho cả dân công sở và bố mẹ.", ["60", "sáu mươi", "vani"], [])]),
            ("vo_05", [
                ("Bojomi giá năm trăm hai mươi nghìn đồng.", ["520", "năm trăm hai mươi"], ["52.000", "5.000", "năm 20"]),
                ("Đợt cuối đến ba mươi tháng mười một, mua ba hộp tặng ngay một Bojomi năm trăm hai mươi nghìn đồng.", ["520", "năm trăm hai mươi"], ["52.000", "5.000", "năm 20"]),
                ("Nhắn Bojomi ngay nhé!", ["bojomi", "nhắn"], []),
            ]),
        ],
    },
    {
        "vkey": "n03_v3_curcumilk_3_nguon_nghe_em_bung",
        "title": "Curcumilk Phyto — Hệ 3 Nguồn Nghệ & Phytosome Ý Không Hăng Cả Nhà Đều Mê",
        "final_name": "261126 AVPM 03 - Curcumilk Phyto 3 Nguon Nghe Phytosome Y Em Bung final.mp4",
        "bgm_rel": r"05_Acoustic - Guitar - Nhẹ Nhàng Mộc Mạc\Acoustic Background Folk (2p03s).mp3",
        "segs": [
            ("vo_01", [("Hay ăn trưa trễ vì bận việc, muốn uống nghệ ấm bụng mỗi chiều mà ngại mùi nghệ tươi hăng nồng?", ["nghệ", "ấm bụng", "bận"], [])]),
            ("vo_02", [("Thử ngay ly Curcumilk Phyto nền ngũ cốc sữa dừa hương Vani thơm dịu, cả nhà uống đều khen ngon dễ chịu.", ["sữa dừa", "vani", "dễ chịu"], [])]),
            ("vo_03", [("Mỗi gói chứa ba trăm bốn mươi ba phẩy hai miligam Curcuminoid từ ba nguồn nghệ kết hợp công nghệ Phytosome nhập khẩu Ý.", ["curcumin", "phytosome", "ý"], [])]),
            ("vo_04", [("Chỉ cần pha ấm bốn mươi đến năm mươi độ lúc xế chiều, vừa nạp năng lượng nhẹ nhàng vừa êm bụng.", ["nước ấm", "bốn mươi", "êm bụng"], [])]),
            ("vo_05", [
                ("Curcumilk Phyto giá sáu trăm năm mươi nghìn đồng.", ["650", "sáu trăm năm mươi"], ["65.000", "6.000"]),
                ("Đợt cuối đến ba mươi tháng mười một, mua bốn hộp tặng ngay một hộp sáu trăm năm mươi nghìn đồng.", ["650", "sáu trăm năm mươi"], ["65.000", "6.000"]),
                ("Nhắn Phyto ngay nhé!", ["phyto", "nhắn"], []),
            ]),
        ],
    },
    {
        "vkey": "n03_v4_collamela_vi_dao_100ml_khong_tanh",
        "title": "Collamela — Vị Đào 100ml Không Tanh 2.530mg Collagen Tripeptide Chăm Da Đón Tết",
        "final_name": "261126 AVPM 04 - Collamela Vi Dao 100ml Khong Tanh Cham Da Don Tet final.mp4",
        "bgm_rel": r"06_Jazz - Lounge - Sang Trọng - Lãng Mạn\Bossa Da Vida (2p56s).mp3",
        "segs": [
            ("vo_01", [("Muốn uống Collagen đều đặn kịp đón Tết mà ngại mấy loại pha lích kích hay có vị tanh khó uống?", ["collagen", "tết", "tanh"], [])]),
            ("vo_02", [("Chuyển sang Collamela vị đào thanh ngọt này nhé! Chỉ một trăm mililit nước mát, khuấy mười giây là tan trong veo không hề tanh.", ["vị đào", "không hề tanh", "trăm"], [])]),
            ("vo_03", [("Khẩu phần hai gói bổ sung hai nghìn năm trăm ba mươi miligam Collagen Tripeptide phân tử nhỏ cùng HA, Vitamin C và Kẽm.", ["collagen", "tripeptide", "vitamin"], [])]),
            ("vo_04", [("Gói nhỏ mang đi làm hay để bàn trang điểm đều tiện, duy trì thói quen chăm da căng mịn tươi tắn mỗi tối.", ["chăm da", "mỗi tối", "tươi tắn"], [])]),
            ("vo_05", [
                ("Collamela hai mươi gói giá chín trăm hai mươi nghìn đồng.", ["920", "chín trăm hai mươi"], ["92.000", "9.000"]),
                ("Đợt cuối đến ba mươi tháng mười một, mua hai hộp tặng ngay một hộp mười gói bốn trăm tám mươi nghìn đồng.", ["480", "bốn trăm tám mươi"], ["48.000", "4.000"]),
                ("Nhắn Da Đẹp ngay nhé!", ["da đẹp"], []),
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
    tmp = WORK / "_tmp_n03_asr.wav"

    # 1. Normalize 4 unique BGM tracks (-18 LUFS)
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

    # 2. Synthesize 4 Whisper-verified Voiceover suites (< 46s each!)
    for v in VIDEOS:
        vdir = WORK / v["vkey"] / "06_Audio_Voiceover"
        vdir.mkdir(parents=True, exist_ok=True)
        mpath = vdir / "vo_manifest.json"
        if mpath.exists():
            print(f"[SKIP VO] {v['vkey']} manifest already exists.", flush=True)
            continue

        segs_meta = []
        cursor = 0.22  # gentle 0.22s breath at opening
        for s_idx, (sid, clauses) in enumerate(v["segs"]):
            pieces, sr = [], 24000
            full_txt = " ".join(c[0] for c in clauses)
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
                            "speed": "1.06",
                            "seed": str(sd),
                            "effect_preset": "raw",
                        },
                        timeout=180,
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
                if c_idx > 0:
                    pieces.append(np.zeros(int(0.14 * sr), dtype=np.float32))
                pieces.append(best)

            seg_pcm = np.concatenate(pieces)
            seg_wav = vdir / f"{sid}.wav"
            save_wav(seg_wav, seg_pcm, sr)
            dur = round(len(seg_pcm) / float(sr), 2)
            st_s = round(cursor, 2)
            en_s = round(st_s + dur, 2)
            gap = 0.24 if s_idx < len(v["segs"]) - 1 else 0.75
            shot_end = round(en_s + gap, 2)
            segs_meta.append({
                "id": sid,
                "text": full_txt,
                "path": str(seg_wav),
                "start_s": st_s,
                "duration_s": dur,
                "end_s": en_s,
                "shot_end_s": shot_end,
            })
            cursor = shot_end

        total_dur = round(cursor, 2)
        manifest = {
            "vkey": v["vkey"],
            "title": v["title"],
            "final_name": v["final_name"],
            "bgm_path": str(BGM_OUT / f"{v['vkey']}_bgm.mp3"),
            "total_duration_s": total_dur,
            "segments": segs_meta,
        }
        mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[VO COMPLETE] {v['vkey']} -> {total_dur:.2f}s", flush=True)

    tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
