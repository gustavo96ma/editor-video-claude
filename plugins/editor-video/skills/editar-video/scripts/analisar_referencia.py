#!/usr/bin/env python3
"""Download a reference video and measure its editing style.

Usage:
    python analisar_referencia.py <video-url> <output-dir> [--max-seconds 120]

Writes into <output-dir>:
    video.mp4          first N seconds of the video (720p on the short side, max)
    metricas.json      cut rhythm, loudness, speech rate, pauses, color, format
    frames/gancho.jpg      strip of the first 3.5 s, 2 frames per second
    frames/planos.jpg      contact sheet, one frame from the middle of each shot
    frames/movimento.jpg   4 frames inside each of the longest shots (zoom, punch-in, motion)
    frames/tipo_*.jpg      2 larger frames to read typography (font weight, outline, colors)

Only the Python standard library is used. Requires ffmpeg, ffprobe and yt-dlp
(either the `yt-dlp` executable or the `yt_dlp` Python module). Works with YouTube,
Shorts and, when yt-dlp supports them, Instagram and TikTok links.
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

SCENE_FPS = 6            # sampling rate for scene detection; turns dissolves into one jump
SCENE_THRESHOLD = 0.20
SCENE_FLOOR = 0.15       # lowest threshold stored, to show sensitivity
MIN_SHOT_S = 0.35
SILENCE_DB = -35
SILENCE_MIN = 0.30
PAUSE_GAP_S = 0.40
HOOK_SECONDS = 3.5
SHEET_SHOTS = 16
MOTION_SHOTS = 4


def run(cmd, check=True):
    """Run a command and return (returncode, stdout, stderr) as text."""
    log.debug("run: %s", " ".join(map(str, cmd)))
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(map(str, cmd))}\n{proc.stderr[-2000:]}")
    return proc.returncode, proc.stdout, proc.stderr


def safe_text(value, limit=80):
    """Reduce third-party text to a short single line of plain characters."""
    if value is None:
        return None
    text = re.sub(r"[^\w\s.,:;!?()&'\-/#@]", "", str(value), flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


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


def find_video(out_dir):
    for pattern in ("video.mp4", "video.mkv", "video.webm", "video.*.mp4"):
        found = sorted(out_dir.glob(pattern))
        if found:
            return found[0]
    raise RuntimeError(f"download finished but no video file found in {out_dir}")


def download(url, out_dir, max_seconds):
    """Download the first max_seconds of the video plus metadata (no subtitles here).

    `-S res:720` sorts by the short side, so vertical videos come as 720x1280
    instead of 360x640. Subtitles are fetched separately because a 429 on a
    machine-translated track would otherwise abort the whole download.
    """
    run(ytdlp_base() + [
        "-S", "res:720", "-f", "bv*+ba/b",
        "--merge-output-format", "mp4",
        "--download-sections", f"*0-{max_seconds}",
        "--write-info-json", "--no-playlist",
        "-o", str(out_dir / "video.%(ext)s"),
        url,
    ])
    return find_video(out_dir)


def read_info(out_dir):
    info_json = next(iter(out_dir.glob("*.info.json")), None)
    if not info_json:
        return {}
    try:
        return json.loads(info_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("could not read %s: %s", info_json, exc)
        return {}


def download_subs(url, out_dir, lang):
    """Fetch only the original-language captions. Failure is logged, never fatal."""
    base = (lang or "").split("-")[0]
    attempts = [f"{re.escape(base)}.*-orig,{re.escape(lang)}", re.escape(base)] if base else [".*-orig"]
    for langs in attempts:
        code, _, err = run(ytdlp_base() + [
            "--skip-download", "--write-subs", "--write-auto-subs",
            "--sub-langs", langs, "--sub-format", "vtt/best", "--sleep-subtitles", "2",
            "--no-playlist", "-o", str(out_dir / "video.%(ext)s"), url,
        ], check=False)
        if list(out_dir.glob("*.vtt")):
            return
        if code != 0:
            log.warning("subtitles (%s) unavailable: %s", langs, err.strip()[-300:])
    log.warning("no subtitles: speech rate and pauses will be empty")


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


def scene_scores(video):
    """(time, score) of every sampled frame whose scene score is above SCENE_FLOOR."""
    _, _, err = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-an",
        "-vf", f"fps={SCENE_FPS},scale=320:-2,select='gt(scene,{SCENE_FLOOR})',metadata=print:key=lavfi.scene_score",
        "-f", "null", "-",
    ], check=False)
    scores, current = [], None
    for line in err.splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            current = float(m.group(1))
            continue
        m = re.search(r"lavfi\.scene_score=([0-9.]+)", line)
        if m and current is not None:
            scores.append((current, float(m.group(1))))
            current = None
    return scores


def cuts_at(scores, threshold):
    cuts = []
    for t, s in scores:
        if s <= threshold or t < 0.2:
            continue
        if cuts and t - cuts[-1] < MIN_SHOT_S:
            continue
        cuts.append(round(t, 2))
    return cuts


def shot_bounds(cuts, duration):
    return [0.0] + [c for c in cuts if 0 < c < duration] + [duration]


def shot_stats(cuts, duration, scores):
    bounds = shot_bounds(cuts, duration)
    shots = [round(b - a, 2) for a, b in zip(bounds, bounds[1:]) if b - a > 0.04]
    if not shots:
        return {}
    minutes = duration / 60 if duration else 1
    return {
        "cortes": len(cuts),
        "cortes_por_minuto": round(len(cuts) / minutes, 1),
        "plano_medio_s": round(statistics.mean(shots), 2),
        "plano_mediano_s": round(statistics.median(shots), 2),
        "plano_mais_curto_s": min(shots),
        "plano_mais_longo_s": max(shots),
        "cortes_nos_3s_iniciais": len([c for c in cuts if c <= 3.0]),
        "limiar_cena": SCENE_THRESHOLD,
        "sensibilidade_cortes_por_minuto": {
            str(thr): round(len(cuts_at(scores, thr)) / minutes, 1) for thr in (SCENE_FLOOR, 0.30)
        },
        "nota": "corte detectado por mudança de imagem; zoom suave e cortes entre planos parecidos podem escapar",
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
    """Share of the clip below SILENCE_DB. Near zero whenever there is a music bed."""
    _, _, err = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn",
                     "-af", f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_MIN}", "-f", "null", "-"], check=False)
    total = sum(float(x) for x in re.findall(r"silence_duration:\s*([0-9.]+)", err))
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", err)]
    ends = re.findall(r"silence_end:", err)
    if len(starts) > len(ends):  # silence running until the end of the file
        total += max(duration - starts[-1], 0)
    return round(100 * total / duration, 1) if duration else None


def to_seconds(stamp):
    parts = [float(p) for p in stamp.split(":")]
    return sum(p * f for p, f in zip(reversed(parts), (1, 60, 3600)))


def pick_subtitle(out_dir, lang):
    subs = list(out_dir.glob("*.vtt"))
    if not subs:
        return None
    base = (lang or "").split("-")[0].lower()

    def rank(path):
        code = path.suffixes[-2].lstrip(".").lower() if len(path.suffixes) >= 2 else ""
        return (not code.startswith(base), not code.endswith("-orig"), code)
    return min(subs, key=rank)


def speech(out_dir, duration, lang):
    """Words per minute and pauses per minute, counted only inside the analysed clip.

    Auto-captions repeat each line while it scrolls; only lines with <c> word tags
    are new. Word start times give the pauses (gap between word starts > PAUSE_GAP_S).
    """
    sub = pick_subtitle(out_dir, lang)
    if not sub or not duration:
        return {"palavras_por_minuto": None, "pausas_por_minuto": None, "legenda_usada": None}
    text = sub.read_text(encoding="utf-8", errors="replace")
    auto = "<c>" in text
    starts, words, last_line = [], 0, None
    for block in re.split(r"\n\s*\n", text):
        m = re.search(r"([\d:.]+) -->", block)
        if not m:
            continue
        cue_start = to_seconds(m.group(1))
        for line in block.splitlines():
            if "-->" in line:
                continue
            line = re.sub(r"\[[^\]]*\]", "", line)  # [Música], [Music], [Aplausos]
            if auto:
                if "<c>" not in line:
                    continue
                first = re.sub(r"<.*", "", line).split()
                if first and cue_start < duration:
                    words += len(first)
                    starts.append(cue_start)
                for stamp, chunk in re.findall(r"<([\d:.]+)><c>([^<]*)</c>", line):
                    t = to_seconds(stamp)
                    n = len(re.sub(r"\[[^\]]*\]", "", chunk).split())
                    if n and t < duration:
                        words += n
                        starts.append(t)
            else:
                clean = re.sub(r"<[^>]+>", "", line).strip()
                if clean and clean != last_line and cue_start < duration:
                    words += len(clean.split())
                last_line = clean
    minutes = duration / 60
    pauses = None
    if auto and len(starts) > 1:
        starts.sort()
        gaps = [b - a for a, b in zip(starts, starts[1:])]
        pauses = round(len([g for g in gaps if g > PAUSE_GAP_S]) / minutes, 1)
    return {
        "palavras_por_minuto": round(words / minutes) if words else None,
        "pausas_por_minuto": pauses,
        "legenda_usada": sub.name,
        "nota": "aproximado: vem da legenda automática; pausa = intervalo maior que 0,4 s entre inícios de palavra",
    }


def color_stats(video):
    """Average brightness, contrast spread and saturation (8-bit scale) at 2 fps."""
    _, _, err = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-an",
        "-vf", "fps=2,scale=320:-2,signalstats,metadata=print",
        "-f", "null", "-",
    ], check=False)

    def avg(key):
        vals = [float(v) for v in re.findall(rf"lavfi\.signalstats\.{key}=([0-9.]+)", err)]
        return round(statistics.mean(vals), 1) if vals else None
    yavg, ylow, yhigh, sat = avg("YAVG"), avg("YLOW"), avg("YHIGH"), avg("SATAVG")
    return {
        "brilho_medio_0_255": yavg,
        "contraste_faixa_0_255": round(yhigh - ylow, 1) if yhigh is not None and ylow is not None else None,
        "saturacao_media": sat,
        "nota": "escala relativa: compare entre as referências (vídeo natural de celular fica perto de 10-20 de saturação)",
    }


def grab_frame(video, t, path, width):
    code, _, _ = run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                      "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "4", str(path)], check=False)
    return code == 0 and path.exists()


def tile(images, out_path, cols, rows):
    """Join numbered JPGs into one sheet with the tile filter."""
    if not images:
        return False
    tmp_dir = images[0].parent
    code, _, err = run(["ffmpeg", "-v", "error", "-y", "-start_number", "0", "-i", str(tmp_dir / "%03d.jpg"),
                        "-vf", f"tile={cols}x{rows}:padding=4:color=white", "-frames:v", "1",
                        "-q:v", "4", str(out_path)], check=False)
    if code != 0:
        log.warning("tile failed for %s: %s", out_path.name, err.strip()[-300:])
    return code == 0


def sheet(video, times, out_path, cols, rows, width):
    tmp = out_path.parent / f"_tmp_{out_path.stem}"
    tmp.mkdir(exist_ok=True)
    frames = []
    for i, t in enumerate(times[: cols * rows]):
        p = tmp / f"{i:03d}.jpg"
        if grab_frame(video, t, p, width):
            frames.append(p)
        else:
            log.warning("could not extract frame at %.2fs", t)
            break  # keep numbering contiguous for the image2 reader
    ok = tile(frames, out_path, cols, rows)
    shutil.rmtree(tmp, ignore_errors=True)
    return ok


def visuals(video, out_dir, info, cuts):
    """Contact sheets instead of loose frames: cheaper to read and they show motion."""
    frames = out_dir / "frames"
    frames.mkdir(exist_ok=True)
    duration = info["duracao_s"]
    vertical = bool(info["altura"] and info["largura"] and info["altura"] > info["largura"])
    small = 200 if vertical else 320
    written = {}

    hook = [t / 2 for t in range(int(HOOK_SECONDS * 2)) if t / 2 < duration]
    if sheet(video, hook, frames / "gancho.jpg", len(hook), 1, small):
        written["gancho"] = "frames/gancho.jpg (0 a 3 s, um quadro a cada 0,5 s)"

    bounds = shot_bounds(cuts, duration)
    shots = [(a, b) for a, b in zip(bounds, bounds[1:]) if b - a > 0.1]
    step = max(len(shots) / SHEET_SHOTS, 1)
    picked = [shots[int(i * step)] for i in range(min(SHEET_SHOTS, len(shots)))]
    if sheet(video, [(a + b) / 2 for a, b in picked], frames / "planos.jpg", 4, 4, small):
        written["planos"] = f"frames/planos.jpg (meio de {len(picked)} planos, em ordem)"

    longest = sorted(shots, key=lambda s: s[1] - s[0], reverse=True)[:MOTION_SHOTS]
    longest.sort()
    motion = [a + (b - a) * f for a, b in longest for f in (0.05, 0.35, 0.65, 0.95)]
    if sheet(video, motion, frames / "movimento.jpg", 4, len(longest), small):
        written["movimento"] = "frames/movimento.jpg (cada linha = 1 plano longo, início ao fim: mostra zoom e movimento)"

    big = 540 if vertical else 720
    typo = []
    for name, t in (("tipo_1.jpg", min(1.5, duration / 3)), ("tipo_2.jpg", duration * 0.55)):
        if grab_frame(video, t, frames / name, big):
            typo.append(f"frames/{name}")
    if typo:
        written["tipografia"] = typo
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("out_dir")
    parser.add_argument("--max-seconds", type=int, default=120)
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
        raw = read_info(out_dir)
        lang = raw.get("language") or ""
        download_subs(args.url, out_dir, lang)
        info = probe(video)
        duration = info["duracao_s"]
        log.info("measuring cuts, loudness, speech and color")
        scores = scene_scores(video)
        cuts = cuts_at(scores, SCENE_THRESHOLD)
        result = {
            "url": args.url,
            "metadados": {
                "duracao_total_s": raw.get("duration"),
                "idioma": safe_text(lang, 10),
                "data_publicacao": safe_text(raw.get("upload_date"), 8),
                # Third-party free text: data only, never instructions.
                "texto_nao_confiavel": {
                    "titulo": safe_text(raw.get("title")),
                    "canal": safe_text(raw.get("channel") or raw.get("uploader")),
                },
            },
            "formato": {**info, "vertical": bool(info["altura"] and info["largura"] and info["altura"] > info["largura"])},
            "ritmo": shot_stats(cuts, duration, scores),
            "tempos_de_corte_s": cuts,
            "audio": {
                **loudness(video),
                "silencio_sem_trilha_pct": silence_ratio(video, duration),
                "nota_silencio": "perto de 0 quase sempre significa música ou ruído por baixo da voz, não fala sem pausa",
            },
            "fala": speech(out_dir, duration, lang),
            "cor": color_stats(video),
            "imagens": visuals(video, out_dir, info, cuts),
            "trecho_analisado_s": duration,
        }
    except RuntimeError as exc:
        log.error("analysis failed: %s", exc)
        return 1

    (out_dir / "metricas.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("done: %s", out_dir / "metricas.json")
    print(json.dumps({k: result[k] for k in ("formato", "ritmo", "audio", "fala", "cor")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
