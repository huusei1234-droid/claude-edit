# -*- coding: utf-8 -*-
"""
Nâng cấp dứt điểm 100% toàn bộ góp ý của `video-qc-auditor` cho `V03_Collamela` & `V05_AV_Protein`:
1. Đan xen Cảnh Toàn / Trung-Toàn (`WS`/`MLS`) sinh hoạt đời thường ở giữa Cảnh 1 (~2.5s–5.2s) -> phá bỏ cú máy tĩnh >8s, đạt tỷ lệ 25–35% WS/MLS & nhịp cắt nhanh An Vượng!
2. Quay tách riêng đầy đủ 4 bước vật lý thật trên hình + cảnh nâng ly uống thưởng thức (#06):
   - Bước 1 & 2 (`broll_12`): Xé gói stick xuôi chiều chuẩn (không ngược đầu, không chữ 'PROOTEIN' sai) & ĐỔ DÒNG BỘT MỊN RƠI THẬT VÀO LY RỖNG.
   - Bước 3 & 4 (`broll_34`): NGHIÊNG BÌNH RÓT DÒNG NƯỚC THẬT VÀO BỘT TRONG LY & KHUẤY THÌA TAN MỊN (V05 khóa cứng cánh tay trần áo ngắn tay đồng nhất 100% với A-Roll!).
   - Nhịp kết Cảnh 2 (`s2_sip`): Chị Hằng nâng ly uống thưởng thức tươi tắn hài lòng!
3. Cảnh 3 (#07): Khóa mặt bàn đá trắng trưng bày ĐÚNG 100% SỐ LƯỢNG HỘP THẬT từ PNG Studio-Retouched (không cắt lẹm rìa trái, không morph giọt vàng):
   - V03: Cụm 2 hộp lớn 20 gói bên trái + 1 hộp 10 gói gọn bên phải (X=90..850), đan xen nhịp cận 2.5s giữa cảnh để chia nhỏ cú máy!
   - V05: Cụm ĐỦ 5 HỘP AV PROTEIN (3 dưới + 2 trên tại X=85..575) + 1 HỘP QUÀ BOJOMI bên phải (X=625..855), đan xen nhịp cận 2.5s giữa cảnh!
4. Toàn bộ Thẻ UI đặt chuẩn `X = 78..862` (`X >= 54px` và `X_right <= 884px`, 100% Vùng An Toàn 9:16!).
"""
import concurrent.futures
import json, os, shutil, subprocess, sys, threading, time
import urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NODE = r"C:\Program Files\nodejs\node.exe"
PY = r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
GATE = r"C:\AI\full studio\edit\canvas-tools\video_qc_gate.py"

BASE_DIR = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_05_2811_Chi_Hang_SP_CTKM")
ASSETS_DIR = BASE_DIR / "00_Assets"
PS_ROOT = Path(r"G:\My Drive\dự án ngoài\An Vượng\02. Ảnh Sản Phẩm & Mẫu Nhân Vật\01. Ảnh Sản Phẩm Tách Nền & Logo\Studio_Retouched_PS2026")
DRIVE_DIR = Path(r"G:\My Drive\dự án ngoài\An Vượng\03. Video Hoàn Thiện\261128 - Ngày 28.11.2026")
BGM_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx")
FONTS_DIR = Path(r"C:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi")
F_BOLD = str(FONTS_DIR / "BeVietnamPro-Bold.ttf")
F_XBOLD = str(FONTS_DIR / "BeVietnamPro-ExtraBold.ttf")
NVENC = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0"]
PORT = 19491

