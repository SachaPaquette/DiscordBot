import json
import time
from Commands.database import Database
import random
from bs4 import BeautifulSoup
import re
from Commands.utility import Utility
from Config.Driver.driver_config import driver_setup
from Config.logging import setup_logging
from Config.config import conf
from Commands.Inventory.inventory import Inventory

import asyncio

# Create a logger for this file
logger = setup_logging("case.py", conf.LOGS_PATH)
class Case():
    def __init__(self, server_id):
        with open("./Commands/Case/case.json", "r") as f:
            self.cases = json.load(f)
        self.case = self.get_random_case()
        self.database = Database.getInstance()
        self.collection = self.database.get_collection(server_id)
        self.weapon_rarity = {
            "Mil-Spec Grade": 0.7997,
            "Restricted": 0.1598,
            "Classified": 0.032,
            "Covert": 0.0064,
            "Rare Special Item": 0.0026,
        }
        self.rarity_colors = {
            "Mil-Spec Grade": 0x4B69FF,
            "Restricted": 0x8847FF,
            "Classified": 0xD32CE6,
            "Covert": 0xEB4B4B,
            "Rare Special Item": 0xADE55C 
        }
        self.color = None
        self.wear_levels = {
            "Factory New": (0.00,0.07),
            "Minimal Wear": (0.07,0.15),
            "Field-Tested": (0.15,0.38),
            "Well-Worn": (0.38,0.45),
            "Battle-Scarred": (0.45,1)
        }
        # The price of a case
        self.case_price = 5
        # Create a Utility object
        self.utility = Utility()
        # Set the server id
        self.server_id = server_id
        # Set the Selenium driver
        self.driver = driver_setup()
        
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
        self.inventory = Inventory(server_id)
        self.page = 0
        self.user_nickname = None
        self.user_id = None
        self.is_sold_or_bought = False 
        
    def get_random_case(self):
        # Get a random case from the json file ./Cases/cases.json
        return random.choice(self.cases)

            
    def gamble_rarity(self):
            """
            Randomly selects a rarity based on the probabilities.
            
            Returns:
            - rarity: The rarity of the item.
            """
            rarity = random.choices(list(self.weapon_rarity.keys()), weights=list(self.weapon_rarity.values()))[0]
            self.get_color_from_rarity(rarity)
            return rarity
            
    def get_color_from_rarity(self, rarity):
        self.color = self.rarity_colors[rarity]
            
    def get_weapon_from_case(self):
        """
        Randomly selects a weapon from the case.

        Returns:
        - weapon: The weapon that was selected.
        """
        # Use the rarity to get a weapon
        rarity = self.gamble_rarity()
        
        possible_guns_list = []
        is_rare = False

        # Check if the rarity is for a rare special item
        if rarity == "Rare Special Item":
            for case in self.case["contains_rare"]:
                if "contains_rare" in case:
                    possible_guns_list.extend(case)
                    is_rare = True
        else:
            
            # Using the rarity obtained, get a weapon from this rarity in the case
            for case in self.case["contains"]:
                
                
                if case["rarity"]["name"] == rarity:
                        possible_guns_list.append(case)
                        break

        # Get a random weapon from the possible guns list
        weapon = random.choice(possible_guns_list)
        return weapon, is_rare

    
    def get_weapon_information(self, weapon):
        """
        Retrieves the information of the weapon.
        
        Parameters:
        - weapon: The weapon to get the information from.
        
        Returns:
        - weapon_information: The information of the weapon.
        """
        try:   
            # From the weapon id, find the weapon information in skins.json
            with open("./Commands/Case/skins.json", "r") as f:
                skins = json.load(f)
                
            for skin in skins:
                if skin["id"] == weapon["id"]:
                    return skin
            return None
        except Exception as e:
            print(f"Error getting weapon information: {e}")
            return None
    
    def calculate_float(self, weapon):
        # Get the minimum and maximum float values
        min_float = weapon["min_float"]
        max_float = weapon["max_float"]
        
        # Calculate a random value between the min and max float values
        return random.uniform(min_float, max_float)

    def calculate_wear_level(self, gun_float):
        # Iterate through the wear levels and find the one that includes the gun_float value
        for wear_level, (min_float, max_float) in self.wear_levels.items():
            if min_float <= gun_float <= max_float:
                return wear_level

        # If no wear level matches the gun_float value, return None
        return None
    
    def get_weapon_name(self, weapon):
        return weapon["weapon"]["name"]
    
    def get_weapon_pattern(self, weapon):
        return weapon["pattern"]["name"]
    
    def get_weapon_image(self, weapon):
        return weapon["image"]
    

    
    
    def get_weapon_price(self, weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak):
        if is_stattrak:
            weapon_name = f"StatTrak™ {weapon_name}"
            
        if is_rare:
            weapon_name = f"★ {weapon_name}"
        # Create a name for the weapon (assemble all the parameters)
        
        
        weapon_title = f"{weapon_name} | {weapon_pattern} ({wear_level})"
        # Find the weapon in latest_data.json
        with open("./Commands/Case/latest_data.json", "r") as f:
            latest_date = json.load(f)
        
        # Get the weapon price
        if weapon_title in latest_date:
            return latest_date[weapon_title]["steam"]
        
        return 0
    

        
    def add_experience(self, user_id, payout):
        if payout < 0:
            return
        # Get the user
        user = self.database.get_user(self.server_id, user_id)
        # Update the user's experience  
        self.database.update_user_experience(self.server_id, user_id, payout)
        
    def can_be_stattrak(self, weapon):
        return weapon["stattrak"]
    
    def roll_stattrak(self):
        # There is a 10% chance that the weapon will be stattrak
        return random.random() < 0.1
        
    async def open_case(self, interactions):
        try:
            embed_first_message = self.utility.create_open_case_embed_message(self.case, "Case", self.case_price)
            # Send a message that the case is being bought
            await interactions.response.send_message(embed=embed_first_message)
            first_message = await interactions.original_response()
            #time.sleep(1)
            self.user_id = interactions.user.id
            # Get the nickname of the user
            self.user_nickname = interactions.user.display_name
            
            # Check if the user has enough balance to buy the case
            user = self.database.get_user(self.server_id , self.user_id)
            
            if user["balance"] < self.case_price:
                await interactions.followup.send(f"{self.user_nickname} has insufficient balance to buy the case.")
                return
            
            # Get a random weapon from the case
            weapon, is_rare = self.get_weapon_from_case()
            
            # Get the weapon information
            weapon_info = self.get_weapon_information(weapon)
            
            # Calculate the float value of the weapon
            gun_float = self.calculate_float(weapon_info)
            
            # Calculate the wear level of the weapon
            wear_level = self.calculate_wear_level(gun_float)
            
            # Get the weapon name and pattern
            weapon_name = self.get_weapon_name(weapon_info)
            weapon_pattern = self.get_weapon_pattern(weapon_info)
            
            # Check if the weapon can be stattrak and roll for it
            is_stattrak = self.roll_stattrak() if self.can_be_stattrak(weapon_info) else False
            
            # Get the weapon price
            prices = self.format_inexistant_prices(self.get_weapon_price(weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak))
            
            weapon_price = prices["last_24h"]
            
            # Adjust the profit based on the case price
            profit = float(weapon_price) - self.case_price
            
            # Update the user's balance (subtract the case price from the user's balance)
            user["balance"] -= self.case_price
            
            # Update the user's balance
            self.database.update_user_balance(self.server_id,self.user_id, user["balance"])
            
            # Add experience to the user
            self.add_experience(self.user_id, profit)
            
            # Get the weapon image
            weapon_image = self.get_weapon_image(weapon_info)
            
            weapon = self.utility.create_weapon_from_info(weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, weapon_image, is_stattrak, self.color, weapon_price)
            

            # Create the embed message
            embed  = self.utility.create_case_embed(user["balance"], profit, weapon_price, wear_level, gun_float, weapon_name, weapon_pattern, weapon_image, is_stattrak, self.color, self.user_nickname)
            
            if embed is None:
                await interactions.followup.send("An error occurred while opening the case.")
                return
            
            # Send the embed message
            embed_message = await first_message.edit(embed=embed)

            # Add buttons to the message
            await self.utility.add_buttons(interactions=interactions, message=embed_message, function_keep=self.keep_function, function_sell=self.sell_function, weapon=weapon)
            
            # Wait 5 seconds before selling
            await asyncio.sleep(5)

            # If the user hasn't sold or kept the skin, sell it
            if not self.is_sold_or_bought:
                await self.sell_function(interactions, weapon, embed_message)
            return
            
        except Exception as e:
            print(f"Error opening case: {e}")
            await interactions.response.send_message("An error occurred while opening the case.")
            return
        
    async def keep_function(self, interactions, weapon, message):
        # Make sure the person that is clicking on the button is the same person that opened the case
        if interactions.user.id != self.user_id:
            return
        # Acknowledge the interaction
        await interactions.response.defer()
        
        self.is_sold_or_bought = True
        
        # Modify the message to show that the skin was kept
        await message.edit(content=f"{self.user_nickname} kept the skin.")
        # Disable the buttons
        await self.utility.disable_buttons(interactions, message)
        # Add the skin to the user's inventory
        self.inventory.add_or_remove_item_to_inventory(interactions.user.id, weapon, "add")
        
        return
    
    async def sell_function(self, interactions, weapon, message):
         # Make sure the person that is clicking on the button is the same person that opened the case
        if interactions.user.id != self.user_id:
            return
        
        self.is_sold_or_bought = True
        
        # Modify the message to show that the skin was sold
        await message.edit(content=f"{self.user_nickname} sold the skin.")
        
        # Disable the buttons
        await self.utility.disable_buttons(interactions, message)
        
        # Sell the skin
        self.collection.update_one({"user_id": interactions.user.id}, {"$inc": {"balance": weapon["price"]}})
        
        return
    
        
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
        
        
    async def open_capsule(self, interactions):
        try:
            # Get the user from the database
            user_id = interactions.user.id
            user = self.database.get_user(self.server_id, user_id)
            
            # Check if the user has enough balance to buy the sticker capsule
            if user["balance"] < self.sticker_capsule_price:
                await interactions.followup.send("Not enough balance")
                return
            
            # Get a random sticker case
            sticker_case = self.get_random_sticker_case()
            
            # Create an embed message for the sticker case
            embed_first_message = self.utility.create_open_case_embed_message(sticker_case, "Capsule", self.sticker_capsule_price)

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
            sticker_price = self.format_inexistant_prices(self.get_sticker_price(sticker))
            
            # Calculate the profit
            profit = sticker_price - self.sticker_capsule_price
            
            # Update the user's balance
            user["balance"] += profit
            self.database.update_user_balance(self.server_id, user_id, user["balance"])
            
            if profit > 0:
                # Add experience to the user
                self.add_experience(user_id, profit)
            
            # Create an embed message for the sticker
            embed = self.utility.create_sticker_embed(sticker, user["balance"], sticker_price, profit, self.color)
            
            # Edit the message that the sticker has been bought
            await first_message.edit(embed=embed)
        except Exception as e:
            print(f"Error buying stickers: {e}")
            await interactions.followup.send("An error occurred while buying the stickers.")
            return
        
    async def display_inventory(self, interactions):
        try:
            user_id = interactions.user.id
            inventory = self.inventory.get_inventory(user_id)
            if inventory is None or len(inventory) == 0:
                await interactions.response.send_message("You don't have any items in your inventory.")
                return
            embed = self.utility.create_inventory_embed_message(interactions, inventory, self.page)
            await interactions.response.send_message(embed=embed)
            embed_message = await interactions.original_response()
            
            await self.utility.add_page_buttons(embed_message, inventory, self.previous_page, self.next_page)
            
        except Exception as e:
            print(f"Error displaying inventory: {e}")
            await interactions.followup.send("An error occurred while displaying the inventory.")
            return
        
    async def next_page(self, interactions, inventory, message):
        #Acknowledge the interaction
        await interactions.response.defer()
        
        # Get the next 10 items from the inventory
        if len(inventory[(self.page+1) * 10: (self.page+2) * 10]) == 0:
            return

        # Increment the page
        self.page += 1
        
        # Get the next 10 items from the inventory
        embed = self.utility.create_inventory_embed_message(interactions=interactions, user_inventory=inventory, page=self.page)
        
        # Edit the message
        await message.edit(embed=embed)
    
        return
        
    async def previous_page(self, interactions, inventory, message):
        #Acknowledge the interaction
        await interactions.response.defer()
        # Make sure the page is not less than 1
        if self.page < 1:
            return
        
        # Decrement the page
        self.page -= 1

        # Get the previous 10 items from the inventory
        embed = self.utility.create_inventory_embed_message(interactions, inventory, self.page)
        
        # Edit the message
        await message.edit(embed=embed)
        
        return