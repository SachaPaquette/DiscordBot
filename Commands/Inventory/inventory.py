from Commands.database import Database
class Inventory():
    def __init__(self, server_id):
        self.database = Database.getInstance()
        self.collection = self.database.get_collection(server_id)
        self.users = {}
        
    def get_inventory(self, user_id):
        user = self.collection.find_one({"user_id": user_id})
        if user is None:
            return None
        return user.get("inventory", [])
    
    def add_or_remove_item_to_inventory(self, user_id, item, condition:str):
        inventory = self.get_inventory(user_id)
        
        if condition == "add":
            inventory.append(item)
        elif condition == "remove":
            inventory.remove(item)
        else:
            return
        
        self.collection.update_one({"user_id": user_id}, {"$set": {"inventory": inventory}})
        
    
    