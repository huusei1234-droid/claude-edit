param(
    [ValidateSet("Only2", "Restore3")]
    [string]$Mode = "Only2"
)

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class DisplaySwitcher {
    public const uint QDC_ALL_PATHS = 0x00000001;
    public const uint QDC_ONLY_ACTIVE_PATHS = 0x00000002;
    public const uint DISPLAYCONFIG_PATH_ACTIVE = 0x00000001;
    public const uint DISPLAYCONFIG_PATH_MODE_IDX_INVALID = 0xFFFFFFFF;

    public const uint SDC_USE_SUPPLIED_DISPLAY_CONFIG = 0x00000020;
    public const uint SDC_VALIDATE = 0x00000040;
    public const uint SDC_APPLY = 0x00000080;
    public const uint SDC_SAVE_TO_DATABASE = 0x00000200;
    public const uint SDC_ALLOW_CHANGES = 0x00000400;

    [StructLayout(LayoutKind.Sequential)]
    public struct LUID { public uint LowPart; public int HighPart; }

    [StructLayout(LayoutKind.Sequential)]
    public struct POINTL { public int x; public int y; }

    [StructLayout(LayoutKind.Sequential)]
    public struct DISPLAYCONFIG_PATH_SOURCE_INFO {
        public LUID adapterId;
        public uint id;
        public uint modeInfoIdx;
        public uint statusFlags;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct DISPLAYCONFIG_RATIONAL { public uint Numerator; public uint Denominator; }

    [StructLayout(LayoutKind.Sequential)]
    public struct DISPLAYCONFIG_PATH_TARGET_INFO {
        public LUID adapterId;
        public uint id;
        public uint modeInfoIdx;
        public uint outputTechnology;
        public uint rotation;
        public uint scaling;
        public DISPLAYCONFIG_RATIONAL refreshRate;
        public uint scanLineOrdering;
        public int targetAvailable;
        public uint statusFlags;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct DISPLAYCONFIG_PATH_INFO {
        public DISPLAYCONFIG_PATH_SOURCE_INFO sourceInfo;
        public DISPLAYCONFIG_PATH_TARGET_INFO targetInfo;
        public uint flags;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct DISPLAYCONFIG_SOURCE_MODE {
        public uint width;
        public uint height;
        public uint pixelFormat;
        public POINTL position;
    }

    [StructLayout(LayoutKind.Explicit)]
    public struct DISPLAYCONFIG_MODE_INFO {
        [FieldOffset(0)] public uint infoType;
        [FieldOffset(4)] public uint id;
        [FieldOffset(8)] public LUID adapterId;
        [FieldOffset(16)] public DISPLAYCONFIG_SOURCE_MODE sourceMode;
        [FieldOffset(16)] public ulong raw0;
        [FieldOffset(24)] public ulong raw1;
        [FieldOffset(32)] public ulong raw2;
        [FieldOffset(40)] public ulong raw3;
        [FieldOffset(48)] public ulong raw4;
        [FieldOffset(56)] public ulong raw5;
    }

    [DllImport("user32.dll")]
    public static extern int GetDisplayConfigBufferSizes(uint flags, out uint numPathArrayElements, out uint numModeInfoArrayElements);

    [DllImport("user32.dll")]
    public static extern int QueryDisplayConfig(uint flags, ref uint numPathArrayElements, [Out] DISPLAYCONFIG_PATH_INFO[] pathArray, ref uint numModeInfoArrayElements, [Out] DISPLAYCONFIG_MODE_INFO[] modeInfoArray, IntPtr currentTopologyId);

    [DllImport("user32.dll")]
    public static extern int SetDisplayConfig(uint numPathArrayElements, [In] DISPLAYCONFIG_PATH_INFO[] pathArray, uint numModeInfoArrayElements, [In] DISPLAYCONFIG_MODE_INFO[] modeInfoArray, uint flags);

    public static int SwitchToTargetOnly(uint keepTargetId) {
        uint pc, mc;
        int rc = GetDisplayConfigBufferSizes(QDC_ONLY_ACTIVE_PATHS, out pc, out mc);
        if (rc != 0) return rc;

        var paths = new DISPLAYCONFIG_PATH_INFO[pc];
        var modes = new DISPLAYCONFIG_MODE_INFO[mc];
        rc = QueryDisplayConfig(QDC_ONLY_ACTIVE_PATHS, ref pc, paths, ref mc, modes, IntPtr.Zero);
        if (rc != 0) return rc;

        int foundIdx = -1;
        for (int i = 0; i < pc; i++) {
            if (paths[i].targetInfo.id == keepTargetId) {
                foundIdx = i;
                break;
            }
        }
        if (foundIdx < 0) return -99;

        var chosen = paths[foundIdx];
        uint srcModeIdx = chosen.sourceInfo.modeInfoIdx;
        uint tgtModeIdx = chosen.targetInfo.modeInfoIdx;

        // Build clean 1-path + its source/target mode array with Primary Position = (0, 0)
        var newPaths = new DISPLAYCONFIG_PATH_INFO[1];
        chosen.flags = DISPLAYCONFIG_PATH_ACTIVE;

        if (srcModeIdx < mc && tgtModeIdx < mc) {
            var newModes = new DISPLAYCONFIG_MODE_INFO[2];
            newModes[0] = modes[srcModeIdx];
            newModes[0].sourceMode.position.x = 0;
            newModes[0].sourceMode.position.y = 0;
            newModes[1] = modes[tgtModeIdx];

            chosen.sourceInfo.modeInfoIdx = 0;
            chosen.targetInfo.modeInfoIdx = 1;
            newPaths[0] = chosen;

            rc = SetDisplayConfig(1, newPaths, 2, newModes, SDC_APPLY | SDC_USE_SUPPLIED_DISPLAY_CONFIG | SDC_ALLOW_CHANGES | SDC_SAVE_TO_DATABASE);
            if (rc == 0) return 0;
        }

        // Fallback: let Windows pick fresh mode indices automatically
        chosen.sourceInfo.id = 0;
        chosen.sourceInfo.modeInfoIdx = DISPLAYCONFIG_PATH_MODE_IDX_INVALID;
        chosen.targetInfo.modeInfoIdx = DISPLAYCONFIG_PATH_MODE_IDX_INVALID;
        newPaths[0] = chosen;
        return SetDisplayConfig(1, newPaths, 0, null, SDC_APPLY | SDC_USE_SUPPLIED_DISPLAY_CONFIG | SDC_ALLOW_CHANGES | SDC_SAVE_TO_DATABASE);
    }

    public static int RestoreThreeMonitors() {
        uint pc, mc;
        int rc = GetDisplayConfigBufferSizes(QDC_ALL_PATHS, out pc, out mc);
        if (rc != 0) return rc;

        var paths = new DISPLAYCONFIG_PATH_INFO[pc];
        var modes = new DISPLAYCONFIG_MODE_INFO[mc];
        rc = QueryDisplayConfig(QDC_ALL_PATHS, ref pc, paths, ref mc, modes, IntPtr.Zero);
        if (rc != 0) return rc;

        // Targets: 4352 (Monitor 1, left vertical rot=4, 1080x1920 at 0,0),
        //          4353 (Monitor 2, center landscape rot=1, 2560x1440 at 1080,371),
        //          4355 (Monitor 3, right vertical rot=2, 1440x2560 at 3640,-642)
        uint[] targets = new uint[] { 4352, 4353, 4355 };
        uint[] srcIds  = new uint[] { 2, 0, 1 };
        uint[] rots    = new uint[] { 4, 1, 2 };

        var selected = new DISPLAYCONFIG_PATH_INFO[3];
        for (int t = 0; t < 3; t++) {
            bool ok = false;
            for (int i = 0; i < pc; i++) {
                if (paths[i].targetInfo.id == targets[t] && paths[i].targetInfo.targetAvailable != 0 && paths[i].sourceInfo.id == srcIds[t]) {
                    selected[t] = paths[i];
                    selected[t].flags = DISPLAYCONFIG_PATH_ACTIVE;
                    selected[t].targetInfo.rotation = rots[t];
                    selected[t].sourceInfo.modeInfoIdx = DISPLAYCONFIG_PATH_MODE_IDX_INVALID;
                    selected[t].targetInfo.modeInfoIdx = DISPLAYCONFIG_PATH_MODE_IDX_INVALID;
                    ok = true;
                    break;
                }
            }
            if (!ok) return -100 - t;
        }
        return SetDisplayConfig(3, selected, 0, null, SDC_APPLY | SDC_USE_SUPPLIED_DISPLAY_CONFIG | SDC_ALLOW_CHANGES | SDC_SAVE_TO_DATABASE);
    }
}
"@

if ($Mode -eq "Only2") {
    $res = [DisplaySwitcher]::SwitchToTargetOnly(4353)
    Write-Output "SwitchToTargetOnly(4353) result = $res"
} else {
    $res = [DisplaySwitcher]::RestoreThreeMonitors()
    Write-Output "RestoreThreeMonitors() result = $res"
}

Start-Sleep -Milliseconds 800
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::AllScreens | Select-Object DeviceName, Primary, Bounds | Format-Table -AutoSize
