import datetime
import os
import discord
from discord import app_commands
from discord.ext import commands
from Commands.Information.health_command import HealthCheck
from Commands.Information.user_info_command import UserInfo
from Commands.Inventory.inventory_command import Inventory
from Commands.Inventory.leaderboard_command import Leaderboard

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
    @app_commands.command(name="inventory", description="Check your inventory.")
    async def inventory(self, ctx):
        try:
            inventory = Inventory()
            await inventory.display_inventory(ctx)
        except Exception as e:
            
            raise e
    @app_commands.command(name="userinfo", description="Get information about a user.")
    async def user_information(self, interactions, *, member: discord.Member = None):
        """
        Fetches and displays information about a user.

        Parameters:
        - interactions (discord.Context): The context of the command.
        - member (discord.Member, optional): The member to fetch information about. Defaults to None.

        Raises:
        - Exception: If there is an error in fetching the user information.

        Examples:
        ` /userinfo @user -> 
            User Information - Chencho
            Username
            discordusername
            User ID
            0000000000
            Joined Server On
            2017-02-26 20:37:34
            Account Created On
            2017-02-18 04:04:35 `

        Returns:
        - None
        """
        try:
            user_info = UserInfo()
            # Create the embed message that will display the user information (username, ID, join date, account creation date)
            await user_info.fetch_user_information(interactions=interactions, member=member)
        except Exception as e:
            raise e
        
    @app_commands.command(name='leaderboard', description='Display the leaderboard.')
    async def leaderboard(self, interactions):
        """
        Display the leaderboard.

        Parameters:
        - interactions (Context): The context object representing the invocation context of the command.

        Returns:
        - None
        """
        try:

            leaderboard = Leaderboard()
            await leaderboard.leaderboard_command(interactions)
        except Exception as e:
            raise e
    @app_commands.command(name='rank', description='Display your rank.')
    async def rank(self, interactions):
        """
        Display the user's rank.

        Parameters:
        - interactions (Context): The context object representing the invocation context of the command.

        Returns:
        - None
        """
        try:
            leaderboard = Leaderboard()
            # Call the rank function in Gambling
            await leaderboard.rank_command(interactions)
        except Exception as e:
            raise e
        
    @app_commands.command(name='health', description='Display information about the bot.')
    async def health(self, interactions):
        """
        Check if the bot is alive and provide detailed health information.
        Used to sync the commands with the guild.
        """
        # Check if the BOT_OWNER_ID is set in the environment variables
        if not os.environ.get("BOT_OWNER_ID"):
            await interactions.response.send_message("The BOT_OWNER_ID is not set in the environment variables.")
            return
        # Make sure the user has the correct permissions (by having the userid of the bot owner)
        if interactions.user.id != int(os.environ.get("BOT_OWNER_ID")):
            await interactions.response.send_message("You do not have permission to run this command.")
            return

        try:
            health_check = HealthCheck(self.bot)
            await health_check.health_command(interactions, self.bot, self.start_time)
            await self.bot.tree.sync()
        except Exception as e:
            print(f"Error in the health command: {e}")
            raise e
async def setup(bot):
    await bot.add_cog(Information(bot))