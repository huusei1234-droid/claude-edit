import os
import shutil
import sys
from pathlib import Path
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageSegmentation

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from ai_ref_video import (
    generate_ref_images_parallel_batch,
    get_canvas_state,
    cleanup_exported_canvas_nodes,
)

BASE = Path(r"d:\AI\full studio\projects\feelchicken_micay_muc_chay")
ASSETS = BASE / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
ART_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856")
UP_DIR = ART_DIR / ".user_uploaded"

RAW_PHOTOS = {
    "2muc_hero45": UP_DIR / "media_1795611338929_3191c27f.jpg",
    "2muc_dup":    UP_DIR / "media_1795611338979_32fd7d1a.jpg",
    "2muc_top":    UP_DIR / "media_1795611339002_5217ef00.jpg",
    "1muc_top":    UP_DIR / "media_1795611339023_42f8d62d.jpg",
    "1muc_hero45": UP_DIR / "media_1795611339029_325f199f.jpg",
}

# Check if 3191c27f and 32fd7d1a are identical or slightly different
im_a = cv2.imread(str(RAW_PHOTOS["2muc_hero45"]))
im_b = cv2.imread(str(RAW_PHOTOS["2muc_dup"]))
diff_ab = float(np.mean(np.abs(im_a.astype(np.float32) - im_b.astype(np.float32))))
print(f"Diff between photo 1 and photo 2: {diff_ab:.3f}")


def studio_food_grade(bgr: np.ndarray, alpha_u8: np.ndarray) -> np.ndarray:
    """
    Commercial Korean spicy seafood food color-grading:
    1. Neutralizes cool/green indoor fluorescent cast from the marble table.
    2. Boosts rich gochujang fiery crimson-orange soup & ramen noodles.
    3. Gives the scored whole squid plump, glossy, warm ivory-violet appetizing contrast.
    4. Adds crisp micro-contrast & specular highlights without blowing out whites.
    """
    # Upscale 2x first for crisp 2000px edges
    h0, w0 = bgr.shape[:2]
    bgr2 = cv2.resize(bgr, (w0 * 2, h0 * 2), interpolation=cv2.INTER_CUBIC)
    a2 = cv2.resize(alpha_u8, (w0 * 2, h0 * 2), interpolation=cv2.INTER_CUBIC)

    # 1.LAB white-balance warmth & soup richness (+a*, +b*)
    lab = cv2.cvtColor(bgr2, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]

    # Midtone S-curve on Luminance for 3D juiciness
    Ln = L / 255.0
    Ln_lift = Ln + 0.085 * (np.power(Ln, 0.82) * np.power(1.0 - Ln, 1.15))
    # Gentle S-contrast
    Ln_contrast = np.clip(0.5 + (Ln_lift - 0.5) * 1.12, 0.0, 1.0)
    L_new = Ln_contrast * 255.0

    # Identify metallic pot rim (low chroma near outer border of object) vs food interior
    chroma = np.sqrt((A - 128.0) ** 2 + (B - 128.0) ** 2)
    dist_in = cv2.distanceTransform((a2 > 90).astype(np.uint8), cv2.DIST_L2, 5)
    max_d = max(1.0, float(dist_in.max()))
    interior_w = np.clip((dist_in / (max_d * 0.22)), 0.0, 1.0)
    metal_rim = np.clip(1.0 - interior_w, 0.0, 1.0) * np.clip((16.0 - chroma) / 12.0, 0.0, 1.0)

    # Decontaminate greenish cast on metal rim (pull A slightly >= 128, keep neutral warm silver)
    A_clean = A * (1.0 - metal_rim) + np.maximum(A, 128.5) * metal_rim
    B_clean = B * (1.0 - metal_rim) + (128.0 + (B - 128.0) * 0.45) * metal_rim

    # Inside the pot: warm appetizing shift (+7.5 A* magenta-red, +9.5 B* golden-warmth weighted by chroma)
    food_w = interior_w * np.clip((chroma - 5.0) / 18.0, 0.18, 1.0)
    A_warm = np.clip(A_clean + 7.5 * food_w, 0, 255)
    B_warm = np.clip(B_clean + 9.5 * food_w, 0, 255)

    graded = cv2.cvtColor(np.dstack([L_new, A_warm, B_warm]).astype(np.uint8), cv2.COLOR_LAB2BGR)

    # 2. Selective HSV boost for red-orange spicy soup & fresh greens
    hsv = cv2.cvtColor(graded, cv2.COLOR_BGR2HSV).astype(np.float32)
    H_h, S_h, V_h = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    # Spicy soup / sausage / noodles (Hue 0..24 or 168..180)
    is_spicy = ((H_h <= 25) | (H_h >= 166)).astype(np.float32) * interior_w
    # Shift slightly toward rich fiery red-orange (Hue ~ 8..13) when pale orange
    S_h = np.clip(S_h * (1.0 + 0.30 * is_spicy + 0.14 * (1.0 - metal_rim)), 0, 255)
    V_h = np.clip(V_h * (1.0 + 0.04 * interior_w), 0, 255)
    graded = cv2.cvtColor(np.dstack([H_h, S_h, V_h]).astype(np.uint8), cv2.COLOR_HSV2BGR)

    # 3. Crisp food texture detail (Unsharp mask on luminance only, zero halo)
    blur = cv2.GaussianBlur(graded, (0, 0), 1.8)
    sharp = cv2.addWeighted(graded, 1.34, blur, -0.34, 0)

    # Smooth clean alpha contour & crop tight with 8px padding
    a_smooth = cv2.GaussianBlur(a2, (5, 5), 0.9)
    ys, xs = np.where(a_smooth > 18)
    pad = 8
    y0, y1 = max(0, int(ys.min()) - pad), min(sharp.shape[0], int(ys.max()) + pad + 1)
    x0, x1 = max(0, int(xs.min()) - pad), min(sharp.shape[1], int(xs.max()) + pad + 1)
    return np.dstack([sharp[y0:y1, x0:x1], a_smooth[y0:y1, x0:x1]])


