/**
 * Tạo 4 DIỆN MẠO ĐẸP RIÊNG BIỆT cho BỘ 4 VIDEO COMBO PHÁT TRIỂN CHIỀU CAO (BOJOMI + AV PROTEIN):
 * - Look H1 (Sporty Polo Navy): Áo polo thể thao trắng viền navy + váy xếp ly xanh navy + đuôi ngựa cao buộc chun trắng + sân thể thao sáng sớm
 * - Look H2 (Ivory Linen + Mint Cardigan): Đầm midi đũi kem cổ vuông + cardigan xanh mint khoác vai + tóc sóng kẹp ngọc trai + phòng ăn sáng gia đình
 * - Look H3 (Butter Yellow Kitchen): Áo dệt kim cổ vuông vàng bơ + quần suông trắng kem + búi nửa đầu + khuyên tròn vàng + quầy bếp đá sáng nắng
 * - Look H4 (Sky Blue Stretch Studio): Áo croptop tay dài xanh thiên thanh + quần tập loe nhẹ trắng kem + tóc tết bím thể thao + studio giãn cơ cửa kính nắng mai
 * 100% Khóa khuôn mặt Bé Mẫu từ 1 file AV_MODEL_MASTER_SHEET.jpg -> ChatGPT HTPM (3 tab song song, tự xóa chat tạm).
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const MODEL_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc";
const OUT_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_4_Video_Combo_Chieu_Cao\\01_ChatGPT_Assets";
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
  "Keep the EXACT SAME young Vietnamese woman (25-27 years old) from the attached reference photo av_model_master.jpg with 100% identical facial features, expressive dark-brown eyes, soft brows, gentle rosy smile, luminous fair skin, and tall slender graceful posture. ";

const JOBS = [
  {
    id: "HEIGHT_LOOK1_NAVY_POLO_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "HEIGHT_LOOK1_NAVY_POLO_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a FRESH PREMIUM ATHLETIC PREPPY LOOK #1 (CRISP WHITE & CLASSIC NAVY): " +
      "OUTFIT: a sleek fitted crisp-white sleeveless athletic polo collar top with subtle navy collar trim, paired with a flattering high-waisted navy-blue pleated athletic skort, clean white court sneakers with navy stripes, and white athletic socks. " +
      "HAIRSTYLE: glossy chestnut hair tied into a bouncy high wavy ponytail with a chic white satin scrunchie and soft wispy bangs. " +
      "ACCESSORIES: delicate mini pearl stud earrings, a fine dainty silver chain necklace, and a sleek white-strap fitness smartwatch. " +
      "SETTING & COMPOSITION: Vertical 9:16 three-quarter editorial lifestyle-sport portrait beside a bright sunlit outdoor park court bathed in golden morning sunshine with lush green trees and blue sky softly blurred behind. She stands tall with poised athletic posture and warm radiant smile toward camera. " +
      "85mm f/2.0 luxury commercial photography, crisp realistic skin, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
  {
    id: "HEIGHT_LOOK2_LINEN_MINT_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "HEIGHT_LOOK2_LINEN_MINT_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a REFINED MODERN FAMILY WELLNESS LOOK #2 (IVORY LINEN & SOFT MINT): " +
      "OUTFIT: an elegant tailored ivory-cream square-neck A-line linen midi dress with a soft pastel-mint lightweight knit cardigan draped gracefully over her shoulders. " +
      "HAIRSTYLE: glossy chestnut hair styled in soft loose flowing waves tucked neatly behind one ear with a delicate pearl hairpin. " +
      "ACCESSORIES: delicate teardrop pearl earrings, a dainty 18K gold minimal necklace, and a slim cream leather wristwatch. " +
      "SETTING & COMPOSITION: Vertical 9:16 three-quarter lifestyle portrait standing warmly in a bright airy sunlit modern family dining room with light-oak table, fresh flowers, sheer white curtains, and soft golden morning sunlight pouring through tall windows. She smiles warmly and confidently toward camera with poised nurturing elegance. " +
      "85mm f/2.0 luxury editorial photography, crisp natural skin, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
  {
    id: "HEIGHT_LOOK3_BUTTER_KITCHEN_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "HEIGHT_LOOK3_BUTTER_KITCHEN_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a CHIC BRIGHT MORNING KITCHEN LOOK #3 (BUTTER YELLOW & CRISP IVORY): " +
      "OUTFIT: a flattering pastel butter-yellow short-sleeve fine-ribbed square-neck knit top neatly tucked into high-waisted crisp-ivory wide-leg tailored trousers. " +
      "HAIRSTYLE: glossy chestnut hair styled in an effortless youthful half-up top bun with soft airy curtain bangs and loose waves below. " +
      "ACCESSORIES: delicate small polished gold hoop earrings, a dainty gold leaf-pendant necklace, and a slim minimal gold bangle bracelet. " +
      "SETTING & COMPOSITION: Vertical 9:16 three-quarter portrait standing beside a bright sunlit white-marble modern kitchen island with warm morning sunbeams, lush green indoor plant, and clean glass tumblers softly out of focus. She smiles brightly toward camera looking fresh, knowledgeable, and radiant. " +
      "85mm f/2.0 luxury lifestyle commercial photography, realistic healthy skin, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
  {
    id: "HEIGHT_LOOK4_SKY_STRETCH_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "HEIGHT_LOOK4_SKY_STRETCH_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a SLEEK MODERN STRETCHING STUDIO LOOK #4 (SOFT SKY BLUE & CREAM WHITE): " +
      "OUTFIT: a chic fitted soft sky-blue long-sleeve moisture-wicking athletic croptop paired with flattering high-waisted ivory-cream soft-flare athletic yoga trousers and clean white minimal training sneakers. " +
      "HAIRSTYLE: glossy chestnut hair styled neatly into a youthful sporty braided side-swept ponytail with soft wispy face-framing strands. " +
      "ACCESSORIES: tiny sparkling silver stud earrings, a fine dainty silver star-charm necklace, and a pastel sky-blue strap fitness smartwatch. " +
      "SETTING & COMPOSITION: Vertical 9:16 full-to-three-quarter athletic wellness portrait inside a bright sun-drenched minimalist stretching & fitness studio with floor-to-ceiling windows overlooking sunlit green trees and warm natural oak flooring. She stands tall and graceful smiling radiantly toward camera. " +
      "85mm f/2.0 luxury athleisure editorial photography, crisp natural skin, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
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
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START] ${job.id} (${job.ratio}) ChatGPT HTPM attempt ${attempt}/2...`);
    try {
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
      console.warn(`[WARN] ${job.id} attempt ${attempt}:`, res?.error || Object.keys(res || {}));
    } catch (e) {
      console.warn(`[ERR] ${job.id} attempt ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3000));
  }
  console.log(`[FALLBACK] ${job.id} -> Flow Nano Banana...`);
  try {
    const fres = await handlers["flow:generate-image"](null, {
      prompt: job.prompt,
      model: "Nano Banana Pro",
      aspect: "portrait",
      count: 1,
      images: [REF_MASTER],
    });
    const fbuf = extractBuf(fres);
    if (fbuf && fbuf.length > 30000) {
      fs.writeFileSync(job.outPath, fbuf);
      console.log(`[DONE-FLOW] ${job.id} -> ${fbuf.length} bytes`);
      return { id: job.id, ok: true, provider: "flow" };
    }
  } catch (e) {
    console.error(`[FAIL-FLOW] ${job.id}:`, e?.message || e);
  }
  return { id: job.id, ok: false };
}

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
  const t0 = Date.now();
  const res = await runPool(JOBS, 3);
  const ok = res.filter((r) => r && r.ok).length;
  console.log(`\n=== 4 HEIGHT COMBO LOOKS DONE: ${ok}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(res, null, 2));
  process.exit(ok === JOBS.length ? 0 : 1);
})();
