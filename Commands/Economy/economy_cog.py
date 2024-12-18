import discord
from discord.ext import commands
from discord import app_commands
from Commands.Economy.balance_command import Balance
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


async def setup(bot):
    await bot.add_cog(Economy(bot))
