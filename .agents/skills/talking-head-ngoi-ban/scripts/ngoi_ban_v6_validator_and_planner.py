#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plan V6 Master speech cuts and HyperFrames parameters with Python 3.11."""

from __future__ import annotations

import argparse
from array import array
from dataclasses import dataclass
from itertools import accumulate, groupby
import json
import math
from pathlib import Path
import re
import sys
import unicodedata
import wave


THEMES = (
    ("EdgeSweep_Gold", "#FFD979"),
    ("LightSweep_Emerald", "#79F5BD"),
    ("StrokeUp_Ruby", "#FF829B"),
    ("NeonNumber_Cyan", "#75EFFF"),
    ("RingsBg_Amber", "#FFC266"),
)
CARD_MOTIONS = ("fan", "flip", "carousel")
EPISODE_COUNT = 14
FADE_SECONDS = 0.025
RMS_SECONDS = 0.020
BREATH_RMS = 0.012
WORD_EDGE_TOLERANCE = 0.060
SUPPRESS_PADDING = 0.08
WORD_PATTERN = re.compile(r"[^\W_]+")
CLIPPED_MARK = re.compile(r"^(?:[-‐‑–—]|…|\.{3})")


@dataclass(frozen=True)
class Word:
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class Token:
    text: str
    word_index: int
    clipped: bool


def theme_for_episode(episode: int) -> dict:
    if not 1 <= episode <= EPISODE_COUNT:
        raise ValueError(f"episode must be 1–{EPISODE_COUNT}")
    cycle, slot = divmod(episode - 1, len(THEMES))
    name, accent = THEMES[slot]
    return {
        "episode": episode,
        "cycle": cycle + 1,
        "theme": name,
        "accent": accent,
        "card_motion": CARD_MOTIONS[(slot + cycle) % len(CARD_MOTIONS)],
        "shoulder": "left" if episode % 2 else "right",
    }


def master_settings() -> dict:
    return {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "speaker_offset_px": 0,
        "bg_blur": 0,
        "bgm_volume": 0.0,
        "voice_lufs": -14.0,
        "micro_sfx_db": -20.0,
        "micro_sfx_volume": 0.1,
        "hook": {
            "start": 0.0, "end": 3.0, "background": "#FFD600",
            "text_color": "#000000", "uppercase": True,
        },
        "presenter_z_index": 20,
        "behind_stage_z_index": 10,
    }


def emphasis_plan(head_top_y: float, intervals: list[tuple[float, float]], duration: float) -> dict:
    if not math.isfinite(head_top_y) or not 0 <= head_top_y <= 1920:
        raise ValueError("head_top_y must be within 0–1920 pixels")
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration must be positive and finite")
    cues = []
    suppression = []
    previous_end = 0.0
    for start, end in sorted(intervals):
        if not previous_end <= start < end <= duration:
            raise ValueError("keyword intervals must be non-overlapping and within the final video")
        previous_end = end
        cues.append({"start": start, "end": end})
        suppress_start = max(0.0, round(start - SUPPRESS_PADDING, 9))
        suppress_end = min(duration, round(end + SUPPRESS_PADDING, 9))
        if suppression and suppress_start <= suppression[-1]["end"]:
            suppression[-1]["end"] = suppress_end
        else:
            suppression.append({"start": suppress_start, "end": suppress_end})
    top = max(14, head_top_y - 186)
    return {
        "head_top_y": head_top_y,
        "top": top,
        "title_safe": 248 <= top <= 1388,
        "cues": cues,
        "hide_subtitles_and_cards": suppression,
    }


def load_words(payload: object) -> list[Word]:
    """Read Whisper segment words, flat words, or the existing V5 w/s/e form."""
    nested = isinstance(payload, dict) and "words" not in payload
    if isinstance(payload, dict):
        rows = payload.get("segments" if nested else "words")
    else:
        rows = payload
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("expected a word list, {words: [...]}, or {segments: [...]} with timed words")
    if nested or any("words" in row for row in rows):
        if any(not isinstance(row.get("words"), list) for row in rows):
            raise ValueError("each Whisper segment must contain a words list")
        rows = [word for row in rows for word in row["words"]]

    words = []
    previous_start = 0.0
    for index, row in enumerate(rows, 1):
        try:
            raw_text = row.get("word", row.get("w", row.get("text")))
            start = float(row.get("start", row.get("s")))
            end = float(row.get("end", row.get("e")))
            if not isinstance(raw_text, str) or not previous_start <= start <= end < math.inf:
                raise ValueError
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"invalid word or unordered timestamps in entry {index}") from error
        previous_start = start
        if WORD_PATTERN.search(raw_text):
            words.append(Word(raw_text.strip(), start, end))
    return words


