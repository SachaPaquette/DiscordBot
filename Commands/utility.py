import discord
from discord.ui import Button, View
from discord.ext import commands
from Config.logging import setup_logging
from Config.config import conf

from Commands.database import Database
# Create a logger for this file
logger = setup_logging("utility.py", conf.LOGS_PATH)


class Utility():
    def __init__(self):
        self.database = Database.getInstance()

    async def join(self, interactions: discord.Interaction, message=None):
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

            if not channel:
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
            # Create a user voice variable
            user_voice = interactions.user.voice

            # Check if the user is in a voice channel
            if not user_voice:
                await message.edit(content=interactions.user.mention + " is not in a voice channel.")
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

            # Send a message that the bot is leaving
            await interactions.response.send_message("Leaving voice channel.")
            # Disconnect the bot from the voice channel
            await interactions.guild.voice_client.disconnect()
        except Exception as e:
            logger.error(f"Error in the leave command: {e}")
            raise e

    def is_emoji(self, message):
        # Check if the message is a custom Discord emoji reaction
        if message.startswith("<:") and message.endswith(">"):
            parts = message[2:-1].split(":")
            return len(parts) == 2 and parts[1].isdigit()
        return False

    def format_inexistant_prices(self, sticker_price):

        time_periods = ["last_24h", "last_7d", "last_30d", "last_90d"]
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
                    sticker_price[current_period] = 1200

        return sticker_price["last_24h"]

    async def add_buttons(self, message, function_keep, function_sell, weapon):
        keep_button = Button(style=discord.ButtonStyle.green,
                             label="Keep", custom_id="keep")
        sell_button = Button(style=discord.ButtonStyle.red,
                             label="Sell", custom_id="sell")

        # Add functions to the buttons
        async def keep_callback(interactions):
            await function_keep(interactions, weapon, message)

        async def sell_callback(interactions):
            await function_sell(interactions, weapon, message)

        keep_button.callback = keep_callback
        sell_button.callback = sell_callback

        # Add buttons to the message
        view = View(timeout=5)
        view.add_item(keep_button)
        view.add_item(sell_button)
        await message.edit(view=view)

    async def disable_buttons(self, interactions, message):
        # Disable the buttons
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
            color_text = "🟦"  # Blue square emoji
        # Purple text
        elif hex(color) == "0x8847ff":
            color_text = "🟪"  # Purple square emoji
        # Pink text
        elif hex(color) == "0xd32ce6":
            # Pink square emoji (no exact pink emoji available)
            color_text = "🟩"
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


