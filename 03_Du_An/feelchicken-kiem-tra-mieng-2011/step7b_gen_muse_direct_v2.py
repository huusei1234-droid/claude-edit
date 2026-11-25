import base64, io, json, os, subprocess, time, urllib.request, urllib.error
from PIL import Image, ImageDraw

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

BASE = "http://127.0.0.1:18610"
MEME2_SRC = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Meme_KiemTraMieng_02_DuaThu5.jpg"
LUU_SRC   = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Lưu ngày địa chỉ lại nhé .mp4"
FEAST_SRC = r"Z:\Máy tính khác\My Computer\feel chicken\Ảnh retouch\Ảnh Feel ngũ vị & Mỳ\A1_08956.JPG"

def get_api_key():
    j = json.loads(urllib.request.urlopen(f"{BASE}/local/keys", timeout=5).read().decode())
    return j["api_key"]

def to_data_url(path, max_side=1280):
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def post_json(url, payload, api_key, timeout=240):
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(8):
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"  [HTTP {e.code} attempt {attempt+1}] {body[:160]}", flush=True)
            if e.code in (429, 502, 503, 504):
                time.sleep(8)
                continue
            raise
    raise RuntimeError(f"Failed after retries: {url}")

def gen_image_9x16(name, prompt, ref_data_urls, api_key):
    dst = os.path.join(MEDIA_DIR, f"{name}.png")
    if os.path.isfile(dst) and os.path.getsize(dst) > 20000:
        print(f"Reusing existing {dst}", flush=True)
        return dst
    print(f"Generating 9:16 image [{name}]...", flush=True)
    t0 = time.time()
    payload = {
        "model": "muse-image",
        "prompt": prompt,
        "size": "9:16",
        "n": 1,
        "response_format": "b64_json",
    }
    if ref_data_urls:
        payload["image"] = ref_data_urls
    res = post_json(f"{BASE}/v1/images/generations", payload, api_key, timeout=240)
    b64 = res["data"][0]["b64_json"]
    raw = base64.b64decode(b64)
    Image.open(io.BytesIO(raw)).convert("RGBA").save(dst)
    print(f"  -> Saved {name}.png in {time.time()-t0:.1f}s!", flush=True)
    return dst

def gen_video_9x16(name, prompt, first_frame_path, api_key):
    dst = os.path.join(MEDIA_DIR, f"{name}.mp4")
    if os.path.isfile(dst) and os.path.getsize(dst) > 100000:
        print(f"Reusing existing {dst}", flush=True)
        return dst
    print(f"Generating 9:16 video [{name}]...", flush=True)
    t0 = time.time()
    ff_url = to_data_url(first_frame_path, max_side=1280)
    for retry in range(3):
        sub = post_json(f"{BASE}/v1/videos", {
            "model": "muse-video",
            "prompt": prompt,
            "size": "9:16",
            "duration": 6,
            "image": ff_url,
        }, api_key, timeout=60)
        tid = sub["id"]
        while time.time() - t0 < 360:
            req = urllib.request.Request(f"{BASE}/v1/videos/{tid}", headers={"Authorization": f"Bearer {api_key}"})
            st = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
            status = st.get("status")
            if status == "succeeded":
                vurl = st.get("url") or st.get("result", {}).get("url")
                tmp_mp4 = os.path.join(MEDIA_DIR, f"_raw_{name}.mp4")
                urllib.request.urlretrieve(vurl, tmp_mp4)
                subprocess.run([
                    "ffmpeg", "-y", "-v", "error", "-ss", "0.10", "-i", tmp_mp4,
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                    "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
                    dst
                ], check=True)
                os.remove(tmp_mp4)
                print(f"  -> Saved {name}.mp4 in {time.time()-t0:.1f}s!", flush=True)
                return dst
            elif status == "failed":
                print(f"  [Video failed retry {retry+1}] {st.get('error')}", flush=True)
                time.sleep(6)
                break
            time.sleep(6)
    raise RuntimeError(f"Video failed: {name}")

