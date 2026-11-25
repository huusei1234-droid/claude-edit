"""
Tổng hợp Voiceover giọng 'THANH THANH TVC' trên GPU NVIDIA RTX 4070 CUDA
cho BỘ 4 VIDEO BOJOMI CHẠY BỘ (4 trang phục chạy bộ đẹp riêng biệt, 100% chuẩn luật TPBS).
"""
import os, sys, json, math, wave, shutil
from pathlib import Path
import numpy as np

PACK_ROOT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE")
VOICE_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "voice_profile_thanh_thanh_tvc"
AUDIO_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "audio_bgm_sfx"
FONTS_BUNDLE_DIR = PACK_ROOT / "03_TAI_NGUYEN_DUNG_CHUNG" / "fonts_tvc_vi"
VS_PROJ = Path(r"d:\AI\full studio\voice-studio")
WORK_DIR = Path(r"d:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Bo_4_Video_Bojomi_Chay_Bo")

VIDEOS = {
    "bojomi_run_01_khung_xuong": {
        "title": "Bojomi Chạy Bộ 01 — Khung Xương Vững Vàng Canxi Tảo Biển Aquamin F",
        "final_name": "261124 AVPM Bojomi Chay Bo 01 - Khung Xuong Vung Vang Aquamin F final.mp4",
        "segments": [
            ("vo_01", "Chạy bền mỗi ngày, đừng quên chăm khung xương từ bên trong!"),
            ("vo_02", "Mỗi ki lô mét chạy bộ, đôi chân và khung xương phải chịu lực liên tục nên rất cần bổ sung Canxi đúng chuẩn."),
            ("vo_03", "Bojomi của An Vượng Pharma sử dụng nguồn Canxi hữu cơ từ tảo biển đỏ Aquamin F lành tính, dễ hấp thu."),
            ("vo_04", "Mỗi gói hai mươi gam cung cấp bốn trăm mười bảy phẩy sáu miligam Canxi, đồng hành cùng bảy trăm bảy mươi chín phẩy bốn IU Vitamin D3 và K2 MK-7."),
            ("vo_05", "Chỉ cần pha với hai trăm mililit nước ấm sáu mươi độ là có ngay ly ngũ cốc hương Vani thơm béo, nhẹ bụng sau buổi chạy."),
            ("vo_06", "Duy trì đều đặn mỗi sáng giúp khung xương vững vàng, tự tin chinh phục mọi cung đường mới."),
            ("vo_07", "Bojomi năm trăm hai mươi nghìn hộp mười bốn gói. Nhắn Bojomi nhận ngay ưu đãi mua ba tặng một đến hết ba mươi tháng mười một nhé!"),
        ],
    },
    "bojomi_run_02_bo3_d3_k2": {
        "title": "Bojomi Chạy Bộ 02 — Bộ 3 Dẫn Đường Ca – D3 – K2 MK-7 Nhẹ Bụng",
        "final_name": "261124 AVPM Bojomi Chay Bo 02 - Bo 3 Canxi D3 K2 MK7 Nhe Bung final.mp4",
        "segments": [
            ("vo_01", "Uống Canxi cho dân chạy bộ, nhớ phải đủ bộ đôi D3 và K2 MK-7!"),
            ("vo_02", "Nhiều bạn chạy bộ uống Canxi thông thường nhưng vẫn dễ nặng bụng, khó hấp thu vì thiếu bộ dẫn đường khoa học."),
            ("vo_03", "Ngũ cốc dinh dưỡng Bojomi kết hợp trọn bộ kiềng ba chân: Canxi tảo biển Aquamin F, Vitamin D3 và Vitamin K2 MK-7."),
            ("vo_04", "Công thức chuẩn trong một gói gồm bốn trăm mười bảy phẩy sáu miligam Canxi, bảy trăm bảy mươi chín phẩy bốn IU D3 và một trăm sáu mươi chín phẩy tám microgam K2 MK-7."),
            ("vo_05", "Dạng bột ngũ cốc vị Vani thanh béo, hòa tan mịn trong hai trăm mililit nước ấm sáu mươi độ, uống cực kỳ nhẹ bụng."),
            ("vo_06", "Nhờ hấp thu tốt và êm dạ, mỗi buổi chạy sáng đều tràn đầy hứng khởi và bền bỉ hơn hẳn."),
            ("vo_07", "Đừng bỏ lỡ ưu đãi sinh nhật Droppii: mua ba Bojomi tặng ngay một hộp năm trăm hai mươi nghìn. Nhắn Bojomi để nhận tư vấn ngay nhé!"),
        ],
    },
    "bojomi_run_03_collagen_deo_dai": {
        "title": "Bojomi Chạy Bộ 03 — Bổ Sung 201,4mg Collagen Cho Bước Chạy Dẻo Dai",
        "final_name": "261124 AVPM Bojomi Chay Bo 03 - 201mg Collagen Buoc Chay Deo Dai final.mp4",
        "segments": [
            ("vo_01", "Muốn chạy bộ bền bỉ lâu dài, chỉ Canxi thôi là chưa đủ đâu!"),
            ("vo_02", "Khi vận động và sải bước thường xuyên, cơ thể cần đồng thời cả Canxi cho khung xương lẫn Collagen cho độ dẻo dai."),
            ("vo_03", "Bojomi của An Vượng Pharma mang đến công thức kép thông minh ngay trong một ly ngũ cốc thơm ngon mỗi sáng."),
            ("vo_04", "Bên cạnh bốn trăm mười bảy phẩy sáu miligam Canxi tảo biển Aquamin F, mỗi gói còn bổ sung hai trăm lẻ một phẩy bốn miligam Collagen."),
            ("vo_05", "Hòa một gói hai mươi gam với hai trăm mililit nước ấm sáu mươi độ, hương Vani dịu nhẹ hoàn toàn không ngán."),
            ("vo_06", "Một thói quen nhỏ sau mỗi buổi tập sân giúp từng sải chân luôn linh hoạt, dẻo dai và tràn đầy sức sống."),
            ("vo_07", "Hộp mười bốn gói chỉ năm trăm hai mươi nghìn, đang có chương trình mua ba tặng một. Nhắn Bojomi ngay hôm nay bạn nhé!"),
        ],
    },
    "bojomi_run_04_pha_30s_uu_dai": {
        "title": "Bojomi Chạy Bộ 04 — Pha 30 Giây Tiếp Năng Lượng & Quà Tặng 520K",
        "final_name": "261124 AVPM Bojomi Chay Bo 04 - Pha 30 Giay Sau Chay Tang 520K final.mp4",
        "segments": [
            ("vo_01", "Vừa hoàn thành năm ki lô mét chạy sáng, nạp gì vừa nhanh vừa đủ chất?"),
            ("vo_02", "Sau khi chạy bộ, nhiều người hay bỏ bữa sáng hoặc uống tạm đồ ngọt khiến cơ thể nhanh đuối sức."),
            ("vo_03", "Bí kíp của hội yêu chạy bộ chính là một gói Bojomi nhỏ gọn hai mươi gam mang theo ngay trong túi tập."),
            ("vo_04", "Chỉ mất ba mươi giây pha cùng hai trăm mililit nước ấm sáu mươi độ, nạp ngay Canxi tảo biển Aquamin F, D3, K2 MK-7 và Collagen."),
            ("vo_05", "Vị ngũ cốc Vani thơm béo ấm bụng, tan mịn không vón cục, uống xong vừa no nhẹ vừa sảng khoái để bắt đầu ngày mới."),
            ("vo_06", "Cả nhóm chạy bộ hay gia đình cùng dùng mỗi sáng đều cực kỳ tiện lợi, mang đi tập hay đi giải chạy đều gọn gàng."),
            ("vo_07", "Ưu đãi đến hết ba mươi tháng mười một: mua ba Bojomi tặng ngay một hộp năm trăm hai mươi nghìn. Nhắn Bojomi nhận quà liền tay nhé!"),
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
