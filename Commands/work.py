# Simulate working and gives a random amount of money
import time, random
from Config.logging import setup_logging
from Config.config import conf
from Commands.database import Database
# Create a logger for this file
logger = setup_logging("work.py", conf.LOGS_PATH)
class Work():
    def __init__(self):
        self.database = Database.getInstance()
    async def work_command(self, interactions):
        try:
            # Get the user's data
            user = self.database.get_user(interactions.guild.id, interactions.user.id)
            # Check if the user has worked in the last 10 minutes
            if user.get("last_work", 0) + 600 > time.time():
                await interactions.response.send_message("You can only work every 10 minutes.")
                return
            money_earned = random.randint(1, 1000)
            # Update the user's balance
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"] + money_earned, 0, True)
            # Send a message to the user
            await interactions.response.send_message(f"Congratulations! You earned ${money_earned}, you now have {(user['balance'] + money_earned):.2f} dollars.")
        except Exception as e:
            logger.error(f"Error in the work function in gambling.py: {e}")
            return