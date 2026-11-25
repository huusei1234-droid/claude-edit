/**
 * Tạo 3 DIỆN MẠO HOÀN TOÀN MỚI cho Bé Mẫu USP (đổi toàn bộ: trang phục + kiểu tóc + bông tai + dây chuyền + bối cảnh!)
 * - Look 2 (Bojomi): Đồ công sở kem sữa + tóc búi thấp Hàn Quốc thả mái bay + bông tai ngọc trai giọt nước + dây chuyền vàng mảnh + đồng hồ da nâu (1:1 + 9:16)
 * - Look 3 (Collamela): Đầm lụa hồng phấn đào cổ đổ + tóc xoăn sóng kẹp ngọc trai + bông tai hoa pha lê + dây chuyền giọt pha lê (1:1 + 9:16)
 * - Look 4 (Curcumilk Phyto): Áo cardigan len vàng kem bơ mặc nhà + tóc đuôi ngựa thấp tự nhiên + khuyên tròn vàng mảnh + dây chuyền mặt lá (1:1)
 * Dùng 1 file ảnh neo duy nhất (AV_MODEL_MASTER_SHEET.jpg) để ChatGPT HTPM nhận 100% không lỗi multiple upload (tự xóa chat tạm, fallback Flow Nano Banana).
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const MODEL_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc";
const OUT_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Ngay_01_2411\\01_ChatGPT_Assets";
fs.mkdirSync(OUT_DIR, { recursive: true });

const handlers = {};
const origLoad = Module._load;
Module._load = function (req) {
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
flow.setup({ getPath: () => DATA_DIR });
chatgpt.setup({ getPath: () => DATA_DIR });

const MASTER_BUF = fs.readFileSync(path.join(MODEL_DIR, "AV_MODEL_MASTER_SHEET.jpg"));
const REF_MASTER = { name: "av_model_master.jpg", mime: "image/jpeg", base64: MASTER_BUF.toString("base64") };

const FACE_LOCK =
  "Keep the EXACT SAME young Vietnamese woman (25-27 years old) from the attached reference photo av_model_master.jpg with 100% identical facial features, eyes, eyebrows, nose, gentle rosy smile, luminous fair skin, and slender graceful proportions. ";

const LOOK2_DESC =
  "COMPLETELY REPLACE her pajamas and hairstyle with a refined LUXURY OFFICE CHIC LOOK: " +
  "OUTFIT: a crisp ivory-cream silk V-neck button blouse tucked into tailored warm-beige wide-leg office trousers. " +
  "HAIRSTYLE: an elegant low Korean chignon bun with soft wispy face-framing bangs. " +
  "JEWELRY & ACCESSORIES: delicate teardrop pearl stud earrings, a fine 18K gold dainty pendant necklace with tiny round charm, and a slim brown leather wristwatch. " +
  "PROP: holding a classy warm cream ceramic mug of steaming vanilla cereal milk gently in her hands. ";

const LOOK3_DESC =
  "COMPLETELY REPLACE her pajamas and hairstyle with a radiant LUXURY BEAUTY EVENING LOOK: " +
  "OUTFIT: an elegant blush peach-pink satin silk midi dress with soft cowl neckline and delicate short flutter sleeves. " +
  "HAIRSTYLE: voluminous glossy dark-chestnut loose curls styled half-up with a chic pearl-embellished ivory satin claw clip. " +
  "JEWELRY & ACCESSORIES: sparkling dainty crystal-flower earrings, a delicate silver necklace with tiny crystal teardrop pendant, and a thin delicate ring. " +
  "PROP: holding a sleek stemmed crystal glass filled with translucent rosy-peach collagen beverage near chest level with radiant dewy glowing skin. ";

const LOOK4_DESC =
  "COMPLETELY REPLACE her pajamas and hairstyle with a cozy SUNLIT AFTERNOON WELLNESS LOOK: " +
  "OUTFIT: a soft butter-cream fine-knit lightweight cardigan layered over a crisp white square-neck top paired with relaxed sand-beige linen trousers. " +
  "HAIRSTYLE: an effortless chic low ponytail with soft airy curtain bangs. " +
  "JEWELRY & ACCESSORIES: delicate small polished gold hoop earrings, a dainty gold leaf-charm necklace, and a delicate thin gold bracelet. " +
  "PROP: cradling a clear glass mug of rich warm golden-amber turmeric coconut milk with soft gentle steam. ";

const JOBS = [
  {
    id: "N01_LOOK2_BOJOMI_1x1",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "N01_LOOK2_BOJOMI_1x1.png"),
    prompt:
      FACE_LOCK + LOOK2_DESC +
      "Square 1:1 editorial health campaign portrait. Position her cleanly on the RIGHT HALF of the frame (56%-92% horizontally) standing beside a bright sunlit light-oak and white-marble executive office/home-office desk with fresh white tulips and airy sheer curtains behind. " +
      "Leave the ENTIRE LEFT HALF of the image bright, uncluttered, clean sunlit warm-ivory negative space ready for huge Vietnamese typography and real product box compositing. " +
      "85mm f/2.0 commercial photography, crisp 8K realistic skin, ZERO text, ZERO letters, ZERO logos, ZERO product boxes, ZERO watermarks.",
  },
  {
    id: "N01_LOOK2_BOJOMI_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "N01_LOOK2_BOJOMI_9x16.png"),
    prompt:
      FACE_LOCK + LOOK2_DESC +
      "Vertical 9:16 commercial portrait in a bright sunlit modern luxury office / minimalist bright dining space with sunlit window curtains, white marble desk surface, soft green botanical accent. She stands naturally smiling warmly toward camera while holding her warm ceramic mug of vanilla cereal milk. " +
      "Leave clean airy bright negative space in the upper third for bold vertical video typography. 85mm f/2.0 commercial photography, ZERO text, ZERO logos, ZERO product boxes, ZERO watermarks.",
  },
  {
    id: "N01_LOOK3_COLLAMELA_1x1",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "N01_LOOK3_COLLAMELA_1x1.png"),
    prompt:
      FACE_LOCK + LOOK3_DESC +
      "Square 1:1 luxury skincare & beauty editorial portrait. Position her cleanly on the RIGHT HALF of the frame (56%-92% horizontally) beside a sunlit pearl-white marble vanity table with soft blush-peach afternoon bokeh light and delicate pink peony flowers softly blurred behind. " +
      "Leave the ENTIRE LEFT HALF of the frame bright, luminous, clean pearl-peach ivory negative space ready for giant Vietnamese typography and real product box compositing. " +
      "85mm f/2.0 luxury beauty photography, radiant glass-skin glow, ZERO text, ZERO letters, ZERO logos, ZERO product boxes, ZERO watermarks.",
  },
  {
    id: "N01_LOOK3_COLLAMELA_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "N01_LOOK3_COLLAMELA_9x16.png"),
    prompt:
      FACE_LOCK + LOOK3_DESC +
      "Vertical 9:16 luxury beauty commercial portrait in a luminous pearl-white and warm blush-gold vanity room with soft glowing bokeh lamps and fresh pale-pink flowers in background. She smiles warmly toward camera holding her crystal glass of translucent peach collagen drink. " +
      "Leave airy bright negative space in the upper third for bold vertical video typography. 85mm f/2.0 beauty commercial photography, ZERO text, ZERO logos, ZERO boxes, ZERO watermarks.",
  },
  {
    id: "N01_LOOK4_CURCUMILK_1x1",
    ratio: "1:1",
    outPath: path.join(OUT_DIR, "N01_LOOK4_CURCUMILK_1x1.png"),
    prompt:
      FACE_LOCK + LOOK4_DESC +
      "Square 1:1 warm editorial lifestyle nutrition portrait. Position her cleanly on the RIGHT HALF of the frame (56%-92% horizontally) beside a sunlit warm-cream marble kitchen counter bathed in golden honey afternoon sunbeams with subtle green herbs and airy sheer curtains behind. " +
      "Leave the ENTIRE LEFT HALF of the image luminous warm-ivory sunlit negative space completely uncluttered for giant Vietnamese typography and real product box compositing. " +
      "85mm f/2.0 commercial photography, cozy healthy golden-hour warmth, ZERO text, ZERO letters, ZERO logos, ZERO boxes, ZERO watermarks.",
  },
];

function extractBuf(res) {
  const b64 = res?.data || res?.items?.[0]?.data || res?.items?.[0]?.base64 || res?.images?.[0]?.base64 || res?.base64;
  if (!b64) return null;
  if (Buffer.isBuffer(b64)) return b64;
  if (b64 instanceof Uint8Array) return Buffer.from(b64);
  if (Array.isArray(b64)) return Buffer.from(b64);
  return Buffer.from(String(b64).replace(/^data:image\/\w+;base64,/, ""), "base64");
}

async function runOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 100000) {
    console.log(`[SKIP] ${job.id} cached`);
    return { id: job.id, ok: true, provider: "cached" };
  }
  console.log(`[START] ${job.id} (${job.ratio}) via ChatGPT HTPM (1 ref)...`);
  const res = await handlers["chatgpt:generate-image"](null, {
    prompt: job.prompt,
    ratio: job.ratio,
    count: 1,
    images: [REF_MASTER],
    keepChat: false,
  });
  const buf = extractBuf(res);
  if (buf && buf.length > 30000) {
    fs.writeFileSync(job.outPath, buf);
    console.log(`[DONE] ${job.id} (${res.provider || "chatgpt"}) -> ${buf.length} bytes`);
    return { id: job.id, ok: true, provider: res.provider || "chatgpt" };
  }
  console.error(`[FAIL] ${job.id}:`, res?.error || Object.keys(res || {}));
  return { id: job.id, ok: false, error: res?.error || "no buffer" };
}

// Run 3 parallel workers (ChatGPT HTPM supports up to 3 parallel tabs cleanly)
async function runPool(items, concurrency) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 2500));
    while (idx < items.length) {
      const i = idx++;
      out[i] = await runOne(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => w(k)));
  return out;
}

(async () => {
  const results = await runPool(JOBS, 3);
  console.log("=== 3 NEW LOOKS RESULTS ===", JSON.stringify(results));
  process.exit(results.every((r) => r && r.ok) ? 0 : 1);
})();
