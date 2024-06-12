# Command to display the leaderboard of the server.
from Commands.utility import Utility
from Commands.database import Database
from .UserProfile.user import UserCard
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("leaderboard.py", conf.LOGS_PATH)
class Leaderboard():
    def __init__(self):
        self.utility = Utility()
        self.user_card = UserCard()
        self.database = Database.getInstance()
        
    
    # Display a leaderboard of all the users experience
    async def leaderboard_command(self, interactions):
        try:
            # Get the top 10 users
            users = self.database .get_top_users(interactions.guild.id, 10)
            
            # Create an embed message that contains the top 10 users
            embed = await self.utility.create_leaderboard_embed(interactions, users)
                
            # Send the embed
            await interactions.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"An error occurred when trying to display the leaderboard. {e}")
            raise e
        
    async def rank_command(self, interactions):
        try:
            # Get the user's rank
            user = self.database.get_user(interactions.guild.id, interactions.user.id)
            rank = user["level"]
            total_bet = user["total_bet"]

            # Create an embed message that contains the user's rank
            embed = self.utility.create_rank_embed(interactions, rank, total_bet)
                
            # Send the embed
            await interactions.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"An error occurred when trying to display the rank. {e}")
            raise e