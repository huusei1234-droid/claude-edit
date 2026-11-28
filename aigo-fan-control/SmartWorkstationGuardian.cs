using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;
using HidSharp;

namespace SmartWorkstationGuardian
{
    static class NativeDisplayAndInput
    {
        [DllImport("user32.dll")]
        public static extern bool SetProcessDPIAware();

        [StructLayout(LayoutKind.Sequential)]
        public struct LASTINPUTINFO
        {
            public uint cbSize;
            public uint dwTime;
        }

        [DllImport("user32.dll")]
        public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);

        [DllImport("kernel32.dll")]
        public static extern uint GetTickCount();

        public static double GetIdleSeconds()
        {
            LASTINPUTINFO lii = new LASTINPUTINFO();
            lii.cbSize = (uint)Marshal.SizeOf(typeof(LASTINPUTINFO));
            if (!GetLastInputInfo(ref lii)) return 0.0;
            uint elapsed = unchecked(GetTickCount() - lii.dwTime);
            return elapsed / 1000.0;
        }

        [DllImport("user32.dll")]
        public static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

        [DllImport("user32.dll")]
        public static extern bool UnregisterHotKey(IntPtr hWnd, int id);

        public const uint MOD_ALT = 0x0001;
        public const uint MOD_CONTROL = 0x0002;
        public const int WM_HOTKEY = 0x0312;

        // DisplayConfig (Win32 CCD API) — exact 72-byte PathInfo & 64-byte ModeInfo structs
        [StructLayout(LayoutKind.Sequential)]
        public struct LUID { public uint LowPart; public int HighPart; }

        [StructLayout(LayoutKind.Sequential)]
        public struct RATIONAL { public uint Numerator; public uint Denominator; }

        [StructLayout(LayoutKind.Sequential)]
        public struct POINTL { public int x; public int y; }

        [StructLayout(LayoutKind.Sequential)]
        public struct DISPLAYCONFIG_PATH_SOURCE_INFO
        {
            public LUID adapterId;
            public uint id;
            public uint modeInfoIdx;
            public uint statusFlags;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct DISPLAYCONFIG_PATH_TARGET_INFO
        {
            public LUID adapterId;
            public uint id;
            public uint modeInfoIdx;
            public uint outputTechnology;
            public uint rotation;
            public uint scaling;
            public RATIONAL refreshRate;
            public uint scanLineOrdering;
            public int targetAvailable;
            public uint statusFlags;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct DISPLAYCONFIG_PATH_INFO
        {
            public DISPLAYCONFIG_PATH_SOURCE_INFO sourceInfo;
            public DISPLAYCONFIG_PATH_TARGET_INFO targetInfo;
            public uint flags;
        }

        // Exact 64-byte mode struct: 4 + 4 + 8 = 16-byte header + 48-byte union
        // For SOURCE mode (infoType == 1): width(4), height(4), pixelFormat(4), position.x(4), position.y(4) + 28 bytes pad = 48 bytes
        [StructLayout(LayoutKind.Explicit, Size = 64)]
        public struct DISPLAYCONFIG_MODE_INFO
        {
            [FieldOffset(0)] public uint infoType;
            [FieldOffset(4)] public uint id;
            [FieldOffset(8)] public LUID adapterId;

            // SourceMode fields when infoType == 1
            [FieldOffset(16)] public uint srcWidth;
            [FieldOffset(20)] public uint srcHeight;
            [FieldOffset(24)] public uint srcPixelFormat;
            [FieldOffset(28)] public int srcPosX;
            [FieldOffset(32)] public int srcPosY;
        }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        public struct DISPLAYCONFIG_SOURCE_DEVICE_NAME
        {
            public uint type;
            public uint size;
            public LUID adapterId;
            public uint id;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string viewGdiDeviceName;
        }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        public struct DISPLAYCONFIG_TARGET_DEVICE_NAME
        {
            public uint type;
            public uint size;
            public LUID adapterId;
            public uint id;
            public uint flags;
            public uint outputTechnology;
            public ushort edidManufactureId;
            public ushort edidProductCodeId;
            public uint connectorInstance;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)]
            public string monitorFriendlyDeviceName;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
            public string monitorDevicePath;
        }

