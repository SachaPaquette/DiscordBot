import json
from Commands.database import Database
import random
from bs4 import BeautifulSoup
import re
from Commands.utility import Utility
from Config.Driver.driver_config import driver_setup
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("case.py", conf.LOGS_PATH)
class Case():
    def __init__(self, server_id):
        with open("./Commands/Case/case.json", "r") as f:
            self.cases = json.load(f)
        self.case = self.get_random_case()
        self.database = Database.getInstance()
        self.collection = self.database.get_collection(server_id)
        self.rarity = {
            "Mil-Spec Grade": 0.7997,
            "Restricted": 0.1598,
            "Classified": 0.032,
            "Covert": 0.0064,
            "Rare Special Item": 0.0026,
        }
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
            
                 
    def get_random_case(self):
        # Get a random case from the json file ./Cases/cases.json
        return random.choice(self.cases)

            
    def gamble_rarity(self):
            """
            Randomly selects a rarity based on the probabilities.
            
            Returns:
            - rarity: The rarity of the item.
            """
            rarity = random.choices(list(self.rarity.keys()), weights=list(self.rarity.values()))[0]
            return rarity
            
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
            for case in self.cases:
                if "contains_rare" in case:
                    possible_guns_list.extend(case["contains_rare"])
                    is_rare = True
        else:
            # Using the rarity obtained, get a weapon from this rarity in the case
            for case in self.cases:
                contains = case["contains"]
                for contain in contains:
                    if contain["rarity"]["name"] == rarity:
                        possible_guns_list.append(contain)
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
    
    def get_url(self, weapon_name, weapon_pattern, wear_level, is_rare):
        # Replace the spaces in the weapon name and pattern with dashes
        weapon_name = weapon_name.replace(" ", "-")
        weapon_pattern = weapon_pattern.replace(" ", "-")
        wear_level = wear_level.replace(" ", "-")
        
        # Construct the base URL
        base_url = "https://skin.land/market/csgo/"
        
        # Add special URL if the weapon is rare, else return the normal URL
        if is_rare:
            return f"{base_url}★-{weapon_name}-{weapon_pattern}-{wear_level}/"
        return f"{base_url}{weapon_name}-{weapon_pattern}-{wear_level}/"
    
    def get_weapon_price(self, weapon_name, weapon_pattern, wear_level, is_rare):
        try:
                
            # Get the URL of the weapon
            url = self.get_url(weapon_name, weapon_pattern, wear_level, is_rare)
            # Open the URL
            self.driver.get(url)
            
            # Get the page source
            page_source = self.driver.page_source
            # Create a BeautifulSoup object
            soup = BeautifulSoup(page_source, "html.parser")
            
            # Get the weapon price from the page (class = skin-page__best-offer best-offer)
            price_element = soup.find("div", class_=re.compile(r"skin-page__best-offer\s+best-offer"))
            if price_element:
                # Extract the site price
                site_price_element = price_element.find("div", class_="best-offer__site-price-value")
                if site_price_element:
                    site_price = site_price_element.get_text(strip=True).replace("$", "")
                else:
                    site_price = "Site price not found"

                # Extract the steam price
                steam_price_element = price_element.find("div", class_="best-offer__steam-price-value")
                if steam_price_element:
                    steam_price = steam_price_element.get_text(strip=True).replace("$", "")
                else:
                    steam_price = "Steam price not found"

                return steam_price if steam_price != "Steam price not found" else site_price if site_price != "Site price not found" else 0
            else:
                return 0
        except Exception as e:
            print(f"Error getting weapon price: {e}")
            return 0
        
    def add_experience(self, user_id, payout):
        if payout < 0:
            return
        # Get the user
        user = self.database.get_user(self.server_id, user_id)
        # Update the user's experience  
        self.database.update_user_experience(self.server_id, user_id, payout)
        
        
        

    async def open_case(self, interactions):
        try:
            embed_first_message = self.utility.create_open_case_embed_message(self.case)
            # Send a message that the case is being bought
            await interactions.response.send_message(embed=embed_first_message, ephemeral=True)
            
            user_id = interactions.user.id
            
            # Check if the user has enough balance to buy the case
            user = self.database.get_user(self.server_id , user_id)
            
            if user["balance"] < self.case_price:
                interactions.followup.send("Not enough balance")
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
            
            # Get the weapon price
            prices = self.get_weapon_price(weapon_name, weapon_pattern, wear_level, is_rare)
            
            # Adjust the profit
            profit = float(prices) - self.case_price
            
            # Update the user's balance
            user["balance"] += profit
            
            # Update the user's balance
            self.database.update_user_balance(self.server_id,user_id, user["balance"])
            
            # Add experience to the user
            self.add_experience(user_id, profit)
            
            # Get the weapon image
            weapon_image = self.get_weapon_image(weapon_info)

            # Create the embed message
            embed = self.utility.create_case_embed(user["balance"], profit, prices, wear_level, gun_float, weapon_name, weapon_pattern, weapon_image)
            
            if embed is None:
                await interactions.followup.send("An error occurred while opening the case.")
                return
            
            # Send the embed message
            await interactions.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error opening case: {e}")
            await interactions.followup.send("An error occurred while opening the case.")
            return
        
        

        
        