#!/usr/bin/env python3
"""Download a reference video and measure its editing style.

Usage:
    python analisar_referencia.py <youtube-url> <output-dir> [--max-seconds 180]

Writes into <output-dir>:
    video.mp4          first N seconds of the video (720p max)
    metricas.json      cut rhythm, loudness, silence, speech rate, format
    frames/            small frames for visual reading (hook + spread over the clip)

Only the Python standard library is used. Requires ffmpeg, ffprobe and yt-dlp
(either the `yt-dlp` executable or the `yt_dlp` Python module).
"""

import argparse
import json
import logging
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("analisar_referencia")

SCENE_THRESHOLD = 0.30
SILENCE_DB = -35
SILENCE_MIN = 0.30
MAX_SPREAD_FRAMES = 16
HOOK_SECONDS = 3.0


def run(cmd, check=True):
    """Run a command and return (returncode, stdout, stderr) as text."""
    log.debug("run: %s", " ".join(map(str, cmd)))
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(map(str, cmd))}\n{proc.stderr[-2000:]}")
    return proc.returncode, proc.stdout, proc.stderr


def ytdlp_base():
    """Return the command prefix for yt-dlp, preferring the executable."""
    exe = shutil.which("yt-dlp")
    if exe:
        return [exe]
    try:
        import yt_dlp  # noqa: F401
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError as exc:
        raise RuntimeError("yt-dlp not found. Install it (Windows: winget install yt-dlp.yt-dlp; Mac: brew install yt-dlp)") from exc


def download(url, out_dir, max_seconds):
    """Download the first max_seconds of the video plus subtitles and metadata."""
    target = out_dir / "video.%(ext)s"
    cmd = ytdlp_base() + [
        "-f", "bv*[height<=720]+ba/b[height<=720]/b",
        "--merge-output-format", "mp4",
        "--download-sections", f"*0-{max_seconds}",
        "--force-keyframes-at-cuts",
        "--write-auto-subs", "--write-subs",
        "--sub-langs", "pt.*,en.*,es.*",
        "--sub-format", "vtt",
        "--write-info-json",
        "--no-playlist",
        "-o", str(target),
        url,
    ]
    run(cmd)
    video = out_dir / "video.mp4"
    if not video.exists():
        candidates = sorted(out_dir.glob("video.*.mp4")) + sorted(out_dir.glob("video.mkv")) + sorted(out_dir.glob("video.webm"))
        if not candidates:
            raise RuntimeError(f"download finished but no video file found in {out_dir}")
        video = candidates[0]
    return video


def probe(video):
    """Return width, height, fps and duration of the video stream."""
    _, out, _ = run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate:format=duration",
        "-of", "json", str(video),
    ])
    data = json.loads(out)
    stream = data["streams"][0]
    num, den = stream.get("r_frame_rate", "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0.0
    return {
        "largura": stream.get("width"),
        "altura": stream.get("height"),
        "fps": round(fps, 2),
        "duracao_s": round(float(data["format"]["duration"]), 2),
    }


def detect_cuts(video):
    """Return the timestamps (s) where the scene changes above SCENE_THRESHOLD."""
    _, _, err = run([
        "ffmpeg", "-hide_banner", "-i", str(video), "-an",
        "-vf", f"select='gt(scene,{SCENE_THRESHOLD})',showinfo",
        "-f", "null", "-",
    ], check=False)
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", err)]


def shot_stats(cuts, duration):
    """Shot-length statistics derived from cut timestamps."""
    bounds = [0.0] + [c for c in cuts if 0 < c < duration] + [duration]
    shots = [round(b - a, 2) for a, b in zip(bounds, bounds[1:]) if b - a > 0.04]
    if not shots:
        return {}
    minutes = duration / 60 if duration else 1
    hook_cuts = [c for c in cuts if c <= HOOK_SECONDS]
    return {
        "cortes": len(cuts),
        "cortes_por_minuto": round(len(cuts) / minutes, 1),
        "plano_medio_s": round(statistics.mean(shots), 2),
        "plano_mediano_s": round(statistics.median(shots), 2),
        "plano_mais_curto_s": min(shots),
        "plano_mais_longo_s": max(shots),
        "cortes_nos_3s_iniciais": len(hook_cuts),
        "limiar_cena": SCENE_THRESHOLD,
    }


def loudness(video):
    """Integrated loudness, loudness range and true peak via ebur128."""
    _, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn",
                     "-af", "ebur128=peak=true", "-f", "null", "-"], check=False)
    summary = err[err.rfind("Summary:"):] if "Summary:" in err else ""
    def grab(pattern):
        m = re.search(pattern, summary)
        return float(m.group(1)) if m else None
    return {
        "lufs_integrado": grab(r"I:\s*(-?[0-9.]+) LUFS"),
        "lra_lu": grab(r"LRA:\s*(-?[0-9.]+) LU"),
        "pico_real_dbfs": grab(r"Peak:\s*(-?[0-9.]+) dBFS"),
    }


