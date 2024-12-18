import discord
from discord.ext import commands
from discord import app_commands
from Commands.Economy.balance_command import Balance
from Commands.Economy.portfolio_command import Portfolio
from Commands.Economy.stocks_command import Options, Stocks
from Commands.Economy.work_command import Work
from Commands.Economy.give_command import Give


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Check your balance.")
    async def balance(self, interaction: discord.Interaction):
        try:
            balance = Balance()
            await balance.balance_command(interaction)
        except Exception as e:
            await interaction.response.send_message("An error occurred while checking balance.", ephemeral=True)
            print(f"Error in /balance: {e}")

    @app_commands.command(name="work", description="Work to earn money.")
    async def work(self, interaction: discord.Interaction):
        try:
            work = Work()
            await work.work_command(interaction)  
        except Exception as e:
            await interaction.response.send_message("An error occurred while working.", ephemeral=True)
            print(f"Error in /work: {e}")

    @app_commands.command(name="give", description="Give money to another user.")
    async def give(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        try:
            give = Give()
            await give.give_command(interaction, member, amount)  
        except Exception as e:
            await interaction.response.send_message("An error occurred while giving money.", ephemeral=True)
            print(f"Error in /give: {e}")
            
    @app_commands.command(name="stocks", description="Buy or sell stocks.")
    async def stocks(self, interactions, option: Options, stock: str, quantity: float):
        """
        Buy or sell stocks.

        Parameters:
        - interactions (Context): The context object representing the invocation context of the command.
        - option (Options): The option to buy or sell stocks.
        - stock (str): The stock to buy or sell.
        - quantity (int): The quantity of stocks to buy or sell.

        Returns:
        - None
        """
        try:
            stocks = Stocks()
            await stocks.stocks_command(interactions, option, stock, quantity)
        except Exception as e:
            raise e


    @app_commands.command(name='portfolio', description='Display your stock portfolio.')
    async def portfolio(self, interactions):
        """
        Display the user's stock portfolio.

        Parameters:
        - interactions (Context): The context object representing the invocation context of the command.

        Returns:
        - None
        """
        try:
            portfolio = Portfolio()
            await portfolio.portfolio_command(interactions)
        except Exception as e:
            raise e

async def setup(bot):
    await bot.add_cog(Economy(bot))
