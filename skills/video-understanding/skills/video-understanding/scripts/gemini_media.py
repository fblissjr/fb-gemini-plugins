#!/usr/bin/env python3
"""Deterministic CLI helper for the `video-understanding` skill and plugin.

Enforces the Native-First (`agy`) Gate and wraps local preparation (`encode-1fps`,
`crop`) alongside `gemini-api` (using its built-in credential store) across
progressive-disclosure multimodal workflows:

1. `encode-1fps`: Local `$0` preparation for Path 1. Encodes any video (or
   `[--first F --last L]` frame span) into `<stem>.1fps.<first:05d>-<last:05d>.mp4`
   parts where each frame is held for `1.0s` (`-r 1`, muted, capped under `80 MB`
   per part), optionally burning in source frame numbers (`--burn-frame-numbers`),
   so `agy`'s built-in `read_file` tool achieves `1:1` frame alignment at `$0`
   API spend.
2. `crop`: Local `$0` image tile cropper for Path 3B. Crops a pixel region
   (`--box x1,y1,x2,y2`) or normalized `0..1000` region
   (`--box-1000 ymin,xmin,ymax,xmax`) to a PNG file for native `read_file`
   inspection.
3. `boxes`: Path 3A 2D bounding-box (`box_2d` `[ymin, xmin, ymax, xmax]` in
   `0..1000`) and polygon segmentation (`mask` `[[x, y], ...]` in `0..1000`)
   grounding, descaling to exact pixel coordinates (`box_xyxy_px` and
   `box_ltwh_px`) on the image's canvas and optionally matching against local
   detector outputs (`--match-boxes <json|npz>`, `IoU >= 0.50`).
4. `slice`: Path 2A server-side frame-span slicing (`start_offset` /
   `end_offset` in seconds from `[first..last]` frame spans) in static
   high-resolution mode at the video's frame rate.
5. `agentic-video`: Path 2B opt-in `"processing": "agentic"` timeline navigation
   on long single-canvas videos (`>100 MB` master videos), or mixed `agentic`
   (master video) + `static` (candidate clip via `--compare-clip`) continuity
   checks. Mechanically refuses `*_STACKED*` and `.1fps.` strips.
6. `zoom`: Path 3B Agentic Vision (`tools: [{"type": "code_execution"}]` +
   `"resolution": "ultra_high"`) on dense contact sheets or diagnostic grids
   when remote sandboxed code execution is required.
7. `transcribe-spans`: Path 4 speaker and lyric/dialogue transcription
   (audio-only or `--visual-speakers` at high resolution) with automatic
   conversion of `MM:SS(.mmm)` timestamps into `[start_frame, end_frame]` spans.

Native-First (`agy`) Gate:
  When a local video `<100 MB` is passed to `slice`, `agentic-video`, or
  `transcribe-spans` and a matching `<stem>.1fps.*.mp4` companion exists on
  disk, this tool refuses to upload the video unless `--force-api` is explicitly
  passed, instructing the caller to use `agy`'s built-in `read_file` tool at
  `$0` API spend.

Run `--self-test` to verify coordinate math, local `.json`/`.npz` IoU matching,
timestamp-to-frame conversion, local `crop` and `encode-1fps` helpers,
Native-First / multi-panel refusal guards, and `gemini-api --dry-run` payload
schemas without API spend.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_MODEL = os.environ.get("GEMINI_VIDEO_MODEL", "gemini-3.8-flash")
INLINE_MAX_BYTES = 12 * 1024 * 1024  # Safe raw ceiling under 20 MB base64 limit
READ_FILE_MAX_BYTES = 100 * 1024 * 1024  # agy read_file ceiling (100 MB)
ONE_A_SECOND_BYTES = 80_000_000  # 80 MB per .1fps part (20% headroom under 100 MB)
ONE_A_SECOND_COST = 0.1  # Conservative bytes/pixel/frame estimate at CRF 18


def _mime_of(path: Path, default: str = "image/png") -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or default


def _image_size(path: Path) -> tuple[int, int]:
    """Return `(width, height)` of an image using PIL or cv2."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            return int(im.width), int(im.height)
    except Exception:
        import cv2
        img = cv2.imread(str(path))
        if img is None:
            raise ValueError(f"cannot read image dimensions from {path}")
        h, w = img.shape[:2]
        return int(w), int(h)