class EmbedMessage():
    def __init__(self):
        self.utility = Utility()

    def create_coinflip_embed_message(self, interactions, bet, result, result_emoji, winner, winnings, balance, opponent_balance):
        # Embed message for the coinflip command
        embed = discord.Embed(
            title="Coinflip Results",
            color=discord.Color.gold()
        )
        # Add the user's name and the opponent to the embed message
        embed.add_field(
            name="👤 User", value=f"**{interactions.user.name}**", inline=False)
        embed.add_field(name="👤 Opponent", value=f"**{winner}**", inline=False)

        # Add the bet amount and the coin result to the embed message
        embed.add_field(name="💰 Bet Amount", value=f"**${bet}**", inline=True)
        embed.add_field(name="🪙 Coin Result",
                        value=f"**{result}**", inline=True)

        # Add the user and opponents balance to the embed message
        embed.add_field(name="🏦 Your Balance",
                        value=f"**${balance:.2f}**", inline=False)
        embed.add_field(name="🏦 Opponent Balance",
                        value=f"**${opponent_balance:.2f}**", inline=True)

        # Add the winner of the coinflip to the embed message
        embed.add_field(name="🎉 Winner", value=f"**{winner}**", inline=False)
        embed.add_field(name="💰 Winnings",
                        value=f"**${winnings}**", inline=False)

        return embed

    def create_roll_embed_message(self, interactions, bet, number, rolled_number, winnings, balance):

        # Determine the color based on the winnings
        if winnings > 0:
            color = discord.Color.green()
            value = f"🎉 You win! 🎉"
        else:
            color = discord.Color.red()
            value = f"😢 You lose! Better luck next time noob. 😢"
        # Create the embed message
        embed = discord.Embed(
            title="🎲 Roll Result 🎲",
            color=color
        )

        # Add the user's name to the embed message
        embed.add_field(
            name="👤 User", value=f"**{interactions.user.name}**", inline=False)
        embed.add_field(name="Result", value=f"{value}", inline=False)

        # Add the user's number, the rolled number, the bet amount, the winnings, and the balance to the embed message
        embed.add_field(name="🎲 Your Number",
                        value=f"**{number}**", inline=True)
        embed.add_field(name="🎲 Rolled Number",
                        value=f"**{rolled_number}**", inline=True)
        embed.add_field(name="💰 Bet Amount",
                        value=f"**${bet:.2f}**", inline=True)
        embed.add_field(name="🏦 Winnings",
                        value=f"**${winnings:.2f}**", inline=True)
        embed.add_field(name="💼 Balance",
                        value=f"**${balance:.2f}**", inline=True)

        return embed

    def create_rockpaperscissors_embed(self, user_choice, bot_choice, result, bet, balance, user_name, profit, amount_betted):
        # Normalize the result string to lower case
        result = result.lower().strip()

        # Determine the color based on the result
        if result == "you win!":
            color = discord.Color.green()
        elif result == "you lose!":
            color = discord.Color.red()
        else:
            color = discord.Color.gold()

        # Create the embed message
        embed = discord.Embed(
            title="Rock-Paper-Scissors",
            color=color
        )

        # Add fields with enhanced formatting
        embed.add_field(name=f"👤 {user_name}'s Choice",
                        value=f"**{user_choice.capitalize()}**", inline=True)
        embed.add_field(name="🤖 My Choice",
                        value=f"**{bot_choice.capitalize()}**", inline=True)
        embed.add_field(name="🎲 Result",
                        value=f"**{result.capitalize()}**", inline=False)

        # Add the bet amount, profit/loss, and balance with emojis
        embed.add_field(name="💰 Bet Amount",
                        value=f"**${amount_betted:.2f}**", inline=True)
        embed.add_field(name="📈 Profit/Loss",
                        value=f"**${profit:.2f}**", inline=True)
        embed.add_field(
            name="🏦 Total", value=f"**${(bet + profit):.2f}**", inline=True)
        embed.add_field(name="💼 Balance",
                        value=f"**${balance:.2f}**", inline=True)

        return embed

    def create_inventory_embed_message(self, user_inventory, page, username):
        try:
            embed = discord.Embed(title="🎒 Inventory",
                                  color=discord.Color.gold())
            embed.add_field(
                name="👤 User", value=f"**{username}**", inline=False)

            if not user_inventory:
                embed.add_field(name="No items",
                                value="Your inventory is empty.", inline=False)
                return embed

            user_inventory = sorted(
                user_inventory, key=lambda x: x["price"], reverse=True)

            # Get the 10 items of the current page
            items = user_inventory[page * 10: (page + 1) * 10]
            if not items:
                embed.add_field(
                    name="Invalid Page", value="There are no items on this page.", inline=False)
                return embed

            for item in items:
                embed.add_field(
                    name = f"{self.utility.create_color_text(item['color'])} {item['name']} | {item['pattern']}",
                    value=f"**Price:** ${item['price']:.2f}",
                    inline=False
                )

            embed.add_field(name="💰 Total Value",
                            value=f"**${sum(item["price"] for item in user_inventory):.2f}**", inline=False)
            return embed
        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in inventory.py: {e}")
            return None

    def create_sticker_embed(self, sticker, balance, sticker_price, profit, color):
        try:
            embed = discord.Embed(
                title="🎉 Sticker Opening Results 🎉", color=discord.Colour(color))
            # Add sticker name
            embed.add_field(name="🎨 Sticker",
                            value=f'**{sticker["name"]}**', inline=False)

            # Add sticker image
            embed.set_thumbnail(url=sticker["image"])

            # Add user balance
            embed.add_field(name="💰 Current Balance",
                            value=f"**${balance:.2f}**", inline=True)

            # Add profit or loss
            if profit > 0:
                embed.add_field(name="📈 Profit",
                                value=f"+$**{profit:.2f}**", inline=True)
            else:
                embed.add_field(
                    name="📉 Loss", value=f"-$**{-profit:.2f}**", inline=True)

            # Add sticker price
            embed.add_field(name="💵 Sticker Price",
                            value=f"$**{float(sticker_price):.2f}**", inline=True)

            return embed

        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in sticker.py: {e}")
            return None

    def create_open_case_embed_message(self, case, title: str, price: float):
        # Create an embed message with the case image
        embed = discord.Embed(title=f"🎉 {title} Opening 🎉", color=discord.Color.gold())
        # Add the case image to the embed message
        embed.set_image(url=case["image"])
        # Add the case name to the embed message
        embed.add_field(name="Case", value=case["name"], inline=False)
        # Add a field for the price of the case to the embed message
        embed.add_field(name="Price", value=f"${price}", inline=True)
        return embed

    def create_case_embed(self, balance: float, profit: float, prices: float, wear_level: str, gun_float: float, weapon_name: str, weapon_pattern: float, weapon_image: str, is_stattrak: bool, color: str, user_nickname: str):
        try:
            embed = discord.Embed(
                title=f"🎉 Case Opening Results 🎉", color=discord.Colour(color))

            # Add username to the embed message
            embed.add_field(
                name="👤 User", value=f"**{user_nickname}**", inline=False)

            if is_stattrak:
                weapon_name = "StatTrak™ " + weapon_name

            # Add weapon name and pattern
            embed.add_field(
                name="🔫 Weapon", value=f"**{weapon_name}** | *{weapon_pattern}*", inline=False)

            # Add weapon image
            embed.set_thumbnail(url=weapon_image)

            # Add wear level
            embed.add_field(name="🛠️ Wear Level",
                            value=f"**{wear_level}**", inline=True)

            # Add user balance
            embed.add_field(name="💰 Current Balance",
                            value=f"**${balance:.2f}**", inline=True)

            # Add profit or loss
            if profit > 0:
                embed.add_field(name="📈 Profit",
                                value=f"+$**{profit:.2f}**", inline=True)
            else:
                embed.add_field(
                    name="📉 Loss", value=f"-$**{-profit:.2f}**", inline=True)

            # Add weapon price
            embed.add_field(name="💵 Weapon Price",
                            value=f"$**{float(prices):.2f}**", inline=True)

            # Add gun float value
            embed.add_field(name="📊 Float Value",
                            value=f"**{gun_float:.5f}**", inline=True)

            return embed

        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in case.py: {e}")
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
                description=f"Welcome to the server, {member.display_name}! We're glad to have you here.",
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

    def now_playing_song_embed(self, song_title, thumbnail, song_duration):
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
            logger.error(
                f"Error while trying to create an embed message in nowplaying.py: {e}")
            return

    def create_gambling_embed_message(self, symbols, profit, balance):
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
            symbols_str = " |".join(symbols)
            embed.add_field(name="Slot Symbols", value=f"```{symbols_str}```", inline=True)

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
            logger.error(
                f"Error while trying to create an embed message in gambling.py: {e}")
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
                    value=f"**Level:** {user['level']} | **Experience:** {user['experience']:.2f} | **Total Bet:** {user['total_bet']}",
                    inline=False
                )

            return embed
        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in leaderboard.py: {e}")
            return None

    def create_rank_embed(self, interactions,  rank, total_bet):
        try:

            # Create an embed message that contains the user's rank
            embed = discord.Embed(title="Rank", color=discord.Color.gold())

            # Get the user profile picture
            embed.set_thumbnail(url=interactions.user.avatar)

            # Add the user's name to the embed message
            embed.add_field(name="Your Name", value=f"{interactions.user.name}", inline=False)

            # Add the user's rank to the embed message
            embed.add_field(name="Your level",
                            value=f"**{rank}**", inline=False)

            # Add the total bet amount to the embed message
            embed.add_field(name="Total Bet",
                            value=f"$**{total_bet}**", inline=False)

            return embed

        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in rank.py: {e}")
            return None

    def create_embed_user_information(self, member):
        try:
            # Create an embed to display user information
            embed = discord.Embed(
                title=f'User Information - {member.display_name}', color=member.color)
            # Add the user's avatar
            embed.set_thumbnail(url=member.avatar)
            # Add the user's information
            embed.add_field(name='Username', value=member.name, inline=True)
            # Add the user's ID
            embed.add_field(name='User ID', value=member.id, inline=True)
            # Add the user's join date to the server
            embed.add_field(name='Joined Server On', value=member.joined_at.strftime(
                '%Y-%m-%d %H:%M:%S'), inline=True)
            # Add the user's account creation date
            embed.add_field(name='Account Created On', value=member.created_at.strftime(
                '%Y-%m-%d %H:%M:%S'), inline=True)
            return embed
        except Exception as e:
            logger.error(f"Error creating user information embed: {e}")
            return None

    def create_work_embed(self, interactions, job, amount_earned, balance):
        # Create an embed message for the work command
        try:
            embed = discord.Embed(
                title="Work Results",
                description=f"You worked as a {job['title']} {job['icon']} and earned ${amount_earned}!",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 Balance",
                            value=f"**${balance:.2f}**", inline=False)
            # Add the minimum and maximum amount of money that can be earned
            embed.add_field(name="💼 Salary Range", value=f"**${job['min_earnings']} - ${job['max_earnings']}**", inline=False)
            # Add the user's picture to the embed
            embed.set_thumbnail(url=interactions.user.avatar)
            return embed
        except Exception as e:
            logger.error(
                f"Error while trying to create an embed message in work.py: {e}")
            return None
        
