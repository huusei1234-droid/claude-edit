/**
 * Infinite Canvas model request script (capability: "text"):
 * Kết nối trực tiếp Nút Văn Bản / Kịch Bản / Hỏi Ảnh trên Canvas vào tài khoản ChatGPT Plus (0 tốn phí API):
 * - chatgpt-plus-thinking : Chế độ Suy luận (Thinking) tự động nhận diện ngữ cảnh dự án
 * - chatgpt-k4-flow       : Vào thẳng Dự án K4 Phim Chuyện Trong Nhà (Asset Board + CHỐT KHÔNG GIAN + Prompt Flow)
 * - chatgpt-htpm-brand    : Vào thẳng Dự án HTPM / An Vượng / Feel Chicken (chuẩn thương hiệu & Sources)
 * - chatgpt-deep-research : Kích hoạt Deep Research nghiên cứu chuyên sâu đa nguồn trên web
 */
async function chatgptPlusText({ messages, params, model, reasoningEffort, onDelta }) {
  const p = params || {};
  const modelId = String(model || "chatgpt-plus-thinking").replace(/^chatgpt::/i, "");
  const reqId = "gpt_txt_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 7);

  const chatgpt = window.desktop && window.desktop.chatgpt;
  if (chatgpt && typeof chatgpt.ask === "function") {
    let unsub = null;
    if (typeof chatgpt.onStreamDelta === "function" && typeof onDelta === "function") {
      unsub = chatgpt.onStreamDelta((payload) => {
        if (payload && payload.requestId === reqId && typeof payload.text === "string") {
          onDelta(payload.text);
        }
      });
    }
    try {
      const res = await chatgpt.ask({
        requestId: reqId,
        model: modelId,
        messages: messages || [],
        project: p.project || "auto",
        mode: p.mode || "auto",
        reasoningEffort: reasoningEffort || "auto",
        keepChat: Boolean(p.keepChat),
      });
      if (!res || !res.ok) {
        throw new Error((res && res.error) || "ChatGPT Plus không phản hồi.");
      }
      if (typeof onDelta === "function" && res.text) {
        onDelta(res.text);
      }
      return res.text || "";
    } finally {
      if (typeof unsub === "function") unsub();
    }
  }

  // Dự phòng qua Cổng HTTP cục bộ :18620 (cho phép gọi ngay cả khi mở Canvas trên trình duyệt thường!)
  const r = await fetch("http://127.0.0.1:18620/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: modelId,
      messages: messages || [],
      project: p.project || "auto",
      mode: p.mode || "auto",
      keepChat: Boolean(p.keepChat),
    }),
  });
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || "Lỗi cổng ChatGPT Plus :18620");
  const text = (j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content) || "";
  if (typeof onDelta === "function" && text) onDelta(text);
  return text;
}

return await chatgptPlusText({ messages, params, model, reasoningEffort, onDelta });