def find_repeat_tokens(words: list[Word]) -> tuple[list[Token], dict[int, tuple[str, int]]]:
    """Find tandem 1–5 grams and marked fragments. Keep the last full take."""
    tokens = []
    for word_index, word in enumerate(words):
        text = unicodedata.normalize("NFC", word.text.casefold())
        for match in WORD_PATTERN.finditer(text):
            clipped = bool(CLIPPED_MARK.match(text[match.end():]))
            tokens.append(Token(match.group(), word_index, clipped))

    active = list(range(len(tokens)))
    keys = [token.text for token in tokens]
    removed = {}
    i = 0
    while i + 1 < len(active):
        candidates = []
        for size in range(1, min(5, (len(active) - i) // 2) + 1):
            pattern = [keys[index] for index in active[i:i + size]]
            end = i + size
            while pattern == [keys[index] for index in active[end:end + size]]:
                end += size
            if end >= i + 2 * size:
                candidates.append((end - i, size, end - size))

        if candidates:
            _, size, stop = max(candidates, key=lambda item: (item[0], -item[1]))
            reason = ("tandem", size)
        else:
            current, following = (tokens[index] for index in active[i:i + 2])
            if not (current.clipped and following.text.startswith(current.text)):
                i += 1
                continue
            stop = i + 1
            reason = ("clipped_restart", 1)
        removed.update((index, reason) for index in active[i:stop])
        del active[i:stop]
        i = max(0, i - 9)

    # Tail such as “kiểm tra sức khỏe | kiểm tra” where the second take stops early.
    remaining = [keys[index] for index in active]
    for size in range(min(5, len(active) - 1), 1, -1):
        for partial in range(size - 1, 0, -1):
            if size + partial > len(active) or (partial == 1 and not tokens[active[-1]].clipped):
                continue
            previous = len(active) - size - partial
            if remaining[previous:previous + partial] == remaining[-partial:]:
                removed.update((index, ("truncated_tail", size)) for index in active[-partial:])
                return tokens, removed
    return tokens, removed


class Waveform:
    def __init__(self, path: Path):
        with wave.open(str(path), "rb") as source:
            if (source.getnchannels(), source.getsampwidth(), source.getcomptype()) != (1, 2, "NONE"):
                raise ValueError("audio must be mono 16-bit PCM WAV")
            self.rate = source.getframerate()
            self.samples = array("h", source.readframes(source.getnframes()))
            if len(self.samples) != source.getnframes() or not self.samples:
                raise ValueError("WAV is empty or incomplete")
        if sys.byteorder != "little":
            self.samples.byteswap()
        self.count = len(self.samples)
        self.fade = round(FADE_SECONDS * self.rate)
        self.half_rms = round(RMS_SECONDS * self.rate / 2)
        if self.half_rms == 0:
            raise ValueError("WAV sample rate is too low for a 20 ms RMS window")
        self.power = array("Q", accumulate((sample * sample for sample in self.samples), initial=0))

    def rms(self, start: int, end: int) -> float:
        return math.sqrt((self.power[end] - self.power[start]) / (end - start)) / 32768

    def breath_edge(self, before: Word, after: Word, *, fade_out: bool) -> int | None:
        before_slack = min(WORD_EDGE_TOLERANCE, (before.end - before.start) / 3)
        after_slack = min(WORD_EDGE_TOLERANCE, (after.end - after.start) / 3)
        target = round(after.start * self.rate)
        lo = max(self.half_rms, math.ceil((before.end - before_slack) * self.rate))
        hi = min(self.count - self.half_rms, math.floor((after.start + after_slack) * self.rate))
        if fade_out:
            lo = max(lo, self.fade)
        else:
            hi = min(hi, self.count - self.fade)

        best = None
        for sample in range(lo, hi + 1):
            left, right = self.samples[sample - 1], self.samples[sample]
            if left and right and (left < 0) == (right < 0):
                continue
            if self.rms(sample - self.half_rms, sample + self.half_rms) >= BREATH_RMS:
                continue
            fade_start, fade_end = (sample - self.fade, sample) if fade_out else (sample, sample + self.fade)
            if self.rms(fade_start, fade_end) < BREATH_RMS:
                score = (abs(sample - target), abs(left) + abs(right), sample)
                if best is None or score < best:
                    best = score
        return None if best is None else best[2]


def plan_speech(words: list[Word], waveform: Waveform | None = None) -> dict:
    if waveform and any(word.end > waveform.count / waveform.rate + WORD_EDGE_TOLERANCE for word in words):
        raise ValueError("word timestamps run past the audio; use the WAV from the same source")
    tokens, removed = find_repeat_tokens(words)
    by_word = {}
    retained = set()
    for token_index, token in enumerate(tokens):
        if token_index in removed:
            by_word.setdefault(token.word_index, set()).add(removed[token_index])
        else:
            retained.add(token.word_index)

    candidates = []
    # Consecutive Whisper rows form one splice, even if different patterns matched.
    for _, entries in groupby(enumerate(sorted(by_word)), key=lambda entry: entry[1] - entry[0]):
        group = [word_index for _, word_index in entries]
        first, last = group[0], group[-1]
        reasons = sorted(set().union(*(by_word[index] for index in group)))
        candidate = {
            "text": " ".join(word.text for word in words[first:last + 1]),
            "whisper_range": [words[first].start, words[last].end],
            "matches": [{"kind": kind, "ngram": size} for kind, size in reasons],
            "status": "needs_waveform",
        }
        candidates.append(candidate)
        if retained.intersection(group):
            candidate.update(status="review", reason="repeat shares a Whisper timestamp with retained speech")
        elif waveform:
            start = waveform.breath_edge(words[first - 1], words[first], fade_out=True) if first else 0
            end = waveform.breath_edge(words[last], words[last + 1], fade_out=False) if last + 1 < len(words) else waveform.count
            if start is None or end is None or start >= end:
                candidate.update(status="review", reason="missing a quiet zero crossing with room for the 25 ms fade")
                continue
            candidate.update(
                status="ready",
                cut={
                    "start_sample": start, "end_sample": end,
                    "start_s": start / waveform.rate, "end_s": end / waveform.rate,
                    "fade_out_samples": waveform.fade if start else 0,
                    "fade_in_samples": waveform.fade if end < waveform.count else 0,
                },
            )

    ready = [candidate for candidate in candidates if candidate["status"] == "ready"]
    for left, right in zip(ready, ready[1:]):
        left_cut, right_cut = left["cut"], right["cut"]
        if left_cut["end_sample"] + left_cut["fade_in_samples"] > right_cut["start_sample"] - right_cut["fade_out_samples"]:
            for candidate in (left, right):
                candidate.update(status="review", reason="neighboring cuts leave insufficient room for both fades")
    for candidate in candidates:
        if candidate["status"] != "ready":
            candidate.pop("cut", None)
    return {
        "word_count": len(words),
        "sample_rate_hz": waveform.rate if waveform else None,
        "breath_rms_limit": BREATH_RMS,
        "rms_window_ms": 20,
        "micro_fade_ms": 25,
        "candidates": candidates,
        "cuts": [candidate["cut"] for candidate in candidates if candidate["status"] == "ready"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan V6 Master speech cleanup and the theme rotation for 14 Reels.")
    parser.add_argument("--words", type=Path, help="UTF-8 Whisper or Full Studio V5 word timestamps JSON")
    parser.add_argument("--audio", type=Path, help="mono 16-bit PCM WAV from the same source as --words")
    parser.add_argument("--episode", type=int, choices=range(1, EPISODE_COUNT + 1),
                        help="emit one episode instead of the whole series")
    parser.add_argument("--head-top-y", type=float, help="top edge of the RVM hair matte in the 1920 px frame")
    parser.add_argument("--duration", type=float, help="final video duration in seconds for --head-top-y and --keyword")
    parser.add_argument("--keyword", nargs=2, type=float, metavar=("START", "END"), action="append",
                        help="keyword time window after editing; repeat for multiple cues")
    parser.add_argument("--output", type=Path, help="write UTF-8 JSON to this path instead of stdout")
    args = parser.parse_args()

    if args.audio and not args.words:
        parser.error("--audio requires --words")
    if args.keyword and args.head_top_y is None:
        parser.error("--keyword requires --head-top-y")
    if (args.head_top_y is None) != (args.duration is None):
        parser.error("--head-top-y and --duration must be provided together")

    try:
        report = {"version": "V6 Master", "master": master_settings()}
        if args.episode is None:
            report["series"] = [theme_for_episode(episode) for episode in range(1, EPISODE_COUNT + 1)]
        else:
            report["episode"] = theme_for_episode(args.episode)
        if args.words:
            words = load_words(json.loads(args.words.read_text(encoding="utf-8-sig")))
            report["speech"] = plan_speech(words, Waveform(args.audio) if args.audio else None)
        if args.head_top_y is not None:
            report["emphasis"] = emphasis_plan(args.head_top_y, args.keyword or [], args.duration)
        result = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(result, encoding="utf-8")
        else:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stdout.write(result)
    except (OSError, ValueError, wave.Error, EOFError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
