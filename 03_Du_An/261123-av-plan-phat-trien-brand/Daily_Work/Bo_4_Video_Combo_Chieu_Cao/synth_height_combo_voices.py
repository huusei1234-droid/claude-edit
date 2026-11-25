"""
Tổng hợp Voiceover giọng 'THANH THANH TVC' trên GPU NVIDIA RTX 4070 CUDA
cho BỘ 4 VIDEO COMBO PHÁT TRIỂN CHIỀU CAO (BOJOMI + AV PROTEIN) — 100% CHUẨN LUẬT TPBS AN VƯỢNG × DROPPII:
- Không cam kết tăng bao nhiêu cm, nhấn mạnh khoa học 4 trụ cột: Dinh dưỡng (Đạm + Canxi D3 K2) + Giấc ngủ sớm + Vận động + Di truyền
- Nhắc pha RIÊNG 2 nhiệt độ chuẩn bao bì (AV Protein 20-40°C giữ lợi khuẩn B-3; Bojomi 60°C tan mịn)
- Nhắc xem kỹ nhãn và tham vấn theo từng độ tuổi.
"""
import os, sys, json, math, wave, shutil
from pathlib import Path
import numpy as np

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
VS_PROJ = Path(r"d:\AI\full studio\voice-studio")
WORK_DIR = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Bo_4_Video_Combo_Chieu_Cao")

