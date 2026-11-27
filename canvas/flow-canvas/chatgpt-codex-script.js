/**
 * Infinite Canvas model request script (capability: "text"):
 * Thực thi trực tiếp OpenAI Codex cục bộ (codex.exe -> gpt-6.2-sol / gpt-6.2-astra) bằng gói ChatGPT Plus:
 * - Chạy ngầm 100% không mở bất kỳ tab trình duyệt nào, tốc độ phản hồi ~2-5 giây, không đụng chuột.
 * - Hỗ trợ đính kèm Ảnh tham chiếu từ Canvas (-i) và mức độ Suy luận (low / medium / high / xhigh).
 * - Model `codex-gpt-6.2-sol`       : Suy luận / Viết kịch bản / Phân tích ảnh (read-only an toàn).
 * - Model `codex-agent-workspace`   : Agent toàn quyền đọc/ghi mã nguồn & tệp trong C:\AI\full studio (workspace-write).
 */
async function chatgptCodexLocal({ messages, params, model, reasoningEffort, onDelta }) {
  const p = params || {};
  const rawModel = String(model || "codex-gpt-6.2-sol").replace(/^chatgpt::/i, "");
  const isWorkspaceAgent = /workspace|agent-write/i.test(rawModel);
  const codexModel = /reserve/i.test(rawModel)
    ? "gpt-reserve"
    : /astra/i.test(rawModel)
      ? "gpt-6.2-astra"
      : "gpt-6.2-sol";
  const reqId = "codex_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 7);

  const payload = {
    requestId: reqId,
    model: codexModel,
    messages: messages || [],
    reasoningEffort: reasoningEffort || p.reasoningEffort || "medium",
    sandbox: isWorkspaceAgent ? "workspace-write" : (p.sandbox || "read-only"),
    project: p.project || "auto",
    outputSchema: p.outputSchema || null,
    cwd: p.cwd || "",
  };

  const chatgpt = window.desktop && window.desktop.chatgpt;
  if (chatgpt && typeof chatgpt.codex === "function") {
    let unsub = null;
    if (typeof chatgpt.onStreamDelta === "function" && typeof onDelta === "function") {
      unsub = chatgpt.onStreamDelta((ev) => {
        if (ev && ev.requestId === reqId && typeof ev.text === "string") {
          onDelta(ev.text);
        }
      });
    }
    try {
      const res = await chatgpt.codex(payload);
      if (!res || !res.ok) {
        throw new Error((res && res.error) || "Codex không phản hồi.");
      }
      const text = res.text || res.stdout || "";
      if (typeof onDelta === "function" && text) onDelta(text);
      return text;
    } finally {
      if (typeof unsub === "function") unsub();
    }
  }

  // Dự phòng qua Cổng HTTP cục bộ :18620
  const r = await fetch("http://127.0.0.1:18620/v1/codex/exec", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const j = await r.json();
  if (!r.ok || !j.ok) throw new Error(j.error || "Lỗi gọi Codex qua cổng :18620");
  const text = j.text || j.stdout || "";
  if (typeof onDelta === "function" && text) onDelta(text);
  return text;
}

return await chatgptCodexLocal({ messages, params, model, reasoningEffort, onDelta });