        public const uint QDC_ALL_PATHS = 0x00000001;
        public const uint QDC_ONLY_ACTIVE_PATHS = 0x00000002;
        public const uint SDC_USE_SUPPLIED_DISPLAY_CONFIG = 0x00000020;
        public const uint SDC_APPLY = 0x00000080;
        public const uint SDC_SAVE_TO_DATABASE = 0x00000200;
        public const uint SDC_ALLOW_CHANGES = 0x00000400;

        [DllImport("user32.dll")]
        public static extern int GetDisplayConfigBufferSizes(uint flags, out uint numPath, out uint numMode);

        [DllImport("user32.dll")]
        public static extern int QueryDisplayConfig(uint flags, ref uint numPath, [Out] DISPLAYCONFIG_PATH_INFO[] paths, ref uint numMode, [Out] DISPLAYCONFIG_MODE_INFO[] modes, IntPtr currentTopologyId);

        [DllImport("user32.dll")]
        public static extern int SetDisplayConfig(uint numPath, [In] DISPLAYCONFIG_PATH_INFO[] paths, uint numMode, [In] DISPLAYCONFIG_MODE_INFO[] modes, uint flags);

        [DllImport("user32.dll")]
        public static extern int DisplayConfigGetDeviceInfo(ref DISPLAYCONFIG_SOURCE_DEVICE_NAME requestPacket);

        [DllImport("user32.dll")]
        public static extern int DisplayConfigGetDeviceInfo(ref DISPLAYCONFIG_TARGET_DEVICE_NAME requestPacket);

        // DDC/CI VCP 0xD6 Power State probe
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
        public struct PHYSICAL_MONITOR
        {
            public IntPtr hPhysicalMonitor;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
            public string szDesc;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct RECT { public int Left, Top, Right, Bottom; }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
        public struct MONITORINFOEX
        {
            public int cbSize;
            public RECT rcMonitor;
            public RECT rcWork;
            public uint dwFlags;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string szDevice;
        }

        public delegate bool MonEnumProc(IntPtr hMon, IntPtr hdc, ref RECT r, IntPtr data);

        [DllImport("user32.dll")]
        public static extern bool EnumDisplayMonitors(IntPtr hdc, IntPtr clip, MonEnumProc fn, IntPtr data);

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        public static extern bool GetMonitorInfo(IntPtr hMon, ref MONITORINFOEX mi);

        [DllImport("dxva2.dll", SetLastError = true)]
        public static extern bool GetNumberOfPhysicalMonitorsFromHMONITOR(IntPtr hMon, out uint count);

        [DllImport("dxva2.dll", SetLastError = true, CharSet = CharSet.Auto)]
        public static extern bool GetPhysicalMonitorsFromHMONITOR(IntPtr hMon, uint count, [Out] PHYSICAL_MONITOR[] arr);

        [DllImport("dxva2.dll", SetLastError = true)]
        public static extern bool GetVCPFeatureAndVCPFeatureReply(IntPtr hPhys, byte vcpCode, out int vct, out uint curVal, out uint maxVal);

        [DllImport("dxva2.dll", SetLastError = true)]
        public static extern bool DestroyPhysicalMonitors(uint count, [In] PHYSICAL_MONITOR[] arr);

        public static Dictionary<string, bool> ProbeActiveMonitorsPowerOn()
        {
            var result = new Dictionary<string, bool>(StringComparer.OrdinalIgnoreCase);
            EnumDisplayMonitors(IntPtr.Zero, IntPtr.Zero, delegate(IntPtr hMon, IntPtr hdc, ref RECT r, IntPtr d)
            {
                MONITORINFOEX mi = new MONITORINFOEX();
                mi.cbSize = Marshal.SizeOf(typeof(MONITORINFOEX));
                if (!GetMonitorInfo(hMon, ref mi)) return true;

                uint cnt = 0;
                bool isOn = true;
                if (GetNumberOfPhysicalMonitorsFromHMONITOR(hMon, out cnt) && cnt > 0)
                {
                    PHYSICAL_MONITOR[] arr = new PHYSICAL_MONITOR[cnt];
                    if (GetPhysicalMonitorsFromHMONITOR(hMon, cnt, arr))
                    {
                        int vct; uint cur = 0, mx = 0;
                        bool ok = GetVCPFeatureAndVCPFeatureReply(arr[0].hPhysicalMonitor, 0xD6, out vct, out cur, out mx);
                        // VCP 0xD6: 1 = On; 2,3,4,5 = Standby/Suspend/Off; ok == false when monitor power button switched off DDC power
                        isOn = ok && (cur == 1);
                        DestroyPhysicalMonitors(cnt, arr);
                    }
                }
                result[mi.szDevice] = isOn;
                return true;
            }, IntPtr.Zero);
            return result;
        }
    }

