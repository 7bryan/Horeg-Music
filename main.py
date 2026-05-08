import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv #load environment variable
import os
import yt_dlp
import asyncio

def get_audio_url(query):
    ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True,
            'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        return info['entries'][0]['url']


load_dotenv()
token = os.getenv('DISCORD_TOKEN') #the discord token


#basic logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default() #specify intent

#enable intents
intents.message_content = True
intents.members = True

#set up a bot
bot = commands.Bot(command_prefix='!', intents=intents) #call the bot using !

# song queues -> one list for each guild
queues = {}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]

async def play_next(ctx):
    queue = get_queue(ctx.guild.id)
    if not queue:
        await ctx.send("Queue is empty, add more songs!")
        return

    query = queue.pop(0) # grabbing the next song
    vc = ctx.voice_client

    # handling error if yt-dlp finds nothing
    try:
        # prevent slow searches freeze the bot
        audio_url = await bot.loop.run_in_executor(None, get_audio_url, query)
    except Exception as e:
        await ctx.send(f"Skipping - couldn't load track: {e}")
        if queue:
            await play_next(ctx) # try the next one if the current one failed
        return

    #s setting for disconnected music stream
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)

    def after_playing(e):
        if e:   
            print(f"Error: {e}")
        # schedule play_next from the non_async after callback
        asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

    vc.play(source, after=after_playing)
    await ctx.send(f"Now Playing: **{query}**")

@bot.event
async def on_ready():
    print(f"Horeg Music is ready for some rock and roll!")

@bot.command()
async def ping(ctx):
    latency = bot.latency
    await ctx.send(latency)


@bot.command()
async def join(ctx):
    # join the voice channel
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        # check if the bot already on the channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"{channel.name} is ready for music")
    else:
        await ctx.send("please join a voice channel first")

@bot.command()
async def leave(ctx):
    # leave the voice channel
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Music never dies")
    else:
        await ctx.send("I'm not even in a voice channel")

#play some local music
@bot.command()
async def play(ctx, *, query):
    #check if the user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("join voice channel first")
        return 


    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        #connect to the voice channel
        await channel.connect()
    
    queue = get_queue(ctx.guild.id)
    queue.append(query)
    await ctx.send(f"Added to queue: **{query}**")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped!")
    else:
        await ctx.send("Nothing is played")

@bot.command()
async def queue(ctx):
    q = get_queue(ctx.guild.id)
    if not q:
        await ctx.send("Queue is empty")
    else:
        listed = "\n".join(f"{i+1}. {song}" for i, song in enumerate(q))
        await ctx.send(f"**Queue:**\n{listed}")

@bot.command()
async def clear(ctx):
    queues[ctx.guild.id] = []
    await ctx.send("Queue cleared")
    
bot.run(token)
