from .Profanity.better_profanity import profane
# Used to check for profanity in messages and warn users
class Profanity():
    def __init__(self, bot):
        self.bot = bot
        self.profanity_filter = profane()

    async def on_message_command(self, message):
        try:
            
            # Ignore messages sent by the bot
            if message.author == self.bot.user:
                return
            
            #TODO Make sure the message is a command otherwise people can abuse this
            # Ignore message that is a command
            if message.content.startswith("/"):
                return
            
            
            # Check if the message contains profanity
            if self.profanity_filter.contains_profanity(message.content):
                # Send a warning message
                await message.channel.send(f"{message.author.mention}, please refrain from using profanity.")
        except Exception as e:
            print(f"Error while handling message: {e}")
            return
        
   