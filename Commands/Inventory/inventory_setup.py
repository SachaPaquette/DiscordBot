from Commands.database import Database
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
        operator = "$push" if condition == "add" else "$pull"
        self.collection.update_one({"user_id": interactions.user.id}, {operator: {"inventory": item}}, upsert=True)
        
    
    