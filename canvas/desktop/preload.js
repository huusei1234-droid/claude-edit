const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("desktop", {
  getDataDir: () => ipcRenderer.invoke("desktop:get-data-dir"),
  chooseDataDir: () => ipcRenderer.invoke("desktop:choose-data-dir"),
  openDataDir: () => ipcRenderer.invoke("desktop:open-data-dir"),
  flow: {
    status: () => ipcRenderer.invoke("flow:status"),
    show: () => ipcRenderer.invoke("flow:show"),
    accounts: () => ipcRenderer.invoke("flow:accounts"),
    switchAccount: (id) => ipcRenderer.invoke("flow:switch-account", id),
    addAccount: () => ipcRenderer.invoke("flow:add-account"),
    removeAccount: (id) => ipcRenderer.invoke("flow:remove-account", id),
    renameAccount: (id, name) => ipcRenderer.invoke("flow:rename-account", id, name),
    openAccount: (id) => ipcRenderer.invoke("flow:open-account", id),
    refreshCredits: () => ipcRenderer.invoke("flow:refresh-credits"),
    setMinCredits: (n) => ipcRenderer.invoke("flow:set-min-credits", n),
    generateVideo: (job) => ipcRenderer.invoke("flow:generate-video", job),
    generateImage: (job) => ipcRenderer.invoke("flow:generate-image", job),
  },
  chatgpt: {
    status: () => ipcRenderer.invoke("chatgpt:status"),
    show: () => ipcRenderer.invoke("chatgpt:show"),
    accounts: () => ipcRenderer.invoke("chatgpt:accounts"),
    switchAccount: (id) => ipcRenderer.invoke("chatgpt:switch-account", id),
    addAccount: () => ipcRenderer.invoke("chatgpt:add-account"),
    removeAccount: (id) => ipcRenderer.invoke("chatgpt:remove-account", id),
    renameAccount: (id, name) => ipcRenderer.invoke("chatgpt:rename-account", id, name),
    openAccount: (id) => ipcRenderer.invoke("chatgpt:open-account", id),
    generateImage: (job) => ipcRenderer.invoke("chatgpt:generate-image", job),
    ask: (job) => ipcRenderer.invoke("chatgpt:ask", job),
    listProjects: () => ipcRenderer.invoke("chatgpt:list-projects"),
    syncProject: (spec) => ipcRenderer.invoke("chatgpt:sync-project", spec),
    scheduleTask: (spec) => ipcRenderer.invoke("chatgpt:schedule-task", spec),
    openHub: (target) => ipcRenderer.invoke("chatgpt:open-hub", target),
    codex: (spec) => ipcRenderer.invoke("chatgpt:codex", spec),
    onStreamDelta: (cb) => {
      if (typeof cb !== "function") return () => {};
      const listener = (_e, payload) => cb(payload);
      ipcRenderer.on("chatgpt:stream-delta", listener);
      return () => ipcRenderer.removeListener("chatgpt:stream-delta", listener);
    },
  },
  sora: {
    status: () => ipcRenderer.invoke("sora:status"),
    show: () => ipcRenderer.invoke("sora:show"),
    generateVideo: (job) => ipcRenderer.invoke("sora:generate-video", job),
  },
  gemini: {
    status: () => ipcRenderer.invoke("gemini:status"),
    show: () => ipcRenderer.invoke("gemini:show"),
    accounts: () => ipcRenderer.invoke("gemini:accounts"),
    refreshAccounts: (opts) => ipcRenderer.invoke("gemini:refresh-accounts", opts),
    generateVideo: (job) => ipcRenderer.invoke("gemini:generate-video", job),
  },
});
