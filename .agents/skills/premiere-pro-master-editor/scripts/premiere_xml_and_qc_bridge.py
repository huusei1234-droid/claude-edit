#!/usr/bin/env python3
"""Convert a Full Studio timeline manifest to Premiere-compatible FCP 7 XML."""

import argparse
import json
import os
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


VIDEO_TRACKS = ("V1_Base_Footage", "V2_Broll_Overlay", "V3_SafeZone_Graphics")
AUDIO_TRACKS = ("A1_Clean_Voice", "A2_Micro_SFX", "A3_BGM_Ducked")
TRACKS = VIDEO_TRACKS + AUDIO_TRACKS
MARKERS = {"Hook": 4294954555, "CTA": 4281740498}  # Premiere ARGB: yellow, blue.
TICKS_PER_SECOND = 254_016_000_000


@dataclass(frozen=True)
class Source:
    path: Path
    duration: int
    fps: int
    ntsc: bool
    video_size: tuple[int, int] | None
    alpha: str
    audio_channels: int
    sample_rate: int

    @property
    def frame_rate(self):
        return Fraction(self.fps * 1000, 1001) if self.ntsc else Fraction(self.fps)


@dataclass(frozen=True)
class Clip:
    source_id: str
    start: int
    end: int
    source_in: int
    source_out: int


