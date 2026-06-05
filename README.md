# Horeg Music

A Discord music bot that streams audio directly from YouTube into your voice channel.  
Built with `discord.py` and `yt-dlp`, structured with modularity and maintainability in mind.

---

## Features

- 🔍 Search and stream audio from YouTube by keyword or URL
- 📋 Per-server song queue system
- ⏸️ Pause, resume, skip, and stop playback
- 🔊 Live volume control (0–100)
- 🗑️ Remove specific songs from the queue by position
- 🎵 Rich Now Playing embed with title, duration, thumbnail, and requester
- 💬 Consistent Discord embeds for every response
- 🤖 Auto-disconnect after 60s when left alone in a channel
- ⚡ Non-blocking audio search (runs in executor — won't freeze the bot)
- 🔁 Auto-reconnect on stream interruption

---

## Tech Stack

- [discord.py](https://discordpy.readthedocs.io/) — Discord API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube audio extraction
- [FFmpeg](https://ffmpeg.org/) — Audio streaming
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Environment variable management

---

## Project Structure

```
horeg-music/
├── cogs/
    ├── __init__.py
│   ├── music.py           # Music commands: !play, !skip, !queue, !volume, etc.
│   └── general.py         # Utility commands: !ping, !help
├── utils/
    ├── __init__.py
│   ├── audio_handler.py   # yt-dlp fetching, per-guild state, playback engine
│   └── embed_factory.py   # All Discord embed construction in one place
├── models/
    ├── __init__.py
│   └── track.py           # Track dataclass (title, URL, duration, requester…)
├── config.py              # Centralized configuration (token, colors, FFmpeg opts)
├── main.py                # Entry point — loads cogs and starts the bot
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/7bryan/Horeg-Music
cd Horeg-Music
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **Linux/macOS:** `source venv/bin/activate`

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

FFmpeg must be installed separately and available on your system PATH.

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract, and add the `bin/` folder to PATH
- **Linux:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`

Verify:
```bash
ffmpeg -version
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and add your bot token:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

> Get your token from the [Discord Developer Portal](https://discord.com/developers/applications).  
> Enable **Message Content Intent** and **Server Members Intent** under *Privileged Gateway Intents*.

### 6. Run the bot

```bash
python main.py
```

---

## Commands

| Command | Description |
|---|---|
| `!join` | Bot joins your current voice channel |
| `!leave` | Bot leaves the voice channel and clears the queue |
| `!play <song name or URL>` | Adds a song to the queue and starts playing |
| `!pause` | Pauses the current song |
| `!resume` | Resumes paused playback |
| `!skip` | Skips the currently playing song |
| `!stop` | Stops playback and clears the entire queue |
| `!queue` / `!q` | Displays the current song queue |
| `!remove <position>` | Removes a song from the queue by its number |
| `!np` / `!nowplaying` | Shows what's currently playing |
| `!volume <0-100>` | Sets the playback volume |
| `!ping` | Shows the bot's response latency |
| `!help` | Shows all available commands |

---

## Notes

- Song search uses `ytsearch:` under the hood — just type a song name, no YouTube URL needed.
- Each Discord server has its own independent queue and volume level.
- Stream URLs are re-fetched right before playback since YouTube URLs expire.
- If a track fails to load, the bot automatically skips to the next song.
- The bot disconnects automatically after 60 seconds if left alone in a voice channel.

---

## License

Open source — do whatever you want with it.
