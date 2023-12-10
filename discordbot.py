# Discord bot for the server
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import youtube_dl
import os

bot = commands.Bot(command_prefix="#")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.command()  # command prefix
async def join(ctx):
    channel = ctx.author.voice.channel  # gets the channel of the user
    await channel.connect()  # joins the voice channel


@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()  # leaves the voice channel


@bot.command()
async def ping(ctx, username):  # function to ping someone in the server
    await ctx.send(f"@{username}")


@bot.command()
async def play(ctx, url):
    channel = ctx.author.voice.channel
    voice = await channel.connect()
    voice.play(discord.FFmpegPCMAudio(url))
    await ctx.send("playing")


# Gets the token from the .env file and
bot.run(os.getenv("TOKEN"))  # gets the token from the .env file
