# YoutubeList

A small Python tool that captures **video titles** and **thumbnail images** from
any YouTube channel, playlist, or single video URL.

- Writes the titles to `videos.txt` (one per line, prefixed with a sequence
  number like `v1`, `v2`, ...).
- Saves each thumbnail into `downloads/` with a matching name (`v1.jpg`,
  `v2.jpg`, ...) so titles and images are easy to map 1-to-1.
- Pulls the **uploader's original title** (no auto-translation), so non-English
  titles (Telugu, Hindi, etc.) are preserved exactly as the creator wrote them.
- Lets you choose how many of the **most recent** videos to capture, or grab
  every video on the page.

## How it works

1. `yt-dlp` lists the videos on the URL (newest-first ordering for channels and
   playlists). It can be limited to the first N entries, which are the N most
   recently uploaded videos.
2. For each video, the script calls YouTube's public `oembed` endpoint to fetch
   the original (untranslated) title.
3. The highest-quality thumbnail URL is downloaded to `downloads/`.

## Requirements

- Python 3.10+
- Internet access
- Dependencies: `yt-dlp`, `requests`

## Setup

```bash
# from the project root
python3 -m venv .venv
source .venv/bin/activate
pip install yt-dlp requests
```

## Usage

The script accepts an optional **URL** and an optional **count**.

```bash
# 1. Fully interactive — uses the default URL inside main.py, asks for count
python main.py

# 2. URL provided, asks for count interactively
python main.py "https://www.youtube.com/@AmmaChethiVanta/videos"

# 3. Fully non-interactive — URL + count
python main.py "https://www.youtube.com/@AmmaChethiVanta/videos" 10

# 4. Capture every video on the page
python main.py "https://www.youtube.com/@AmmaChethiVanta/videos" all
```

When a count is requested interactively, you can type a positive integer (e.g.
`25`) or the word `all`.

### URL types you can pass

- A channel videos tab: `https://www.youtube.com/@SomeChannel/videos`
- A playlist: `https://www.youtube.com/playlist?list=PL...`
- A single video: `https://www.youtube.com/watch?v=...`

### Changing the default URL

`YOUTUBE_URL` near the top of `main.py` is used when no URL is passed on the
command line. Edit it to whatever channel you want as the default.

## Output

After a successful run:

```
videos.txt
downloads/
├── v1.jpg
├── v2.jpg
├── v3.jpg
└── ...
```

`videos.txt` contains one row per video, tab-separated as
`sequence<TAB>title<TAB>views`:

```
v1	2ని||ల్లో చేసుకొనే షుగర్స్ లేని హెల్దీ ఫ్రూట్ డ్రింక్😋 Healthy Summer Drink	36K
v2	నోరూరించే పచ్చి మామిడికాయ రోటి పచ్చడి😋 Mamidikaya Tomato Pachadi	77K
v3	బయట దొరికే కల్తీ బాదం పాలకు బదులు ఇలా స్వచ్ఛమైన బాదంపాలు చేసి పిల్లలకు ఇవ్వండి👌 Badam Milk Recipe	367K
...
```

The view count is short-formatted: `921`, `36K`, `1.2M`, `3.4B`. If the count
can't be retrieved (rare network/parse failure), it appears as `?`.

Each line `vN` matches `downloads/vN.jpg` (or `.png` / `.webp` depending on
what YouTube serves for that thumbnail).

The sequence numbers are zero-padded to the total count so that filenames sort
naturally (e.g. `v01` … `v10` … `v100`).

## Examples

**Capture the latest 10 videos from a channel**

```bash
python main.py "https://www.youtube.com/@AmmaChethiVanta/videos" 10
```

Result: `videos.txt` has 10 lines (`v01` … `v10`), `downloads/` has 10 images.

**Capture every video from a playlist**

```bash
python main.py "https://www.youtube.com/playlist?list=PLxxxxxx" all
```

**Just one video (any video URL works)**

```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 1
```

## Notes

- Each run **overwrites** `videos.txt`. Thumbnails in `downloads/` are
  overwritten when filenames collide (i.e. for the same `vN`), but old files
  from a longer previous run will still be sitting in the folder. Delete the
  folder between runs if you want a clean slate.
- Channels with separate Shorts / Live / Videos tabs: pass the specific tab URL
  you want (e.g. `/videos` for long-form uploads only).
- The script makes two small HTTP requests per video — one for the original
  title (oEmbed), one for the view count (the watch page). For very large pulls
  (1000+ videos) that can add a few minutes total.