# --- STEP 1: BiRefNet FP16 GPU Cutout + Studio Food Grading ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Loading BiRefNet FP16 on:", device)
model = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet", trust_remote_code=True).to(device).eval()
if device.type == "cuda":
    model = model.half()

tf = transforms.Compose([
    transforms.Resize((1024, 1024)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

targets = ["2muc_hero45", "2muc_top", "1muc_hero45", "1muc_top"]
for key in targets:
    src_p = RAW_PHOTOS[key]
    bgr = cv2.imread(str(src_p), cv2.IMREAD_COLOR)
    # Note: in 1muc_top & 1muc_hero45, there is a tiny black bowl edge on the far left x=0..45px — mask x<18 if disconnected!
    with torch.inference_mode():
        inp = tf(Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))).unsqueeze(0).to(device)
        if device.type == "cuda":
            inp = inp.half()
        pred = model(inp)[-1].sigmoid().float()
        alpha = F.interpolate(pred, size=bgr.shape[:2], mode="bilinear", align_corners=False)[0, 0].cpu().numpy()

    a_u8 = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    # Keep only largest connected component (excludes stray soy-sauce dish in top-right or black plate edge on far-left)
    nl, lb, st, _ = cv2.connectedComponentsWithStats((a_u8 > 45).astype(np.uint8))
    if nl > 1:
        best = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        keep = cv2.dilate((lb == best).astype(np.uint8) * 255, np.ones((7, 7), np.uint8), 1)
        a_u8 = np.minimum(a_u8, cv2.GaussianBlur(keep, (7, 7), 1.2))

    cut_rgba = studio_food_grade(bgr, a_u8)
    out_p = ASSETS / f"cut_{key}.png"
    cv2.imwrite(str(out_p), cut_rgba)
    print(f"Saved cutout {out_p.name}: {cut_rgba.shape}")

del model
if device.type == "cuda":
    torch.cuda.empty_cache()

# Build contact sheet of the 4 cutouts on dark fiery background for instant QA
qa_cards = []
for key in targets:
    rgba = cv2.imread(str(ASSETS / f"cut_{key}.png"), cv2.IMREAD_UNCHANGED)
    ch, cw = rgba.shape[:2]
    sc = min(560 / cw, 560 / ch)
    nw, nh = int(cw * sc), int(ch * sc)
    rs = cv2.resize(rgba, (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.full((620, 620, 3), (18, 16, 42), dtype=np.uint8)
    ox, oy = (620 - nw) // 2, (620 - nh) // 2
    al = rs[:, :, 3:4].astype(np.float32) / 255.0
    canvas[oy : oy + nh, ox : ox + nw] = (rs[:, :, :3] * al + canvas[oy : oy + nh, ox : ox + nw] * (1.0 - al)).astype(np.uint8)
    cv2.putText(canvas, key, (24, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (80, 220, 255), 2, cv2.LINE_AA)
    qa_cards.append(canvas)

qa_grid = np.vstack([np.hstack(qa_cards[:2]), np.hstack(qa_cards[2:])])
cv2.imwrite(str(ASSETS / "qa_4_muc_cutouts.jpg"), qa_grid, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
print("Saved QA grid:", ASSETS / "qa_4_muc_cutouts.jpg")

# --- STEP 2: Generate 3 Blazing Fiery Commercial Backdrops via 3 Parallel ChatGPT HTPM Tabs ---
specs = [
    {
        "ref_tag": "fc_muc_bg_wide",
        "ratio": "16:9",
        "prompt": (
            "Explosive fiery Korean spicy seafood noodle commercial stage background, wide 16:9 composition. "
            "In the lower 38 percent is a sleek dark charred-wood and black volcanic slate Korean restaurant tabletop glowing with warm orange fire reflections, completely empty and ready for placing pots. "
            "Behind the table, dramatic roaring kitchen wok flames, glowing golden-red embers, flying whole red chili peppers in mid-air, and rich rising hot steam against a deep crimson-black atmosphere. "
            "On the far right side (x from 76% to 96%) stands a super cool energetic kawaii 3D yellow baby chick mascot wearing red headphones and a red flame headband, cheering excitedly while holding a glowing red chili pepper. "
            "CRITICAL: The tabletop MUST be 100 percent empty — NO food, NO bowls, NO pots, NO squid, NO text, NO numbers, NO prices, NO logos anywhere."
        ),
    },
    {
        "ref_tag": "fc_muc_bg_fire1",
        "ratio": "1:1",
        "prompt": (
            "Ultra-dramatic Korean spicy food commercial photography background, square 1:1 composition. "
            "Lower 42 percent is a clean, completely empty dark obsidian slate and dark walnut tabletop catching intense fiery orange-red rim light. "
            "Background features blazing golden-crimson tongues of fire, glowing sparks, dynamic splashes of glossy red chili oil and flying red chili peppers in dramatic dark studio lighting with rising steam. "
            "CRITICAL: Completely empty tabletop — NO food, NO bowls, NO plates, NO text, NO letters, NO numbers, NO watermarks anywhere."
        ),
    },
    {
        "ref_tag": "fc_muc_bg_fire2",
        "ratio": "1:1",
        "prompt": (
            "High-energy Korean night-market spicy noodle commercial backdrop, square 1:1 composition. "
            "Lower 45 percent is an empty dark glossy roasted-oak counter seen at a 40-degree dining angle under warm studio key light. "
            "Behind the counter are glowing fiery red and amber Korean street lanterns, dramatic rising hot steam, floating red chili flakes and warm golden fire bokeh sparks. "
            "CRITICAL: Completely empty counter — NO food, NO bowls, NO pots, NO text, NO letters, NO numbers, NO logos anywhere."
        ),
    },
]

results = generate_ref_images_parallel_batch(specs, max_workers=3)
_, cur_nodes = get_canvas_state()
blob_root = Path(os.environ.get("APPDATA", "")) / "infinite-canvas-flow" / "IndexedDB" / "http_127.0.0.1_3100.indexeddb.blob"

# Index all recent IndexedDB blobs by byte size for instant 0.1s lossless extraction!
size_to_blob = {}
if blob_root.exists():
    for dirpath, _, filenames in os.walk(blob_root):
        for fn in filenames:
            p = Path(dirpath) / fn
            sz = p.stat().st_size
            mtime = p.stat().st_mtime
            if sz not in size_to_blob or mtime > size_to_blob[sz][0]:
                size_to_blob[sz] = (mtime, p)

saved_ids = []
for tag, nid, prov in results:
    n = cur_nodes.get(nid, {})
    meta = n.get("metadata") or {}
    sz = int(meta.get("bytes") or 0)
    dst = ASSETS / f"{tag}.png"
    if sz in size_to_blob:
        shutil.copy2(size_to_blob[sz][1], dst)
        im_chk = cv2.imread(str(dst))
        print(f"Instant IndexedDB extracted {tag} ({prov}, {sz} bytes) -> {im_chk.shape if im_chk is not None else 'ERR'}")
        saved_ids.append(nid)
    else:
        print(f"WARNING: byte size {sz} not found in IndexedDB for {tag} ({nid})")

if len(saved_ids) == len(results):
    cleanup_exported_canvas_nodes(saved_ids)
    print("Cleaned up all temporary Canvas nodes!")
