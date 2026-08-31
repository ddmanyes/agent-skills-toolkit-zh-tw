#!/usr/bin/env python3
"""Transcribe one video into TXT, SRT, and JSON with faster-whisper."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


def timestamp(seconds: float, separator: str = ",") -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1_000)
    return f"{hours:02}:{minutes:02}:{secs:02}{separator}{milliseconds:03}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe a local video with faster-whisper."
    )
    parser.add_argument("source", type=Path, help="Input video or audio file")
    parser.add_argument("output_dir", type=Path, help="Directory for transcript files")
    parser.add_argument("--model", default="small", help="Whisper model name or path")
    parser.add_argument(
        "--language",
        default="zh",
        help="Language code, or 'auto' for automatic detection",
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cuda", "cpu"),
        default="auto",
        help="Inference device; auto tries CUDA then CPU",
    )
    parser.add_argument("--compute-type", default=None)
    parser.add_argument("--beam-size", type=int, default=3)
    parser.add_argument("--cpu-threads", type=int, default=16)
    parser.add_argument("--initial-prompt", default="")
    parser.add_argument("--no-vad", action="store_true")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing TXT, SRT, and JSON outputs",
    )
    return parser.parse_args()


def device_candidates(args: argparse.Namespace) -> list[tuple[str, str]]:
    if args.device == "cuda":
        return [("cuda", args.compute_type or "float16")]
    if args.device == "cpu":
        return [("cpu", args.compute_type or "int8")]
    if shutil.which("nvidia-smi"):
        return [("cuda", args.compute_type or "float16"), ("cpu", "int8")]
    return [("cpu", args.compute_type or "int8")]


def transcribe(
    args: argparse.Namespace, device: str, compute_type: str
) -> tuple[Any, list[dict[str, Any]]]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit(
            "faster-whisper is required. Install it in an isolated environment: "
            "python -m pip install faster-whisper"
        ) from exc

    model = WhisperModel(
        args.model,
        device=device,
        compute_type=compute_type,
        cpu_threads=args.cpu_threads,
    )
    segments, info = model.transcribe(
        str(args.source),
        language=None if args.language == "auto" else args.language,
        beam_size=args.beam_size,
        vad_filter=not args.no_vad,
        condition_on_previous_text=True,
        initial_prompt=args.initial_prompt or None,
    )

    rows: list[dict[str, Any]] = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        row = {
            "start": segment.start,
            "end": segment.end,
            "text": text,
            "avg_logprob": segment.avg_logprob,
            "no_speech_prob": segment.no_speech_prob,
        }
        rows.append(row)
        print(f"[{timestamp(segment.start)}] {text}", flush=True)
    return info, rows


def write_outputs(
    source: Path, output_dir: Path, info: Any, rows: list[dict[str, Any]]
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem

    payload = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "segments": rows,
    }
    (output_dir / f"{stem}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / f"{stem}.txt").write_text(
        "\n".join(f"[{timestamp(row['start'])}] {row['text']}" for row in rows)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    srt_blocks = []
    for index, row in enumerate(rows, 1):
        srt_blocks.append(
            f"{index}\n{timestamp(row['start'])} --> {timestamp(row['end'])}\n"
            f"{row['text']}\n"
        )
    (output_dir / f"{stem}.srt").write_text(
        "\n".join(srt_blocks),
        encoding="utf-8-sig",
        newline="\n",
    )


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    source = args.source.resolve()
    if not source.is_file():
        print(f"Input file does not exist: {source}", file=sys.stderr)
        return 2

    output_dir = args.output_dir.resolve()
    output_paths = [output_dir / f"{source.stem}.{suffix}" for suffix in ("json", "txt", "srt")]
    existing_outputs = [path for path in output_paths if path.exists()]
    if existing_outputs and not args.overwrite:
        print(
            "Output files already exist; use --overwrite to replace them:\n- "
            + "\n- ".join(str(path) for path in existing_outputs),
            file=sys.stderr,
        )
        return 3

    failures = []
    for device, compute_type in device_candidates(args):
        try:
            info, rows = transcribe(args, device, compute_type)
            if not rows:
                raise RuntimeError("Transcription produced no text segments")
            write_outputs(source, output_dir, info, rows)
            print(f"Completed with device={device}, compute_type={compute_type}")
            return 0
        except RuntimeError as exc:
            failures.append(f"{device}/{compute_type}: {exc}")
            if args.device != "auto":
                break
            print(
                f"Transcription failed on {device}; trying the next device.",
                file=sys.stderr,
            )

    print("Transcription failed:\n- " + "\n- ".join(failures), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
