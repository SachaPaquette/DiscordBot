# Command to give money to another user
import discord
from Config.logging import setup_logging
from Commands.database import Database
from Config.config import conf
# Create a logger for this file
logger = setup_logging("give.py", conf.LOGS_PATH)
class Give():
    def __init__(self):
        self.database = Database.getInstance()
        
    async def give_command(self, interactions, destination_user: discord.Member, amount: int):
        try:
            # Check if the destination user is the same as the user
            if destination_user.id == interactions.user.id:
                await interactions.response.send_message(f'{interactions.user.mention}, you can\'t give money to yourself.')
                return
            
            # Check if the amount is positive
            if amount <= 0:
                await interactions.response.send_message(f'{interactions.user.mention}, you must give a positive amount.')
                return
                
            giving_user_id = interactions.user.id
            user = self.database.get_user(interactions.guild.id, giving_user_id)
            
            if user["balance"] < amount:
                await interactions.response.send_message("You don't have enough money to give that amount.")
                return
                
            user["balance"] -= amount
            self.database.update_user_balance(interactions.guild.id, giving_user_id, user["balance"])
            
            receiving_user = self.database.get_user(interactions.guild.id, destination_user.id)
            receiving_user["balance"] += amount
            self.database.update_user_balance(interactions.guild.id, destination_user.id, receiving_user["balance"])
            
            await interactions.response.send_message(f'{interactions.user.mention} gave {destination_user.mention} {amount} dollars.')
        except Exception as e:
            logger.error(f"Error in the give function in gambling.py: {e}")
            return