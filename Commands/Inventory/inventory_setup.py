from Commands.Services.database import Database
from Config.logging import setup_logging
from Config.config import conf

logger = setup_logging("inventory.py", conf.LOGS_PATH)

class Inventory_class():
    def __init__(self, server_id):
        self.database = Database.getInstance()
        self.collection = self.database.get_collection(server_id)
        self.users = {}
        self.server_id = server_id
        
    def get_inventory(self, interactions):
        user = self.collection.find_one({"user_id": interactions.user.id})
        
        if user is None:
            # Create a new user
            user = self.database.get_user(interactions)
        return user.get("inventory", [])
    
    def add_or_remove_item_to_inventory(self, interactions, item, condition: str):
        try:
            operator = "$push" if condition == "add" else "$pull"  
            self.collection.update_one({"user_id": interactions.user.id}, {operator: {"inventory": item}}, upsert=True)
        except Exception as e:
            logger.error(f"Error adding or removing item to inventory: {e}")
            return
    
    