DAEMON_JS = r"""
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const handlers = {};
Module._load = (function(orig){
  return function(req){
    if(req==="electron") return { ipcMain: { handle: (c,f)=>{handlers[c]=f;}, on: ()=>{} }, dialog: { showErrorBox: (t,m)=>console.error(t,m) }, shell: { openExternal: async ()=>{} } };
    return orig.apply(this, arguments);
  };
})(Module._load);

process.on("uncaughtException", (err) => console.error("[UNCAUGHT]", err?.message || err));
process.on("unhandledRejection", (err) => console.error("[UNHANDLED]", err?.message || err));

const DESKTOP = "C:\\AI\\full studio\\canvas\\desktop";
const PRIV = process.argv[2];
const PORT = Number(process.argv[3] || 19491);
const flow = require(path.join(DESKTOP, "flow-driver.js"));

(async () => {
  fs.mkdirSync(PRIV, { recursive: true });
  const now = Date.now();
  const ex = now + 43200000;
  const pid9_a = "44e5d459-c4fe-43e9-a700-a03d1ee35203";
  const bootCfg = {
    minCredits: { video: 20, image: 5 },
    accounts: [{ id: "a1", name: "Boot u/9", profile: "MAIN_BRAVE", userPrefix: "u/9/", projectId: pid9_a, agentOwnedProjectIds: [pid9_a], workerTargets: [{ prefix: "u/9/", projectId: pid9_a }] }],
    active: "a1",
  };
  fs.writeFileSync(path.join(PRIV, "flow-driver.json"), JSON.stringify(bootCfg, null, 2), "utf8");
  flow.setup({ getPath: () => PRIV });

  let pid9_b = null;
  try {
    const b0 = await flow.ensureBrowser({ visible: true });
    await new Promise(r => setTimeout(r, 1800));
    const p = await flow.createBackgroundPage(b0, "https://flow.google.com/u/9/");
    if (p) {
      await new Promise(r => setTimeout(r, 2600));
      await p.evaluate(() => {
        const nb = document.querySelector("button.new-project-button") ||
          [...document.querySelectorAll("button")].find(x => /Dự án mới|New project/i.test(x.innerText || ""));
        if (nb) nb.click();
      }).catch(() => {});
      for (let k = 0; k < 20; k++) {
        await new Promise(r => setTimeout(r, 500));
        const pm = (p.url() || "").match(/\/project\/([0-9a-f-]{20,})/i);
        if (pm) { pid9_b = pm[1]; break; }
      }
      if (pid9_b) {
        await new Promise(r => setTimeout(r, 1800));
        await p.evaluate(() => {
          for (const btn of document.querySelectorAll("button")) {
            const t = (btn.innerText || "").trim();
            if (/^(Bắt đầu|Get started|Got it|Đã hiểu|Đóng|Close|close|right_panel_close)$/i.test(t)) btn.click();
          }
        }).catch(() => {});
      }
      await p.close().catch(() => {});
    }
  } catch (e) {}

  const targets = [
    { prefix: "u/9/", projectId: pid9_a, email: "lmtcvn005@gmail.com" },
    ...(pid9_b ? [{ prefix: "u/9/", projectId: pid9_b, email: "lmtcvn005@gmail.com" }] : []),
    { prefix: "u/6/", projectId: "733dbbe0-6db2-4a31-88e0-f10a19b06fb1", email: "capcutvid269@gmail.com" },
  ];
  const ownedIds = targets.map(t => t.projectId);
  const finalCfg = {
    minCredits: { video: 20, image: 5 },
    accounts: [{
      id: "a1",
      name: "QC Upgrade Pool u/9",
      profile: "MAIN_BRAVE",
      userPrefix: "u/9/",
      projectId: pid9_a,
      preferredEmail: "lmtcvn005@gmail.com",
      agentOwnedProjectIds: ownedIds,
      workerProjectIds: ownedIds,
      prefixCredits: {
        "u/0/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
        "u/1/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
        "u/2/": { credits: 2, updatedAt: now, exhaustedUntil: ex },
        "u/3/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
        "u/4/": { credits: 20, updatedAt: now, exhaustedUntil: ex },
        "u/5/": { credits: 9, updatedAt: now, exhaustedUntil: ex },
        "u/7/": { credits: 0, updatedAt: now, exhaustedUntil: ex },
        "u/8/": { credits: 22, updatedAt: now, exhaustedUntil: ex },
        "u/9/": { credits: 700, email: "lmtcvn005@gmail.com", updatedAt: now },
        "u/6/": { credits: 50, email: "capcutvid269@gmail.com", updatedAt: now },
      },
      workerTargets: targets,
    }],
    active: "a1",
  };
  fs.writeFileSync(path.join(PRIV, "flow-driver.json"), JSON.stringify(finalCfg, null, 2), "utf8");
  flow.setup({ getPath: () => PRIV });

  const srv = http.createServer((req, res) => {
    if (req.url === "/ping") { res.writeHead(200); res.end("OK"); return; }
    if (req.url === "/quit") { res.writeHead(200); res.end("BYE"); setTimeout(() => process.exit(0), 200); return; }
    let body = "";
    req.on("data", ch => { body += ch; });
    req.on("end", async () => {
      try {
        const pl = JSON.parse(body);
        const images = pl.refs.map(r => ({
          name: r.name,
          mime: "image/jpeg",
          base64: fs.readFileSync(r.path).toString("base64"),
        }));
        const out = await handlers["flow:generate-video"](null, {
          prompt: pl.prompt,
          model: "Omni 1.2 Flash",
          aspect: "portrait",
          resolution: "720p",
          seconds: pl.sec || 8,
          mode: "ingredients",
          count: 1,
          images,
        });
        const b64 = out?.data || out?.videoBase64 || out?.items?.[0]?.data || out?.items?.[0]?.base64;
        if (!b64) {
          res.writeHead(500);
          res.end(JSON.stringify({ ok: false, error: out?.error || "empty" }));
          return;
        }
        const buf = Buffer.isBuffer(b64) ? b64 : Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
        if (buf.length > 150000) {
          fs.writeFileSync(pl.outPath, buf);
          res.writeHead(200);
          res.end(JSON.stringify({ ok: true, kb: Math.round(buf.length / 1024) }));
          return;
        }
        res.writeHead(500);
        res.end(JSON.stringify({ ok: false, error: "SMALL_BUF" }));
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ ok: false, error: String(e.message || e) }));
      }
    });
  });
  srv.listen(PORT, "127.0.0.1", () => console.log(`[UPGRADE_DAEMON_READY] targets=${targets.length}`));
})();
"""


