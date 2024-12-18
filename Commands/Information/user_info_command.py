# Purpose: Command to display an user informations (Username, userID, server joined date, account creation date).
import discord 
from Config.logging import setup_logging
from Config.config import conf
from Commands.Services.utility import EmbedMessage
# Create a logger for this file
logger = setup_logging("userinfo.py", conf.LOGS_PATH)
class UserInfo:
    def __init__(self):
        self.embedMessage = EmbedMessage()
    async def fetch_user_information(self, interactions, *, member):
            """
            Fetches and displays user information.

            Parameters:
            - interactions: The interaction object.
            - member: The member whose information is to be fetched.

            Returns:
            None
            """
            try:
                member = member or interactions.user
                await interactions.response.send_message(embed=self.embedMessage.create_embed_user_information(member))
            except Exception as e:
                logger.error(f"Error: {e}")
                raise e