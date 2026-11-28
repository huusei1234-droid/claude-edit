---
name: media-use
description: Resolve and generate HyperFrames media, including voiceover, music, SFX, images, video and transcripts. Treat footage and mix placed audio using Full Studio V6 Broadcast Audio & Media Master for frame-aligned Tactile Micro-SFX, voice loudness and BGM gain staging.
---

**Plugin installs:** Inside a HyperFrames plugin, follow [plugin execution rules](../hyperframes/references/plugin-installation.md).

**Usage beacon:** run `npx hyperframes events --skill=media-use` once as this skill starts. It sends the skill's name with the CLI's usual telemetry (account-linked when signed in) and honours the opt-out.

# Media in HyperFrames

Media lands as a local file in the project's `assets/` with a ledger record; renders never fetch. One verb finds or makes it:

```bash
npx hyperframes media-use resolve --type <type> --intent "<what you need>" --project <dir>
```

It prints one line, `resolved <id> → <path> (<type>, <metadata>)`. List reusable assets first with `--candidates` and judge the fit yourself; reuse, ingest (`--from`) and adopt are in `references/resolve.md`.

## Where it comes from

| Need | Free | HyperFrames credits | Local or the person's own key (only when they ask) |
| --- | --- | --- | --- |
| Music (`bgm`) | HeyGen catalog of 10k+ tracks (signed in) | Generated track | Local MusicGen |
| Sound effects (`sfx`) | HeyGen (signed in); Openverse (credit CC BY); bundled | | |
| Images, icons | HeyGen asset search, 75k+ (signed in) | Generated images | Local FLUX (mflux), if installed |
| Logos (`logo`) | theSVG, GitHub avatar, favicon; never redrawn | | |
| Voiceover (`voice`) | Voice Turbo, Free plan: 3 min a month | Voice Turbo on a paid plan, other HeyGen voices, cloning | `npx hyperframes tts` (Kokoro on device) |
| A presenter speaking | | Avatar video (`--type video`) | Local LTX for generic clips, if installed |
| Transcripts | `npx hyperframes transcribe` (Parakeet or whisper) | | |
| Cutouts | | Video: `--type cutout` | `npx hyperframes remove-background` |
| Grades, LUTs, looks | `npx hyperframes media-treatment` | | |

**Sign in.** Every time a request needs a HeyGen model or the catalog, run `npx hyperframes auth status` first. Not signed in: tell the person in one line that sign-in is free and gives the music catalog, asset search and 3 min of Voice Turbo a month on the Free plan, ask them to type an exclamation mark and `npx hyperframes auth login` in the prompt, and wait until they say it is done. Use local tools only when the person asks, not as a fallback.

**Host apps.** Inside an app with its own media tools, use those first. When `HEYGEN_API_BASE` is set, the host pays: don't ask for a sign-in; relay a refused call's message as written and stop.

