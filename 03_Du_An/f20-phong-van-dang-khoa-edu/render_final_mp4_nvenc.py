import json, shutil, subprocess, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30

WORK       = Path(r"d:\AI\full studio\output\f20-phong-van-dang-khoa-edu")
MANIFEST   = json.loads((WORK / "project_manifest.json").read_text(encoding="utf-8"))
COINY_TTF  = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7482665772876156165\57619fa23667c87dee08a75d49a8b51a\font.ttf"

FINAL_NAME = "261121 F20 Phỏng vấn Đăng Khoa Edu 77 set quà final.mp4"
OUT_LOCAL  = WORK / FINAL_NAME
OUT_CLIENT = Path(r"Z:\Máy tính khác\My Computer\F20\Final") / FINAL_NAME
OUT_CLOUD  = Path(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final") / FINAL_NAME
OUT_ARCHIVE = Path(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\f20-phong-van-dang-khoa-edu")


def build_base_video_and_voice():
    """
    1) Resolves flat non-overlapping visual slices (Track 1 B-roll overrides Track 0).
    2) Renders each visual slice cleanly to local D: using NVENC, then concats with -c copy into base_video.mp4.
    3) Extracts & concatenates Track-0 dialogue audio with per-speaker gain, micro-fades & broadcast voice polish -> voice_master.wav.
    """
    t0_segs = MANIFEST["track0"]
    brolls  = sorted(MANIFEST["brolls"], key=lambda x: x["t0"])
    total_s = MANIFEST["total_s"]

    # Build flat visual intervals [a, b]
    pts = {0.0, total_s}
    for s in t0_segs:
        pts.add(s["tl_start"]); pts.add(s["tl_end"])
    for b in brolls:
        pts.add(b["t0"]); pts.add(b["t1"])
    pts_sorted = sorted(pts)

    visual_slices = []
    for i in range(len(pts_sorted) - 1):
        a, b = pts_sorted[i], pts_sorted[i + 1]
        if b - a < 0.02:
            continue
        mid = 0.5 * (a + b)
        # Check B-roll first
        chosen = None
        for br in brolls:
            if br["t0"] - 1e-4 <= mid < br["t1"] + 1e-4:
                src_in = br["src_in"] + (a - br["t0"]) * br["speed"]
                chosen = (br["path"], src_in, b - a, br["speed"], False)
                break
        if chosen is None:
            for s in t0_segs:
                if s["tl_start"] - 1e-4 <= mid < s["tl_end"] + 1e-4:
                    src_in = s["src_in"] + (a - s["tl_start"]) * s["speed"]
                    is_banner = (s["id"] == "25_banner")
                    chosen = (s["path"], src_in, b - a, s["speed"], is_banner)
                    break
        assert chosen is not None, f"No visual at {mid:.3f}s!"
        visual_slices.append((a, b, *chosen))

    slices_dir = WORK / "render_slices"
    if slices_dir.exists():
        shutil.rmtree(slices_dir)
    slices_dir.mkdir(parents=True)

    print(f"1) Rendering {len(visual_slices)} base visual slices on GPU (h264_nvenc)...", flush=True)
    concat_v_lines = []
    for idx, (a, b, path, src_in, dur_tl, spd, is_banner) in enumerate(visual_slices):
        out_f = slices_dir / f"v_{idx:03d}.ts"
        src_dur = dur_tl * spd
        n_frames = max(1, int(round(dur_tl * FPS)))
        vf = f"setpts=(PTS-STARTPTS)/{spd:.6f},fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p"
        if is_banner:
            vf += ",fade=t=in:st=0:d=0.22"
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{src_in:.4f}", "-t", f"{src_dur + 0.15:.4f}", "-i", path,
            "-an", "-vf", vf, "-frames:v", str(n_frames),
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
            "-f", "mpegts", str(out_f)
        ]
        subprocess.run(cmd, check=True)
        concat_v_lines.append(f"file '{out_f.as_posix()}'")

    vlist = slices_dir / "vlist.txt"
    vlist.write_text("\n".join(concat_v_lines), encoding="utf-8")
    base_video = WORK / "base_video.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(vlist),
        "-c", "copy", str(base_video)
    ], check=True)
    print(f"   Base video built -> {base_video.name}", flush=True)

    # Build Track-0 Dialogue Master WAV with exact speaker leveling & micro-fades!
    print(f"2) Building balanced Track-0 Dialogue Master WAV ({len(t0_segs)} segments)...", flush=True)
    concat_a_lines = []
    for idx, s in enumerate(t0_segs):
        out_a = slices_dir / f"a_{idx:03d}.wav"
        dur_tl = s["tl_dur_u"] / 1e6
        if s["vol"] <= 0.001:
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-t", f"{dur_tl:.6f}", "-c:a", "pcm_s16le", str(out_a)
            ], check=True)
        else:
            src_dur = dur_tl * s["speed"]
            # Gentle highpass + speaker gain + micro-fades (33ms in, 67ms out)
            af = (
                f"atempo={s['speed']:.6f},"
                f"highpass=f=85,"
                f"volume={s['vol']:.3f},"
                f"afade=t=in:st=0:d=0.033,"
                f"afade=t=out:st={max(0.0, dur_tl - 0.067):.4f}:d=0.067,"
                f"apad,atrim=0:{dur_tl:.6f}"
            )
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-ss", f"{s['src_in']:.4f}", "-t", f"{src_dur + 0.15:.4f}", "-i", s["path"],
                "-vn", "-af", af, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out_a)
            ], check=True)
        concat_a_lines.append(f"file '{out_a.as_posix()}'")

    alist = slices_dir / "alist.txt"
    alist.write_text("\n".join(concat_a_lines), encoding="utf-8")
    voice_raw = WORK / "voice_raw.wav"
    voice_master = WORK / "voice_master.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(alist), "-c", "copy", str(voice_raw)], check=True)
    # Broadcast voice polish: smooth leveling compressor + gentle 3kHz clarity + limiter
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(voice_raw),
        "-af", "acompressor=threshold=-22dB:ratio=2.8:attack=10:release=140:makeup=3dB,equalizer=f=2800:width_type=q:width=1.2:g=1.5,alimiter=limit=0.92",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(voice_master)
    ], check=True)
    print(f"   Voice master built -> {voice_master.name}", flush=True)
    return base_video, voice_master


