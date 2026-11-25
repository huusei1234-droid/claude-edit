import ctypes
import os
import subprocess
import threading
import time
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

HERE = os.path.dirname(os.path.abspath(__file__))
CARD_HTML_PATH = os.path.join(HERE, "card.html")
APP_URI = "ui://explorer/card.html"
ALLOWED_PREFIXES = ("C:\\", "D:\\", "E:\\", "F:\\", "G:\\", "Z:\\")

mcp = FastMCP("open-folder")


def _reveal_windows_explorer(raw_path: str) -> tuple[bool, str]:
    if not raw_path:
        return False, "Missing path"
    p = os.path.normpath(raw_path.strip().strip('"'))
    if not any(p.upper().startswith(pref) for pref in ALLOWED_PREFIXES):
        return False, f"Disallowed drive: {p}"
    is_virtual_drive = p.upper().startswith(("Z:\\", "G:\\"))
    has_ext = bool(os.path.splitext(p)[1])
    if not is_virtual_drive and not os.path.exists(p):
        parent = os.path.dirname(p)
        if parent and os.path.isdir(parent):
            p = parent
            has_ext = False
        else:
            return False, f"Path not found: {p}"

    def _spawn():
        try:
            user32 = ctypes.windll.user32
            user32.keybd_event(0, 0, 0, 0)
        except Exception:
            pass
        is_file_target = os.path.isfile(p) or (is_virtual_drive and has_ext and not os.path.isdir(p))
        if is_file_target:
            subprocess.Popen(["explorer.exe", f"/select,{p}"])
            folder_name = os.path.basename(os.path.dirname(p))
        else:
            subprocess.Popen(["explorer.exe", p])
            folder_name = os.path.basename(p) or p

        for _ in range(14):
            time.sleep(0.10)
            try:
                user32 = ctypes.windll.user32
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
                found = []

                def enum_cb(hwnd, _):
                    if user32.IsWindowVisible(hwnd):
                        cls_buf = ctypes.create_unicode_buffer(64)
                        user32.GetClassNameW(hwnd, cls_buf, 64)
                        if cls_buf.value in ("CabinetWClass", "ExploreWClass"):
                            ln = user32.GetWindowTextLengthW(hwnd)
                            tbuf = ctypes.create_unicode_buffer(ln + 2)
                            user32.GetWindowTextW(hwnd, tbuf, ln + 2)
                            if not folder_name or folder_name.lower() in tbuf.value.lower():
                                found.append(hwnd)
                    return True

                user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
                if found:
                    hwnd = found[0]
                    user32.ShowWindow(hwnd, 9)
                    user32.keybd_event(0, 0, 0, 0)
                    user32.SetForegroundWindow(hwnd)
                    break
            except Exception:
                pass

    threading.Thread(target=_spawn, daemon=True).start()
    return True, p


@mcp.resource(
    APP_URI,
    name="Open File Location Card",
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"prefersBorder": False}},
)
def card_html() -> str:
    with open(CARD_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


@mcp.tool(
    name="show_file_location_card",
    title="Mở vị trí tệp",
    description="Render an inline 1-click button card in the conversation that opens Windows File Explorer directly selecting the exported file (zero web browser).",
    meta={"ui": {"resourceUri": APP_URI, "visibility": ["model", "app"]}},
)
def show_file_location_card(file_path: str, cloud_path: str = "", label: str = "") -> CallToolResult:
    norm_file = os.path.normpath(file_path.strip().strip('"')) if file_path else ""
    norm_cloud = os.path.normpath(cloud_path.strip().strip('"')) if cloud_path else ""
    fname = os.path.basename(norm_file) if norm_file else "Video Final"
    folder = os.path.dirname(norm_file) if norm_file else ""
    payload = {
        "filePath": norm_file,
        "cloudPath": norm_cloud,
        "fileName": fname,
        "folderPath": folder,
        "label": label,
    }
    return CallToolResult(
        content=[TextContent(type="text", text=f"Đã hiển thị thẻ nút 1 chạm Mở vị trí tệp cho {norm_file}")],
        structuredContent=payload,
    )


@mcp.tool(
    name="reveal_in_explorer",
    title="Mở thư mục chứa tệp trong Windows Explorer",
    description="Open Windows File Explorer directly highlighting the specified file or folder.",
    meta={"ui": {"visibility": ["model", "app"]}},
)
def reveal_in_explorer(path: str) -> CallToolResult:
    ok, msg = _reveal_windows_explorer(path)
    return CallToolResult(
        content=[TextContent(type="text", text=msg)],
        structuredContent={"ok": ok, "target": msg},
        isError=not ok,
    )


if __name__ == "__main__":
    mcp.run()
