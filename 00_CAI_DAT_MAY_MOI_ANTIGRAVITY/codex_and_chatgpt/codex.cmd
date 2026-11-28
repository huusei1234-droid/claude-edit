@echo off
setlocal
set "CODEX_EXE="
for /f "delims=" %%F in ('dir /b /s /o-d "%LOCALAPPDATA%\OpenAI\Codex\bin\codex.exe" 2^>nul') do (
    set "CODEX_EXE=%%F"
    goto :found
)
echo OpenAI Codex binary not found under %LOCALAPPDATA%\OpenAI\Codex\bin >&2
exit /b 1
:found
"%CODEX_EXE%" %*
