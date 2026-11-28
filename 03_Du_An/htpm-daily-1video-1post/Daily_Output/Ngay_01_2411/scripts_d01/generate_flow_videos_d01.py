"""
Ngày 01 (24/11/2026) — Tạo 8 Clip Chuyển Động Dọc 9:16 ONLY trên Google Flow (flow::flow-omni-1.2-flash)
- BẮT BUỘC chế độ THÀNH PHẦN (video_mode="reference" / Ingredients) nối trực tiếp ảnh tham chiếu Bộ 01 Chị Hằng.
- Zero Lip-Sync tuyệt đối (không nhép miệng nói tiếng Anh).
- Watcher 1.0s bắt chính xác MP4 raw từ IndexedDB + transcode CFR 24fps 1080x1920 bằng GPU RTX 4070 (h264_nvenc).
- Xuất kèm bảng thước đo tọa độ mặt ruler_8shots.jpg (vạch Y mỗi 100px + vạch Vùng An Toàn 250px / 860px / 1545px) để đặt chữ 0% che mặt!
"""
import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from ai_ref_video import (
    generate_videos_parallel_batch,
    get_canvas_state,
    cleanup_exported_canvas_nodes,
)

PROJ_DIR = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124")
RAW_VID_DIR = PROJ_DIR / "03_Flow_Raw_Videos"
HF_VID_DIR = PROJ_DIR / "07_HyperFrames_Project" / "assets" / "videos"
RAW_VID_DIR.mkdir(parents=True, exist_ok=True)
HF_VID_DIR.mkdir(parents=True, exist_ok=True)

UD_BLOB_DIR = Path(r"C:\Users\Hang thu\AppData\Roaming\infinite-canvas-flow\IndexedDB\http_127.0.0.1_3100.indexeddb.blob")

ZERO_LIP = " Natural calm breathing, lips gently closed or softly smiling, zero speaking, zero lip-syncing, no on-screen text."

MOTION_PROMPTS = {
    "LT_S01": (
        "Slow subtle cinematic push-in in the sunlit modern office; the graceful Vietnamese woman in the cream blazer and blush silk blouse "
        "glances thoughtfully at her smartphone screen with a subtle worried expression, then lets out a quiet breath; warm sunlight bokeh shimmers." + ZERO_LIP
    ),
    "LT_S02": (
        "Gentle empathetic camera drift in the late-afternoon office; she pauses at her laptop desk with a subtle expression of 8-hour sitting fatigue "
        "and quiet self-consciousness, shifting slightly in her chair with lips closed." + ZERO_LIP
    ),
    "LT_S03": (
        "Smooth 3D luxury feminine-care fluid motion: translucent blush-pink silk waves and crystal-clear pure water ripples undulate gracefully around "
        "a blooming pale-pink lotus flower as pearl-gold light droplets float upward in serene morning light."
    ),
    "LT_S04": (
        "Graceful slow dolly-in in the airy sunlit living room; she smiles warmly and reassuringly with closed lips while holding the pastel-pink "
        "LT PLUS HẰNG THU box and white bottle steadily at chest-to-waist height as soft golden sunbeams flare gently." + ZERO_LIP
    ),
    "LT_S05": (
        "Luxury commercial tabletop slow orbit and push-in on the pastel-pink LT PLUS HẰNG THU box and white bottle on the rose-quartz marble podium "
        "as crystal-clear water ripples expand softly and dewdrops glisten on pink rose petals."
    ),
    "LT_S06": (
        "Sensory macro slow-motion slider move across golden Hoàng bá bark slices, white-and-gold Kim ngân hoa blossoms, dewy green Trầu không leaves, "
        "and Trà xanh leaves as crystal dew droplets and warm morning light particles shimmer."
    ),
    "LT_S07": (
        "Smooth gimbal tracking shot along the sunlit rose garden terrace as she walks forward gracefully in her cream blazer and blush silk blouse "
        "with a radiant, relieved, confident smile and joyful feminine aura, sunlit hair swaying softly." + ZERO_LIP
    ),
    "LT_S08": (
        "Poised luxury Brand End-Card slow push-in: standing in the left half of the sunlit studio, she smiles warmly with closed lips and presents "
        "the pastel-pink LT PLUS HẰNG THU box and white bottle steadily on the marble counter while pastel blush-ivory bokeh glows in the upper-right." + ZERO_LIP
    ),
}


