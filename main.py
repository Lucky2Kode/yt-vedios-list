"""Capture YouTube video titles and thumbnails from a channel/playlist URL.

Change YOUTUBE_URL below to any channel /videos page or playlist URL.
Run:
  python main.py                       # uses YOUTUBE_URL, asks how many videos
  python main.py <url>                 # asks how many videos
  python main.py <url> <count>         # non-interactive
  python main.py <url> all             # capture every video

Outputs:
  - videos.txt          : one title per line (most recent first)
  - downloads/<id>.jpg  : thumbnail image per video
"""

from pathlib import Path
import re
import sys

import requests
from yt_dlp import YoutubeDL


YOUTUBE_URL = "https://www.youtube.com/@leelashankara/shorts"

ROOT = Path(__file__).resolve().parent
TITLES_FILE = ROOT / "videos.txt"
DOWNLOADS_DIR = ROOT / "downloads"


def pick_thumbnail_url(entry: dict) -> str | None:
    thumbs = entry.get("thumbnails") or []
    if thumbs:
        # yt-dlp orders thumbnails worst-to-best; last one is highest quality.
        for t in reversed(thumbs):
            url = t.get("url")
            if url:
                return url
    return entry.get("thumbnail")


def fetch_entries(url: str, limit: int | None) -> list[dict]:
    """Fetch video entries newest-first. limit=None means all videos."""
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "ignoreerrors": True,
    }
    if limit is not None and limit > 0:
        # YouTube channel/playlist pages are ordered newest-first, so the first
        # N items are the most recent uploads.
        opts["playlistend"] = limit

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if not info:
        return []

    entries: list[dict] = []
    if "entries" in info and info["entries"]:
        for e in info["entries"]:
            if not e:
                continue
            # Channel URLs may return nested playlists (Videos/Shorts/Live tabs).
            if e.get("_type") == "playlist" and e.get("entries"):
                entries.extend(x for x in e["entries"] if x)
            else:
                entries.append(e)
    else:
        entries = [info]

    if limit is not None and limit > 0:
        entries = entries[:limit]
    return entries


def download_thumbnail(url: str, dest: Path, session: requests.Session) -> bool:
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  ! thumbnail download failed: {exc}")
        return False
    dest.write_bytes(resp.content)
    return True


def fetch_original_title(video_id: str, session: requests.Session) -> str | None:
    """Fetch the uploader's original (untranslated) title via YouTube oEmbed."""
    try:
        resp = session.get(
            "https://www.youtube.com/oembed",
            params={
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "format": "json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("title")
    except (requests.RequestException, ValueError):
        return None


def format_views(count: int) -> str:
    """Format a view count as short human-readable text: 921, 31K, 1.2M, 3.4B."""
    if count < 1_000:
        return str(count)
    for unit, divisor in (("B", 1_000_000_000), ("M", 1_000_000), ("K", 1_000)):
        if count >= divisor:
            value = count / divisor
            # Show one decimal under 10 (e.g. 1.2M), no decimals at/above (e.g. 36K).
            return f"{value:.1f}{unit}" if value < 10 else f"{int(value)}{unit}"
    return str(count)


def fetch_view_count(video_id: str, session: requests.Session) -> str:
    """Scrape the view count from the watch page. Returns short text or '?'."""
    try:
        resp = session.get(
            f"https://www.youtube.com/watch?v={video_id}",
            headers={"Accept-Language": "en-US,en;q=0.9"},
            timeout=20,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return "?"
    match = re.search(r'"viewCount":"(\d+)"', resp.text)
    if not match:
        return "?"
    return format_views(int(match.group(1)))


def parse_count(raw: str) -> int | None:
    """Return None for 'all', else a positive int. Raises ValueError otherwise."""
    raw = raw.strip().lower()
    if raw in {"all", "0", ""}:
        return None
    n = int(raw)
    if n <= 0:
        raise ValueError("count must be positive")
    return n


def prompt_count() -> int | None:
    while True:
        raw = input("How many recent videos to capture? (number or 'all'): ")
        try:
            return parse_count(raw)
        except ValueError:
            print("  Please enter a positive number or 'all'.")


def main(url: str, limit: int | None) -> int:
    DOWNLOADS_DIR.mkdir(exist_ok=True)

    label = "all videos" if limit is None else f"latest {limit} video(s)"
    print(f"Fetching {label} from: {url}")
    entries = fetch_entries(url, limit)
    if not entries:
        print("No videos found.")
        return 1

    print(f"Got {len(entries)} videos. Writing titles and downloading thumbnails...")

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (YoutubeList script)"})

    total = len(entries)
    pad = len(str(total))  # zero-pad so files sort naturally (v01, v02, ... v10)

    with TITLES_FILE.open("w", encoding="utf-8") as f:
        for idx, entry in enumerate(entries, 1):
            seq = f"v{idx:0{pad}d}"
            video_id = entry.get("id") or f"video_{idx}"
            title = (
                fetch_original_title(video_id, session)
                or entry.get("title")
                or "(untitled)"
            )
            views = fetch_view_count(video_id, session)
            f.write(f"{seq}\t{title}\t{views}\n")
            print(f"[{idx}/{total}] {seq}  {views:>6}  {title}")

            thumb_url = pick_thumbnail_url(entry)
            if not thumb_url:
                print("  ! no thumbnail url available")
                continue

            ext = Path(thumb_url.split("?")[0]).suffix.lower()
            if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
                ext = ".jpg"
            dest = DOWNLOADS_DIR / f"{seq}{ext}"
            download_thumbnail(thumb_url, dest, session)

    print(f"\nDone. Titles -> {TITLES_FILE}")
    print(f"Thumbnails  -> {DOWNLOADS_DIR}")
    return 0


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else YOUTUBE_URL

    if len(sys.argv) > 2:
        try:
            count = parse_count(sys.argv[2])
        except ValueError as e:
            print(f"Invalid count: {e}")
            sys.exit(2)
    else:
        count = prompt_count()

    sys.exit(main(target_url, count))