    class PolychromeLedController
    {
        private readonly string _stateFile;

        public PolychromeLedController(string stateDir)
        {
            _stateFile = Path.Combine(stateDir, "polychrome_saved_zones.bin");
        }

        public bool SetLedPower(bool turnOn)
        {
            HidStream stream = null;
            try
            {
                HidDevice dev = null;
                foreach (var d in DeviceList.Local.GetHidDevices(0x26CE, 0x01A2))
                {
                    dev = d;
                    break;
                }
                if (dev == null || !dev.TryOpen(out stream)) return false;

                if (!turnOn)
                {
                    byte[] dump = new byte[8 * 6];
                    bool anyLit = false;
                    for (int z = 0; z < 8; z++)
                    {
                        byte[] req = new byte[65];
                        req[0] = 0x00; req[1] = 0x11; req[3] = (byte)z;
                        stream.Write(req, 0, 65);
                        byte[] rb = new byte[65];
                        stream.Read(rb, 0, 65);
                        if (rb[5] != 0x00 && rb[10] != 0x00) anyLit = true;
                        for (int k = 0; k < 6; k++) dump[z * 6 + k] = rb[5 + k];
                    }
                    if (anyLit) File.WriteAllBytes(_stateFile, dump);

                    for (int z = 0; z < 8; z++)
                    {
                        byte[] w = new byte[65];
                        w[0] = 0x00; w[1] = 0x10; w[3] = (byte)z; w[4] = 0x00; w[9] = 0x00;
                        stream.Write(w, 0, 65);
                        byte[] ack = new byte[65];
                        stream.Read(ack, 0, 65);
                    }
                    return true;
                }
                else
                {
                    byte[] dump = null;
                    if (File.Exists(_stateFile))
                    {
                        byte[] raw = File.ReadAllBytes(_stateFile);
                        if (raw.Length == 48) dump = raw;
                    }
                    for (int z = 0; z < 8; z++)
                    {
                        byte[] w = new byte[65];
                        w[0] = 0x00; w[1] = 0x10; w[3] = (byte)z;
                        if (dump != null)
                        {
                            w[4] = dump[z * 6 + 0];
                            w[5] = dump[z * 6 + 1];
                            w[6] = dump[z * 6 + 2];
                            w[7] = dump[z * 6 + 3];
                            w[8] = dump[z * 6 + 4];
                            w[9] = dump[z * 6 + 5];
                        }
                        else
                        {
                            w[4] = 0x0E; w[5] = 0x00; w[6] = 0x00; w[7] = 0xFF; w[8] = 0x80; w[9] = 0xFF;
                        }
                        stream.Write(w, 0, 65);
                        byte[] ack = new byte[65];
                        stream.Read(ack, 0, 65);
                    }
                    return true;
                }
            }
            catch
            {
                return false;
            }
            finally
            {
                if (stream != null) { try { stream.Close(); } catch { } }
            }
        }
    }

    class DisplayTopologyManager
    {
        private readonly string _layoutPath;
        private readonly string _logPath;

        public DisplayTopologyManager(string stateDir, string logPath)
        {
            _layoutPath = Path.Combine(stateDir, "saved_3monitors_ccd.bin");
            _logPath = logPath;
        }

        private void Log(string msg)
        {
            try { File.AppendAllText(_logPath, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " " + msg + Environment.NewLine); } catch { }
        }

