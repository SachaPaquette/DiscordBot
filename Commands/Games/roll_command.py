# Command to roll a number (1-100), the closer the user is to the number, the more money they win.
import random 
import discord
from Config.logging import setup_logging
from Commands.Services.database import Database
from Config.config import conf
from Commands.Services.utility import Utility, EmbedMessage
# Create a logger for this file
logger = setup_logging("roll.py", conf.LOGS_PATH)

class Roll():
    def __init__(self):
        self.database = Database.getInstance()
        self.utility = Utility()
        self.embedMessage = EmbedMessage()
        
    def calculate_winnings(self, bet, number, rolled_number):
        difference = abs(number - rolled_number)
        multipliers = {
            range(0, 1): 10,
            range(1, 6): 5,
            range(6, 11): 2,
        }
        return next((bet * value for key, value in multipliers.items() if difference in key), 0)
            
    async def roll_command(self, interactions, bet: float, number: int):
        try:
            # Validate input
            if not await self.validate_input(interactions, bet, number):
                return
            
            # Get user and deduct bet
            user = await self.get_user_and_deduct_bet(interactions, bet)
            
            # Roll number and calculate winnings
            rolled_number = random.randint(1, 100)
            winnings = self.calculate_winnings(bet, number, rolled_number)
            
            # Update user balance and database
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"] + winnings, winnings)
            
            # Send embed message
            await self.send_roll_embed_message(interactions, bet, number, rolled_number, winnings, user["balance"])
        
        except Exception as e:
            await interactions.response.send_message(f'{interactions.user.mention}, there was an error processing your request.')
            logger.error(f"Error in the roll_command function: {e}")
            return

    async def validate_input(self, interactions, bet, number):
        if bet <= 0:
            await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
            return False
        if number < 1 or number > 100:
            await interactions.response.send_message(f'{interactions.user.mention}, the number must be between 1 and 100.')
            return False
        return True

    async def get_user_and_deduct_bet(self, interactions, bet):
        user = self.database.get_user(interactions)
        if not self.utility.has_sufficient_balance(user, bet):
            await interactions.response.send_message(f'{interactions.user.mention}, you don\'t have enough money to bet that amount.')
            return None
        user["balance"] -= bet
        return user

    async def send_roll_embed_message(self, interactions, bet, number, rolled_number, winnings, balance):
        embed = self.embedMessage.create_roll_embed_message(interactions, bet, number, rolled_number, winnings, balance)
        await interactions.response.send_message(embed=embed)