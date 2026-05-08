# 🎸 Horeg Music

A simple Discord music bot that streams audio directly from YouTube into your voice channel. Built with `discord.py` and `yt-dlp`.

---

## ✨ Features

- 🔍 Search and stream audio from YouTube by keyword or URL
- 📋 Per-server song queue system
- ⏭️ Skip, clear, and view the queue
- 🔁 Auto-reconnect on stream interruption
- 🚀 Non-blocking audio search (won't freeze the bot)

---

## 🛠️ Tech Stack

- [discord.py](https://discordpy.readthedocs.io/) — Discord API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube audio extraction
- [FFmpeg](https://ffmpeg.org/) — Audio streaming
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Environment variable management

---

## ⚙️ Setup

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

## 🎮 Commands

| Command | Description |
|---|---|
| `!join` | Bot joins your current voice channel |
| `!leave` | Bot leaves the voice channel |
| `!play <song name or URL>` | Adds a song to the queue and starts playing |
| `!skip` | Skips the currently playing song |
| `!queue` | Displays the current song queue |
| `!clear` | Clears the entire queue |
| `!ping` | Shows the bot's latency |

---

## 📁 Project Structure

```
horeg-music/
├── main.py           # Main bot logic
├── requirements.txt  # Python dependencies
├── .env              # Your secret token 
├── .env.example      # Token template 
├── .gitignore        # Ignores .env, venv, logs, etc.
└── README.md
```

---

## 📝 Notes

- The bot uses `ytsearch:` to find audio by song name, so you can type a song title directly without a YouTube URL.
- Each Discord server (guild) has its own independent queue.
- If a track fails to load, the bot will automatically skip to the next song in the queue.

---

## 📜 License

This project is open source and free to use. Do whatever you want with it. 🤘
