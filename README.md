# Horeg Music 
A Discord music bot that streams audio directly from YouTube into your voice channel. Built with `discord.py` and `yt-dlp`.

---

## Features

- 🔍 Search and stream audio from YouTube by keyword or URL
- 📋 Per-server song queue system
- ⏸️ Pause, resume, skip, and stop playback
- 🔊 Live volume control (0–100)
- 🗑️ Remove specific songs from the queue
- 🎵 Now Playing embed with title, duration, thumbnail, and requester
- 💬 Rich Discord embeds for all responses
- 🤖 Auto-disconnect when left alone in a voice channel
- ⚡ Non-blocking audio search (won't freeze the bot)
- 🔁 Auto-reconnect on stream interruption

---

## Tech Stack

- [discord.py](https://discordpy.readthedocs.io/) — Discord API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube audio extraction
- [FFmpeg](https://ffmpeg.org/) — Audio streaming
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Environment variable management

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

FFmpeg is required for audio streaming and must be installed separately on your system.

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract it, and add the `bin` folder to your system PATH
- **Linux:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`

Verify it's working:
```bash
ffmpeg -version
```

### 5. Configure environment variables

Copy the example env file and fill in your token:

```bash
cp .env.example .env
```

Then open `.env` and replace the placeholder with your actual bot token:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

> Get your bot token from the [Discord Developer Portal](https://discord.com/developers/applications). Make sure your bot has the **Message Content Intent** and **Server Members Intent** enabled under the *Privileged Gateway Intents* section.

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
| `!ping` | Shows the bot's latency |
| `!help` | Shows all available commands |

---

## Project Structure

```
horeg-music/
├── main.py           # Main bot logic
├── requirements.txt  # Python dependencies
├── .env              # Your secret token (don't commit this)
├── .env.example      # Token template
├── .gitignore        # Ignores .env, venv, logs, etc.
└── README.md
```

---

## Notes

- The bot uses `ytsearch:` to find audio by song name, so you can type a song title directly without a YouTube URL.
- Each Discord server (guild) has its own independent queue and volume setting.
- If a track fails to load, the bot will automatically skip to the next song in the queue.
- The bot will automatically disconnect after 60 seconds if left alone in a voice channel.
- All bot responses use rich Discord embeds with color-coded status (green = success, red = error, orange = warning, blue = info).

---

## License

This project is open source and free to use. Do whatever you want with it.
