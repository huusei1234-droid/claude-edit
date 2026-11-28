"""
Ngày 01 (24/11/2026) — Tạo Bảng Ảnh Tham Chiếu trên ChatGPT Dự án HTPM (3 Tab song song, tự xóa chat tạm)
- Khóa cứng 100% gương mặt Chị Hằng (MAU_CHI_HANG_PORTRAIT.png)
- BẮT BUỘC đổi trang phục sang Bộ 01 của Ngày 01: Blazer trắng kem chiết eo + Áo lụa hồng phấn cổ đổ + Khuyên tai ngọc trai nhỏ (0% giữ áo cardigan len màu be gốc!)
- Gồm 8 cảnh Dọc 9:16 cho Video USP 'Viên Đặt LT Plus' (LT_S01..LT_S08) + 1 ảnh Key Visual 1:1 cho Bài Thiết Kế 'Gel Phụ Khang' (GPK_KV)
- Tích hợp Watcher IndexedDB tự động lấy ảnh gốc full-res ngay cả khi Canvas không có node export:folder!
"""
import json
import os
import shutil
import sys
import threading
import time
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from ai_ref_video import (
    stage_local_ref_image_once,
    generate_ref_images_parallel_batch,
    export_canvas_nodes_to_files,
    get_canvas_state,
)

PROJ_DIR = Path(r"d:\AI\full studio\output\htpm-d01-ltplus-261124")
ING_DIR = PROJ_DIR / "01_ChatGPT_Ingredients"
ING_DIR.mkdir(parents=True, exist_ok=True)

BRAND_KIT = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma")
CH_HANG_PATH = str(BRAND_KIT / "ambassadors_models" / "MAU_CHI_HANG_PORTRAIT.png")
LT_COMBO_PATH = str(BRAND_KIT / "products_cutout_png" / "SP_LT_PLUS_COMBO_CUTOUT.png")
LT_OPEN_PATH = str(BRAND_KIT / "products_cutout_png" / "SP_LT_PLUS_OPENBOX_CUTOUT.png")

UD_BLOB_DIR = Path(r"C:\Users\Hang thu\AppData\Roaming\infinite-canvas-flow\IndexedDB\http_127.0.0.1_3100.indexeddb.blob")

# Khóa mặt Chị Hằng 100% + Thay trang phục Bộ 01 Ngày 24/11
CHAR_OUTFIT_DAY01 = (
    "[CHARACTER LOCK — CHI HANG]: Keep the EXACT SAME graceful 36-year-old Vietnamese woman from the first reference portrait "
    "with 100% identical facial identity: soft full-oval face, luminous fair rosy realistic skin texture, warm expressive dark-brown eyes "
    "with natural double eyelids, softly arched dark-brown eyebrows, refined nose, warm radiant smile with coral-rose lips, "
    "voluminous dark-brown softly wavy hair parted slightly off-center. "
    "[DAILY OUTFIT SWAP LOCK — DAY 01]: COMPLETELY REPLACE the beige oatmeal knit cardigan and inner ribbed top from the reference photo "
    "with DAY 01 EXECUTIVE OUTFIT: a tailored cream-ivory fitted blazer worn open over a soft blush-pink silk cowl-neck blouse, "
    "and delicate small pearl stud earrings. NEVER keep the beige knit cardigan from the reference image. "
)

CINE_916 = "Vertical 9:16 4K photorealistic commercial cinematography, ARRI Alexa Mini LF, 50mm f/1.8 prime lens. "


def list_image_blobs(min_mtime: float):
    out = {}
    if not UD_BLOB_DIR.exists():
        return out
    for f in UD_BLOB_DIR.rglob("*"):
        if not f.is_file():
            continue
        try:
            st = f.stat()
            if st.st_mtime >= min_mtime and st.st_size > 180_000:
                head = f.read_bytes()[:16]
                if b"ftyp" in head:
                    continue
                im = Image.open(f)
                w, h = im.size
                if max(w, h) >= 900:
                    out[str(f)] = (int(f.name, 16), st.st_mtime, st.st_size, f, (w, h))
        except Exception:
            pass
    return out