def build_final_audio_mix(voice_master: Path) -> Path:
    """
    Mixes Voice Master + Warm Acoustic Corporate BGM (sidechain-ducked under speech, rising on Banner, 1.4s fade-out)
    + all 23 Ear-Verified Tactile SFX -> -14.0 LUFS broadcast AAC!
    """
    print("3) Mixing Voice + Sidechain-Ducked Acoustic BGM + 23 Tactile SFX (-14.0 LUFS)...", flush=True)
    total_s = MANIFEST["total_s"]
    bgm = MANIFEST["bgm"]
    sfxs = MANIFEST["sfx"]

    # First pre-mix all SFX into 1 clean stereo WAV at exact timeline offsets!
    sfx_inputs = ["-f", "lavfi", "-t", f"{total_s:.4f}", "-i", "anullsrc=r=48000:cl=stereo"]
    sfx_fchains = []
    sfx_labels = ["[0:a]"]
    for i, sf in enumerate(sfxs, start=1):
        sfx_inputs += ["-t", f"{sf['max_dur']:.3f}", "-i", sf["path"]]
        delay_ms = max(0, int(round(sf["t0"] * 1000)))
        vol = sf["vol_cc"] * 1.15  # slightly crisp in final mix (-18..-20dB under voice)
        fd_out = min(0.12, sf["max_dur"] / 3.0)
        sfx_fchains.append(
            f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"afade=t=in:st=0:d=0.015,afade=t=out:st={max(0.0, sf['max_dur']-fd_out):.3f}:d={fd_out:.3f},"
            f"volume={vol:.3f},adelay={delay_ms}|{delay_ms}[s{i}]"
        )
        sfx_labels.append(f"[s{i}]")

    sfx_mix_wav = WORK / "sfx_mix.wav"
    fc_sfx = ";".join(sfx_fchains) + f";{''.join(sfx_labels)}amix=inputs={len(sfx_labels)}:duration=first:normalize=0[sout]"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", *sfx_inputs,
        "-filter_complex", fc_sfx, "-map", "[sout]",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(sfx_mix_wav)
    ], check=True)

    # Now mix Voice + Sidechain-Ducked BGM + SFX -> Broadcast -14.0 LUFS AAC!
    audio_final = WORK / "audio_final.m4a"
    fc_mix = (
        f"[0:a]asplit=2[v_main][v_sc];"
        f"[1:a]atrim=2.0:{2.0 + total_s:.4f},asetpts=PTS-STARTPTS,"
        f"aformat=sample_rates=48000:channel_layouts=stereo,"
        f"equalizer=f=2200:width_type=q:width=1.0:g=-2.5,"
        f"volume=0.22,afade=t=in:st=0:d=0.45,afade=t=out:st={max(0.0, total_s - 1.40):.4f}:d=1.40[bgm_pre];"
        f"[bgm_pre][v_sc]sidechaincompress=threshold=0.025:ratio=3.5:attack=25:release=320[bgm_duck];"
        f"[v_main][bgm_duck][2:a]amix=inputs=3:duration=first:normalize=0,"
        f"loudnorm=I=-14.0:TP=-1.0:LRA=11[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(voice_master), "-i", bgm["path"], "-i", str(sfx_mix_wav),
        "-filter_complex", fc_mix, "-map", "[aout]",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(audio_final)
    ], check=True)
    print(f"   Final audio mixed (-14.0 LUFS) -> {audio_final.name}", flush=True)
    return audio_final


