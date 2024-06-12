# Rock paper scissors command
from Commands.utility import Utility
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
        self.utility = Utility()
        
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
        
        
    async def rockpaperscissors_command(self, interactions,bet:float, choice: Choices):
        
        if bet <= 0:
            await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
            return
        user = self.database.get_user(interactions.guild.id, interactions.user.id)
        if self.utility.has_sufficient_balance(user, bet) == False:    
            await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
            return

        bot_choice = random.choice(self.choices)
        
        user["balance"] -= bet
        
        if self.game_logic(choice, bot_choice) == GameStates.WIN:
            bet *= 2
            
        elif self.game_logic(choice, bot_choice) == GameStates.LOSE:
            bet = 0
            
        else:
            bet = bet    
            
        
        self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"] + bet)
        embed = self.utility.create_rockpaperscissors_embed(choice.value, bot_choice.value, self.game_logic(choice, bot_choice).value, bet, user["balance"] + bet, interactions.user.display_name)
        
        
        await interactions.response.send_message(embed=embed)
        
        return
    
        
        