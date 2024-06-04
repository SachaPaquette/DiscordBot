# Used to interact with the mongodb database
import pymongo, time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .UserProfile.user import User
import re
# Connect to the database
class Database():
    # Instatiate a singleton instance of the database
    __instance = None
    @staticmethod
    def getInstance(server_id):
        """ Static access method. """
        if Database.__instance == None:
            Database(server_id)
        return Database.__instance
    def __init__(self, server_id):
        """ Virtually private constructor. """
        if Database.__instance == None:
            Database.__instance = self
            self.client = None
            self.db = None
            self.collection = None
            self.connect(server_id)
            

            
    def connect(self, server_id: str):
        try:
            # Connect to the database
            self.client = MongoClient("mongodb://localhost:27017/")
            # if the database does not exist, it will be created    
            self.db = self.client["discord"]
            self.collection = self.db[str(server_id)]
            print("Database connected.")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise e
    
    def close(self):
        try:
            self.client.close()
        except Exception as e:
            print(f"Error closing the database connection: {e}")
            raise e
        
    def insert_user(self, user_id):
        # Insert a user into the database
        self.collection.insert_one(User(user_id, 100, 0).return_user())
        
    def get_user(self, user_id):
        """
        Retrieves a user from the database.
        
        Parameters:
        - user_id: The id of the user to retrieve.
        
        Returns:
        - user: The user object.
        """
        # Check if were connected to the database
        
        user = self.collection.find_one({"user_id": user_id})
        if not user:
            self.insert_user(user_id)
            user = self.collection.find_one({"user_id": user_id})
        
        # Update the user's level
        user["level"] = User(user["user_id"], user["balance"], user["experience"]).calculate_level()
        
        return user
    

    def update_user_balance(self, user_id, balance, update_last_work_time=False):
        """
        Updates the balance of a user.
        
        Parameters:
        - user_id: The id of the user to update.
        - balance: The balance of the user.
        - update_last_work_time: Whether to update the last work time.
        """
        update_fields = {"balance": balance}
        if update_last_work_time:
            update_fields["last_work"] = time.time()
        self.collection.update_one({"user_id": user_id}, {"$set": update_fields})
        
    def update_user_experience(self, user_id, payout):
        """
        Updates the experience of a user.
        
        Parameters:
        - user_id: The id of the user to update.
        - experience: The experience to add to the user.
        """
        self.collection.update_one({"user_id": user_id}, {"$inc": {"experience": payout}})
        
    def get_top_users(self, limit):
        """
        Retrieves the top users by experience.
        """
        lists = list(self.collection.find().sort("experience", -1).limit(limit))
        # Change the user's level to the correct level
        for user in lists:
            user["level"] = User(user["user_id"], user["balance"], user["experience"]).calculate_level()
        return lists
        
    