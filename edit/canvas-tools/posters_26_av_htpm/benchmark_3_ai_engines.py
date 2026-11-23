# -*- coding: utf-8 -*-
"""
Benchmark 3 AI Engines head-to-head (ChatGPT vs Google Flow Nano Banana Pro vs Muse)
for generating Chị Hằng's exact rich commercial infographic style:
1. Lush scenic background ("background có hình hài")
2. Harmonized product scene with rich natural side decor ("sản phẩm có decor bên cạnh, không lệch tông, chữ bao bì không bị hư")
3. Custom AI-created icons & HUGE vivid 3D illustrations + MASSIVE clear Vietnamese typography!
"""
import base64, io, json, os, sys, time, uuid
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call
from ai_ref_video import (
    get_canvas_state,
    stage_local_ref_image_once,
    export_canvas_nodes_to_files,
    cleanup_exported_canvas_nodes,
    _outs,
    _delete_nodes_safe,
)

V3_DIR = r"d:\AI\full studio\projects\av_htpm_26_posters_v3"
BENCH_DIR = os.path.join(V3_DIR, "benchmark_3ai")
os.makedirs(BENCH_DIR, exist_ok=True)


def prepare_clean_packshot_ref(cutout_png: str, out_jpg: str) -> str:
    im = Image.open(cutout_png).convert("RGBA")
    bg = Image.new("RGBA", (im.width + 80, im.height + 80), (246, 244, 240, 255))
    bg.alpha_composite(im, dest=(40, 40))
    bg.convert("RGB").save(out_jpg, quality=95)
    return out_jpg


def run_direct_canvas_image(prompt: str, model_id: str, ratio: str, ref_ids: list, tag: str, timeout_s: int = 300):
    cfg_title = f"BENCH_{tag}_{uuid.uuid4().hex[:5]}"
    payload = {
        "prompt": prompt,
        "model": model_id,
        "size": ratio,
        "count": 1,
        "title": cfg_title,
        "referenceNodeIds": list(ref_ids),
    }
    print(f"[Bench] Launching {tag} ({model_id}) [{ratio}]...", flush=True)
    res = call("canvas_generate_image", payload)
    if not res.get("ok", True) and res.get("error"):
        print(f"[Bench] {tag} immediate error: {res.get('error')}", flush=True)
        return None, str(res.get("error"))

    t0 = time.time()
    prompt_sig = prompt[:48]
    owned = []
    while time.time() - t0 < timeout_s:
        time.sleep(6)
        cur_r, cur_nodes = get_canvas_state()
        cfgs = [n for n in cur_nodes.values() if n.get("type") == "config" and (n.get("title") or "") == cfg_title]
        txts = [n for n in cur_nodes.values() if n.get("type") == "text" and (n.get("title") or "") == cfg_title]
        img_node = None
        out_imgs = []
        if cfgs:
            out_imgs = _outs(cur_r, cur_nodes, cfgs[0]["id"], "image")
            if out_imgs:
                img_node = out_imgs[0]
        if not img_node:
            sig_imgs = [
                n for n in cur_nodes.values()
                if n.get("type") == "image" and cfg_title in ((n.get("title") or ""))
            ]
            if sig_imgs:
                img_node = sig_imgs[-1]
                out_imgs = [img_node]
        owned = [n["id"] for n in txts] + [n["id"] for n in cfgs] + [n["id"] for n in out_imgs]
        if not img_node:
            continue
        meta = img_node.get("metadata") or {}
        st = meta.get("status")
        if st == "success" and meta.get("content"):
            _delete_nodes_safe([n["id"] for n in txts] + [n["id"] for n in cfgs])
            print(f"[Bench] {tag} SUCCESS in {int(time.time()-t0)}s -> {img_node['id']}", flush=True)
            return img_node["id"], meta.get("content")
        if st == "error":
            err = meta.get("error") or "status=error"
            print(f"[Bench] {tag} ERROR: {err}", flush=True)
            _delete_nodes_safe(owned)
            return None, err
    _delete_nodes_safe(owned)
    return None, f"timeout after {timeout_s}s"


def save_data_url_or_export(nid: str, content: str, out_path: str):
    if content and content.startswith("data:image/"):
        b64 = content.split(",", 1)[1]
        im = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
        im.save(out_path, quality=96)
        print(f"Saved directly from dataURL -> {out_path} {im.size}", flush=True)
        return True
    exported = export_canvas_nodes_to_files({nid: out_path}, timeout_s=90)
    return nid in exported