def list_mp4_blobs(min_mtime: float):
    out = {}
    for f in UD_BLOB_DIR.rglob("*"):
        if not f.is_file():
            continue
        try:
            st = f.stat()
            if st.st_mtime >= min_mtime and st.st_size > 250_000:
                head = f.read_bytes()[:16]
                if b"ftyp" in head:
                    out[str(f)] = (int(f.name, 16), st.st_mtime, st.st_size, f)
        except Exception:
            pass
    return out


def transcode_cfr24_nvenc(src_mp4: Path, dst_mp4: Path):
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(src_mp4),
        "-vf", "fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-r", "24", "-fps_mode", "cfr",
        "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
        "-pix_fmt", "yuv420p", "-g", "24",
        str(dst_mp4),
    ]
    subprocess.run(cmd, check=True)
    pr = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,duration", "-of", "json", str(dst_mp4)]
        ).decode("utf-8")
    )["streams"][0]
    return float(pr["duration"]), pr["r_frame_rate"]


def draw_ruler_overlay(im_1080x1920: Image.Image, label: str) -> Image.Image:
    im = im_1080x1920.copy()
    d = ImageDraw.Draw(im)
    for y in range(100, 1900, 100):
        col = (255, 70, 70) if y in (250, 1545) else ((80, 220, 255) if y == 860 else (255, 255, 160))
        w = 4 if y in (250, 860, 1545) else 2
        d.line([(0, y), (1080, y)], fill=col, width=w)
        d.rectangle([(8, y - 22), (112, y - 2)], fill=(0, 0, 0))
        d.text((14, y - 20), f"Y={y}", fill=col)
    # Draw right-bottom TikTok interaction column X=884 for Y>=860
    d.line([(884, 860), (884, 1548)], fill=(255, 80, 80), width=4)
    d.rectangle([(12, 12), (460, 58)], fill=(0, 0, 0))
    d.text((22, 22), label, fill=(140, 255, 190))
    return im


