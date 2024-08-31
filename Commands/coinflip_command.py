import asyncio
import random 
import discord
from Config.logging import setup_logging
from Commands.database import Database
from Config.config import conf
from Commands.utility import Utility, EmbedMessage
from enum import Enum
# Create a logger for this file
logger = setup_logging("roll.py", conf.LOGS_PATH)

class CoinChoices(Enum):
    HEADS = "heads"
    TAILS = "tails"

class CoinFlip():
    def __init__(self):
        self.database = Database.getInstance()
        self.utility = Utility()
        self.embedMessage = EmbedMessage()
    async def coinflip_command(self, interactions, bet: float, opponent: discord.Member):
        try:
            # Check if the user is betting against themselves
            if opponent.id == interactions.user.id:
                await interactions.response.send_message(f'{interactions.user.mention}, you can\'t bet against yourself.')
                return
            
            
            # Check if the opponent is a bot
            if opponent.bot:
                await interactions.response.send_message(f'{interactions.user.mention}, you can\'t bet against a bot.')
                return
            
            # Check if the bet is positive
            if bet <= 0:
                await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
                return

            command_user = self.database.get_user(interactions)
            opposing_user = self.database.get_user(interactions, opponent.id)

            # Check if both users have enough money
            if not self.utility.has_sufficient_balance(command_user, bet):
                await interactions.response.send_message(f'{interactions.user.mention}, you don\'t have enough money to bet that amount.')
                return

            if not self.utility.has_sufficient_balance(opposing_user, bet):
                await interactions.response.send_message(f'{opponent.mention} doesn\'t have enough money to bet that amount.')
                return

            # Send a message with an emoji to react to
            self.message = await interactions.response.send_message(
                f'{interactions.user.mention} and {opponent.mention}, choose heads (🪙) or tails (🃏).', ephemeral=False)

            message = await interactions.original_response()

            # Add reactions to the message
            await message.add_reaction("🪙")
            await message.add_reaction("🃏")

            # Check function to ensure both users react
            def check(reaction, user):
                return user in [interactions.user, opponent] and str(reaction.emoji) in ["🪙", "🃏"]

            # Wait for reactions from both users
            command_user_reaction = await interactions.client.wait_for('reaction_add', timeout=60.0, check=check)
            opposing_user_reaction = await interactions.client.wait_for('reaction_add', timeout=60.0, check=check)

            if command_user_reaction[0].emoji == opposing_user_reaction[0].emoji:
                await message.edit(content='Both users cannot choose the same option. The game is canceled.')
                return


            # Deduct the bet from the user's balance
            command_user["balance"] -= bet
            opposing_user["balance"] -= bet

            # Flip a coin
            coin = random.choice([CoinChoices.HEADS, CoinChoices.TAILS])
            
            # Determine the result emoji
            result_emoji = "🪙" if coin == CoinChoices.HEADS else "🃏"

            # Determine the winner based on reactions
            winner = interactions.user if result_emoji in [reaction.emoji for reaction in message.reactions if reaction.count > 1 and reaction.users().first() == interactions.user] else opponent

            # Calculate the winnings
            winnings = bet * 2

            # Add the winnings to the winner's balance
            if winner == interactions.user:
                command_user["balance"] += winnings
            else:
                opposing_user["balance"] += winnings

            # Update the balances in the database
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, command_user["balance"])
            self.database.update_user_balance(interactions.guild.id, opponent.id, opposing_user["balance"])

            # Send a message with the result
            #await interactions.followup.send(f'{interactions.user.mention} bet {bet} dollars. The coin landed on {coin.value}. {winner.display_name} won {winnings} dollars.')

            embed = self.embedMessage.create_coinflip_embed_message(interactions, bet, coin.value, result_emoji, winner.display_name, winnings, command_user["balance"], opposing_user["balance"])

            await message.edit(embed=embed)
            
        except asyncio.TimeoutError:
            await message.edit(content='The game timed out. Both users need to react within 60 seconds.')

        except Exception as e:
            print(f"Error in the coinflip function: {e}")
            await message.edit(content='An error occurred. Please try again.')

        
       
        
        