# Command to display the leaderboard of the server.
from Commands.utility import Utility
from Commands.database import Database
class Leaderboard():
    # Display a leaderboard of all the users experience
    async def leaderboard_command(self, interactions):
        try:
            # Get the top 10 users
            users = Database.getInstance().get_top_users(10)
            
            # Create an embed message that contains the top 10 users
            embed = Utility.create_leaderboard_embed(users)
                
            # Send the embed
            await interactions.response.send_message(embed=embed)
        except Exception as e:
            print(f"An error occurred when trying to display the leaderboard. {e}")
            raise e
        
    async def rank_command(self, interactions):
        try:
            # Get the user's rank
            rank = Database.getInstance().get_user(interactions.user.id)["level"]
            
            # Create an embed message that contains the user's rank
            embed = Utility.create_rank_embed(rank)
                
            # Send the embed
            await interactions.response.send_message(embed=embed)
        except Exception as e:
            print(f"An error occurred when trying to display the rank. {e}")
            raise e