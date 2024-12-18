import asyncio
import json
import time
from Commands.Services.database import Database
import random
from Commands.Services.utility import Utility, EmbedMessage
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("capsule.py", conf.LOGS_PATH)
class Capsule():
    def __init__(self, server_id):
        self.sticker_rarity = self.get_all_sticker_rarity()
        self.sticker_rarity_colors = self.get_all_sticker_rarity_colors()
        self.sticker_capsule_price = 100
        self.utility = Utility()
        self.database = Database.getInstance()
        self.server_id = server_id
        self.color = None
        self.embedMessage = EmbedMessage()
        self.caseDir = "./Commands/CaseData/"
    def get_all_sticker_rarity(self):
        return {
            "High Grade": 0.7997,
            "Remarkable": 0.1598,
            "Exotic": 0.032,
            "Extraordinary": 0.0064,
        }
    
    def get_all_sticker_rarity_colors(self):
        return {
            "High Grade": 0x4B69FF,
            "Remarkable": 0x8847FF,
            "Exotic": 0xD32CE6,
            "Extraordinary": 0xEB4B4B
        }
    
    def get_random_sticker_case(self):
        try:
            with open(f"{self.caseDir}sticker_cases.json", "r", encoding="utf-8") as f:
                sticker_cases = json.load(f)
            if not sticker_cases:
                raise ValueError("No sticker cases available in the JSON file.")
            return random.choice(sticker_cases)
        except Exception as e:
            logger.error(f"Error getting random sticker case: {e}")
            return None

        
    def get_sticker_rarity(self, sticker_case):
        """
        Determines the rarity of the sticker based on its name and predefined rarity distributions.

        Parameters:
        - sticker_case: The sticker case from which the sticker is being selected.

        Returns:
        - rarity: The determined rarity of the sticker.
        """
        sticker_name = sticker_case["name"]
        
        if "(Foil)" in sticker_name:
            rarity = "Exotic"
        elif "(Holo/Foil)" in sticker_name:
            rarity = random.choices(["Exotic", "Remarkable"], weights=[0.1, 0.9])[0]
        else:
            rarity = random.choices(
                list(self.sticker_rarity.keys()),
                weights=list(self.sticker_rarity.values())
            )[0]

        self.color = self.sticker_rarity_colors.get(rarity)
        return rarity

    def get_sticker_from_case(self, sticker_case):
        """
        Retrieves a random sticker from the given sticker case based on its rarity.
        
        Parameters:
        - sticker_case: The case containing the stickers.

        Returns:
        - A randomly selected sticker from the possible stickers list or None if no stickers match the rarity.
        """
        possible_stickers_list = [
            contain for contain in sticker_case["contains"] if contain["rarity"]["name"] == self.get_sticker_rarity(sticker_case) 
        ]
        return random.choice(possible_stickers_list) if possible_stickers_list else None

    def get_sticker_price(self, sticker):
        """
        Retrieves the price of the given sticker from the latest data file.

        Parameters:
        - sticker: The sticker whose price needs to be retrieved.

        Returns:
        - The price of the sticker if found, otherwise 0.
        """
        try:
            sticker_name = f"Sticker | {sticker['name']}"
            with open("./Commands/CaseData/latest_data.json", "r", encoding="utf-8") as f:
                latest_data = json.load(f)
            return latest_data.get(sticker_name, {}).get("steam", 0)
        except Exception as e:
            print(f"Error getting sticker price: {e}")
            return 0
    
    async def open_capsule(self, interactions):
        try:
            user = self.get_user(interactions)
            if not user:
                await interactions.followup.send("User data could not be retrieved.")
                return

            if not self.has_sufficient_balance(user):
                await interactions.followup.send("You don't have enough balance to open this sticker capsule.")
                return

            # Get a random sticker case
            sticker_case = self.get_random_sticker_case()
            if not sticker_case:
                await interactions.followup.send("No sticker cases are available at the moment.")
                return

            # Send initial opening message
            try:
                await self.send_opening_message(interactions, sticker_case)
                first_message = await interactions.original_response()
            except Exception as e:
                logger.error(f"Error during initial message send: {e}")
                await interactions.followup.send("An error occurred while opening the capsule.")
                return

            # Pause for animation effect
            await asyncio.sleep(0.5)

            # Get the sticker from the case
            sticker = self.get_sticker_from_case(sticker_case)
            if not sticker:
                await first_message.edit(content="An error occurred while opening the sticker case.")
                return

            # Process sticker details
            sticker_price = self.get_formatted_sticker_price(sticker)
            profit = self.calculate_profit(sticker_price)

            # Update the user's balance
            self.update_user_balance(user, profit)
            if profit > 0:
                self.add_experience(interactions, profit)

            # Create and send final embed
            embed = self.create_sticker_embed(sticker, user, sticker_price, profit)
            await first_message.edit(embed=embed)

        except Exception as e:
            logger.error(f"Error buying stickers: {e}")
            await interactions.followup.send("An error occurred while opening the stickers.", ephemeral=True)



    def get_user(self, interactions):
        return self.database.get_user(interactions)

    def has_sufficient_balance(self, user):
        return self.utility.has_sufficient_balance(user, self.sticker_capsule_price)

    async def send_insufficient_balance_message(self, interactions):
        await interactions.followup.send("Not enough balance")

    async def send_opening_message(self, interactions, sticker_case):
        try:
            embed_first_message = self.embedMessage.create_open_case_embed_message(sticker_case, "Capsule", self.sticker_capsule_price)
            await interactions.followup.send(embed=embed_first_message)
        except Exception as e:
            logger.error(f"Failed to send opening message: {e}")
            raise e


    async def send_error_message(self, first_message):
        await first_message.edit(content="An error occurred while opening the capsule.")

    def get_formatted_sticker_price(self, sticker):
        return self.utility.format_inexistant_prices(self.get_sticker_price(sticker))

    def calculate_profit(self, sticker_price):
        return self.utility.calculate_profit(sticker_price, self.sticker_capsule_price)

    def update_user_balance(self, user, profit):
        user["balance"] += profit
        self.database.update_user_balance(self.server_id, user["user_id"], user["balance"], self.sticker_capsule_price)

    def add_experience(self, interactions, profit):
        self.utility.add_experience(interactions, profit)

    def create_sticker_embed(self, sticker, user, sticker_price, profit):
        return self.embedMessage.create_sticker_embed(sticker, user["balance"], sticker_price, profit, self.color)

    async def edit_message_with_embed(self, first_message, embed):
        await first_message.edit(embed=embed)
