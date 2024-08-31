import asyncio
import random 
import discord
from Config.logging import setup_logging
from Commands.Services.database import Database
from Config.config import conf
from Commands.Services.utility import Utility, EmbedMessage
from enum import Enum
# Create a logger for this file
logger = setup_logging("roll.py", conf.LOGS_PATH)

class CoinChoices(Enum):
    HEADS = "🪙"
    TAILS = "🃏"

class CoinFlip():
    def __init__(self):
        self.database = Database.getInstance()
        self.utility = Utility()
        self.embedMessage = EmbedMessage()
    async def coinflip_command(self, interactions, bet: float, opponent: discord.Member):
        try:
            await self.check_bet_validity(interactions, bet, opponent)
            command_user, opposing_user = await self.get_users(interactions, opponent)
            message = await self.send_reaction_message(interactions, opponent)
            reactions = await self.get_reactions(interactions, message)
            if reactions[0][0].emoji == reactions[1][0].emoji:
                await interactions.edit_original_response(content='Both users cannot choose the same option. The game is canceled.')
                return
            winner, winnings = await self.determine_winner(interactions, reactions, bet)
            self.update_balances(interactions, command_user, opposing_user, winner, winnings, bet)
            await self.send_result_message(interactions, bet, winner, winnings, CoinChoices(reactions[0][0].emoji), reactions[0][0].emoji, command_user, opposing_user)
        except asyncio.TimeoutError:
            await interactions.edit_original_response(content='The game timed out. Both users need to react within 60 seconds.')

        except Exception as e:
            logger.error(f"Error in the coinflip function: {e}")
            await interactions.edit_original_response(content='An error occurred. Please try again.')

    async def check_bet_validity(self, interactions, bet, opponent):
        if opponent.id == interactions.user.id:
            await interactions.response.send_message(f'{interactions.user.mention}, you can\'t bet against yourself.')
            raise Exception
        if opponent.bot:
            await interactions.response.send_message(f'{interactions.user.mention}, you can\'t bet against a bot.')
            raise Exception
        if bet <= 0:
            await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
            raise Exception

    async def get_users(self, interactions, opponent):
        command_user = self.database.get_user(interactions)
        opposing_user = self.database.get_user(interactions, opponent.id)
        return command_user, opposing_user

    async def send_reaction_message(self, interactions, opponent):
        try:
            await interactions.response.send_message(
                f'{interactions.user.mention} and {opponent.mention}, choose heads (🪙) or tails (🃏).')
            
            message = await interactions.original_response()
            await message.add_reaction("🪙")
            await message.add_reaction("🃏")
            return message
        except Exception as e:
            logger.error(f"Error sending the reaction message: {e}")
            return
        
    async def get_reactions(self, interactions, message):
        try:
            def command_user_check(reaction, user):
                return user == interactions.user and str(reaction.emoji) in ["🪙", "🃏"]
            
            def opposing_user_check(reaction, user):
                return user == message.mentions[0] and str(reaction.emoji) in ["🪙", "🃏"]
            
            command_user_reaction = await interactions.client.wait_for('reaction_add', timeout=60.0, check=command_user_check)
            opposing_user_reaction = await interactions.client.wait_for('reaction_add', timeout=60.0, check=opposing_user_check)
            return command_user_reaction, opposing_user_reaction
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError
        except Exception as e:
            logger.error(f"Error getting reactions: {e}")
            return
        
    async def determine_winner(self, interactions, reactions, bet):
        try:
            coin = random.choice([CoinChoices.HEADS, CoinChoices.TAILS])
            result_emoji = "🪙" if coin == CoinChoices.HEADS else "🃏"
            winner = interactions.user if reactions[0][0].emoji == result_emoji else interactions.message.mentions[0]
            winnings = bet * 2
            return winner, winnings
        except Exception as e:
            logger.error(f"Error determining the winner: {e}")
            return None, None  # Return None explicitly
    def update_balances(self, interactions, command_user, opposing_user, winner, winnings, bet):
        try:
            
            command_user["balance"] -= bet
            opposing_user["balance"] -= bet
            if winner == interactions.user:
                command_user["balance"] += winnings
            else:
                opposing_user["balance"] += winnings
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, command_user["balance"])
            self.database.update_user_balance(interactions.guild.id, interactions.message.mentions[0].id, opposing_user["balance"])
        except Exception as e:
            logger.error(f"Error updating balances: {e}")
            return
        
    async def send_result_message(self, interactions, bet, winner, winnings, coin, result_emoji, command_user, opposing_user):
        try:
            
            embed = self.embedMessage.create_coinflip_embed_message(interactions, bet, coin.value, result_emoji, winner.display_name, winnings, command_user["balance"], opposing_user["balance"])
            await interactions.edit_original_response(embed=embed)
        except Exception as e:
            logger.error(f"Error in the coinflip function in gambling.py: {e}")
            return
        
       
        
        