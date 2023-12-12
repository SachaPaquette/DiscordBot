# Discord bot for the server
import discord
from discord.ext import commands
from discord.utils import get
from discord.voice_client import VoiceClient
import youtube_dl
from yt_dlp import YoutubeDL

import nacl
import os
from dotenv import load_dotenv
import asyncio
from Commands.help import CustomHelpCommand
from Commands.ytdl import YTDLSource
from Commands.music import SongSession
from Commands.bot import Bot
load_dotenv()


def create_bot():
    # Create an instance of the bot
    intents = discord.Intents.default()
    # Make sure the bot can read messages
    intents.message_content = True
    # Create the command prefix and pass in the intents parameter
    bot = commands.Bot(command_prefix="!", intents=intents)
    return bot
async def main():
    # Get the token from the .env file
    token = os.environ.get("DISCORD_TOKEN")
    bot = create_bot()
    # Await the coroutine
    await bot.add_cog(Bot(bot))
    # Create a new event loop
    loop = asyncio.new_event_loop()
    # Set the event loop
    asyncio.set_event_loop(loop)
    # Start the bot
    try:
        await bot.start(token)
    except Exception as e:
        print(f"Error: {e}")
        exit()

# Run the main coroutine
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        exit()
