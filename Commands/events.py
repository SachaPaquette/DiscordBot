import discord
from discord.ext import commands
from Commands.Profanity.profanity_event import Profanity
from Config.logging import setup_logging
from Commands.Services.utility import EmbedMessage
import os


class EventHandlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.GENERAL_CHANNEL_NAME = os.getenv("GENERAL_CHANNEL_NAME")
        
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name="with your heart"))
        print(f"{self.bot.user.name} has connected to Discord!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        profanity = Profanity(self.bot)
        await profanity.on_message_command(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        if not self.GENERAL_CHANNEL_NAME:
            print("GENERAL_CHANNEL_NAME is not set in the .env file.")
            return
        channel = discord.utils.get(member.guild.text_channels, name=self.GENERAL_CHANNEL_NAME)
        if channel:
            embed_message = EmbedMessage()
            await channel.send(embed=await embed_message.on_member_join_message(member))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not self.GENERAL_CHANNEL_NAME:
            print("GENERAL_CHANNEL_NAME is not set in the .env file.")
            return
        channel = discord.utils.get(member.guild.text_channels, name=self.GENERAL_CHANNEL_NAME)
        if channel:
            embed_message = EmbedMessage()
            await channel.send(embed=await embed_message.on_member_leave_message(member))


async def setup(bot):
    await bot.add_cog(EventHandlers(bot))