VIDEOS = {
    "height_01_dam_va_canxi": {
        "title": "Combo Chiều Cao 01 — Đạm Sạch AV Protein & Canxi Tảo Biển Bojomi",
        "final_name": "261124 AVPM Combo Chieu Cao 01 - Dam Sach AV Protein Va Canxi Bojomi final.mp4",
        "segments": [
            ("vo_01", "Muốn xây nền tảng vóc dáng cao ráo, uống mình Canxi thôi liệu đã đủ chưa?"),
            ("vo_02", "Thực tế, để khung xương và cơ thể phát triển hài hòa, bên cạnh Canxi cần có thêm Đạm sạch làm nguyên liệu xây dựng mỗi ngày."),
            ("vo_03", "Đó là lý do bộ đôi Bojomi và AV Protein của An Vượng Pharma luôn được nhiều gia đình lựa chọn đồng hành."),
            ("vo_04", "AV Protein cung cấp hai mươi hai phẩy không năm gam Đạm thực vật cùng một nghìn sáu trăm ba mươi hai miligam L-Leucine, kết hợp Inulin và lợi khuẩn B-3 giúp êm bụng."),
            ("vo_05", "Còn Bojomi bổ sung bốn trăm mười bảy phẩy sáu miligam Canxi tảo biển Aquamin F cùng Vitamin D3, K2 MK-7 và hai trăm lẻ một phẩy bốn miligam Collagen."),
            ("vo_06", "Khi kết hợp đủ dinh dưỡng, ngủ sớm trước hai mươi hai giờ và vận động thể thao đều đặn, nền tảng khung xương và vóc dáng sẽ được chăm sóc toàn diện nhất."),
            ("vo_07", "Bộ đôi Bojomi năm trăm hai mươi nghìn và AV Protein ba trăm năm mươi nghìn, tổng tám trăm bảy mươi nghìn. Nhắn Chiều Cao để được tư vấn đúng độ tuổi nhé!"),
        ],
    },
    "height_02_4_tru_cot_vang": {
        "title": "Combo Chiều Cao 02 — 4 Trụ Cột Vàng Phát Triển Chiều Cao Khoa Học",
        "final_name": "261124 AVPM Combo Chieu Cao 02 - 4 Tru Cot Vang Phat Trien Chieu Cao final.mp4",
        "segments": [
            ("vo_01", "Chăm chiều cao khoa học cho cả nhà, đừng chỉ tìm một loại uống lẻ rồi trông chờ phép màu!"),
            ("vo_02", "Chiều cao và vóc dáng phụ thuộc vào bốn trụ cột: bữa ăn cân đối, giấc ngủ sâu trước hai mươi hai giờ, vận động đều đặn và yếu tố di truyền."),
            ("vo_03", "Trong đó, dinh dưỡng mỗi ngày đóng vai trò nền tảng với bộ đôi chủ lực từ An Vượng Pharma: Bojomi và AV Protein."),
            ("vo_04", "Bojomi mang đến kiềng ba chân Canxi tảo biển Aquamin F, Vitamin D3 và K2 MK-7 hỗ trợ chăm sóc hệ xương vững chắc."),
            ("vo_05", "Song song đó, AV Protein bổ sung đạm đậu Hà Lan và đạm gạo lành tính, dễ tiêu hóa, giúp duy trì khối cơ khỏe khoắn cho người hay vận động."),
            ("vo_06", "Gia đình luôn nhớ đọc kỹ nhãn sản phẩm và điều chỉnh khẩu phần phù hợp theo từng độ tuổi cùng chế độ ăn đa dạng hằng ngày."),
            ("vo_07", "Đang có ưu đãi sinh nhật Droppii đến hết ba mươi tháng mười một: quà tặng Bojomi lên tới năm trăm hai mươi nghìn. Nhắn Chiều Cao nhận bảng hướng dẫn ngay nhé!"),
        ],
    },
    "height_03_pha_chuan_2_nhiet_do": {
        "title": "Combo Chiều Cao 03 — Bí Kíp Pha Riêng 2 Nhiệt Độ Chuẩn Bao Bì",
        "final_name": "261124 AVPM Combo Chieu Cao 03 - Cach Pha Chuan 2 Nhiet Do Bojomi AV Protein final.mp4",
        "segments": [
            ("vo_01", "Dùng bộ đôi Bojomi và AV Protein, tuyệt đối đừng đổ chung vào một ly nước sôi nhé!"),
            ("vo_02", "Nhiều gia đình hay tiện tay pha chung hai gói một lần, nhưng mỗi sản phẩm lại có ngưỡng nhiệt độ riêng để giữ trọn dưỡng chất."),
            ("vo_03", "Hãy chia lịch uống khoa học hai khung giờ trong ngày để cơ thể hấp thu nhẹ bụng và tối ưu nhất."),
            ("vo_04", "Buổi sáng, pha AV Protein với nước mát hoặc nước ấm hai mươi đến bốn mươi độ giúp bảo toàn lợi khuẩn B-3 và chất xơ Inulin, nạp ngay hai mươi hai phẩy không năm gam đạm sạch."),
            ("vo_05", "Đến bữa phụ chiều hoặc sau buổi tập, pha một gói Bojomi hai mươi gam với hai trăm mililit nước ấm sáu mươi độ cho bột ngũ cốc vị Vani tan mịn thơm béo."),
            ("vo_06", "Uống đúng nhiệt độ, đúng khung giờ, kết hợp ngủ sớm và tập bật nhảy giãn cơ mỗi ngày sẽ giúp cơ thể tràn đầy sức sống."),
            ("vo_07", "Bộ đôi có giá tám trăm bảy mươi nghìn đồng. Ưu đãi mua ba Bojomi hoặc năm AV Protein tặng ngay Bojomi năm trăm hai mươi nghìn đồng, nhắn Chiều Cao ngay nhé!"),
        ],
    },
    "height_04_van_dong_va_deal_870k": {
        "title": "Combo Chiều Cao 04 — Đồng Hành Giãn Cơ Vận Động & Deal Quà 520K",
        "final_name": "261124 AVPM Combo Chieu Cao 04 - Bo Doi 870K Van Dong Gian Co Tang 520K final.mp4",
        "segments": [
            ("vo_01", "Tập giãn cơ, nhảy dây hay chơi thể thao mỗi ngày, bổ sung gì để cơ và xương phát triển bền vững?"),
            ("vo_02", "Khi cơ thể vận động nhiều mà thiếu đạm và Canxi, các bạn rất dễ nhanh mỏi và khó đạt phong độ vóc dáng như mong muốn."),
            ("vo_03", "Bộ đôi dinh dưỡng nền tảng Bojomi và AV Protein giúp nạp trọn bộ dưỡng chất sạch chỉ trong vài chục giây pha mỗi ngày."),
            ("vo_04", "AV Protein với hai mươi hai phẩy không năm gam đạm thực vật và một nghìn sáu trăm ba mươi hai miligam L-Leucine hỗ trợ phục hồi và săn chắc khối cơ."),
            ("vo_05", "Bojomi tiếp sức bốn trăm mười bảy phẩy sáu miligam Canxi tảo biển Aquamin F, Vitamin D3, K2 MK-7 và hai trăm lẻ một phẩy bốn miligam Collagen chăm khung xương dẻo dai."),
            ("vo_06", "Pha riêng hai ly thơm béo dễ uống, phù hợp cho thanh thiếu niên theo tư vấn độ tuổi, người yêu thể thao và cả gia đình cùng chăm sức khỏe chủ động."),
            ("vo_07", "Bộ đôi Bojomi và AV Protein có giá tám trăm bảy mươi nghìn đồng. Đến hết ba mươi tháng mười một, mua năm AV Protein hoặc ba Bojomi tặng ngay một Bojomi năm trăm hai mươi nghìn đồng. Nhắn Chiều Cao nhận ưu đãi ngay nhé!"),
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
                speed=float(params.get("speed", 1.07)),
            )
            sr = int(getattr(backend, "sample_rate", 24000))
            arr = trim_and_normalize(wav_t, sr)
            dur_s = round(len(arr) / float(sr), 3)
            seg_path = vo_dir / f"{seg_id}.wav"
            save_wav(seg_path, arr, sr)
            shutil.copy2(seg_path, hf_aud / f"{seg_id}.wav")

            shot_dur_s = max(3.50, round(math.ceil((dur_s + 0.56) * 4.0) / 4.0, 2))
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

        min_end = max(5.50, round(math.ceil((manifest[-1]["duration_s"] + 1.05) * 4.0) / 4.0, 2))
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
