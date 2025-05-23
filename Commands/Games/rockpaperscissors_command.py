# Rock paper scissors command
from Commands.Services.utility import Utility, EmbedMessage
from Config.logging import setup_logging
from Config.config import conf
import discord
import random
from Commands.Services.database import Database
# Create a logger for this file
logger = setup_logging("rockpaperscissors.py", conf.LOGS_PATH)
from enum import Enum

class Choices(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"
    
class GameStates(Enum):
    WIN = "You win!"
    LOSE = "You lose!"
    TIE = "It's a tie!"


class RockPaperScissors():
    def __init__(self):
        self.utility = Utility()
        self.choices = [Choices.ROCK, Choices.PAPER, Choices.SCISSORS]
        self.database = Database.getInstance()
        self.embedMessage = EmbedMessage()
        
    def game_logic(self, user_choice, bot_choice):
        winning_conditions = {
            Choices.ROCK: Choices.SCISSORS,
            Choices.PAPER: Choices.ROCK,
            Choices.SCISSORS: Choices.PAPER
        }
        
        if bot_choice == winning_conditions[user_choice]:
            return GameStates.WIN
        elif bot_choice == user_choice:
            return GameStates.TIE
        else:
            return GameStates.LOSE
        
        
    async def rockpaperscissors_command(self, interactions, bet: float, choice: Choices):
        try:
            # Check if the bet is positive
            if bet <= 0:
                await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
                return
            # Check if the user has enough money
            user = self.database.get_user(interactions)
            if not self.utility.has_sufficient_balance(user, bet):
                await interactions.response.send_message(f'{interactions.user.mention}, you are too broke.')
                return
            # Get the bot's choice 
            bot_choice = random.choice(self.choices)
            # Calculate the profit
            profit = bet if self.game_logic(choice, bot_choice) == GameStates.WIN else -bet if self.game_logic(choice, bot_choice) == GameStates.LOSE else 0
            # Update the user's balance
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"] + profit)
            # Send the result to the user 
            await interactions.response.send_message(embed=self.embedMessage.create_rockpaperscissors_embed(
                choice.value, bot_choice.value,  self.game_logic(choice, bot_choice).value, bet, user["balance"] + profit, interactions.user.display_name, profit, bet
            ))
        except Exception as e:
            logger.error(f"Error in the rockpaperscissors_command function: {e}")
            await interactions.response.send_message("An error occurred while processing your request.")

        
        