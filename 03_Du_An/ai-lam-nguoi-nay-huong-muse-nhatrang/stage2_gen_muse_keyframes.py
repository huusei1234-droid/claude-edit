import base64, io, json, os, time, urllib.request, urllib.error
from PIL import Image

PROJ_DIR = r"d:\AI\full studio\output\reel-2343806956159111"
ANC_DIR  = os.path.join(PROJ_DIR, "anchors")
KF_DIR   = os.path.join(PROJ_DIR, "keyframes_9x16")
os.makedirs(KF_DIR, exist_ok=True)

BASE = "http://127.0.0.1:18610"
api_key = json.loads(urllib.request.urlopen(f"{BASE}/local/keys", timeout=5).read().decode())["api_key"]

def to_durl(path, max_side=1280):
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def gen_muse_kf(name, prompt, ref_paths, size="9:16"):
    dst = os.path.join(KF_DIR, f"{name}.jpg")
    if os.path.exists(dst) and os.path.getsize(dst) > 25_000:
        print(f"[SKIP KF] {name}.jpg already exists.", flush=True)
        return dst
    refs = [to_durl(p) for p in ref_paths]
    payload = {
        "model": "muse-image",
        "prompt": prompt,
        "size": size,
        "n": 1,
        "response_format": "b64_json",
        "image": refs,
    }
    for attempt in range(5):
        t0 = time.time()
        try:
            req = urllib.request.Request(
                f"{BASE}/v1/images/generations",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=240) as resp:
                res = json.loads(resp.read().decode("utf-8"))
            raw = base64.b64decode(res["data"][0]["b64_json"])
            Image.open(io.BytesIO(raw)).convert("RGB").save(dst, quality=95)
            print(f"  -> [KF DONE] {name}.jpg ({int(time.time()-t0)}s, {os.path.getsize(dst)//1024} KB)", flush=True)
            return dst
        except Exception as e:
            print(f"  -> [KF RETRY {attempt+1}] {name}: {e}", flush=True)
            time.sleep(8)
    raise RuntimeError(f"Failed generating keyframe {name}")

CH1 = os.path.join(ANC_DIR, "ANC_CH1_VY.jpg")
CH2 = os.path.join(ANC_DIR, "ANC_CH2_BALE.jpg")
CH3 = os.path.join(ANC_DIR, "ANC_CH3_MINH.jpg")
BO1 = os.path.join(ANC_DIR, "ANC_BO1_DINING.jpg")
BO2 = os.path.join(ANC_DIR, "ANC_BO2_BALCONY.jpg")

