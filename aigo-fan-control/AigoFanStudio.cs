using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;
using Gigabyte.EnvironmentControl.CoolingDevice.Fan;
using Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan;
using Gigabyte.EnvironmentControl.Common.CoolingDevice.Fan.CoordinateSystem;
using Gigabyte.EnvironmentControl.Common.HardwareMonitor;

namespace AigoFanStudio
{
    static class Program
    {
        public static readonly string GbtDir = @"C:\Program Files (x86)\GIGABYTE\EasyTuneEngineService";

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        static extern bool SetDllDirectory(string lpPathName);

        [STAThread]
        static void Main(string[] args)
        {
            bool createdNew;
            using (Mutex mutex = new Mutex(true, "Global\\HuuSeiz_AigoFanStudio_SingleInstance", out createdNew))
            {
                if (!createdNew)
                {
                    MessageBox.Show("Aigo Fan Studio đang chạy sẵn dưới khay hệ thống (góc phải dưới màn hình)!", "Aigo Fan Studio", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }

                if (Directory.Exists(GbtDir))
                {
                    SetDllDirectory(GbtDir);
                    Environment.SetEnvironmentVariable("PATH", GbtDir + ";" + Environment.GetEnvironmentVariable("PATH"));
                }

                AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
                {
                    string name = new AssemblyName(e.Name).Name + ".dll";
                    string candidate = Path.Combine(GbtDir, name);
                    if (File.Exists(candidate)) return Assembly.LoadFrom(candidate);
                    return null;
                };

                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);

                bool startMin = false;
                foreach (string a in args)
                {
                    if (a.Equals("--minimized", StringComparison.OrdinalIgnoreCase) || a.Equals("-m", StringComparison.OrdinalIgnoreCase))
                        startMin = true;
                }

                Application.Run(new MainForm(startMin));
            }
        }
    }

    public class FanSettings
    {
        public string ActivePreset = "turbo";
        public int ManualPercent = 85;
        public int TargetChannel = -1; // -1 = All 4 headers, 0..3 = individual
        public bool AutoStart = true;
        public int[] CurveTemps = new int[] { 0, 20, 30, 40, 50, 60, 70, 75 };
        public int[] CurvePercents = new int[] { 82, 82, 86, 90, 96, 100, 100, 100 };

