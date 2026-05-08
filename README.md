# 🎸 Horeg-Music

A Discord music bot that plays audio from YouTube directly in your voice channel. Built with Python, discord.py, and yt-dlp.

---

## Features

- 🔎 Search and play music from YouTube by name or keyword
- 📋 Per-server song queue — add songs and they play in order
- ⏭️ Skip, clear, and view the queue
- 🔄 Auto-plays the next song when the current one finishes
- 🔌 Handles stream disconnects with automatic reconnection
- 🛡️ Non-blocking audio search — bot stays responsive while loading tracks

---

## Commands

| Command | Description |
|---|---|
| `!play <query>` | Search YouTube and add the song to the queue |
| `!skip` | Skip the currently playing song |
| `!queue` | Show the current song queue |
| `!clear` | Clear the entire queue |
| `!join` | Join your current voice channel |
| `!leave` | Leave the voice channel |
| `!ping` | Check bot latency |

---

## Requirements

- Python 3.9+
- FFmpeg installed and available in your system PATH
- A Discord bot token
- The following Python packages (see `requirements.txt`)

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/Horeg-Music.git
cd Horeg-Music
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Install FFmpeg**

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

**5. Set up your environment variables**

Create a `.env` file in the root directory:
```
DISCORD_TOKEN=your_bot_token_here
```

**6. Run the bot**
```bash
python bot.py
```

---

## Getting a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** and give it a name
3. Go to the **Bot** tab and click **Add Bot**
4. Under **Token**, click **Copy**
5. Paste it into your `.env` file
6. Under **Privileged Gateway Intents**, enable **Message Content Intent** and **Server Members Intent**

To invite the bot to your server, go to **OAuth2 > URL Generator**, select `bot`, then check `Connect`, `Speak`, and `Send Messages` permissions.

---

## requirements.txt

```
discord.py
yt-dlp
python-dotenv
PyNaCl
```

---

## Project Structure

```
Horeg-Music/
├── bot.py          # Main bot file
├── .env            # Your Discord token (never commit this)
├── .gitignore
├── requirements.txt
└── discord.log     # Auto-generated log file
```

---

## .gitignore

Make sure your `.env` is never committed:
```
.env
venv/
discord.log
__pycache__/
*.pyc
```

---

## License

MIT License — feel free to fork and modify.
