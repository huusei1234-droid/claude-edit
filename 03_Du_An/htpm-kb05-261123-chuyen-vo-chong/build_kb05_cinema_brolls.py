import math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJ  = r"C:\AI\full studio\output\htpm-kb05-261123"
MEDIA = os.path.join(PROJ, "media")
CHECK = os.path.join(PROJ, "check")
os.makedirs(MEDIA, exist_ok=True)
os.makedirs(CHECK, exist_ok=True)

PY_EXE    = r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
APPLY_LUT = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\apply_lut.py"
LUT_HARM  = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"
FONT_BOLD = r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi\AsapCondensed-Bold.ttf"

def load_depth_estimator():
    try:
        import torch
        from transformers import pipeline
        dev = 0 if torch.cuda.is_available() else -1
        pipe = pipeline(task="depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=dev)
        print("[Depth2.5D] Loaded Depth-Anything-V2-Small on CUDA!" if dev == 0 else "[Depth2.5D] Loaded on CPU", flush=True)
        return pipe
    except Exception as e:
        print("[Depth2.5D] Fallback smooth depth map:", e, flush=True)
        return None

def compute_depth_map(pipe, pil_rgb):
    w, h = pil_rgb.size
    if pipe is not None:
        try:
            res = pipe(pil_rgb)
            dm = np.array(res["depth"].resize((w, h), Image.Resampling.BICUBIC), dtype=np.float32)
            dm = (dm - dm.min()) / max(1e-5, dm.max() - dm.min())
            return cv2.GaussianBlur(dm, (31, 31), 8.0)
        except Exception:
            pass
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return np.clip(1.0 - 0.55 * (((xx - w * 0.5) / (w * 0.55)) ** 2 + ((yy - h * 0.55) / (h * 0.55)) ** 2), 0.1, 1.0)

def render_25d_parallax_clip(src_img_path, ref_png_out, out_mp4, pipe, pan_dir=1.0, warm_motes=True):
    im = Image.open(src_img_path).convert("RGB")
    iw, ih = im.size
    target_ar = 16.0 / 9.0
    if (iw / ih) > target_ar:
        nw = int(round(ih * target_ar))
        x0 = (iw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, ih))
    else:
        nh = int(round(iw / target_ar))
        y0 = (ih - nh) // 2
        im = im.crop((0, y0, iw, y0 + nh))
    W, H = 1280, 720
    im_1280 = im.resize((W, H), Image.Resampling.LANCZOS)
    im_1280.save(ref_png_out)

    # Overscan working buffer (1440x810) for edge-free 3D parallax camera travel
    OW, OH = 1440, 810
    im_over = im.resize((OW, OH), Image.Resampling.LANCZOS)
    rgb_over = np.array(im_over, dtype=np.float32)
    depth = compute_depth_map(pipe, im_over)  # 0=far background, 1=near foreground

    grid_y, grid_x = np.mgrid[0:H, 0:W].astype(np.float32)
    ox = (OW - W) * 0.5
    oy = (OH - H) * 0.5

    rng = np.random.default_rng(abs(hash(out_mp4)) % 100000)
    motes = [
        (rng.uniform(0.05, 0.95) * W, rng.uniform(0.10, 0.90) * H, rng.uniform(3.5, 9.0), rng.uniform(-16, 16), rng.uniform(-22, -8), rng.uniform(0.12, 0.30))
        for _ in range(14 if warm_motes else 6)
    ]

    tmp_mp4 = out_mp4 + ".prelut.mp4"
    writer = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p",
        tmp_mp4
    ], stdin=subprocess.PIPE)

    n_frames = 120  # 4.00s @ 30fps
    for fi in range(n_frames):
        u = fi / float(n_frames - 1)
        u_sm = u * u * (3.0 - 2.0 * u)

        # True 3D multi-plane perspective dolly + lateral parallax:
        # Foreground moves 2.9x faster than background, creating genuine cinema camera depth!
        zoom_bg = 1.02 + 0.045 * u_sm
        zoom_fg_extra = 0.065 * u_sm
        pan_lat = pan_dir * (-22.0 + 44.0 * u_sm)
        pan_vert = -8.0 + 16.0 * math.sin(u * math.pi)

        cx_o, cy_o = OW * 0.5, OH * 0.5
        base_x = grid_x + ox
        base_y = grid_y + oy
        d_local = cv2.remap(depth, base_x, base_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

        eff_zoom = zoom_bg + d_local * zoom_fg_extra
        shift_x = pan_lat * (0.32 + 0.95 * d_local)
        shift_y = pan_vert * (0.35 + 0.75 * d_local)

        map_x = cx_o + (base_x - cx_o) / eff_zoom + shift_x
        map_y = cy_o + (base_y - cy_o) / eff_zoom + shift_y

        warped = cv2.remap(rgb_over, map_x.astype(np.float32), map_y.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)

        # Subtle living sunlight breathing + floating warm bokeh dust motes
        light_breath = 1.0 + 0.025 * math.sin(u * math.pi)
        warped = np.clip(warped * light_breath, 0, 255)

        ov = np.zeros((H, W, 3), dtype=np.float32)
        t_sec = fi / 30.0
        for mx, my, mr, vx, vy, mal in motes:
            px = int((mx + vx * t_sec) % W)
            py = int((my + vy * t_sec) % H)
            cv2.circle(ov, (px, py), int(round(mr)), (255.0 * mal, 236.0 * mal, 198.0 * mal), -1, lineType=cv2.LINE_AA)
        ov = cv2.GaussianBlur(ov, (21, 21), 6.0)
        frame_u8 = np.clip(warped + ov, 0, 255).astype(np.uint8)
        writer.stdin.write(frame_u8.tobytes())

    writer.stdin.close(); writer.wait()
    subprocess.run([PY_EXE, "-X", "utf8", APPLY_LUT, tmp_mp4, out_mp4, LUT_HARM, "--intensity", "0.62"], check=True)
    os.remove(tmp_mp4)
    print("READY_25D_CINEMA_CLIP ->", out_mp4, flush=True)

def main():
    src_paths = sys.argv[1:5]
    assert len(src_paths) == 4, f"Expected 4 image paths, got {len(src_paths)}"
    pipe = load_depth_estimator()

    specs = [
        ("KB05-01 • Khoảng cách vợ chồng ngày một xa", src_paths[0], "ref_kb05_01.png", "kb05_01_silent_distance.mp4",  1.0, False),
        ("KB05-02 • Phụ nữ mệt mỏi, stress & khó chịu", src_paths[1], "ref_kb05_02.png", "kb05_02_tired_stress.mp4",   -1.0, False),
        ("KB05-03 • Chọn im lặng • Cả hai tổn thương", src_paths[2], "ref_kb05_03.png", "kb05_03_silent_back_to_back.mp4", 1.0, False),
        ("KB05-04 • Nói ra đúng cách • Gần nhau hơn",  src_paths[3], "ref_kb05_04.png", "kb05_04_open_heart_talk.mp4", -1.0, True),
    ]

    for _, sp, rfn, vfn, pdir, wm in specs:
        render_25d_parallax_clip(sp, os.path.join(MEDIA, rfn), os.path.join(MEDIA, vfn), pipe, pan_dir=pdir, warm_motes=wm)

    sheet = Image.new("RGB", (1280, 760), (244, 246, 252))
    fnt = ImageFont.truetype(FONT_BOLD, 24)
    for idx, (lbl, _, rfn, vfn, _, _) in enumerate(specs):
        x0 = (idx % 2) * 640 + 16
        y0 = (idx // 2) * 375 + 14
        ImageDraw.Draw(sheet).text((x0, y0), lbl, font=fnt, fill=(20, 24, 38))
        rp = os.path.join(MEDIA, rfn)
        vp = os.path.join(MEDIA, vfn)
        im_r = Image.open(rp).convert("RGB"); im_r.thumbnail((285, 310))
        sheet.paste(im_r, (x0, y0 + 34))
        tjpg = vp + ".qc.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.2", "-i", vp, "-frames:v", "1", tjpg], check=True)
        im_v = Image.open(tjpg).convert("RGB"); im_v.thumbnail((285, 310))
        sheet.paste(im_v, (x0 + 305, y0 + 34))
        os.remove(tjpg)
    qc_p = os.path.join(CHECK, "brolls_kb05_qc.jpg")
    sheet.save(qc_p, quality=93)
    print("SAVED_BROLLS_QC ->", qc_p, flush=True)

if __name__ == "__main__":
    main()
