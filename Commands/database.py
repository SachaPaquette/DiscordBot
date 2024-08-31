# Used to interact with the mongodb database
import pymongo, time, os, re
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .UserProfile.user import User
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

            
    def connect(self):
        try:
            # Connect to the database
            self.client = MongoClient(os.getenv("MONGO_DB_ADDRESS"))
            # if the database does not exist, it will be created    
            self.db = self.client["discord"]
            
            
            print("Database connected.")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise e
        
    def get_collection(self, server_id):
        if server_id not in self.collections:
            self.collections[server_id] = self.db[str(server_id)]
            print(f"Connected to collection for server_id: {server_id}")
        return self.collections[server_id]
        
    def close(self):
        try:
            self.client.close()
        except Exception as e:
            print(f"Error closing the database connection: {e}")
            raise e
        
    def insert_user(self, interactions, user_id):
        collection = self.get_collection(interactions.guild.id)
        # Insert a user into the database
        collection.insert_one(User(user_id=user_id, user_name=interactions.user.display_name, balance=100, experience=0).return_user())
        
    def get_user(self, interactions, user_id=None):
        """
        Retrieves a user from the database.

        Parameters:
        - user_id: The id of the user to retrieve.

        Returns:
        - user: The user object.
        """
        user_id = user_id or interactions.user.id
        collection = self.get_collection(interactions.guild.id)
        user = collection.find_one({"user_id": user_id})
        
        if not user:
            self.insert_user(interactions, user_id)
            user = collection.find_one({"user_id": user_id})
            
        # Define the required fields and their default values
        required_fields = {
            "user_name": interactions.user.name,
            "balance": 0,
            "experience": 0,
            "total_bet": 0,
            "stocks": {},
            "last_work": 0,
            "level": 0
        }
        
        # Check if required fields are missing and update the user document
        update_fields = {}
        for field, default_value in required_fields.items():
            if field not in user:
                user[field] = default_value
                update_fields[field] = default_value
        
        if update_fields:
            collection.update_one({"user_id": user_id}, {"$set": update_fields})
        
        user["level"] = User(user_id=user["user_id"], user_name=user["user_name"], balance=user["balance"], experience=user["experience"]).calculate_level()
        
        return user

    

    def update_user_balance(self, server_id, user_id, balance,bet=0, update_last_work_time=False):
        """
        Updates the balance of a user.
        
        Parameters:
        - user_id: The id of the user to update.
        - balance: The balance of the user.
        - update_last_work_time: Whether to update the last work time.
        """
        collection = self.get_collection(server_id)
        update_fields = {"balance": balance}
        # Update the last work time (a user can only work every X minutes)
        if update_last_work_time:
            update_fields["last_work"] = time.time()
        # Update the user's balance
        collection.update_one(
            {"user_id": user_id},
            {
                "$set": update_fields,
                "$inc": {"total_bet": bet}
            }
        )
        
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