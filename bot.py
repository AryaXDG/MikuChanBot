import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import subprocess
from dotenv import load_dotenv

# Import AI chat system
from ai_chat import MikuChatAI
from config import DEBUG_CONFIG

# Bug of outdate yt-dlp
import ssl
import certifi

# Fix SSL issues in yt-dlp by forcing correct CA bundle
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())


# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not TOKEN:
    print("❌ Error: DISCORD_TOKEN not found in .env file!")
    print("Make sure you have a .env file with: DISCORD_TOKEN=your_bot_token_here")
    exit(1)

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in .env file!")
    print("Add to your .env file: GEMINI_API_KEY=your_gemini_api_key_here")
    print("Get your key from: https://makersuite.google.com/app/apikey")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Initialize AI chat system
miku_ai = MikuChatAI()

# Create downloads folder if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Updated yt-dlp options for better reliability
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extractaudio': True,
    'audioformat': 'mp3',
    'audioquality': '192K',
}

# Updated FFmpeg options (simplified and working)
ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        
        try:
            print(f"Extracting info for: {url}")
            # Extract info
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            
            if 'entries' in data:
                # Take first item from playlist
                data = data['entries'][0]
                print(f"Found video: {data.get('title', 'Unknown')}")
            
            if stream:
                # For streaming, use the direct URL
                filename = data['url']
                print(f"Using stream URL: {filename}")
            else:
                # For downloading, use the filename
                filename = ytdl.prepare_filename(data)
                print(f"Downloaded to: {filename}")
                
                # Check if file exists
                if not os.path.exists(filename):
                    print(f"❌ Downloaded file not found: {filename}")
                else:
                    print(f"✅ Downloaded file exists: {filename}")
            
            print("Creating FFmpeg audio source...")
            # Use absolute path to ensure file is found
            abs_filename = os.path.abspath(filename)
            print(f"Using absolute path: {abs_filename}")
            
            audio_source = discord.FFmpegPCMAudio(abs_filename, **ffmpeg_options)
            print("✅ FFmpeg audio source created successfully")
            
            return cls(audio_source, data=data)
        
        except Exception as e:
            print(f"❌ Error in YTDLSource.from_url: {e}")
            import traceback
            traceback.print_exc()
            raise e

@bot.event
async def on_ready():
    print(f"✅ MikuChan is online as {bot.user}")
    
    # Initialize AI chat system
    print("🤖 Initializing AI chat system...")
    ai_success = await miku_ai.initialize(GEMINI_API_KEY)
    
    if ai_success:
        print("✅ AI chat system ready!")
        await bot.change_presence(activity=discord.Game(name="🎵 Music & AI Chat | !help"))
    else:
        print("❌ AI chat system failed to initialize")
        await bot.change_presence(activity=discord.Game(name="🎵 Music Only | !help"))

# ===================
# AI CHAT COMMANDS
# ===================

@bot.command(aliases=['c', 'talk'])
async def chat(ctx, *, message):
    """Chat with MikuChan AI! Usage: !chat <your message>"""
    if not miku_ai.initialized:
        await ctx.send("Sorry, my AI brain isn't working right now 😔 Try again later!")
        return
    
    # Show typing indicator
    async with ctx.typing():
        try:
            # Get user info
            user_id = str(ctx.author.id)
            display_name = ctx.author.display_name
            username = ctx.author.name
            
            if DEBUG_CONFIG["log_ai_requests"]:
                print(f"💬 Chat request from {display_name}: {message[:100]}...")
            
            # Generate AI response
            response, success = await miku_ai.generate_response(
                message, user_id, display_name, username
            )
            
            if success:
                await ctx.send(response)
            else:
                await ctx.send(response)  # Error message is already friendly
                
        except Exception as e:
            if DEBUG_CONFIG["verbose_errors"]:
                print(f"❌ Chat command error: {e}")
            await ctx.send("Oops, something went wrong while I was thinking... 🤖✨")

@bot.command()
async def aistats(ctx):
    """Show AI chat system statistics"""
    if not miku_ai.initialized:
        await ctx.send("❌ AI system is not initialized!")
        return
    
    try:
        stats = miku_ai.get_stats()
        
        embed = discord.Embed(
            title="🤖 MikuChan AI Statistics",
            color=0x00ff9f,
            timestamp=ctx.message.created_at
        )
        
        embed.add_field(name="Status", value="✅ Online" if stats["initialized"] else "❌ Offline", inline=True)
        embed.add_field(name="Total Conversations", value=f"{stats['total_conversations']}", inline=True)
        embed.add_field(name="Active Users", value=f"{stats['active_users']}", inline=True)
        embed.add_field(name="Known Members", value=f"{stats['known_members']}", inline=True)
        
        embed.set_footer(text="MikuChan AI powered by Gemini")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        if DEBUG_CONFIG["verbose_errors"]:
            print(f"❌ AI stats error: {e}")
        await ctx.send("❌ Failed to get AI statistics!")

