# Purpose: Command to display an user informations (Username, userID, server joined date, account creation date).
import discord 
class UserInfo:
    async def fetch_user_information(self, interactions, member):
            """
            Fetches and displays user information.

            Parameters:
            - interactions: The interaction object.
            - member: The member whose information is to be fetched.

            Returns:
            None
            """
            try:
                # If no member is mentioned, default to the author of the command
                if member is None:
                    member = interactions.author

                # Create an embed to display user information
                embed = discord.Embed(title=f'User Information - {member.display_name}', color=member.color)
                # Add the user's avatar
                embed.set_thumbnail(url=member.avatar)
                # Add the user's information
                embed.add_field(name='Username', value=member.name, inline=True)
                # Add the user's ID
                embed.add_field(name='User ID', value=member.id, inline=True)
                # Add the user's join date to the server
                embed.add_field(name='Joined Server On', value=member.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                # Add the user's account creation date
                embed.add_field(name='Account Created On', value=member.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                
                # Send the embed
                await interactions.response.send_message(embed=embed)

            except Exception as e:
                print(f"Error: {e}")
                raise e
