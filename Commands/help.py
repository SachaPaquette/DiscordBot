
from discord.ext import commands
from dotenv import load_dotenv


class CustomHelpCommand(commands.HelpCommand):
    """
    A custom help command for the Discord bot.
    """

    async def send_bot_help(self, mapping):
        """
        Sends the bot help message. 

        Args:
            mapping (dict): A dictionary mapping cogs to their commands.
        """
        embed = self.context.bot.embed_template()
        embed.description = "Type `!help command` for more info on a command."

        for cog, commands in mapping.items():
            if cog:
                cog_name = cog.qualified_name
                cog_commands = [
                    self.get_command_signature(c) for c in commands]
                embed.add_field(value="\n".join(cog_commands), inline=False)
            else:
                other_commands = [
                    self.get_command_signature(c) for c in commands]
                embed.add_field(value="\n".join(other_commands), inline=False)

        embed.set_footer(
            text="You can also type !help category for more info on a category.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        """
        Sends the help message for a specific command.

        Args:
            command (Command): The command object.
        """
        embed = self.context.bot.embed_template()
        embed.title = f"Command Help: {command.qualified_name}"
        embed.description = command.help or "No help available."

        await self.get_destination().send(embed=embed)

    def get_command_signature(self, command):
        """
        Returns a clean string denoting the signature of a command. (e.g. !help [command])

        Args:
            command (Command): The command object.

        Returns:
            str: The command signature string.
        """
        return f"!{command.qualified_name} {command.signature}"
