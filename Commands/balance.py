# Command to display the balance of a user
from Config.logging import setup_logging
from Config.config import conf
from Commands.database import Database
# Create a logger for this file
logger = setup_logging("balance.py", conf.LOGS_PATH)
class Balance():
    def __init__(self): 
        self.database = Database.getInstance()
    async def balance_command(self, interactions):
        try:
            # Get the user from the database
            user = self.database.get_user(interactions)
            # Send a message to the user with their balance
            await interactions.response.send_message(f'Your balance is {user["balance"]:.2f} dollars.')
        except Exception as e:
            logger.error(f"Error in the balance function in gambling.py: {e}")
            return