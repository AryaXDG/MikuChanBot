
# 🎵 MikuChanBot — Simple Discord Music Bot

**MikuChanBot** is a straightforward Discord music bot written in Python. It can join voice channels, play music from YouTube, and handle basic playback controls — no Lavalink or complex setup needed.

---

## ✨ Features

- 🎶 Join and leave voice channels
- 🔍 Search and download YouTube audio using `yt-dlp`
- ▶️ Play, pause, resume, stop music
- 🔊 Adjust playback volume
- 🧪 Test audio setup (PulseAudio / ALSA / FFmpeg)
- 🐧 Linux-friendly (tested with PulseAudio and ALSA)

---

## 🛠️ Tech Stack

| Tool/Library   | Purpose                              |
|----------------|--------------------------------------|
| Python 3.x     | Core language                        |
| discord.py     | Discord bot framework                |
| yt-dlp         | YouTube audio extraction             |
| ffmpeg         | Audio playback (via subprocess)      |
| asyncio        | Async control flow                   |
| dotenv         | Environment variable management      |
| subprocess     | System-level audio checks            |

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/AryaXDG/MikuChanBot.git
cd MikuChanBot
```

### 2. Create and activate virtual environment (optional)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install required packages

```bash
pip install -r requirements.txt
```

### 4. Add your bot token

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_bot_token_here
```

---

## ▶️ Running the Bot

```bash
python bot.py
```

Then invite your bot to your server and use commands like:

```text
!join         # Join voice channel
!play <song>  # Search & play from YouTube
!pause
!resume
!stop
!volume 50
!leave
```

---

## 🧪 Debug Tools

- `!test` – Checks if FFmpeg is installed
- `!debug` – Prints PulseAudio/ALSA status
- `!filetest` – Tests the last downloaded audio file

---

## 📁 Project Structure

```
MikuChanBot/
├── bot.py
├── .env                # Your Discord bot token (never commit this)
├── downloads/          # Auto-created folder for downloaded audio
├── requirements.txt
└── .gitignore
```

---

## ✅ Requirements

- Python 3.8+
- FFmpeg installed and available in PATH
- (Linux) PulseAudio or ALSA for audio output

---

## 📝 License

This project is under the [MIT License](LICENSE).

---

> Developed with 💙 by Arya (Maiku) — Simple bots, no BS.
