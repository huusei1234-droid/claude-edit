import base64, io, json, os, shutil, sys, time, urllib.request
from PIL import Image, ImageDraw

# Ensure direct localhost connection without any system proxy interference
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv
import ai_ref_video as arv

OUT_DIR = r"d:\AI\full studio\output\feelchicken-food-cinematic"
REF_DIR = os.path.join(OUT_DIR, "refs_v3_real_dishes")
AI_DIR  = os.path.join(OUT_DIR, "ai_v3_clips")
CHK_V3  = os.path.join(OUT_DIR, "check_v3")
os.makedirs(AI_DIR, exist_ok=True)
os.makedirs(CHK_V3, exist_ok=True)

def upload_local_dish_ref(img_path: str, title: str, x_pos: int, y_pos: int) -> str:
    """Uploads a real Feel Chicken Sony A1 dish photo onto Infinity Canvas as an image node (or reuses if already uploaded)."""
    r, nodes = arv.get_canvas_state()
    for n in nodes.values():
        if n.get("type") == "image" and (n.get("title") or "").strip() == title and (n.get("metadata") or {}).get("status") == "success":
            print(f"[UploadRef] Reusing existing Canvas ref node '{title}' -> {n['id']}", flush=True)
            return n["id"]

    im = Image.open(img_path).convert("RGB")
    im.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=93)
    data_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    before_ids = set(nodes.keys())
    cv.call("canvas_create_node", {
        "nodeType": "image",
        "title": title,
        "x": x_pos,
        "y": y_pos,
        "width": 260,
        "height": 340,
        "metadata": {
            "content": data_url,
            "status": "success",
            "mimeType": "image/jpeg",
            "naturalWidth": im.width,
            "naturalHeight": im.height,
        }
    })
    time.sleep(1.2)
    _, after_nodes = arv.get_canvas_state()
    new_ids = [nid for nid in after_nodes.keys() if nid not in before_ids and after_nodes[nid].get("type") == "image"]
    if not new_ids:
        raise RuntimeError(f"Failed to create image node for {title}")
    nid = new_ids[-1]
    print(f"[UploadRef] Uploaded real dish '{title}' -> {nid}", flush=True)
    return nid