def render_text_roi(text: str, font: ImageFont.FreeTypeFont, fill_rgb: tuple, stroke_rgb: tuple, stroke_w: int,
                    cx: int, cy: int):
    """Pre-renders tight RGBA ROI for ultra-fast NumPy compositing!"""
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(tmp)
    bb = dr.multiline_textbbox((0, 0), text, font=font, stroke_width=stroke_w, align="center", spacing=8)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x_draw = cx - tw // 2 - bb[0]
    y_draw = cy - th // 2 - bb[1]
    # Subtle soft drop shadow for legibility
    dr.multiline_text((x_draw + 2, y_draw + 4), text, font=font, fill=(0, 0, 0, 95),
                      stroke_width=stroke_w + 1, stroke_fill=(0, 0, 0, 95), align="center", spacing=8)
    dr.multiline_text((x_draw, y_draw), text, font=font, fill=(*fill_rgb, 255),
                      stroke_width=stroke_w, stroke_fill=(*stroke_rgb, 255), align="center", spacing=8)
    bbox = tmp.getbbox()
    if not bbox:
        return None
    x0, y0, x1, y1 = bbox
    crop = np.array(tmp.crop((x0, y0, x1, y1)), dtype=np.float32)
    return (x0, y0, x1, y1, crop[:, :, :3], crop[:, :, 3:4] / 255.0)


def render_circle_roi(png_path: str, px: float, py: float, sc: float):
    im = Image.open(png_path).convert("RGBA")
    nw, nh = int(round(W * sc)), int(round(H * sc))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    cx = int(round((px + 1.0) * 0.5 * W))
    cy = int(round((1.0 - py) * 0.5 * H))
    # Crop tight bounding box of the non-transparent circle!
    bb = im.getbbox()
    bx0, by0, bx1, by1 = bb
    crop_im = im.crop((bx0, by0, bx1, by1))
    dst_x0 = cx - nw // 2 + bx0
    dst_y0 = cy - nh // 2 + by0
    dst_x1 = dst_x0 + crop_im.width
    dst_y1 = dst_y0 + crop_im.height
    # Clip to frame bounds
    cx0, cy0 = max(0, dst_x0), max(0, dst_y0)
    cx1, cy1 = min(W, dst_x1), min(H, dst_y1)
    arr = np.array(crop_im.crop((cx0 - dst_x0, cy0 - dst_y0, cx1 - dst_x0, cy1 - dst_y0)), dtype=np.float32)
    return (cx0, cy0, cx1, cy1, arr[:, :, :3], arr[:, :, 3:4] / 255.0)


