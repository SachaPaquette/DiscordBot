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
        """
        Get or create a MongoDB collection for the given server ID.
        
        Parameters:
        - server_id (str): The server ID for which to retrieve the collection.

        Returns:
        - Collection: The MongoDB collection for the server.
        """
        if server_id not in self.collections:
            self.collections[server_id] = self.db[str(server_id)]
            print(f"Connected to collection for server_id: {server_id}")
            
        return self.collections[server_id]

        
    def insert_user(self, interactions, user_id, user_name=None):
        try:
            collection = self.get_collection(interactions.guild.id)
            collection.insert_one(User(user_id=user_id, user_name=user_name or interactions.user.name).return_user())
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return    
        
    def get_user(self, interactions, user_id=None, user_name=None, fields=None):
            """
            Retrieves a user from the database.
            """
            try:
                user_id = user_id or interactions.user.id
                collection = self.get_collection(interactions.guild.id)

                # Fetch user with specified fields
                projection = {"_id": 0}
                if fields:
                    projection.update({field: 1 for field in fields})
                user = collection.find_one({"user_id": user_id}, projection)

                # Create user if not found
                if not user:
                    logger.info(f"User not found. Creating a new user with user_id: {user_id}.")
                    user_name = user_name or interactions.user.name
                    self.insert_user(interactions, user_id, user_name)
                    user = collection.find_one({"user_id": user_id}, projection)

                # Ensure required fields are present
                required_fields = {
                    "user_name": user_name or interactions.user.name,
                    "balance": 100,
                    "experience": 0,
                    "total_bet": 0,
                    "stocks": {},
                    "last_work": 0,
                    "level": 0,
                }
                user = self.update_user_fields(user, required_fields)

                # Recalculate level
                user["level"] = User(**user).calculate_level()

                return user
            except Exception as e:
                logger.error(f"Error retrieving user: {e}")
                return None


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
        - server_id: The ID of the server (guild).
        - user_id: The ID of the user.
        - balance: The new balance of the user (optional).
        - bet: The amount to adjust the balance by (default: 0).
        - update_last_work_time: Whether to update the last work time (default: False).
        """
        try:
            collection = self.get_collection(server_id)
            if bet != 0:
                collection.update_one(
                    {"user_id": user_id},
                    {"$inc": {"balance": bet, "total_bet": bet}}
                )
            update_fields = {}
            if balance is not None:
                update_fields["balance"] = balance
            if update_last_work_time:
                update_fields["last_work"] = time.time()

            if update_fields:
                collection.update_one(
                    {"user_id": user_id},
                    {"$set": update_fields}
                )

        except Exception as e:
            logger.error(f"Error updating user balance: {e}")

            
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
        
        
    def transfer_money(self, guild_id, sender_id, receiver_id, amount):
        try:
            sender = self.get_user({"guild_id": guild_id, "user_id": sender_id})
            receiver = self.get_user({"guild_id": guild_id, "user_id": receiver_id})
            self.update_user_balance(guild_id, sender_id, sender["balance"] - amount)
            self.update_user_balance(guild_id, receiver_id, receiver["balance"] + amount)
        except Exception as e:
            logger.error(f"Error in the transfer_money function in give_command.py: {e}")
            return