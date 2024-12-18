import discord
from discord.ui import Button, View
from discord.ext import commands
from Config.logging import setup_logging
from Config.config import conf

from Commands.Services.database import Database
# Create a logger for this file
logger = setup_logging("utility.py", conf.LOGS_PATH)

class VoiceManager:
    async def join(self, interactions: discord.Interaction, message=None):
        """
        Join the voice channel.

        This command makes the bot join the voice channel of the user who sent the command.
        If the bot is already in the correct channel, it will send a message indicating that it is already in the channel.
        If the bot is in a different channel, it will move to the correct channel.
        If the bot is not in any channel, it will connect to the voice channel.
        """
        try:


            if not interactions.channel:
                if message is None:
                    await interactions.response.send_message(interactions.user.mention + " is not in a voice channel.")
                else:
                    await message.edit(content=interactions.user.mention + " is not in a voice channel.")
        except AttributeError:
            if message is None:
                await interactions.response.send_message(interactions.user.mention + " is not in a voice channel.")
            else:
                await message.edit(content=interactions.user.mention + " is not in a voice channel.")
            logger.error("User is not in a voice channel.")
            return
        try:

            # Check if the user is in a voice channel
            if not interactions.user.voice:
                await message.edit(content=interactions.user.mention + " is not in a voice channel.")
                return

            # Create a voice client variable
            voice_client = interactions.guild.voice_client

            # Check if the bot is in a voice channel
            if voice_client:
                # Check if the bot is in the correct channel
                if voice_client.channel.id == interactions.user.voice.channel.id:
                    return

            # Connect to the voice channel
            await interactions.user.voice.channel.connect(reconnect=True)
            # Send a message that the bot joined the channel
            # await interactions.response.send_message(f"Joined {channel}")
        except Exception as e:
            logger.error(
                f"An error occurred when trying to join the channel. {e}")
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
            # Disconnect the bot from the voice channel
            await interactions.guild.voice_client.disconnect()
        except Exception as e:
            logger.error(f"Error in the leave command: {e}")
            raise e

class Utility():
    def __init__(self):
        self.database = Database.getInstance()


    def is_emoji(self, message):
        # Check if the message is a custom Discord emoji reaction
        if message.startswith("<:") and message.endswith(">"):
            parts = message[2:-1].split(":")
            return len(parts) == 2 and parts[1].isdigit()
        return False

    def format_inexistant_prices(self, sticker_price):
        DEFAULT_PRICE = 1200
        
        time_periods = ["last_24h", "last_7d",
                        "last_30d", "last_90d", "last_ever"]
        # Iterate over the time periods
        for i in range(len(time_periods)):
            current_period = time_periods[i]

            # If the current period price is None, find the next available non-None price
            if sticker_price[current_period] is None:
                for j in range(i + 1, len(time_periods)):
                    next_period = time_periods[j]
                    if sticker_price[next_period] is not None:
                        sticker_price[current_period] = sticker_price[next_period]
                        break
                else:
                    # If no non-None value is found, set it to 0
                    sticker_price[current_period] = DEFAULT_PRICE

        return sticker_price["last_24h"]

    async def add_buttons(self, message, function_keep, function_sell, weapon):
        keep_button = Button(style=discord.ButtonStyle.green,
                             label="Keep", custom_id="keep")
        sell_button = Button(style=discord.ButtonStyle.red,
                             label="Sell", custom_id="sell")

        async def keep_callback(interaction):
            await function_keep(interaction, weapon, message)

        async def sell_callback(interaction):
            await function_sell(interaction, weapon, message)

        keep_button.callback = keep_callback
        sell_button.callback = sell_callback

        # Add buttons to the message
        view = View(timeout=5)
        view.add_item(keep_button)
        view.add_item(sell_button)
        await message.edit(view=view)

    async def disable_buttons(self, message):
        view = View()
        await message.edit(view=view, embed=None)

    def create_weapon_from_info(self, weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, weapon_image, is_stattrak, color, weapon_price):
        return {
            "name": weapon_name,
            "pattern": weapon_pattern,
            "image": weapon_info["image"],
            "float": round(gun_float, 5),
            "wear": wear_level,
            "stattrak": is_stattrak,
            "color": color,
            "price": round(weapon_price, 2)
        }

    def create_color_text(self, color):
        color_text = ""
        # Blue text
        if hex(color) == "0x4b69ff":
            color_text = "🟦" 
        # Purple text
        elif hex(color) == "0x8847ff":
            color_text = "🟪"  
        # Pink text
        elif hex(color) == "0xd32ce6":
            color_text = "🟪" 
        # Red text
        elif hex(color) == "0xeb4b4b":
            color_text = "🟥"  # Red square emoji
        # Yellow text
        elif hex(color) == "0xade55c":
            color_text = "🟨"  # Yellow square emoji

        return color_text

    async def add_page_buttons(self, message, inventory,  function_previous, function_next):
        previous_button = Button(
            style=discord.ButtonStyle.green, label="⬅️", custom_id="previous")
        next_button = Button(style=discord.ButtonStyle.green,
                             label="➡️", custom_id="next")
        # Add functions to the buttons

        async def previous_callback(interactions):
            await function_previous(interactions, inventory, message)

        async def next_callback(interactions):
            await function_next(interactions, inventory, message)
        previous_button.callback = previous_callback
        next_button.callback = next_callback

        # Add buttons to the message
        view = View()
        view.add_item(previous_button)
        view.add_item(next_button)
        await message.edit(view=view)

    def bot_check_session(self, session):
        # Check if the song session is None
        if session is None:
            return False
        return True

    def has_sufficient_balance(self, user, amount):
        # Check if the user has sufficient balance
        return user["balance"] >= amount

    def calculate_profit(self, total, item_price):
        # Calculate the profit
        return total - item_price

    def add_experience(self, interactions, payout):
        if payout > 0:
            # Update the user's experience
            self.database.update_user_experience(interactions, payout)

    def check_user(self, interactions, saved_id):
        if interactions.user.id != saved_id:
            return False
        return True


