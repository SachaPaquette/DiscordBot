# Rock paper scissors command
from Commands.utility import Utility, EmbedMessage
from Config.logging import setup_logging
from Config.config import conf
import discord
import random
from Commands.database import Database
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
            if bet <= 0:
                await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
                return
            
            user = self.database.get_user(interactions.guild.id, interactions.user.id)
            if not self.utility.has_sufficient_balance(user, bet):
                await interactions.response.send_message(f'{interactions.user.mention}, you are too broke.')
                return

            bot_choice = random.choice(self.choices)
            game_result = self.game_logic(choice, bot_choice)
            
            # Calculate profit and update bet
            if game_result == GameStates.WIN:
                profit = bet
                new_balance = user["balance"] + bet
            elif game_result == GameStates.LOSE:
                profit = -bet
                new_balance = user["balance"] - bet
            else:  # GameStates.DRAW
                profit = 0
                new_balance = user["balance"]

            self.database.update_user_balance(interactions.guild.id, interactions.user.id, new_balance)
            
            embed = self.embedMessage.create_rockpaperscissors_embed(
                choice.value, bot_choice.value, game_result.value, bet, new_balance, interactions.user.display_name, profit, bet
            )
            
            await interactions.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"Error in the rockpaperscissors_command function: {e}")
            await interactions.response.send_message("An error occurred while processing your request.")

        
        