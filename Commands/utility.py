import discord
from discord.ui import Button, View
from discord.ext import commands
from Config.logging import setup_logging
from Config.config import conf
import matplotlib.pyplot as plt
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
                    value=f"**Level:** {user['level']} | **Experience:** {user['experience']:.2f}",
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
    
    def create_case_embed(self, balance: float, profit: float, prices: float, wear_level:str, gun_float:float, weapon_name:str, weapon_pattern:float, weapon_image:str, is_stattrak:bool, color:str, user_nickname:str):
        try:
            embed = discord.Embed(title=f"🎉 Case Opening Results 🎉", color=discord.Colour(color))
            
            # Add username to the embed message
            embed.add_field(name="👤 User", value=f"**{user_nickname}**", inline=False)
            
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

            
            # Add the graph to the embed message that is stored in ./Case/graph.png
            #file = discord.File("./Commands/Case/graph.png", filename="graph.png")
            #embed.set_image(url="attachment://graph.png")
            
            return embed

        except Exception as e:
            logger.error(f"Error while trying to create an embed message in case.py: {e}")
            return None
        
    def create_open_case_embed_message(self, case, title:str, price:float):
        # find the case image
        case_image = case["image"]
        
        # Create an embed message with the case image
        embed = discord.Embed(title=f"🎉 {title} Opening 🎉", color=discord.Color.gold())

        # Add the case image to the embed message
        embed.set_image(url=case_image)
        # Add the case name to the embed message
        embed.add_field(name="Case", value=case["name"], inline=False)
        # Add a field for the price of the case to the embed message
        embed.add_field(name="Price", value=f"${price}", inline=True)
        
        return embed
    
    
    def create_open_case_graph_skin_prices(self, prices):
        # Extract time frames and price values
        time_frames = list(prices['steam'].keys())
        price_values = list(prices['steam'].values())

        # Reorder time frames and price values
        time_frames = time_frames[::-1]
        price_values = price_values[::-1]

        # Set a custom style
        plt.style.use('dark_background')

        # Create the line graph
        plt.figure(figsize=(10, 6))
        plt.plot(time_frames, price_values, marker='o', color='red', linestyle='-', linewidth=1, markersize=8)

        # Add titles and labels
        plt.title('Steam Average Prices Over Different Time Periods', fontsize=16)
        plt.xlabel('Time Period', fontsize=12)
        plt.ylabel('Average Price', fontsize=12)

        # Display values on top of the points
        for i, price in enumerate(price_values):
            plt.text(i, price + 0.02, f'{price:.4f}', ha='center', va='bottom', fontsize=10)

        # Show the plot
        plt.grid(True)  # Adding grid for better readability

        # Save the plot as an image file
        plt.savefig('./Commands/Case/graph.png')
        plt.close()
            
    def create_sticker_embed(self, sticker, balance, sticker_price, profit, color):
        try:
            embed = discord.Embed(title="🎉 Sticker Opening Results 🎉", color=discord.Colour(color))
            sticker_name = sticker["name"]
            sticker_image = sticker["image"]
            # Add sticker name
            embed.add_field(name="🎨 Sticker", value=f"**{sticker_name}**", inline=False)   
            
            # Add sticker image     
            embed.set_thumbnail(url=sticker_image)
            
            # Add user balance
            embed.add_field(name="💰 Current Balance", value=f"**${balance:.2f}**", inline=True)
            
            # Add profit or loss
            if profit > 0:
                embed.add_field(name="📈 Profit", value=f"+$**{profit:.2f}**", inline=True)
            else:
                embed.add_field(name="📉 Loss", value=f"-$**{-profit:.2f}**", inline=True)
            
            # Add sticker price
            embed.add_field(name="💵 Sticker Price", value=f"$**{float(sticker_price):.2f}**", inline=True)
            
            return embed

        except Exception as e:
            logger.error(f"Error while trying to create an embed message in sticker.py: {e}")
            return None
        
    async def add_buttons(self,interactions, message, function_keep, function_sell, weapon):
        keep_button = Button(style=discord.ButtonStyle.green, label="Keep", custom_id="keep")
        sell_button = Button(style=discord.ButtonStyle.red, label="Sell", custom_id="sell")
        
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
        
        
        


        
    async def disable_buttons(self,interactions, message):
        # Remove the buttons, the embed and the picture
        
        
        
        view = View()
        await message.edit(view=view, embed=None)
        
        
    def create_weapon_from_info(self, weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, weapon_image, is_stattrak, color, weapon_price):
        weapon_image = weapon_info["image"]
        # Keep the price value to 2 decimal places
        weapon_price = round(weapon_price, 2)
        # Keep the float value to 5 decimal places
        gun_float = round(gun_float, 5)
        return {
            "name": weapon_name,
            "pattern": weapon_pattern,
            "image": weapon_image,
            "float": gun_float,
            "wear": wear_level,
            "stattrak": is_stattrak,
            "color": color,
            "price": weapon_price
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
            color_text = "🟩"  # Pink square emoji (no exact pink emoji available)
        # Red text
        elif hex(color) == "0xeb4b4b":
            color_text = "🟥"  # Red square emoji
        # Yellow text
        elif hex(color) == "0xade55c":
            color_text = "🟨"  # Yellow square emoji
        
        return color_text
            
            
        
    def create_inventory_embed_message(self,interactions, user_inventory, page):
        try:
            embed = discord.Embed(title="🎒 Inventory", color=discord.Color.gold())
            # Add the user's name to the embed message
            embed.add_field(name="👤 User", value=f"**{interactions.user.name}**", inline=False)
            # Add the user's inventory to the embed message 
            # Loop through the user's inventory and add each item
            total_value = 0

            # Sort the user's inventory by price
            user_inventory = sorted(user_inventory, key=lambda x: x["price"], reverse=True)
     
            
            # Get the 10 items of the current page
            items = user_inventory[page * 10: (page + 1) * 10] 
            
            
            for item in items:

                
                item_name = item["name"]
                item_pattern = item["pattern"]
                item_price = item["price"]
                item_image = item["image"]
                item_color = item["color"]
                color = self.create_color_text(item_color)
                
                embed.add_field(name=f"{color} {item_name} | {item_pattern}", value=f"**Price:** ${item_price:.2f}", inline=False)
                # add an image of the weapon
                
            

            for item in user_inventory:
                item_price = item["price"]
                total_value += item_price
                
                
            
            # Add the total value of the user's inventory
            embed.add_field(name="💰 Total Value", value=f"**${total_value:.2f}**", inline=False)
            
            return embed
        except Exception as e:
            logger.error(f"Error while trying to create an embed message in inventory.py: {e}")
            return None
    
    async def add_page_buttons(self, message,inventory,  function_previous, function_next):
        previous_button = Button(style=discord.ButtonStyle.green, label="⬅️", custom_id="previous")
        next_button = Button(style=discord.ButtonStyle.green, label="➡️", custom_id="next")
        # Add functions to the buttons
        async def previous_callback(interactions):
            await function_previous(interactions,inventory, message)
        async def next_callback(interactions):
            await function_next(interactions,inventory, message)
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