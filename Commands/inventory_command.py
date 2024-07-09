from Config.logging import setup_logging
from Commands.database import Database
from Config.config import conf
from Commands.utility import Utility, EmbedMessage
from Commands.Inventory.inventory_setup import Inventory_class
# Create a logger for this file
logger = setup_logging("inventory.py", conf.LOGS_PATH)
class Inventory():
    def __init__(self, server_id):
        self.utility = Utility()
        self.page = 0
        self.inventory = Inventory_class(server_id)
        self.user_id = None
        self.username = None
        self.embedMessage = EmbedMessage()
        
    async def display_inventory(self, interactions):
        try:
            self.user_id = interactions.user.id
            self.username = interactions.user.name
            inventory = self.inventory.get_inventory(interactions)
            if inventory is None or len(inventory) == 0:
                await interactions.response.send_message("You don't have any items in your inventory.")
                return
            embed = self.embedMessage.create_inventory_embed_message(inventory, self.page, self.username)
            await interactions.response.send_message(embed=embed)
            embed_message = await interactions.original_response()
            
            await self.utility.add_page_buttons(embed_message, inventory, self.previous_page, self.next_page)
            
        except Exception as e:
            print(f"Error displaying inventory: {e}")
            await interactions.response.send_message("An error occurred while displaying the inventory.")
            return
        
    async def next_page(self, interactions, inventory, message):
        try:
            #Acknowledge the interaction
            await interactions.response.defer()
            
            # Get the next 10 items from the inventory
            if len(inventory[(self.page+1) * 10: (self.page+2) * 10]) == 0:
                return

            # Increment the page
            self.page += 1
            
            # Get the next 10 items from the inventory
            embed = self.embedMessage.create_inventory_embed_message(user_inventory=inventory, page=self.page, username=self.username)
            
            # Edit the message
            await message.edit(embed=embed)
        
            return
        except Exception as e:
            logger.error(f"Error in the next_page function in inventory.py: {e}")
            return
    async def previous_page(self, interactions, inventory, message):
        try:
                
            #Acknowledge the interaction
            await interactions.response.defer()
            # Make sure the page is not less than 1
            if self.page < 1:
                return
            
            # Decrement the page
            self.page -= 1

            # Get the previous 10 items from the inventory
            embed = self.embedMessage.create_inventory_embed_message(inventory, self.page, self.username)
            
            # Edit the message
            await message.edit(embed=embed)
            
            return
        except Exception as e:
            logger.error(f"Error in the previous_page function in inventory.py: {e}")
            return