def composite_overlays_and_mux(base_video: Path, audio_final: Path):
    print("4) Pre-rendering Circle Badges, Native-Style Coiny Subtitles & Headers...", flush=True)
    fnt_sub = ImageFont.truetype(COINY_TTF, 46)
    fnt_hdr = ImageFont.truetype(COINY_TTF, 50)

    # Precompute overlay items: (t0, t1, fade_in, fade_out, roi_tuple)
    overlays = []
    for c in MANIFEST["circles"]:
        roi = render_circle_roi(c["path"], c["px"], c["py"], c["sc"])
        overlays.append((c["t0"], c["t1"], 0.18, 0.18, roi))

    for h in MANIFEST["headers"]:
        cx = int(round((h["px"] + 1.0) * 0.5 * W))
        cy = int(round((1.0 - h["py"]) * 0.5 * H))
        roi = render_text_roi(h["text"], fnt_hdr, (255, 255, 255), (236, 29, 29), 8, cx, cy)
        if roi:
            overlays.append((h["t0"], h["t1"], 0.20, 0.20, roi))

    sub_cy = int(round((1.0 - (-0.58)) * 0.5 * H))  # exact CapCut Y = -0.58!
    for sb in MANIFEST["subtitles"]:
        if sb["highlight"]:
            roi = render_text_roi(sb["text"], fnt_sub, (255, 255, 255), (236, 29, 29), 7, W // 2, sub_cy)
        else:
            roi = render_text_roi(sb["text"], fnt_sub, (236, 29, 29), (255, 255, 255), 7, W // 2, sub_cy)
        if roi:
            overlays.append((sb["t0"], sb["t1"], 0.0, 0.0, roi))

    print(f"   Pre-rendered {len(overlays)} tight RGBA ROIs. Streaming GPU composite -> {OUT_LOCAL.name}...", flush=True)
    t_start = time.time()

    dec = subprocess.Popen([
        "ffmpeg", "-v", "error", "-i", str(base_video),
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ], stdout=subprocess.PIPE)

    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(audio_final),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", "-shortest", str(OUT_LOCAL)
    ], stdin=subprocess.PIPE)

    frame_bytes = W * H * 3
    f_idx = 0
    while True:
        raw = dec.stdout.read(frame_bytes)
        if len(raw) < frame_bytes:
            break
        t = f_idx / float(FPS)
        # Fast-path: check if any overlay is active on this frame
        active = []
        for t0, t1, fi, fo, roi in overlays:
            if t0 <= t < t1:
                a_mul = 1.0
                if fi > 0 and (t - t0) < fi:
                    a_mul = min(a_mul, max(0.0, (t - t0) / fi))
                if fo > 0 and (t1 - t) < fo:
                    a_mul = min(a_mul, max(0.0, (t1 - t) / fo))
                active.append((a_mul, roi))

        if active:
            frame = np.frombuffer(raw, dtype=np.uint8).reshape((H, W, 3)).copy()
            for a_mul, (x0, y0, x1, y1, fg_rgb, fg_a) in active:
                if a_mul <= 0.005:
                    continue
                alpha = fg_a if a_mul >= 0.995 else (fg_a * a_mul)
                bg = frame[y0:y1, x0:x1].astype(np.float32)
                frame[y0:y1, x0:x1] = np.clip(bg * (1.0 - alpha) + fg_rgb * alpha, 0, 255).astype(np.uint8)
            enc.stdin.write(frame.tobytes())
        else:
            enc.stdin.write(raw)
        f_idx += 1
        if f_idx % 900 == 0:
            print(f"   Composited {f_idx} frames ({f_idx/FPS:.1f}s) in {time.time()-t_start:.1f}s...", flush=True)

    dec.stdout.close(); dec.wait()
    enc.stdin.close(); enc.wait()
    assert enc.returncode == 0, f"NVENC encode failed with code {enc.returncode}!"
    print(f"   DONE RENDER: {f_idx} frames ({f_idx/FPS:.2f}s) in {time.time()-t_start:.1f}s -> {OUT_LOCAL.stat().st_size/1e6:.1f} MB", flush=True)


