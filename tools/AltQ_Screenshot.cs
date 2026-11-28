using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;

static class AltQScreenshot {
    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

    [DllImport("user32.dll")]
    private static extern int GetMessage(out MSG lpMsg, IntPtr hWnd, uint wMsgFilterMin, uint wMsgFilterMax);

    [DllImport("shell32.dll", CharSet = CharSet.Unicode)]
    private static extern IntPtr ShellExecute(IntPtr hwnd, string lpOperation, string lpFile, string lpParameters, string lpDirectory, int nShowCmd);

    [StructLayout(LayoutKind.Sequential)]
    private struct MSG {
        public IntPtr hwnd;
        public uint message;
        public IntPtr wParam;
        public IntPtr lParam;
        public uint time;
        public int pt_x;
        public int pt_y;
    }

    private const uint MOD_ALT = 0x0001;
    private const uint MOD_NOREPEAT = 0x4000;
    private const uint VK_Q = 0x51;
    private const uint WM_HOTKEY = 0x0312;

    [STAThread]
    static void Main() {
        bool createdNew;
        using (var mutex = new Mutex(true, @"Local\AltQScreenshotHotkeyDaemon", out createdNew)) {
            if (!createdNew) return;

            bool ok = RegisterHotKey(IntPtr.Zero, 1, MOD_ALT | MOD_NOREPEAT, VK_Q);
            string logPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "AltQ_Screenshot.status.txt");
            try {
                File.WriteAllText(logPath, string.Format("Started={0:o} | RegisterHotKey(Alt+Q)={1} | Err={2}", DateTime.Now, ok, Marshal.GetLastWin32Error()));
            } catch {}

            if (!ok) return;

            MSG msg;
            while (GetMessage(out msg, IntPtr.Zero, 0, 0) > 0) {
                if (msg.message == WM_HOTKEY && (int)msg.wParam == 1) {
                    ShellExecute(IntPtr.Zero, "open", "ms-screenclip:", null, null, 1);
                }
            }
        }
    }
}