        private static string ConfigPath
        {
            get
            {
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "AigoFanStudio");
                if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);
                return Path.Combine(dir, "settings.ini");
            }
        }

        public void Save()
        {
            try
            {
                var sb = new StringBuilder();
                sb.AppendLine("ActivePreset=" + ActivePreset);
                sb.AppendLine("ManualPercent=" + ManualPercent);
                sb.AppendLine("TargetChannel=" + TargetChannel);
                sb.AppendLine("AutoStart=" + (AutoStart ? "1" : "0"));
                sb.AppendLine("CurveTemps=" + string.Join(",", CurveTemps));
                sb.AppendLine("CurvePercents=" + string.Join(",", CurvePercents));
                File.WriteAllText(ConfigPath, sb.ToString(), Encoding.UTF8);
            }
            catch { }
        }

        public static FanSettings Load()
        {
            var s = new FanSettings();
            try
            {
                if (!File.Exists(ConfigPath)) return s;
                foreach (string line in File.ReadAllLines(ConfigPath, Encoding.UTF8))
                {
                    int eq = line.IndexOf('=');
                    if (eq <= 0) continue;
                    string k = line.Substring(0, eq).Trim();
                    string v = line.Substring(eq + 1).Trim();
                    if (k == "ActivePreset") s.ActivePreset = v;
                    else if (k == "ManualPercent") int.TryParse(v, out s.ManualPercent);
                    else if (k == "TargetChannel") int.TryParse(v, out s.TargetChannel);
                    else if (k == "AutoStart") s.AutoStart = (v == "1" || v.Equals("true", StringComparison.OrdinalIgnoreCase));
                    else if (k == "CurvePercents")
                    {
                        string[] parts = v.Split(',');
                        if (parts.Length == 8)
                        {
                            for (int i = 0; i < 8; i++)
                            {
                                int pv;
                                if (int.TryParse(parts[i], out pv))
                                    s.CurvePercents[i] = Math.Max(20, Math.Min(100, pv));
                            }
                        }
                    }
                }
            }
            catch { }
            return s;
        }
    }

    public class CurveCanvas : Control
    {
        public int[] Temps = new int[] { 0, 20, 30, 40, 50, 60, 70, 75 };
        public int[] Percents = new int[] { 82, 82, 86, 90, 96, 100, 100, 100 };
        public float LiveCpuTemp = 45f;
        public int LiveDutyPct = 85;
        public event EventHandler CurveEdited;

        private int _dragIdx = -1;
        private int _hoverIdx = -1;

        public CurveCanvas()
        {
            this.DoubleBuffered = true;
            this.SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw, true);
            this.Cursor = Cursors.Hand;
        }

        private Rectangle PlotArea
        {
            get { return new Rectangle(48, 22, Math.Max(100, Width - 70), Math.Max(80, Height - 52)); }
        }

        private PointF NodeToScreen(int idx)
        {
            Rectangle r = PlotArea;
            float x = r.Left + (Temps[idx] / 85f) * r.Width;
            float y = r.Bottom - (Percents[idx] / 100f) * r.Height;
            return new PointF(x, y);
        }

        public int EvaluateDutyAt(float tempC)
        {
            if (tempC <= Temps[0]) return Percents[0];
            if (tempC >= Temps[Temps.Length - 1]) return Percents[Percents.Length - 1];
            for (int i = 0; i < Temps.Length - 1; i++)
            {
                if (tempC >= Temps[i] && tempC <= Temps[i + 1])
                {
                    float span = Math.Max(1f, Temps[i + 1] - Temps[i]);
                    float t = (tempC - Temps[i]) / span;
                    return (int)Math.Round(Percents[i] + t * (Percents[i + 1] - Percents[i]));
                }
            }
            return Percents[Percents.Length - 1];
        }

        protected override void OnMouseDown(MouseEventArgs e)
        {
            base.OnMouseDown(e);
            for (int i = 0; i < Temps.Length; i++)
            {
                PointF p = NodeToScreen(i);
                float dx = e.X - p.X, dy = e.Y - p.Y;
                if (dx * dx + dy * dy <= 196f)
                {
                    _dragIdx = i;
                    break;
                }
            }
        }

        protected override void OnMouseMove(MouseEventArgs e)
        {
            base.OnMouseMove(e);
            if (_dragIdx >= 0)
            {
                Rectangle r = PlotArea;
                int pct = (int)Math.Round(((r.Bottom - e.Y) / (float)r.Height) * 100f);
                pct = Math.Max(20, Math.Min(100, pct));
                Percents[_dragIdx] = pct;
                // Keep monotonic non-decreasing curve so Smart Fan hardware accepts cleanly
                for (int i = _dragIdx + 1; i < Percents.Length; i++)
                    if (Percents[i] < pct) Percents[i] = pct;
                for (int i = 0; i < _dragIdx; i++)
                    if (Percents[i] > pct) Percents[i] = pct;
                Invalidate();
            }
            else
            {
                int found = -1;
                for (int i = 0; i < Temps.Length; i++)
                {
                    PointF p = NodeToScreen(i);
                    float dx = e.X - p.X, dy = e.Y - p.Y;
                    if (dx * dx + dy * dy <= 196f) { found = i; break; }
                }
                if (found != _hoverIdx) { _hoverIdx = found; Invalidate(); }
            }
        }

        protected override void OnMouseUp(MouseEventArgs e)
        {
            base.OnMouseUp(e);
            if (_dragIdx >= 0)
            {
                _dragIdx = -1;
                if (CurveEdited != null) CurveEdited(this, EventArgs.Empty);
            }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = TextRenderingHint.ClearTypeGridFit;

            using (SolidBrush bg = new SolidBrush(Color.FromArgb(18, 22, 34)))
                g.FillRectangle(bg, ClientRectangle);

            Rectangle r = PlotArea;
            using (Pen borderPen = new Pen(Color.FromArgb(42, 52, 76), 1f))
                g.DrawRectangle(borderPen, r);

            using (Font axisFont = new Font("Segoe UI", 8.2f, FontStyle.Regular))
            using (SolidBrush lblBrush = new SolidBrush(Color.FromArgb(148, 163, 184)))
            using (Pen gridPen = new Pen(Color.FromArgb(30, 38, 58), 1f))
            {
                gridPen.DashStyle = DashStyle.Dot;
                for (int pct = 25; pct <= 100; pct += 25)
                {
                    float y = r.Bottom - (pct / 100f) * r.Height;
                    g.DrawLine(gridPen, r.Left, y, r.Right, y);
                    g.DrawString(pct + "%", axisFont, lblBrush, 8, y - 7);
                }
                for (int tc = 0; tc <= 80; tc += 20)
                {
                    float x = r.Left + (tc / 85f) * r.Width;
                    g.DrawLine(gridPen, x, r.Top, x, r.Bottom);
                    g.DrawString(tc + "°C", axisFont, lblBrush, x - 12, r.Bottom + 7);
                }
            }

            PointF[] pts = new PointF[Temps.Length];
            for (int i = 0; i < Temps.Length; i++) pts[i] = NodeToScreen(i);

            using (GraphicsPath area = new GraphicsPath())
            {
                area.AddLines(pts);
                area.AddLine(pts[pts.Length - 1].X, r.Bottom, pts[0].X, r.Bottom);
                area.CloseFigure();
                using (LinearGradientBrush fill = new LinearGradientBrush(r, Color.FromArgb(95, 0, 212, 255), Color.FromArgb(8, 0, 212, 255), LinearGradientMode.Vertical))
                {
                    g.FillPath(fill, area);
                }
            }

            using (Pen glowPen = new Pen(Color.FromArgb(70, 0, 229, 255), 6f))
            {
                glowPen.LineJoin = LineJoin.Round;
                g.DrawLines(glowPen, pts);
            }
            using (Pen linePen = new Pen(Color.FromArgb(56, 232, 255), 2.5f))
            {
                linePen.LineJoin = LineJoin.Round;
                g.DrawLines(linePen, pts);
            }

            // Live CPU Operating Point Crosshair
            float clampedT = Math.Max(0f, Math.Min(85f, LiveCpuTemp));
            float liveX = r.Left + (clampedT / 85f) * r.Width;
            float liveY = r.Bottom - (LiveDutyPct / 100f) * r.Height;
            using (Pen crossPen = new Pen(Color.FromArgb(120, 255, 107, 129), 1.2f))
            {
                crossPen.DashStyle = DashStyle.Dash;
                g.DrawLine(crossPen, liveX, r.Top, liveX, r.Bottom);
                g.DrawLine(crossPen, r.Left, liveY, r.Right, liveY);
            }
            using (SolidBrush outerPulse = new SolidBrush(Color.FromArgb(75, 255, 90, 110)))
                g.FillEllipse(outerPulse, liveX - 10, liveY - 10, 20, 20);
            using (SolidBrush innerPulse = new SolidBrush(Color.FromArgb(255, 94, 120)))
                g.FillEllipse(innerPulse, liveX - 5, liveY - 5, 10, 10);

            // Draggable Curve Nodes
            using (Font nodeFont = new Font("Segoe UI Semibold", 7.8f))
            using (SolidBrush txtBrush = new SolidBrush(Color.FromArgb(224, 242, 254)))
            {
                for (int i = 0; i < pts.Length; i++)
                {
                    bool active = (i == _dragIdx || i == _hoverIdx);
                    float rad = active ? 6.5f : 5.0f;
                    using (SolidBrush nb = new SolidBrush(active ? Color.FromArgb(255, 214, 102) : Color.FromArgb(14, 165, 233)))
                        g.FillEllipse(nb, pts[i].X - rad, pts[i].Y - rad, rad * 2, rad * 2);
                    using (Pen np = new Pen(Color.White, 1.6f))
                        g.DrawEllipse(np, pts[i].X - rad, pts[i].Y - rad, rad * 2, rad * 2);

                    if (active || i == 0 || i == 3 || i == 5 || i == 7)
                    {
                        string tag = Percents[i] + "%";
                        g.DrawString(tag, nodeFont, txtBrush, pts[i].X - 12, pts[i].Y - 20);
                    }
                }
            }
        }
    }

    public class MainForm : Form
    {
        private FanSettings _settings;
        private SmartGuardianFanControlCoordinateSystem _fanHw;
        private readonly object _hwLock = new object();
        private bool _hwReady = false;
        private string _hwStatusText = "Đang kết nối chip điều khiển Gigabyte Super I/O...";

        private Label _lblCpuTemp, _lblVrmTemp, _lblGpuTemp, _lblDutyVal, _lblVoltVal, _lblStatusBadge;
        private Button _btnSilent, _btnBalanced, _btnTurbo, _btnMax, _btnManual;
        private TrackBar _sliderManual;
        private Label _lblManualPct;
        private ComboBox _cmbChannel;
        private CheckBox _chkAutoStart;
        private CurveCanvas _curveCanvas;
        private NotifyIcon _trayIcon;
        private System.Windows.Forms.Timer _uiTimer;

        private float _cpuTemp = 45f, _vrmTemp = 38f, _pchTemp = 40f, _sysTemp = 35f, _gpuTemp = 38f;
        private float[] _fanRpms = new float[4];
        private int _currentAppliedPct = 85;
        private int _gpuTick = 0;
        private bool _allowExit = false;

        public MainForm(bool startMinimized)
        {
            _settings = FanSettings.Load();
            InitHardware();
            BuildUI();
            SetupTray();

            ApplyCurrentSettingsToHardware(false);
            SyncAutoStartRegistry(_settings.AutoStart);
            PollSensorsOnce();

            _uiTimer = new System.Windows.Forms.Timer();
            _uiTimer.Interval = 1500;
            _uiTimer.Tick += (s, e) => PollSensorsOnce();
            _uiTimer.Start();

            if (startMinimized)
            {
                this.WindowState = FormWindowState.Minimized;
                this.ShowInTaskbar = false;
                this.Load += (s, e) => this.Hide();
            }
        }

        private void InitHardware()
        {
            try
            {
                lock (_hwLock)
                {
                    _fanHw = new SmartGuardianFanControlCoordinateSystem();
                    _hwReady = _fanHw.IsSupported;
                    if (_hwReady)
                    {
                        var info = _fanHw.HardwareInfo;
                        _hwStatusText = string.Format("ĐÃ KẾT NỐI PHẦN CỨNG • Gigabyte B760M ({0} cổng Fan PWM/DC • {1} cảm biến nhiệt)",
                            info.FanControlCount, info.TemperatureInputCount);
                    }
                    else
                    {
                        _hwStatusText = "Không tìm thấy bộ điều khiển SmartGuardian trên bo mạch chủ.";
                    }
                }
            }
            catch (Exception ex)
            {
                _hwReady = false;
                _hwStatusText = "Lỗi khởi tạo driver phần cứng: " + ex.Message;
            }
        }

        private void BuildUI()
        {
            this.Text = "Aigo Fan Studio • Điều Khiển Tốc Độ Fan CPU & Case (Gigabyte B760M)";
            this.ClientSize = new Size(760, 565);
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.FromArgb(11, 15, 25);
            this.ForeColor = Color.White;
            this.Font = new Font("Segoe UI", 9.5f);

            string icoPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "aigo_fan.ico");
            if (File.Exists(icoPath)) this.Icon = new Icon(icoPath);

            // Header Banner
            Panel header = new Panel { Dock = DockStyle.Top, Height = 68, BackColor = Color.FromArgb(16, 22, 36) };
            Label title = new Label
            {
                Text = "❄️ AIGO FAN STUDIO",
                Font = new Font("Segoe UI", 16f, FontStyle.Bold),
                ForeColor = Color.FromArgb(56, 232, 255),
                AutoSize = true,
                Location = new Point(20, 11)
            };
            Label sub = new Label
            {
                Text = "Intel Core i5-14400F  •  Gigabyte B760M G P WIFI DDR4  •  Điều khiển trực tiếp Điện áp DC 12V & xung PWM",
                Font = new Font("Segoe UI", 8.8f),
                ForeColor = Color.FromArgb(148, 163, 184),
                AutoSize = true,
                Location = new Point(23, 41)
            };
            header.Controls.Add(title);
            header.Controls.Add(sub);
            this.Controls.Add(header);

            // 4 Live Metric Cards
            int cardY = 80, cardW = 172, cardH = 84, gap = 10, startX = 20;
            _lblCpuTemp = CreateMetricCard(startX + (cardW + gap) * 0, cardY, cardW, cardH, "NHIỆT ĐỘ CPU", "-- °C", Color.FromArgb(56, 232, 255));
            _lblGpuTemp = CreateMetricCard(startX + (cardW + gap) * 1, cardY, cardW, cardH, "GPU RTX 3060", "-- °C", Color.FromArgb(74, 222, 128));
            _lblVrmTemp = CreateMetricCard(startX + (cardW + gap) * 2, cardY, cardW, cardH, "VRM / MAINBOARD", "-- °C", Color.FromArgb(250, 204, 21));
            _lblDutyVal = CreateMetricCard(startX + (cardW + gap) * 3, cardY, cardW, cardH, "CÔNG SUẤT FAN AIGO", "85%", Color.FromArgb(251, 113, 133), out _lblVoltVal);

            // Preset Mode Buttons Row
            Label lblMode = new Label
            {
                Text = "CHẾ ĐỘ TỐC ĐỘ QUẠT (1 CHẠM):",
                Font = new Font("Segoe UI", 8.8f, FontStyle.Bold),
                ForeColor = Color.FromArgb(148, 163, 184),
                AutoSize = true,
                Location = new Point(20, 176)
            };
            this.Controls.Add(lblMode);

            int btnY = 198, btnW = 136, btnH = 40, btnGap = 10;
            _btnSilent = CreatePresetBtn("🌙 Êm ái (Silent)", startX + (btnW + btnGap) * 0, btnY, btnW, btnH, "silent");
            _btnBalanced = CreatePresetBtn("⚖️ Cân bằng", startX + (btnW + btnGap) * 1, btnY, btnW, btnH, "balanced");
            _btnTurbo = CreatePresetBtn("🚀 Turbo Aigo", startX + (btnW + btnGap) * 2, btnY, btnW, btnH, "turbo");
            _btnMax = CreatePresetBtn("🔥 Tối đa 100%", startX + (btnW + btnGap) * 3, btnY, btnW, btnH, "max");
            _btnManual = CreatePresetBtn("🎛️ Kéo tay %", startX + (btnW + btnGap) * 4, btnY, btnW, btnH, "manual");

            // Manual Slider & Channel Selector Panel
            Panel ctrlBar = new Panel
            {
                Location = new Point(20, 248),
                Size = new Size(720, 48),
                BackColor = Color.FromArgb(18, 24, 38)
            };
            Label lblSlider = new Label
            {
                Text = "Tốc độ cố định:",
                Location = new Point(12, 14),
                AutoSize = true,
                ForeColor = Color.FromArgb(203, 213, 225)
            };
            _sliderManual = new TrackBar
            {
                Minimum = 25,
                Maximum = 100,
                TickFrequency = 5,
                Value = Math.Max(25, Math.Min(100, _settings.ManualPercent)),
                Location = new Point(112, 8),
                Size = new Size(255, 34),
                BackColor = Color.FromArgb(18, 24, 38)
            };
            _lblManualPct = new Label
            {
                Text = _sliderManual.Value + "%",
                Font = new Font("Segoe UI", 11f, FontStyle.Bold),
                ForeColor = Color.FromArgb(56, 232, 255),
                Location = new Point(370, 12),
                AutoSize = true
            };
            _sliderManual.Scroll += (s, e) =>
            {
                _lblManualPct.Text = _sliderManual.Value + "%";
            };
            _sliderManual.MouseUp += (s, e) =>
            {
                _settings.ActivePreset = "manual";
                _settings.ManualPercent = _sliderManual.Value;
                ApplyCurrentSettingsToHardware(true);
            };

            Label lblCh = new Label
            {
                Text = "Cổng áp dụng:",
                Location = new Point(432, 14),
                AutoSize = true,
                ForeColor = Color.FromArgb(203, 213, 225)
            };
            _cmbChannel = new ComboBox
            {
                DropDownStyle = ComboBoxStyle.DropDownList,
                Location = new Point(528, 11),
                Size = new Size(180, 26),
                BackColor = Color.FromArgb(28, 36, 56),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat
            };
            _cmbChannel.Items.AddRange(new object[]
            {
                "Tất cả cổng (CPU + Case 1-3)",
                "Chỉ CPU_FAN (Fan Aigo)",
                "Chỉ SYS_FAN 1",
                "Chỉ SYS_FAN 2",
                "Chỉ SYS_FAN 3"
            });
            _cmbChannel.SelectedIndex = (_settings.TargetChannel < 0 || _settings.TargetChannel > 3) ? 0 : (_settings.TargetChannel + 1);
            _cmbChannel.SelectedIndexChanged += (s, e) =>
            {
                _settings.TargetChannel = _cmbChannel.SelectedIndex == 0 ? -1 : (_cmbChannel.SelectedIndex - 1);
                ApplyCurrentSettingsToHardware(true);
            };

            ctrlBar.Controls.Add(lblSlider);
            ctrlBar.Controls.Add(_sliderManual);
            ctrlBar.Controls.Add(_lblManualPct);
            ctrlBar.Controls.Add(lblCh);
            ctrlBar.Controls.Add(_cmbChannel);
            this.Controls.Add(ctrlBar);

            // Interactive Smart Fan Curve Section
            Label lblCurve = new Label
            {
                Text = "BIỂU ĐỒ ĐƯỜNG CONG NHIỆT ĐỘ THÔNG MINH (Kéo thả các nút tròn để tùy chỉnh % tốc độ theo nhiệt độ CPU):",
                Font = new Font("Segoe UI", 8.6f, FontStyle.Bold),
                ForeColor = Color.FromArgb(148, 163, 184),
                Location = new Point(20, 306),
                AutoSize = true
            };
            this.Controls.Add(lblCurve);

            _curveCanvas = new CurveCanvas
            {
                Location = new Point(20, 328),
                Size = new Size(720, 182)
            };
            Array.Copy(_settings.CurvePercents, _curveCanvas.Percents, 8);
            _curveCanvas.CurveEdited += (s, e) =>
            {
                _settings.ActivePreset = "custom";
                Array.Copy(_curveCanvas.Percents, _settings.CurvePercents, 8);
                ApplyCurrentSettingsToHardware(true);
            };
            this.Controls.Add(_curveCanvas);

            // Footer Bar
            _chkAutoStart = new CheckBox
            {
                Text = "Tự khởi động ngầm & giữ tốc độ Fan khi bật máy",
                Checked = _settings.AutoStart,
                Location = new Point(20, 523),
                AutoSize = true,
                ForeColor = Color.FromArgb(203, 213, 225)
            };
            _chkAutoStart.CheckedChanged += (s, e) =>
            {
                _settings.AutoStart = _chkAutoStart.Checked;
                SyncAutoStartRegistry(_settings.AutoStart);
                _settings.Save();
            };
            this.Controls.Add(_chkAutoStart);

            _lblStatusBadge = new Label
            {
                Text = _hwStatusText,
                Font = new Font("Segoe UI", 8.5f),
                ForeColor = _hwReady ? Color.FromArgb(74, 222, 128) : Color.FromArgb(248, 113, 113),
                Location = new Point(355, 525),
                Size = new Size(385, 22),
                TextAlign = ContentAlignment.MiddleRight
            };
            this.Controls.Add(_lblStatusBadge);

            UpdatePresetButtonStyles();
        }

        private Label CreateMetricCard(int x, int y, int w, int h, string caption, string initVal, Color accent)
        {
            Label dummy;
            return CreateMetricCard(x, y, w, h, caption, initVal, accent, out dummy);
        }

        private Label CreateMetricCard(int x, int y, int w, int h, string caption, string initVal, Color accent, out Label subLabel)
        {
            Panel card = new Panel { Location = new Point(x, y), Size = new Size(w, h), BackColor = Color.FromArgb(18, 24, 38) };
            Panel topBar = new Panel { Dock = DockStyle.Top, Height = 3, BackColor = accent };
            Label lblCap = new Label
            {
                Text = caption,
                Font = new Font("Segoe UI", 7.8f, FontStyle.Bold),
                ForeColor = Color.FromArgb(148, 163, 184),
                Location = new Point(12, 10),
                AutoSize = true
            };
            Label lblVal = new Label
            {
                Text = initVal,
                Font = new Font("Segoe UI", 18f, FontStyle.Bold),
                ForeColor = accent,
                Location = new Point(10, 28),
                AutoSize = true
            };
            subLabel = new Label
            {
                Text = "",
                Font = new Font("Segoe UI", 7.8f),
                ForeColor = Color.FromArgb(148, 163, 184),
                Location = new Point(12, 62),
                AutoSize = true
            };
            card.Controls.Add(topBar);
            card.Controls.Add(lblCap);
            card.Controls.Add(lblVal);
            card.Controls.Add(subLabel);
            this.Controls.Add(card);
            return lblVal;
        }

        private Button CreatePresetBtn(string text, int x, int y, int w, int h, string presetKey)
        {
            Button b = new Button
            {
                Text = text,
                Tag = presetKey,
                Location = new Point(x, y),
                Size = new Size(w, h),
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI Semibold", 9.2f),
                Cursor = Cursors.Hand
            };
            b.FlatAppearance.BorderSize = 1;
            b.Click += (s, e) => ActivatePreset(presetKey);
            this.Controls.Add(b);
            return b;
        }

        private void ActivatePreset(string key)
        {
            _settings.ActivePreset = key;
            if (key == "silent")
                _settings.CurvePercents = new int[] { 30, 32, 38, 45, 55, 68, 82, 95 };
            else if (key == "balanced")
                _settings.CurvePercents = new int[] { 48, 50, 56, 65, 76, 88, 96, 100 };
            else if (key == "turbo")
                _settings.CurvePercents = new int[] { 82, 82, 86, 90, 96, 100, 100, 100 };
            else if (key == "max")
                _settings.CurvePercents = new int[] { 100, 100, 100, 100, 100, 100, 100, 100 };
            else if (key == "manual")
            {
                int p = _sliderManual.Value;
                _settings.ManualPercent = p;
                _settings.CurvePercents = new int[] { p, p, p, p, p, Math.Max(p, 90), Math.Max(p, 95), 100 };
            }

            Array.Copy(_settings.CurvePercents, _curveCanvas.Percents, 8);
            _curveCanvas.Invalidate();
            ApplyCurrentSettingsToHardware(true);
        }

        private void UpdatePresetButtonStyles()
        {
            foreach (Button b in new[] { _btnSilent, _btnBalanced, _btnTurbo, _btnMax, _btnManual })
            {
                if (b == null) continue;
                bool active = string.Equals((string)b.Tag, _settings.ActivePreset, StringComparison.OrdinalIgnoreCase);
                b.BackColor = active ? Color.FromArgb(14, 116, 144) : Color.FromArgb(22, 30, 48);
                b.ForeColor = active ? Color.White : Color.FromArgb(203, 213, 225);
                b.FlatAppearance.BorderColor = active ? Color.FromArgb(56, 232, 255) : Color.FromArgb(45, 58, 86);
            }
        }

        private void ApplyCurrentSettingsToHardware(bool saveConfig)
        {
            UpdatePresetButtonStyles();
            if (saveConfig) _settings.Save();
            if (!_hwReady || _fanHw == null) return;

            try
            {
                lock (_hwLock)
                {
                    int startCh = _settings.TargetChannel < 0 ? 0 : _settings.TargetChannel;
                    int endCh = _settings.TargetChannel < 0 ? 3 : _settings.TargetChannel;

                    if (_settings.ActivePreset == "max")
                    {
                        _fanHw.ResetCalibrationPwm();
                        var fullSet = BuildDataPointSet(new int[] { 100, 100, 100, 100, 100, 100, 100, 100 });
                        for (int ch = startCh; ch <= endCh; ch++)
                        {
                            _fanHw.Set(ch, fullSet);
                            _fanHw.SetCalibrationPwm(ch, 100);
                        }
                        _currentAppliedPct = 100;
                    }
                    else if (_settings.ActivePreset == "manual")
                    {
                        int p = Math.Max(25, Math.Min(100, _settings.ManualPercent));
                        _fanHw.ResetCalibrationPwm();
                        var manSet = BuildDataPointSet(_settings.CurvePercents);
                        for (int ch = startCh; ch <= endCh; ch++)
                        {
                            _fanHw.Set(ch, manSet);
                            _fanHw.SetCalibrationPwm(ch, p);
                        }
                        _currentAppliedPct = p;
                    }
                    else
                    {
                        _fanHw.ResetCalibrationPwm();
                        var curveSet = BuildDataPointSet(_settings.CurvePercents);
                        for (int ch = startCh; ch <= endCh; ch++)
                        {
                            _fanHw.Set(ch, curveSet);
                        }
                        _currentAppliedPct = _curveCanvas != null ? _curveCanvas.EvaluateDutyAt(_cpuTemp) : _settings.CurvePercents[3];
                    }
                }
                if (_lblStatusBadge != null)
                {
                    _lblStatusBadge.ForeColor = Color.FromArgb(74, 222, 128);
                    _lblStatusBadge.Text = "✓ Đã nạp mức quạt (" + _settings.ActivePreset.ToUpper() + ") xuống chip Gigabyte B760M!";
                }
            }
            catch (Exception ex)
            {
                if (_lblStatusBadge != null)
                {
                    _lblStatusBadge.ForeColor = Color.FromArgb(248, 113, 113);
                    _lblStatusBadge.Text = "Lỗi ghi cấu hình Fan: " + ex.Message;
                }
            }
        }

        private SmartFanDataPointSet BuildDataPointSet(int[] pcts)
        {
            var set = new SmartFanDataPointSet();
            set.Mode = FanConfigMode.SmartFanMode;
            set.DeltaTemperature = 2;
            set.FanSpeed = 0;
            set.DataPoints = new List<SmartFanDataPoint>();
            int[] xs = _settings.CurveTemps;
            for (int i = 0; i < 8; i++)
            {
                var dp = new SmartFanDataPoint();
                dp.X = xs[i];
                dp.Y = (int)Math.Round(Math.Max(20, Math.Min(100, pcts[i])) * 2.55);
                set.DataPoints.Add(dp);
            }
            return set;
        }

        private void PollSensorsOnce()
        {
            if (_hwReady && _fanHw != null)
            {
                try
                {
                    var temps = new List<float>();
                    var rpms = new List<float>();
                    lock (_hwLock)
                    {
                        _fanHw.GetHardwareMonitorDatas(ref temps, ref rpms);
                    }
                    if (temps != null && temps.Count >= 5)
                    {
                        _sysTemp = temps[0];
                        _pchTemp = temps[1];
                        _cpuTemp = temps[2];
                        _vrmTemp = temps[4];
                    }
                    if (rpms != null)
                    {
                        for (int i = 0; i < Math.Min(4, rpms.Count); i++) _fanRpms[i] = rpms[i];
                    }
                }
                catch { }
            }

            if (_gpuTick % 3 == 0)
            {
                ThreadPool.QueueUserWorkItem(_ =>
                {
                    try
                    {
                        var psi = new ProcessStartInfo("nvidia-smi", "--query-gpu=temperature.gpu --format=csv,noheader,nounits")
                        {
                            CreateNoWindow = true,
                            UseShellExecute = false,
                            RedirectStandardOutput = true
                        };
                        using (var p = Process.Start(psi))
                        {
                            string s = p.StandardOutput.ReadToEnd().Trim();
                            p.WaitForExit(1500);
                            float gt;
                            if (float.TryParse(s.Split('\n')[0].Trim(), out gt)) _gpuTemp = gt;
                        }
                    }
                    catch { }
                });
            }
            _gpuTick++;

            if (_settings.ActivePreset == "max") _currentAppliedPct = 100;
            else if (_settings.ActivePreset == "manual") _currentAppliedPct = _settings.ManualPercent;
            else _currentAppliedPct = _curveCanvas.EvaluateDutyAt(_cpuTemp);

            _lblCpuTemp.Text = string.Format("{0:0} °C", _cpuTemp);
            _lblCpuTemp.ForeColor = _cpuTemp >= 75 ? Color.FromArgb(248, 113, 113) : (_cpuTemp >= 60 ? Color.FromArgb(250, 204, 21) : Color.FromArgb(56, 232, 255));
            _lblGpuTemp.Text = string.Format("{0:0} °C", _gpuTemp);
            _lblVrmTemp.Text = string.Format("{0:0} / {1:0} °C", _vrmTemp, _pchTemp);

            _lblDutyVal.Text = _currentAppliedPct + "%";
            float estVolt = 12.0f * (_currentAppliedPct / 100f);
            if (_fanRpms[0] > 50)
                _lblVoltVal.Text = string.Format("{0:0} RPM  •  ~{1:0.0}V", _fanRpms[0], estVolt);
            else
                _lblVoltVal.Text = string.Format("Điện áp cấp: ~{0:0.0}V / 12V", estVolt);

            _curveCanvas.LiveCpuTemp = _cpuTemp;
            _curveCanvas.LiveDutyPct = _currentAppliedPct;
            _curveCanvas.Invalidate();

            if (_trayIcon != null)
            {
                _trayIcon.Text = string.Format("Aigo Fan Studio: CPU {0:0}°C | Fan {1}% ({2})",
                    _cpuTemp, _currentAppliedPct, _settings.ActivePreset.ToUpper());
            }
        }

        private void SetupTray()
        {
            _trayIcon = new NotifyIcon();
            _trayIcon.Icon = this.Icon ?? SystemIcons.Application;
            _trayIcon.Visible = true;
            _trayIcon.Text = "Aigo Fan Studio";

            var menu = new ContextMenuStrip();
            menu.Items.Add("❄️ Mở bảng điều khiển Aigo Fan Studio", null, (s, e) => ShowWindowFromTray());
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add("🌙 Chế độ Êm ái (Silent)", null, (s, e) => ActivatePreset("silent"));
            menu.Items.Add("⚖️ Chế độ Cân bằng (Balanced)", null, (s, e) => ActivatePreset("balanced"));
            menu.Items.Add("🚀 Chế độ Turbo Aigo (85-100%)", null, (s, e) => ActivatePreset("turbo"));
            menu.Items.Add("🔥 Tốc độ Tối đa (Full Speed 100%)", null, (s, e) => ActivatePreset("max"));
            menu.Items.Add(new ToolStripSeparator());
            menu.Items.Add("❌ Thoát hoàn toàn", null, (s, e) =>
            {
                _allowExit = true;
                _trayIcon.Visible = false;
                Application.Exit();
            });

            _trayIcon.ContextMenuStrip = menu;
            _trayIcon.DoubleClick += (s, e) => ShowWindowFromTray();
        }

        private void ShowWindowFromTray()
        {
            this.Show();
            this.ShowInTaskbar = true;
            this.WindowState = FormWindowState.Normal;
            this.Activate();
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            if (!_allowExit && e.CloseReason == CloseReason.UserClosing)
            {
                e.Cancel = true;
                this.Hide();
                this.ShowInTaskbar = false;
                _trayIcon.ShowBalloonTip(1800, "Aigo Fan Studio vẫn đang chạy ngầm",
                    "Quạt vẫn đang giữ chế độ " + _settings.ActivePreset.ToUpper() + " (" + _currentAppliedPct + "%). Nhấp đúp biểu tượng góc phải để mở lại.",
                    ToolTipIcon.Info);
                return;
            }
            base.OnFormClosing(e);
        }

        private void SyncAutoStartRegistry(bool enable)
        {
            try
            {
                using (RegistryKey rk = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Run", true))
                {
                    if (rk == null) return;
                    if (enable)
                        rk.SetValue("AigoFanStudio", "\"" + Application.ExecutablePath + "\" --minimized");
                    else
                        rk.DeleteValue("AigoFanStudio", false);
                }
            }
            catch { }
        }
    }
}
