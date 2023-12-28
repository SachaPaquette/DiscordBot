import discord
class NowPlaying():    
        
    async def nowplaying_command(self, ctx, session):
        try:
            # Get the voice client
            vc = ctx.voice_client
            
            # Check if the bot is playing something
            if vc is None or not vc.is_playing():
                await ctx.send("No music is currently playing.")
                return
            
            # Get the title of the song
            song_title = session.get_song_title()
            
            # Check if the song title is None
            if song_title is None:
                await ctx.send("No music is currently playing.")
                return

            # Create an embed message that contains the title of the song, the thumbnail, and the duration
            embed = discord.Embed(
                title="Now Playing", description=song_title, color=discord.Color.green())
            
            # Add the thumbnail if available and the song duration
            if session.thumbnail is not None:
                embed.set_thumbnail(url=session.thumbnail)
            if session.song_duration is not None:
                embed.add_field(name="Duration",
                                value=session.song_duration)
                
            # Send the embed
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"An error occurred when trying to display the song. {e}")
            raise e