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
        self.first_message = None

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


    async def send_initial_message(self, interactions):
        embed = self.create_embed(interactions.user, {}, interactions)
        if embed is None:
            await interactions.response.send_message("An error occurred while creating the embed.")
        else:
            await interactions.response.send_message(embed=embed)
            self.first_message = await interactions.original_response()



    async def process_case(self, interactions):
        if not self.case or not self.weapon_generator:
            return await interactions.response.send_message("An error occurred while processing the case.")
        await self.send_initial_message(interactions)
        case_data = self.weapon_generator.generate_weapon_data()
        user = await self.get_user_and_check_balance(interactions)
        if not case_data:
            return await interactions.response.send_message("An error occurred while opening the case.")
        embed = self.create_embed(user, case_data, interactions)
        await self.process_case_opening(interactions, user, case_data, embed)

    async def process_case_opening(self, interactions, user, case_data, embed):
        try:
            if not embed:
                logger.error("Embed is None or invalid. Cannot send message.")
                return await interactions.response.send_message("An error occurred while creating the case embed.")

            tasks = [
                self.send_embed_message(embed, case_data["weapon"]),
                self.wait_and_sell_if_needed(interactions, case_data["weapon"]),
                asyncio.to_thread(self.add_user_experience, interactions, case_data["price"]),
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in process_case_opening: {e}")
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
        try:
            case_data["price"] = float(case_data.get("price", 0.0))
            case_data["balance"] = float(user.get("balance", 0.0))
            case_data["profit"] = float(
                self.utility.calculate_profit(case_data["price"], self.case_price))
            case_data["gun_float"] = float(case_data.get("gun_float", 0.0))

            return self.embedMessage.create_case_embed({
                "balance": case_data["balance"],
                "profit": case_data["profit"],
                **case_data,
                "is_souvenir": self.weapon_generator.is_souvenir,
                "color": self.weapon_generator.color,
                "user_nickname": interactions.user.display_name,
            })
        except Exception as e:
            logger.error(f"Error creating embed: {e}")
            return None

        
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
        if action_type == "keep":
            self.inventory.add_or_remove_item_to_inventory(weapon, "add")
        elif action_type == "sell":
            self.database.update_user_balance(self.server_id, self.user_id, bet=weapon["price"])
        update_method = {"keep": self.embedMessage.create_keep_message, "sell": self.embedMessage.create_sell_message}[action_type]
        await self.update_message(message, weapon, update_method, username)
        await self.utility.disable_buttons(message)
        # Remove the weapon text from the message
        await message.edit(content="")            
            
    async def update_message(self, message, weapon, update_method, username):
        content = update_method(username, weapon)
        await message.edit(content=content)


    async def handle_exception(self, e):
        logger.error(f"Error in Case: {e}")



class WeaponGenerator():
    skins_data = None
    latest_data = None
    def __init__(self, case=None, is_souvenir=False):
        self.utility = Utility()
        self.embedMessage = EmbedMessage()
        self.caseDir = "./Commands/CaseData/"
        self.is_souvenir = is_souvenir
        self.case = case
        self.RARITY_WEIGHTS = {
            "Mil-Spec Grade": 0.7997,
            "Restricted": 0.1598,
            "Classified": 0.032,
            "Covert": 0.0064,
            "Rare Special Item": 0.0026,
        }

        self.SOUVENIR_RARITY_WEIGHTS = {
            "Consumer Grade": 0.7997,
            "Industrial Grade": 0.1598,
            "Mil-Spec Grade": 0.7997,
            "Restricted": 0.1598,
            "Classified": 0.0013,
            "Covert": 0.00027,
            "Rare Special Item": 0.0, 
        }
        self.weapon_rarity = self.RARITY_WEIGHTS if not self.is_souvenir else self.SOUVENIR_RARITY_WEIGHTS
        self.rarity_colors = self.get_rarity_colors()
        self.wear_levels = self.get_wear_levels()
        if WeaponGenerator.skins_data is None:
            logger.info("Loading skins data...")
            WeaponGenerator.skins_data = self.load_json_file(f"{self.caseDir}skins.json")
        if WeaponGenerator.latest_data is None:
            logger.info("Loading latest weapon data...")
            WeaponGenerator.latest_data = self.load_json_file(f"{self.caseDir}latest_data.json")
        self.skins_data = WeaponGenerator.skins_data
        self.latest_data = WeaponGenerator.latest_data

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


    def get_weapon_rarity(self) -> dict:
        try:
            # Base rarities
            base_rarities = {
                "Consumer Grade": 0.7997,
                "Industrial Grade": 0.1598,
                "Mil-Spec Grade": 0.0799,
                "Restricted": 0.1598,
                "Classified": 0.032 if not self.is_souvenir else 0.0013,
                "Covert": 0.0064 if not self.is_souvenir else 0.00027,
            }
            
            # Rare special item only for non-souvenir cases
            additional_rarities = {
                "Rare Special Item": 0.0026,
            }
            
            # Combine both dictionaries
            rarities = {**base_rarities, **(additional_rarities if not self.is_souvenir else {})}
            
            logger.debug(f"Weapon rarities generated: {rarities}")
            return rarities
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
            return float(random.uniform(
                float(weapon.get("min_float", 0.0)), 
                float(weapon.get("max_float", 1.0))
            ))
        except Exception as e:
            logger.error(f"Error calculating weapon float: {e}")
            return 0.0  # Default to 0.0 on error



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

            if possible_guns_list:
                return random.choice(possible_guns_list), rarity == "Rare Special Item"
            else:
                logger.warning(f"No weapons available for rarity '{rarity}', rerolling.")
                return self.get_weapon_from_case()
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

    def generate_weapon_data(self):
        try:
            weapon, is_rare = self.get_weapon_from_case()
            weapon_info = self.get_weapon_information(weapon)
            gun_float = self.calculate_weapon_float(weapon_info)
            wear_level = self.calculate_wear_level(gun_float)
            weapon_name = weapon_info.get("weapon", {}).get("name", "Unknown")
            weapon_pattern = weapon_info.get("pattern", {}).get("name", "Unknown")
            is_stattrak = weapon.get("stattrak") and random.random() < 0.1
            prices = self.get_weapon_prices(weapon_name, weapon_pattern, wear_level, is_rare, is_stattrak)

            return {
                "weapon": self.create_weapon(weapon_info, gun_float, wear_level, weapon_name, weapon_pattern, is_stattrak, prices),
                "info": weapon_info,
                "name": weapon_name,
                "pattern": weapon_pattern,
                "float": gun_float,
                "wear": wear_level,
                "stattrak": is_stattrak,
                "price": prices,
                "is_souvenir": self.is_souvenir,
                "color": self.color,
            }
        except Exception as e:
            logger.error(f"Error generating weapon data: {e}")
            return {}
        