def main():
    api_key = get_api_key()

    ref_fc_neon_p = os.path.join(MEDIA_DIR, "ref_fc_bg_neon_9x16.jpg")
    ref_fc_wide_p = os.path.join(MEDIA_DIR, "ref_fc_bg_wide_9x16.jpg")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "13.70", "-i", LUU_SRC, "-frames:v", "1", "-q:v", "2", ref_fc_neon_p], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "12.20", "-i", LUU_SRC, "-frames:v", "1", "-q:v", "2", ref_fc_wide_p], check=True)

    d_meme  = to_data_url(MEME2_SRC)
    d_neon  = to_data_url(ref_fc_neon_p)
    d_wide  = to_data_url(ref_fc_wide_p)
    d_feast = to_data_url(FEAST_SRC)

    # 1. Generate 4 clean 9:16 images (n=1, fast & deterministic!)
    p_meme_img = gen_image_9x16(
        "FC_v2_meme_pray_img",
        "Recreate this exact funny candid Vietnamese high school classroom scene in vertical 9:16 smartphone camera look, completely clean with ZERO text, ZERO captions, ZERO words anywhere in the image: three Vietnamese teenage high school boys wearing burgundy-and-white and navy-blue Vietnamese PE polo shirts sitting at a light wooden classroom desk with blue school notebooks, yellow painted classroom wall with a colorful map poster on the top-left and green painted iron window bars on the right, pressing their palms together in desperate prayer and bowing nervously with eyes squeezed tight in comical dread during oral exam time, leave clean yellow wall headroom above their heads, authentic candid Vietnamese student meme photo, no text",
        [d_meme], api_key
    )

    p_quiz_img = gen_image_9x16(
        "FC_v2_quiz_fcbg_img",
        "Vertical 9:16 commercial photo inside the exact Feel Chicken restaurant from Reference 1: preserve the exact gray Venetian plaster textured wall, the glowing yellow-and-red chicken mascot neon sign on the upper wall, yellow-red menu boards at the top, and the warm light-wood dining table. Seated in the lower half of the frame (below the vertical midpoint) around that wooden table are three cheerful cute Vietnamese students (18-20 years old, two girls and one boy in youthful student outfits, smiling naturally with mouths closed) holding small folded paper quiz slips and iced peach teas, with the golden crispy Korean fried chicken drumsticks platter from Reference 2 on the table. Keep the upper half showing the gray wall and neon sign above their heads. Clean photo, no added text overlays",
        [d_neon, d_feast], api_key
    )

    p_outro_img = gen_image_9x16(
        "FC_v2_outro_fcwide_img",
        "Vertical 9:16 commercial wide-medium shot inside the exact Feel Chicken restaurant dining room from Reference 1: preserve the exact gray textured interior wall, white iron window grilles on the left, row of warm light-wood dining tables and chairs, and lively Korean chicken shop atmosphere. Seated happily around the foreground wooden table in the lower two-thirds of the frame is a different group of four cheerful Vietnamese high school/college friends (two boys and two girls wearing crisp white student shirts and pastel cardigans, big joyful smiles, mouths closed) clinking tall iced fruit tea glasses and celebrating over big plates of golden crispy Korean fried chicken drumsticks, french fries and spicy red tokbokki from Reference 2. Leave generous headroom in the top third of the vertical frame above everyone's heads. Clean photo, no text overlays",
        [d_wide, d_feast], api_key
    )

    p_ban_img = gen_image_9x16(
        "FC_v2_banner_2011_bg",
        "Bright joyful 3D Korean kawaii festive Vietnamese Teachers Day 20/11 vertical background illustration: warm sunlit pastel cream-and-peach school celebration scene with cute pastel pink roses and carnations, floating white paper airplanes, golden twinkling stars, soft bokeh confetti, and cozy wooden classroom window edges, clean open bright center, ultra-cute commercial art style, no text or letters",
        None, api_key
    )

    # 2. Generate 3 9:16 videos from the 3 keyframe images!
    v_meme = gen_video_9x16(
        "FC_v2_meme_pray_vid",
        "Hilarious candid Vietnamese high school classroom meme video: the three teenage boys in PE uniforms at the wooden desk press their palms together and bow up and down rapidly praying in comical nervous panic with eyes squeezed tight and shoulders trembling, while one boy peeks anxiously through his fingers toward the teacher, natural handheld smartphone camera micro-movement, no text overlays",
        p_meme_img, api_key
    )

    v_quiz = gen_video_9x16(
        "FC_v2_quiz_fcbg_vid",
        "Cheerful vertical video inside Feel Chicken restaurant: the three young Vietnamese students seated at the wooden table under the glowing Feel Chicken neon sign smile and laugh joyfully with mouths closed, point excitedly at the folded paper quiz slips in their hands as they solve a fun riddle, and clink their iced peach tea glasses over the platter of crispy golden fried chicken, gentle smooth camera push-in, no text overlays",
        p_quiz_img, api_key
    )

    v_outro = gen_video_9x16(
        "FC_v2_outro_fcwide_vid",
        "Joyful celebratory vertical video inside the Feel Chicken restaurant dining room: the group of four happy Vietnamese student friends in white shirts and cardigans around the wooden table cheerfully clink their tall iced fruit tea glasses together, laugh warmly with mouths closed, and hold up crispy golden Korean fried chicken drumsticks in celebration, lively warm restaurant atmosphere, smooth subtle camera glide, no text overlays",
        p_outro_img, api_key
    )

    # 3. Build QC ruler sheet!
    qc_imgs = []
    for vk, vp in [("meme_pray", v_meme), ("quiz_fcbg", v_quiz), ("outro_fcwide", v_outro)]:
        fp = os.path.join(CHECK_DIR, "_v2q.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", vp, "-frames:v", "1", fp], check=True)
        im = Image.open(fp).convert("RGB")
        dr = ImageDraw.Draw(im)
        for y in range(200, 1900, 200):
            dr.line([(0, y), (1080, y)], fill=(255, 230, 0), width=2)
            dr.rectangle([6, y - 18, 96, y + 6], fill=(0, 0, 0))
            dr.text((10, y - 14), f"y={y}", fill=(255, 255, 100))
        dr.rectangle([10, 10, 420, 56], fill=(0, 0, 0))
        dr.text((20, 20), vk, fill=(100, 255, 180))
        qc_imgs.append(im.resize((360, 640), Image.Resampling.LANCZOS))
        os.remove(fp)

    bim = Image.open(p_ban_img).convert("RGB").resize((360, 640), Image.Resampling.LANCZOS)
    qc_imgs.append(bim)
    grid = Image.new("RGB", (360 * len(qc_imgs), 640))
    for i, qim in enumerate(qc_imgs):
        grid.paste(qim, (i * 360, 0))
    qcp = os.path.join(CHECK_DIR, "canvas_v2_qc_ruler.jpg")
    grid.save(qcp, quality=90)
    print("ALL V2 MUSE ASSETS COMPLETE ->", qcp, flush=True)

if __name__ == "__main__":
    main()
