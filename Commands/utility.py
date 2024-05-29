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
            print(channel)
            if not channel:
                await interactions.response.send_message(interactions.user.mention + " is not in a voice channel.")
        except AttributeError:
            await interactions.response.send_message(interactions.user.mention + " is not in a voice channel.")
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
            
            # Check if the bot is in a voice channel
            if voice_client:
                # Check if the bot is in the correct channel
                if voice_client.channel.id == user_voice.channel.id:
                    return
                
            # Connect to the voice channel                
            await user_voice.channel.connect(reconnect=True)

            # Send a message that the bot joined the channel
            #await interactions.response.send_message(f"Joined {channel}")
        except Exception as e:
            print(f"An error occurred when trying to join the channel. {e}")
            raise e
        

        
    async def leave(self, interactions):
        """
        Disconnects the bot from the voice channel it is currently in.

        Parameters:
        - interactions: The interaction object representing the command invocation.

        Returns:
        None
        """
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
        
    def now_playing_song_embed(song_title, thumbnail, song_duration):
        """
        Create an embed message that contains the title of the song, the thumbnail, and the duration.

        Args:
            song_title (str): The title of the song.
            thumbnail (str): The URL of the thumbnail image.
            song_duration (str): The duration of the song.

        Returns:
            discord.Embed: The embed message containing the song information.
        """
        try:
            embed = discord.Embed(
                title="Now Playing", description=song_title, color=discord.Color.green())

            if thumbnail is not None:
                embed.set_thumbnail(url=thumbnail)
            if song_duration is not None:
                embed.add_field(name="Duration", value=song_duration)

            return embed
        except Exception as e:
            print(f"Error while trying to create an embed message in nowplaying.py: {e}")
            return
        
    def get_userid_from_sender(sender):
        """
        Get the user ID from the sender object.

        Args:
            sender (discord.User): The sender object.

        Returns:
            int: The user ID.
        """
        try:
            return sender.id
        except Exception as e:
            print(f"Error while trying to get the user ID from the sender object: {e}")
            return None

    def create_gambling_embed_message(symbols, profit, balance):
        # Determine the color based on profit
        if profit > 0:
            color = discord.Color.green()
            result = "YOU WON!"
            field_value = f"**Profit:** {profit} dollars :moneybag:"
        elif profit < 0:
            color = discord.Color.red()
            result = "YOU LOST!"
            field_value = f"**Loss:** {-profit} dollars :money_with_wings:"
        else:
            color = discord.Color.gold()
            field_value = "**No Profit or Loss**"

        # Create the embed
        embed = discord.Embed(title="Slot Machine", color=color)

        # Add slot symbols
        symbols_str = " | ".join(symbols)
        embed.add_field(name="Slot Symbols", value=f"```{symbols_str}```", inline=False)

        # Add result without a title
        embed.add_field(name=" ", value=f"**{result}**", inline=False)
        
        # Add profit/loss and balance
        embed.add_field(name="Result", value=field_value, inline=False)
        embed.add_field(name="Balance", value=f"{balance} :coin:", inline=False)

        # Add footer with additional information
        embed.set_footer(text="Feeling lucky? Spin again!")

        return embed
    
    @staticmethod
    def create_slots_9x9_embed_message(grid, payout):
        """
        Create an embed message for the 9x9 slot machine game result.

        Parameters:
        - grid (list): The grid representing the slot machine result.
        - payout (int): The payout amount.

        Returns:
        - discord.Embed: The embed message.
        """
        # Create the embed message
        embed = discord.Embed(
            title="Slot Machine Result",
            description="Here's the result of the 9x9 slot machine game:",
            color=discord.Color.blue()
        )

        # Add the grid to the embed message
        for row in grid:
            embed.add_field(name="\u200b", value=" | ".join(row), inline=False)

        # Add the payout amount to the embed message
        if payout > 0:
            embed.add_field(name="Congratulations!", value=f"You won {payout} dollars!", inline=False)
        else:
            embed.add_field(name="Better luck next time!", value="\u200b", inline=False)

        return embed
        
    def create_leaderboard_embed(self, users):
        # Create an embed message that contains the top 10 users
        embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
        
        # Add the users to the embed message
        for i, user in enumerate(users):
            embed.add_field(name=f"{i + 1}. {user['name']}", value=f"Experience: {user['experience']}", inline=False)
        
        return embed
        
    def create_rank_embed(self, rank):
        # Create an embed message that contains the user's rank
        embed = discord.Embed(title="Rank", color=discord.Color.gold())
        
        
        # Add the user's rank to the embed message
        embed.add_field(name="Your Rank", value=f"{rank}", inline=False)
        
        return embed
    
    def is_message_command(self, message, commands):
        # Get all commands
        
        print(commands)
        # Check if the the string after the / is a command
        return message.content.split()[0][1:] in commands
    
        