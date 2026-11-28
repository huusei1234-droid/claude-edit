// Direct Brave CDP (:9333) Streaming Engine (ChatGPT HTPM -> Fast JPEG -> Patched Google Flow Omni 1.2 Flash)
// Powers ALL remaining 8 Day-25 AI USP Videos (V01, V02, V03, V05, V06, V07, V08, V10 + V09 solo endcard)!
const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const BATCH_ROOT = "d:\\AI\\full studio\\output\\htpm-ngay-261125";
const SPEC_JSON = path.join(BATCH_ROOT, "day25_v4_usp_jobs.json");

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
  return { mime, base64: fs.readFileSync(fp).toString("base64"), name: "v4d_" + path.basename(fp) };
}

function pngToFastJpg(pngPath, jpgPath) {
  execFileSync("ffmpeg", ["-y", "-v", "error", "-i", pngPath, "-vf", "scale='min(1080,iw)':-2", "-q:v", "3", jpgPath], { stdio: "inherit" });
}

function transcodeNvenc(rawMp4, dstMp4, minDurS) {
  fs.mkdirSync(path.dirname(dstMp4), { recursive: true });
  let rawDur = minDurS;
  try {
    const pr = JSON.parse(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "json", rawMp4], { encoding: "utf8" }));
    rawDur = parseFloat(pr.format.duration) || minDurS;
  } catch {}
  const stretch = Math.max(1.0, Number(((minDurS + 0.55) / Math.max(1.0, rawDur)).toFixed(4)));
  const vf = `setpts=${stretch}*PTS,fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p`;
  execFileSync("ffmpeg", ["-y", "-v", "error", "-i", rawMp4, "-vf", vf, "-r", "24", "-fps_mode", "cfr", "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-g", "24", dstMp4], { stdio: "inherit" });
}

(async () => {
  const allScenes = JSON.parse(fs.readFileSync(SPEC_JSON, "utf8")).scenes;
  const todo = allScenes.filter((s) => !(fs.existsSync(s.dst_mp4) && fs.statSync(s.dst_mp4).size > 250000));
  console.log(`[Day25:V4DirectEngine] Todo = ${todo.length}/${allScenes.length} AI USP Scenes...`);

  // Step A: Generate any missing Reference Images on ChatGPT HTPM (2 parallel workers)
  const imgTodo = todo.filter((s) => !(fs.existsSync(s.ref_jpg) && fs.statSync(s.ref_jpg).size > 40000));
  if (imgTodo.length > 0) {
    console.log(`[Phase A] Generating ${imgTodo.length} AI USP Reference Images on ChatGPT HTPM...`);
    let iIdx = 0;
    async function imgWorker(wId) {
      if (wId > 0) await sleep(wId * 3000);
      while (iIdx < imgTodo.length) {
        const cur = iIdx++;
        const sc = imgTodo[cur];
        fs.mkdirSync(path.dirname(sc.ref_png), { recursive: true });
        if (!(fs.existsSync(sc.ref_png) && fs.statSync(sc.ref_png).size > 200000)) {
          const refs = (sc.refs || []).map(fileToImgObj);
          let res = null;
          for (let att = 1; att <= 3; att++) {
            res = await handlers["chatgpt:generate-image"](null, {
              prompt: sc.image_prompt,
              model: "chatgpt-image",
              ratio: "9:16",
              quality: "auto",
              count: 1,
              images: refs,
              keepChat: false,
              noFallback: true,
            });
            if (res && res.ok && res.data && res.data.length > 200000) break;
            console.warn(`[ImgRetry#${att}] ${sc.scene_id}: ${(res?.error || "empty").slice(0, 140)}`);
            await sleep(8000);
          }
          if (!res || !res.ok || !res.data) throw new Error(`ChatGPT image failed for ${sc.scene_id}: ${res?.error}`);
          fs.writeFileSync(sc.ref_png, Buffer.from(res.data));
        }
        pngToFastJpg(sc.ref_png, sc.ref_jpg);
        console.log(`[ImgOK] (${cur + 1}/${imgTodo.length}) ${sc.scene_id} -> ${Math.round(fs.statSync(sc.ref_jpg).size / 1024)} KB JPG`);
      }
    }
    await Promise.all([imgWorker(0), imgWorker(1)]);
    await chatgpt.sweepIdleChatgptTabs?.().catch(() => {});
  }

  // Step B: Generate Live 9:16 Flow Omni 1.2 Flash Videos from Fast JPEGs (2 parallel workers)
  console.log(`[Phase B] Generating ${todo.length} Live 9:16 AI USP Videos on Google Flow...`);
  let vIdx = 0;
  async function vidWorker(wId) {
    if (wId > 0) await sleep(wId * 4000);
    while (vIdx < todo.length) {
      const cur = vIdx++;
      const sc = todo[cur];
      let res = null;
      const genSec = Math.min(8, Math.max(6, Math.round(sc.shot_dur + 1.0)));
      for (let att = 1; att <= 4; att++) {
        res = await handlers["flow:generate-video"](null, {
          prompt: sc.motion_prompt,
          model: "Omni 1.2 Flash",
          aspect: "portrait",
          resolution: "720p",
          seconds: genSec,
          count: 1,
          mode: "ingredients",
          images: [fileToImgObj(sc.ref_jpg)],
        });
        if (res && res.ok && res.data && res.data.length > 100000) break;
        console.warn(`[VidRetry#${att}] ${sc.scene_id}: ${(res?.error || "empty").slice(0, 160)}`);
        await sleep(8000);
      }
      if (!res || !res.ok || !res.data) throw new Error(`Flow video failed for ${sc.scene_id}: ${res?.error}`);
      fs.mkdirSync(path.dirname(sc.raw_mp4), { recursive: true });
      fs.writeFileSync(sc.raw_mp4, Buffer.from(res.data));
      transcodeNvenc(sc.raw_mp4, sc.dst_mp4, sc.shot_dur);
      console.log(`[VidOK] (${cur + 1}/${todo.length}) ${sc.scene_id} -> ${sc.dst_mp4}`);
    }
  }
  await Promise.all([vidWorker(0), vidWorker(1)]);
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  console.log("=== ALL DAY-25 V4 AI USP VIDEOS GENERATED SUCCESSFULLY ===");
  process.exit(0);
})().catch((e) => {
  console.error("[FATAL]", e && (e.stack || e.message || e));
  process.exit(1);
});