def main():
    style_ref_path = r"C:\Users\Hang thu\.gemini\antigravity\brain\3c47ebbb-8468-44f7-b584-19bc2acdc8cf\.user_uploaded\media_1795404719183_a2e19ad8.jpg"
    dk_ref_jpg = prepare_clean_packshot_ref(
        os.path.join(V3_DIR, "assets", "cutouts", "ht01_dieu_kinh_a.png"),
        os.path.join(BENCH_DIR, "ref_dk_packshot.jpg"),
    )
    logo_ref_jpg = prepare_clean_packshot_ref(
        os.path.join(V3_DIR, "assets", "cutouts", "logo_hang_thu.png"),
        os.path.join(BENCH_DIR, "ref_ht_logo.jpg"),
    )

    nid_style = stage_local_ref_image_once(style_ref_path, "ref_style_av", x=200, y=0)
    nid_prod  = stage_local_ref_image_once(dk_ref_jpg, "ref_dk_box", x=200, y=420)
    nid_logo  = stage_local_ref_image_once(logo_ref_jpg, "ref_ht_logo", x=200, y=840)

    PROMPT_FULL = (
        "Create a super-clear, luxury commercial pharmaceutical infographic poster (vertical 3:4 aspect ratio) "
        "modeled directly on the exact layout density, huge typography, vivid scenic depth, and stone podium decor of Ảnh 1 (ref_style_av), "
        "featuring the exact real product box & open pill bottle from Ảnh 2 (ref_dk_box) and the official brand emblem from Ảnh 3 (ref_ht_logo). "
        "\n\n1. SCENIC BACKGROUND & PRODUCT DECOR (CRITICAL — NO FLAT PLAIN BACKGROUND): "
        "Set in a lush, sunlit royal ruby-crimson & botanical herbal garden studio with soft blooming pink lotus petals, lush dewy green medicinal leaves framing the left, bottom-left and corners, warm golden sunbeams, and flowing 3D champagne-gold silk ribbons. "
        "On the middle-left, place the EXACT product box 'ĐIỀU KINH HT' and open white bottle with herbal pills from Ảnh 2 standing naturally with unified warm golden rim lighting on a sculpted chiseled natural stone slab, "
        "surrounded right beside the box by rich natural herbal decor: sliced Đương quy roots, vibrant red Hồng hoa saffron blossoms, green herbal leaves, and scattered dark-brown herbal pills on the stone. Keep every letter and detail on the 'ĐIỀU KINH HT' box 100% sharp, accurate, and ungarbled! "
        "\n\n2. TOP HEADER & BRANDING: "
        "- Top-left: Official circular red-blue Yin-Yang HT logo from Ảnh 3 with crisp white-gold text 'HẰNG THU PHARMA - Tinh Hoa Thảo Dược Việt'. "
        "- Top-right MASSIVE 3D metallic gold headline: 'ĐIỀU KINH BỔ TRỨNG' "
        "- Large clear white bold subtitle underneath: 'Bồi bổ khí huyết — Điều hòa chu kỳ tự nhiên' and smaller gold line 'Nuôi dưỡng nền tảng buồng trứng khỏe từ gốc'. "
        "- Highlight pill banner with giant gold '4' and bold white uppercase 'NHÓM THẢO DƯỢC QUÝ / TRONG VIÊN HOÀN ĐIỀU KINH HẰNG THU'. "
        "\n\n3. FOUR COMPACT CREAM BENTO CARDS (01, 02 on middle-right; 03, 04 on bottom-right leaving the stone slab & leaves visible at bottom-left, ZERO empty space, HUGE vivid 3D illustrations filling 85% of each card + warm gold pill highlight behind the bold benefit): "
        "- Card 01: 'ĐƯƠNG QUY' | Huge 3D illustration of sliced Angelica root, green leaves & ruby essence drops | Gold highlight 'Bổ Huyết Chủ Đạo' | 'Hỗ trợ hoạt huyết, nuôi dưỡng tử cung ấm khỏe.' "
        "- Card 02: 'HƯƠNG PHỤ & SÀI HỒ' | Huge 3D illustration of herbal roots in a wooden mortar & pestle | Gold highlight 'Điều Hòa Kinh Kỳ' | 'Hỗ trợ hành khí, làm dịu tức bụng ngày đèn đỏ.' "
        "- Card 03: 'HỒNG HOA & HUYỀN HỒ' | Huge 3D illustration of vibrant red-orange saffron-like Carthamus flowers glowing | Gold highlight 'Thông Kinh Hoạt Lạc' | 'Hỗ trợ cải thiện kinh thâm đen, vón cục.' "
        "- Card 04: 'ĐAN SÂM & HUYẾT ĐẰNG' | Huge 3D illustration of red Salvia root slices & luminous pearl-pink healthy follicle orb | Gold highlight 'Dưỡng Trứng Khỏe' | 'Bồi bổ tuần hoàn khí huyết, đón tin vui.' "
        "\n\n4. BOTTOM CREAM FOOTER BAR WITH CUSTOM VECTOR ICONS: "
        "Left herbal shield icon + bold text 'Ngày uống 2 lần (sáng & tối), mỗi lần 10–20 viên cùng nước ấm.' | Middle 3 cute line icons (herbal bowl + yoga woman + warm water cup) | Right italic text 'Thực phẩm bảo vệ sức khỏe, không phải là thuốc và không thay thế thuốc chữa bệnh.'"
    )

    engines = [
        ("chatgpt", "chatgpt::chatgpt-image", os.path.join(BENCH_DIR, "01_chatgpt_full.jpg")),
        ("flow_pro", "flow::flow-nano-banana-pro", os.path.join(BENCH_DIR, "02_flow_nanobanana_pro_full.jpg")),
        ("muse", "muse::muse-image", os.path.join(BENCH_DIR, "03_muse_full.jpg")),
    ]

    created_nids = [nid_style, nid_prod, nid_logo]

    def _run_one(item):
        tag, model_id, out_p = item
        nid, content = run_direct_canvas_image(PROMPT_FULL, model_id, "3:4", [nid_style, nid_prod, nid_logo], tag, timeout_s=280)
        if nid:
            created_nids.append(nid)
            save_data_url_or_export(nid, content, out_p)
        return (tag, nid is not None, out_p)

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(_run_one, engines))

    print("BENCHMARK RESULTS:", results, flush=True)
    cleanup_exported_canvas_nodes(created_nids)
    print("Cleaned up temporary Canvas nodes!", flush=True)


if __name__ == "__main__":
    main()
