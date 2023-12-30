import discord
from discord.ext import commands

class Utility():
    async def join(self, interactions: discord.Interaction):
        """
        Join the voice channel.

        This command makes the bot join the voice channel of the user who sent the command.
        If the bot is already in the correct channel, it will send a message indicating that it is already in the channel.
        If the bot is in a different channel, it will move to the correct channel.
        If the bot is not in any channel, it will connect to the voice channel.
        """
        try:

            # Get the voice channel of the user who sent the command
            channel = interactions.channel
        except AttributeError:
            await interactions.response.send_message(interactions.user + " is not in a voice channel.")
            return
        try:
            # Create a user voice variable
            user_voice = interactions.user.voice
            
            # Check if the user is in a voice channel
            if not user_voice:
                await interactions.response.send_message(interactions.user.mention + " is not in a voice channel.")
                return
            
            # Create a voice client variable
            voice_client = interactions.guild.voice_client
            
            if voice_client:
                if voice_client.channel.id == user_voice.channel.id:
                    #await interactions.response.send_message("I'm already in your channel.")
                    return
            # Connect to the voice channel                
            await user_voice.channel.connect(reconnect=True)

            # Return True to indicate that the bot is in the correct channel
            await interactions.response.send_message(f"Joined {channel}")
        except Exception as e:
            print(f"An error occurred when trying to join the channel. {e}")
            raise e
        

        
    async def leave(self, interactions):
        try:
            # Check if the bot is in a voice channel
            if interactions.guild.voice_client is None:
                await interactions.response.send_message("I'm not in a voice channel.")
                return
            
            # Send a message that the bot is leaving
            await interactions.response.send_message("Leaving voice channel.")
            # Disconnect the bot from the voice channel
            await interactions.guild.voice_client.disconnect()
        except Exception as e:
            print(f"Error in the leave command: {e}")
            raise e