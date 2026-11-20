// Launcher "full studido": mở Infinite Canvas (Electron) + trình duyệt Brave chính (hiển thị thật 100% trên màn hình).
// - Dùng Win32 EnumWindows trên chính Desktop thật của người dùng:
//   + Nếu cửa sổ Studio đang mở hoặc thu nhỏ dưới Taskbar trên Desktop người dùng -> khôi phục & đưa lên trước mặt!
//   + Nếu tiến trình electron.exe / VoiceStudio.exe / brave.exe bị một tab AI chạy ngầm nhốt trong màn hình ẩn (0 HWND trên Desktop người dùng) -> tự động dọn sạch tiến trình ẩn đó để mở cửa sổ thật ngay lần bấm đầu tiên!
// Build: launcher\build.bat   ->   full studido.exe
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;

static class FullStudio
{
    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    [DllImport("user32.dll")]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    private static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern bool IsIconic(IntPtr hWnd);

    private const int SW_RESTORE = 9;

    static HashSet<int> GetPidsOnCurrentDesktop()
    {
        var pids = new HashSet<int>();
        EnumWindows((hWnd, lParam) =>
        {
            uint pid;
            GetWindowThreadProcessId(hWnd, out pid);
            if (pid != 0) pids.Add((int)pid);
            return true;
        }, IntPtr.Zero);
        return pids;
    }

    static void KillTree(int pid, bool force)
    {
        try
        {
            string args = "/PID " + pid + (force ? " /T /F" : "");
            var p = Process.Start(new ProcessStartInfo("taskkill", args)
            {
                CreateNoWindow = true,
                UseShellExecute = false,
            });
            if (p != null) p.WaitForExit(3000);
        }
        catch { }
    }

    static bool IsPort9333Alive()
    {
        try
        {
            var req = (HttpWebRequest)WebRequest.Create("http://127.0.0.1:9333/json/version");
            req.Timeout = 800;
            req.ReadWriteTimeout = 800;
            using (var resp = (HttpWebResponse)req.GetResponse())
            {
                return resp.StatusCode == HttpStatusCode.OK;
            }
        }
        catch
        {
            return false;
        }
    }

