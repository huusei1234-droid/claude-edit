/**
 * Direct Node.js Benchmark across ALL 3 AI Engines:
 * 1. ChatGPT (Project HTPM on Brave :9333, with product + style + logo reference images, auto-delete chat)
 * 2. Google Flow Nano Banana Pro (on Brave :9333, with product + style + logo reference images)
 * 3. Muse2API (http://127.0.0.1:18610/v1/images/generations)
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "D:\\full studio_data\\infinite-canvas-flow";
fs.mkdirSync(DATA_DIR, { recursive: true });

const handlers = {};
const origLoad = Module._load;
Module._load = function (req, parent, isMain) {
  if (req === "electron") {
    return {
      ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
      dialog: { showErrorBox: (t, m) => console.error("[DIALOG]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));

const mockApp = { getPath: () => DATA_DIR };
flow.setup(mockApp);
chatgpt.setup(mockApp);

function fileToRefObj(filePath, customName) {
  const buf = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const mime = ext === ".png" ? "image/png" : ext === ".webp" ? "image/webp" : "image/jpeg";
  return { base64: buf.toString("base64"), mime, name: customName || path.basename(filePath) };
}

const BENCH_DIR = "d:\\AI\\full studio\\projects\\av_htpm_26_posters_v3\\benchmark_3ai";
fs.mkdirSync(BENCH_DIR, { recursive: true });

const refs = [
  fileToRefObj("C:\\Users\\Hang thu\\.gemini\\antigravity\\brain\\3c47ebbb-8468-44f7-b584-19bc2acdc8cf\\.user_uploaded\\media_1795404719183_a2e19ad8.jpg", "ref_style_av.jpg"),
  fileToRefObj(path.join(BENCH_DIR, "ref_dk_packshot.jpg"), "ref_dk_box.jpg"),
  fileToRefObj(path.join(BENCH_DIR, "ref_ht_logo.jpg"), "ref_ht_logo.jpg"),
];

const PROMPT_REF = `Create a super-clear, luxury commercial pharmaceutical infographic poster (vertical 3:4 aspect ratio) modeled directly on the exact layout clarity, giant typography, vivid scenic background, custom icons, and sculpted stone podium with ingredient decor of ref_style_av.jpg, featuring the exact real product box & open herbal pill bottle from ref_dk_box.jpg and the official brand emblem from ref_ht_logo.jpg.

1. LUSH SCENIC BACKGROUND & PRODUCT SIDE DECOR (CRITICAL — NO FLAT PLAIN BACKGROUND):
Set in a rich, sunlit royal ruby-crimson & traditional herbal garden studio with blooming pink lotus flowers, lush dewy green medicinal leaves framing the left, bottom-left and corners, warm golden sunbeams, and flowing 3D champagne-gold silk ribbons.
On the middle-left, place the EXACT product box "ĐIỀU KINH HT" and open white bottle with herbal pills from ref_dk_box.jpg standing naturally with unified warm studio lighting on a chiseled natural stone slab, surrounded right beside the box by rich natural herbal decor: sliced Đương quy roots, vibrant red Hồng hoa saffron blossoms, green herbal leaves, and scattered dark-brown herbal pills on the stone. Keep every letter and logo on the "ĐIỀU KINH HT" box 100% sharp, faithful, and ungarbled!

2. TOP HEADER & MASSIVE BRANDING:
- Top-left: Official circular red-blue Yin-Yang HT logo from ref_ht_logo.jpg with crisp white-gold text "HẰNG THU PHARMA - Tinh Hoa Thảo Dược Việt".
- Top-right MASSIVE 3D metallic gold headline: "ĐIỀU KINH BỔ TRỨNG"
- Large clear white bold subtitle underneath: "Bồi bổ khí huyết — Điều hòa chu kỳ tự nhiên" and gold line "Nuôi dưỡng nền tảng buồng trứng khỏe từ gốc".
- Highlight pill banner with giant gold "4" and bold white uppercase "NHÓM THẢO DƯỢC QUÝ / TRONG VIÊN HOÀN ĐIỀU KINH HẰNG THU".

3. FOUR COMPACT CREAM BENTO CARDS (01, 02 on middle-right; 03, 04 on bottom-right leaving the stone slab, herbs & leaves visible at bottom-left, ZERO empty space, HUGE vivid 3D illustrations filling 85%+ of each card + warm gold highlight bar behind the bold benefit):
- Card 01: "ĐƯƠNG QUY" | Huge 3D illustration of sliced Angelica root, green leaves & ruby essence drops | Gold highlight "Bổ Huyết Chủ Đạo" | "Hỗ trợ hoạt huyết, nuôi dưỡng tử cung ấm khỏe."
- Card 02: "HƯƠNG PHỤ & SÀI HỒ" | Huge 3D illustration of herbal roots in a wooden mortar & pestle | Gold highlight "Điều Hòa Kinh Kỳ" | "Hỗ trợ hành khí, làm dịu tức bụng ngày đèn đỏ."
- Card 03: "HỒNG HOA & HUYỀN HỒ" | Huge 3D illustration of vibrant red-orange saffron-like Carthamus flowers glowing | Gold highlight "Thông Kinh Hoạt Lạc" | "Hỗ trợ cải thiện kinh thâm đen, vón cục."
- Card 04: "ĐAN SÂM & HUYẾT ĐẰNG" | Huge 3D illustration of red Salvia root slices & luminous pearl-pink healthy follicle orb | Gold highlight "Dưỡng Trứng Khỏe" | "Bồi bổ tuần hoàn khí huyết, đón tin vui."

4. BOTTOM CREAM FOOTER BAR WITH CUTE VECTOR ICONS:
Left herbal shield badge + bold text "Ngày uống 2 lần (sáng & tối), mỗi lần 10–20 viên cùng nước ấm." | Middle 3 clean line icons (herbal bowl + yoga woman + warm water cup) | Right italic text "Thực phẩm bảo vệ sức khỏe, không phải là thuốc và không thay thế thuốc chữa bệnh."`;

async function testChatGPT() {
  const t0 = Date.now();
  console.log("[1. ChatGPT] Starting generation in Project HTPM...");
  const res = await handlers["chatgpt:generate-image"](null, {
    prompt: PROMPT_REF,
    ratio: "3:4",
    count: 1,
    images: refs,
    keepChat: false,
    noFallback: true,
  });
  if (res && res.ok && res.data) {
    const out = path.join(BENCH_DIR, "01_chatgpt_direct.png");
    fs.writeFileSync(out, res.data);
    console.log(`[1. ChatGPT] SUCCESS in ${Math.round((Date.now() - t0) / 1000)}s -> ${out} (${Math.round(res.data.length / 1024)} KB)`);
    return { engine: "chatgpt", ok: true, out };
  }
  console.error("[1. ChatGPT] FAILED:", res?.error);
  return { engine: "chatgpt", ok: false, error: res?.error };
}

async function testFlowPro() {
  const t0 = Date.now();
  console.log("[2. Google Flow Nano Banana Pro] Starting generation...");
  const res = await handlers["flow:generate-image"](null, {
    prompt: `@ref_style_av.jpg @ref_dk_box.jpg @ref_ht_logo.jpg ` + PROMPT_REF,
    model: "Nano Banana Pro",
    ratio: "3:4",
    count: 1,
    images: refs,
  });
  if (res && res.ok && res.data) {
    const out = path.join(BENCH_DIR, "02_flow_nanobanana_pro_direct.png");
    fs.writeFileSync(out, res.data);
    console.log(`[2. Flow Nano Banana Pro] SUCCESS in ${Math.round((Date.now() - t0) / 1000)}s -> ${out} (${Math.round(res.data.length / 1024)} KB)`);
    return { engine: "flow_pro", ok: true, out };
  }
  console.error("[2. Flow Nano Banana Pro] FAILED:", res?.error);
  return { engine: "flow_pro", ok: false, error: res?.error };
}

async function testMuse() {
  const t0 = Date.now();
  console.log("[3. Muse2API :18610] Starting generation...");
  try {
    const keyPath = "d:\\AI\\full studio\\canvas\\muse2api\\data\\api_key";
    const museKey = fs.existsSync(keyPath) ? fs.readFileSync(keyPath, "utf8").trim() : "";
    const r = await fetch("http://127.0.0.1:18610/v1/images/generations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(museKey ? { Authorization: `Bearer ${museKey}` } : {}),
      },
      body: JSON.stringify({
        model: "muse-image",
        prompt: PROMPT_REF.replace(/ref_\w+\.jpg/g, "a white-and-magenta herbal medicine box 'ĐIỀU KINH HT' and open pill bottle"),
        n: 1,
        size: "1024x1792",
        response_format: "b64_json",
      }),
    });
    const txt = await r.text();
    if (!r.ok) {
      console.error(`[3. Muse2API] HTTP ${r.status}: ${txt.slice(0, 240)}`);
      return { engine: "muse", ok: false, error: `HTTP ${r.status}: ${txt.slice(0, 180)}` };
    }
    const j = JSON.parse(txt);
    const b64 = j?.data?.[0]?.b64_json;
    if (b64) {
      const buf = Buffer.from(b64, "base64");
      const out = path.join(BENCH_DIR, "03_muse_direct.png");
      fs.writeFileSync(out, buf);
      console.log(`[3. Muse2API] SUCCESS in ${Math.round((Date.now() - t0) / 1000)}s -> ${out} (${Math.round(buf.length / 1024)} KB)`);
      return { engine: "muse", ok: true, out };
    }
    return { engine: "muse", ok: false, error: "empty b64_json" };
  } catch (e) {
    console.error("[3. Muse2API] ERR:", e.message || e);
    return { engine: "muse", ok: false, error: String(e.message || e) };
  }
}

(async () => {
  const all = await Promise.all([testChatGPT(), testFlowPro(), testMuse()]);
  console.log("ALL 3 BENCHMARKS FINISHED:", JSON.stringify(all, null, 2));
  process.exit(0);
})();