# 8 AL-Dante-Style Chiaroscuro Studio Food Cinema Shots using 100% Real Feel Chicken Dish Photos in 'reference' (Thành phần) mode!
SCENES = [
    {
        "id": "FC_AI01_flour_plunge",
        "ref_file": "ref01_crispy_gold.jpg",
        "ref_title": "FC_REF01_CrispyGold",
        "slot_dur": 2.4,
        "prompt": (
            "AL Dante style moody low-key chiaroscuro studio food cinematography, 9:16 vertical macro, 85mm f/1.4 shallow depth of field, pitch-black studio background, warm directional side-back key light: "
            "black-gloved chef hands toss a freshly seasoned chicken drumstick in snowy crispy flour on a dark walnut board—fine white flour dust explodes into the warm rim light—and lower it into bubbling hot golden frying oil with crisp micro-bubbles erupting."
        ),
    },
    {
        "id": "FC_AI02_golden_fry_lift",
        "ref_file": "ref01_crispy_gold.jpg",
        "ref_title": "FC_REF01_CrispyGold",
        "slot_dur": 2.4,
        "prompt": (
            "AL Dante style moody low-key studio food cinematography, 9:16 vertical extreme macro, shallow depth of field, pitch-black studio background, warm golden rim light: "
            "stainless steel spider strainer lifts exact ultra-crispy golden fried chicken drumsticks out of shimmering hot oil, glistening droplets dripping off the crunchy flaky crust while delicate wisps of hot white steam curl upward into the dark background."
        ),
    },
    {
        "id": "FC_AI03_wok_fire_glaze",
        "ref_file": "ref02_wok_red_glaze.jpg",
        "ref_title": "FC_REF02_WokRed",
        "slot_dur": 2.5,
        "prompt": (
            "AL Dante style moody low-key studio food cinematography, 9:16 vertical macro close-up, shallow depth of field, dark charcoal studio background, warm side light: "
            "a dark seasoned iron wok over a blue-orange gas flame tosses crispy golden fried chicken drumsticks coated in thick glossy crimson Korean chili Yangnyeom sauce—pieces arc gracefully mid-air with glossy red sauce droplets and aromatic steam."
        ),
    },
    {
        "id": "FC_AI04_ruby_sauce_pour",
        "ref_file": "ref03_ruby_pour.jpg",
        "ref_title": "FC_REF03_RubyPour",
        "slot_dur": 2.4,
        "prompt": (
            "AL Dante style moody chiaroscuro food art, 9:16 vertical extreme macro, f/1.4 razor-thin focus, pitch-black background, warm directional backlight: "
            "smooth camera push-in as a thick, glossy ribbon of ruby-red Korean Yangnyeom sauce pours slowly from above onto an ultra-crispy golden fried chicken drumstick on a dark matte plate, while toasted white sesame seeds rain gently through the air."
        ),
    },
    {
        "id": "FC_AI05_cheddar_velvet",
        "ref_file": "ref04_cheddar_pour.jpg",
        "ref_title": "FC_REF04_CheddarPour",
        "slot_dur": 2.4,
        "prompt": (
            "AL Dante style moody low-key studio food cinematography, 9:16 vertical extreme macro, shallow depth of field, dark background, warm golden rim light: "
            "orbital macro camera movement as rich molten golden cheddar cheese sauce cascades in a silky ribbon over ultra-crispy fried chicken drumsticks on fresh green lettuce, delicate steam wisps curling upward."
        ),
    },
    {
        "id": "FC_AI06_crispy_steam_tear",
        "ref_file": "ref05_crispy_pull.jpg",
        "ref_title": "FC_REF05_CrispyPull",
        "slot_dur": 2.5,
        "prompt": (
            "AL Dante style moody chiaroscuro food cinematography, 9:16 vertical symmetric macro close-up against a pitch-black studio backdrop, warm directional side-back key light: "
            "black nitrile chef-gloved hands gently tear open a piping-hot ultra-crispy golden cheese-glazed fried chicken piece—crunchy golden crust flakes part to reveal tender juicy white meat, stretching melted cheese, and dramatic curling wisps of hot steam."
        ),
    },
    {
        "id": "FC_AI07_jajang_steam_lift",
        "ref_file": "ref06_jajang_lift.jpg",
        "ref_title": "FC_REF06_JajangLift",
        "slot_dur": 2.4,
        "prompt": (
            "AL Dante style moody low-key studio food cinematography, 9:16 vertical macro close-up, shallow depth of field, dark charcoal background, warm backlight sculpting steam: "
            "sleek black chopsticks lift gleaming, glossy black-bean Jajangmyeon noodles upward from a matte black bowl with julienned cucumber and boiled egg, curling wisps of hot steam rising underneath the glistening noodles."
        ),
    },
    {
        "id": "FC_AI08_hero_drumstick_lift",
        "ref_file": "ref08_nguvi_platter.jpg",
        "ref_title": "FC_REF08_NguViPlatter",
        "slot_dur": 2.8,
        "prompt": (
            "AL Dante style signature hero reveal shot, 9:16 vertical macro close-up, f/1.4 shallow depth of field, dark moody background, warm golden backlight: "
            "camera smoothly racks focus and tilts up slightly as black-gloved fingers lift one glistening sesame-coated Korean fried chicken drumstick upward off the colorful 5-flavor Feel Chicken platter on dark walnut wood, dramatic wisps of hot aromatic steam curling underneath."
        ),
    },
]

