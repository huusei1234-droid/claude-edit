/**
 * Infinite Canvas model request script (capability: "video"):
 * Tạo video B-Roll / Điện ảnh qua OpenAI Sora (https://sora.chatgpt.com) bằng gói ChatGPT Plus trên Brave (:9333).
 */
async function chatgptSoraVideo({ prompt, images, params }) {
  const p = params || {};
  const rawSeconds = Math.round(Number(p.seconds) || 10);
  const seconds = Math.min(20, Math.max(5, rawSeconds));
  const ratioStr = String(p.ratio || p.size || "16:9");
  const ratio = ["9:16", "3:4", "2:3"].includes(ratioStr) ? "9:16" : ratioStr === "1:1" ? "1:1" : "16:9";

  const cleanPrompt = String(prompt || "")
    .replace(/^Nhãn ảnh tham chiếu:[^\n]*\n+/i, "")
    .replace(/【[^】\n]*】\s*/g, "")
    .replace(/@\[node:[^\]]+\]\s*/g, "")
    .trim();

  const imgs = (images || []).slice(0, 2).map((d, i) => {
    const m = String(d).match(/^data:([^;]+);base64,(.*)$/);
    if (!m) throw new Error("Ảnh tham chiếu không đúng định dạng data URL.");
    return { mime: m[1], base64: m[2], name: `sora_ref_${i + 1}.png` };
  });

  const sora = window.desktop && window.desktop.sora;
  if (sora && typeof sora.generateVideo === "function") {
    const res = await sora.generateVideo({
      prompt: cleanPrompt,
      ratio,
      seconds,
      images: imgs,
    });
    if (!res || !res.ok) throw new Error((res && res.error) || "Sora không tạo được video.");
    return { blob: new Blob([res.data], { type: res.mime || "video/mp4" }) };
  }

  // Dự phòng qua Cổng HTTP cục bộ :18620
  const r = await fetch("http://127.0.0.1:18620/v1/videos/sora", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: cleanPrompt, ratio, seconds, images: imgs }),
  });
  const j = await r.json();
  if (!r.ok || !j.ok) throw new Error(j.error || "Lỗi gọi Sora qua cổng :18620");
  const bin = Uint8Array.from(atob(j.b64_json), (c) => c.charCodeAt(0));
  return { blob: new Blob([bin], { type: j.mime || "video/mp4" }) };
}

return await chatgptSoraVideo({ prompt, images, params });
