import json, math, os, pathlib, shutil, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

PROJ = pathlib.Path(r"d:\AI\full studio\output\lt-plus-talking-head")
MEDIA = PROJ / "media"
Z_ANH = pathlib.Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\Ảnh")

def build_real_product_showcase_clip(out_mp4, dur_s=6.5, fps=30):
    """
    Render a silky 1080x1920 30fps luxury studio product showcase video using 100% REAL
    high-resolution LT PLUS HẰNG THU photographs from Z:\\...\\Ảnh (DSC00275.JPG + 4.png + 2.png + 6.png)
    so every Vietnamese letter on the packaging is 100% authentic and razor-sharp!
    """
    W, H = 1080, 1920
    n_frames = int(round(dur_s * fps))

    # Load real studio photo DSC00275.JPG (box + bottle + inner box) & cutout 4.png + 2.png + 6.png
    box_cut = Image.open(Z_ANH / "4.png").convert("RGBA")
    bot_cut = Image.open(Z_ANH / "2.png").convert("RGBA")
    open_cut = Image.open(Z_ANH / "6.png").convert("RGBA")

    # Prebuild luxury blush-silk studio background (1080x1920)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rad = np.exp(-(((xx - 540.0) / 560.0) ** 2 + ((yy - 960.0) / 880.0) ** 2))
    bg_base = np.zeros((H, W, 3), dtype=np.float32)
    bg_base[:, :, 0] = 236.0 + 19.0 * rad
    bg_base[:, :, 1] = 205.0 + 38.0 * rad
    bg_base[:, :, 2] = 218.0 + 30.0 * rad

    # Soft podium reflection plane at y > 1280
    pod = np.clip((yy - 1260.0) / 140.0, 0.0, 1.0)
    bg_base[:, :, 0] = bg_base[:, :, 0] * (1.0 - 0.06 * pod) + 250.0 * 0.06 * pod
    bg_base[:, :, 1] = bg_base[:, :, 1] * (1.0 - 0.08 * pod) + 232.0 * 0.08 * pod
    bg_base[:, :, 2] = bg_base[:, :, 2] * (1.0 - 0.06 * pod) + 240.0 * 0.06 * pod

    # Floating bokeh seeds
    rng = np.random.default_rng(42)
    bokehs = [(rng.uniform(80, 1000), rng.uniform(180, 1700), rng.uniform(18, 56), rng.uniform(0.4, 1.0), rng.uniform(0, 6.28)) for _ in range(22)]

    proc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", str(out_mp4)
    ], stdin=subprocess.PIPE)

    # Pre-scale cutouts cleanly
    box_w = 700
    box_h = int(round(box_cut.height * (box_w / box_cut.width)))
    box_im = box_cut.resize((box_w, box_h), Image.Resampling.LANCZOS)

    bot_w = 330
    bot_h = int(round(bot_cut.height * (bot_w / bot_cut.width)))
    bot_im = bot_cut.resize((bot_w, bot_h), Image.Resampling.LANCZOS)

    open_w = 680
    open_h = int(round(open_cut.height * (open_w / open_cut.width)))
    open_im = open_cut.resize((open_w, open_h), Image.Resampling.LANCZOS)

    for fi in range(n_frames):
        t = fi / float(fps)
        u = t / dur_s

        # Soft animated warm sunbeam across silk studio
        beam = np.exp(-(((xx - (280.0 + 520.0 * u)) + (yy - 960.0) * 0.35) / 260.0) ** 2)
        arr = np.clip(bg_base + beam[:, :, None] * np.array([18.0, 14.0, 10.0], dtype=np.float32), 0, 255).astype(np.uint8)
        canvas = Image.fromarray(arr, "RGB").convert("RGBA")

        # Draw soft golden-pink bokeh particles
        b_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bdr = ImageDraw.Draw(b_layer)
        for bx, by, br, bsp, bph in bokehs:
            cy_b = (by - t * 38.0 * bsp) % H
            cx_b = bx + math.sin(t * 1.4 + bph) * 18.0
            al = int(55 + 35 * math.sin(t * 2.2 + bph))
            bdr.ellipse([cx_b - br, cy_b - br, cx_b + br, cy_b + br], fill=(255, 245, 225, al))
        b_layer = b_layer.filter(ImageFilter.GaussianBlur(radius=6))
        canvas = Image.alpha_composite(canvas, b_layer)

        # Podium ellipse ring
        pdr = ImageDraw.Draw(canvas)
        pdr.ellipse([120, 1290, 960, 1465], fill=(255, 246, 250, 190), outline=(255, 215, 165, 210), width=4)

        # First half (0 - 3.3s): Closed Box + Bottle parallax push-in; Second half (3.0 - 6.5s): Smooth crossfade to Open Magnetic Box + Bottle!
        cross = 0.0
        if t > 3.1:
            cross = min(1.0, (t - 3.1) / 0.65)
            cross = cross * cross * (3.0 - 2.0 * cross)

        z1 = 0.96 + 0.08 * u
        if cross < 0.999:
            op1 = 1.0 - cross
            # Closed box shadow + box + bottle
            layer1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(layer1).ellipse([210, 1320, 890, 1425], fill=(115, 55, 75, int(95 * op1)))
            layer1 = layer1.filter(ImageFilter.GaussianBlur(radius=20))

            bw1, bh1 = int(box_w * z1), int(box_h * z1)
            bim1 = box_im.resize((bw1, bh1), Image.Resampling.BILINEAR)
            bx1, by1 = int(465 - bw1 // 2 - 12 * u), int(980 - bh1 // 2)
            if op1 < 0.999:
                a = bim1.split()[3].point(lambda p: int(p * op1))
                bim1.putalpha(a)
            layer1.paste(bim1, (bx1, by1), mask=bim1.split()[3])

            tw1, th1 = int(bot_w * (z1 + 0.02)), int(bot_h * (z1 + 0.02))
            tim1 = bot_im.resize((tw1, th1), Image.Resampling.BILINEAR)
            tx1, ty1 = int(775 - tw1 // 2 + 14 * u), int(1095 - th1 // 2)
            if op1 < 0.999:
                a2 = tim1.split()[3].point(lambda p: int(p * op1))
                tim1.putalpha(a2)
            layer1.paste(tim1, (tx1, ty1), mask=tim1.split()[3])
            canvas = Image.alpha_composite(canvas, layer1)

        if cross > 0.001:
            op2 = cross
            z2 = 0.95 + 0.07 * max(0.0, (t - 3.0) / 3.5)
            layer2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(layer2).ellipse([220, 1330, 860, 1435], fill=(115, 55, 75, int(95 * op2)))
            layer2 = layer2.filter(ImageFilter.GaussianBlur(radius=20))

            ow2, oh2 = int(open_w * z2), int(open_h * z2)
            oim2 = open_im.resize((ow2, oh2), Image.Resampling.BILINEAR)
            ox2, oy2 = int(540 - ow2 // 2), int(955 - oh2 // 2)
            if op2 < 0.999:
                ao = oim2.split()[3].point(lambda p: int(p * op2))
                oim2.putalpha(ao)
            layer2.paste(oim2, (ox2, oy2), mask=oim2.split()[3])
            canvas = Image.alpha_composite(canvas, layer2)

        proc.stdin.write(np.array(canvas.convert("RGB"), dtype=np.uint8).tobytes())

    proc.stdin.close()
    proc.wait()
    print("Saved 100% real-packaging showcase clip ->", out_mp4)

def export_canvas_and_map():
    st = cv.call("canvas_get_state", {})["result"]
    ex_nodes = [n for n in st["nodes"] if n.get("type") == "export:folder"]
    if not ex_nodes:
        raise RuntimeError("No export:folder node on canvas!")
    ex_id = ex_nodes[0]["id"]
    req_id = f"ltplus-export-{int(time.time()*1000)}"
    cv.call("canvas_apply_ops", {
        "ops": [{
            "type": "update_node",
            "id": ex_id,
            "metadata": {"exportAll": True, "exportRequest": req_id}
        }]
    })
    time.sleep(7)
    manifest_p = pathlib.Path(r"d:\AI\full studio\canvas\exports\manifest.json")
    mf = json.loads(manifest_p.read_text(encoding="utf-8"))
    return st, mf

def wait_for_videos(titles, max_steps=42):
    for step in range(max_steps):
        time.sleep(10)
        st_res = cv.call("canvas_get_state", {})["result"]
        nodes = {n["id"]: n for n in st_res["nodes"]}
        conns = st_res["connections"]
        status_map = {}
        for t in titles:
            cfgs = [n for n in nodes.values() if n["type"] == "config" and (n.get("title") or "").startswith(t)]
            if not cfgs:
                status_map[t] = "no_cfg"
                continue
            cid = cfgs[-1]["id"]
            outs = [nodes[c["toNodeId"]] for c in conns if c["fromNodeId"] == cid and nodes[c["toNodeId"]]["type"] == "video"]
            if not outs:
                status_map[t] = cfgs[-1].get("metadata", {}).get("status", "pending")
            else:
                m = outs[-1].get("metadata") or {}
                status_map[t] = f"{m.get('status')}|err={str(m.get('error') or '')[:60]}"
        print(f"[Videos {step*10}s]", status_map, flush=True)
        if all(v.startswith("success") or v.startswith("error") for v in status_map.values()):
            return status_map
    return {}

def main():
    # 1. Build 100% real LT PLUS packaging video clip immediately
    build_real_product_showcase_clip(MEDIA / "broll_4b_ltplus.mp4", dur_s=6.5, fps=30)

    # 2. Generate 7 vertical 9:16 B-roll clips on Flow in 3 small sub-batches (2 + 2 + 3)
    VID_BATCHES = [
        [
            {
                "key": "broll_1a_calendar",
                "title": "LT-v-1a",
                "x": 4500, "y": 0,
                "prompt": "Cinematic vertical 9:16 morning bedroom vanity tabletop B-roll, slow gentle camera push-in on a clean pastel blush-pink desk calendar, a warm white porcelain cup of chamomile tea with gentle steam, and soft sheer curtains swaying in warm sunlight, shallow depth of field, no people, no speech, no text overlays, no numbers, no captions, no watermark"
            },
            {
                "key": "broll_1b_droplet",
                "title": "LT-v-1b",
                "x": 4500, "y": 550,
                "prompt": "Clean 3D aesthetic pharmaceutical visualization, vertical 9:16, luminous translucent rose-pearl and crystal-aqua micro-droplets gently floating and rippling across a soft pastel blush silk wave surface, serene studio lighting, no blood, no real body parts, no people, no speech, no text overlays, no captions, no watermark"
            },
        ],
        [
            {
                "key": "broll_2a_consult",
                "title": "LT-v-2a",
                "x": 4500, "y": 1100,
                "prompt": "Bright modern women wellness pharmacy clinic desk B-roll, vertical 9:16, slow smooth camera glide across a clean white medical stethoscope resting beside a closed pastel-pink notebook and fresh soft pink peony flowers in morning bokeh, high-key studio daylight, no people, no speech, no text overlays, no captions, no watermark"
            },
            {
                "key": "broll_2b_barrier",
                "title": "LT-v-2b",
                "x": 4500, "y": 1650,
                "prompt": "Clean 3D scientific medical animation, vertical 9:16, glowing pearl-white and soft mint-rose protective barrier spheres arranged in a gentle shield layer deflecting tiny grey dust specks under bright sterile studio lighting, aesthetic medical illustration, no blood, no anatomy, no speech, no text overlays, no captions, no watermark"
            },
        ],
        [
            {
                "key": "broll_3a_lab",
                "title": "LT-v-3a",
                "x": 5200, "y": 0,
                "prompt": "Clean high-key medical laboratory B-roll, vertical 9:16, slow cinematic dolly past a sleek white optical microscope and clean crystal-clear glass test tubes on a sunlit sterile clinic counter, soft mint and warm white bokeh, no people, no blood, no speech, no text overlays, no captions, no watermark"
            },
            {
                "key": "broll_3b_shield",
                "title": "LT-v-3b",
                "x": 5200, "y": 550,
                "prompt": "Clean 3D luxury medical animation, vertical 9:16, a luminous translucent rose-quartz and champagne-gold protective medical shield emblem hovering gently above soft white silk waves with delicate golden bokeh particles, no people, no speech, no text overlays, no captions, no watermark"
            },
            {
                "key": "broll_4a_herbs",
                "title": "LT-v-4a",
                "x": 5200, "y": 1100,
                "prompt": "Breathtaking macro botanical nature B-roll, vertical 9:16, fresh green tea leaves, betel leaves, and golden honeysuckle blossoms with sparkling morning dewdrops resting beside a clean white ceramic mortar on a sunlit marble spa table, warm natural sunbeams, no people, no speech, no text overlays, no captions, no watermark"
            },
        ],
    ]

    for bi, batch in enumerate(VID_BATCHES, 1):
        print(f"=== Submitting LT PLUS Video Batch {bi}/3 ===")
        for item in batch:
            res = cv.call("canvas_generate_video", {
                "prompt": item["prompt"],
                "model": "flow::flow-omni-1.2-flash",
                "size": "9:16",
                "seconds": "6",
                "vquality": "720",
                "generateAudio": "false",
                "videoMode": "frames",
                "title": item["title"],
                "x": item["x"],
                "y": item["y"],
            })
            print("Submitted", item["title"], "-> ok:", res.get("ok"))
            time.sleep(5)
        wait_for_videos([x["title"] for x in batch])

    # 3. Export all generated icons & videos from Canvas via export:folder!
    print("Exporting all generated LT PLUS icons & B-roll videos from Canvas...")
    st, mf = export_canvas_and_map()
    nodes = {n["id"]: n for n in st["nodes"]}
    conns = st["connections"]
    mf_by_node = {it["nodeId"]: it["path"] for it in mf.get("items", [])}

    ICON_MAP = {
        "LT-ic-hook1": "hook_01_clean.png",
        "LT-ic-hook2": "hook_02_clean.png",
        "LT-ic-clinic": "icon_clinic_clean.png",
        "LT-ic-herbs": "icon_herbs_clean.png",
        "LT-ic-ph": "icon_ph_clean.png",
    }
    VID_MAP = {
        "LT-v-1a": "broll_1a_calendar.mp4",
        "LT-v-1b": "broll_1b_droplet.mp4",
        "LT-v-2a": "broll_2a_consult.mp4",
        "LT-v-2b": "broll_2b_barrier.mp4",
        "LT-v-3a": "broll_3a_lab.mp4",
        "LT-v-3b": "broll_3b_shield.mp4",
        "LT-v-4a": "broll_4a_herbs.mp4",
    }

    for title_prefix, out_png in ICON_MAP.items():
        cfgs = [n for n in nodes.values() if n["type"] == "config" and (n.get("title") or "").startswith(title_prefix)]
        if cfgs:
            cid = cfgs[-1]["id"]
            outs = [nodes[c["toNodeId"]] for c in conns if c["fromNodeId"] == cid and nodes[c["toNodeId"]]["type"] == "image"]
            if outs and outs[-1]["id"] in mf_by_node:
                src_p = mf_by_node[outs[-1]["id"]]
                im = Image.open(src_p).convert("RGBA")
                # Center-crop 6% margin to remove any outer corner artifact & resize to 600x600
                w, h = im.size
                mx, my = int(w * 0.05), int(h * 0.05)
                im = im.crop((mx, my, w - mx, h - my)).resize((600, 600), Image.Resampling.LANCZOS)
                im.save(MEDIA / out_png)
                print("Saved icon ->", out_png)

    for title_prefix, out_mp4 in VID_MAP.items():
        cfgs = [n for n in nodes.values() if n["type"] == "config" and (n.get("title") or "").startswith(title_prefix)]
        if cfgs:
            cid = cfgs[-1]["id"]
            outs = [nodes[c["toNodeId"]] for c in conns if c["fromNodeId"] == cid and nodes[c["toNodeId"]]["type"] == "video"]
            if outs and outs[-1]["id"] in mf_by_node:
                src_p = mf_by_node[outs[-1]["id"]]
                raw_dst = MEDIA / (out_mp4.replace(".mp4", "_raw.mp4"))
                shutil.copy2(src_p, raw_dst)
                # Trim first 0.25s + slight 1.05x crop-scale to 1080x1920 @ 30fps cleanly!
                subprocess.run([
                    "ffmpeg", "-y", "-v", "error", "-ss", "0.25", "-i", str(raw_dst),
                    "-vf", "scale=1134:2016:flags=lanczos,crop=1080:1920,fps=30",
                    "-an", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
                    str(MEDIA / out_mp4)
                ], check=True)
                print("Saved clean 1080x1920@30 B-roll ->", out_mp4)

if __name__ == "__main__":
    main()
