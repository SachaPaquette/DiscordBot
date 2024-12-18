from Commands.Services.database import Database
import random
from Config.logging import setup_logging
from Config.config import conf
from Commands.Services.utility import EmbedMessage
# Create a logger for this file
logger = setup_logging("gambling.py", conf.LOGS_PATH)


class Gambling():
    def __init__(self, server_id):
        self.database = Database.getInstance()
        self.collection = self.database.get_collection(server_id)
        self.embedMessage = EmbedMessage()

    def get_slot_symbols(self):
        return random.choices(['🍒', '🍋', '🍊', '🍉', '⭐', '🔔', '7️⃣'], k=3)

    def calculate_payout(self, symbols, bet):
        if symbols[0] == symbols[1] == symbols[2]:
            if symbols[0] == '7️⃣':
                return bet * 10
            return bet * 5
        elif symbols[0] == symbols[1] or symbols[1] == symbols[2] or symbols[0] == symbols[2]:
            return bet * 2
        else:
            return -bet

    async def gamble(self, interactions, bet: int):
        try:
            if not await self.is_valid_bet(interactions, bet):
                return

            user = self.get_user(interactions)

            if not self.has_sufficient_balance(user, bet):
                await self.send_insufficient_balance_message(interactions)
                return
            symbols = self.get_slot_symbols()
            payout = self.calculate_payout(symbols, bet)
            self.update_user_balance(interactions, user, payout, bet)

            if payout > 0:
                self.update_user_experience(interactions, payout)

            # Send the initial result as a follow-up message
            embed = self.embedMessage.create_gambling_embed_message(symbols, payout, user["balance"])
            await interactions.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in the gamble function in gambling.py: {e}")
            await interactions.followup.send("An unexpected error occurred while processing your gamble.")


    async def is_valid_bet(self, interactions, bet):
        if bet <= 0:
            await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
            return False
        return True

    def get_user(self, interactions):
        return self.database.get_user(interactions)

    def has_sufficient_balance(self, user, bet):
        return user["balance"] >= bet

    async def send_insufficient_balance_message(self, interactions):
        await interactions.response.send_message("You don't have enough money to bet that amount.")

    def update_user_balance(self, interactions, user, payout, bet):
        user["balance"] += payout
        self.database.update_user_balance(
            interactions.guild.id, interactions.user.id, user["balance"], bet)

    def update_user_experience(self, interactions, payout):
        self.database.update_user_experience(interactions, payout)

    async def send_initial_message(self, interactions):
        await interactions.response.send_message(f'{interactions.user.mention} spun the slots!', ephemeral=False)
        return await interactions.original_response()

    async def edit_result_message(self, result_message, symbols, payout, balance):
        await result_message.edit(content=None, embed=self.embedMessage.create_gambling_embed_message(symbols, payout, balance))
