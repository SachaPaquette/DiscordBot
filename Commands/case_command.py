import json
from Commands.Inventory.inventory_setup import Inventory_class
from Commands.database import Database
import random
from Commands.utility import Utility, EmbedMessage
from Config.logging import setup_logging
from Config.config import conf
import asyncio
# Create a logger for this file
logger = setup_logging("case.py", conf.LOGS_PATH)
class Case():
    def __init__(self, server_id):
        self.caseDir = "./Commands/CaseData/"
        self.server_id = server_id
        self.database = Database.getInstance()
        self.collection = self.database.get_collection(server_id)
        self.cases = self.load_cases()
        self.case = self.get_random_case()
        self.weapon_rarity = self.get_weapon_rarity()
        self.rarity_colors = self.get_rarity_colors()
        self.wear_levels = self.get_wear_levels()
        self.case_price = 5
        self.utility = Utility()
        self.is_sold_or_bought = False
        self.inventory = Inventory_class(server_id)
        self.user_id = None
        self.embedMessage = EmbedMessage()
        self.color = None
        
    
    def load_cases(self):
        """
        Loads case information from the JSON file.
        """
        try:
            with open(f"{self.caseDir}case.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cases: {e}")
            return []
        
    def get_weapon_rarity(self):
        """
        Returns the dictionary mapping weapon rarities to their probabilities.
        """
        return {
            "Mil-Spec Grade": 0.7997,
            "Restricted": 0.1598,
            "Classified": 0.032,
            "Covert": 0.0064,
            "Rare Special Item": 0.0026,
        }

    def get_rarity_colors(self):
        """
        Returns the dictionary mapping weapon rarities to their corresponding colors.
        """
        return {
            "Mil-Spec Grade": 0x4B69FF,
            "Restricted": 0x8847FF,
            "Classified": 0xD32CE6,
            "Covert": 0xEB4B4B,
            "Rare Special Item": 0xADE55C 
        }

    def get_wear_levels(self):
        """
        Returns the dictionary mapping wear levels to their corresponding float value ranges.
        """
        return {
            "Factory New": (0.00, 0.07),
            "Minimal Wear": (0.07, 0.15),
            "Field-Tested": (0.15, 0.38),
            "Well-Worn": (0.38, 0.45),
            "Battle-Scarred": (0.45, 1.00)
        }
        
    def get_random_case(self):
        # Get a random case from the json file case.json
        return random.choice(self.cases)
    
    def gamble_rarity(self):
            """
            Randomly selects a rarity based on the probabilities.
            Returns:
            - rarity: The rarity of the item.
            """
            rarity = random.choices(list(self.weapon_rarity.keys()), weights=list(self.weapon_rarity.values()))[0]
            # Set the rarity color
            self.color = self.rarity_colors[rarity]
            return rarity
            
                
    def get_weapon_from_case(self):
        """
        Randomly selects a weapon from the case.

        Returns:
        - weapon: The weapon that was selected.
        - is_rare: Whether the selected weapon is a rare special item.
        """
        rarity = self.gamble_rarity()
        is_rare = rarity == "Rare Special Item"

        possible_guns_list = (
            self.case["contains_rare"] if is_rare
            else [weapon for weapon in self.case["contains"] if weapon["rarity"]["name"] == rarity]
        )

        return random.choice(possible_guns_list), is_rare
    
    def get_weapon_information(self, weapon):
        """
        Retrieves the information of the weapon.

        Parameters:
        - weapon: The weapon to get the information from.

        Returns:
        - weapon_information: The information of the weapon.
        """
        try:
            with open(f"{self.caseDir}skins.json", "r") as f:
                skins = json.load(f)
            
            return next((skin for skin in skins if skin.get("id") == weapon.get("id")), None)
        except Exception as e:
            print(f"Error getting weapon information: {e}")
            return None
    
    def calculate_float(self, weapon):   
        # Calculate a random value between the min and max float values
        return random.uniform(weapon["min_float"], weapon["max_float"])

    def calculate_wear_level(self, gun_float):
        """
        Calculates the wear level of a gun based on its float value.

        Args:
        - gun_float (float): The float value of the gun.

        Returns:
        - str: The wear level of the gun, or None if no match is found.
        """
        return next((wear_level for wear_level, (min_float, max_float) in self.wear_levels.items() if min_float <= gun_float <= max_float), None)
        
    def get_weapon_name(self, weapon):
        return weapon["weapon"]["name"]
    
    def get_weapon_pattern(self, weapon):
        return weapon["pattern"]["name"]
    
    def get_weapon_image(self, weapon):
        return weapon["image"]

    def get_weapon_price(self, weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak):
        def format_weapon_name(weapon_name, is_rare, is_stattrak):
            prefixes = ["★ " if is_rare else "", "StatTrak™ " if is_stattrak else ""]
            return "".join(prefixes) + weapon_name

        def assemble_weapon_title(weapon_name, weapon_pattern, wear_level):
            return f"{weapon_name} | {weapon_pattern} ({wear_level})"

        def load_latest_data(file_path):
            with open(file_path, "r") as f:
                return json.load(f)

        def find_weapon_price(weapon_title, latest_data):
            return latest_data.get(weapon_title, {}).get("steam", 0)

        weapon_name = format_weapon_name(weapon_name, is_rare, is_stattrak)
        weapon_title = assemble_weapon_title(weapon_name, weapon_pattern, wear_level)
        latest_data = load_latest_data(f"{self.caseDir}latest_data.json")
        
        return find_weapon_price(weapon_title, latest_data)
    
    def can_be_stattrak(self, weapon):
        return weapon["stattrak"]
    
    def roll_stattrak(self):
        # There is a 10% chance that the weapon will be stattrak
        return random.random() < 0.1
        
    async def open_case(self, interactions):
        try:
            await self.send_initial_message(interactions)
            user = self.get_user_info(interactions)

            if not self.check_user_balance(user):
                await self.send_insufficient_balance_message(interactions)
                return

            weapon, is_rare = self.get_weapon_from_case()
            weapon_info = self.get_weapon_information(weapon)
            gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak = self.process_weapon_info(weapon_info)
            prices = self.get_weapon_prices(weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak)

            self.update_user_balance(user, interactions)
            self.add_user_experience(interactions, prices)
            weapon = self.create_weapon(weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak, prices)
            embed = self.create_embed(user, weapon_info,  prices, wear_level, gun_float, weapon_name, weapon_pattern, is_stattrak, interactions)

            if embed is None:
                await self.send_error_message(interactions)
                return

            await self.send_embed_message(embed, interactions, weapon)
            await self.wait_and_sell_if_needed(interactions, weapon)
        except Exception as e:
            await self.handle_exception(e, interactions)

    async def send_initial_message(self, interactions):
        await interactions.response.send_message(embed=self.embedMessage.create_open_case_embed_message(self.case, "Case", self.case_price))
        self.first_message = await interactions.original_response()

    def get_user_info(self, interactions):
        self.user_id = interactions.user.id
        return self.database.get_user(interactions)

    def check_user_balance(self, user):
        return self.utility.has_sufficient_balance(user, self.case_price)

    async def send_insufficient_balance_message(self, interactions):
        await interactions.followup.send(f"{interactions.user.display_name} has insufficient balance to buy the case.")

    def process_weapon_info(self, weapon_info):
        gun_float = self.calculate_float(weapon_info)
        wear_level = self.calculate_wear_level(gun_float)
        weapon_name = self.get_weapon_name(weapon_info)
        weapon_pattern = self.get_weapon_pattern(weapon_info)
        is_stattrak = self.roll_stattrak() if self.can_be_stattrak(weapon_info) else False
        return gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak

    def get_weapon_prices(self, weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak):
        return self.utility.format_inexistant_prices(
            self.get_weapon_price(weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak))

    def update_user_balance(self, user, interactions):
        user["balance"] -= self.case_price
        self.database.update_user_balance(self.server_id, interactions.user.id, user["balance"], self.case_price)

    def add_user_experience(self, interactions, prices):
        profit = self.utility.calculate_profit(float(prices), self.case_price)
        self.utility.add_experience(interactions, profit)

    def create_weapon(self, weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak, prices):
        return self.utility.create_weapon_from_info(
            weapon_info, gun_float, wear_level, weapon_name, weapon_pattern,
            self.get_weapon_image(weapon_info), is_stattrak, self.color, prices)

    def create_embed(self, user, weapon_info, prices, wear_level, gun_float, weapon_name, weapon_pattern, is_stattrak, interactions):
        return self.embedMessage.create_case_embed(
            balance=user["balance"],
            profit=self.utility.calculate_profit(float(prices), self.case_price),
            prices=prices,
            wear_level=wear_level,
            gun_float=gun_float,
            weapon_name=weapon_name,
            weapon_pattern=weapon_pattern,
            weapon_image=self.get_weapon_image(weapon_info),
            is_stattrak=is_stattrak,
            color=self.color,
            user_nickname=interactions.user.display_name)

    async def send_error_message(self, interactions):
        await interactions.followup.send("An error occurred while opening the case.")

    async def send_embed_message(self, embed, interactions, weapon):
        embed_message = await self.first_message.edit(embed=embed)
        await self.utility.add_buttons(
            message=embed_message, function_keep=self.keep_function, function_sell=self.sell_function, weapon=weapon)

    async def wait_and_sell_if_needed(self, interactions, weapon):
        await asyncio.sleep(5)
        if not self.is_sold_or_bought:
            await self.sell_function(interactions, weapon, self.first_message)

    async def handle_exception(self, e, interactions):
        print(f"Error opening case: {e}")
        await interactions.followup.send("An error occurred while opening the case.")

    async def keep_function(self, interactions, weapon, message):
        # Make sure the person that is clicking on the button is the same person that opened the case
        if interactions.user.id != self.user_id:
            return
        # Acknowledge the interaction
        await interactions.response.defer()
        
        self.is_sold_or_bought = True
        
        # Modify the message to show that the skin was kept
        await message.edit(content=f"{self.embedMessage.create_keep_message(interactions.user.display_name, weapon)}")
        # Disable the buttons
        await self.utility.disable_buttons(interactions, message)
        
        # Add the skin to the user's inventory
        self.inventory.add_or_remove_item_to_inventory(interactions, weapon, "add")
        
        return
    
    async def sell_function(self, interactions, weapon, message):
         # Make sure the person that is clicking on the button is the same person that opened the case
        if self.user_id != interactions.user.id:
            return
        
        self.is_sold_or_bought = True

        # Modify the message to show that the skin was sold
        await message.edit(content=f"{self.embedMessage.create_sell_message(interactions.user.display_name, weapon)}")
        
        # Disable the buttons
        await self.utility.disable_buttons(interactions, message)
        
        # Sell the skin
        self.collection.update_one({"user_id": interactions.user.id}, {"$inc": {"balance": weapon["price"]}})
        
        return