def silence_ratio(video, duration):
    """Share of the clip below SILENCE_DB for at least SILENCE_MIN seconds."""
    _, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn",
                     "-af", f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_MIN}", "-f", "null", "-"], check=False)
    total = sum(float(x) for x in re.findall(r"silence_duration:\s*([0-9.]+)", err))
    return round(100 * total / duration, 1) if duration else None


def speech_rate(out_dir, duration):
    """Words per minute from the first subtitle file found (auto-captions are fine)."""
    subs = sorted(out_dir.glob("*.vtt"))
    if not subs:
        return None, None
    text_lines = []
    seen = set()
    for line in subs[0].read_text(encoding="utf-8", errors="replace").splitlines():
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:")) or line.isdigit():
            continue
        if line in seen:  # auto-captions repeat rolling lines
            continue
        seen.add(line)
        text_lines.append(line)
    words = len(" ".join(text_lines).split())
    wpm = round(words / (duration / 60), 0) if duration else None
    return wpm, subs[0].name


def extract_frames(video, out_dir, duration):
    """Hook frames every 0.5 s in the first 3 s, then frames spread over the clip."""
    frames = out_dir / "frames"
    frames.mkdir(exist_ok=True)
    times = [t / 2 for t in range(int(HOOK_SECONDS * 2) + 1) if t / 2 < duration]
    step = max(duration / MAX_SPREAD_FRAMES, 1.0)
    t = HOOK_SECONDS + step / 2
    while t < duration and len(times) < MAX_SPREAD_FRAMES + 7:
        times.append(round(t, 2))
        t += step
    written = []
    for ts in times:
        name = frames / f"t{ts:07.2f}s.jpg"
        code, _, _ = run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ts}", "-i", str(video),
                          "-frames:v", "1", "-vf", "scale=480:-2", "-q:v", "4", str(name)], check=False)
        if code == 0 and name.exists():
            written.append(name.name)
        else:
            log.warning("could not extract frame at %ss", ts)
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("out_dir")
    parser.add_argument("--max-seconds", type=int, default=180)
    args = parser.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            log.error("%s not found. Windows: winget install Gyan.FFmpeg ; Mac: brew install ffmpeg", tool)
            return 2

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        log.info("downloading %s (first %ss)", args.url, args.max_seconds)
        video = download(args.url, out_dir, args.max_seconds)
        info = probe(video)
        duration = info["duracao_s"]
        log.info("measuring cuts, loudness, silence and speech rate")
        cuts = detect_cuts(video)
        wpm, sub_file = speech_rate(out_dir, duration)
        meta = {}
        info_json = next(iter(out_dir.glob("*.info.json")), None)
        if info_json:
            raw = json.loads(info_json.read_text(encoding="utf-8"))
            meta = {k: raw.get(k) for k in ("title", "channel", "duration", "aspect_ratio", "upload_date")}
        result = {
            "url": args.url,
            "metadados": meta,
            "formato": {**info, "vertical": bool(info["altura"] and info["largura"] and info["altura"] > info["largura"])},
            "ritmo": shot_stats(cuts, duration),
            "tempos_de_corte_s": [round(c, 2) for c in cuts],
            "audio": {**loudness(video), "silencio_pct": silence_ratio(video, duration)},
            "fala": {"palavras_por_minuto": wpm, "legenda_usada": sub_file},
            "frames": extract_frames(video, out_dir, duration),
            "trecho_analisado_s": duration,
        }
    except RuntimeError as exc:
        log.error("analysis failed: %s", exc)
        return 1

    (out_dir / "metricas.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("done: %s", out_dir / "metricas.json")
    print(json.dumps({k: result[k] for k in ("formato", "ritmo", "audio", "fala")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
