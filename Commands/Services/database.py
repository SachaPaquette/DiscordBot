# Used to interact with the mongodb database
import pymongo, time, os, re
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from ..UserProfile.user import User
from Config.logging import setup_logging
from Config.config import conf
 
# Load the .env file
from dotenv import load_dotenv
load_dotenv()

# Create a logger for this file
logger = setup_logging("database.py", conf.LOGS_PATH)

# Connect to the database
class Database():
    # Instatiate a singleton instance of the database
    __instance = None
    @staticmethod
    def getInstance():
        if Database.__instance == None:
            Database()
        return Database.__instance
    def __init__(self):
        try:
            # If the instance does not exist, create it
            if Database.__instance == None:
                Database.__instance = self
                self.client = MongoClient(os.getenv("MONGO_DB_ADDRESS"))
                self.db = self.client["discord"]
                self.collections = {}
                
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise e
        
    def get_collection(self, server_id):
        if server_id not in self.collections:
            self.collections[server_id] = self.db[str(server_id)]
            print(f"Connected to collection for server_id: {server_id}")
        return self.collections[server_id]
        
    def insert_user(self, interactions, user_id, user_name=None):
        try:
            collection = self.get_collection(interactions.guild.id)
            collection.insert_one(User(user_id=user_id, user_name=user_name or interactions.user.name, balance=100, experience=0).return_user())
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return    
        
    def get_user(self, interactions, user_id=None, user_name=None, fields=None):
        """
        Retrieves a user from the database.

        Parameters:
        - user_id: The id of the user to retrieve.
        - user_name: The name of the user to retrieve (optional).
        - fields: A list of fields to retrieve (optional).

        Returns:
        - user: The user object.
        """
        user_id = user_id or interactions.user.id
        collection = self.get_collection(interactions.guild.id)
        # Fetch only the specified fields if provided
        if fields:
            # Fetch the user's data with the specified fields
            user = collection.find_one({"user_id": user_id}, {"_id": 0, **{field: 1 for field in fields}})
            # If fields have level, recalculate the user's level
            if "level" in fields:
                if "experience" not in user:
                    user["experience"] = collection.find_one({"user_id": user_id}, {"experience": 1})["experience"]
                # Calculate the level without including the level field in the user data
                level = User().calculate_level(user["experience"])
                # Update the user's level in the database
                collection.update_one({"user_id": user_id}, {"$set": {"level": level}})    
                # Update the user's level in the local data
                user["level"] = level
        else:
            user = collection.find_one({"user_id": user_id})

        if not user:
            user_name = user_name or interactions.user.name
            user = self.insert_user(interactions, user_id, user_name)
        
        required_fields = {
            "user_name": user_name or interactions.user.name,
            "balance": 0,
            "experience": 0,
            "total_bet": 0,
            "stocks": {},
            "last_work": 0,
            "level": 0
        }

        user = self.update_user_fields(user, required_fields)
        user["level"] = User(**user).calculate_level()

        return user

    def update_user_fields(self, user, required_fields):
        """
        Updates the fields of a user.

        Parameters:
        - user: The user object to update.
        - required_fields: The fields to add to the user object.

        Returns:
        - user: The updated user object.
        """
        for field, value in required_fields.items():
            user.setdefault(field, value)
        return user
    

    def update_user_balance(self, server_id, user_id, balance=None, bet=0, update_last_work_time=False):
        """
        Updates the balance of a user.

        Parameters:
        - user_id: The id of the user to update.
        - balance: The new balance of the user (optional).
        - bet: The amount to increment the total bet by (default: 0).
        - update_last_work_time: Whether to update the last work time (default: False).
        """
        collection = self.get_collection(server_id)
        update_fields = {}
        if balance is not None:
            update_fields["balance"] = balance
        if update_last_work_time:
            update_fields["last_work"] = time.time()
        update = {"$set": update_fields}
        if bet != 0:
            update["$inc"] = {"total_bet": bet}
        collection.update_one({"user_id": user_id}, update)
            
    def update_user_experience(self,interactions, payout):
        """
        Updates the experience of a user.
        
        Parameters:
        - user_id: The id of the user to update.
        - experience: The experience to add to the user.
        """
        collection = self.get_collection(interactions.guild.id)
        collection.update_one({"user_id": interactions.user.id}, {"$inc": {"experience": payout}})
        
    def get_top_users(self,server_id, limit):
        """
        Retrieves the top users by experience.
        """
        collection = self.get_collection(server_id)
        lists = list(collection.find().sort("experience", -1).limit(limit))
        # Change the user's level to the correct level
        for user in lists:
            user["level"] = User(user["user_id"],user["user_name"], user["balance"], user["experience"]).calculate_level()
        return lists
        
    def add_stocks(self,server_id, user_id, stock, amount, stock_price):
        """
        Adds stocks to a user.
        
        Parameters:
        - user_id: The id of the user to add stocks to.
        - stock: The stock to add.
        - amount: The amount of the stock to add.
        """
        try:
            collection = self.get_collection(server_id)
            # Get the total amount of the stock the user has
            user = collection.find_one({"user_id": user_id})
            user.setdefault("stocks", {})
            data = user["stocks"].get(stock["symbol"], {})
            
            
            total_amount = data.get("amount", 0) + amount
            # Get the total price amount of the stock the user has
            price = total_amount * stock_price
            
            stock_data = {
                "symbol": stock["symbol"],
                "amount": total_amount,
                "total_price": price
            }
            
            # Update the user's balance
            collection.update_one({"user_id": user_id}, {"$set": {f"stocks.{stock['symbol']}": stock_data}, "$inc": {"balance": -price}})   
        except Exception as e:
            logger.error(f"Error adding stocks: {e}")
            return
        
    def sell_stocks(self,server_id, user_id, stock, amount):
        """
        Sells stocks from a user.
        
        Parameters:
        - user_id: The id of the user to sell stocks from.
        - stock: The stock to sell.
        - amount: The amount of the stock to sell.
        """
        try:
            collection = self.get_collection(server_id)
            # Get the total amount of the stock the user has
            user = collection.find_one({"user_id": user_id})
            user.setdefault("stocks", {})
            data = user["stocks"].get(stock["symbol"], {})

            total_amount = data.get("amount", 0) - amount
            # Get the total price amount of the stock the user has
            price = amount * stock["currentPrice"]
            total_price = data.get("total_price", 0) - price
            stock_data = {
                "symbol": stock["symbol"],
                "amount": total_amount,
                "total_price": total_price
            }
            
            # Update the user's balance
            collection.update_one({"user_id": user_id}, {"$set": {f"stocks.{stock['symbol']}": stock_data}, "$inc": {"balance": price}})
        except Exception as e:
            logger.error(f"Error selling stocks: {e}")
            return