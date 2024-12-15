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
        
        # Ensure the database is initialized
        try:
            self.database = Database.getInstance()
            if self.database.db is None:
                raise Exception("Database connection is unavailable.")
        except Exception as e:
            logger.error(f"Error initializing database in Case: {e}")
            self.database = None

        self.utility = Utility()
        self.inventory = Inventory_class(server_id)
        self.embedMessage = EmbedMessage()
        self.caseDir = "./Commands/CaseData/"

        # Load cases and validate
        self.cases = self.load_cases()
        if not self.cases:
            logger.error("No cases found in case data.")
            self.case = {}
            self.weapon_generator = None
        else:
            self.case = self.get_random_case()
            self.weapon_generator = WeaponGenerator(self.case, self.case.get("type") == "Souvenir")


        self.case_price = 5
        self.user_id = None
        self.is_item_sold_or_kept = False

    def load_cases(self):
        try:
            with open(f"{self.caseDir}case.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):  # Ensure it's a list of cases
                    raise ValueError("Invalid case data format.")
                return data
        except Exception as e:
            logger.error(f"Error loading case data: {e}")
            return []




    def get_random_case(self):
        if not self.cases:
            logger.error("No cases available to select from.")
            return None
        return random.choice(self.cases)



    async def process_case_opening(self, interactions, user, case_data, embed):
        try:
            self.update_user_balance(user, interactions)
            self.add_user_experience(interactions, case_data["price"])
            await self.send_embed_message(embed, interactions, case_data["weapon"])
            await self.wait_and_sell_if_needed(interactions, case_data["weapon"])
        except Exception as e:
            await self.handle_exception(e)
            logger.error(f"Error processing case opening: {e}")

    async def wait_and_sell_if_needed(self, interactions, weapon):
        await asyncio.sleep(5)
        if not self.is_item_sold_or_kept:
            await self.process_action(interactions, weapon, self.first_message, "sell")

    async def open_case(self, interactions):
        try:
            if not self.case or not self.weapon_generator:
                await interactions.response.send_message("No valid case available to open.")
                return

            await self.send_initial_message(interactions)
            user = await self.get_user_and_check_balance(interactions)

            if user is None:
                return

            case_data = self.weapon_generator.open_case_get_weapon()
            if not case_data:
                logger.error("Failed to retrieve weapon data from case.")
                await interactions.response.send_message("An error occurred while opening the case.")
                return

            embed = self.create_embed(user, case_data, interactions)
            if embed is None:
                await self.send_error_message(interactions)
                return

            await self.process_case_opening(interactions, user, case_data, embed)
        except Exception as e:
            logger.error(f"Error opening case: {e}")
            await interactions.response.send_message("An unexpected error occurred. Please try again later.")


    async def get_user_and_check_balance(self, interactions):
        try:
            user = self.get_user_info(interactions)
            
            if not self.check_user_balance(user):
                await self.send_insufficient_balance_message(interactions)
                return None
            return user
        except Exception as e:
            logger.error(f"Error getting user and checking balance: {e}")
            return None

    async def send_initial_message(self, interactions):
        await interactions.response.send_message(embed=self.embedMessage.create_open_case_embed_message(self.case, "Case", self.case_price))
        self.first_message = await interactions.original_response()

    def get_user_info(self, interactions):
        try:
            self.user_id = interactions.user.id
            user = self.database.get_user(interactions)
            if not user:
                raise Exception(f"Failed to retrieve or create user for user_id: {self.user_id}")
            return user
        except Exception as e:
            logger.error(f"Error in get_user_info: {e}")
            return None


    def check_user_balance(self, user):
        return self.utility.has_sufficient_balance(user, self.case_price)

    async def send_insufficient_balance_message(self, interactions):
        await interactions.followup.send(f"{interactions.user.display_name} has insufficient balance to buy the case.")


    def update_user_balance(self, user, interactions):
        user["balance"] -= self.case_price
        self.database.update_user_balance(
            self.server_id, interactions.user.id, user["balance"], self.case_price)

    def add_user_experience(self, interactions, prices):
        profit = self.utility.calculate_profit(float(prices), self.case_price)
        self.utility.add_experience(interactions, profit)


    def create_embed(self, user, case_data, interactions):
        embed_data = {
            "balance": user["balance"],
            "profit": self.utility.calculate_profit(float(case_data["price"]), self.case_price),
            **case_data,
            "is_souvenir": self.weapon_generator.is_souvenir,
            "color": self.weapon_generator.color,
            "user_nickname": interactions.user.display_name
        }
        return self.embedMessage.create_case_embed(embed_data)

    async def send_error_message(self, interactions):
        await interactions.followup.send("An error occurred while opening the case.")

    async def send_embed_message(self, embed, interactions, weapon):
        embed_message = await self.first_message.edit(embed=embed)
        await self.utility.add_buttons(
            message=embed_message,
            function_keep=self.keep_callback,
            function_sell=self.sell_callback,
            weapon=weapon
        )

    async def keep_callback(self, interactions, weapon, message):
        await self.process_action(interactions, weapon, message, "keep")

    async def sell_callback(self, interactions, weapon, message):
        await self.process_action(interactions, weapon, message, "sell")

    async def handle_exception(self, e):
        logger.error(f"Error opening case: {e}")
        
    async def process_action(self, interactions, weapon, message, action_type):
        try:
            if interactions.user.id != self.user_id:
                return

            self.is_item_sold_or_kept = True
            update_method = {
                "keep": self.embedMessage.create_keep_message,
                "sell": self.embedMessage.create_sell_message
            }[action_type]

            await self.update_message(message, interactions.user.display_name, weapon, update_method)
            await self.utility.disable_buttons(interactions, message)

            if action_type == "keep":
                self.inventory.add_or_remove_item_to_inventory(interactions, weapon, "add")
            elif action_type == "sell":
                self.database.update_user_balance(self.server_id, interactions.user.id, bet=weapon["price"])
        except Exception as e:
            logger.error(f"Error processing action: {e}")
            
    async def update_message(self, message, username, weapon, update_method):
        content = update_method(username, weapon)
        await message.edit(content=content)
        
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
        try:
            if rarity == "Rare Special Item":
                return self.case.get("contains_rare", [])
            return [
                weapon for weapon in self.case.get("contains", [])
                if weapon.get("rarity", {}).get("name") == rarity
            ]
        except Exception as e:
            logger.error(f"Error filtering weapons for rarity '{rarity}': {e}")
            return []

        
    def get_weapon_information(self, weapon):
        try:
            with open(f"{self.caseDir}skins.json", "r", encoding="utf-8") as f:
                skins = json.load(f)
                if not isinstance(skins, list):  # Ensure it's a list of weapon data
                    raise ValueError("Invalid skins data format.")
                return next((skin for skin in skins if skin.get("id") == weapon.get("id")), None)
        except Exception as e:
            logger.error(f"Error getting weapon information: {e}")
            return None



    def calculate_float(self, weapon):
        try:
            if weapon is None:
                raise ValueError("Weapon data is None.")
            return random.uniform(weapon["min_float"], weapon["max_float"])
        except ValueError as e:
            logger.error(f"Value error in calculate_float: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating float: {e}")
            return 0.0


    def calculate_wear_level(self, gun_float):
        try:
            return next((wear_level for wear_level, (min_float, max_float) in self.wear_levels.items() if min_float <= gun_float <= max_float), None)
        except Exception as e:
            logger.error(f"Error calculating wear level: {e}")
            return None
        
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
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading latest data: {e}")
                return {}
        def find_weapon_price(weapon_title, latest_data):
            return latest_data.get(weapon_title, {}).get("steam", 0)

        weapon_name = format_weapon_name(weapon_name, is_rare, is_stattrak)
        weapon_title = assemble_weapon_title(
            weapon_name, weapon_pattern, wear_level)
        latest_data = load_latest_data(f"{self.caseDir}latest_data.json")

        return find_weapon_price(weapon_title, latest_data)


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
            possible_guns_list = self.get_possible_guns(rarity)

            if not possible_guns_list:
                raise ValueError(f"No weapons available for rarity '{rarity}'.")

            return random.choice(possible_guns_list), rarity == "Rare Special Item"
        except Exception as e:
            logger.error(f"Error getting weapon from case: {e}")
            return None, False


    
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

        
    def process_weapon_info(self, weapon_info):
        gun_float = self.calculate_float(weapon_info)
        is_stattrak = self.roll_stattrak() if self.can_be_stattrak(weapon_info) else False
        return gun_float, self.calculate_wear_level(gun_float), weapon_info["weapon"]["name"], weapon_info["pattern"]["name"], is_stattrak

    def get_weapon_prices(self, weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak):
        return self.utility.format_inexistant_prices(
            self.get_weapon_price(weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak))
    def roll_stattrak(self):
        # There is a 10% chance that the weapon will be stattrak
        return random.random() < 0.1
    
    def can_be_stattrak(self, weapon):
        return weapon["stattrak"]   
    
    
    def open_case_get_weapon(self):
        try:
            weapon, is_rare = self.get_weapon_from_case()
            if weapon is None:
                raise Exception("Failed to retrieve weapon from case.")

            weapon_info = self.get_weapon_information(weapon)
            if weapon_info is None:
                raise Exception("Failed to retrieve weapon information.")

            gun_float = self.calculate_float(weapon_info)
            wear_level = self.calculate_wear_level(gun_float)
            if wear_level is None:
                raise Exception("Failed to calculate wear level.")

            weapon_name = weapon_info.get("weapon", {}).get("name")
            weapon_pattern = weapon_info.get("pattern", {}).get("name")
            is_stattrak = self.roll_stattrak() if self.can_be_stattrak(weapon_info) else False
            prices = self.get_weapon_prices(
                weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak
            )
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
        except Exception as e:
            logger.error(f"Error opening case and getting weapon: {e}")
            return None
