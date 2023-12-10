# Discord bot for the server
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import youtube_dl
import os
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def health(ctx):
    await ctx.send("I am alive!")


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


def main():
    token = os.environ.get("DISCORD_TOKEN")
    # Gets the token from the .env file and
    print(token)
    bot.run(token)  # gets the token from the .env file


if __name__ == "__main__":
    main()
