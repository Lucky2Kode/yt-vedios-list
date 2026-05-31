# How to Run YoutubeList

## 1. Prerequisites

Make sure you have **Python 3.10 or higher** installed:

```bash
python3 --version
```

## 2. First-Time Setup

Run these once from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows

pip install yt-dlp requests
```

## 3. Activate the Virtual Environment (every session)

```bash
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows
```

You'll see `(.venv)` in your terminal prompt when it's active.

## 4. Where to Specify the URL

**Option A — Change the default URL in the script (recommended for repeated use)**

Open [main.py](main.py) and edit line 23:

```python
YOUTUBE_URL = "https://www.youtube.com/@leelashankara/shorts"
```

Replace the URL with your target channel, then just run:

```bash
python main.py
```

**Option B — Pass the URL directly on the command line (no file editing needed)**

```bash
python main.py "https://www.youtube.com/@YourChannel/videos"
```

## 5. Running the Script

### Interactive (asks how many videos)

```bash
python main.py
```

You'll be prompted:
```
How many recent videos to capture? (number or 'all'):
```
Type a number like `20` or type `all` to grab every video.

### Non-Interactive (URL + count in one command)

```bash
python main.py "https://www.youtube.com/@YourChannel/videos" 20
```

## 6. Examples

**Capture the latest 10 videos from a channel's main uploads:**
```bash
python main.py "https://www.youtube.com/@MrBeast/videos" 10
```

**Capture all Shorts from a channel:**
```bash
python main.py "https://www.youtube.com/@leelashankara/shorts" all
```

**Capture videos from a playlist:**
```bash
python main.py "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx" 50
```

**Capture a single video:**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 1
```

## 7. Output

After the run completes you'll find:

```
videos.txt          ← titles + view counts (tab-separated)
downloads/
├── v001.jpg
├── v002.jpg
└── ...
```

`videos.txt` format — each line is:
```
v001    Video Title Here    36K
```

## 8. Notes

- Each run **overwrites** `videos.txt` from scratch.
- Thumbnails in `downloads/` are overwritten only when the filename matches (same `vN`). Delete the folder before a fresh run to get a clean slate.
- For large channels (500+ videos) the script can take several minutes — it makes 2 HTTP requests per video.
- To get only long-form videos (no Shorts), use the `/videos` tab URL. For Shorts only, use the `/shorts` tab URL.