def main():
    ref_meta = json.loads((PROJ_DIR / "ref_board_manifest.json").read_text(encoding="utf-8"))
    vo_meta = json.loads((PROJ_DIR / "06_Audio_Voiceover" / "vo_manifest.json").read_text(encoding="utf-8"))
    vo_by_shot = {s["shot_id"]: s for s in vo_meta["segments"]}

    video_specs = []
    wanted_titles = set()
    shot_items = [x for x in ref_meta["shots"] if x["shot_id"].startswith("LT_S")]

    for item in shot_items:
        sid = item["shot_id"]
        sec = int(vo_by_shot[sid]["recommended_flow_gen_s"])
        mprompt = MOTION_PROMPTS[sid]
        out_title = f"vid_{sid.lower()}"
        wanted_titles.add(out_title)
        video_specs.append({
            "out_title": out_title,
            "ref_img_node_id": item["img_node_id"],
            "extra_ref_node_ids": [],
            "motion_prompt": mprompt,
            "ratio": "9:16",
            "seconds": sec,
            "video_mode": "reference",
        })

    baseline_time = time.time() - 1.0
    seen_blobs = set(list_mp4_blobs(baseline_time - 3600).keys())
    seen_success_titles = set()
    matched_blobs = {}
    stop_flag = threading.Event()

    def _watcher():
        pending_titles = []
        pending_blobs = []
        while not stop_flag.is_set():
            try:
                cur_blobs = list_mp4_blobs(baseline_time)
                new_b = [v for k, v in cur_blobs.items() if k not in seen_blobs]
                new_b.sort(key=lambda x: (x[0], x[1]))
                for binfo in new_b:
                    seen_blobs.add(str(binfo[3]))
                    pending_blobs.append(binfo)

                _, cnodes = get_canvas_state()
                for n in cnodes.values():
                    if n.get("type") == "video":
                        t = (n.get("title") or "").strip()
                        if t in wanted_titles and t not in seen_success_titles and (n.get("metadata") or {}).get("status") == "success":
                            seen_success_titles.add(t)
                            pending_titles.append((time.time(), t, n["id"]))

                while pending_titles and pending_blobs:
                    _, t, _ = pending_titles.pop(0)
                    binfo = pending_blobs.pop(0)
                    matched_blobs[t] = binfo[3]
                    print(f"  [Watcher] Paired {t} -> IndexedDB MP4 blob {binfo[3].name} ({binfo[2]} bytes)", flush=True)
            except Exception:
                pass
            time.sleep(1.2)

    wt = threading.Thread(target=_watcher, daemon=True)
    wt.start()

    try:
        vid_results = generate_videos_parallel_batch(video_specs, max_workers=4)
    finally:
        time.sleep(3.0)
        stop_flag.set()
        wt.join(timeout=5.0)

    all_new = [v for k, v in list_mp4_blobs(baseline_time).items() if v[3] not in matched_blobs.values()]
    all_new.sort(key=lambda x: x[0])

    vid_summary = []
    ruler_tiles = []
    for idx, (title, vnid, prov) in enumerate(vid_results, start=1):
        sid = f"LT_S{idx:02d}"
        blob_p = matched_blobs.get(title)
        if not blob_p and all_new:
            blob_p = all_new.pop(0)[3]
        if not blob_p or not blob_p.exists():
            raise RuntimeError(f"Missing MP4 blob for {sid} ({title})")
        raw_dst = RAW_VID_DIR / f"{sid}_raw.mp4"
        shutil.copy2(blob_p, raw_dst)
        hf_dst = HF_VID_DIR / f"{sid}.mp4"
        dur, fr = transcode_cfr24_nvenc(raw_dst, hf_dst)

        # If clip duration is slightly shorter than shot_duration_s (e.g. 8.0s VO shot vs 8.0s clip),
        # create a seamless ping-pong extended source if needed so media never freezes at tail!
        req_dur = float(vo_by_shot[sid]["shot_duration_s"]) + 0.35
        if dur < req_dur:
            ext_dst = HF_VID_DIR / f"{sid}_ext.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-y", "-v", "error",
                    "-i", str(hf_dst),
                    "-filter_complex", "[0:v]split[f][r];[r]reverse[rr];[f][rr]concat=n=2:v=1:a=0,fps=24,setsar=1[v]",
                    "-map", "[v]", "-r", "24", "-fps_mode", "cfr", "-an",
                    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
                    "-pix_fmt", "yuv420p", "-g", "24",
                    str(ext_dst),
                ],
                check=True,
            )
            shutil.move(str(ext_dst), str(hf_dst))
            dur = round(dur * 2.0, 3)

        thumb_p = RAW_VID_DIR / f"{sid}_mid.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", "1.0", "-i", str(hf_dst), "-frames:v", "1", "-q:v", "2", str(thumb_p)],
            check=True,
        )
        full_im = Image.open(thumb_p).convert("RGB")
        ruler_tiles.append(draw_ruler_overlay(full_im, f"{sid} ({dur:.1f}s)"))

        vid_summary.append({
            "shot_id": sid,
            "out_title": title,
            "vid_node_id": vnid,
            "provider": prov,
            "raw_path": str(raw_dst),
            "hf_path": str(hf_dst),
            "cfr24_duration_s": round(dur, 3),
            "r_frame_rate": fr,
        })
        print(f"  [{sid}] CFR24 NVENC OK -> {hf_dst.name} ({dur:.2f}s @ {fr})", flush=True)

    (PROJ_DIR / "flow_videos_manifest.json").write_text(json.dumps(vid_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # Save ruler_8shots.jpg (4x2 grid) for exact Face-Safe & Box-Safe Y measurement!
    tw, th = 360, 640
    sheet = Image.new("RGB", (tw * 4, th * 2), (18, 14, 18))
    for i, rim in enumerate(ruler_tiles):
        c, rr = i % 4, i // 4
        sheet.paste(rim.resize((tw - 6, th - 6), Image.Resampling.LANCZOS), (c * tw + 3, rr * th + 3))
    ruler_path = PROJ_DIR / "ruler_8shots.jpg"
    sheet.save(ruler_path, quality=90)
    print(f"[RULER QA SHEET] {ruler_path}", flush=True)

    # Clean up temporary nodes on Infinite Canvas
    to_clean = (
        [x["vid_node_id"] for x in vid_summary]
        + [x["img_node_id"] for x in ref_meta["shots"]]
        + list(ref_meta["anchors"].values())
    )
    cleanup_exported_canvas_nodes(to_clean)
    print("[CLEANUP] Temporary nodes cleaned from Infinite Canvas!", flush=True)


if __name__ == "__main__":
    main()