**HeyGen.** `npx hyperframes media-use generate` makes images, shots, talking photos, voices and music on the sign-in alone. Helpers and direct recipes need the [`heygen` CLI](https://developers.heygen.com/cli); if it is missing, give the link and wait until they say it is installed. Direct `heygen` recipes bill that CLI's own login: use them only when that payer is selected.

**Credits.** Plan for the best result: no cheaper or free swaps, no dropped items, unless asked to save cost. Don't volunteer prices, estimates or usage; `--plan` is for you. A credit limit the person sets: write it once to `.hyperframes/credit-limit.json` as `{"credits": N}`; every paid call then refuses what would go past it (`--max-credits` only tightens). A step that won't fit (a `--plan` over what is left, or a refused call): say what doesn't, ask before dropping or shrinking it. A refused call names a `billing` command: say why, ask them to run it, then retry.

## Looks on real footage

Feedback that footage is dark, flat or dull, should feel retro or printed, needs a face hidden, or needs a reveal is media intent. Inspect the real `<img>`/`<video>`, pick one intent, and follow `references/media-treatments.md`; persist with `npx hyperframes media-treatment`, never a CSS, SVG or `.cube` stand-in.

## V6 Broadcast Audio & Media Master

Dùng `.agents/skills/media-use/scripts/studio_audio_sfx_mixer.py` để xuất bản phối Full Studio khi đã có thoại và mốc hình. Công cụ chạy bằng Python 3.11 và dùng FFmpeg trong `PATH` để xuất WAV stereo 48 kHz, PCM 24-bit.

```powershell
python -X utf8 .agents/skills/media-use/scripts/studio_audio_sfx_mixer.py --spec mix_spec.json --out mixed.wav
python -X utf8 .agents/skills/media-use/scripts/studio_audio_sfx_mixer.py --spec mix_spec.json --dry-run-filter
python -X utf8 .agents/skills/media-use/scripts/studio_audio_sfx_mixer.py --self-test
```

Mẫu `mix_spec.json` dùng UTF-8.

```json
{
  "voice": "audio/voice.wav",
  "bgm": "audio/bed.wav",
  "existing_bgm_detected": false,
  "fps": 30,
  "events": [
    { "type": "airy_whoosh", "frame": 30 },
    { "type": "pop", "frame": 30, "sequence_id": "reveal" },
    { "type": "click", "frame": 39, "sequence_id": "reveal" },
    { "type": "card_riffle", "frame": 48, "sequence_id": "reveal", "path": "audio/cards.wav" },
    { "type": "soft_ping", "time_ms": 2600 }
  ]
}
```

- Đường dẫn tương đối tính từ thư mục chứa JSON. `voice` là bắt buộc. `bgm` và `events` có thể bỏ qua. `existing_bgm_detected: true` tắt track BGM bổ sung. Tên `Whoosh - Lướt chuyển cảnh cơ bản.mp3` bị chặn ở mọi nguồn trong cấu hình, kể cả BGM đã tắt.
- Đặt mỗi cue bằng `time_ms` hoặc `frame` đếm từ 0. Khi dùng `frame`, khai báo `fps` bằng số hoặc phân số như `"30000/1001"`. `pop` và `click` khớp frame chạm đích. `airy_whoosh` (cũng nhận `whoosh`) vào sớm 110 ms, phần vượt trước đầu timeline được cắt. Dùng `source_onset_ms` để bỏ đoạn dẫn đầu đã có sẵn trong file SFX.
- `pop`, `click`, `soft_ping` và `airy_whoosh` có âm thanh đi kèm. Dùng `path` để chọn asset riêng. `card_riffle` cần `path`.
- Gắn cùng `sequence_id` cho 3–5 cue cùng chuỗi, mỗi cue một mốc. Cao độ đi lần lượt `0`, `+1`, `+2` semitone và tiếp tục theo số cue, tính theo thời gian xuất hiện. Với cue chưa gắn nhóm, công cụ nhận chuỗi 3–5 mốc cách nhau tối đa 500 ms và bỏ qua whoosh khi dò chuỗi. Nâng cao độ bằng đổi tốc độ phát nên cue ngắn đi nhẹ.
- Chuẩn hóa thoại về `−14.5 LUFS` tích hợp. Đo RMS thoại đã chuẩn hóa để đặt từng Micro-SFX thấp hơn `11 dB` và BGM thấp hơn `14.5 dB` trước limiter của bản phối. BGM dừng khi phần thoại và SFX kết thúc.
- `--dry-run-filter` in filtergraph và thứ tự input với mức gain danh định. Khi xuất WAV, công cụ đo nguồn để tính gain thực. `--self-test` kiểm tra filtergraph và chặn file cấm mà không cần FFmpeg hay media đầu vào.

## Offer once, never add silently

Scan a piece you build or review once for concrete gaps (on-screen text with no voiceover, emoji standing in for icons, placeholder images, silent cuts, 10 s+ with no music, a colour cast) and offer the fixes in one ask. No signal, no suggestion; respect "leave it".

## Where to look

| Task | Read |
| --- | --- |
| Resolve, reuse, adopt, ingest, flags | `references/resolve.md` |
| Grading, LUTs, `grade-compare` | `references/grading.md` |
| Voiceover, music, sound effects, captions, transcription | `references/audio.md` |
| Cut, reframe or transform media; direct `heygen` recipes | `references/operations.md` |
| Treatments, realtime effects, overlays, reveals | `references/media-treatments.md` |
| Install, sign-in, credentials, `--provider`, `--local-only`, RAM ladders | `references/setup-providers.md` |
| `media-use generate`, HeyGen transcription, prices | `references/heygen.md` |
| Fades, gain, ducking, automation, effects, buses on placed tracks | `references/mixing.md` |
| Local commands: grade, cutout, loudness, beats | `references/local.md` |
| Remembered preferences | `references/memory.md` |