def _probe_video(path: Path) -> tuple[int, int, int, float]:
    """Return `(width, height, total_frames, fps)` of a local video via `ffprobe`."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-count_packets",
        "-show_entries",
        "stream=width,height,r_frame_rate,nb_read_packets",
        "-of",
        "json",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {res.stderr.strip()}")
    data = json.loads(res.stdout)
    streams = data.get("streams") or []
    if not streams:
        raise ValueError(f"no video stream found in {path}")
    st = streams[0]
    w = int(st["width"])
    h = int(st["height"])
    frames = int(st.get("nb_read_packets") or st.get("nb_frames") or 0)
    rate_str = str(st.get("r_frame_rate") or "24/1")
    if "/" in rate_str:
        num, den = rate_str.split("/", 1)
        fps = float(num) / float(den) if float(den) != 0 else 24.0
    else:
        fps = float(rate_str)
    return w, h, frames, round(fps, 4)


def _resolve_fps(video_target: str, explicit_fps: float | None, default_fps: float = 24.0) -> float:
    """Use `explicit_fps` if given; else probe local video via `ffprobe`, falling back to `default_fps`."""
    if explicit_fps is not None and explicit_fps > 0:
        return float(explicit_fps)
    if not video_target.startswith("files/"):
        p = Path(video_target)
        if p.is_file() and shutil.which("ffprobe"):
            try:
                _, _, _, fps = _probe_video(p)
                if fps > 0:
                    return fps
            except Exception:
                pass
    return float(default_fps)


def _find_1fps_companions(video_path: Path) -> list[Path]:
    """Return any `<stem>.1fps.*.mp4` companions sitting alongside `video_path`."""
    if not video_path.parent.is_dir():
        return []
    stem = video_path.stem
    if ".1fps." in video_path.name:
        return [video_path]
    return sorted(video_path.parent.glob(f"{stem}.1fps.*.mp4"))


def _check_native_first(video_target: str, force_api: bool, dry_run: bool) -> None:
    """Refuse uploading a local `<100 MB` video when a `.1fps.*.mp4` companion exists."""
    if force_api or dry_run or video_target.startswith("files/"):
        return
    p = Path(video_target)
    if not p.is_file():
        return
    size_bytes = p.stat().st_size
    if size_bytes >= READ_FILE_MAX_BYTES:
        return
    companions = _find_1fps_companions(p)
    if companions:
        comp_names = ", ".join(c.name for c in companions[:3])
        raise ValueError(
            f"Native-First (agy) Gate refused uploading {p.name} ({size_bytes / (1024 * 1024):.1f} MB < 100 MB): "
            f"companion .1fps file(s) exist on disk ({comp_names}). "
            f"Use agy's native `read_file` tool on {comp_names} (and {p.name} for audio) at $0 API spend, "
            f"or pass --force-api if an explicit gemini-api call is required."
        )


def _check_not_stacked_for_agentic(video_target: str) -> None:
    """Refuse `*_STACKED*` or `.1fps.` diagnostic strips on `agentic-video`."""
    name_upper = Path(video_target).name.upper()
    if "STACKED" in name_upper or ".1FPS." in name_upper:
        raise ValueError(
            f"Path 2B (`processing: agentic`) is BANNED on multi-panel/stacked or .1fps strips ({video_target}). "
            f"Server-side dynamic cropping misreads multi-row diagnostic tiles. "
            f"Use Path 1 (`read_file` on `.1fps.mp4`) or Path 2A (`gemini_media.py slice` at `resolution: high`)."
        )


def descale_box_2d(box_2d: list[int | float], width: int, height: int) -> dict[str, Any]:
    """Convert Gemini `[ymin, xmin, ymax, xmax]` in `[0, 1000]` to pixel coordinates.

    Returns both `box_xyxy_px` (`[x1, y1, x2, y2]`) and `box_ltwh_px`
    (`[left, top, width, height]`).
    """
    if len(box_2d) != 4:
        raise ValueError(f"expected [ymin, xmin, ymax, xmax] of length 4, got {box_2d}")
    ymin, xmin, ymax, xmax = [float(v) for v in box_2d]
    x1 = round(xmin * width / 1000.0, 2)
    y1 = round(ymin * height / 1000.0, 2)
    x2 = round(xmax * width / 1000.0, 2)
    y2 = round(ymax * height / 1000.0, 2)
    w = round(max(0.0, x2 - x1), 2)
    h = round(max(0.0, y2 - y1), 2)
    return {
        "box_2d_1000": [ymin, xmin, ymax, xmax],
        "canvas": [int(width), int(height)],
        "box_xyxy_px": [x1, y1, x2, y2],
        "box_ltwh_px": [x1, y1, w, h],
    }


def descale_polygon(mask_1000: list[list[int | float]], width: int, height: int) -> list[list[float]]:
    """Convert Gemini `[[x, y], ...]` polygon in `[0, 1000]` to pixel `[[x_px, y_px], ...]`."""
    out: list[list[float]] = []
    for pt in mask_1000:
        if isinstance(pt, (list, tuple)) and len(pt) >= 2:
            out.append([
                round(float(pt[0]) * width / 1000.0, 2),
                round(float(pt[1]) * height / 1000.0, 2),
            ])
    return out


def _iou_ltwh(box_a: list[float], box_b: list[float]) -> float:
    ax0, ay0, aw, ah = [float(v) for v in box_a]
    bx0, by0, bw, bh = [float(v) for v in box_b]
    ax1, ay1 = ax0 + aw, ay0 + ah
    bx1, by1 = bx0 + bw, by0 + bh
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    union = max(0.0, aw) * max(0.0, ah) + max(0.0, bw) * max(0.0, bh) - inter
    return inter / union if union > 0 else 0.0


def match_detector_boxes(
    box_ltwh: list[float],
    target_size: tuple[int, int],
    detector_path: Path,
    source_frame: int | None = None,
) -> dict[str, Any]:
    """Match a `box_ltwh` (`[left, top, width, height]`) against local detector boxes.

    Supports two local detector formats:
    1. A JSON file (`.json`) containing `"boxes"` (or a top-level list) where each
       item is `[x1, y1, x2, y2]` (`xyxy`), `{"box_xyxy": [x1, y1, x2, y2]}`, or
       `{"box_ltwh": [left, top, width, height]}`.
    2. A bit-packed mask archive (`.npz`) containing `masks`, `frame`, and `first`
       (plus optional companion `<stem>.json` with `{"canvas": [w, h]}`).
    """
    if detector_path.suffix.lower() == ".json":
        raw = json.loads(detector_path.read_text(encoding="utf-8"))
        items = raw.get("boxes", raw) if isinstance(raw, dict) else raw
        candidates_ltwh: list[list[float]] = []
        for item in items or []:
            if isinstance(item, dict):
                if source_frame is not None and "frame" in item and int(item["frame"]) != int(source_frame):
                    continue
                if "box_ltwh" in item:
                    candidates_ltwh.append([float(v) for v in item["box_ltwh"]])
                elif "box_xyxy" in item:
                    x1, y1, x2, y2 = [float(v) for v in item["box_xyxy"]]
                    candidates_ltwh.append([x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)])
            elif isinstance(item, (list, tuple)) and len(item) == 4:
                x1, y1, x2, y2 = [float(v) for v in item]
                candidates_ltwh.append([x1, y1, max(0.0, x2 - x1), max(0.0, y2 - y1)])

        best_iou = 0.0
        best_box: list[float] | None = None
        best_rank: int | None = None
        for rank, cand in enumerate(candidates_ltwh):
            iou = _iou_ltwh(box_ltwh, cand)
            if iou > best_iou:
                best_iou = iou
                best_rank = rank
                best_box = [round(v, 2) for v in cand]
        fmt_box = (
            [int(v) if float(v).is_integer() else float(v) for v in best_box]
            if best_box is not None
            else None
        )
        return {
            "source_frame": source_frame,
            "detections_on_frame": len(candidates_ltwh),
            "best_detection_rank": best_rank,
            "best_iou": round(float(best_iou), 4),
            "passes_0_50_gate": bool(best_iou >= 0.5 and fmt_box is not None),
            "matched_box_ltwh": fmt_box,
        }

    import numpy as np

    z = np.load(detector_path)
    if "masks" not in z.files or "frame" not in z.files or "first" not in z.files:
        raise ValueError(f"{detector_path} is missing required keys (`masks`, `frame`, `first`)")
    if source_frame is None:
        raise ValueError("--frame is required when matching against a multi-frame .npz mask archive")
    pf = int(z["first"])
    p_json = detector_path.with_suffix(".json")
    if p_json.is_file():
        pw, ph = [int(v) for v in json.loads(p_json.read_text(encoding="utf-8"))["canvas"]]
    else:
        ph = int(z["masks"].shape[1])
        pw = int(round(ph * (target_size[0] / float(target_size[1]))))
    sx, sy = pw / float(target_size[0]), ph / float(target_size[1])
    rel = int(source_frame) - pf
    z_frames = np.asarray(z["frame"], dtype=np.int32)
    idxs = np.nonzero(z_frames == rel)[0]
    if len(idxs) == 0:
        return {
            "source_frame": int(source_frame),
            "relative_frame": int(rel),
            "detections_on_frame": 0,
            "best_iou": 0.0,
            "passes_0_50_gate": False,
            "matched_box_ltwh": None,
        }

    bx, by0, bw, bh = [float(v) for v in box_ltwh]
    ux0, uy0, ux1, uy1 = bx * sx, by0 * sy, (bx + bw) * sx, (by0 + bh) * sy
    best_iou = 0.0
    best_det_box: list[float] | None = None
    best_det_idx: int | None = None

    for det_rank, idx in enumerate(idxs):
        m_2d = np.unpackbits(z["masks"][int(idx)], axis=-1)[:, :pw].astype(bool)
        ys, xs = np.nonzero(m_2d)
        if len(ys) == 0:
            continue
        dx0, dy0 = float(xs.min()), float(ys.min())
        dx1, dy1 = float(xs.max() + 1), float(ys.max() + 1)
        ix0, iy0 = max(ux0, dx0), max(uy0, dy0)
        ix1, iy1 = min(ux1, dx1), min(uy1, dy1)
        inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
        union = (
            max(0.0, ux1 - ux0) * max(0.0, uy1 - uy0)
            + max(0.0, dx1 - dx0) * max(0.0, dy1 - dy0)
            - inter
        )
        if union > 0:
            iou = inter / union
            if iou > best_iou:
                best_iou = iou
                best_det_idx = int(det_rank)
                best_det_box = [
                    round(dx0 / sx, 2),
                    round(dy0 / sy, 2),
                    round((dx1 - dx0) / sx, 2),
                    round((dy1 - dy0) / sy, 2),
                ]

    fmt_box = (
        [int(v) if float(v).is_integer() else float(v) for v in best_det_box]
        if best_det_box is not None
        else None
    )
    frame_box_arg = (
        f"{int(source_frame)}:{fmt_box[0]},{fmt_box[1]},{fmt_box[2]},{fmt_box[3]}"
        if fmt_box is not None
        else None
    )
    return {
        "source_frame": int(source_frame),
        "relative_frame": int(rel),
        "detections_on_frame": int(len(idxs)),
        "best_detection_rank": best_det_idx,
        "best_iou": round(float(best_iou), 4),
        "passes_0_50_gate": bool(best_iou >= 0.5 and fmt_box is not None),
        "matched_box_ltwh": fmt_box,
        "frame_box_arg": frame_box_arg,
    }


def frame_span_to_offsets(first: int, last: int, fps: float = 24.0) -> tuple[float, float]:
    """Convert inclusive frame span `[first..last]` to `(start_offset, end_offset)` seconds."""
    if fps <= 0:
        raise ValueError(f"fps must be > 0, got {fps}")
    if last < first or first < 0:
        raise ValueError(f"invalid frame span [{first}..{last}]")
    return round(first / fps, 3), round((last + 1) / fps, 3)


_TS_RE = re.compile(
    r"^\s*(?:(?P<h>\d+):)?(?P<m>\d{1,2}):(?P<s>\d{1,2}(?:\.\d+)?)\s*$"
)


def parse_timestamp_seconds(ts: str | float | int) -> float:
    """Parse `HH:MM:SS(.mmm)`, `MM:SS(.mmm)`, or numeric seconds into float seconds."""
    if isinstance(ts, (int, float)):
        return float(ts)
    s = str(ts).strip()
    if not s:
        raise ValueError("empty timestamp")
    m = _TS_RE.match(s)
    if m:
        hours = int(m.group("h") or 0)
        minutes = int(m.group("m"))
        seconds = float(m.group("s"))
        return hours * 3600.0 + minutes * 60.0 + seconds
    if s.endswith("s"):
        return float(s[:-1].strip())
    return float(s)


def timestamp_span_to_frames(
    start_ts: str | float | int,
    end_ts: str | float | int,
    shot_first: int = 0,
    fps: float = 24.0,
    shot_last: int | None = None,
) -> tuple[int, int]:
    """Convert `(start_ts, end_ts)` clip-relative timestamps into inclusive `[start_frame, end_frame]`."""
    t0 = max(0.0, parse_timestamp_seconds(start_ts))
    t1 = max(t0, parse_timestamp_seconds(end_ts))
    f0 = int(shot_first) + int(round(t0 * fps))
    f1 = int(shot_first) + int(round(t1 * fps))
    if f1 < f0:
        f1 = f0
    if shot_last is not None:
        f0 = min(max(int(shot_first), f0), int(shot_last))
        f1 = min(max(f0, f1), int(shot_last))
    return f0, f1


def _burn_frame_label(rgb_bytes: bytes, width: int, height: int, frame_num: int) -> bytes:
    """Draw a high-contrast `frame NNNNN` badge in the top-left corner using PIL or cv2."""
    label = f"frame {frame_num:05d}"
    try:
        from PIL import Image, ImageDraw
        im = Image.frombytes("RGB", (width, height), rgb_bytes)
        draw = ImageDraw.Draw(im)
        pad = 6
        bbox = draw.textbbox((0, 0), label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.rectangle([8, 8, 8 + tw + pad * 2, 8 + th + pad * 2], fill=(0, 0, 0))
        draw.text((8 + pad, 8 + pad), label, fill=(255, 255, 0))
        return im.tobytes()
    except Exception:
        import cv2
        import numpy as np
        arr = np.frombuffer(rgb_bytes, dtype=np.uint8).reshape((height, width, 3)).copy()
        cv2.rectangle(arr, (8, 8), (190, 38), (0, 0, 0), -1)
        cv2.putText(arr, label, (14, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2, cv2.LINE_AA)
        return arr.tobytes()


class OneASecondEncoder:
    """Encode frames at `1 fps` (muted, `<80 MB` parts) named `<stem>.1fps.<first:05d>-<last:05d>.mp4`."""

    def __init__(self, stem: Path, size: tuple[int, int]):
        self.stem = Path(stem)
        self.size = (int(size[0]), int(size[1]))
        self.per_part = max(1, int(ONE_A_SECOND_BYTES / (ONE_A_SECOND_COST * self.size[0] * self.size[1])))
        self.proc: subprocess.Popen[bytes] | None = None
        self.tmp: Path | None = None
        self.first: int | None = None
        self.last: int | None = None
        self.count = 0
        self.parts: list[dict[str, Any]] = []
        self.code = 0

    def _open(self, source_frame: int) -> None:
        self.first = source_frame
        self.count = 0
        self.tmp = self.stem.with_name(f"{self.stem.name}.1fps.part.mp4")
        cmd = [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-threads",
            "2",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{self.size[0]}x{self.size[1]}",
            "-r",
            "1",
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(self.tmp),
        ]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def _shut(self) -> int:
        assert self.proc is not None and self.tmp is not None and self.first is not None and self.last is not None
        if self.proc.stdin:
            self.proc.stdin.close()
        code = self.proc.wait()
        name = self.stem.with_name(f"{self.stem.name}.1fps.{self.first:05d}-{self.last:05d}.mp4")
        self.tmp.replace(name)
        size = name.stat().st_size
        self.parts.append({"file": str(name), "frames": [self.first, self.last], "bytes": size})
        self.proc = None
        return code

    def write(self, rgb_bytes: bytes, source_frame: int) -> None:
        if self.proc is not None and self.count >= self.per_part:
            self.code = self.code or self._shut()
        if self.proc is None:
            self._open(source_frame)
        assert self.proc is not None and self.proc.stdin is not None
        self.proc.stdin.write(rgb_bytes)
        self.last = source_frame
        self.count += 1

    def close(self) -> tuple[int, list[dict[str, Any]]]:
        if self.proc is not None:
            self.code = self.code or self._shut()
        return self.code, self.parts


def cmd_encode_1fps(args: argparse.Namespace) -> int:
    """Encode a video (or `[--first..--last]` span) into `<80 MB` `.1fps.<first:05d>-<last:05d>.mp4` companions."""
    video_path = Path(args.video)
    if not video_path.is_file():
        raise FileNotFoundError(f"video file not found: {video_path}")
    w, h, total_frames, fps = _probe_video(video_path)
    first = int(args.first) if args.first is not None else 0
    last = int(args.last) if args.last is not None else max(0, total_frames - 1)
    if last < first or first < 0:
        raise ValueError(f"invalid frame span [{first}..{last}]")
    count = last - first + 1

    out_dir = Path(args.out_dir) if args.out_dir else video_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / video_path.stem

    vf_parts = [f"select=gte(n\\,{first})"] if first > 0 else []
    cmd = ["ffmpeg", "-v", "error", "-threads", "2", "-i", str(video_path), "-map", "0:v:0"]
    if vf_parts:
        cmd.extend(["-vf", ",".join(vf_parts)])
    cmd.extend(["-fps_mode", "passthrough", "-frames:v", str(count), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])

    frame_bytes_len = w * h * 3
    enc = OneASecondEncoder(stem, (w, h))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=frame_bytes_len)
    try:
        idx = 0
        while idx < count:
            assert proc.stdout is not None
            buf = proc.stdout.read(frame_bytes_len)
            if len(buf) < frame_bytes_len:
                break
            frame_num = first + idx
            if args.burn_frame_numbers:
                buf = _burn_frame_label(buf, w, h, frame_num)
            enc.write(buf, frame_num)
            idx += 1
    finally:
        if proc.stdout:
            proc.stdout.close()
        proc.wait()

    code, parts = enc.close()
    if code != 0:
        raise RuntimeError(f"ffmpeg 1fps encoder exited with code {code}")
    print(
        json.dumps(
            {
                "source_video": str(video_path),
                "canvas": [w, h],
                "source_fps": fps,
                "first_frame": first,
                "last_frame": first + max(0, idx - 1),
                "encoded_frames": idx,
                "burn_frame_numbers": bool(args.burn_frame_numbers),
                "parts": parts,
            },
            indent=2,
        )
    )
    return 0


def cmd_crop(args: argparse.Namespace) -> int:
    """Crop a pixel region (`--box`) or `0..1000` normalized region (`--box-1000`) for `$0` native `read_file` QA."""
    img_path = Path(args.image)
    if not img_path.is_file():
        raise FileNotFoundError(f"image not found: {img_path}")
    w, h = _image_size(img_path)

    if args.box_1000:
        vals = [float(v.strip()) for v in args.box_1000.split(",")]
        d = descale_box_2d(vals, w, h)
        x1, y1, x2, y2 = [int(round(v)) for v in d["box_xyxy_px"]]
    elif args.box:
        vals = [float(v.strip()) for v in args.box.split(",")]
        if len(vals) != 4:
            raise ValueError("--box must be x1,y1,x2,y2")
        x1, y1, x2, y2 = [int(round(v)) for v in vals]
    else:
        raise ValueError("either --box x1,y1,x2,y2 or --box-1000 ymin,xmin,ymax,xmax is required")

    x1 = max(0, min(w - 1, x1))
    y1 = max(0, min(h - 1, y1))
    x2 = max(x1 + 1, min(w, x2))
    y2 = max(y1 + 1, min(h, y2))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        with Image.open(img_path) as im:
            cropped = im.crop((x1, y1, x2, y2))
            cropped.save(out_path)
    except Exception:
        import cv2
        img = cv2.imread(str(img_path))
        if img is None:
            raise ValueError(f"cannot read image from {img_path}")
        cv2.imwrite(str(out_path), img[y1:y2, x1:x2])

    print(
        json.dumps(
            {
                "source_image": str(img_path),
                "canvas": [w, h],
                "crop_box_xyxy_px": [x1, y1, x2, y2],
                "crop_size": [x2 - x1, y2 - y1],
                "output_path": str(out_path),
            },
            indent=2,
        )
    )
    return 0


def _upload_file(path: Path) -> str:
    res = subprocess.run(
        ["gemini-api", "files", "upload", str(path), "--wait"],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"gemini-api files upload failed ({res.returncode}): {res.stderr.strip()}")
    return res.stdout.strip().splitlines()[-1].strip()


def _delete_file(file_id: str) -> None:
    subprocess.run(
        ["gemini-api", "files", "delete", file_id],
        capture_output=True,
        text=True,
        check=False,
    )


def _resolve_video_id(target: str, dry_run: bool, uploaded: list[str], tag: str = "vid01") -> str:
    if target.startswith("files/"):
        return target
    if dry_run:
        clean_id = "".join(c for c in Path(target).stem.lower() if c.isalnum()) or tag
        return f"files/dryrun{clean_id}"
    p = Path(target)
    if not p.is_file():
        raise FileNotFoundError(f"video file not found and not a files/<id> URI: {target}")
    fid = _upload_file(p)
    uploaded.append(fid)
    return fid


def _image_part(path: Path, resolution: str, dry_run: bool, uploaded: list[str]) -> dict[str, Any]:
    mime = _mime_of(path, "image/png")
    if dry_run:
        clean_id = "".join(c for c in path.stem.lower() if c.isalnum()) or "img01"
        return {
            "type": "image",
            "uri": f"https://generativelanguage.googleapis.com/v1beta/files/dryrun{clean_id}",
            "mime_type": mime,
            "resolution": resolution,
        }
    if path.stat().st_size <= INLINE_MAX_BYTES:
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return {
            "type": "image",
            "data": b64,
            "mime_type": mime,
            "resolution": resolution,
        }
    fid = _upload_file(path)
    uploaded.append(fid)
    return {
        "type": "image",
        "uri": f"https://generativelanguage.googleapis.com/v1beta/{fid}",
        "mime_type": mime,
        "resolution": resolution,
    }


def _run_agent(
    model: str,
    body: dict[str, Any],
    dry_run: bool,
    previous_interaction_id: str | None = None,
) -> dict[str, Any]:
    cmd = [
        "gemini-api",
        "agent",
        "run",
        "-m",
        model,
        "--stream=false",
        "-o",
        "json",
    ]
    if previous_interaction_id:
        cmd.extend(["--previous-interaction-id", previous_interaction_id])
    if dry_run:
        cmd.append("--dry-run")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump(body, tf)
        body_path = tf.name
    try:
        cmd.extend(["--body", f"@{body_path}"])
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise RuntimeError(f"gemini-api agent run failed ({res.returncode}): {res.stderr.strip()}")
        return json.loads(res.stdout)
    finally:
        Path(body_path).unlink(missing_ok=True)


def _extract_output_text(resp: dict[str, Any]) -> str:
    if "output_text" in resp and isinstance(resp["output_text"], str):
        return resp["output_text"]
    for step in reversed(resp.get("steps") or []):
        if step.get("type") == "model_output":
            for block in step.get("content") or []:
                if block.get("type") == "text" and block.get("text"):
                    return str(block["text"])
    return ""


def cmd_boxes(args: argparse.Namespace) -> int:
    img_path = Path(args.image)
    if not args.dry_run and not img_path.is_file():
        raise FileNotFoundError(f"image not found: {img_path}")
    match_path_str = args.match_boxes or args.people
    if args.target_size:
        w_str, h_str = args.target_size.lower().split("x", 1)
        target_w, target_h = int(w_str), int(h_str)
    elif img_path.is_file():
        target_w, target_h = _image_size(img_path)
    else:
        target_w, target_h = 1024, 768

    uploaded: list[str] = []
    try:
        inputs: list[dict[str, Any]] = []
        if args.ref:
            ref_path = Path(args.ref)
            inputs.append(_image_part(ref_path, "low", args.dry_run, uploaded))
        inputs.append(_image_part(img_path, args.resolution, args.dry_run, uploaded))

        schema_props: dict[str, Any] = {
            "box_2d": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "The 2D bounding box as [ymin, xmin, ymax, xmax] normalized to 0-1000.",
            },
            "label": {
                "type": "string",
                "description": "Descriptive label for the detected subject or object.",
            },
        }
        req_fields = ["box_2d", "label"]
        if args.with_masks:
            schema_props["mask"] = {
                "type": "array",
                "items": {"type": "array", "items": {"type": "integer"}},
                "description": "Polygon segmentation mask as [[x, y], ...] normalized to 0-1000.",
            }
            req_fields.append("mask")

        prompt_suffix = (
            " Return JSON with `boxes`, where each entry has `box_2d` as "
            "[ymin, xmin, ymax, xmax] normalized to 0-1000"
            + (", `mask` as a polygon of [x, y] normalized to 0-1000," if args.with_masks else "")
            + " and `label`."
        )
        inputs.append({"type": "text", "text": args.prompt.strip() + prompt_suffix})

        body: dict[str, Any] = {
            "input": inputs,
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "boxes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": schema_props,
                                "required": req_fields,
                            },
                        }
                    },
                    "required": ["boxes"],
                },
            },
        }
        if args.with_masks:
            body["generation_config"] = {"thinking_level": "minimal"}

        resp = _run_agent(args.model, body, args.dry_run)
        if args.dry_run:
            print(json.dumps(resp, indent=2))
            return 0

        raw_text = _extract_output_text(resp)
        parsed = json.loads(raw_text) if raw_text else {"boxes": []}
        enriched = []
        for item in parsed.get("boxes") or []:
            entry = descale_box_2d(item["box_2d"], target_w, target_h)
            entry["label"] = item.get("label", "")
            if args.with_masks and "mask" in item:
                entry["mask_polygon_px"] = descale_polygon(item["mask"], target_w, target_h)
            if match_path_str:
                entry["detector_match"] = match_detector_boxes(
                    entry["box_ltwh_px"],
                    (target_w, target_h),
                    Path(match_path_str),
                    args.frame,
                )
            enriched.append(entry)

        print(json.dumps({"canvas": [target_w, target_h], "boxes": enriched}, indent=2))
        return 0
    finally:
        for fid in uploaded:
            _delete_file(fid)


def cmd_slice(args: argparse.Namespace) -> int:
    _check_native_first(args.video, args.force_api, args.dry_run)
    fps = _resolve_fps(args.video, args.fps, default_fps=24.0)
    start_s, end_s = frame_span_to_offsets(args.first, args.last, fps)
    uploaded: list[str] = []
    try:
        file_id = _resolve_video_id(args.video, args.dry_run, uploaded, tag="slice01")
        body = {
            "input": [
                {
                    "type": "video",
                    "uri": f"https://generativelanguage.googleapis.com/v1beta/{file_id}",
                    "mime_type": "video/mp4",
                    "resolution": args.resolution,
                    "processing": {
                        "type": "static",
                        "start_offset": start_s,
                        "end_offset": end_s,
                        "fps": fps,
                    },
                },
                {
                    "type": "text",
                    "text": args.prompt,
                },
            ]
        }
        resp = _run_agent(args.model, body, args.dry_run)
        print(json.dumps(resp, indent=2))
        return 0
    finally:
        for fid in uploaded:
            _delete_file(fid)


def cmd_agentic_video(args: argparse.Namespace) -> int:
    _check_not_stacked_for_agentic(args.video)
    _check_native_first(args.video, args.force_api, args.dry_run)
    compare_target = args.compare_clip or args.compare_shot
    if compare_target and not compare_target.startswith("files/"):
        _check_native_first(compare_target, args.force_api, args.dry_run)

    uploaded: list[str] = []
    try:
        master_id = _resolve_video_id(args.video, args.dry_run, uploaded, tag="master01")
        inputs: list[dict[str, Any]] = [
            {
                "type": "video",
                "uri": f"https://generativelanguage.googleapis.com/v1beta/{master_id}",
                "mime_type": "video/mp4",
                "processing": "agentic",
            }
        ]
        if compare_target:
            comp_fps = _resolve_fps(compare_target, args.compare_fps, default_fps=24.0)
            shot_id = _resolve_video_id(compare_target, args.dry_run, uploaded, tag="clip01")
            shot_proc: dict[str, Any] = {"type": "static", "fps": comp_fps}
            if args.compare_first is not None and args.compare_last is not None:
                s0, s1 = frame_span_to_offsets(args.compare_first, args.compare_last, comp_fps)
                shot_proc["start_offset"] = s0
                shot_proc["end_offset"] = s1
            inputs.append(
                {
                    "type": "video",
                    "uri": f"https://generativelanguage.googleapis.com/v1beta/{shot_id}",
                    "mime_type": "video/mp4",
                    "resolution": args.compare_resolution,
                    "processing": shot_proc,
                }
            )
        inputs.append({"type": "text", "text": args.prompt})
        body: dict[str, Any] = {"input": inputs}
        resp = _run_agent(
            args.model,
            body,
            args.dry_run,
            previous_interaction_id=args.previous_interaction_id,
        )
        if args.dry_run:
            print(json.dumps(resp, indent=2))
            return 0

        steps = resp.get("steps") or []
        proc_calls = [s for s in steps if s.get("type") in ("processing_call", "processing_result")]
        summary = {
            "interaction_id": resp.get("id"),
            "processing_steps_count": len(proc_calls),
            "processing_steps": proc_calls,
            "output_text": _extract_output_text(resp),
            "usage": resp.get("usage"),
        }
        print(json.dumps(summary, indent=2))
        return 0
    finally:
        for fid in uploaded:
            _delete_file(fid)


def cmd_zoom(args: argparse.Namespace) -> int:
    img_path = Path(args.image)
    uploaded: list[str] = []
    try:
        img_part = _image_part(img_path, args.resolution, args.dry_run, uploaded)
        body = {
            "input": [
                img_part,
                {"type": "text", "text": args.prompt},
            ],
            "tools": [{"type": "code_execution"}],
        }
        resp = _run_agent(args.model, body, args.dry_run)
        print(json.dumps(resp, indent=2))
        return 0
    finally:
        for fid in uploaded:
            _delete_file(fid)


def cmd_transcribe_spans(args: argparse.Namespace) -> int:
    _check_native_first(args.video, args.force_api, args.dry_run)
    fps = _resolve_fps(args.video, args.fps, default_fps=24.0)
    uploaded: list[str] = []
    try:
        file_id = _resolve_video_id(args.video, args.dry_run, uploaded, tag="audio01")
        video_part: dict[str, Any] = {
            "type": "video",
            "uri": f"https://generativelanguage.googleapis.com/v1beta/{file_id}",
            "mime_type": _mime_of(Path(args.video), "video/mp4"),
        }
        proc: dict[str, Any] = {"type": "static"}
        if args.visual_speakers:
            video_part["resolution"] = "high"
            proc["fps"] = fps
        if args.slice_master and args.shot_last is not None:
            s0, s1 = frame_span_to_offsets(args.shot_first, args.shot_last, fps)
            proc["start_offset"] = s0
            proc["end_offset"] = s1
        video_part["processing"] = proc

        prompt_text = (
            args.prompt.strip()
            + " Return JSON with `segments`, where each segment has `speaker` (describing "
            "which person or voice is speaking/singing), `start_time` and `end_time` in "
            "`MM:SS.mmm` format (relative to the start of the clip/slice), `text` (exact "
            "spoken or sung words), and `mouth_visibly_open` (boolean)."
        )
        body: dict[str, Any] = {
            "input": [
                video_part,
                {"type": "text", "text": prompt_text},
            ],
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "segments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "speaker": {"type": "string"},
                                    "start_time": {"type": "string"},
                                    "end_time": {"type": "string"},
                                    "text": {"type": "string"},
                                    "mouth_visibly_open": {"type": "boolean"},
                                },
                                "required": [
                                    "speaker",
                                    "start_time",
                                    "end_time",
                                    "text",
                                    "mouth_visibly_open",
                                ],
                            },
                        }
                    },
                    "required": ["segments"],
                },
            },
        }
        resp = _run_agent(args.model, body, args.dry_run)
        if args.dry_run:
            print(json.dumps(resp, indent=2))
            return 0

        raw_text = _extract_output_text(resp)
        parsed = json.loads(raw_text) if raw_text else {"segments": []}
        enriched_segments: list[dict[str, Any]] = []
        for seg in parsed.get("segments") or []:
            f0, f1 = timestamp_span_to_frames(
                seg.get("start_time", "00:00"),
                seg.get("end_time", "00:00"),
                shot_first=args.shot_first,
                fps=fps,
                shot_last=args.shot_last,
            )
            enriched_segments.append(
                {
                    "speaker": seg.get("speaker", ""),
                    "start_time": seg.get("start_time", ""),
                    "end_time": seg.get("end_time", ""),
                    "start_frame": f0,
                    "end_frame": f1,
                    "frame_count": f1 - f0 + 1,
                    "mouth_visibly_open": bool(seg.get("mouth_visibly_open", True)),
                    "text": seg.get("text", ""),
                }
            )
        out = {
            "shot_first": args.shot_first,
            "shot_last": args.shot_last,
            "fps": fps,
            "visual_speakers": bool(args.visual_speakers),
            "segments": enriched_segments,
        }
        print(json.dumps(out, indent=2))
        return 0
    finally:
        for fid in uploaded:
            _delete_file(fid)


def run_self_test() -> int:
    # 1. Verify [ymin, xmin, ymax, xmax] -> [x1, y1, x2, y2] and [left, top, width, height]
    d = descale_box_2d([250, 500, 750, 750], 1024, 768)
    assert d["box_xyxy_px"] == [512.0, 192.0, 768.0, 576.0], d
    assert d["box_ltwh_px"] == [512.0, 192.0, 256.0, 384.0], d
    poly = descale_polygon([[500, 250], [750, 750]], 1920, 1080)
    assert poly == [[960.0, 270.0], [1440.0, 810.0]], poly

    # 2. Verify frame-span offset math and timestamp-to-frame math across 24 and 30 fps
    s0, s1 = frame_span_to_offsets(1200, 1271, 24.0)
    assert s0 == 50.0 and s1 == 53.0, (s0, s1)
    s30_0, s30_1 = frame_span_to_offsets(0, 29, 30.0)
    assert s30_0 == 0.0 and s30_1 == 1.0, (s30_0, s30_1)
    assert parse_timestamp_seconds("01:02.500") == 62.5
    f0, f1 = timestamp_span_to_frames("00:00.500", "00:01.250", shot_first=1000, fps=24.0, shot_last=1050)
    assert (f0, f1) == (1012, 1030), (f0, f1)

    # 3. Verify local JSON & bit-packed .npz detector IoU matching, crop, encode-1fps, and refusal guards
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        json_det = td_path / "detections.json"
        json_det.write_text(
            json.dumps({"boxes": [{"frame": 10, "box_ltwh": [512, 192, 256, 384]}]}),
            encoding="utf-8",
        )
        jm = match_detector_boxes(d["box_ltwh_px"], (1024, 768), json_det, 10)
        assert jm["passes_0_50_gate"] is True and jm["best_iou"] == 1.0, jm

        try:
            import numpy as np

            npz_path = td_path / "detections.npz"
            mask = np.zeros((768, 1024), dtype=bool)
            mask[192:576, 512:768] = True
            packed = np.packbits(mask, axis=-1)[None, ...]
            np.savez_compressed(
                npz_path,
                masks=packed,
                frame=np.array([10], dtype=np.int32),
                first=np.array(100, dtype=np.int32),
            )
            (td_path / "detections.json").write_text(
                json.dumps({"canvas": [1024, 768]}), encoding="utf-8"
            )
            m = match_detector_boxes(d["box_ltwh_px"], (1024, 768), npz_path, 110)
            assert m["passes_0_50_gate"] is True, m
            assert m["best_iou"] == 1.0, m
            assert m["matched_box_ltwh"] == [512, 192, 256, 384], m
        except ImportError:
            pass

        # Test local crop helper
        try:
            from PIL import Image
            test_img = td_path / "scene.png"
            Image.new("RGB", (400, 300), color=(30, 60, 90)).save(test_img)
            crop_out = td_path / "crop.png"
            rc = build_parser().parse_args(
                ["crop", str(test_img), "--box", "50,40,250,190", "--out", str(crop_out)]
            )
            assert rc.func(rc) == 0 and crop_out.is_file()
            assert _image_size(crop_out) == (200, 150)
        except ImportError:
            pass

        # Test local encode-1fps helper if ffmpeg and ffprobe are on PATH
        if shutil.which("ffmpeg") and shutil.which("ffprobe"):
            tiny_mp4 = td_path / "sample.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=navy:s=160x120:r=24:d=0.25",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    str(tiny_mp4),
                ],
                check=True,
            )
            enc_args = build_parser().parse_args(
                ["encode-1fps", str(tiny_mp4), "--burn-frame-numbers"]
            )
            assert enc_args.func(enc_args) == 0
            companions = _find_1fps_companions(tiny_mp4)
            assert len(companions) == 1 and companions[0].is_file(), companions

        # Native-First Gate must refuse a <100 MB local .mp4 when a .1fps.*.mp4 sibling exists
        clip_24 = td_path / "clip.mp4"
        clip_1fps = td_path / "clip.1fps.00000-00024.mp4"
        clip_24.write_bytes(b"00" * 1024)
        clip_1fps.write_bytes(b"00" * 1024)
        try:
            _check_native_first(str(clip_24), force_api=False, dry_run=False)
            raise AssertionError("expected _check_native_first to refuse when .1fps sibling exists")
        except ValueError as exc:
            assert "Native-First (agy) Gate refused" in str(exc), exc

        # Multi-panel / STACKED refusal guard on agentic-video
        try:
            _check_not_stacked_for_agentic("comparison_STACKED.mp4")
            raise AssertionError("expected _check_not_stacked_for_agentic to refuse *_STACKED*")
        except ValueError as exc:
            assert "BANNED" in str(exc), exc

    # 4. Verify gemini-api --dry-run schemas across all 5 API subcommands (if gemini-api CLI is installed)
    if shutil.which("gemini-api"):
        for sub_argv in [
            ["boxes", "frame.png", "--prompt", "Detect object", "--with-masks", "--dry-run"],
            ["slice", "files/abc123", "--first", "120", "--last", "180", "--prompt", "Inspect slice", "--dry-run"],
            [
                "agentic-video",
                "master_video.mp4",
                "--compare-clip",
                "candidate_clip.mp4",
                "--prompt",
                "Compare continuity",
                "--dry-run",
            ],
            ["zoom", "contact_sheet.jpg", "--prompt", "Zoom into tiles", "--dry-run"],
            [
                "transcribe-spans",
                "dialogue.mp4",
                "--shot-first",
                "0",
                "--shot-last",
                "120",
                "--visual-speakers",
                "--dry-run",
            ],
        ]:
            p = build_parser().parse_args(sub_argv)
            rc = p.func(p)
            assert rc == 0, f"dry-run failed for {sub_argv}"

    print(
        "ok    gemini_media.py self-test passed "
        "(descaling, FPS offsets, timestamps, detector IoU, crop, encode-1fps, Native-First & STACKED guards, CLI dry-runs)"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true", help="Run deterministic unit and dry-run tests")
    sub = ap.add_subparsers(dest="subcommand")

    p_1fps = sub.add_parser(
        "encode-1fps",
        help="Encode <80 MB .1fps.<first>-<last>.mp4 companions for $0 native read_file every-frame inspection",
    )
    p_1fps.add_argument("video", help="Source video path (.mp4, .mkv, .mov)")
    p_1fps.add_argument("--first", type=int, help="Optional inclusive start frame number (default: 0)")
    p_1fps.add_argument("--last", type=int, help="Optional inclusive end frame number (default: last frame)")
    p_1fps.add_argument("--burn-frame-numbers", action="store_true", help="Burn source frame numbers into top-left corner")
    p_1fps.add_argument("--out-dir", help="Optional output directory (default: alongside source video)")
    p_1fps.set_defaults(func=cmd_encode_1fps)

    p_crop = sub.add_parser(
        "crop",
        help="Crop a pixel box (--box) or 0..1000 box (--box-1000) to a local PNG for $0 read_file inspection",
    )
    p_crop.add_argument("image", help="Source image path")
    p_crop.add_argument("--box", help="Pixel crop coordinates as x1,y1,x2,y2")
    p_crop.add_argument("--box-1000", help="Normalized 0..1000 crop coordinates as ymin,xmin,ymax,xmax")
    p_crop.add_argument("--out", required=True, help="Output cropped PNG path (e.g., /tmp/crop.png)")
    p_crop.set_defaults(func=cmd_crop)

    p_boxes = sub.add_parser("boxes", help="2D box / polygon mask grounding + optional local detector IoU snap")
    p_boxes.add_argument("image", help="Scene frame image path")
    p_boxes.add_argument("--ref", help="Optional reference still to locate a specific person or object")
    p_boxes.add_argument("--prompt", required=True, help="Detection prompt")
    p_boxes.add_argument("--match-boxes", help="Optional local detections (.json or bit-packed .npz) to match by IoU")
    p_boxes.add_argument("--people", help=argparse.SUPPRESS)
    p_boxes.add_argument("--frame", type=int, help="Source frame number when --match-boxes points to a multi-frame file")
    p_boxes.add_argument("--target-size", help="Target WxH coordinate space (default: input image dimensions)")
    p_boxes.add_argument("--with-masks", action="store_true", help="Also request polygon segmentation masks")
    p_boxes.add_argument("--resolution", default="high", choices=["low", "medium", "high", "ultra_high"])
    p_boxes.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    p_boxes.add_argument("--dry-run", action="store_true", help="Preview request JSON via gemini-api --dry-run")
    p_boxes.set_defaults(func=cmd_boxes)

    p_slice = sub.add_parser("slice", help="Inspect a [first..last] frame slice on a video via static start_offset/end_offset")
    p_slice.add_argument("video", help="Uploaded files/<id> or local .mp4 path")
    p_slice.add_argument("--first", type=int, required=True, help="Inclusive start frame number")
    p_slice.add_argument("--last", type=int, required=True, help="Inclusive end frame number")
    p_slice.add_argument("--fps", type=float, help="Frame rate (default: auto-probed via ffprobe, or 24.0)")
    p_slice.add_argument("--prompt", required=True, help="Inspection prompt")
    p_slice.add_argument("--resolution", default="high", choices=["low", "medium", "high"])
    p_slice.add_argument("--force-api", action="store_true", help="Override Native-First Gate even if a .1fps.mp4 sibling exists")
    p_slice.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    p_slice.add_argument("--dry-run", action="store_true", help="Preview request JSON via gemini-api --dry-run")
    p_slice.set_defaults(func=cmd_slice)

    p_agentic = sub.add_parser(
        "agentic-video",
        help="Opt-in agentic video timeline navigation on >100 MB single-canvas videos (+ optional --compare-clip)",
    )
    p_agentic.add_argument("video", help="Uploaded files/<id> or local single-canvas master video .mp4")
    p_agentic.add_argument("--compare-clip", help="Optional second video (candidate clip) inspected in static high-res mode")
    p_agentic.add_argument("--compare-shot", help=argparse.SUPPRESS)
    p_agentic.add_argument("--compare-first", type=int, help="Optional start frame on --compare-clip")
    p_agentic.add_argument("--compare-last", type=int, help="Optional end frame on --compare-clip")
    p_agentic.add_argument("--compare-fps", type=float, help="Frame rate for --compare-clip (default: auto-probed or 24.0)")
    p_agentic.add_argument("--compare-resolution", default="high", choices=["low", "medium", "high"])
    p_agentic.add_argument("--previous-interaction-id", help="Stateful multi-turn follow-up interaction ID")
    p_agentic.add_argument("--prompt", required=True, help="Timeline query or continuity comparison prompt")
    p_agentic.add_argument("--force-api", action="store_true", help="Override Native-First Gate even if a .1fps.mp4 sibling exists")
    p_agentic.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    p_agentic.add_argument("--dry-run", action="store_true", help="Preview request JSON via gemini-api --dry-run")
    p_agentic.set_defaults(func=cmd_agentic_video)

    p_zoom = sub.add_parser("zoom", help="Agentic code-execution zoom-and-inspect on contact sheets or diagnostic grids")
    p_zoom.add_argument("image", help="Contact sheet or dense grid image path")
    p_zoom.add_argument("--prompt", required=True, help="Inspection prompt")
    p_zoom.add_argument("--resolution", default="ultra_high", choices=["high", "ultra_high"])
    p_zoom.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    p_zoom.add_argument("--dry-run", action="store_true", help="Preview request JSON via gemini-api --dry-run")
    p_zoom.set_defaults(func=cmd_zoom)

    p_trans = sub.add_parser(
        "transcribe-spans",
        help="Speaker/dialogue transcription converted to inclusive [start_frame, end_frame] spans",
    )
    p_trans.add_argument("video", help="Uploaded files/<id> or local .mp4/.wav path")
    p_trans.add_argument("--shot-first", type=int, default=0, help="Source frame corresponding to clip start (default: 0)")
    p_trans.add_argument("--shot-last", type=int, help="Optional inclusive end frame of the clip")
    p_trans.add_argument("--slice-master", action="store_true", help="Apply start_offset/end_offset using --shot-first/--shot-last on a full master video")
    p_trans.add_argument("--fps", type=float, help="Frame rate (default: auto-probed via ffprobe, or 24.0)")
    p_trans.add_argument(
        "--visual-speakers",
        action="store_true",
        help="Inspect video at high resolution alongside audio to attribute speech/vocals to specific on-screen people",
    )
    p_trans.add_argument(
        "--prompt",
        default="Transcribe all spoken and sung lines with accurate timestamps and identify which speaker is active.",
        help="Transcription prompt",
    )
    p_trans.add_argument("--force-api", action="store_true", help="Override Native-First Gate even if a .1fps.mp4 sibling exists")
    p_trans.add_argument("-m", "--model", default=DEFAULT_MODEL, help=f"Model name (default: {DEFAULT_MODEL})")
    p_trans.add_argument("--dry-run", action="store_true", help="Preview request JSON via gemini-api --dry-run")
    p_trans.set_defaults(func=cmd_transcribe_spans)

    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()
    if args.self_test:
        return run_self_test()
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
