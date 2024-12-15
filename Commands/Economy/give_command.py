# Command to give money to another user
import discord
from Config.logging import setup_logging
from Commands.Services.database import Database
from Config.config import conf
# Create a logger for this file
logger = setup_logging("give_command.py", conf.LOGS_PATH)

class Give:
    def __init__(self):
        self.database = Database.getInstance()

    async def check_conditions(self, interactions, destination_user: discord.Member, amount: float):
        try:
            if not destination_user or not amount:
                await interactions.response.send_message(f'{interactions.user.mention}, you must specify a user and an amount to give.')
                return

            if destination_user.bot or destination_user.id == interactions.user.id:
                await interactions.response.send_message(f'{interactions.user.mention}, you can\'t give money to a bot or yourself.')
                return

            if amount <= 0:
                await interactions.response.send_message(f'{interactions.user.mention}, you must give a positive amount.')
                return
        except Exception as e:
            logger.error(
                f"Error in the check_conditions function in give_command.py: {e}")

    async def give_command(self, interactions, destination_user: discord.Member, amount: float):
        try:
            await self.check_conditions(interactions, destination_user, amount)

            user = self.database.get_user(interactions, fields=["balance"])
            if user["balance"] < amount:
                await interactions.response.send_message("You don't have enough money to give that amount.")
                return

            self.database.transfer_money(
                interactions.guild.id,
                interactions.user.id,
                destination_user.id,
                amount
            )

            await interactions.response.send_message(f'{interactions.user.mention} gave {destination_user.mention} {amount} dollars.')
        except Exception as e:
            logger.error(f"Error in the give function in give_command.py: {e}")
            return