        private static byte[] StructArrayToBytes<T>(T[] arr) where T : struct
        {
            int sz = Marshal.SizeOf(typeof(T));
            byte[] buf = new byte[sz * arr.Length];
            IntPtr ptr = Marshal.AllocHGlobal(sz);
            try
            {
                for (int i = 0; i < arr.Length; i++)
                {
                    Marshal.StructureToPtr(arr[i], ptr, false);
                    Marshal.Copy(ptr, buf, i * sz, sz);
                }
            }
            finally { Marshal.FreeHGlobal(ptr); }
            return buf;
        }

        private static T[] BytesToStructArray<T>(byte[] buf, int offset, int count) where T : struct
        {
            int sz = Marshal.SizeOf(typeof(T));
            T[] arr = new T[count];
            IntPtr ptr = Marshal.AllocHGlobal(sz);
            try
            {
                for (int i = 0; i < count; i++)
                {
                    Marshal.Copy(buf, offset + i * sz, ptr, sz);
                    arr[i] = (T)Marshal.PtrToStructure(ptr, typeof(T));
                }
            }
            finally { Marshal.FreeHGlobal(ptr); }
            return arr;
        }

        public int GetActivePathCount(out NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO[] paths, out NativeDisplayAndInput.DISPLAYCONFIG_MODE_INFO[] modes)
        {
            uint np, nm;
            NativeDisplayAndInput.GetDisplayConfigBufferSizes(NativeDisplayAndInput.QDC_ONLY_ACTIVE_PATHS, out np, out nm);
            paths = new NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO[np];
            modes = new NativeDisplayAndInput.DISPLAYCONFIG_MODE_INFO[nm];
            if (NativeDisplayAndInput.QueryDisplayConfig(NativeDisplayAndInput.QDC_ONLY_ACTIVE_PATHS, ref np, paths, ref nm, modes, IntPtr.Zero) != 0)
                return 0;
            Array.Resize(ref paths, (int)np);
            Array.Resize(ref modes, (int)nm);
            return (int)np;
        }

        public int CountAvailableTargetsInAllPaths()
        {
            uint np, nm;
            if (NativeDisplayAndInput.GetDisplayConfigBufferSizes(NativeDisplayAndInput.QDC_ALL_PATHS, out np, out nm) != 0) return 0;
            var paths = new NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO[np];
            var modes = new NativeDisplayAndInput.DISPLAYCONFIG_MODE_INFO[nm];
            if (NativeDisplayAndInput.QueryDisplayConfig(NativeDisplayAndInput.QDC_ALL_PATHS, ref np, paths, ref nm, modes, IntPtr.Zero) != 0) return 0;
            var targets = new HashSet<uint>();
            for (int i = 0; i < np; i++)
            {
                if (paths[i].targetInfo.targetAvailable != 0)
                    targets.Add(paths[i].targetInfo.id);
            }
            return targets.Count;
        }

        public void SaveCurrentMultiMonitorLayoutIf3()
        {
            NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO[] paths;
            NativeDisplayAndInput.DISPLAYCONFIG_MODE_INFO[] modes;
            int cnt = GetActivePathCount(out paths, out modes);
            if (cnt >= 3)
            {
                byte[] pb = StructArrayToBytes(paths);
                byte[] mb = StructArrayToBytes(modes);
                using (var ms = new MemoryStream())
                using (var bw = new BinaryWriter(ms))
                {
                    bw.Write(paths.Length);
                    bw.Write(modes.Length);
                    bw.Write(pb);
                    bw.Write(mb);
                    File.WriteAllBytes(_layoutPath, ms.ToArray());
                }
            }
        }