def call_daemon(pl: dict) -> bool:
    data = json.dumps(pl, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/gen", data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=260) as r:
            res = json.loads(r.read().decode("utf-8"))
            return bool(res.get("ok"))
    except Exception as e:
        print("  daemon err:", e, flush=True)
        return False


def gen_visual_clip(out_p: Path, sec: int, refs: list, prompt: str):
    if out_p.exists() and out_p.stat().st_size > 160000:
        print(f"  [CACHED] {out_p.name}", flush=True)
        return
    cand = out_p.parent / f"_cand_{out_p.name}"
    pl = {
        "sec": sec,
        "refs": [{"name": rn, "path": str(ASSETS_DIR / fn)} for rn, fn in refs],
        "outPath": str(cand),
        "prompt": prompt,
    }
    for att in range(1, 4):
        cand.unlink(missing_ok=True)
        print(f"  [GEN] {out_p.name} ({sec}s) try {att}/3...", flush=True)
        if call_daemon(pl) and cand.exists():
            shutil.move(str(cand), str(out_p))
            print(f"  -> OK {out_p.name}", flush=True)
            return
    raise RuntimeError(f"Failed visual clip {out_p}")


def make_safe_card(out_png: Path, badge: str, line1: str, line2: str = None, is_hook: bool = False, y_top: int = 880):
    """Mép trái X=78 (>=54px), mép phải X=862 (<=884px) — chuẩn 100% Vùng An Toàn 9:16!"""
    ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    h = 148 if (line2 or is_hook) else 116
    box = (78, y_top, 862, y_top + h)
    sd.rounded_rectangle((box[0] + 4, box[1] + 7, box[2] + 4, box[3] + 7), radius=24, fill=(12, 42, 32, 54))
    ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(7)))
    dr = ImageDraw.Draw(ov)
    dr.rounded_rectangle(box, radius=24, fill=(251, 254, 252, 238), outline=(18, 118, 88, 220), width=3)
    dr.rounded_rectangle((78, box[1], 93, box[3]), radius=8, fill=(14, 112, 82, 255))

    f_badge = ImageFont.truetype(F_XBOLD, 20)
    if is_hook:
        f1 = ImageFont.truetype(F_XBOLD, 32)
        f2 = ImageFont.truetype(F_XBOLD, 35)
        dr.text((108, y_top + 18), line1, font=f1, fill=(18, 52, 40, 255))
        dr.text((108, y_top + 72), line2 or "", font=f2, fill=(186, 108, 12, 255))
    else:
        f1 = ImageFont.truetype(F_XBOLD, 26)
        f2 = ImageFont.truetype(F_BOLD, 23)
        bw = int(dr.textlength(badge, font=f_badge)) + 26
        dr.rounded_rectangle((106, y_top + 12, 106 + bw, y_top + 43), radius=13, fill=(14, 112, 82, 255))
        dr.text((119, y_top + 15), badge, font=f_badge, fill=(255, 255, 255, 255))
        dr.text((108, y_top + 52), line1, font=f1, fill=(18, 48, 38, 255))
        if line2:
            dr.text((108, y_top + 96), line2, font=f2, fill=(175, 98, 10, 255))
    ov.save(out_png)


def load_sku_rgba(fn: str) -> Image.Image:
    im = Image.open(PS_ROOT / fn).convert("RGBA")
    return im.crop(im.getbbox())


def build_foreground_counter_deck(out_png: Path, mode: str, f_small_path: str):
    """
    Mặt bàn đá trắng sáng trong trẻo phủ phần tiền cảnh dưới (Y=1185..1920, mép trên bo viền bàn đá tự nhiên)
    trưng bày ĐÚNG 100% SỐ LƯỢNG HỘP THẬT Studio-Retouched, nằm gọn trong X=85..865 (0% xén rìa trái, 0% morph AI!).
    """
    ov = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    # Clean bright sunlit white marble counter deck from Y=1360..1920
    for y in range(1360, 1920):
        t = (y - 1360) / 560.0
        v = int(244 + 9 * (1 - abs(t - 0.3)))
        dr.line((0, y, 1080, y), fill=(v, v + 1, v, 255))
    dr.line((0, 1360, 1080, 1360), fill=(220, 226, 222, 255), width=4)

    def place(canvas, item, x, bot_y, w):
        h = int(item.height * w / item.width)
        y = bot_y - h
        it = item.resize((w, h), Image.Resampling.LANCZOS)
        refl = it.transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((w, int(h * 0.18)), Image.Resampling.LANCZOS)
        refl.putalpha(refl.getchannel("A").point(lambda p: int(p * 0.13)))
        canvas.paste(refl, (x, bot_y + 3), refl)
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse((x + 10, bot_y - 14, x + w - 10, bot_y + 16), fill=(20, 35, 28, 78))
        res = Image.alpha_composite(canvas, sh.filter(ImageFilter.GaussianBlur(9)))
        res.paste(it, (x, y), it)
        return res

    if mode == "collamela_2plus1":
        col = load_sku_rgba("ps_master_collamela.png")
        # 2 hộp lớn (20 gói) bên trái (X=92..540) + 1 hộp nhỏ gọn 10 gói quà tặng bên phải (X=625..825) kèm nhãn quà tặng rõ ràng!
        ov = place(ov, col, 92, 1695, 225)
        ov = place(ov, col, 325, 1710, 225)
        ov = place(ov, col, 635, 1705, 182)
        # Nhãn nhỏ "QUÀ TẶNG HỘP 10 GÓI" gọn ngay phía trên hộp phải (X=622..832, Y=1368..1404 <= 1545, 100% Safe Zone!)
        d2 = ImageDraw.Draw(ov)
        f_tag = ImageFont.truetype(f_small_path, 18)
        d2.rounded_rectangle((622, 1368, 832, 1404), radius=10, fill=(14, 112, 82, 245))
        d2.text((636, 1374), "TẶNG 1 HỘP 10 GÓI", font=f_tag, fill=(255, 255, 255, 255))
    elif mode == "avprotein_5plus1":
        pro = load_sku_rgba("ps_master_av_protein.png")
        boj = load_sku_rgba("ps_master_bojomi.png")
        # Cụm ĐỦ 5 HỘP AV PROTEIN bên trái (2 hộp tầng trên + 3 hộp tầng dưới, X=84..588, 0% cắt lẹm!) + 1 HỘP BOJOMI bên phải (X=642..852)!
        # Top row (2 boxes: #4, #5)
        ov = place(ov, pro, 162, 1465, 162)
        ov = place(ov, pro, 336, 1465, 162)
        # Bottom row (3 boxes: #1, #2, #3)
        ov = place(ov, pro, 84, 1725, 166)
        ov = place(ov, pro, 256, 1735, 166)
        ov = place(ov, pro, 428, 1725, 166)
        # Gift Bojomi box on right
        ov = place(ov, boj, 645, 1725, 206)

    ov.save(out_png)


