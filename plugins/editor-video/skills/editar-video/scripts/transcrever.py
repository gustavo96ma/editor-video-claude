#!/usr/bin/env python3
"""Transcribe a video with word-level timestamps (for word-by-word captions).

Usage:
    python transcrever.py <video> <output-dir> [--lang pt] [--model small]

Writes into <output-dir>:
    palavras.json      [{"palavra", "inicio", "fim"}] in seconds
    transcricao.txt    plain text, one sentence per line, for the person to review
    transcricao.srt    sentence-level subtitles (editable in CapCut, Premiere, DaVinci)

Requires ffmpeg and the faster-whisper package (pip install faster-whisper).
The model is downloaded on first use (small is about 500 MB) and runs on the CPU.
"""

import argparse
import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("transcrever")

MAX_LINE_CHARS = 20
MAX_GAP_S = 0.6


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def group_words(words):
    """Split into caption blocks of up to 2 lines of MAX_LINE_CHARS, breaking at
    punctuation or pauses so each block reads as a unit of meaning."""
    blocks, current = [], []
    for w in words:
        text = " ".join(x["palavra"] for x in current + [w])
        gap = w["inicio"] - current[-1]["fim"] if current else 0
        if current and (len(text) > 2 * MAX_LINE_CHARS or gap > MAX_GAP_S):
            blocks.append(current)
            current = []
        current.append(w)
        if re.search(r"[.!?]$", w["palavra"]):
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def two_lines(text):
    if len(text) <= MAX_LINE_CHARS:
        return text
    words = text.split()
    best, best_diff = text, None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        diff = abs(len(a) - len(b))
        if best_diff is None or diff < best_diff:
            best, best_diff = f"{a}\n{b}", diff
    return best


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("out_dir")
    parser.add_argument("--lang", default="pt")
    parser.add_argument("--model", default="small", help="tiny, base, small, medium (larger = slower and better)")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        log.error("ffmpeg not found")
        return 2
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        log.error("faster-whisper not installed. Run: python -m pip install faster-whisper (Windows: py -m pip install faster-whisper)")
        return 2

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.wav"
        proc = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(Path(args.video).expanduser()),
                               "-vn", "-ac", "1", "-ar", "16000", str(wav)],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            log.error("could not extract audio: %s", proc.stderr[-500:])
            return 1
        log.info("loading model %s (first run downloads it)", args.model)
        model = WhisperModel(args.model, device="cpu", compute_type="int8")
        # Decode the WAV ourselves: faster-whisper's own decoder (PyAV) breaks across versions.
        import wave

        import numpy as np
        with wave.open(str(wav), "rb") as wf:
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        segments, info = model.transcribe(audio, language=args.lang, word_timestamps=True, vad_filter=True)
        words = []
        for seg in segments:
            for w in seg.words or []:
                text = w.word.strip()
                if text:
                    words.append({"palavra": text, "inicio": round(w.start, 3), "fim": round(w.end, 3)})
        log.info("transcribed %.1f s, %d words", info.duration, len(words))

    if not words:
        log.error("no speech found")
        return 1

    blocks = group_words(words)
    lines = ",\n".join(json.dumps(w, ensure_ascii=False) for w in words)
    (out_dir / "palavras.json").write_text(f"[\n{lines}\n]\n", encoding="utf-8")
    sentences, line = [], []
    for w in words:
        line.append(w["palavra"])
        if re.search(r"[.!?]$", w["palavra"]):
            sentences.append(" ".join(line))
            line = []
    if line:
        sentences.append(" ".join(line))
    (out_dir / "transcricao.txt").write_text("\n".join(sentences) + "\n", encoding="utf-8")
    srt = []
    for i, b in enumerate(blocks, 1):
        text = two_lines(" ".join(x["palavra"] for x in b))
        srt.append(f"{i}\n{srt_time(b[0]['inicio'])} --> {srt_time(b[-1]['fim'])}\n{text}\n")
    (out_dir / "transcricao.srt").write_text("\n".join(srt), encoding="utf-8")
    log.info("done: %s", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
