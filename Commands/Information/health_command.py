import datetime
import discord
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("health.py", conf.LOGS_PATH)


class HealthCheck():
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.now(
            datetime.UTC).replace(tzinfo=None)

    def create_bot_uptime(self):
        """
        Calculates the uptime of the bot based on the start time.

        Returns:
            str: A string representation of the bot's uptime in the format "X days, X hours, X minutes, X seconds".

        Raises:
            Exception: If there is an error during the calculation.
        """
        try:
            # Calculate the days, hours, minutes, and seconds that make up the uptime
            days, hours, minutes, seconds = self.calculate_time_components(
                datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - self.start_time)
            # Return a string representation of the uptime
            return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        except Exception as e:
            logger.error(f"Error in create_bot_uptime in health.py: {e}")
            raise e

    async def health_command(self, interactions, bot):
        """
        Check if the bot is running and provide detailed health information.
        """
        try:
            # Create an embed with health information
            embed = discord.Embed(
                title="**Bot Health Check**", color=discord.Color.green())
            embed.add_field(name="Bot Status",
                            value="I am alive and functioning!", inline=False)
            embed.add_field(name="Latency",
                            value=f"{round(bot.latency * 1000)} ms", inline=False)
            embed.add_field(
                name="Uptime", value=self.create_bot_uptime(), inline=False)
            embed.add_field(name="Channels", value=len(
                self.bot.guilds), inline=True)
            embed.add_field(name="Users", value=sum(
                [guild.member_count for guild in self.bot.guilds]), inline=True)
            # Send the embed as a response
            await interactions.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"Error in the health command in health.py: {e}")
            raise e

    def calculate_time_components(self, delta):
        """
        Calculate days, hours, minutes, and seconds from a timedelta object.

        Parameters:
        - delta (datetime.timedelta): The timedelta to calculate components from.

        Returns:
        - Tuple[int, int, int, int]: Tuple containing days, hours, minutes, and seconds.
        """
        try:
            # Calculate days, hours, minutes, and seconds
            days, seconds = delta.days, delta.seconds
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            return days, hours, minutes, seconds
        except Exception as e:
            logger.error(
                f"Error in calculate_time_components in health.py: {e}")
            raise e