        public bool CollapseToSingleMonitor(string keepGdiDeviceOrNull)
        {
            SaveCurrentMultiMonitorLayoutIf3();
            NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO[] paths;
            NativeDisplayAndInput.DISPLAYCONFIG_MODE_INFO[] modes;
            int cnt = GetActivePathCount(out paths, out modes);
            if (cnt <= 1) return true;

            int chosenIdx = -1;
            for (int i = 0; i < cnt; i++)
            {
                var sn = new NativeDisplayAndInput.DISPLAYCONFIG_SOURCE_DEVICE_NAME();
                sn.type = 1; sn.size = (uint)Marshal.SizeOf(typeof(NativeDisplayAndInput.DISPLAYCONFIG_SOURCE_DEVICE_NAME));
                sn.adapterId = paths[i].sourceInfo.adapterId; sn.id = paths[i].sourceInfo.id;
                NativeDisplayAndInput.DisplayConfigGetDeviceInfo(ref sn);
                if (!string.IsNullOrEmpty(keepGdiDeviceOrNull) && string.Equals(sn.viewGdiDeviceName, keepGdiDeviceOrNull, StringComparison.OrdinalIgnoreCase))
                {
                    chosenIdx = i;
                    break;
                }
            }
            if (chosenIdx < 0)
            {
                // Fallback: pick srcId == 0 (Monitor 1 in Windows Display Settings) or index 0
                for (int i = 0; i < cnt; i++)
                {
                    if (paths[i].sourceInfo.id == 0) { chosenIdx = i; break; }
                }
                if (chosenIdx < 0) chosenIdx = 0;
            }

            var keepPath = paths[chosenIdx];
            uint srcModeIdx = keepPath.sourceInfo.modeInfoIdx;
            uint tgtModeIdx = keepPath.targetInfo.modeInfoIdx;

            var newModes = new List<NativeDisplayAndInput.DISPLAYCONFIG_MODE_INFO>();
            if (srcModeIdx < modes.Length)
            {
                var sm = modes[srcModeIdx];
                // Make the kept monitor Primary at (0, 0) so all windows & RustDesk snap cleanly onto it!
                sm.srcPosX = 0;
                sm.srcPosY = 0;
                keepPath.sourceInfo.modeInfoIdx = (uint)newModes.Count;
                newModes.Add(sm);
            }
            if (tgtModeIdx < modes.Length)
            {
                var tm = modes[tgtModeIdx];
                keepPath.targetInfo.modeInfoIdx = (uint)newModes.Count;
                newModes.Add(tm);
            }
            keepPath.flags = 1; // DISPLAYCONFIG_PATH_ACTIVE

            var singlePaths = new NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO[] { keepPath };
            var singleModes = newModes.ToArray();
            int rc = NativeDisplayAndInput.SetDisplayConfig(
                1, singlePaths, (uint)singleModes.Length, singleModes,
                NativeDisplayAndInput.SDC_APPLY | NativeDisplayAndInput.SDC_USE_SUPPLIED_DISPLAY_CONFIG | NativeDisplayAndInput.SDC_ALLOW_CHANGES
            );
            Log("CollapseToSingleMonitor(" + (keepGdiDeviceOrNull ?? "Monitor1") + ") -> rc=" + rc);
            return rc == 0;
        }

        public bool RestoreMultiMonitorLayout()
        {
            if (File.Exists(_layoutPath))
            {
                try
                {
                    byte[] raw = File.ReadAllBytes(_layoutPath);
                    int np = BitConverter.ToInt32(raw, 0);
                    int nm = BitConverter.ToInt32(raw, 4);
                    int psz = Marshal.SizeOf(typeof(NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO));
                    var paths = BytesToStructArray<NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO>(raw, 8, np);
                    var modes = BytesToStructArray<NativeDisplayAndInput.DISPLAYCONFIG_MODE_INFO>(raw, 8 + np * psz, nm);
                    int rc = NativeDisplayAndInput.SetDisplayConfig(
                        (uint)np, paths, (uint)nm, modes,
                        NativeDisplayAndInput.SDC_APPLY | NativeDisplayAndInput.SDC_USE_SUPPLIED_DISPLAY_CONFIG | NativeDisplayAndInput.SDC_ALLOW_CHANGES | NativeDisplayAndInput.SDC_SAVE_TO_DATABASE
                    );
                    Log("RestoreMultiMonitorLayout from saved CCD -> rc=" + rc);
                    if (rc == 0)
                    {
                        ReloadLivelyWallpapersAsync();
                        return true;
                    }
                }
                catch (Exception ex)
                {
                    Log("RestoreMultiMonitorLayout err: " + ex.Message);
                }
            }
            // Fallback to DisplaySwitch /extend
            try
            {
                Process.Start(new ProcessStartInfo("DisplaySwitch.exe", "/extend") { CreateNoWindow = true, UseShellExecute = false });
                ReloadLivelyWallpapersAsync();
                return true;
            }
            catch { return false; }
        }

