import concurrent.futures, json, math, os, shutil, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw

SRC_MP4   = r"C:\Users\Hang thu\Downloads\260904 HTPM KB03 - Sau 30 Tuổi Đừng Chỉ Soi Nếp Nh.mp4"
PROJ_DIR  = r"d:\AI\full studio\output\htpm7-261121"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll_dl")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
STEMS_DIR = os.path.join(PROJ_DIR, "audio_stems_dl")
for d in (AROLL_DIR, CHECK_DIR, STEMS_DIR):
    os.makedirs(d, exist_ok=True)

PY_EXE     = r"d:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
TRANSCRIBE = r"d:\AI\full studio\phong-cach\talking-head\tools\transcribe.py"
RVM_MODEL  = r"d:\AI\full studio\phong-cach\talking-head\tools\models\rvm_mobilenetv3_fp32.onnx"
LUT_ROSY   = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\01_HTPM_Beauty_Rosy_Skin.cube"

mc_raw    = os.path.join(AROLL_DIR, "_mc_full.mp4")
mc        = os.path.join(AROLL_DIR, "main_cut.mp4")
mc_graded = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
mc_json   = os.path.join(AROLL_DIR, "main_cut.json")
matte_out = os.path.join(AROLL_DIR, "main_cut_matte.mp4")

