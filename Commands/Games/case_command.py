import json
from Commands.Inventory.inventory_setup import Inventory_class
from Commands.Services.database import Database
import random
from Commands.Services.utility import Utility, EmbedMessage
from Config.logging import setup_logging
from Config.config import conf
import asyncio
# Create a logger for this file
logger = setup_logging("case.py", conf.LOGS_PATH)


class Case:
    def __init__(self, server_id):
        self.server_id = server_id
        self.database = self.init_database()
        self.utility = Utility()
        self.inventory = Inventory_class(server_id)
        self.embedMessage = EmbedMessage()
        self.caseDir = "./Commands/CaseData/"
        self.cases = self.load_json_file(f"{self.caseDir}case.json")
        self.case = self.get_random_case() if self.cases else None
        self.weapon_generator = WeaponGenerator(self.case) if self.case else None
        self.case_price = 5
        self.user_id = None
        self.is_item_sold_or_kept = False

    def init_database(self):
        try:
            db = Database.getInstance()
            if db.db is None:
                raise Exception("Database connection is unavailable.")
            return db
        except Exception as e:
            logger.error(f"Error initializing database in Case: {e}")
            return None

    def load_json_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file {filepath}: {e}")
            return {}

    def get_random_case(self):
        if not self.cases:
            logger.error("No cases available to choose from.")
            return None
        return random.choice(self.cases)


    async def open_case(self, interactions):
        if not self.case:
            return await interactions.response.send_message("No valid case available to open.")
        await self.send_initial_message(interactions)
        user = await self.get_user_and_check_balance(interactions)
        if not user:
            return
        await self.process_case(user, interactions)


    async def process_case(self, user, interactions):
        case_data = self.weapon_generator.open_case_get_weapon()
        if not case_data:
            return await interactions.response.send_message("An error occurred while opening the case.")
        embed = self.create_embed(user, case_data, interactions)
        await self.process_case_opening(interactions, user, case_data, embed)

    async def process_case_opening(self, interactions, user, case_data, embed):
        try:
            tasks = [
                self.send_embed_message(embed, case_data["weapon"]),
                self.wait_and_sell_if_needed(interactions, case_data["weapon"]),
                asyncio.to_thread(self.update_user_balance, user),
                asyncio.to_thread(self.add_user_experience, interactions, case_data["price"]),
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            await self.handle_exception(e)


    async def wait_and_sell_if_needed(self, interactions, weapon):
        await asyncio.sleep(5)
        if not self.is_item_sold_or_kept:
            await self.process_action(interactions, weapon, self.first_message, "sell")

    async def send_initial_message(self, interactions):
        embed = self.embedMessage.create_open_case_embed_message(self.case, "Case", self.case_price)
        if embed is None:
            await interactions.response.send_message("Failed to load the case details.")
        else:
            await interactions.response.send_message(embed=embed)
            self.first_message = await interactions.original_response()


    async def get_user_and_check_balance(self, interactions):
        user = self.get_user_info(interactions)
        if not user or not self.check_user_balance(user):
            await self.send_insufficient_balance_message(interactions)
            return None
        return user

    def get_user_info(self, interactions):
        try:
            self.user_id = interactions.user.id
            return self.database.get_user(interactions)
        except Exception as e:
            logger.error(f"Error retrieving user info: {e}")
            return None

    def check_user_balance(self, user):
        return self.utility.has_sufficient_balance(user, self.case_price)

    async def send_insufficient_balance_message(self, interactions):
        await interactions.followup.send(f"{interactions.user.display_name} has insufficient balance to buy the case.")

    def update_user_balance(self, user):
        user["balance"] -= self.case_price
        self.database.update_user_balance(self.server_id, self.user_id, user["balance"], self.case_price)

    def add_user_experience(self,interactions, price):
        profit = self.utility.calculate_profit(float(price), self.case_price)
        self.utility.add_experience(interactions=interactions, payout=profit)

    def create_embed(self, user, case_data, interactions):
        return self.embedMessage.create_case_embed({
            "balance": user["balance"],
            "profit": self.utility.calculate_profit(float(case_data["price"]), self.case_price),
            **case_data,
            "is_souvenir": self.weapon_generator.is_souvenir,
            "color": self.weapon_generator.color,
            "user_nickname": interactions.user.display_name
        })
        
    async def button_callback(self, interactions, weapon, message, action_type):
        await self.process_action(interactions, weapon, message, action_type)


    async def send_embed_message(self, embed, weapon):
        embed_message = await self.first_message.edit(embed=embed)
        await self.utility.add_buttons(
            embed_message,
            lambda i, w, m: self.button_callback(i, w, m, "keep"),
            lambda i, w, m: self.button_callback(i, w, m, "sell"),
            weapon,
        )

    async def keep_callback(self, interactions, weapon, message):
        await self.process_action(interactions, weapon, message, "keep")

    async def sell_callback(self, interactions, weapon, message):
        await self.process_action(interactions, weapon, message, "sell")

    async def process_action(self, interactions, weapon, message, action_type):
        if interactions.user.id != self.user_id:
            return
        self.is_item_sold_or_kept = True
        await self.handle_action(interactions.user.display_name, action_type, weapon, message)

    async def handle_action(self,username, action_type, weapon, message):
        update_method = {"keep": self.embedMessage.create_keep_message, "sell": self.embedMessage.create_sell_message}[action_type]
        await self.update_message(message, weapon, update_method, username)
        await self.utility.disable_buttons(message)
        # Remove the weapon text from the message
        await message.edit(content="")
        
        if action_type == "keep":
            self.inventory.add_or_remove_item_to_inventory(weapon, "add")
        else:
            self.database.update_user_balance(self.server_id, self.user_id, bet=weapon["price"])

    async def update_message(self, message, weapon, update_method, username):
        content = update_method(username, weapon)
        await message.edit(content=content)


    async def handle_exception(self, e):
        logger.error(f"Error in Case: {e}")



class WeaponGenerator():
    def __init__(self, case=None, is_souvenir=False):
        self.utility = Utility()
        self.embedMessage = EmbedMessage()
        self.caseDir = "./Commands/CaseData/"
        self.is_souvenir = is_souvenir
        self.case = case
        self.weapon_rarity = self.get_weapon_rarity()
        self.rarity_colors = self.get_rarity_colors()
        self.wear_levels = self.get_wear_levels()
        self.skins_data = self.load_json_file(f"{self.caseDir}skins.json")
        self.latest_data = self.load_json_file(f"{self.caseDir}latest_data.json")
        self.preprocessed_weapons = self.preprocess_weapons()

    def preprocess_weapons(self):
        weapons_by_rarity = {}
        for rarity in self.weapon_rarity.keys():
            weapons_by_rarity[rarity] = [
                weapon for weapon in self.case.get("contains", [])
                if weapon.get("rarity", {}).get("name") == rarity
            ]
        return weapons_by_rarity

    def load_json_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file {filepath}: {e}")
            return {}


    def get_weapon_rarity(self):
        try:
            base_rarities = {
                "Mil-Spec Grade": 0.7997,
                "Restricted": 0.1598,
                "Classified": 0.032 if not self.is_souvenir else 0.0013,
                "Covert": 0.0064 if not self.is_souvenir else 0.00027,
            }
            additional_rarities = {
                "Consumer Grade": 0.7997,
                "Industrial Grade": 0.1598,
            } if self.is_souvenir else {
                "Rare Special Item": 0.0026,
            }
            return {**base_rarities, **additional_rarities}
        except Exception as e:
            logger.error(f"Error getting weapon rarity: {e}")
            return {}

    def get_rarity_colors(self):
        try:
            base_colors = {
                "Mil-Spec Grade": 0x4B69FF,
                "Restricted": 0x8847FF,
                "Classified": 0xD32CE6,
                "Covert": 0xEB4B4B,
            }
            additional_colors = {
                "Consumer Grade": 0xF5F5F5,
                "Industrial Grade": 0x1E90FF,
            } if self.is_souvenir else {
                "Rare Special Item": 0xADE55C,
            }
            return {**base_colors, **additional_colors}
        except Exception as e:
            logger.error(f"Error getting rarity colors: {e}")
            return {}

    def get_wear_levels(self):
        try:
            return {
                "Factory New": (0.00, 0.07),
                "Minimal Wear": (0.07, 0.15),
                "Field-Tested": (0.15, 0.38),
                "Well-Worn": (0.38, 0.45),
                "Battle-Scarred": (0.45, 1.00)
            }
        except Exception as e:
            logger.error(f"Error getting wear levels: {e}")
            return {}

    def get_possible_guns(self, rarity):
        return self.preprocessed_weapons.get(rarity, [])
    
    def get_weapon_information(self, weapon):
        try:
            return next((skin for skin in self.skins_data if skin.get("id") == weapon.get("id")), None)
        except Exception as e:
            logger.error(f"Error retrieving weapon information: {e}")
            return None


    def calculate_weapon_float(self, weapon):
        try:
            return random.uniform(weapon.get("min_float", 0.0), weapon.get("max_float", 1.0))
        except Exception as e:
            logger.error(f"Error calculating weapon float: {e}")
            return 0.0


    def calculate_wear_level(self, gun_float):
        try:
            return next((wear_level for wear_level, (min_float, max_float) in self.wear_levels.items() if min_float <= gun_float <= max_float), None)
        except Exception as e:
            logger.error(f"Error calculating wear level: {e}")
            return None

    def get_weapon_price(self, weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak):
        prefixes = "★ " if is_rare else ""
        prefixes += "Souvenir " if self.is_souvenir else ""
        prefixes += "StatTrak™ " if is_stattrak and not self.is_souvenir else ""

        weapon_title = f"{prefixes}{weapon_name} | {
            weapon_pattern} ({wear_level})"
        return self.latest_data.get(weapon_title, {}).get("steam", 0)

    def gamble_rarity(self):
        rarity = random.choices(list(self.weapon_rarity.keys()), weights=list(
            self.weapon_rarity.values()))[0]
        self.color = self.rarity_colors[rarity]
        return rarity

    def increase_rarity(self, rarity):
        weapon_rarity = list(self.weapon_rarity.keys())
        index = weapon_rarity.index(rarity)
        return weapon_rarity[index + 1] if index + 1 < len(weapon_rarity) else weapon_rarity[0]

    def get_weapon_from_case(self):
        try:
            rarity = self.gamble_rarity()
            possible_guns_list = self.preprocessed_weapons.get(rarity, [])

            if not possible_guns_list:
                logger.warning(f"No weapons available for rarity '{rarity}'.")
                return None, False

            return random.choice(possible_guns_list), rarity == "Rare Special Item"
        except Exception as e:
            logger.error(f"Error getting weapon from case: {e}")
            raise e

    def create_weapon(self, weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak, prices):
        try:
            if not weapon_info or not weapon_name or not wear_level:
                raise ValueError("Missing required weapon information.")

            return self.utility.create_weapon_from_info(
                weapon_info, gun_float, wear_level, weapon_name, weapon_pattern,
                weapon_info.get("image", ""), is_stattrak, self.color, prices
            )
        except Exception as e:
            logger.error(f"Error creating weapon: {e}")
            return None

    def get_weapon_prices(self, weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak):
        return self.utility.format_inexistant_prices(
            self.get_weapon_price(weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak))



    def create_weapon_data(self, weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak, prices):
        return {
            "weapon": self.create_weapon(weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak, prices),
            "weapon_info": weapon_info,
            "price": prices,
            "wear_level": wear_level,
            "gun_float": gun_float,
            "weapon_name": weapon_name,
            "weapon_pattern": weapon_pattern,
            "is_stattrak": is_stattrak,
        }

    def open_case_get_weapon(self):
        try:
            weapon, is_rare = self.get_weapon_from_case()
            weapon_info = self.get_weapon_information(weapon)
            gun_float = self.calculate_weapon_float(weapon_info)
            wear_level = self.calculate_wear_level(gun_float)
            weapon_name = weapon_info.get("weapon", {}).get("name", "")
            weapon_pattern = weapon_info.get("pattern", {}).get("name", "")
            if not weapon_name or not weapon_pattern:
                raise ValueError("Invalid weapon name or pattern.")
            
            # 10% chance of StatTrak if weapon has "stattrak" enabled
            is_stattrak = weapon.get("stattrak") and random.random() < 0.1
            
            prices = self.get_weapon_prices(
                weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak)

            return self.create_weapon_data(weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak, prices)
        except ValueError as ve:
            logger.error(f"Value error in open_case_get_weapon: {ve}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in open_case_get_weapon: {e}")
            return None