# ===================
# MUSIC COMMANDS (Existing)
# ===================

@bot.command()
async def join(ctx):
    """Join the voice channel"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send("🎶 MikuChan joined the voice channel!")
        else:
            await ctx.send("🎶 MikuChan is already in a voice channel!")
    else:
        await ctx.send("❌ You're not in a voice channel!")

@bot.command()
async def play(ctx, *, query):
    """Play a song from YouTube"""
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ You're not in a voice channel!")
            return

    # Stop current playback if any
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        try:
            print(f"Searching for: {query}")
            
            # Try downloading first (more reliable than streaming)
            player = await YTDLSource.from_url(query, loop=bot.loop, stream=False)
            print(f"Successfully created player for: {player.title}")
            
            # Play with detailed error callback
            def after_playing(error):
                if error:
                    print(f'❌ Playback error: {error}')
                else:
                    print('✅ Playback finished successfully')
            
            ctx.voice_client.play(player, after=after_playing)
            
            # Check if it's actually playing
            await asyncio.sleep(2)  # Give it more time to start
            if ctx.voice_client.is_playing():
                await ctx.send(f"🎵 Now playing: **{player.title}**")
                print("✅ Audio is playing!")
            else:
                await ctx.send(f"❌ Failed to play: **{player.title}** - Check terminal for errors")
                print("❌ Audio is NOT playing!")
                
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            print(f"Play command error: {e}")
            import traceback
            traceback.print_exc()

@bot.command()
async def pause(ctx):
    """Pause the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused the music!")
    else:
        await ctx.send("❌ Nothing is currently playing!")

@bot.command()
async def resume(ctx):
    """Resume the paused song"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed the music!")
    else:
        await ctx.send("❌ Music is not paused!")

@bot.command()
async def stop(ctx):
    """Stop the current song"""
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped the music!")
    else:
        await ctx.send("❌ Not connected to a voice channel!")

@bot.command()
async def leave(ctx):
    """Leave the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 MikuChan has left the voice channel.")
    else:
        await ctx.send("❌ Not connected to a voice channel!")

@bot.command()
async def volume(ctx, volume: int):
    """Change the player's volume (0-100)"""
    if ctx.voice_client is None:
        return await ctx.send("❌ Not connected to a voice channel!")
    
    if 0 <= volume <= 100:
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 Changed volume to {volume}%")
    else:
        await ctx.send("❌ Volume must be between 0 and 100!")

# ===================
# DEBUG/TEST COMMANDS (Existing)
# ===================

@bot.command()
async def filetest(ctx):
    """Test the most recent downloaded file"""
    try:
        downloads_dir = 'downloads'
        if not os.path.exists(downloads_dir):
            await ctx.send("❌ No downloads folder found!")
            return
            
        files = [f for f in os.listdir(downloads_dir) if f.endswith(('.webm', '.mp4', '.mp3'))]
        if not files:
            await ctx.send("❌ No audio files found!")
            return
            
        latest_file = max([os.path.join(downloads_dir, f) for f in files], key=os.path.getctime)
        abs_path = os.path.abspath(latest_file)
        
        if not ctx.voice_client:
            await ctx.send("❌ Not connected to voice channel! Use !join first.")
            return
            
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            
        # Test with the actual file
        audio_source = discord.FFmpegPCMAudio(abs_path, **ffmpeg_options)
        ctx.voice_client.play(audio_source, after=lambda e: print(f'File test error: {e}') if e else print('File test completed'))
        
        await ctx.send(f"🔊 Testing file: {os.path.basename(latest_file)}")
        
    except Exception as e:
        await ctx.send(f"❌ File test failed: {e}")
        print(f"File test error: {e}")

@bot.command()
async def debug(ctx):
    """Show audio system debug info"""
    try:
        info = []
        
        # Check audio system
        try:
            result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
            if result.returncode == 0:
                info.append("✅ PulseAudio is running")
            else:
                info.append("❌ PulseAudio not detected")
        except:
            info.append("❌ PulseAudio not available")
            
        # Check for ALSA
        try:
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                info.append("✅ ALSA detected")
            else:
                info.append("❌ ALSA not detected")
        except:
            info.append("❌ ALSA not available")
            
        # Check Discord voice connection
        if ctx.voice_client:
            info.append(f"✅ Connected to voice channel: {ctx.voice_client.channel.name}")
            info.append(f"Voice client latency: {ctx.voice_client.latency*1000:.1f}ms")
        else:
            info.append("❌ Not connected to voice channel")
            
        # AI system status
        ai_status = "✅ Online" if miku_ai.initialized else "❌ Offline"
        info.append(f"AI Chat System: {ai_status}")
            
        await ctx.send("**System Debug Info:**\n" + "\n".join(info))
        
    except Exception as e:
        await ctx.send(f"❌ Debug failed: {e}")

