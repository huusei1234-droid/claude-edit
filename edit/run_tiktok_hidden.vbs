Dim extraArg
extraArg = ""
If WScript.Arguments.Count > 0 Then
  extraArg = " " & WScript.Arguments(0)
End If
CreateObject("Wscript.Shell").Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""C:\AI\full studio\edit\run_tiktok_auto.ps1""" & extraArg, 0, False
