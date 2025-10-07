# 🎵 MikuChan Discord Bot

> **An AI-powered Discord music bot with personality and emotions**

Created by **Arya Dasgupta**

MikuChan is not just another Discord bot - she's a soft, emotionally complex AI companion who can play music from YouTube and engage in meaningful conversations. She remembers your choices, knows server members, and has her own unique personality.

## ✨ Features

- 🤖 **AI Chat System** - Chat with MikuChan using Google's Gemini AI
- 🎵 **YouTube Music Player** - Play, pause, resume, and control music
- 🧠 **Memory & Personality** - Knows server members and key infomation about them
- 💕 **Emotional Intelligence** - Responds with genuine emotions and personality
- 🎛️ **Voice Controls** - Volume control, queue management
- 🔧 **Debug Tools** - Built-in system diagnostics

## 🛠️ Tech Stack

- **Python 3.8+** - Core programming language
- **discord.py** - Discord API wrapper
- **Google Gemini AI** - Advanced conversational AI
- **yt-dlp** - YouTube audio extraction
- **FFmpeg** - Audio processing

---

# 📋 Installation Guide

## Prerequisites

### For Windows Users:

1. **Install Python 3.8 or higher:**
   - Go to [python.org](https://www.python.org/downloads/)
   - Download the latest Python version
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify installation: Open Command Prompt and run `python --version`

2. **Install FFmpeg:**
   - Go to [ffmpeg.org](https://ffmpeg.org/download.html)
   - Download FFmpeg for Windows
   - Extract to `C:\ffmpeg\`
   - Add `C:\ffmpeg\bin` to your system PATH
   - Verify: Run `ffmpeg -version` in Command Prompt

### For Linux Users:

1. **Install Python 3.8+:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # CentOS/RHEL/Fedora
   sudo dnf install python3 python3-pip
   
   # Arch Linux
   sudo pacman -S python python-pip
   ```

2. **Install FFmpeg:**
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # CentOS/RHEL/Fedora
   sudo dnf install ffmpeg
   
   # Arch Linux
   sudo pacman -S ffmpeg
   ```

3. **Install audio dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt install pulseaudio alsa-utils
   
   # For headless servers
   sudo apt install pulseaudio-utils
   ```

---

## 🚀 Setup Instructions

### Step 1: Get the Bot Code

**Option A: Git Clone (Recommended)**
```bash
git clone https://github.com/AryaXDG/MikuChanBot.git
cd MikuChanBot
```

**Option B: Download ZIP**
1. Go to the GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

### Step 2: Create Virtual Environment

**Windows:**
```cmd
python -m venv mikuchan_env
mikuchan_env\Scripts\activate
```

**Linux:**
```bash
python3 -m venv mikuchan_env
source mikuchan_env/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If you get permission errors on Linux, try:
```bash
pip install --user -r requirements.txt
```

---

## 🔑 Getting API Keys

### Discord Bot Token

1. **Go to Discord Developer Portal:**
   - Visit [discord.com/developers/applications](https://discord.com/developers/applications)
   - Click "New Application"
   - Give it a name (e.g., "MikuChan")

2. **Create Bot:**
   - Go to "Bot" section in left sidebar
   - Click "Add Bot"
   - Under "Token" section, click "Copy" to copy your bot token
   - ⚠️ **Keep this token SECRET!**

3. **Set Bot Permissions:**
   - Under "Privileged Gateway Intents":
     - ✅ Enable "Message Content Intent"
   - Under "Bot Permissions":
     - ✅ Send Messages
     - ✅ Connect
     - ✅ Speak
     - ✅ Use Voice Activity

### Google Gemini API Key

1. **Go to Google AI Studio:**
   - Visit [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key:**
   - Click "Create API Key"
   - Choose "Create API key in new project" (or select existing project)
   - Copy the generated API key
   - ⚠️ **Keep this key SECRET!**

---

## ⚙️ Configuration

### Step 1: Create Environment File

Create a file named `.env` in the bot folder:

**Windows:** Use Notepad or any text editor
**Linux:** Use nano, vim, or any text editor

```bash
# Windows
notepad .env

# Linux
nano .env
```

### Step 2: Add Your Keys

Put this in your `.env` file:
```env
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder text with your actual tokens!

### Step 3: Customize Bot Personality (Optional)

Edit `config.py` to:
- Add server members to `SERVER_MEMBERS`
- Modify `MIKU_PERSONALITY` to change bot behavior
- Adjust `CHAT_CONFIG` for response settings

---

## 🎮 Running the Bot

### Start the Bot

**Windows:**
```cmd
python bot.py
```

**Linux:**
```bash
python3 bot.py
```

### Expected Output:
```
🚀 Starting MikuChan Bot...
🎵 Music system ready
🤖 AI chat system will initialize on ready
==================================================
✅ MikuChan is online as MikuChan#1234
🤖 Initializing AI chat system...
✅ AI chat system ready!
```

### Keep Bot Running 24/7 (Linux):

Use screen or tmux:
```bash
# Using screen
screen -S mikuchan
python3 bot.py
# Press Ctrl+A, then D to detach

# To reattach later
screen -r mikuchan
```

---

## 📨 Inviting Bot to Your Server

### Step 1: Generate Invite Link

1. Go back to Discord Developer Portal
2. Select your application
3. Go to "OAuth2" → "URL Generator"
4. **Scopes:** Check `bot`
5. **Bot Permissions:** Select:
   - Send Messages
   - Connect
   - Speak
   - Use Voice Activity
   - Read Message History
6. Copy the generated URL

### Step 2: Invite Bot

1. Paste the URL in your browser
2. Select your Discord server
3. Click "Authorize"
4. Complete the captcha

---

## 🎵 Bot Commands

### 🤖 AI Chat Commands
| Command | Aliases | Description | Example |
|---------|---------|-------------|---------|
| `!chat <message>` | `!c`, `!talk` | Chat with MikuChan AI | `!chat How are you feeling?` |
| `!aistats` | - | Show AI system statistics | `!aistats` |

### 🎵 Music Commands
| Command | Description | Example |
|---------|-------------|---------|
| `!join` | Join your voice channel | `!join` |
| `!play <song>` | Play music from YouTube | `!play Never Gonna Give You Up` |
| `!pause` | Pause current song | `!pause` |
| `!resume` | Resume paused song | `!resume` |
| `!stop` | Stop current song | `!stop` |
| `!leave` | Leave voice channel | `!leave` |
| `!volume <0-100>` | Change volume | `!volume 50` |

### 🔧 Debug Commands
| Command | Description |
|---------|-------------|
| `!debug` | Show system information |
| `!test` | Test FFmpeg installation |
| `!filetest` | Test latest downloaded file |

### 💡 Pro Tips
- **Direct mentions:** You can also mention MikuChan directly: `@MikuChan how are you?`
- **Personality:** She has moods, emotions, and will react differently based on context
- **Server members:** Configure known members in `config.py` for personalized interactions

---

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError"**
```bash
# Make sure virtual environment is activated
# Windows: mikuchan_env\Scripts\activate
# Linux: source mikuchan_env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**"Discord Token Invalid"**
- Double-check your token in `.env` file
- Make sure there are no extra spaces
- Regenerate token in Discord Developer Portal if needed

**"FFmpeg not found"**
- Verify FFmpeg installation: `ffmpeg -version`
- Check PATH environment variable
- Restart terminal after installing FFmpeg

**"Audio not playing"**
- Use `!debug` command to check system status
- Try `!test` to verify FFmpeg
- Ensure bot has voice permissions in Discord

**"AI not responding"**
- Check Gemini API key in `.env` file
- Verify API key hasn't exceeded quota
- Use `!aistats` to check AI system status

### Linux Audio Issues
```bash
# Install additional audio packages
sudo apt install pulseaudio-utils alsa-utils

# Start PulseAudio
pulseaudio --start

# Check audio devices
aplay -l
```

### Getting Help
- Check the console output for detailed error messages
- Use `!debug` command for system diagnostics
- Enable verbose debugging in `config.py`

---

## 📁 File Structure

```
mikuchan-bot/
├── bot.py              # Main bot file
├── ai_chat.py          # AI chat system
├── config.py           # Configuration and personalities
├── requirements.txt    # Dependencies
├── .env               # Environment variables (you create this)
├── downloads/         # Downloaded music files
└── README.md          # This file
```

---

## 🔒 Security Notes

- **Never share your `.env` file** - it contains secret tokens
- **Never commit `.env` to git** - add it to `.gitignore`
- **Regenerate tokens if compromised**
- **Use a dedicated Google account** for Gemini API
- **Monitor API usage** to avoid unexpected charges

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Arya Dasgupta**

- GitHub: [AryaXDG](https://github.com/AryaXDG)
- Discord: [aryaxdg]

---

Thanks for trying out my bot :)

