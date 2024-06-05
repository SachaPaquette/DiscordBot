from .Profanity.better_profanity import profane
from Commands.utility import Utility
# Used to check for profanity in messages and warn users
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
            print(f"Error while handling message: {e}")
            return
        
   