def main():
    base_x = 42000
    base_y = 200
    ref_node_map = {}

    print("=== STEP 1: Uploading 7 unique Sony A1 Feel Chicken Dish Reference Photos to Canvas ===", flush=True)
    for idx, sc in enumerate(SCENES):
        rt = sc["ref_title"]
        if rt not in ref_node_map:
            img_p = os.path.join(REF_DIR, sc["ref_file"])
            ref_node_map[rt] = upload_local_dish_ref(img_p, rt, base_x, base_y + len(ref_node_map) * 460)

    print("\n=== STEP 2: Generating 8 Reference-Ingredient ('Thành phần') AI Videos via Google Flow -> Muse Fallback ===", flush=True)
    vid_node_to_dest = {}
    for idx, sc in enumerate(SCENES):
        out_mp4 = os.path.join(AI_DIR, f"{sc['id']}.mp4")
        if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 50_000:
            print(f"[Skip] Already exported on disk: {out_mp4}", flush=True)
            continue
        opt_sec = arv.calc_optimal_flow_seconds(sc["slot_dur"], min_s=4, max_s=5)
        ref_nid = ref_node_map[sc["ref_title"]]
        vid_nid, prov = arv.generate_video_with_ref(
            motion_prompt=sc["prompt"],
            ref_img_node_id=ref_nid,
            out_title=sc["id"],
            ratio="9:16",
            seconds=opt_sec,
            video_mode="reference",  # MANDATORY Rule 0.1: "Thành phần" / Ingredients mode!
            timeout_per_tier=360,
        )
        vid_node_to_dest[vid_nid] = out_mp4
        # Brief breather between Flow generations per HE-THONG-TONG-HOP 4.4
        time.sleep(3)

    if vid_node_to_dest:
        print(f"\n=== STEP 3: Exporting {len(vid_node_to_dest)} generated videos from Canvas to disk ===", flush=True)
        exported = arv.export_canvas_nodes_to_files(vid_node_to_dest, timeout_s=240)
        print(f"Exported {len(exported)}/{len(vid_node_to_dest)} videos:", list(exported.values()), flush=True)

    # Build verification contact sheet of all 8 generated AI clips!
    import subprocess
    W_C, H_C = 220, 390
    grid = Image.new("RGB", (W_C * 4, H_C * 4), (12, 12, 12))
    dr = ImageDraw.Draw(grid)
    row_cursor = 0
    for idx, sc in enumerate(SCENES):
        vp = os.path.join(AI_DIR, f"{sc['id']}.mp4")
        if not os.path.exists(vp):
            continue
        # grab 2 frames (35% and 75%) per clip -> 16 cells total (4x4 grid)
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", vp], capture_output=True, text=True)
        dur = float(r.stdout.strip() or 4.0)
        for sub_i, p in enumerate([0.35, 0.75]):
            cell_idx = idx * 2 + sub_i
            ri, ci = divmod(cell_idx, 4)
            jp = os.path.join(CHK_V3, f"ai_f_{cell_idx}.jpg")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{dur*p:.2f}", "-i", vp, "-frames:v", "1",
                            "-vf", f"scale={W_C}:{H_C}:force_original_aspect_ratio=increase,crop={W_C}:{H_C},format=yuvj420p", "-q:v", "3", jp], check=False)
            if os.path.exists(jp):
                x, y = ci * W_C, ri * H_C
                grid.paste(Image.open(jp).convert("RGB"), (x, y))
                dr.rectangle([x, y, x + W_C, y + 22], fill=(0, 0, 0))
                dr.text((x + 5, y + 4), f"{sc['id'][3:16]} @{dur*p:.1f}s", fill=(255, 224, 90))
                os.remove(jp)
    out_sheet = os.path.join(CHK_V3, "ai_v3_8clips_qc.jpg")
    grid.save(out_sheet, quality=90)
    print("Saved AI clips QC sheet:", out_sheet, flush=True)

if __name__ == "__main__":
    main()
