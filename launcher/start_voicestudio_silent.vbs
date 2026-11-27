Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\AI\full studio\voice-studio"
sh.Run "cmd.exe /c bun run start", 0, False
