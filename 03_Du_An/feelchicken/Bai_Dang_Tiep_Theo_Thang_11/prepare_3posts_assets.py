import os
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
    export_canvas_nodes_to_files,
    cleanup_exported_canvas_nodes,
)

BASE = Path(r"d:\AI\full studio\projects\feelchicken_3posts_t11")
ASSETS = BASE / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
SCR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\scratch")

# --- 1. Cutout Anh Khang (IMG_1341.jpg — warm natural smile pointing at food!) via BiRefNet FP16 ---
khang_path = Path(r"Z:\Máy tính khác\My Computer\feel chicken\Ảnh retouch\Anh Khang\IMG_1341.jpg")
k_bgr = cv2.imdecode(np.fromfile(str(khang_path), dtype=np.uint8), cv2.IMREAD_COLOR)
Hk, Wk = k_bgr.shape[:2]
# Crop upper body & pointing hands cleanly above the foreground chicken platter (y=0.14..0.76, x=0.05..0.96)
k_crop = k_bgr[int(Hk * 0.14) : int(Hk * 0.78), int(Wk * 0.04) : int(Wk * 0.96)].copy()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Running BiRefNet FP16 for Anh Khang cutout on:", device)
model = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet", trust_remote_code=True).to(device).eval()
if device.type == "cuda":
    model = model.half()
tf = transforms.Compose([
    transforms.Resize((1024, 1024)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])
with torch.inference_mode():
    inp = tf(Image.fromarray(cv2.cvtColor(k_crop, cv2.COLOR_BGR2RGB))).unsqueeze(0).to(device)
    if device.type == "cuda":
        inp = inp.half()
    pred = model(inp)[-1].sigmoid().float()
    alpha = F.interpolate(pred, size=k_crop.shape[:2], mode="bilinear", align_corners=False)[0, 0].cpu().numpy()

# Release VRAM right away
del model
if device.type == "cuda":
    torch.cuda.empty_cache()

a_u8 = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
# Remove any foreground chicken lettuce caught below y > 0.74 where hue is green/orange
hsv_k = cv2.cvtColor(k_crop, cv2.COLOR_BGR2HSV)
food_bottom = (np.arange(k_crop.shape[0])[:, None] > int(k_crop.shape[0] * 0.74)) & (hsv_k[:, :, 1] > 55)
a_u8[food_bottom] = 0
nl, lb, st, _ = cv2.connectedComponentsWithStats((a_u8 > 35).astype(np.uint8))
bl = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
keep_k = (lb == bl).astype(np.uint8) * 255
a_u8 = np.minimum(a_u8, cv2.GaussianBlur(cv2.dilate(keep_k, np.ones((5, 5), np.uint8), 1), (5, 5), 1.0))

# Gentle midtone brightness lift (+0.12 EV) preserving 100% natural eye/brow crispness & white shirt neutrality
f_k = k_crop.astype(np.float32) / 255.0
lift = f_k + 0.08 * (np.power(f_k, 0.85) * np.power(1.0 - f_k, 1.15))
k_nice = np.clip(lift * 255.0, 0, 255).astype(np.uint8)
ys, xs = np.where(a_u8 > 16)
k_bgra = np.dstack([k_nice[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1], a_u8[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]])
cv2.imwrite(str(ASSETS / "anh_khang_cutout.png"), k_bgra)
print("Saved Anh Khang cutout:", k_bgra.shape)

# --- 2. Generate 3 Custom Scenic Backdrops via 3 Parallel ChatGPT HTPM Tabs! ---
specs = [
    {
        "ref_tag": "fc_t11_bg_post1_micay",
        "ratio": "16:9",
        "prompt": (
            "Cozy vibrant Korean restaurant commercial background illustration and photography blend, wide 16:9 view. "
            "In the lower 38 percent is a clean, completely empty warm honey-oak wooden dining tabletop with soft studio lighting, ready for placing dishes. "
            "Behind the table on the left and right are rain-streaked glass windows at dusk with glowing warm red and golden Korean street bokeh lights, gentle rain droplets, and cozy rising warm mist. "
            "On the far right corner stands a super cute kawaii 2.5D yellow baby chick mascot wearing red headphones and a cozy red scarf, holding a tiny cute red chili pepper with a cheerful expression. "
            "CRITICAL: The wooden table surface MUST be 100 percent empty — NO food, NO bowls, NO plates, NO text, NO letters, NO numbers, NO logos anywhere."
        ),
    },
    {
        "ref_tag": "fc_t11_bg_post2_challenge",
        "ratio": "16:9",
        "prompt": (
            "Exciting Korean fried chicken eating-challenge game show commercial backdrop, wide 16:9 view. "
            "Dramatic festive crimson-red and blazing golden spotlight rays radiating from the center, subtle floating golden confetti sparks and fiery warm bokeh. "
            "Along the bottom 26 percent is a clean, completely empty warm polished wooden counter stage under bright studio lights. "
            "Keep the left, center, and right areas clean and uncluttered with rich red-gold depth. "
            "CRITICAL: Completely empty wooden counter — NO people, NO food, NO plates, NO text, NO letters, NO numbers, NO clocks, NO logos anywhere."
        ),
    },
    {
        "ref_tag": "fc_t11_bg_post3_cozyrain",
        "ratio": "1:1",
        "prompt": (
            "Heartwarming, joyful Korean fried chicken restaurant commercial background blending cozy realistic warm interior photography with cute kawaii accents, square 1:1 composition. "
            "The lower 48 percent is a wide, completely empty warm honey-wood dining table seen at a natural 35-degree dining angle under bright appetizing studio light. "
            "The upper background shows a cozy bright warm-cream and coral-red restaurant window with gentle afternoon rain droplets outside, warm golden string lights, and soft pastel clouds. "
            "Near the middle-left edge stands an adorable kawaii yellow baby chick mascot wearing red headphones and a yellow raincoat holding a tiny folded umbrella, smiling warmly. "
            "CRITICAL: The wooden table MUST be 100 percent empty — NO food, NO dishes, NO drinks, NO text, NO letters, NO numbers, NO watermarks anywhere."
        ),
    },
]

results = generate_ref_images_parallel_batch(specs, max_workers=3)
node_to_dest = {}
node_ids = []
for tag, nid, prov in results:
    print(f"Generated {tag} via {prov}: {nid}")
    node_ids.append(nid)
    node_to_dest[nid] = str(ASSETS / f"{tag}.png")

exported = export_canvas_nodes_to_files(node_to_dest)
print("Exported files:", exported)
cleanup_exported_canvas_nodes(node_ids)
print("Cleaned up temporary Canvas nodes!")
