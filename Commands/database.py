# Used to interact with the mongodb database
import pymongo, time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .UserProfile.user import User
import re
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("database.py", conf.LOGS_PATH)
# Connect to the database
class Database():
    # Instatiate a singleton instance of the database
    __instance = None
    @staticmethod
    def getInstance():
        """ Static access method. """
        if Database.__instance == None:
            Database()
        return Database.__instance
    def __init__(self):
        try:
            """ Virtually private constructor. """
            if Database.__instance == None:
                Database.__instance = self
                self.client = MongoClient("mongodb://localhost:27017/")
                self.db = self.client["discord"]
                self.collections = {}
                
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise e

            
    def connect(self):
        try:
            # Connect to the database
            self.client = MongoClient("mongodb://localhost:27017/")
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
        
    def insert_user(self,server_id, user_id):
        collection = self.get_collection(server_id)
        # Insert a user into the database
        collection.insert_one(User(user_id, 100, 0).return_user())
        
    def get_user(self, server_id, user_id):
        """
        Retrieves a user from the database.
        
        Parameters:
        - user_id: The id of the user to retrieve.
        
        Returns:
        - user: The user object.
        """
        # Check if were connected to the database
        collection = self.get_collection(server_id)
        user = collection.find_one({"user_id": user_id})
        if not user:
            self.insert_user(server_id, user_id)
            user = collection.find_one({"user_id": user_id})
        
        # Update the user's level
        user["level"] = User(user["user_id"], user["balance"], user["experience"]).calculate_level()
        
        return user
    

    def update_user_balance(self, server_id, user_id, balance, update_last_work_time=False):
        """
        Updates the balance of a user.
        
        Parameters:
        - user_id: The id of the user to update.
        - balance: The balance of the user.
        - update_last_work_time: Whether to update the last work time.
        """
        collection = self.get_collection(server_id)
        update_fields = {"balance": balance}
        if update_last_work_time:
            update_fields["last_work"] = time.time()
        collection.update_one({"user_id": user_id}, {"$set": update_fields})
        
    def update_user_experience(self,server_id, user_id, payout):
        """
        Updates the experience of a user.
        
        Parameters:
        - user_id: The id of the user to update.
        - experience: The experience to add to the user.
        """
        collection = self.get_collection(server_id)
        collection.update_one({"user_id": user_id}, {"$inc": {"experience": payout}})
        
    def get_top_users(self,server_id, limit):
        """
        Retrieves the top users by experience.
        """
        collection = self.get_collection(server_id)
        lists = list(collection.find().sort("experience", -1).limit(limit))
        # Change the user's level to the correct level
        for user in lists:
            user["level"] = User(user["user_id"], user["balance"], user["experience"]).calculate_level()
        return lists
        
    