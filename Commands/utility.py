import discord
from discord.ext import commands

class Utility(commands.Cog):
    async def join(self, ctx):
        """
        Join the voice channel.

        This command makes the bot join the voice channel of the user who sent the command.
        If the bot is already in the correct channel, it will send a message indicating that it is already in the channel.
        If the bot is in a different channel, it will move to the correct channel.
        If the bot is not in any channel, it will connect to the voice channel.
        """
        try:
            # Get the voice channel of the user who sent the command
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send(ctx.author.mention + " is not in a voice channel.")
            return
        try:
            # Create a voice client variable
            vc = ctx.voice_client
            # Check if the bot is already in the correct channel
            if vc and vc.channel == channel:
                await ctx.send("I'm already in your channel.")
                return

            # Check if the bot is already in a channel
            if vc:
                # Move the bot to the correct channel
                await vc.move_to(channel)
            else:
                # Connect to the voice channel
                await channel.connect()
            # Return True to indicate that the bot is in the correct channel
            await ctx.send(f"Joined {channel}")
        except Exception as e:
            print(f"An error occurred when trying to join the channel. {e}")
            raise e
        
    async def joinChannel(self, ctx):
        try:
            # Check if the user is in a voice channel
            try:
                # Get the voice channel of the user who sent the command
                channel = ctx.author.voice.channel
            except Exception as e:
                # Send a message that the user is not in a voice channel
                await ctx.send(ctx.author.mention + " is not in a voice channel.")
                # Return False to indicate that the user is not in a voice channel
                return False

            # Create a voice client variable
            vc = ctx.voice_client
            # Check if the bot is already in the correct channel
            if vc and vc.channel == channel:
                return True  # Bot is already in the correct channel, no need to reconnect
            # Check if the bot is already in a channel
            if vc:
                # Move the bot to the correct channel
                await vc.move_to(channel)
            else:
                # Connect to the voice channel
                await channel.connect()
            # Return True to indicate that the bot is in the correct channel
            return True
        except Exception as e:
            print(f"An error occurred when trying to join the channel. {e}")
            raise e
        
    async def leave(self, ctx):
        try:
            # Check if the bot is in a voice channel
            if ctx.voice_client is None:
                await ctx.send("I'm not in a voice channel.")
                return
            
            # Send a message that the bot is leaving
            await ctx.send("Leaving voice channel.")
            # Disconnect the bot from the voice channel
            await ctx.voice_client.disconnect()
        except Exception as e:
            print(f"Error in the leave command: {e}")
            raise e