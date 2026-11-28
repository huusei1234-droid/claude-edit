// V5 PIPELINED STREAMING ENGINE (Brave CDP :9333)
// 1. Generates 10 Unique Commercial Poster Plates on ChatGPT HTPM (3 parallel tabs)
// 2. Streams 42 Real-Life Action USP Scenes (ChatGPT HTPM -> Fast JPEG -> Live Queue -> Google Flow Omni 1.2 Flash IN PARALLEL!)
const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const JOBS_JSON = "d:\\AI\\full studio\\output\\htpm-ngay-261125\\10_V5_Action_USP\\v5_jobs.json";

const handlers = {};
const origLoad = Module._load;
Module._load = function (request, parent, isMain) {
  if (request === "electron") {
    return {
      ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
      dialog: { showErrorBox: (t, m) => console.error("[DialogError]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};

const userDataDir = path.join(process.env.APPDATA || "C:\\Users\\Hang thu\\AppData\\Roaming", "infinite-canvas-flow");
const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));
flow.setup({ getPath: () => userDataDir });
chatgpt.setup({ getPath: () => userDataDir });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function fileToImgObj(fp) {
  const ext = path.extname(fp).toLowerCase();
  const mime = ext === ".png" ? "image/png" : "image/jpeg";
  return { mime, base64: fs.readFileSync(fp).toString("base64"), name: "v5_" + path.basename(fp) };
}

function pngToFastJpg(pngPath, jpgPath) {
  fs.mkdirSync(path.dirname(jpgPath), { recursive: true });
  execFileSync("ffmpeg", ["-y", "-v", "error", "-i", pngPath, "-vf", "scale='min(1080,iw)':-2", "-q:v", "3", jpgPath], { stdio: "inherit" });
}

function transcodeActionClipNvenc(rawMp4, cfrMp4) {
  fs.mkdirSync(path.dirname(cfrMp4), { recursive: true });
  // Ensure at least 5.2s smooth 24fps CFR clip for 3.6s-4.4s dynamic cuts
  let rawDur = 6.0;
  try {
    const pr = JSON.parse(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "json", rawMp4], { encoding: "utf8" }));
    rawDur = parseFloat(pr.format.duration) || 6.0;
  } catch {}
  const stretch = Math.max(1.0, Number((5.2 / Math.max(1.0, rawDur)).toFixed(4)));
  const vf = `setpts=${stretch}*PTS,fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p`;
  execFileSync("ffmpeg", [
    "-y", "-v", "error", "-i", rawMp4,
    "-vf", vf, "-r", "24", "-fps_mode", "cfr", "-an",
    "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-g", "24",
    cfrMp4
  ], { stdio: "inherit" });
}

async function genChatgptImg(id, prompt, refPaths, pngPath, jpgPath) {
  if (fs.existsSync(jpgPath) && fs.statSync(jpgPath).size > 40000) {
    return true;
  }
  fs.mkdirSync(path.dirname(pngPath), { recursive: true });
  if (!(fs.existsSync(pngPath) && fs.statSync(pngPath).size > 180000)) {
    const refs = (refPaths || []).map(fileToImgObj);
    let res = null;
    for (let att = 1; att <= 3; att++) {
      res = await handlers["chatgpt:generate-image"](null, {
        prompt,
        model: "chatgpt-image",
        ratio: "9:16",
        quality: "auto",
        count: 1,
        images: refs,
        keepChat: false,
        noFallback: true,
      });
      if (res && res.ok && res.data && res.data.length > 180000) break;
      console.warn(`[ChatGPTRetry#${att}] ${id}: ${(res?.error || "empty").slice(0, 140)}`);
      await sleep(7000);
    }
    if (!res || !res.ok || !res.data) throw new Error(`ChatGPT failed for ${id}: ${res?.error}`);
    fs.writeFileSync(pngPath, Buffer.from(res.data));
  }
  pngToFastJpg(pngPath, jpgPath);
  console.log(`[ImgOK] ${id} -> ${Math.round(fs.statSync(jpgPath).size / 1024)} KB JPG`);
  return true;
}

(async () => {
  const jobs = JSON.parse(fs.readFileSync(JOBS_JSON, "utf8"));

  // STAGE 1: 10 Unique Commercial Poster Plates (3 parallel workers)
  const posterTodo = jobs.poster_plates.filter((p) => !(fs.existsSync(p.jpg_path) && fs.statSync(p.jpg_path).size > 40000));
  if (posterTodo.length > 0) {
    console.log(`[Stage 1] Generating ${posterTodo.length}/10 Unique Poster Plates on ChatGPT HTPM...`);
    let pIdx = 0;
    async function pWorker(w) {
      if (w > 0) await sleep(w * 2500);
      while (pIdx < posterTodo.length) {
        const p = posterTodo[pIdx++];
        await genChatgptImg(p.id, p.prompt, p.refs, p.png_path, p.jpg_path);
      }
    }
    await Promise.all([pWorker(0), pWorker(1), pWorker(2)]);
  }
  console.log("=== [POSTER_PLATES_100_DONE] ===");

  // STAGE 2: PIPELINED STREAMING — ChatGPT (2 workers) feeds Google Flow (2 workers) SIMULTANEOUSLY!
  const actAll = jobs.action_scenes;
  const actNeedVid = actAll.filter((s) => !(fs.existsSync(s.cfr_mp4) && fs.statSync(s.cfr_mp4).size > 200000));
  console.log(`[Stage 2] Pipelined Action Scenes needed: ${actNeedVid.length}/${actAll.length}...`);

  if (actNeedVid.length > 0) {
    const flowReadyQueue = [];
    let imgProducerDone = false;

    // Seed any scenes that ALREADY have ref JPGs directly into flowReadyQueue!
    const needImgGen = [];
    for (const sc of actNeedVid) {
      if (fs.existsSync(sc.jpg_path) && fs.statSync(sc.jpg_path).size > 40000) {
        flowReadyQueue.push(sc);
      } else {
        needImgGen.push(sc);
      }
    }

    let iPtr = 0;
    async function imgProducer(w) {
      if (w > 0) await sleep(w * 3000);
      while (iPtr < needImgGen.length) {
        const sc = needImgGen[iPtr++];
        await genChatgptImg(sc.id, sc.img_p, sc.refs, sc.png_path, sc.jpg_path);
        flowReadyQueue.push(sc);
      }
    }

    let completedVids = 0;
    async function flowConsumer(w) {
      if (w > 0) await sleep(w * 4500);
      while (true) {
        if (flowReadyQueue.length === 0) {
          if (imgProducerDone) break;
          await sleep(1500);
          continue;
        }
        const sc = flowReadyQueue.shift();
        let res = null;
        let curVidPrompt = sc.vid_p;
        for (let att = 1; att <= 4; att++) {
          res = await handlers["flow:generate-video"](null, {
            prompt: curVidPrompt,
            model: "Omni 1.2 Flash",
            aspect: "portrait",
            resolution: "720p",
            seconds: 6,
            count: 1,
            mode: "ingredients",
            images: [fileToImgObj(sc.jpg_path)],
          });
          if (res && res.ok && res.data && res.data.length > 100000) break;
          const errStr = String(res?.error || "empty");
          console.warn(`[FlowRetry#${att}] ${sc.id}: ${errStr.slice(0, 160)}`);
          // If Google Flow policy filter triggered on image/prompt, auto-regenerate a clean modest living-room/walkway image + neutral motion prompt!
          if (/chính sách|policy|violat/i.test(errStr) && att === 1) {
            console.log(`[PolicyAutoHeal] Regenerating ultra-clean modest image & motion prompt for ${sc.id}...`);
            try { fs.unlinkSync(sc.png_path); } catch {}
            try { fs.unlinkSync(sc.jpg_path); } catch {}
            const safeImgPrompt = sc.img_p
              .replace(/bedroom|bathroom|loungewear|camisole|menstrual|cramps|abdomen|stomach|epigastric|bloat|indigestion|heartburn/gi, "sunlit modern living room")
              + " Modest tailored business attire in a bright sunlit living room.";
            await genChatgptImg(sc.id, safeImgPrompt, sc.refs, sc.png_path, sc.jpg_path);
            curVidPrompt = "Smooth cinematic camera movement in a bright sunlit modern home living room: natural graceful everyday motion, calm expression, lips closed, no text.";
          }
          await sleep(7000);
        }
        if (!res || !res.ok || !res.data) throw new Error(`Flow failed for ${sc.id}: ${res?.error}`);
        fs.mkdirSync(path.dirname(sc.raw_mp4), { recursive: true });
        fs.writeFileSync(sc.raw_mp4, Buffer.from(res.data));
        transcodeActionClipNvenc(sc.raw_mp4, sc.cfr_mp4);
        completedVids++;
        console.log(`[VidOK] (${completedVids}/${actNeedVid.length}) ${sc.id} -> CFR24`);
      }
    }

    const prodPromise = Promise.all([imgProducer(0), imgProducer(1)]).then(async () => {
      imgProducerDone = true;
      await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
      console.log("=== [ALL_42_ACTION_REFS_DONE] ===");
    });
    const consPromise = Promise.all([flowConsumer(0), flowConsumer(1)]);
    await Promise.all([prodPromise, consPromise]);
    await flow.sweepIdleFlowTabs?.().catch(() => {});
  }

  console.log("=== [V5_ENGINE_ALL_DONE] ===");
  process.exit(0);
})().catch((e) => {
  console.error("[V5_FATAL]", e && (e.stack || e.message || e));
  process.exit(1);
});
