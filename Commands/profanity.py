# Used to check for profanity in messages and warn users
from .Profanity.better_profanity import profane
from Commands.utility import Utility
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("profanity.py", conf.LOGS_PATH)

class Profanity():
    def __init__(self, bot):
        self.bot = bot
        self.profanity_filter = profane()
        self.utility = Utility()
    async def on_message_command(self, message, commands):
        try:
            
            # Ignore messages sent by the bot
            if message.author == self.bot.user:
                return
            
            #TODO Make sure the message is a command otherwise people can abuse this
            # Ignore message that is a command
            
            
            # Check that it is not an emoji reaction (:emoji:)
            if self.utility.is_emoji(message.content):
                return
            
            # Check if the message contains profanity
            if self.profanity_filter.contains_profanity(message.content):
                # Put a reaction on the user's message to warn them
                await message.add_reaction("🚫")
        except Exception as e:
            logger.error(f"Error while handling message: {e}")
            return
        
   