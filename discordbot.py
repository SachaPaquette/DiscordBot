# Discord bot for the server
from dotenv import load_dotenv
import Commands.bot as bot_commands
load_dotenv()
if __name__ == "__main__":
    bot_commands.main()
    

