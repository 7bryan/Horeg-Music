import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv #load environment variable
import os
import yt_dlp

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
        vc = await channel.connect()
    else:
        vc = ctx.voice_client
    
    if vc.is_playing():
        vc.stop()

    audio_url = get_audio_url(query)

    # setting for solving disconnected music stream
    ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
            }

    source =discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)

    vc.play(source, after=lambda e: print(f"Error: {e}" if e else "Done"))

    await ctx.send(f"Playing {query}")
    
bot.run(token)