def require_object(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def require_int(value, label, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty text")
    return value


def read_source(value, label, base_dir, sequence_fps):
    data = require_object(value, label)
    path_text = require_text(data.get("path"), f"{label}.path")
    if "://" in path_text or "\0" in path_text:
        raise ValueError(f"{label}.path must be a filesystem path")
    path = Path(os.path.abspath(base_dir / path_text))
    duration = require_int(data.get("duration_frames"), f"{label}.duration_frames", 1)
    fps = require_int(data.get("fps", sequence_fps), f"{label}.fps", 1)
    ntsc = data.get("ntsc", False)
    if fps not in (24, 25, 30, 48, 50, 60, 120) or type(ntsc) is not bool:
        raise ValueError(f"{label}: unsupported source fps or non-boolean ntsc")

    video_size = None
    alpha = "none"
    if "video" in data:
        video = require_object(data["video"], f"{label}.video")
        video_size = (
            require_int(video.get("width"), f"{label}.video.width", 1),
            require_int(video.get("height"), f"{label}.video.height", 1),
        )
        alpha = video.get("alpha", "none")
        if alpha not in ("none", "straight", "black", "white"):
            raise ValueError(f"{label}.video.alpha must be none, straight, black or white")

    audio_channels = require_int(data.get("audio_channels", 0), f"{label}.audio_channels")
    if audio_channels not in (0, 1, 2) or (video_size is None and not audio_channels):
        raise ValueError(f"{label} must describe video, mono/stereo audio, or both")
    sample_rate = require_int(data.get("sample_rate_hz", 48000), f"{label}.sample_rate_hz", 1)
    return Source(path, duration, fps, ntsc, video_size, alpha, audio_channels, sample_rate)


def read_track(rows, track_name, sources, sequence_fps):
    if not isinstance(rows, list):
        raise ValueError(f"tracks.{track_name} must be an array")
    clips = []
    for index, value in enumerate(rows):
        label = f"tracks.{track_name}[{index}]"
        data = require_object(value, label)
        source_id = require_text(data.get("source"), f"{label}.source")
        if source_id not in sources:
            raise ValueError(f"{label}.source refers to an unknown source: {source_id}")
        source = sources[source_id]
        if track_name in VIDEO_TRACKS and source.video_size is None:
            raise ValueError(f"{label} requires a video source")
        if track_name in AUDIO_TRACKS and not source.audio_channels:
            raise ValueError(f"{label} requires an audio source")

        start = require_int(data.get("start_frame"), f"{label}.start_frame")
        duration = require_int(data.get("duration_frames"), f"{label}.duration_frames", 1)
        source_in = require_int(data.get("in_frame", 0), f"{label}.in_frame")
        # The placement uses sequence frames. Snap the corresponding source trim to its edit grid.
        source_duration = int(duration * source.frame_rate / sequence_fps + Fraction(1, 2))
        source_out = source_in + source_duration
        if source_duration < 1 or source_out > source.duration:
            raise ValueError(f"{label} trim is outside the source duration ({source.duration} frames)")
        clips.append(Clip(source_id, start, start + duration, source_in, source_out))

    clips.sort(key=lambda clip: clip.start)
    for left, right in zip(clips, clips[1:]):
        if left.end > right.start:
            raise ValueError(f"tracks.{track_name} has overlapping clips at frame {right.start}")
    return clips


def fields(parent, **values):
    for key, value in values.items():
        ET.SubElement(parent, key).text = str(value)


def add_rate(parent, fps, ntsc=False):
    fields(ET.SubElement(parent, "rate"), timebase=fps, ntsc="TRUE" if ntsc else "FALSE")


def add_timecode(parent, fps, ntsc=False):
    timecode = ET.SubElement(parent, "timecode")
    add_rate(timecode, fps, ntsc)
    fields(timecode, string="00:00:00:00", frame=0, displayformat="NDF")


def video_format(parent, size, fps, ntsc=False):
    sample = ET.SubElement(parent, "samplecharacteristics")
    add_rate(sample, fps, ntsc)
    width, height = size
    fields(sample, width=width, height=height, anamorphic="FALSE",
           pixelaspectratio="square", fielddominance="none")


def audio_format(parent, sample_rate):
    fields(ET.SubElement(parent, "samplecharacteristics"), depth=16, samplerate=sample_rate)


def write_source(file_node, source):
    uri = source.path.as_uri()
    if uri.startswith("file:///"):
        uri = "file://localhost" + uri[len("file://"):]
    fields(file_node, name=source.path.name, pathurl=uri)
    add_rate(file_node, source.fps, source.ntsc)
    fields(file_node, duration=source.duration)
    add_timecode(file_node, source.fps, source.ntsc)
    media = ET.SubElement(file_node, "media")
    if source.video_size is not None:
        video_format(ET.SubElement(media, "video"), source.video_size, source.fps, source.ntsc)
    if source.audio_channels:
        audio = ET.SubElement(media, "audio")
        audio_format(audio, source.sample_rate)
        fields(audio, channelcount=source.audio_channels)


def write_clip(track, clip, source, index, file_id, define_file, is_audio):
    item = ET.SubElement(track, "clipitem", id=f"clipitem-{index}")
    fields(item, name=source.path.name, enabled="TRUE", duration=source.duration)
    add_rate(item, source.fps, source.ntsc)
    fields(item, start=clip.start, end=clip.end, **{"in": clip.source_in, "out": clip.source_out})
    ticks_per_frame = TICKS_PER_SECOND / source.frame_rate
    fields(item, pproTicksIn=int(clip.source_in * ticks_per_frame),
           pproTicksOut=int(clip.source_out * ticks_per_frame))
    if not is_audio:
        fields(item, alphatype=source.alpha, pixelaspectratio="square", anamorphic="FALSE")

    file_node = ET.SubElement(item, "file", id=file_id)
    if define_file:
        write_source(file_node, source)
    if is_audio:
        item.set("premiereChannelType", "stereo" if source.audio_channels == 2 else "mono")
        fields(ET.SubElement(item, "sourcetrack"), mediatype="audio", trackindex=1)


def build_xml(manifest, base_dir):
    data = require_object(manifest, "manifest")
    name = require_text(data.get("name"), "name")
    fps = require_int(data.get("fps"), "fps", 1)
    width = require_int(data.get("width"), "width", 1)
    height = require_int(data.get("height"), "height", 1)
    if fps not in (24, 30) or (width, height) not in ((1080, 1920), (1920, 1080)):
        raise ValueError("sequence must be 1080x1920 or 1920x1080 at 24 or 30 fps")

    sources = {
        key: read_source(value, f"sources.{key}", base_dir, fps)
        for key, value in require_object(data.get("sources"), "sources").items()
    }
    track_data = require_object(data.get("tracks"), "tracks")
    if unknown := track_data.keys() - set(TRACKS):
        raise ValueError(f"unknown tracks: {', '.join(sorted(unknown))}")
    tracks = {key: read_track(track_data.get(key, []), key, sources, fps) for key in TRACKS}
    duration = max((clip.end for clips in tracks.values() for clip in clips), default=0)
    if duration == 0:
        raise ValueError("the sequence must contain at least one clip")
    markers = require_object(data.get("markers"), "markers")
    marker_frames = {key: require_int(markers.get(key), f"markers.{key}") for key in MARKERS}
    if any(frame >= duration for frame in marker_frames.values()):
        raise ValueError("Hook and CTA must both be inside the sequence")

    root = ET.Element("xmeml", version="4")
    sequence = ET.SubElement(root, "sequence", {
        "id": "sequence-1",
        "MZ.Sequence.PreviewFrameSizeWidth": str(width),
        "MZ.Sequence.PreviewFrameSizeHeight": str(height),
        "MZ.Sequence.VideoTimeDisplayFormat": "100" if fps == 24 else "104",
    })
    fields(sequence, name=name, duration=duration)
    add_rate(sequence, fps)
    media = ET.SubElement(sequence, "media")
    video = ET.SubElement(media, "video")
    video_format(ET.SubElement(video, "format"), (width, height), fps)
    audio = ET.SubElement(media, "audio")
    fields(audio, numOutputChannels=2)
    audio_format(ET.SubElement(audio, "format"), 48000)

    file_ids = {}
    clip_index = 0
    for track_name, clips in tracks.items():
        is_audio = track_name in AUDIO_TRACKS
        track = ET.SubElement(audio if is_audio else video, "track", {"MZ.TrackName": track_name})
        if is_audio:
            # A Premiere Standard track accepts both mono and stereo source clips.
            track.attrib.update(premiereTrackType="Stereo", currentExplodedTrackIndex="0",
                                totalExplodedTrackCount="2")
        for clip in clips:
            clip_index += 1
            define_file = clip.source_id not in file_ids
            file_id = file_ids.setdefault(clip.source_id, f"file-{len(file_ids) + 1}")
            write_clip(track, clip, sources[clip.source_id], clip_index, file_id, define_file, is_audio)
        fields(track, enabled="TRUE", locked="FALSE")

    add_timecode(sequence, fps)
    for name, frame in sorted(marker_frames.items(), key=lambda pair: pair[1]):
        marker = ET.SubElement(sequence, "marker")
        fields(marker, name=name, comment="", **{"in": frame, "out": -1}, pproColor=MARKERS[name])

    ET.indent(root, space="  ")
    header = b'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n'
    return header + ET.tostring(root, encoding="utf-8") + b"\n"


def write_atomic(path, payload):
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".premiere-", suffix=".tmp",
                                         delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def self_test():
    manifest = {
        "name": "Tập 42 – Mở đầu & Kết",
        "width": 1080, "height": 1920, "fps": 30,
        "sources": {
            "base": {"path": "media/Cảnh #1 & A.mov", "duration_frames": 240,
                     "video": {"width": 1080, "height": 1920}, "audio_channels": 1},
            "broll": {"path": "media/B-roll.mov", "duration_frames": 120, "fps": 60,
                      "video": {"width": 1080, "height": 1920}},
            "graphic": {"path": "media/CTA.mov", "duration_frames": 120,
                        "video": {"width": 1080, "height": 1920, "alpha": "straight"}},
            "sfx": {"path": "media/SFX.wav", "duration_frames": 60, "audio_channels": 1},
            "bgm": {"path": "media/BGM.wav", "duration_frames": 240, "audio_channels": 2},
        },
        "tracks": {
            VIDEO_TRACKS[0]: [{"source": "base", "start_frame": 0, "in_frame": 24, "duration_frames": 120}],
            VIDEO_TRACKS[1]: [{"source": "broll", "start_frame": 20, "in_frame": 2, "duration_frames": 10}],
            VIDEO_TRACKS[2]: [{"source": "graphic", "start_frame": 90, "duration_frames": 30}],
            AUDIO_TRACKS[0]: [{"source": "base", "start_frame": 0, "in_frame": 24, "duration_frames": 120}],
            AUDIO_TRACKS[1]: [{"source": "sfx", "start_frame": 90, "duration_frames": 8}],
            AUDIO_TRACKS[2]: [{"source": "bgm", "start_frame": 0, "duration_frames": 120}],
        },
        "markers": {"Hook": 0, "CTA": 90},
    }
    for width, height in ((1080, 1920), (1920, 1080)):
        for fps in (24, 30):
            manifest.update(width=width, height=height, fps=fps)
            root = ET.fromstring(build_xml(manifest, Path.cwd()))
            assert root.tag == "xmeml" and root.get("version") == "4"
            sequence = root.find("sequence")
            assert sequence.findtext("name") == manifest["name"]
            assert sequence.findtext("duration") == "120"
            assert sequence.findtext("rate/timebase") == str(fps)
            assert sequence.findtext("rate/ntsc") == "FALSE"
            sample = sequence.find("media/video/format/samplecharacteristics")
            assert (sample.findtext("width"), sample.findtext("height")) == (str(width), str(height))
            for kind, expected in (("video", VIDEO_TRACKS), ("audio", AUDIO_TRACKS)):
                tracks = sequence.findall(f"media/{kind}/track")
                assert tuple(track.get("MZ.TrackName") for track in tracks) == expected
                assert all(len(track.findall("clipitem")) == 1 for track in tracks)
            items = sequence.findall("media/video/track/clipitem")
            assert items[0].findtext("out") == "144"
            assert "C%E1%BA%A3nh%20%231%20%26%20A.mov" in items[0].findtext("file/pathurl")
            assert items[1].findtext("out") == ("27" if fps == 24 else "22")
            assert items[2].findtext("alphatype") == "straight"
            audio = sequence.findall("media/audio/track/clipitem")
            assert audio[0].find("file").attrib == items[0].find("file").attrib
            assert len(audio[0].find("file")) == 0
            assert audio[2].get("premiereChannelType") == "stereo"
            assert [tuple(marker.findtext(tag) for tag in ("name", "in", "out", "pproColor"))
                    for marker in sequence.findall("marker")] == [
                ("Hook", "0", "-1", str(MARKERS["Hook"])),
                ("CTA", "90", "-1", str(MARKERS["CTA"])),
            ]

    manifest["tracks"].pop(VIDEO_TRACKS[1])
    root = ET.fromstring(build_xml(manifest, Path.cwd()))
    assert len(root.findall("sequence/media/video/track")) == 3
    assert root.findall("sequence/media/video/track")[1].find("clipitem") is None
    manifest["markers"]["CTA"] = 120
    try:
        build_xml(manifest, Path.cwd())
    except ValueError as error:
        assert "inside the sequence" in str(error)
    else:
        raise AssertionError("accepted a marker at the exclusive sequence end")
    print("SELF_TEST_OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="UTF-8 timeline JSON")
    parser.add_argument("--out", type=Path, help="Destination .xml file")
    parser.add_argument("--self-test", action="store_true", help="Generate and parse an in-memory fixture")
    args = parser.parse_args()
    if args.self_test:
        if args.manifest is not None or args.out is not None:
            parser.error("--self-test is a standalone mode")
        self_test()
        return 0
    if args.manifest is None or args.out is None:
        parser.error("--manifest and --out are required for export")

    try:
        manifest_path = args.manifest.resolve()
        output_path = args.out.resolve()
        if output_path.suffix.lower() != ".xml" or output_path == manifest_path:
            raise ValueError("--out must be a separate .xml file")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        payload = build_xml(manifest, manifest_path.parent)
        ET.fromstring(payload)
        write_atomic(output_path, payload)
    except (OSError, ValueError, ET.ParseError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