def main():
    ch_id = stage_local_ref_image_once(CH_HANG_PATH, "ch_hang_d01", x=120, y=120)
    lt_combo_id = stage_local_ref_image_once(LT_COMBO_PATH, "pr_lt_combo", x=120, y=520)

    specs = [
        {
            "shot_id": "LT_S01",
            "ref_tag": "lt_s01_ref",
            "ratio": "9:16",
            "reference_node_ids": [ch_id],
            "prompt": (
                CINE_916 + CHAR_OUTFIT_DAY01
                + "Medium shot in a sunlit modern glass office at 9:30 AM. She sits at a clean light oak desk holding her smartphone "
                "with a subtle thoughtful, slightly worried expression after looking up feminine health symptoms online. "
                "Frame her head and body in the lower two-thirds (top of hair strictly below Y=46%), leaving a bright, airy sunlit "
                "cream-and-blush window bokeh sky in the upper 45% for the 3D opening title."
            ),
        },
        {
            "shot_id": "LT_S02",
            "ref_tag": "lt_s02_ref",
            "ratio": "9:16",
            "reference_node_ids": [ch_id],
            "prompt": (
                CINE_916 + CHAR_OUTFIT_DAY01
                + "Medium shot in a modern sunlit office workspace late in the afternoon after sitting for 8 hours at a sleek laptop desk. "
                "She pauses work with a subtle expression of quiet fatigue, discomfort, and lost confidence, one hand resting gently near her lap. "
                "Soft warm neutral office bokeh background."
            ),
        },
        {
            "shot_id": "LT_S03",
            "ref_tag": "lt_s03_ref",
            "ratio": "9:16",
            "reference_node_ids": [],
            "prompt": (
                "Vertical 9:16 4K luxury feminine-care 3D CGI commercial metaphor (international Comfort & luxury skincare aesthetic, "
                "100% tasteful, pure, and serene). Delicate translucent blush-pink silk waves and crystal-clear pure water ripples "
                "gently cradling a blooming pale-pink lotus flower with floating pearl-gold light droplets in the lower two-thirds, "
                "while airy luminous ivory-rose light mist fills the upper third negative space."
            ),
        },
        {
            "shot_id": "LT_S04",
            "ref_tag": "lt_s04_ref",
            "ratio": "9:16",
            "reference_node_ids": [ch_id, lt_combo_id],
            "prompt": (
                CINE_916 + CHAR_OUTFIT_DAY01
                + "Medium shot in an airy sunlit luxury living room accented with fresh pink peonies and warm cream drapery. "
                "She smiles warmly and reassuringly at the camera while gently holding the exact pastel-pink LT PLUS HẰNG THU box "
                "and white cylindrical bottle from the second reference image at chest-to-waist height so both her face and the pink product "
                "remain 100% clear and unobstructed."
            ),
        },
        {
            "shot_id": "LT_S05",
            "ref_tag": "lt_s05_ref",
            "ratio": "9:16",
            "reference_node_ids": [lt_combo_id],
            "prompt": (
                "Vertical 9:16 4K high-end commercial product hero packshot photography. Place the exact pastel-pink rectangular box "
                "and matching white cylindrical LT PLUS HẰNG THU bottle from the reference image side-by-side in the lower-middle third "
                "(Y=52%..84%) on a luminous white-and-rose-quartz marble podium surrounded by crystal-clear soothing water ripples "
                "and soft dewy pink petals. Leave the entire upper half (Y=0%..46%) as an airy, bright pastel blush-and-ivory sunlit bokeh sky."
            ),
        },
        {
            "shot_id": "LT_S06",
            "ref_tag": "lt_s06_ref",
            "ratio": "9:16",
            "reference_node_ids": [],
            "prompt": (
                "Vertical 9:16 4K macro botanical sensory world commercial photography. In the lower two-thirds, arrange golden Hoàng bá "
                "herbal bark slices, fresh blooming white-and-gold Kim ngân hoa (honeysuckle) flowers, dewy green Trầu không (betel) leaves, "
                "tender Trà xanh tea leaves, and crystal-clear pure dew droplets on a wet white-and-blush marble stone bathed in warm morning sunbeams. "
                "Keep the upper third (Y=0%..40%) soft luminous ivory-and-rose bokeh."
            ),
        },
        {
            "shot_id": "LT_S07",
            "ref_tag": "lt_s07_ref",
            "ratio": "9:16",
            "reference_node_ids": [ch_id],
            "prompt": (
                CINE_916 + CHAR_OUTFIT_DAY01
                + "Medium shot walking gracefully along a sunlit modern garden terrace lined with soft blooming pink roses in bokeh. "
                "She walks forward with relaxed shoulders and a radiant, relieved, joyful smile full of feminine confidence and fresh morning energy. "
                "Warm golden rim-light on her wavy dark-brown hair."
            ),
        },
        {
            "shot_id": "LT_S08",
            "ref_tag": "lt_s08_ref",
            "ratio": "9:16",
            "reference_node_ids": [ch_id, lt_combo_id],
            "prompt": (
                CINE_916 + CHAR_OUTFIT_DAY01
                + "Commercial TVC Brand End-Card composition: Position the woman gracefully in the LEFT half of the frame (X=6%..52%, head below Y=28%), "
                "smiling radiantly at the camera while presenting the pastel-pink LT PLUS HẰNG THU box and white bottle from the second reference image "
                "on a clean white marble counter in the lower-left foreground. Keep the entire UPPER-RIGHT half (X=48%..96%, Y=10%..54%) as a bright, "
                "uncluttered pastel blush-and-ivory sunlit bokeh space for the brand end-card lockup."
            ),
        },
        {
            "shot_id": "GPK_KV",
            "ref_tag": "gpk_kv_ref",
            "ratio": "1:1",
            "reference_node_ids": [ch_id],
            "prompt": (
                "Square 1:1 4K luxury beauty & feminine-care editorial key visual photography, ARRI Alexa Mini LF, 50mm f/1.8. "
                + CHAR_OUTFIT_DAY01
                + "Position Chị Hằng gracefully on the LEFT side of the square frame (X=4%..54%), standing beside an elegant sunlit white marble "
                "skincare vanity with soft blurred glass serum bottles in the background, smiling warmly and confidently at the camera. "
                "Keep the entire RIGHT half of the frame (X=52%..98%) as an open, bright, airy pastel blush-pink and cream-ivory marble pedestal "
                "and soft sunlit bokeh space (empty table surface on the lower-right) ready for compositing a real product box."
            ),
        },
    ]

    wanted_tags = {s["ref_tag"] for s in specs}
    baseline_time = time.time() - 1.0
    seen_blobs = set(list_image_blobs(baseline_time - 7200).keys())
    seen_success_tags = set()
    matched_blobs = {}
    stop_flag = threading.Event()

    def _img_watcher():
        pending_tags = []
        pending_blobs = []
        while not stop_flag.is_set():
            try:
                cur_blobs = list_image_blobs(baseline_time)
                new_b = [v for k, v in cur_blobs.items() if k not in seen_blobs]
                new_b.sort(key=lambda x: (x[0], x[1]))
                for binfo in new_b:
                    seen_blobs.add(str(binfo[3]))
                    pending_blobs.append(binfo)

                _, cnodes = get_canvas_state()
                for n in cnodes.values():
                    if n.get("type") == "image":
                        t = (n.get("title") or "").strip()
                        if t in wanted_tags and t not in seen_success_tags and (n.get("metadata") or {}).get("status") == "success":
                            seen_success_tags.add(t)
                            pending_tags.append((time.time(), t, n["id"]))

                while pending_tags and pending_blobs:
                    _, t, _ = pending_tags.pop(0)
                    binfo = pending_blobs.pop(0)
                    matched_blobs[t] = binfo[3]
                    print(f"  [ImgWatcher] Paired {t} -> IndexedDB blob {binfo[3].name} ({binfo[4][0]}x{binfo[4][1]})", flush=True)
            except Exception:
                pass
            time.sleep(1.0)

    wt = threading.Thread(target=_img_watcher, daemon=True)
    wt.start()

    try:
        results = generate_ref_images_parallel_batch(specs, max_workers=3)
    finally:
        time.sleep(2.5)
        stop_flag.set()
        wt.join(timeout=5.0)

    node_to_dest = {}
    summary = []
    for sp, (tag, nid, prov) in zip(specs, results):
        sid = sp["shot_id"]
        dest = ING_DIR / f"{sid}_ref.png"
        node_to_dest[nid] = str(dest)
        summary.append({
            "shot_id": sid,
            "ref_tag": tag,
            "ratio": sp["ratio"],
            "img_node_id": nid,
            "provider": prov,
            "local_path": str(dest),
        })

    # Try export:folder first if present; otherwise save directly from IndexedDB watcher!
    exported = {}
    try:
        exported = export_canvas_nodes_to_files(node_to_dest, timeout_s=45)
    except Exception as e:
        print(f"  [ExportFolder Bypass] Using direct IndexedDB full-res blobs ({e})", flush=True)

    rem_blobs = [v for k, v in list_image_blobs(baseline_time).items() if v[3] not in matched_blobs.values()]
    rem_blobs.sort(key=lambda x: x[0])

    for item in summary:
        dest_p = Path(item["local_path"])
        if dest_p.exists() and dest_p.stat().st_size > 50_000:
            continue
        bp = matched_blobs.get(item["ref_tag"])
        if not bp and rem_blobs:
            bp = rem_blobs.pop(0)[3]
        if bp and bp.exists():
            Image.open(bp).convert("RGB").save(dest_p, format="PNG")
            print(f"  [Saved IndexedDB PNG] {item['shot_id']} -> {dest_p.name}", flush=True)

    # Build visual QA Contact Sheet of all 9 plates
    tw, th = 340, 560
    sheet = Image.new("RGB", (tw * 5, th * 2), (24, 16, 20))
    draw = ImageDraw.Draw(sheet)
    for i, item in enumerate(summary):
        p = Path(item["local_path"])
        if not p.exists():
            continue
        c, rr = i % 5, i // 5
        im = Image.open(p).convert("RGB")
        im.thumbnail((tw - 12, th - 34), Image.Resampling.LANCZOS)
        ox = c * tw + (tw - im.width) // 2
        oy = rr * th + 28 + (th - 34 - im.height) // 2
        sheet.paste(im, (ox, oy))
        draw.text((c * tw + 10, rr * th + 6), f"{item['shot_id']} ({item['provider']})", fill=(255, 215, 230))
    sheet_path = PROJ_DIR / "ref_board_d01_sheet.jpg"
    sheet.save(sheet_path, quality=90)
    print(f"[REF QA SHEET] {sheet_path}", flush=True)

    out_meta = PROJ_DIR / "ref_board_manifest.json"
    out_meta.write_text(
        json.dumps(
            {
                "anchors": {"ch_hang": ch_id, "lt_combo": lt_combo_id},
                "shots": summary,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[SAVED] {out_meta}", flush=True)


if __name__ == "__main__":
    main()