        private void ReloadLivelyWallpapersAsync()
        {
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try
                {
                    Thread.Sleep(2500);
                    string lively = @"C:\Program Files\Lively Wallpaper\Lively.exe";
                    string agy = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"Lively Wallpaper\Library\wallpapers\fresh_muses_4k.agy");
                    if (File.Exists(lively) && Directory.Exists(agy))
                    {
                        for (int m = 1; m <= 3; m++)
                        {
                            Process.Start(new ProcessStartInfo(lively, "setwp --file \"" + agy + "\" --monitor " + m) { CreateNoWindow = true, UseShellExecute = false });
                            Thread.Sleep(700);
                        }
                    }
                }
                catch { }
            });
        }
    }

    class GuardianContext : Form
    {
        private const double IDLE_LED_OFF_SEC = 1800.0;     // 30 minutes -> Turn OFF CPU Fan LED (+ Display)
        private const double IDLE_RUSTDESK_SEC = 3600.0;    // 60 minutes -> Auto-launch RustDesk

        private readonly NotifyIcon _tray;
        private readonly System.Windows.Forms.Timer _timer;
        private readonly PolychromeLedController _led;
        private readonly DisplayTopologyManager _disp;
        private readonly string _logPath;

        private bool _ledTurnedOffByIdle = false;
        private bool _rustDeskLaunchedThisIdle = false;
        private bool _collapsedSingleMonitor = false;
        private int _availableTargetsWhenCollapsed = 0;
        private int _twoMonitorsOffStreak = 0;

        public GuardianContext(string stateDir)
        {
            _logPath = Path.Combine(stateDir, "guardian.log");
            _led = new PolychromeLedController(stateDir);
            _disp = new DisplayTopologyManager(stateDir, _logPath);

            // Save initial 3-monitor layout right away if 3 screens are active
            _disp.SaveCurrentMultiMonitorLayoutIf3();

            // Invisible message-only window setup for global hotkeys
            ShowInTaskbar = false;
            WindowState = FormWindowState.Minimized;
            FormBorderStyle = FormBorderStyle.FixedToolWindow;
            Opacity = 0;

            var menu = new ContextMenuStrip();
            menu.Items.Add("🖥️ Mở lại đủ 3 màn hình (Ctrl+Alt+3)", null, (s, e) => ForceRestore3Monitors());
            menu.Items.Add("📱 Gom về 1 màn hình cho RustDesk (Ctrl+Alt+1)", null, (s, e) => ForceSingleMonitor());
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add("💡 Tắt thử LED tản CPU ngay", null, (s, e) => { _led.SetLedPower(false); _ledTurnedOffByIdle = true; });
            menu.Items.Add("🌈 Bật lại LED tản CPU ngay", null, (s, e) => { _led.SetLedPower(true); _ledTurnedOffByIdle = false; });
            menu.Items.Add("🚀 Bật RustDesk ngay", null, (s, e) => EnsureRustDeskRunning());
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add("Thoát", null, (s, e) => { _tray.Visible = false; Application.Exit(); });

            Icon appIcon = SystemIcons.Shield;
            string icoPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "aigo_fan.ico");
            if (File.Exists(icoPath)) { try { appIcon = new Icon(icoPath); } catch { } }

            _tray = new NotifyIcon
            {
                Icon = appIcon,
                Text = "Hữu Seiz Guardian: 30p Tắt Màn & LED • Tự Gom 1 Màn • 1h Bật RustDesk",
                ContextMenuStrip = menu,
                Visible = true
            };
            _tray.DoubleClick += (s, e) =>
            {
                if (_collapsedSingleMonitor) ForceRestore3Monitors();
                else ForceSingleMonitor();
            };

            _timer = new System.Windows.Forms.Timer { Interval = 3500 };
            _timer.Tick += OnTick;
            _timer.Start();

            Log("Guardian started. Initial 3-mon snapshot checked.");
        }

        protected override void SetVisibleCore(bool value)
        {
            base.SetVisibleCore(false);
            if (!IsHandleCreated) CreateHandle();
        }

        protected override void OnHandleCreated(EventArgs e)
        {
            base.OnHandleCreated(e);
            // Global Hotkeys: Ctrl+Alt+1 -> Single Monitor (RustDesk), Ctrl+Alt+3 -> Restore 3 Monitors
            NativeDisplayAndInput.RegisterHotKey(Handle, 101, NativeDisplayAndInput.MOD_CONTROL | NativeDisplayAndInput.MOD_ALT, (uint)Keys.D1);
            NativeDisplayAndInput.RegisterHotKey(Handle, 103, NativeDisplayAndInput.MOD_CONTROL | NativeDisplayAndInput.MOD_ALT, (uint)Keys.D3);
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            NativeDisplayAndInput.UnregisterHotKey(Handle, 101);
            NativeDisplayAndInput.UnregisterHotKey(Handle, 103);
            base.OnFormClosing(e);
        }

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == NativeDisplayAndInput.WM_HOTKEY)
            {
                int id = m.WParam.ToInt32();
                if (id == 101) ForceSingleMonitor();
                else if (id == 103) ForceRestore3Monitors();
            }
            base.WndProc(ref m);
        }

        private void Log(string msg)
        {
            try { File.AppendAllText(_logPath, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " " + msg + Environment.NewLine); } catch { }
        }

        private void ForceSingleMonitor()
        {
            _collapsedSingleMonitor = true;
            _disp.CollapseToSingleMonitor(null);
            _availableTargetsWhenCollapsed = _disp.CountAvailableTargetsInAllPaths();
        }

        private void ForceRestore3Monitors()
        {
            _collapsedSingleMonitor = false;
            _twoMonitorsOffStreak = 0;
            _disp.RestoreMultiMonitorLayout();
        }

        private void EnsureRustDeskRunning()
        {
            try
            {
                string exe = @"C:\Program Files\RustDesk\rustdesk.exe";
                if (!File.Exists(exe)) return;

                int mySession = Process.GetCurrentProcess().SessionId;
                bool hasVisibleUi = false;
                foreach (var p in Process.GetProcessesByName("rustdesk"))
                {
                    try
                    {
                        if (p.SessionId == mySession && p.MainWindowHandle != IntPtr.Zero)
                        {
                            hasVisibleUi = true;
                            break;
                        }
                    }
                    catch { }
                }

                if (!hasVisibleUi)
                {
                    Process.Start(new ProcessStartInfo(exe) { WorkingDirectory = Path.GetDirectoryName(exe), UseShellExecute = true });
                    Log("Auto-launched RustDesk UI in user session " + mySession);
                }
            }
            catch (Exception ex)
            {
                Log("EnsureRustDeskRunning err: " + ex.Message);
            }
        }

        private void OnTick(object sender, EventArgs e)
        {
            double idleSec = NativeDisplayAndInput.GetIdleSeconds();

            // 1. 30-Minute Idle -> Turn OFF CPU Cooler Fan LED; Wake -> Restore LED immediately
            if (idleSec >= IDLE_LED_OFF_SEC)
            {
                if (!_ledTurnedOffByIdle)
                {
                    if (_led.SetLedPower(false))
                    {
                        _ledTurnedOffByIdle = true;
                        Log("Idle >= 30m (" + Math.Round(idleSec) + "s) -> Turned OFF CPU Cooler ARGB LEDs.");
                    }
                }
            }
            else if (_ledTurnedOffByIdle && idleSec < 15.0)
            {
                if (_led.SetLedPower(true))
                {
                    _ledTurnedOffByIdle = false;
                    Log("User activity detected -> Restored CPU Cooler ARGB LEDs.");
                }
            }

            // 2. 60-Minute Idle -> Auto-Start RustDesk so remote access from home is guaranteed ready!
            if (idleSec >= IDLE_RUSTDESK_SEC)
            {
                if (!_rustDeskLaunchedThisIdle)
                {
                    _rustDeskLaunchedThisIdle = true;
                    EnsureRustDeskRunning();
                }
            }
            else if (idleSec < 30.0)
            {
                _rustDeskLaunchedThisIdle = false;
            }

            // 3. Physical Monitor Power Button Detection (Before 30m Windows Display Sleep!)
            // When user presses power buttons to turn OFF Monitors 2 & 3, collapse desktop onto the 1 remaining ON monitor!
            if (idleSec < IDLE_LED_OFF_SEC - 30.0)
            {
                NativeDisplayAndInput.DISPLAYCONFIG_PATH_INFO[] paths;
                NativeDisplayAndInput.DISPLAYCONFIG_MODE_INFO[] modes;
                int activeCount = _disp.GetActivePathCount(out paths, out modes);

                if (!_collapsedSingleMonitor && activeCount >= 2)
                {
                    if (activeCount >= 3) _disp.SaveCurrentMultiMonitorLayoutIf3();

                    var powerMap = NativeDisplayAndInput.ProbeActiveMonitorsPowerOn();
                    var onDevices = new List<string>();
                    int offDevices = 0;
                    foreach (var kv in powerMap)
                    {
                        if (kv.Value) onDevices.Add(kv.Key);
                        else offDevices++;
                    }

                    // Also account for monitors that physically disconnected HPD when powered off (activeCount dropped from 3 to 2, and 1 of the remaining 2 is off -> 1 left on!)
                    bool shouldCollapse = (onDevices.Count == 1 && (offDevices >= 1 || activeCount == 2) && (offDevices + (3 - activeCount) >= 2));
                    if (shouldCollapse)
                    {
                        _twoMonitorsOffStreak++;
                        if (_twoMonitorsOffStreak >= 2)
                        {
                            _collapsedSingleMonitor = true;
                            _twoMonitorsOffStreak = 0;
                            string keepGdi = onDevices[0];
                            Log("Detected 2 monitors powered OFF via physical button! Collapsing desktop onto single ON monitor: " + keepGdi);
                            _disp.CollapseToSingleMonitor(keepGdi);
                            _availableTargetsWhenCollapsed = _disp.CountAvailableTargetsInAllPaths();
                        }
                    }
                    else
                    {
                        _twoMonitorsOffStreak = 0;
                    }
                }
                else if (_collapsedSingleMonitor)
                {
                    // Auto-restore if user physically powers back ON a DisplayPort monitor (available target count increases!)
                    int curAvail = _disp.CountAvailableTargetsInAllPaths();
                    if (_availableTargetsWhenCollapsed > 0 && curAvail > _availableTargetsWhenCollapsed)
                    {
                        Log("Detected monitor powered back ON (targets " + _availableTargetsWhenCollapsed + " -> " + curAvail + "). Restoring 3 monitors!");
                        ForceRestore3Monitors();
                    }
                    else if (activeCount >= 3)
                    {
                        _collapsedSingleMonitor = false;
                    }
                }
            }
        }
    }

    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            NativeDisplayAndInput.SetProcessDPIAware();
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string stateDir = Path.Combine(baseDir, "guardian_state");
            Directory.CreateDirectory(stateDir);

            if (args.Length > 0)
            {
                var led = new PolychromeLedController(stateDir);
                var disp = new DisplayTopologyManager(stateDir, Path.Combine(stateDir, "guardian.log"));
                string cmd = args[0].ToLowerInvariant();
                if (cmd == "--dump-state")
                {
                    disp.SaveCurrentMultiMonitorLayoutIf3();
                    var pmap = NativeDisplayAndInput.ProbeActiveMonitorsPowerOn();
                    Console.WriteLine("IdleSec=" + NativeDisplayAndInput.GetIdleSeconds());
                    Console.WriteLine("Saved3MonExists=" + File.Exists(Path.Combine(stateDir, "saved_3monitors_ccd.bin")));
                    foreach (var kv in pmap) Console.WriteLine("Monitor " + kv.Key + " PowerOn=" + kv.Value);
                    return;
                }
                if (cmd == "--single") { disp.CollapseToSingleMonitor(null); return; }
                if (cmd == "--multi") { disp.RestoreMultiMonitorLayout(); return; }
                if (cmd == "--led-off") { led.SetLedPower(false); return; }
                if (cmd == "--led-on") { led.SetLedPower(true); return; }
            }

            bool createdNew;
            using (Mutex mutex = new Mutex(true, "Global\\HuuSeiz_SmartWorkstationGuardian_Singleton", out createdNew))
            {
                if (!createdNew) return;
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(new GuardianContext(stateDir));
            }
        }
    }
}
