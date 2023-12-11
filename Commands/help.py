
from discord.ext import commands
from dotenv import load_dotenv


class CustomHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        # Return a clean string denoting the signature of a command (e.g. !help [command])
        return f"!{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        embed = self.context.bot.embed_template()
        embed.description = "Type `!help command` for more info on a command."

        for cog, commands in mapping.items():
            if cog:
                cog_name = cog.qualified_name
                cog_commands = [self.get_command_signature(c) for c in commands]
                embed.add_field( value="\n".join(cog_commands), inline=False)
            else:
                other_commands = [self.get_command_signature(c) for c in commands]
                embed.add_field(value="\n".join(other_commands), inline=False)

        embed.set_footer(text="You can also type !help category for more info on a category.")
        await self.get_destination().send(embed=embed)

        
    async def send_command_help(self, command):
        embed = self.context.bot.embed_template()
        embed.title = f"Command Help: {command.qualified_name}"
        embed.description = command.help or "No help available."

        await self.get_destination().send(embed=embed)  