    static void EnsureVisibleMainBrave(HashSet<int> desktopPids)
    {
        string[] braveCandidates = new string[]
        {
            @"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            Path.Combine(Environment.GetEnvironmentVariable("LOCALAPPDATA") ?? "", @"BraveSoftware\Brave-Browser\Application\brave.exe"),
            @"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        };
        string braveExe = null;
        foreach (string c in braveCandidates)
        {
            if (File.Exists(c)) { braveExe = c; break; }
        }
        if (braveExe == null) return;

        // Nếu cổng 9333 đang sống NHƯNG không có bất kỳ tiến trình brave.exe nào có cửa sổ trên Desktop người dùng (tức bị kẹt trong màn hình ẩn của AI), đóng êm để bật lại lên màn hình thật!
        bool anyBraveOnUserDesktop = false;
        foreach (var bp in Process.GetProcessesByName("brave"))
        {
            if (desktopPids.Contains(bp.Id) && bp.MainWindowHandle != IntPtr.Zero)
            {
                anyBraveOnUserDesktop = true;
                break;
            }
        }

        if (IsPort9333Alive() && anyBraveOnUserDesktop) return;

        if (IsPort9333Alive() && !anyBraveOnUserDesktop)
        {
            foreach (var bp in Process.GetProcessesByName("brave"))
            {
                if (!desktopPids.Contains(bp.Id))
                {
                    // Chỉ đóng Brave chính bị kẹt ẩn (không đụng tới headless port 19210 của muse2api: đóng êm không /F sẽ chỉ đóng cửa sổ ẩn của 9333)
                    KillTree(bp.Id, false);
                }
            }
            Thread.Sleep(1200);
        }

        string args = "--remote-debugging-port=9333 --remote-debugging-address=127.0.0.1 --restore-last-session "
            + "--disable-background-timer-throttling --disable-renderer-backgrounding "
            + "--disable-backgrounding-occluded-windows --disable-features=CalculateNativeWinOcclusion "
            + "\"https://chatgpt.com/g/g-p-6afbde0b943481919c6ec31a3b4f8642/project\" \"https://flow.google.com/\"";
        try
        {
            Process.Start(new ProcessStartInfo(braveExe, args)
            {
                UseShellExecute = true,
            });
        }
        catch { }
    }

    [STAThread]
    static int Main()
    {
        string root = AppDomain.CurrentDomain.BaseDirectory;
        string desktop = Path.Combine(root, "canvas", "desktop");
        string electron = Path.Combine(desktop, "node_modules", "electron", "dist", "electron.exe");
        string local = Environment.GetEnvironmentVariable("LOCALAPPDATA") ?? "";
        string voice = Environment.GetEnvironmentVariable("VOICESTUDIO_EXE");
        if (string.IsNullOrEmpty(voice) || !File.Exists(voice))
        {
            string pf = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "VoiceStudio", "VoiceStudio.exe");
            string localVoice = Path.Combine(local, "Programs", "VoiceStudio", "VoiceStudio.exe");
            voice = File.Exists(pf) ? pf : localVoice;
        }

        if (!File.Exists(electron))
        {
            MessageBox.Show("Không tìm thấy Electron của canvas:\n" + electron + "\n\nChạy: npm --prefix canvas/desktop install",
                "full studido", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
        if (!File.Exists(web(root)))
        {
            MessageBox.Show("Canvas chưa được build:\n" + web(root) + "\n\nChạy: npm --prefix canvas/app/web run build",
                "full studido", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }

        HashSet<int> desktopPids = GetPidsOnCurrentDesktop();
        EnsureVisibleMainBrave(desktopPids);

        string fullElectronPath = Path.GetFullPath(electron);
        var hiddenSandboxElectrons = new List<int>();

        foreach (var p in Process.GetProcessesByName("electron"))
        {
            try
            {
                string modPath = p.MainModule != null ? Path.GetFullPath(p.MainModule.FileName) : "";
                if (string.Equals(modPath, fullElectronPath, StringComparison.OrdinalIgnoreCase))
                {
                    // 1. Nếu tiến trình nằm trên Desktop thật của người dùng và có cửa sổ (kể cả đang thu nhỏ dưới Taskbar) -> bật lên trước mặt!
                    if (p.MainWindowHandle != IntPtr.Zero && (IsWindowVisible(p.MainWindowHandle) || IsIconic(p.MainWindowHandle)))
                    {
                        if (IsIconic(p.MainWindowHandle))
                        {
                            ShowWindow(p.MainWindowHandle, SW_RESTORE);
                        }
                        SetForegroundWindow(p.MainWindowHandle);
                        return 0;
                    }
                    // 2. Nếu tiến trình KHÔNG có bất kỳ HWND nào trên Desktop hiện tại (bị kẹt trong màn hình ẩn của AI) -> đưa vào danh sách dọn!
                    if (!desktopPids.Contains(p.Id))
                    {
                        hiddenSandboxElectrons.Add(p.Id);
                    }
                }
            }
            catch { }
        }

        if (hiddenSandboxElectrons.Count > 0)
        {
            foreach (int hidPid in hiddenSandboxElectrons)
            {
                KillTree(hidPid, true);
            }
            Thread.Sleep(600);
        }

        if (File.Exists(voice))
        {
            string voiceProcName = Path.GetFileNameWithoutExtension(voice);
            var vProcs = Process.GetProcessesByName(voiceProcName);
            bool anyVoiceOnDesktop = false;
            foreach (var vp in vProcs)
            {
                if (desktopPids.Contains(vp.Id)) { anyVoiceOnDesktop = true; break; }
            }
            if (vProcs.Length > 0 && !anyVoiceOnDesktop)
            {
                foreach (var vp in vProcs) KillTree(vp.Id, true);
                Thread.Sleep(400);
                vProcs = new Process[0];
            }
            if (vProcs.Length == 0)
            {
                Process.Start(new ProcessStartInfo(voice)
                {
                    WorkingDirectory = Path.GetDirectoryName(voice),
                    UseShellExecute = true,
                });
            }
        }

        Environment.SetEnvironmentVariable("VOICESTUDIO_EXE", voice);
        string curPath = Environment.GetEnvironmentVariable("PATH") ?? "";
        string[] nodeCandidates = new string[]
        {
            Path.Combine(root, ".node22", "node-v22.14.0-win-x64"),
            Path.Combine(root, "BO_KIEN_THUC_TVC_AI_PORTABLE", ".node22", "node-v22.14.0-win-x64"),
            @"D:\antigraviti\.node22\node-v22.14.0-win-x64"
        };
        foreach (string nc in nodeCandidates)
        {
            if (Directory.Exists(nc) && curPath.IndexOf(nc, StringComparison.OrdinalIgnoreCase) < 0)
            {
                curPath = nc + ";" + curPath;
            }
        }
        Environment.SetEnvironmentVariable("PATH", curPath);

        var psi = new ProcessStartInfo(electron, ".")
        {
            WorkingDirectory = desktop,
            UseShellExecute = false,
            CreateNoWindow = false,
        };
        Process.Start(psi);
        return 0;
    }

    static string web(string root) { return Path.Combine(root, "canvas", "app", "web", "dist", "index.html"); }
}
