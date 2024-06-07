import discord
from discord.ext import commands
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("utility.py", conf.LOGS_PATH)
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
            logger.error("User is not in a voice channel.")
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
            logger.error(f"An error occurred when trying to join the channel. {e}")
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
            logger.error(f"Error in the leave command: {e}")
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
            logger.error(f"Error while trying to create an embed message in nowplaying.py: {e}")
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
            logger.error(f"Error while trying to get the user ID from the sender object: {e}")
            return None

    def create_gambling_embed_message(symbols, profit, balance):
        try:
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
            # Add balance with 2 decimal places
            embed.add_field(name="Balance", value=f'{"{:.2f}".format(balance)} :coin:', inline=False)


            # Add footer with additional information
            embed.set_footer(text="Feeling lucky? Spin again!")

            return embed
        except Exception as e:
            logger.error(f"Error while trying to create an embed message in gambling.py: {e}")
            return None
        
    
    @staticmethod
    def create_slots_9x9_embed_message(grid, bet, payout, balance):
        try:
            padding_title = "⠀" * 4
            # Create the embed message with a vibrant color and a dynamic title
            embed = discord.Embed(
                title=f"{padding_title}🎰 3x3 Slots 🎰",
                description=f"{padding_title}🔥 Try your luck! 🔥",
                color=discord.Color.gold()
            )
            padding = "⠀" * 8
            # Add each row with emojis to represent the slot items
            for i, row in enumerate(grid):
                row_with_emojis = f"{padding}║ " + " ║ ".join(row) + " ║"
                embed.add_field(name="\u200b", value=row_with_emojis, inline=False)

            # Format the bet, payout, and balance details with bold text and emojis
            embed.add_field(name="💸 Bet Amount", value=f"**{bet}** coins", inline=True)
            embed.add_field(name="💰 Payout", value=f"**{payout}** coins", inline=True)
            embed.add_field(name="💼 New Balance", value=f"**{balance}** coins", inline=True)

            # Add a celebratory or consoling message based on the payout
            if payout > 0:
                embed.add_field(name=f"{padding_title}🎉 Congratulations! 🎉", value=f"{padding_title}You've won **{payout}** dollars! 🥳", inline=False)
            else:
                embed.add_field(name=f"{padding_title}💔 Better luck next time! 💔", value=f"{padding_title}A gambler never gives up! 🍀", inline=False)

            return embed
        except Exception as e:
            logger.error(f"Error while trying to create an embed message in slots.py: {e}")
            return None

        
    async def create_leaderboard_embed(self, interactions, users):
        try:
            """
            Creates an embed message that contains the top 10 users.

            Args:
                interactions (discord.Interaction): The interaction object to fetch user information.
                users (list): A list of user dictionaries containing 'user_id', 'level', and 'experience'.

            Returns:
                discord.Embed: The constructed leaderboard embed message.
            """
            # Create an embed message with a title and color
            embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())

            # Emojis for the top 3 ranks
            rank_emojis = ["🥇", "🥈", "🥉"]
            
            for i, user in enumerate(users):
                # Get the user using their user_id
                user_obj = await interactions.client.fetch_user(user["user_id"])

                # Determine the rank emoji
                rank_emoji = rank_emojis[i] if i < len(rank_emojis) else f"{i + 1}."

                # Add the user to the embed with their rank, level, and experience
                embed.add_field(
                    name=f"{rank_emoji} {user_obj.display_name}",
                    value=f"**Level:** {user['level']} | **Experience:** {user['experience']}",
                    inline=False
                )

            return embed
        except Exception as e:
            logger.error(f"Error while trying to create an embed message in leaderboard.py: {e}")
            return None
        
    def create_rank_embed(self, interactions,  rank):
        try:
                
            # Create an embed message that contains the user's rank
            embed = discord.Embed(title="Rank", color=discord.Color.gold())
            
            # Get the user profile picture
            embed.set_thumbnail(url=interactions.user.avatar)
            # Put a border around the user's profile picture
            
            # Add the user's name to the embed message
            embed.add_field(name="Your Name", value=f"{interactions.user.name}", inline=False)
            
            # Add the user's rank to the embed message
            embed.add_field(name="Your level", value=f"**{rank}**", inline=False)
            
            return embed
        
        except Exception as e:
            logger.error(f"Error while trying to create an embed message in rank.py: {e}")
            return None
        
    def is_message_command(self, message, commands):
        # Check if the the string after the / is a command
        return message.content.split()[0][1:] in commands
    
    def is_emoji(self, message):
        # Check if the message is a custom Discord emoji reaction
        if message.startswith("<:") and message.endswith(">"):
            parts = message[2:-1].split(":")
            return len(parts) == 2 and parts[1].isdigit()
        return False

    
    def is_command(self, message):
        # Check if the message is a command
        return message.startswith("/")
    
    def create_case_embed(self, balance: float, profit: float, prices: float, wear_level:str, gun_float:float, weapon_name:str, weapon_pattern:float, weapon_image:str, is_stattrak:bool):
        try:
            embed = discord.Embed(title="🎉 Case Opening Results 🎉", color=discord.Color.gold())
            
            if is_stattrak:
                weapon_name = "StatTrak™ " + weapon_name
                
            # Add weapon name and pattern
            embed.add_field(name="🔫 Weapon", value=f"**{weapon_name}** | *{weapon_pattern}*", inline=False)   
            
            # Add weapon image     
            embed.set_thumbnail(url=weapon_image)
            
            # Add wear level
            embed.add_field(name="🛠️ Wear Level", value=f"**{wear_level}**", inline=True)
            
            # Add user balance
            embed.add_field(name="💰 Current Balance", value=f"**${balance:.2f}**", inline=True)
            
            # Add profit or loss
            if profit > 0:
                embed.add_field(name="📈 Profit", value=f"+$**{profit:.2f}**", inline=True)
            else:
                embed.add_field(name="📉 Loss", value=f"-$**{-profit:.2f}**", inline=True)
            
            # Add weapon price
            embed.add_field(name="💵 Weapon Price", value=f"$**{float(prices):.2f}**", inline=True)
            
            # Add gun float value
            embed.add_field(name="📊 Float Value", value=f"**{gun_float:.5f}**", inline=True)
        
            return embed

        except Exception as e:
            logger.error(f"Error while trying to create an embed message in case.py: {e}")
            return None
        
    def create_open_case_embed_message(self, case):
        # find the case image
        case_image = case["image"]
        
        # Create an embed message with the case image
        embed = discord.Embed(title="🎉 Case Opening 🎉", color=discord.Color.gold())
        
        # Add the case image to the embed message
        embed.set_image(url=case_image)
        # Add the case name to the embed message
        embed.add_field(name="Case", value=case["name"], inline=False)
        # Add a field for the price of the case to the embed message
        embed.add_field(name="Price", value=f"$5", inline=True)
        
        return embed
        
        
        
    def bot_check_session(self, session):
        # Check if the song session is None
        if session is None:
            return False
        return True