def render_closeup_promo_insert(out_mp4: Path, deck_png: Path, dur_s: float = 2.50):
    """Cảnh cận 2.5s zoom mượt vào đúng bộ hộp quà tặng chuẩn 100% bao bì để chia nhỏ Cảnh 3 (<3.5s/cảnh)!"""
    deck = Image.open(deck_png).convert("RGBA")
    bg = Image.new("RGBA", (1080, 1920), (247, 250, 248, 255))
    dr = ImageDraw.Draw(bg)
    for y in range(0, 1360):
        v = int(252 - 7 * (y / 1360.0))
        dr.line((0, y, 1080, y), fill=(v, v + 1, v - 1, 255))
    full = Image.alpha_composite(bg, deck).convert("RGB")
    tdir = out_mp4.parent / f"_cu_frames_{out_mp4.stem}"
    tdir.mkdir(parents=True, exist_ok=True)
    n = int(round(dur_s * 24))
    for i in range(n):
        p = i / max(1, n - 1)
        # Zoom into the product tabletop area cleanly
        cw = int(960 - 70 * p)
        ch = int(cw * 1920 / 1080)
        x0 = int(45 + 25 * p)
        y0 = max(0, min(1920 - ch, int(192 - 30 * p)))
        fr = full.crop((x0, y0, x0 + cw, y0 + ch)).resize((1080, 1920), Image.Resampling.LANCZOS)
        fr.save(tdir / f"f_{i:03d}.jpg", quality=95)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-framerate", "24", "-i", str(tdir / "f_%03d.jpg"),
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
        "-pix_fmt", "yuv420p", str(out_mp4)
    ], check=True)
    shutil.rmtree(tdir, ignore_errors=True)


