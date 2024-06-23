import json
import time
from Commands.Inventory.inventory_setup import Inventory_class
from Commands.database import Database
import random
from bs4 import BeautifulSoup
import re
from Commands.utility import Utility, EmbedMessage
from Config.Driver.driver_config import driver_setup
from Config.logging import setup_logging
from Config.config import conf

import asyncio

# Create a logger for this file
logger = setup_logging("capsule.py", conf.LOGS_PATH)
class Capsule():
    
    def __init__(self, server_id):
        self.sticker_rarity = {
            "High Grade": 0.7997,
            "Remarkable": 0.1598,
            "Exotic": 0.032,
            "Extraordinary": 0.0064,
        }
        self.sticker_rarity_colors = {
            "High Grade": 0x4B69FF,
            "Remarkable": 0x8847FF,
            "Exotic": 0xD32CE6,
            "Extraordinary": 0xEB4B4B
        }
        self.sticker_capsule_price = 100
        self.utility = Utility()
        self.database = Database.getInstance()
        self.server_id = server_id
        self.color = None
        self.embedMessage = EmbedMessage()
            
    def get_random_sticker_case(self):
        with open("./Commands/Case/sticker_cases.json", "r") as f:
            sticker_cases = json.load(f)
        return random.choice(sticker_cases)
        
    def get_sticker_rarity(self, sticker_case):
        # If the sticker is a foil, it is always exotic
        if "(Foil)" in sticker_case["name"]:
            rarity = "Exotic"
        elif "(Holo/Foil)" in sticker_case["name"]:
            # Can only have Exotic or Remarkable rarity
            rarity = random.choices(["Exotic", "Remarkable"], weights=[0.1, 0.9])[0]
            
        else:
            rarity = random.choices(list(self.sticker_rarity.keys()), weights=list(self.sticker_rarity.values()))[0]
        self.color = self.sticker_rarity_colors[rarity]
        return rarity
    
    def get_sticker_from_case(self, sticker_case):
        rarity = self.get_sticker_rarity(sticker_case) 
        possible_stickers_list = []
        # Using the rarity obtained, get a weapon from this rarity in the case
     

        contains = sticker_case["contains"]
        for contain in contains:
            if contain["rarity"]["name"] == rarity:
                possible_stickers_list.append(contain)
                
        # Get a random weapon from the possible guns list
        return random.choice(possible_stickers_list) if possible_stickers_list else None
            
    
    def get_sticker_price(self, sticker):
        sticker_name = sticker["name"]
        
        with open("./Commands/Case/latest_data.json", "r") as f:
            latest_date = json.load(f)
        
        sticker_name = f"Sticker | {sticker_name}"
        
        if sticker_name in latest_date:
            return latest_date[sticker_name]["steam"]
        return 0
    

        
    async def open_capsule(self, interactions):
        try:
  
            user = self.database.get_user(self.server_id, interactions.user.id)
            
            # Check if the user has enough balance to buy the sticker capsule
            if self.utility.has_sufficient_balance(user, self.sticker_capsule_price) is False:
                await interactions.followup.send("Not enough balance")
                return
            
            # Get a random sticker case
            sticker_case = self.get_random_sticker_case()
            
            # Create an embed message for the sticker case
            embed_first_message = self.embedMessage.create_open_case_embed_message(sticker_case, "Capsule", self.sticker_capsule_price)

            # Send a message that the stickers are being bought
            await interactions.response.send_message(embed=embed_first_message)
            # Get the message
            first_message = await interactions.original_response()
            
            # Wait 1 second before opening the capsule (so the user can see the capsule being opened)
            time.sleep(2)
            
            # Get a random sticker from the case
            sticker = self.get_sticker_from_case(sticker_case)
            
            # Check if the sticker is None
            if sticker is None:
                await first_message.edit(content="An error occurred while opening the capsule.")
                return

            # Get the sticker price
            sticker_price = self.utility.format_inexistant_prices(self.get_sticker_price(sticker))
            
            
            # Update the user's balance
            user["balance"] += self.utility.calculate_profit(sticker_price, self.sticker_capsule_price)
            self.database.update_user_balance(self.server_id, interactions.user.id, user["balance"], self.sticker_capsule_price)
            
            if self.utility.calculate_profit(sticker_price, self.sticker_capsule_price) > 0:
                # Add experience to the user
                self.utility.add_experience(self.server_id, interactions.user.id, self.utility.calculate_profit(sticker_price, self.sticker_capsule_price))
            
            # Create an embed message for the sticker
            embed = self.embedMessage.create_sticker_embed(sticker, user["balance"], sticker_price, self.utility.calculate_profit(sticker_price, self.sticker_capsule_price), self.color)
            
            # Edit the message that the sticker has been bought
            await first_message.edit(embed=embed)
        except Exception as e:
            print(f"Error buying stickers: {e}")
            await interactions.followup.send("An error occurred while buying the stickers.")
            return
