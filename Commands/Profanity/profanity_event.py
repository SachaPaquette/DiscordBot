# Used to check for profanity in messages and warn users
from .better_profanity import profane
from Commands.Services.utility import Utility
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("profanity.py", conf.LOGS_PATH)

class Profanity():
    _instance = None

    def __new__(cls, bot):
        if not cls._instance:
            cls._instance = super(Profanity, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, bot):
        # Initialize the class only once
        if self._initialized:
            return
        self.bot = bot
        self.profanity_filter = profane()
        self.utility = Utility()
        self._initialized = True

    async def on_message_command(self, message):
        try:
            # Check that it is not a message from the bot or an emoji reaction (:emoji:)
            if not message.author.bot and not self.utility.is_emoji(message.content) and self.profanity_filter.contains_profanity(message.content):
                await message.add_reaction("🚫")  
        except Exception as e:
            logger.error(f"Error while handling message: {e}")
            return
        
   