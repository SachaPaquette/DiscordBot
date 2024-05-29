# Used to interact with the mongodb database
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

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
        """ Virtually private constructor. """
        if Database.__instance == None:
            Database.__instance = self
            self.client = None
            self.db = None
            self.collection = None
            self.connect()
            

            
    def connect(self):
        try:
            # Connect to the database
            self.client = MongoClient("mongodb://localhost:27017/")
            # if the database does not exist, it will be created    
            self.db = self.client["discord"]
            self.collection = self.db["users"]
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
        user = {"user_id": user_id, "balance": 100}
        self.collection.insert_one(user)
        
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
        return user
    
    
    
    