@bot.command()
async def test(ctx):
    """Test if FFmpeg is working"""
    try:
        # Check if ffmpeg is available
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            await ctx.send("✅ FFmpeg is installed and working!")
            print("FFmpeg version info:")
            print(result.stdout[:200])  # First 200 chars
        else:
            await ctx.send("❌ FFmpeg is not working properly!")
            
    except FileNotFoundError:
        await ctx.send("❌ FFmpeg is not installed or not in PATH!")
    except Exception as e:
        await ctx.send(f"❌ Error testing FFmpeg: {e}")

# ===================
# HELP COMMAND (Enhanced)
# ===================

@bot.command(name='mikuhelp')
async def mikuhelp_command(ctx, command_name=None):
    """Show help information"""
    
    if command_name:
        # Show help for specific command
        command = bot.get_command(command_name)
        if command:
            embed = discord.Embed(
                title=f"Help: !{command.name}",
                description=command.help or "No description available",
                color=0x00ff9f
            )
            if command.aliases:
                embed.add_field(name="Aliases", value=", ".join([f"!{alias}" for alias in command.aliases]), inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Command `{command_name}` not found!")
        return
    
    # Show all commands
    embed = discord.Embed(
        title="🎵 MikuChan Bot Commands",
        description="I'm your AI music bot with personality! Here's what I can do:",
        color=0x00ff9f,
        timestamp=ctx.message.created_at
    )
    
    # AI Chat Commands
    chat_commands = [
        "**!chat <message>** - Chat with me! I have feelings and thoughts~ (aliases: !c, !talk)",
        "**!aistats** - See my AI system statistics"
    ]
    embed.add_field(name="🤖 AI Chat", value="\n".join(chat_commands), inline=False)
    
    # Music Commands
    music_commands = [
        "**!join** - Join your voice channel",
        "**!play <song>** - Play music from YouTube",
        "**!pause** - Pause current song",
        "**!resume** - Resume paused song",
        "**!stop** - Stop current song",
        "**!leave** - Leave voice channel",
        "**!volume <0-100>** - Change volume"
    ]
    embed.add_field(name="🎵 Music", value="\n".join(music_commands), inline=False)
    
    # Debug Commands
    debug_commands = [
        "**!debug** - Show system information",
        "**!test** - Test FFmpeg installation",
        "**!filetest** - Test latest downloaded file"
    ]
    embed.add_field(name="🔧 Debug", value="\n".join(debug_commands), inline=False)
    
    embed.add_field(
        name="💡 Pro Tips",
        value="• Try `!chat How are you feeling?` to talk with me!\n• Use `!mikuhelp <command>` for detailed help\n• I remember our conversations and know server members!",
        inline=False
    )
    
    embed.set_footer(text="MikuChan • AI Music Bot with Personality")
    
    await ctx.send(embed=embed)

# ===================
# EVENT HANDLERS
# ===================

@bot.event
async def on_command_error(ctx, error):
    """Enhanced error handling"""
    if isinstance(error, commands.CommandNotFound):
        # Check if it looks like they're trying to chat
        message_content = ctx.message.content.lower()
        if any(word in message_content for word in ['miku', 'hey', 'hello', 'hi', 'chat']):
            await ctx.send("Did you want to chat with me? Try `!chat <your message>` 💕")
        return  # Ignore other unknown commands
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required arguments! Use `!help <command>` for usage info.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument! Use `!help <command>` for usage info.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        if DEBUG_CONFIG["verbose_errors"]:
            print(f"Command error: {error}")
            import traceback
            traceback.print_exc()

@bot.event
async def on_message(ctx):
    """Handle direct mentions for chat"""
    # Don't respond to own messages
    if ctx.author == bot.user:
        return
    
    # Process commands first
    await bot.process_commands(ctx)
    
    # If bot was mentioned and it wasn't a command, treat as chat
    if bot.user.mentioned_in(ctx) and not ctx.content.startswith('!'):
        # Remove the mention from the message
        message_content = ctx.content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '').strip()
        
        if message_content and miku_ai.initialized:
            async with ctx.typing():
                try:
                    user_id = str(ctx.author.id)
                    display_name = ctx.author.display_name
                    username = ctx.author.name
                    
                    response, success = await miku_ai.generate_response(
                        message_content, user_id, display_name, username
                    )
                    
                    await ctx.reply(response)
                    
                except Exception as e:
                    if DEBUG_CONFIG["verbose_errors"]:
                        print(f"❌ Mention chat error: {e}")
                    await ctx.reply("Oops, something went wrong while I was thinking... 🤖✨")

# ===================
# STARTUP
# ===================

if __name__ == "__main__":
    print("🚀 Starting MikuChan Bot...")
    print("🎵 Music system ready")
    print("🤖 AI chat system will initialize on ready")
    print("=" * 50)
    bot.run(TOKEN)
