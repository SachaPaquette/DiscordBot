import discord
from discord import app_commands
from discord.ext import commands
from Commands.Games.blackjack_command import BlackJack
from Commands.Games.case_command import Case
from Commands.Games.coinflip_command import CoinFlip
from Commands.Games.gambling_command import Gambling
from Commands.Games.roll_command import Roll
from Commands.Games.rockpaperscissors_command import RockPaperScissors, Choices
from Commands.Games.capsule_command import Capsule


class Games(commands.Cog):
    """
    Cog to handle all game-related slash commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="blackjack", description="Play blackjack with a bet amount.")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        try:
            await interaction.response.defer()
            blackjack = BlackJack()
            await blackjack.blackjack_command(interaction, bet)
        except Exception as e:
            await interaction.followup.send("An error occurred while playing blackjack.")
            print(f"Error in blackjack command: {e}")

    @app_commands.command(name="coinflip", description="Flip a coin and bet against another user.")
    async def coinflip(self, interaction: discord.Interaction, bet: float, user: discord.Member):
        try:
            await interaction.response.defer()
            coinflip = CoinFlip()
            await coinflip.coinflip_command(interaction, bet, user)
        except Exception as e:
            await interaction.followup.send("An error occurred while flipping a coin.")
            print(f"Error in coinflip command: {e}")

    @app_commands.command(name="case", description="Open a Counter-Strike case.")
    async def case(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            case = Case(interaction.guild.id)
            await case.process_case(interaction)
        except Exception as e:
            await interaction.followup.send("An error occurred while opening a case.")
            print(f"Error in case command: {e}")

    @app_commands.command(name="sticker", description="Open a Counter-Strike sticker capsule.")
    async def capsule(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(thinking=True)

            capsule = Capsule(interaction.guild.id)
            await capsule.open_capsule(interaction)
        except Exception as e:
            await interaction.followup.send("An error occurred while opening a capsule.")
            print(f"Error in capsule command: {e}")

    @app_commands.command(name="rps", description="Play rock-paper-scissors with a bet.")
    async def rps(self, interaction: discord.Interaction, bet: float, choice: Choices):
        try:
            await interaction.response.defer()
            rps = RockPaperScissors()
            await rps.rockpaperscissors_command(interaction, bet, choice)
        except Exception as e:
            await interaction.followup.send("An error occurred while playing rock-paper-scissors.")
            print(f"Error in rps command: {e}")

    @app_commands.command(name="roll", description="Roll a dice between 1 and 100.")
    async def roll(self, interaction: discord.Interaction, bet: int, number: int):
        try:
            await interaction.response.defer()
            roll = Roll()
            await roll.roll_command(interaction, bet, number)
        except Exception as e:
            await interaction.followup.send("An error occurred while rolling the dice.")
            print(f"Error in roll command: {e}")

    @app_commands.command(name="gamble", description="Gamble your money.")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        try:
            await interaction.response.defer()
            gambling = Gambling(interaction.guild.id)
            await gambling.gamble(interaction, amount)
        except Exception as e:
            await interaction.followup.send("An error occurred while gambling.")
            print(f"Error in gamble command: {e}")


async def setup(bot):
    """
    Function to add the Games cog to the bot.
    """
    await bot.add_cog(Games(bot))
