import random
import json
from Commands.database import Database
from bs4 import BeautifulSoup
import requests
from Config.Driver.driver_config import driver_setup
import time
import re
import httpx
class Case():
    def __init__(self, server_id):
        with open("./Commands/Case/case.json", "r") as f:
            self.cases = json.load(f)
        self.case = self.get_random_case()

        self.users = {}
        self.rarity = {
            "Mil-Spec Grade": 0.7997,
            "Restricted": 0.1598,
            "Classified": 0.032,
            "Covert": 0.0064,
        }
        
        self.wear_levels = {
            "Factory New": 0.00,
            "Minimal Wear": 0.07,
            "Field-Tested": 0.15,
            "Well-Worn": 0.38,
            "Battle-Scarred": 0.45
        }
        # Initialize the driver
        self.driver = driver_setup()
        self.user_id = 282361700202577922
        self.server_id = 285510696459042816
        self.case_price = 5
        
        self.database = Database.getInstance(server_id)
        self.collection = self.database.get_collection(server_id)
            
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
            print(rarity)
            possible_guns_list = []
            # Using the rarity obtained, get a weapon from this rarity in the case
            for case in self.cases:
                contains = case["contains"]
                for contain in contains:
                    if contain["rarity"]["name"] == rarity:
                        possible_guns_list.append(contain)
                        break
            
            # Get a random weapon from the possible guns list
            weapon = random.choice(possible_guns_list)
            print(weapon)
            return weapon
    
    def get_weapon_information(self, weapon):
        """
        Retrieves the information of the weapon.
        
        Parameters:
        - weapon: The weapon to get the information from.
        
        Returns:
        - weapon_information: The information of the weapon.
        """
        # From the weapon id, find the weapon information in skins.json
        with open("./Commands/Case/skins.json", "r") as f:
            skins = json.load(f)
            
        for skin in skins:
            if skin["id"] == weapon["id"]:
                return skin
        return None
    
    
    def calculate_float(self, weapon):
        # Get the minimum and maximum float values
        min_float = weapon["min_float"]
        max_float = weapon["max_float"]
        print(min_float, max_float)
        
        # Calculate a random value between the min and max float values
        return random.uniform(min_float, max_float)

    def calculate_wear_level(self, gun_float):
        # Iterate through the wear levels from worst to best and find the first one where the float value is greater than or equal to the threshold
        for wear_level, float_value in sorted(self.wear_levels.items(), key=lambda x: x[1]):
            if gun_float <= float_value:
                return wear_level

        # If the float value exceeds the highest threshold, it's Factory New
        return "Factory New"
    
    def get_weapon_name(self, weapon):
        return weapon["weapon"]["name"]
    
    def get_weapon_pattern(self, weapon):
        return weapon["pattern"]["name"]
    
    def get_weapon_image(self, weapon):
        return weapon["image"]
    
    def get_url(self, weapon_name, weapon_pattern, wear_level):
        # Replace the spaces in the weapon name and pattern with dashes
        weapon_name = weapon_name.replace(" ", "-")
        weapon_pattern = weapon_pattern.replace(" ", "-")
        wear_level = wear_level.replace(" ", "-")
        
        return f"https://skin.land/market/csgo/{weapon_name}-{weapon_pattern}-{wear_level}/"
    
    def get_weapon_price(self, weapon_name, weapon_pattern, wear_level):
        # Get the URL of the weapon
        url = self.get_url(weapon_name, weapon_pattern, wear_level)
        # Open the URL
        self.driver.get(url)
        
        # Get the page source
        page_source = self.driver.page_source
        # Create a BeautifulSoup object
        soup = BeautifulSoup(page_source, "html.parser")
        
        # Get the weapon price from the page (class = skin-page__best-offer best-offer)
        price_element = soup.find("div", class_=re.compile(r"skin-page__best-offer\s+best-offer"))
        #print(price)
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
        

    def buy_case(self):
        # Check if the user has enough balance to buy the case
        user = self.database.get_user(self.server_id ,self.user_id)
        
        if user["balance"] < self.case_price:
            print("Not enough balance")
        
        # Get a random weapon from the case
        weapon = self.get_weapon_from_case()
        
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
        prices = self.get_weapon_price(weapon_name, weapon_pattern, wear_level)
        
        # Adjust the profit
        profit = float(prices) - self.case_price
        
        # Update the user's balance
        user["balance"] += profit
        
        # Update the user's balance
        self.database.update_user_balance(self.server_id,self.user_id, user["balance"])
        
        weapon_image = self.get_weapon_image(weapon_info)
        
        print(f"User balance: {user['balance']}")
        print(f"Profit: {profit}")
        print(f"Prices: {prices}")
        print(f"Wear Level: {wear_level}")
        print(f"Gun Float: {gun_float}")
        print(f"Weapon Name: {weapon_name}")
        print(f"Weapon Pattern: {weapon_pattern}")
        print(f"Weapon Image: {weapon_image}")
        
        


if __name__ == "__main__":
        
    case = Case(123)
    case.buy_case()
    
    
    # Display all the possible rarities names from the json file
    
   
        