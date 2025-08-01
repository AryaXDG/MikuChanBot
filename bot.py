import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ Error: DISCORD_TOKEN not found in .env file!")
    print("Make sure you have a .env file with: DISCORD_TOKEN=your_bot_token_here")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

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
            
        await ctx.send("**Audio System Debug:**\n" + "\n".join(info))
        
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

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required arguments!")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Command error: {error}")

if __name__ == "__main__":
    bot.run(TOKEN)