class EmbedMessage():
    def __init__(self):
        self.utility = Utility()

    def create_coinflip_embed_message(self, interactions, bet, coin, result_emoji, command_user, opposing_user, winner, winnings):
        try:

            balance = command_user["balance"]
            opponent_balance = opposing_user["balance"]

            # Find the opposing user name

            # Embed message for the coinflip command
            embed = discord.Embed(
                title="Coinflip Results",
                color=discord.Color.gold()
            )
            # Add the user's name and the opponent to the embed message
            embed.add_field(
                name="👤 User", value=f"**{interactions.user.display_name}**", inline=False)
            embed.add_field(
                name="👤 Opponent", value=f"**{opposing_user['user_name']}**", inline=False)

            # Add the bet amount and the coin result to the embed message
            embed.add_field(name="💰 Bet Amount",
                            value=f"**${bet}**", inline=True)
            embed.add_field(name="🪙 Coin Result",
                            value=f"**{result_emoji}**", inline=True)

            # Add the user and opponents balance to the embed message
            embed.add_field(name="🏦 Your Balance",
                            value=f"**${balance:.2f}**", inline=False)
            embed.add_field(name="🏦 Opponent Balance",
                            value=f"**${opponent_balance:.2f}**", inline=True)

            # Add the winner of the coinflip to the embed message
            embed.add_field(name="🎉 Winner",
                            value=f"**{winner}**", inline=False)
            embed.add_field(name="💰 Winnings",
                            value=f"**${winnings}**", inline=False)

            return embed
        except Exception as e:
            logger.error(
                f"Error while creating an embed message in coinflip.py: {e}")
            return None

    def create_roll_embed_message(self, interactions, bet, number, rolled_number, winnings, balance):
        color, value = self.get_result_color_and_value(winnings, bet)

        embed = discord.Embed(
            title="🎲 Roll Result 🎲",
            color=color
        )

        embed.add_field(
            name="👤 User", value=f"**{interactions.user.name}**", inline=False)
        embed.add_field(name="Result", value=value, inline=False)

        fields = [
            ("🎲 Your Number", f"**{number}**", True),
            ("🎲 Rolled Number", f"**{rolled_number}**", True),
            ("💰 Bet Amount", f"**${bet:.2f}**", True),
            ("🏦 Winnings", f"**${winnings:.2f}**", True),
            ("💼 Balance", f"**${balance:.2f}**", True)
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        return embed

    def get_result_color_and_value(self, winnings, bet):
        if winnings == bet * 10:
            return discord.Color.gold(), f"🎉 Jackpot! 🎉"
        elif winnings > 0:
            return discord.Color.green(), f"🎉 You win! 🎉"
        else:
            return discord.Color.red(), f"😢 You lose! Better luck next time. 😢"

    def create_rockpaperscissors_embed(self, user_choice, bot_choice, result, bet, balance, user_name, profit, amount_betted):
        color, value = self.get_rps_result_details(result)

        embed = discord.Embed(
            title="Rock-Paper-Scissors",
            color=color
        )

        embed.add_field(name=f"👤 {user_name}'s Choice",
                        value=f"**{user_choice.capitalize()}**", inline=True)
        embed.add_field(name="🤖 My Choice",
                        value=f"**{bot_choice.capitalize()}**", inline=True)
        embed.add_field(name="🎲 Result",
                        value=f"**{result.capitalize()}**", inline=False)

        fields = [
            ("💰 Bet Amount", f"**${amount_betted:.2f}**", True),
            ("📈 Profit/Loss", f"**${profit:.2f}**", True),
            ("🏦 Total", f"**${(bet + profit):.2f}**", True),
            ("💼 Balance", f"**${balance:.2f}**", True)
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        return embed

    def get_rps_result_details(self, result):
        # Normalize the result string to lower case
        result = result.lower().strip()

        # Map results to colors and values
        result_colors = {
            "you win!": (discord.Color.green(), "Congratulations! You won!"),
            "you lose!": (discord.Color.red(), "Sorry, you lost.")
        }

        # Determine the color and value based on the result
        return result_colors.get(result, (discord.Color.gold(), "It's a draw!"))

    def create_inventory_embed_message(self, user_inventory, page, username):
        embed = discord.Embed(title="🎒 Inventory", color=discord.Color.gold())
        embed.add_field(name="👤 User", value=f"**{username}**", inline=False)

        if not user_inventory:
            embed.add_field(name="No items",
                            value="Your inventory is empty.", inline=False)
            return embed

        try:
            # Sort inventory by price in descending order
            user_inventory = sorted(
                user_inventory, key=lambda x: x["price"], reverse=True)

            # Calculate pagination
            start_index = page * 10
            end_index = (page + 1) * 10
            items = user_inventory[start_index:end_index]

            if not items:
                embed.add_field(
                    name="Invalid Page", value="There are no items on this page.", inline=False)
                return embed

            # Add items to embed
            for item in items:
                color_text = self.utility.create_color_text(item['color'])
                embed.add_field(
                    name=f"{color_text} {item['name']} | {item['pattern']}",
                    value=f"**Price:** ${item['price']:.2f}",
                    inline=False
                )

            # Calculate total value
            total_value = sum(item["price"] for item in user_inventory)
            embed.add_field(name="💰 Total Value",
                            value=f"**${total_value:.2f}**", inline=False)

        except Exception as e:
            logger.error(
                f"Error while creating an inventory embed message: {e}")
            return None

        return embed

    def create_sticker_embed(self, sticker, balance, sticker_price, profit, color):
        try:
            embed = discord.Embed(
                title="🎉 Sticker Opening Results 🎉",
                color=discord.Color(color)
            )

            # Add sticker details
            embed.add_field(name="🎨 Sticker",
                            value=f'**{sticker["name"]}**', inline=False)
            embed.set_thumbnail(url=sticker["image"])

            # Add balance, profit/loss, and sticker price
            fields = [
                ("💰 Current Balance", f"**${balance:.2f}**", True),
                ("📈 Profit" if profit > 0 else "📉 Loss",
                 f"{'+' if profit > 0 else '-'}${abs(profit):.2f}", True),
                ("💵 Sticker Price", f"**${sticker_price:.2f}**", True)
            ]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

        except Exception as e:
            logger.error(
                f"Error while creating an embed message in sticker.py: {e}")
            return None

        return embed

    def create_open_case_embed_message(self, case, title: str, price: float):
        try:
            # Validate case data
            if not case or "image" not in case or "name" not in case:
                raise ValueError("Invalid case data provided.")

            # Create the embed message with a gold color
            embed = discord.Embed(
                title=f"🎉 {title} Opening 🎉",
                color=discord.Color.gold()
            )

            # Add the case image and details
            embed.set_image(url=case["image"])
            embed.add_field(name="Case", value=f'**{case["name"]}**', inline=False)
            embed.add_field(name="Price", value=f"**${price:.2f}**", inline=True)

            return embed
        except Exception as e:
            logger.error(f"Error creating open case embed: {e}")
            return None  


    def create_case_embed(self, data):
        try:
            # Safely extract data with defaults
            balance = data.get("balance", 0.0)
            profit = data.get("profit", 0.0)
            weapon = data.get("weapon", {})
            weapon_info = data.get("info", {})
            price = data.get("price", 0.0)
            wear_level = data.get("wear", "Unknown")
            gun_float = data.get("float", 0.0)
            weapon_name = data.get("name", "Unknown Weapon")
            weapon_pattern = data.get("pattern", "Unknown Pattern")
            is_stattrak = data.get("stattrak", False)
            is_souvenir = data.get("is_souvenir", False)
            color = data.get("color", 0xFFFFFF)  # Default white color
            user_nickname = data.get("user_nickname", "Unknown User")

            # Format weapon name
            if is_stattrak:
                weapon_name = f"StatTrak™ {weapon_name}"
            if is_souvenir:
                weapon_name = f"Souvenir {weapon_name}"

            # Create the embed message
            embed = discord.Embed(
                title="🎉 Case Opening Results 🎉",
                color=discord.Color(color)
            )

            embed.add_field(name="👤 User", value=f"**{user_nickname}**", inline=False)
            embed.add_field(
                name="🔫 Weapon",
                value=f"**{weapon_name}** | *{weapon_pattern}*",
                inline=False
            )
            embed.set_thumbnail(url=weapon_info.get("image", ""))

            stats = [
                ("🛠️ Wear Level", f"**{wear_level}**"),
                ("💰 Current Balance", f"**${balance:.2f}**"),
                ("📊 Float Value", f"**{gun_float:.5f}**"),
                ("💵 Weapon Price", f"**${price:.2f}**"),
                ("📈 Profit" if profit > 0 else "📉 Loss",
                f"+$**{profit:.2f}**" if profit > 0 else f"-$**{-profit:.2f}**")
            ]

            for name, value in stats:
                embed.add_field(name=name, value=value, inline=True)

            return embed

        except Exception as e:
            logger.error(f"Error creating embed message: {e}")
            return None



    def create_keep_message(self, user_name, weapon):
        # Create a message to keep the weapon
        return f"{user_name} has decided to keep the **{weapon['wear']} {weapon['name']} | {weapon['pattern']}** worth $**{weapon['price']:.2f}**."

    def create_sell_message(self, user_name, weapon):
        # Create a message to sell the weapon
        return f"{user_name} has decided to sell the **{weapon['wear']} {weapon['name']} | {weapon['pattern']}** worth $**{weapon['price']:.2f}**."

    async def on_member_join_message(self, member):
        # Function to create an embed message when a member joins the server
        try:
            # Create an embed message
            embed = discord.Embed(
                title="Welcome to the server!",
                description=f"""Welcome to the server, {
                    member.display_name}! We're glad to have you here.""",
                color=discord.Color.green()
            )

            # Set the member's avatar as the thumbnail
            embed.set_thumbnail(url=member.avatar)

            return embed

        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in on_member_join_message: {e}")
            return None

    async def on_member_leave_message(self, member):
        # Function to create an embed message when a member leaves the server
        try:
            # Create an embed message
            embed = discord.Embed(
                title="Goodbye!",
                description=f"Goodbye, {member.display_name}! We'll miss you.",
                color=discord.Color.red()
            )

            # Set the member's avatar as the thumbnail
            embed.set_thumbnail(url=member.avatar)

            return embed
        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in on_member_remove_message: {e}")
            return None

    def now_playing_song_embed(self, song_title, thumbnail=None, song_duration=None):
        """
        Create an embed message containing the title of the song, the thumbnail, and the duration.

        Args:
            song_title (str): The title of the song.
            thumbnail (str, optional): The URL of the thumbnail image. Defaults to None.
            song_duration (str, optional): The duration of the song. Defaults to None.

        Returns:
            discord.Embed: The embed message containing the song information.
        """
        try:
            # Create the embed message
            embed = discord.Embed(
                title="Now Playing",
                description=song_title,
                color=discord.Color.green()
            )

            # Optionally set the thumbnail
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)

            # Optionally add the duration field
            if song_duration:
                embed.add_field(name="Duration",
                                value=song_duration, inline=False)

            return embed

        except Exception as e:
            logger.error(f"Error creating 'Now Playing' embed message: {e}")
            return None

    def create_gambling_embed_message(self, symbols, profit, balance):
        try:
            # Determine color and result message based on profit
            color, result_message, profit_loss_message = self.determine_gambling_color_message(
                profit)
            # Create the embed
            embed = discord.Embed(title="Slot Machine", color=color)

            # Add slot symbols
            embed.add_field(name="Slot Symbols", value=f"""```{
                            ' | '.join(symbols)}```""", inline=True)

            # Prepare fields for result, profit/loss, and balance
            fields = [
                ("Result", f"**{result_message}**"),
                ("Profit/Loss", profit_loss_message),
                ("Balance", f"${balance:.2f} :coin:")
            ]

            for name, value in fields:
                embed.add_field(name=name, value=value, inline=False)

            # Add footer with additional information
            embed.set_footer(text="Feeling lucky? Spin again!")

            return embed

        except Exception as e:
            logger.error(
                f"Error while creating an embed message in gambling.py: {e}")
            return None

    def determine_gambling_color_message(self, profit):
        # Determine the color and message based on the profit
        if profit > 0:
            color = discord.Color.green()
            message = "YOU WON!"
            profit_loss_message = f"**Profit:** ${profit:.2f} :moneybag:"

        elif profit < 0:
            color = discord.Color.red()
            message = "YOU LOST!"
            profit_loss_message = f"**Loss:** ${-profit:.2f} :money_with_wings:"

        else:
            color = discord.Color.gold()
            message = "No Profit or Loss"
            profit_loss_message = "**No Profit or Loss**"
        return color, message, profit_loss_message

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
            embed = discord.Embed(title="🏆 Leaderboard",
                                  color=discord.Color.gold())

            # Emojis for the top 3 ranks
            rank_emojis = ["🥇", "🥈", "🥉"]

            for i, user in enumerate(users):
                # Get the user using their user_id
                user_obj = await interactions.client.fetch_user(user["user_id"])

                # Determine the rank emoji
                rank_emoji = rank_emojis[i] if i < len(
                    rank_emojis) else f"{i + 1}."

                # Add the user to the embed with their rank, level, and experience
                embed.add_field(
                    name=f"{rank_emoji} {user_obj.display_name}",
                    value=f"""**Level:** {user['level']} | **Experience:** {
                        user['experience']:.2f} | **Total Bet:** {user['total_bet']:.2f}""",
                    inline=False
                )

            return embed
        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in leaderboard.py: {e}")
            return None

    def create_rank_embed(self, interactions, user):
        try:
            rank, total_bet = user["level"], user["total_bet"]

            # Create an embed message that contains the user's rank
            embed = discord.Embed(title="Rank", color=discord.Color.gold())

            # Get the user profile picture
            embed.set_thumbnail(url=interactions.user.avatar)

            # Add the user's name to the embed message
            embed.add_field(name="Your Name", value=f""" {
                            interactions.user.name} """, inline=False)

            # Add the user's rank to the embed message
            embed.add_field(name="Your level",
                            value=f"**{rank}**", inline=False)

            # Add the total bet amount to the embed message
            embed.add_field(name="Total Bet",
                            value=f"$**{total_bet:.2f}**", inline=False)

            return embed

        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in rank.py: {e}")
            return None

    def create_embed_user_information(self, member):
        try:
            # Create the embed for user information
            embed = discord.Embed(
                title=f'User Information - {member.display_name}',
                color=member.color
            )

            # Add user avatar
            embed.set_thumbnail(url=member.avatar)

            # Prepare fields for user information
            fields = [
                ("Username", member.name),
                ("User ID", member.id),
                ("Joined Server On", member.joined_at.strftime('%Y-%m-%d %H:%M:%S')),
                ("Account Created On", member.created_at.strftime('%Y-%m-%d %H:%M:%S'))
            ]

            # Add fields to embed
            for name, value in fields:
                embed.add_field(name=name, value=value, inline=True)

            return embed

        except Exception as e:
            logger.error(f"Error creating user information embed: {e}")
            return None

    def create_work_embed(self, interactions, job, amount_earned, balance):
        try:
            # Create the embed message
            embed = discord.Embed(
                title="Work Results",
                description=f"""You worked as a **{job['title']}** {
                    job['icon']} and earned **${amount_earned:.2f}**!""",
                color=discord.Color.green()
            )

            # Add balance field
            embed.add_field(name="💰 Balance",
                            value=f"**${balance:.2f}**", inline=False)

            # Add salary range field
            salary_range = f"""${job['earnings_range'][0]:.2f} - ${job['earnings_range'][1]:.2f}"""

            embed.add_field(name="💼 Salary Range",
                            value=f"**{salary_range}**", inline=False)

            # Set user avatar as the thumbnail
            embed.set_thumbnail(url=interactions.user.avatar)

            return embed

        except Exception as e:
            logger.error(f"Error creating work embed message: {e}")
            return None
