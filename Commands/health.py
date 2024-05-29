import datetime
import discord

class HealthCheck():    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        
    def create_bot_uptime(self):
        """
        Calculates the uptime of the bot based on the start time.

        Returns:
            str: A string representation of the bot's uptime in the format "X days, X hours, X minutes, X seconds".
        
        Raises:
            Exception: If there is an error during the calculation.
        """
        try:
            # Get the current time for reference
            current_time = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
            # Calculate the uptime
            uptime_delta = current_time - self.start_time
            # Calculate the days, hours, minutes, and seconds that make up the uptime
            days, hours, minutes, seconds = self.calculate_time_components(uptime_delta)
            # Create a string representation of the uptime
            uptime_str = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

            return uptime_str
        except Exception as e:
            print(f"Error in create_bot_uptime in health.py: {e}")
            raise e
        
    
    async def health_command(self, interactions, bot):
        """
        Check if the bot is running and provide detailed health information.
        """
        try:
            # Get the bot's latency
            latency = round(bot.latency * 1000)  # in milliseconds

            # Get the bot's uptime
            uptime_str = self.create_bot_uptime()

            # Create an embed with health information
            embed = discord.Embed(title="**Bot Health Check**", color=discord.Color.green())
            embed.add_field(name="Bot Status", value="I am alive and functioning!", inline=False)
            embed.add_field(name="Latency", value=f"{latency} ms", inline=False)
            embed.add_field(name="Uptime", value=uptime_str, inline=False)
            embed.add_field(name="Channels", value=len(self.bot.guilds), inline=True)
            embed.add_field(name="Users", value=sum([guild.member_count for guild in self.bot.guilds]), inline=True)

            # Send the embed as a response
            await interactions.response.send_message(embed=embed)

        except Exception as e:
            print(f"Error in the health command in health.py: {e}")
            raise e
        
    @staticmethod
    def calculate_time_components(delta):
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
            print(f"Error in calculate_time_components in health.py: {e}")