def rvm_chunk_worker(args):
    idx, in_mp4, out_mp4 = args
    sys.path.insert(0, r"d:\AI\full studio\phong-cach\talking-head\tools")
    from _cuda import add_cuda_dlls
    add_cuda_dlls()
    import onnxruntime as ort

    so = ort.SessionOptions()
    so.intra_op_num_threads = 4
    so.inter_op_num_threads = 1
    prov = [p for p in ("CUDAExecutionProvider", "CPUExecutionProvider") if p in ort.get_available_providers()]
    sess = ort.InferenceSession(RVM_MODEL, sess_options=so, providers=prov)

    w, h = 1080, 1920
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", in_mp4, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{w}x{h}",
        "-r", "30", "-i", "-", "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "15", "-pix_fmt", "yuv420p", out_mp4
    ], stdin=subprocess.PIPE)

    rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    dr  = np.array([0.25], np.float32)
    fsize, n_done, t_c = w * h * 3, 0, time.time()
    while True:
        buf = dec.stdout.read(fsize)
        if len(buf) < fsize:
            break
        rgb = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        src = (rgb.astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        fgr, pha, *rec = sess.run(None, {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dr})
        alpha = (np.clip(pha[0, 0], 0, 1) * 255 + 0.5).astype(np.uint8)
        enc.stdin.write(alpha.tobytes())
        n_done += 1
    enc.stdin.close(); enc.wait()
    dec.stdout.close(); dec.wait()
    print(f"  [RVM Chunk {idx}] {prov[0]}: {n_done} frames in {time.time() - t_c:.1f}s", flush=True)
    return out_mp4

def main():
    t0 = time.time()
    print("[1/5] Normalizing Downloads KB03 -> 30fps CFR (h264_nvenc)...", flush=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", SRC_MP4,
        "-r", "30", "-fps_mode", "cfr",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        mc_raw
    ], check=True)

    cnt_raw = int(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", mc_raw
    ], text=True).strip())

    tail_start = max(0, cnt_raw - 90)
    raw_tail = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", mc_raw,
        "-vf", f"select='gte(n,{tail_start})',scale=90:160", "-fps_mode", "passthrough",
        "-f", "rawvideo", "-pix_fmt", "gray", "-"
    ])
    tail_arr = np.frombuffer(raw_tail, dtype=np.uint8).reshape((-1, 160, 90))
    valid_frames = cnt_raw
    for k in range(len(tail_arr) - 1, -1, -1):
        if float(tail_arr[k].mean()) > 12.0:
            valid_frames = min(cnt_raw, tail_start + k + 1)
            break

    dur_exact = valid_frames / 30.0
    print(f"  -> Raw frames={cnt_raw}, non-black valid frames={valid_frames} ({dur_exact:.3f}s)", flush=True)

    if valid_frames < cnt_raw:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", mc_raw,
            "-frames:v", str(valid_frames), "-t", f"{dur_exact:.6f}",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            mc
        ], check=True)
        os.remove(mc_raw)
    else:
        if os.path.exists(mc):
            os.remove(mc)
        os.rename(mc_raw, mc)

    grid = Image.new("RGB", (270 * 6, 480 * 2))
    for i in range(12):
        ts = min(dur_exact - 0.25, 0.4 + i * (dur_exact - 0.9) / 11.0)
        fp = os.path.join(CHECK_DIR, f"_rdl_{i:02d}.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", mc, "-frames:v", "1", fp], check=True)
        im = Image.open(fp).convert("RGB")
        d = ImageDraw.Draw(im)
        for y_mark in (205, 320, 380, 440, 750, 1096, 1568, 1602):
            d.line([(0, y_mark), (1080, y_mark)], fill=(255, 220, 40), width=3)
            d.rectangle([8, y_mark - 28, 130, y_mark - 2], fill=(16, 20, 32))
            d.text((14, y_mark - 24), f"y={y_mark}", fill=(255, 235, 110))
        d.rectangle([10, 10, 260, 58], fill=(16, 20, 32))
        d.text((20, 22), f"t={ts:.1f}s", fill=(255, 255, 255))
        grid.paste(im.resize((270, 480), Image.Resampling.LANCZOS), ((i % 6) * 270, (i // 6) * 480))
        os.remove(fp)
    grid.save(os.path.join(CHECK_DIR, "raw_sheet_dl.jpg"), quality=92)

    lut_tmp = os.path.join(AROLL_DIR, "_rosy.cube")
    shutil.copy2(LUT_ROSY, lut_tmp)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", mc, "-frames:v", str(valid_frames), "-an",
        "-filter_complex", "[0:v]split=2[a][b];[b]lut3d=_rosy.cube[bg];[a][bg]blend=all_expr=A*0.45+B*0.55[v]",
        "-map", "[v]", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p",
        mc_graded
    ], cwd=AROLL_DIR, check=True)
    os.remove(lut_tmp)
    print(f"[2/5] GPU RosySkin LUT graded ({valid_frames} frames) in {time.time() - t0:.1f}s!", flush=True)

    # Step 3: Run Demucs GPU + Whisper CPU (no ONNX thread contention!)
    orig_wav = os.path.join(STEMS_DIR, "orig_input.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mc, "-ar", "44100", "-ac", "2", orig_wav], check=True)
    print("[3/5] Running Demucs GPU + Whisper (zero thread contention)...", flush=True)
    p_dem = subprocess.Popen([PY_EXE, "-m", "demucs.separate", "--two-stems", "vocals", "-n", "htdemucs", "-o", os.path.join(STEMS_DIR, "demucs_out"), orig_wav])
    p_wh  = subprocess.Popen([PY_EXE, "-X", "utf8", TRANSCRIBE, mc, mc_json, "--lang", "vi", "--cpu", "--prompt", "Hằng Thu Pharma, nếp nhăn, lão hóa, nội tiết tố, skincare, serum, kem dưỡng, chống nắng, phụ khoa, chị em, tuổi 30"])
    if p_dem.wait() != 0 or p_wh.wait() != 0:
        raise RuntimeError("Demucs or Whisper failed!")
    print(f"  -> Demucs + Whisper done at {time.time() - t0:.1f}s!", flush=True)

    # Step 4: Run 4x RVM workers pinned to 4 intra-op threads each (16 threads total -> zero CPU thrashing!)
    print("[4/5] Running 4x pinned RVM workers...", flush=True)
    n_chunks = 4
    step = math.ceil(valid_frames / n_chunks)
    tasks, tmp_files = [], []
    for c_i in range(n_chunks):
        f0 = c_i * step
        f1 = min(valid_frames, (c_i + 1) * step)
        if f0 >= f1:
            continue
        p_in  = os.path.join(AROLL_DIR, f"_p_{c_i}.mp4")
        p_out = os.path.join(AROLL_DIR, f"_m_{c_i}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", mc,
            "-vf", f"select='between(n,{f0},{f1-1})',setpts=N/30/TB",
            "-fps_mode", "cfr", "-r", "30", "-an",
            "-c:v", "h264_nvenc", "-preset", "p3", "-cq", "16", p_in
        ], check=True)
        tasks.append((c_i, p_in, p_out))
        tmp_files.extend([p_in, p_out])

    with concurrent.futures.ProcessPoolExecutor(max_workers=n_chunks) as ex:
        m_outs = list(ex.map(rvm_chunk_worker, tasks))

    lst = os.path.join(AROLL_DIR, "_m_concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for mo in m_outs:
            f.write("file '" + mo.replace("\\", "/") + "'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", matte_out], check=True)
    for tf in tmp_files + [lst]:
        if os.path.exists(tf):
            os.remove(tf)

    mcnt = int(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
        "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", matte_out
    ], text=True).strip())
    print(f"[5/5] Verified RVM Matte frames={mcnt}/{valid_frames} in total {time.time() - t0:.1f}s!", flush=True)

    # Measure baked-in BGM (Non-Speech RMS)
    voc_p = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "vocals.wav")
    bgm_p = os.path.join(STEMS_DIR, "demucs_out", "htdemucs", "orig_input", "no_vocals.wav")
    raw_orig = subprocess.check_output(["ffmpeg", "-v", "error", "-i", orig_wav, "-ac", "2", "-ar", "48000", "-f", "f32le", "-"])
    arr_orig = np.frombuffer(raw_orig, dtype=np.float32).reshape((-1, 2))
    raw_voc = subprocess.check_output(["ffmpeg", "-v", "error", "-i", voc_p, "-ac", "2", "-ar", "48000", "-f", "f32le", "-"])
    arr_voc = np.frombuffer(raw_voc, dtype=np.float32).reshape((-1, 2))
    raw_bgm = subprocess.check_output(["ffmpeg", "-v", "error", "-i", bgm_p, "-ac", "2", "-ar", "48000", "-f", "f32le", "-"])
    arr_bgm = np.frombuffer(raw_bgm, dtype=np.float32).reshape((-1, 2))
    n_min = min(len(arr_orig), len(arr_voc), len(arr_bgm))
    hop = 2400
    nh = n_min // hop
    voc_hops = np.sqrt(np.mean(arr_voc[:nh*hop].reshape((nh, hop, 2))**2, axis=(1, 2)))
    orig_hops = np.sqrt(np.mean(arr_orig[:nh*hop].reshape((nh, hop, 2))**2, axis=(1, 2)))
    non_sp_mask = voc_hops < 0.008
    non_sp_rms = float(np.sqrt(np.mean(orig_hops[non_sp_mask]**2))) if np.any(non_sp_mask) else float(np.min(orig_hops))
    print(f"[AUDIO CHECK DL] Orig Non-Speech RMS = {20*np.log10(max(1e-7, non_sp_rms)):.2f} dBFS | Demucs Vocals = {20*np.log10(max(1e-7, float(np.sqrt(np.mean(arr_voc**2))))):.2f} dBFS | Demucs No-Vocals = {20*np.log10(max(1e-7, float(np.sqrt(np.mean(arr_bgm**2))))):.2f} dBFS", flush=True)

    tr = json.load(open(mc_json, "r", encoding="utf-8"))
    print(f"\n=== DOWNLOADS TRANSCRIPT ({len(tr['segments'])} segments, {valid_frames} frames = {dur_exact:.3f}s) ===")
    for seg in tr["segments"]:
        print(f"  [{seg['start']:5.2f} - {seg['end']:5.2f}] {seg['text'].strip()}")

if __name__ == "__main__":
    main()
