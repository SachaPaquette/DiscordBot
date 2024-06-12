# Command to roll a number (1-100), the closer the user is to the number, the more money they win.
import random 
import discord
from Config.logging import setup_logging
from Commands.database import Database
from Config.config import conf
from Commands.utility import Utility
# Create a logger for this file
logger = setup_logging("roll.py", conf.LOGS_PATH)

class Roll():
    def __init__(self):
        self.database = Database.getInstance()
        self.utility = Utility()
        
    def calculate_winnings(self, bet, number, rolled_number):
        # Calculate the difference between the number and the rolled number
        difference = abs(number - rolled_number)
        
        # The closer the user is to the number, the more money they win
        if difference == 0:
            return bet * 10
        elif difference <= 5:
            return bet * 5
        elif difference <= 10:
            return bet * 2
        else:
            return 0
        
    async def roll_command(self, interactions, bet: float, number: int):
        
        # Check if the bet is positive
        if bet <= 0:
            await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
            return
        
        # Check if the number is between 1 and 100
        if number < 1 or number > 100:
            await interactions.response.send_message(f'{interactions.user.mention}, the number must be between 1 and 100.')
            return
        
        user = self.database.get_user(interactions.guild.id, interactions.user.id)
        
        # Check if the user has enough money
        if self.utility.has_sufficient_balance(user, bet) == False:
            await interactions.response.send_message(f'{interactions.user.mention}, you don\'t have enough money to bet that amount.')
            return
        
        # Deduct the bet from the user's balance
        user["balance"] -= bet
        
        
        
        # Roll a number between 1 and 100
        rolled_number = random.randint(1, 100)
        
        winnings = self.calculate_winnings(bet, number, rolled_number)
        
        user["balance"] += winnings
        
        self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"])
        
        embed = self.utility.create_roll_embed_message(interactions, bet, number, rolled_number, winnings, user["balance"])
        
        await interactions.response.send_message(embed=embed)
        
        
        