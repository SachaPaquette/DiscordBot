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
        self.is_souvenir = False
        self.case = self.get_random_case()
        
        self.weapon_rarity = self.get_weapon_rarity(self.is_souvenir)
        self.rarity_colors = self.get_rarity_colors(self.is_souvenir)
        self.wear_levels = self.get_wear_levels()
        self.case_price = 5
        self.utility = Utility()
        self.is_item_sold_or_kept = False
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
        
    def get_weapon_rarity(self, souvenir=False):
        """
        Returns the dictionary mapping weapon rarities to their probabilities.

        Args:
        - souvenir (bool): Whether to return the souvenir rarity probabilities. Defaults to False.
        """
        base_rarities = {
            "Mil-Spec Grade": 0.7997,
            "Restricted": 0.1598,
            "Classified": 0.032 if not souvenir else 0.0013,
            "Covert": 0.0064 if not souvenir else 0.00027,
        }

        if souvenir:
            return {
                **base_rarities,
                "Consumer Grade": 0.7997,
                "Industrial Grade": 0.1598,
            }
        else:
            return {
                **base_rarities,
                "Rare Special Item": 0.0026,
            }
                

    def get_rarity_colors(self, souvenir=False):
        """
        Returns the dictionary mapping weapon rarities to their corresponding colors.
        """
        base_rarities = {
            "Mil-Spec Grade": 0x4B69FF,
            "Restricted": 0x8847FF,
            "Classified": 0xD32CE6,
            "Covert": 0xEB4B4B,
        }

        if souvenir:
            return {
                **base_rarities,
                "Consumer Grade": 0xF5F5F5,
                "Industrial Grade": 0x1E90FF,
            }
        else:
            return {
                **base_rarities,
                "Rare Special Item": 0xADE55C,
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
        case = random.choice(self.cases)
        self.is_souvenir = case["type"] == "Souvenir"
        return case
    
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
            
               
    def increase_rarity(self, rarity):
        weapon_rarity = list(self.weapon_rarity.keys())
        index = weapon_rarity.index(rarity)
        return weapon_rarity[index + 1] if index + 1 < len(weapon_rarity) else rarity

    def get_weapon_from_case(self):
        try:
            rarity = self.gamble_rarity()
            while True:
                is_rare = rarity == "Rare Special Item"
                possible_guns_list = self.get_possible_guns(rarity, is_rare)
                if possible_guns_list:
                    return random.choice(possible_guns_list), is_rare
                rarity = self.increase_rarity(rarity)
        except Exception as e:
            logger.error(f"Error getting weapon from case: {e}")
            return None, False

    def get_possible_guns(self, rarity, is_rare):
        return (
            self.case["contains_rare"] if is_rare
            else [weapon for weapon in self.case["contains"] if weapon["rarity"]["name"] == rarity]
        )
        
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
            logger.error(f"Error getting weapon information: {e}")
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
        try:
            return next((wear_level for wear_level, (min_float, max_float) in self.wear_levels.items() if min_float <= gun_float <= max_float), None)
        except Exception as e:
            logger.error(f"Error calculating wear level: {e}")
            return None
        
    def get_weapon_name(self, weapon):
        return weapon["weapon"]["name"]
    
    def get_weapon_pattern(self, weapon):
        return weapon["pattern"]["name"]
    
    def get_weapon_image(self, weapon):
        return weapon["image"]

    def get_weapon_price(self, weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak):
        def format_weapon_name(weapon_name, is_rare, is_stattrak):
            prefixes = [
                "★ " if is_rare else "",
                "Souvenir " if self.is_souvenir else "",
                "StatTrak™ " if is_stattrak and not self.is_souvenir else ""
            ]
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
        
    def open_case_get_weapon(self):
        weapon, is_rare = self.get_weapon_from_case()
        weapon_info = self.get_weapon_information(weapon)
        gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak = self.process_weapon_info(weapon_info)
        prices = self.get_weapon_prices(weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak)
        weapon = self.create_weapon(weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak, prices)
        
        return {
            "weapon": weapon,
            "weapon_info": weapon_info,
            "price": prices,
            "wear_level": wear_level,
            "gun_float": gun_float,
            "weapon_name": weapon_name,
            "weapon_pattern": weapon_pattern,
            "is_stattrak": is_stattrak,
        }
    
    async def process_case_opening(self, interactions, user, case_data, embed):
        try:
            self.update_user_balance(user, interactions)
            self.add_user_experience(interactions, case_data["price"])
            
            await self.send_embed_message(embed, interactions, case_data["weapon"])
            await self.wait_and_sell_if_needed(interactions, case_data["weapon"])
        except Exception as e:
            await self.handle_exception(e, interactions)
            logger.error(f"Error processing case opening: {e}")
    
    async def open_case(self, interactions):
        try:
            await self.send_initial_message(interactions)
            user = self.get_user_info(interactions)

            if not self.check_user_balance(user):
                await self.send_insufficient_balance_message(interactions)
                return

            case_data = self.open_case_get_weapon()
            
            
            embed = self.create_embed(user, case_data, interactions)

            if embed is None:
                await self.send_error_message(interactions)
                return

            await self.process_case_opening(interactions, user, case_data, embed)
        except Exception as e:
            await self.handle_exception(e, interactions)
            logger.error(f"Error opening case: {e}")
            
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

    def create_embed(self, user, case_data, interactions):
        embed_data = {
            "balance": user["balance"],
            "profit": self.utility.calculate_profit(float(case_data["price"]), self.case_price),
            **case_data,
            "is_souvenir": self.is_souvenir,
            "color": self.color,
            "user_nickname": interactions.user.display_name
        }
        
        
        return self.embedMessage.create_case_embed(embed_data)

    async def send_error_message(self, interactions):
        await interactions.followup.send("An error occurred while opening the case.")

    async def send_embed_message(self, embed, interactions, weapon):
        embed_message = await self.first_message.edit(embed=embed)
        await self.utility.add_buttons(
            message=embed_message, function_keep=self.keep_function, function_sell=self.sell_function, weapon=weapon)

    async def wait_and_sell_if_needed(self, interactions, weapon):
        await asyncio.sleep(3)
        if not self.is_item_sold_or_kept:
            await self.sell_function(interactions, weapon, self.first_message)

    async def handle_exception(self, e, interactions):
        logger.error(f"Error opening case: {e}")
        await interactions.followup.send("An error occurred while opening the case.")

    async def process_action(self, interactions, weapon, message, action_type):
        if interactions.user.id != self.user_id:
            return
        
        self.is_item_sold_or_kept = True
        
        update_method = self.embedMessage.create_keep_message if action_type == "keep" else self.embedMessage.create_sell_message
        await self.update_message(message, interactions.user.display_name, weapon, update_method)
        await self.utility.disable_buttons(interactions, message)

        if action_type == "keep":
            await self.inventory.add_or_remove_item_to_inventory(interactions, weapon, "add")
        elif action_type == "sell":
            await self.update_balance(interactions.user.id, weapon["price"])

    async def update_message(self, message, username, weapon, update_method):
        content = update_method(username, weapon)
        await message.edit(content=content)

    async def keep_function(self, interactions, weapon, message):
        await self.process_action(interactions, weapon, message, "keep")

    async def sell_function(self, interactions, weapon, message):
        await self.process_action(interactions, weapon, message, "sell")

    async def update_balance(self, user_id, price):
        self.collection.update_one({"user_id": user_id}, {"$inc": {"balance": price}})