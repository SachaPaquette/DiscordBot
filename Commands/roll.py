# Command to roll a number (1-100), the closer the user is to the number, the more money they win.
import random 
import discord
from Config.logging import setup_logging
from Commands.database import Database
from Config.config import conf
from Commands.utility import Utility, EmbedMessage
# Create a logger for this file
logger = setup_logging("roll.py", conf.LOGS_PATH)

class Roll():
    def __init__(self):
        self.database = Database.getInstance()
        self.utility = Utility()
        self.embedMessage = EmbedMessage()
        
    def calculate_winnings(self, bet, number, rolled_number):
        # Calculate the difference between the number and the rolled number
        difference = abs(number - rolled_number)
        
        # Define a dictionary to map difference ranges to multipliers
        multipliers = {
            range(0,0): 10,
            range(1, 6): 5,
            range(6, 11): 2,
        }
        
        # Iterate through the multipliers dictionary
        for key, value in multipliers.items():
            # Check if the difference is in the key
            if difference in key:
                # Calculate the winnings
                return bet * value
        
        # Default case if no match found
        return 0
        
    async def roll_command(self, interactions, bet: float, number: int):
        try:
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
            
            # Add the winnings to the user's balance
            user["balance"] += self.calculate_winnings(bet, number, rolled_number)
            
            # Update the user's balance in the database
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"], bet)
            
            # Create an embed message
            embed = self.embedMessage.create_roll_embed_message(interactions, bet, number, rolled_number, self.calculate_winnings(bet, number, rolled_number), user["balance"])
            
            # Send the embed message to the user
            await interactions.response.send_message(embed=embed)
            
        except Exception as e:
            await interactions.response.send_message(f'{interactions.user.mention}, there was an error processing your request.')
            logger.error(f"Error in the roll_command function: {e}")
            return
        