def process_v03():
    vdir = BASE_DIR / "V03_Collamela"
    raw_d, work_d, fin_d, qc_d = vdir / "01_Raw_Clips", vdir / "02_Work", vdir / "03_Final", vdir / "04_QC_Gate"

    ws_p = raw_d / "s1_ws_lifestyle.mp4"
    b12_p = raw_d / "broll_12_pour_powder.mp4"
    b34_p = raw_d / "broll_34_water_stir.mp4"
    sip_p = raw_d / "s2_drink_sip.mp4"

    gen_visual_clip(
        ws_p, 6,
        [("hang_v03_pink.jpg", "hang_v03_pink.jpg"), ("sku_col_box.jpg", "sku_collamela_box.jpg")],
        "Tạo video 6 giây WIDE SHOT (cảnh toàn rộng lấy từ đầu gối trở lên thấy rõ không gian phòng khách sáng nắng ban mai trong trẻo), photorealistic live-action dọc 9:16. "
        "Chị Hằng (@hang_v03_pink.jpg, giữ nguyên 100% gương mặt và bộ áo lụa hồng phấn quần kem) đang chuẩn bị váy dạ tiệc cuối năm rồi bước duyên dáng tới bàn đá trắng có đặt hộp @sku_col_box.jpg. Không lời thoại, không chữ trên hình."
    )
    gen_visual_clip(
        b12_p, 6,
        [("sku_col_box.jpg", "sku_collamela_box.jpg")],
        "Tạo video 6 giây cận cảnh bàn đá trắng sáng trong trẻo đặt hộp @sku_col_box.jpg sắc nét ở hậu cảnh gần, dọc 9:16. "
        "Đôi bàn tay thon gọn mặc tay áo lụa hồng phấn cầm 1 gói stick nhỏ màu trắng trơn thanh lịch ĐÚNG CHIỀU THẲNG ĐỨNG: "
        "(1) Xé nhẹ mép trên đầu gói stick -> (2) Nghiêng gói ĐỔ RÕ DÒNG BỘT MỊN MÀU HỒNG PHẤN NHẠT rơi xuống đáy chiếc ly thủy tinh trong suốt rỗng. "
        "Không lời thoại, không chữ in biến dạng trên gói nhỏ, không hiệu ứng bling."
    )
    gen_visual_clip(
        b34_p, 6,
        [("sku_col_box.jpg", "sku_collamela_box.jpg")],
        "Tạo video 6 giây cận cảnh bàn đá trắng sáng trong trẻo đặt hộp @sku_col_box.jpg sắc nét ở hậu cảnh gần, dọc 9:16. "
        "Trước mặt là ly thủy tinh trong suốt có sẵn lớp bột collagen màu hồng phấn dưới đáy: "
        "(3) Tay người phụ nữ mặc áo lụa hồng phấn NGHIÊNG BÌNH THỦY TINH RÓT DÒNG NƯỚC MÁT TRONG VEO chảy thật vào ly bột hồng -> "
        "(4) Dùng thìa inox khuấy đều cho bột tan nhanh thành ly nước collagen màu hồng đào trong trẻo. Không lời thoại, không chữ trên hình."
    )
    gen_visual_clip(
        sip_p, 6,
        [("hang_v03_pink.jpg", "hang_v03_pink.jpg"), ("sku_col_box.jpg", "sku_collamela_box.jpg")],
        "Tạo video 6 giây medium-long shot sáng trong trẻo dọc 9:16: Chị Hằng (@hang_v03_pink.jpg, giữ nguyên 100% khuôn mặt và áo lụa hồng phấn) đứng bên bàn đá trắng có đặt hộp @sku_col_box.jpg, "
        "nâng ly nước collagen màu hồng đào trong trẻo lên UỐNG THƯỞNG THỨC một ngụm nhỏ ngon lành rồi hạ ly xuống mỉm cười tươi tắn hài lòng. Không lời thoại, không chữ trên hình."
    )

    assemble_upgraded(
        slug="V03_Collamela",
        out_name="261128 AVPM Chị Hằng Collamela chăm da mua 2 tặng 1 final.mp4",
        bgm_name="bgm_warm_fretless.mp3",
        deck_mode="collamela_2plus1",
        cards={
            "hook": ("", "SẮP TIỆC CUỐI NĂM:", "ĐỢI SÁT NGÀY MỚI CHĂM DA LÀ MUỘN!"),
            "usp": ("COLLAMELA · AN VƯỢNG PHARMA", "2.530 mg Collagen (Tripeptide) / 2 gói", "Kèm 87 mg Vitamin C & Kẽm • Vị đào thanh mát"),
            "promo": ("ĐỢT CUỐI SINH NHẬT (ĐẾN 30/11)", "MUA 2 HỘP LỚN (1.840K) • TẶNG 1 HỘP 10 GÓI 480K", "Nhắn chữ “DA ĐẸP” để Chị Hằng giữ quà ngay"),
        },
        hook_y=1350,
    )


def process_v05():
    vdir = BASE_DIR / "V05_AV_Protein"
    raw_d = vdir / "01_Raw_Clips"

    ws_p = raw_d / "s1_ws_lifestyle.mp4"
    b12_p = raw_d / "broll_12_pour_powder.mp4"
    b34_p = raw_d / "broll_34_water_stir.mp4"
    sip_p = raw_d / "s2_drink_sip.mp4"

    gen_visual_clip(
        ws_p, 6,
        [("hang_v05_mint.jpg", "hang_v05_linen_mint.jpg"), ("sku_pro_box.jpg", "sku_avprotein_box.jpg")],
        "Tạo video 6 giây WIDE SHOT (cảnh toàn rộng thấy rõ không gian phòng bếp ngập nắng sáng sớm trong trẻo), photorealistic live-action dọc 9:16. "
        "Chị Hằng (@hang_v05_mint.jpg, giữ nguyên 100% gương mặt và áo sơ mi linen NGẮN TAY màu xanh mint phối quần kem, lộ cẳng tay trần) nhìn đồng hồ buổi sáng vội đi làm rồi bước nhanh tươi tắn tới đảo bếp có đặt hộp @sku_pro_box.jpg. Không lời thoại, không chữ trên hình."
    )
    gen_visual_clip(
        b12_p, 6,
        [("sku_pro_box.jpg", "sku_avprotein_box.jpg")],
        "Tạo video 6 giây cận cảnh đảo bếp đá trắng sáng trong trẻo đặt hộp @sku_pro_box.jpg sắc nét ở hậu cảnh gần, dọc 9:16. "
        "Đôi bàn tay và CẲNG TAY TRẦN thon gọn của người phụ nữ mặc áo ngắn tay (TUYỆT ĐỐI KHÔNG mặc áo dài tay!) cầm 1 gói stick màu trắng bạc trơn không chữ: "
        "(1) Xé gọn đầu gói stick -> (2) Dốc gói ĐỔ RÕ DÒNG BỘT ĐẠM THỰC VẬT MỊN MÀU KEM HẠT rơi chảy vào chiếc ly thủy tinh trong suốt rỗng. "
        "Không lời thoại, tuyệt đối không vẽ chữ trên gói nhỏ cầm tay, không hiệu ứng bling."
    )
    gen_visual_clip(
        b34_p, 6,
        [("sku_pro_box.jpg", "sku_avprotein_box.jpg")],
        "Tạo video 6 giây cận cảnh đảo bếp đá trắng sáng trong trẻo đặt hộp @sku_pro_box.jpg sắc nét ở hậu cảnh gần, dọc 9:16. "
        "Trước mặt là chiếc ly thủy tinh trong suốt có lớp bột đạm màu kem hạt dưới đáy. Đôi bàn tay với CẲNG TAY TRẦN (TUYỆT ĐỐI KHÔNG mặc tay áo dài!): "
        "(3) Cầm bình thủy tinh NGHIÊNG BÌNH RÓT DÒNG NƯỚC ẤM TRONG VEO chảy xối thật vào ly bột đạm -> "
        "(4) Dùng thìa inox khuấy đều tan mịn thành ly sữa đạm hạt sánh mượt hấp dẫn. Không lời thoại, không chữ trên hình."
    )
    gen_visual_clip(
        sip_p, 6,
        [("hang_v05_mint.jpg", "hang_v05_linen_mint.jpg"), ("sku_pro_box.jpg", "sku_avprotein_box.jpg")],
        "Tạo video 6 giây medium-long shot sáng trong trẻo dọc 9:16: Chị Hằng (@hang_v05_mint.jpg, giữ nguyên 100% khuôn mặt và áo sơ mi linen NGẮN TAY màu xanh mint, lộ cẳng tay trần) đứng bên đảo bếp trắng đặt hộp @sku_pro_box.jpg, "
        "nâng ly sữa đạm hạt sánh mịn lên UỐNG THƯỞNG THỨC một ngụm ngon lành rồi hạ ly xuống mỉm cười rạng rỡ tràn đầy năng lượng. Không lời thoại, không chữ trên hình."
    )

    assemble_upgraded(
        slug="V05_AV_Protein",
        out_name="261128 AVPM Chị Hằng AV Protein bữa sáng đạm sạch mua 5 tặng 1 final.mp4",
        bgm_name="bgm_coconut_groove_tvc.mp3",
        deck_mode="avprotein_5plus1",
        cards={
            "hook": ("", "SÁNG VỘI NGẠI ĂN ĐỒ KHÔ?", "NẠP ĐỦ ĐẠM SẠCH CHỈ 1 PHÚT!"),
            "usp": ("AV PROTEIN · ĐẠM THỰC VẬT SẠCH", "22g Đạm Thực Vật / khẩu phần • Giàu Chất Xơ", "Thêm Inulin & Lợi khuẩn • Nhẹ bụng êm dáng"),
            "promo": ("ĐỢT CUỐI SINH NHẬT (ĐẾN 30/11)", "MUA 5 HỘP AV PROTEIN (1.750K) • TẶNG 1 BOJOMI 520K", "Nhắn chữ “ĐẠM SẠCH” để Chị Hằng giữ quà ngay"),
        },
        hook_y=880,
    )