KEYFRAME_SPECS = [
    (
        "kf_s01",
        [CH1, CH2, CH3, BO1],
        "Vertical 9:16 photorealistic live-action Vietnamese drama medium shot inside the exact Nha Trang luxury apartment dining room from the reference (prominently showing the smoky-white gold-veined charcoal bamboo wall panel flanked by dark walnut gold-trim fluted wood slats in the background and Nha Trang dusk sea through the right glass door): "
        "in the foreground-left stands Vy (exact young woman in blush-cream blazer over white silk blouse from reference, carrying a cream handbag on one wrist, looking tired and surprised toward the dining table); "
        "seated at the walnut dining table in the mid-ground are Bà Lệ (woman in dark plum silk collared shirt on left of table) and Minh (man in sky-blue dress shirt on right of table) who have already finished eating, with only an almost-empty plate of leftover boiled greens and empty bowls on the table. Natural cinematic lighting, ZERO text, ZERO watermark."
    ),
    (
        "kf_s02",
        [CH2, BO1],
        "Vertical 9:16 photorealistic live-action tight facial close-up from shoulders up of Bà Lệ (exact 56-year-old woman in dark plum silk collared blouse with low hair bun from reference, NO hands in frame) seated on the left side of the luxury Nha Trang dining room, "
        "with the dark walnut gold-trim fluted wood slats and smoky-white gold-veined charcoal bamboo feature wall softly out of focus behind her; she glances coldly and dismissively toward the left-foreground with a sharp judgmental expression. ZERO text, ZERO watermark."
    ),
    (
        "kf_s03",
        [CH3, BO1],
        "Vertical 9:16 photorealistic live-action tight facial close-up from shoulders up of Minh (exact 30-year-old man in sky-blue button-down dress shirt from reference, NO hands in frame) seated on the right side of the luxury Nha Trang dining room, "
        "with the glossy smoky-white gold-veined charcoal bamboo panel and walnut fluted wood slat accent wall softly visible behind him; he furrows his brows impatiently looking toward the left to scold his wife. ZERO text, ZERO watermark."
    ),
    (
        "kf_s04",
        [CH1, BO1],
        "Vertical 9:16 photorealistic live-action tight facial close-up from shoulders up of Vy (exact 28-year-old woman in blush-cream blazer over white silk blouse with long wavy dark brown hair from reference, NO hands in frame) standing on the left side of the luxury Nha Trang apartment, "
        "with the signature smoky-white gold-veined charcoal bamboo panel and dark walnut fluted wood slat wall gleaming softly in the background; her expressive eyes glisten with hurt pride and steely determination as she looks toward the right. ZERO text, ZERO watermark."
    ),
    (
        "kf_s05",
        [CH1, CH2, CH3, BO1],
        "Vertical 9:16 photorealistic live-action medium close-up inside the exact Nha Trang luxury apartment: in the foreground Vy (exact young woman in blush-cream blazer) holds a sleek smartphone to her right ear with a calm, confident half-smirk; "
        "in the soft-focus background in front of the smoky-white gold-veined charcoal bamboo and dark walnut fluted wood slat wall, Bà Lệ (dark plum blouse) and Minh (sky-blue shirt) stand staring at her in surprise. Only one right hand holding phone, left arm down out of frame, ZERO text, ZERO watermark."
    ),
    (
        "kf_s06",
        [CH1, CH2, CH3, BO2],
        "Vertical 9:16 photorealistic live-action cinematic medium shot on the exact Nha Trang sea-view luxury apartment balcony at night (sparkling curved Nha Trang beachfront bay lights & palm boulevard visible on the left background): "
        "in the foreground at the round teak balcony table sits Vy (exact woman in blush-cream blazer) happily enjoying a steaming gourmet platter of golden cheese-baked spiny lobster (tôm hùm nướng phô mai) and grilled seafood; "
        "right behind the wide sliding glass doors on the right (with the glowing charcoal-bamboo & walnut fluted wood slat living room wall visible inside), Minh (sky-blue shirt) and Bà Lệ (dark plum blouse) stand side-by-side staring out at her seafood feast in stunned disbelief. ZERO text, ZERO watermark."
    ),
    (
        "kf_s07",
        [CH3, BO2],
        "Vertical 9:16 photorealistic live-action tight facial close-up from shoulders up of Minh (exact man in sky-blue dress shirt from reference, NO hands in frame) standing just outside the sliding glass balcony door at night, "
        "with the warm glowing living room's walnut fluted wood slat & charcoal bamboo wall behind him; he looks down-left with shocked, annoyed disbelief. ZERO text, ZERO watermark."
    ),
    (
        "kf_s08",
        [CH1, BO2],
        "Vertical 9:16 photorealistic live-action tight facial close-up from shoulders up of Vy (exact woman in blush-cream blazer over white silk blouse from reference, NO hands in frame) seated at the Nha Trang sea-view balcony table at night, "
        "with the glittering curved ocean bay and city lights of Trần Phú, Nha Trang softly sparkling in bokeh behind her; she looks up-right with a poised, unbothered, triumphant queen smile. ZERO text, ZERO watermark."
    ),
    (
        "kf_s09",
        [CH1, CH2, CH3, BO2],
        "Vertical 9:16 photorealistic live-action close-up from shoulders up of Vy (exact woman in blush-cream blazer over white silk blouse, NO hands in frame) seated in the foreground on the Nha Trang sea-view night balcony, looking straight into the camera lens with confident, relatable poise; "
        "in the soft-focus background behind her, Minh (sky-blue shirt) and Bà Lệ (dark plum blouse) stand frozen speechless beside the glass balcony door framed by the walnut fluted wood slats, with sparkling Nha Trang bay lights in the distance. ZERO text, ZERO watermark."
    ),
]

for kname, rpaths, kprompt in KEYFRAME_SPECS:
    gen_muse_kf(kname, kprompt, rpaths)

print("\n=== ALL 9 PURE MUSE SCENE KEYFRAMES READY! ===", flush=True)