def verify_and_deliver():
    # 1. Extract 8-frame QC contact sheet DIRECTLY from the rendered Final MP4!
    total_s = MANIFEST["total_s"]
    sample_ts = [2.0, 15.8, 46.8, 70.8, 118.8, 150.5, 200.5, total_s - 1.0]
    cols, rows = 4, 2
    tw, th = 360, 640
    sheet = Image.new("RGB", (cols * tw, rows * (th + 24)), (16, 18, 22))
    dr = ImageDraw.Draw(sheet)
    for idx, ts in enumerate(sample_ts):
        tmp = WORK / f"_fmp4_{idx}.jpg"
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{ts:.2f}","-i",str(OUT_LOCAL),"-frames:v","1","-update","1","-vf",f"scale={tw}:{th}",str(tmp)], check=True)
        r, c = divmod(idx, cols)
        sheet.paste(Image.open(tmp), (c * tw, r * (th + 24) + 24))
        dr.text((c * tw + 8, r * (th + 24) + 5), f"FINAL MP4 @{ts:05.1f}s", fill=(160, 255, 190))
        tmp.unlink()
    qc_final = WORK / "qc_final_mp4_8frames.jpg"
    sheet.save(qc_final, quality=90)

    # 2. Measure integrated loudness of Final MP4
    r_lu = subprocess.run([
        "ffmpeg", "-v", "info", "-i", str(OUT_LOCAL), "-af", "loudnorm=print_format=json", "-f", "null", "-"
    ], capture_output=True, text=True)
    print("\n=== FINAL MP4 LOUDNESS REPORT ===")
    for ln in r_lu.stderr.splitlines():
        if any(k in ln for k in ("input_i", "input_tp", "input_lra")):
            print(" ", ln.strip())

    # 3. Copy Final MP4 to Official F20 Client Folder + Cloud 04_Videos_Final + Archive scripts/QC to 03_Du_An!
    OUT_CLIENT.parent.mkdir(parents=True, exist_ok=True)
    OUT_CLOUD.parent.mkdir(parents=True, exist_ok=True)
    OUT_ARCHIVE.mkdir(parents=True, exist_ok=True)

    shutil.copy2(OUT_LOCAL, OUT_CLIENT)
    shutil.copy2(OUT_LOCAL, OUT_CLOUD)
    for fn in ("build_capcut_dkedu_project.py", "render_final_mp4_nvenc.py", "project_manifest.json",
               "transcripts_readable.md", "qc_dkedu_master_12.jpg", "qc_final_mp4_8frames.jpg"):
        src = WORK / fn
        if src.exists():
            shutil.copy2(src, OUT_ARCHIVE / fn)

    print(f"\nDELIVERED FINAL MP4:")
    print(f"  -> Client Folder: {OUT_CLIENT}")
    print(f"  -> Cloud Backup : {OUT_CLOUD}")
    print(f"  -> Project Arch : {OUT_ARCHIVE}")
    print(f"  -> Final QC Img : {qc_final}")


if __name__ == "__main__":
    bv, vm = build_base_video_and_voice()
    af = build_final_audio_mix(vm)
    composite_overlays_and_mux(bv, af)
    verify_and_deliver()