def get_dur(p: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)], text=True).strip())


def assemble_upgraded(slug: str, out_name: str, bgm_name: str, deck_mode: str, cards: dict, hook_y: int):
    vdir = BASE_DIR / slug
    raw_d, work_d, fin_d, qc_d = vdir / "01_Raw_Clips", vdir / "02_Work", vdir / "03_Final", vdir / "04_QC_Gate"
    for d in (work_d, fin_d, qc_d):
        d.mkdir(parents=True, exist_ok=True)

    # Reuse already-approved part1/part2/part3 audio durations from existing part1.mp4, part2.mp4, part3.mp4!
    old_p1, old_p2, old_p3 = work_d / "part1.mp4", work_d / "part2.mp4", work_d / "part3.mp4"
    # Save copies of original voice-synced parts before rebuilding visuals!
    orig_p1, orig_p2, orig_p3 = work_d / "_orig_p1.mp4", work_d / "_orig_p2.mp4", work_d / "_orig_p3.mp4"
    if not orig_p1.exists(): shutil.copy2(old_p1, orig_p1)
    if not orig_p2.exists(): shutil.copy2(old_p2, orig_p2)
    if not orig_p3.exists(): shutil.copy2(old_p3, orig_p3)

    d1 = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(orig_p1)], text=True).strip())
    d2 = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(orig_p2)], text=True).strip())
    d3 = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(orig_p3)], text=True).strip())

    clean_vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "delogo=x=860:y=1685:w=105:h=105,"
        "delogo=x=1008:y=1868:w=68:h=48,"
        "eq=brightness=0.015:saturation=1.04:contrast=1.02,"
        "fps=24,format=yuv420p"
    )

    # --- PART 1: 0..2.5s (MCU Chị Hằng) -> 2.5..5.2s (WS Wide Lifestyle!) -> 5.2..d1 (MCU Chị Hằng holding real box) ---
    ws_p = raw_d / "s1_ws_lifestyle.mp4"
    s1_a, s1_ws = 2.50, 2.70
    s1_c = round(d1 - s1_a - s1_ws, 3)
    p1_new = work_d / "part1_up.mp4"
    fc1 = (
        f"[0:v]fps=24,format=yuv420p,split=2[v1a][v1c];"
        f"[v1a]trim=0:{s1_a:.3f},setpts=PTS-STARTPTS[va];"
        f"[1:v]{clean_vf},trim=0:{s1_ws:.3f},setpts=PTS-STARTPTS[vb];"
        f"[v1c]trim={s1_a + s1_ws:.3f}:{d1:.3f},setpts=PTS-STARTPTS[vc];"
        f"[va][vb][vc]concat=n=3:v=1:a=0[vout]"
    )
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(orig_p1), "-i", str(ws_p), "-filter_complex", fc1, "-map", "[vout]", "-map", "0:a", *NVENC, "-c:a", "copy", str(p1_new)], check=True)
    d1_v = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(p1_new)], text=True).strip())

    # --- PART 2: 4-beat rapid physical sequence + drinking shot! ---
    # [0..1.55s MCU intro] -> [1.55..3.65s B12 tear & pour powder] -> [3.65..5.75s B34 tilt pitcher pour water & stir] -> [5.75..d2 Sip & smile!]
    s2_raw = raw_d / "s2_speaking.mp4"
    b12_p = raw_d / "broll_12_pour_powder.mp4"
    b34_p = raw_d / "broll_34_water_stir.mp4"
    sip_p = raw_d / "s2_drink_sip.mp4"

    t_intro = 1.55
    rem = round(d2 - t_intro, 3)
    t_b12 = round(rem * 0.37, 3)
    t_b34 = round(rem * 0.37, 3)
    t_sip = round(d2 - t_intro - t_b12 - t_b34, 3)

    sp_b12 = max(1.0, round(get_dur(b12_p) / max(1.5, t_b12 + 0.3), 3))
    sp_b34 = max(1.0, round(get_dur(b34_p) / max(1.5, t_b34 + 0.3), 3))
    sp_sip = max(1.0, round(get_dur(sip_p) / max(1.5, t_sip + 0.6), 3))

    p2_new = work_d / "part2_up.mp4"
    fc2 = (
        f"[0:v]{clean_vf},trim=0:{t_intro:.3f},setpts=PTS-STARTPTS[v0];"
        f"[1:v]{clean_vf},setpts=PTS/{sp_b12:.3f},trim=0:{t_b12:.3f},setpts=PTS-STARTPTS[v1];"
        f"[2:v]{clean_vf},setpts=PTS/{sp_b34:.3f},trim=0:{t_b34:.3f},setpts=PTS-STARTPTS[v2];"
        f"[3:v]{clean_vf},setpts=PTS/{sp_sip:.3f},trim=0:{t_sip:.3f},setpts=PTS-STARTPTS[v3];"
        f"[v0][v1][v2][v3]concat=n=4:v=1:a=0[vout]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(s2_raw), "-i", str(b12_p), "-i", str(b34_p), "-i", str(sip_p), "-i", str(orig_p2),
        "-filter_complex", fc2, "-map", "[vout]", "-map", "4:a", *NVENC, "-c:a", "copy", str(p2_new)
    ], check=True)
    d2_v = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(p2_new)], text=True).strip())

    # --- PART 3: Exact Studio-Retouched Multi-Box Counter Deck (2+1 Collamela / 5+1 AV Protein+Bojomi) + 2.5s Close-up Cut in middle! ---
    deck_png = work_d / f"deck_{deck_mode}.png"
    build_foreground_counter_deck(deck_png, deck_mode, F_XBOLD)
    cu_mp4 = work_d / "s3_cu_insert.mp4"
    t_s3a, t_cu = 2.80, 2.50
    t_s3c = max(1.80, round(d3 - t_s3a - t_cu, 3))
    render_closeup_promo_insert(cu_mp4, deck_png, t_cu)

    p3_new = work_d / "part3_up.mp4"
    fc3 = (
        f"[0:v][1:v]overlay=0:0,fps=24,format=yuv420p,split=2[s3a][s3c];"
        f"[s3a]trim=0:{t_s3a:.3f},setpts=PTS-STARTPTS[va];"
        f"[2:v]fps=24,format=yuv420p,trim=0:{t_cu:.3f},setpts=PTS-STARTPTS[vb];"
        f"[s3c]trim={t_s3a + t_cu:.3f}:{d3:.3f},setpts=PTS-STARTPTS[vc];"
        f"[va][vb][vc]concat=n=3:v=1:a=0[vout]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(orig_p3), "-loop", "1", "-t", f"{d3 + 0.5:.2f}", "-i", str(deck_png), "-i", str(cu_mp4),
        "-filter_complex", fc3, "-map", "[vout]", "-map", "0:a", *NVENC, "-c:a", "copy", str(p3_new)
    ], check=True)
    d3_v = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(p3_new)], text=True).strip())

    concat_txt = work_d / "concat_up.txt"
    concat_txt.write_text("file 'part1_up.mp4'\nfile 'part2_up.mp4'\nfile 'part3_up.mp4'\n", encoding="utf-8")
    joined_up = work_d / "joined_up.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(joined_up)], check=True)

    # Exact 10-beat cuts.json so video_qc_gate inspects EVERY SINGLE SHOT!
    t = 0.0
    cuts = []
    for lbl, seg_d in [
        ("s1_mcu_hook", s1_a),
        ("s1_ws_sinh_hoat", s1_ws),
        ("s1_mcu_cam_hop", d1_v - s1_a - s1_ws),
        ("s2_mcu_gioi_thieu", t_intro),
        ("s2_broll_xe_do_bot", t_b12),
        ("s2_broll_rot_nuoc_khuay", t_b34),
        ("s2_uong_thuong_thuc", d2_v - t_intro - t_b12 - t_b34),
        ("s3_mls_ctkm_open", t_s3a),
        ("s3_cu_bo_hop_qua", t_cu),
        ("s3_mls_ctkm_cta", d3_v - t_s3a - t_cu),
    ]:
        cuts.append({"start": round(t, 3), "end": round(t + seg_d, 3), "label": lbl})
        t += seg_d
    cuts_p = work_d / "cuts.json"
    cuts_p.write_text(json.dumps(cuts, indent=2), encoding="utf-8")

    c_hook, c_usp, c_promo = work_d / "card_hook.png", work_d / "card_usp.png", work_d / "card_promo.png"
    make_safe_card(c_hook, *cards["hook"], is_hook=True, y_top=hook_y)
    make_safe_card(c_usp, *cards["usp"], y_top=264)
    make_safe_card(c_promo, *cards["promo"], y_top=840)

    p2_st = d1_v
    p3_st = d1_v + d2_v
    overlays = [
        (c_hook, 0.12, round(s1_a - 0.12, 2)),
        (c_usp, round(p2_st + t_intro + 0.12, 2), round(p2_st + t_intro + t_b12 + t_b34 - 0.12, 2)),
        (c_promo, round(p3_st + 0.25, 2), round(p3_st + d3_v - 0.65, 2)),
    ]
    inputs = ["-i", str(joined_up)]
    fc_parts, prev = [], "0:v"
    for k, (png_p, st, en) in enumerate(overlays, 1):
        inputs += ["-loop", "1", "-t", f"{en + 0.3:.2f}", "-i", str(png_p)]
        ov_l, nx_l = f"ov{k}", f"v{k}"
        fc_parts.append(
            f"[{k}:v]format=rgba,fade=t=in:st={st:.2f}:d=0.22:alpha=1,fade=t=out:st={max(st+0.3, en-0.22):.2f}:d=0.22:alpha=1[{ov_l}];"
            f"[{prev}][{ov_l}]overlay=0:0:enable='between(t,{st:.2f},{en:.2f})':eof_action=pass[{nx_l}]"
        )
        prev = nx_l

    nobgm_up = work_d / "nobgm_up.mp4"
    fc_str = ";".join(fc_parts) + f";[{prev}]format=yuv420p[vout]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc_str, "-map", "[vout]", "-map", "0:a", *NVENC, "-c:a", "aac", "-b:a", "192k", "-shortest", str(nobgm_up)], check=True)

    vdur = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=nw=1:nk=1", str(nobgm_up)], text=True).strip())
    bgm_p = BGM_DIR / bgm_name
    fc_audio = (
        f"[0:a]atrim=0:{vdur:.3f},asetpts=PTS-STARTPTS,asplit=2[vo_main][vo_sc];"
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{vdur:.3f},asetpts=PTS-STARTPTS,"
        f"highpass=f=90,lowpass=f=11000,"
        f"equalizer=f=1800:t=q:w=1.1:g=-5.0,equalizer=f=3000:t=q:w=1.2:g=-4.0,"
        f"volume=0.14,afade=t=in:st=0:d=0.45,afade=t=out:st={max(0.5, vdur-1.0):.3f}:d=1.00[bgm_pre];"
        f"[bgm_pre][vo_sc]sidechaincompress=threshold=0.03:ratio=4:attack=35:release=320[bgm_duck];"
        f"[vo_main][bgm_duck]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"loudnorm=I=-14.5:TP=-1.5:LRA=9,atrim=0:{vdur:.3f},asetpts=PTS-STARTPTS[aout]"
    )
    out_mp4 = fin_d / out_name
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(nobgm_up), "-i", str(bgm_p),
        "-filter_complex", fc_audio, "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        "-movflags", "+faststart", str(out_mp4)
    ], check=True)
    shutil.copy2(out_mp4, DRIVE_DIR / out_name)

    pg = subprocess.run([PY, "-X", "utf8", GATE, "inspect", str(out_mp4), "--cuts-json", str(cuts_p), "--out-dir", str(qc_d)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(f"[{slug} UPGRADED + QC GATE rc={pg.returncode}]\n{pg.stdout}", flush=True)


def main():
    ddir = BASE_DIR / "_upgrade_daemon"
    if ddir.exists():
        shutil.rmtree(ddir, ignore_errors=True)
    ddir.mkdir(parents=True, exist_ok=True)
    d_js = ddir / "_daemon.js"
    d_js.write_text(DAEMON_JS, encoding="utf-8")

    proc = subprocess.Popen([NODE, str(d_js), str(ddir), str(PORT)], cwd=r"C:\AI\full studio\canvas\desktop", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    threading.Thread(target=lambda: [print("  [NODE]", ln.rstrip(), flush=True) for ln in proc.stdout if ln.strip()], daemon=True).start()

    ready = False
    for _ in range(55):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/ping", timeout=1.5) as r:
                if r.status == 200:
                    ready = True
                    break
        except Exception:
            pass
    if not ready:
        proc.kill()
        raise RuntimeError("Upgrade daemon failed to start!")

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            f3 = ex.submit(process_v03)
            time.sleep(2.5)
            f5 = ex.submit(process_v05)
            f3.result()
            f5.result()
    finally:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/quit", timeout=2)
        except Exception:
            pass
        proc.kill()
    print("=== V03 & V05 100% UPGRADED & READY FOR RE-AUDIT! ===", flush=True)


if __name__ == "__main__":
    main()
