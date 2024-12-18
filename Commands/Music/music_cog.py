
import discord
from discord.ext import commands
from Commands.Music.music import SongSession
from Commands.Music.queue_command import QueueOperations
from Commands.Music.lyrics_command import LyricsOperations
from Commands.Music.nowplaying_command import NowPlaying
from Commands.Services.utility import VoiceManager

from Config.logging import setup_logging



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None  # Song session instance

    def ensure_session(self, ctx):
        """Ensure a SongSession instance exists for the guild."""
        if not self.session:
            self.session = SongSession(ctx.guild, ctx)

    @commands.command(name="play", description="Play a song.")
    async def play(self, ctx, url: str):
        """Play a song from a given URL."""
        try:
            self.ensure_session(ctx)
            await self.session.play_command(ctx, url, self.bot.loop)
        except Exception as e:
            await ctx.send("An error occurred while trying to play the song.")

    @commands.command(name="pause", description="Pause the current song.")
    async def pause(self, ctx):
        """Pause the currently playing song."""
        if self.session:
            await self.session.pause_command(ctx)
        else:
            await ctx.send("No song is currently playing.")

    @commands.command(name="resume", description="Resume the paused song.")
    async def resume(self, ctx):
        """Resume the paused song."""
        if self.session:
            await self.session.resume_command(ctx)
        else:
            await ctx.send("No song is currently paused.")

    @commands.command(name="skip", description="Skip the current song.")
    async def skip(self, ctx):
        """Skip the currently playing song."""
        if self.session:
            await self.session.skip(ctx)
        else:
            await ctx.send("No song is currently playing to skip.")

    @commands.command(name="volume", description="Change the music volume.")
    async def volume(self, ctx, volume: int):
        """Change the bot's music volume."""
        if self.session:
            await self.session.change_volume(volume, ctx)
        else:
            await ctx.send("No song is currently playing.")

    @commands.command(name="stop", description="Stop the music.")
    async def stop(self, ctx):
        """Stop the music and clear the session."""
        if self.session:
            await self.session.stop(ctx.guild.voice_client)
            self.session = None  # Reset session
        else:
            await ctx.send("No music is playing.")

    @commands.command(name="queue", description="Display the song queue.")
    async def queue(self, ctx):
        """Display the current music queue."""
        if self.session:
            queue_operations = QueueOperations(self.session)
            await queue_operations.display_queue_command(ctx)
        else:
            await ctx.send("The music queue is empty.")

    @commands.command(name="nowplaying", description="Display the currently playing song.")
    async def nowplaying(self, ctx):
        """Display information about the currently playing song."""
        if self.session:
            nowplaying_command = NowPlaying()
            await nowplaying_command.nowplaying_command(ctx, self.session)
        else:
            await ctx.send("No song is currently playing.")

    @commands.command(name="lyrics", description="Display the lyrics of the current song.")
    async def lyrics(self, ctx):
        """Display the lyrics for the currently playing song."""
        if self.session:
            lyrics_command = LyricsOperations(self.bot)
            await lyrics_command.lyrics_command(ctx, self.session)
        else:
            await ctx.send("No song is currently playing.")

    @commands.command(name="shuffle", description="Shuffle the music queue.")
    async def shuffle(self, ctx):
        """Shuffle the current music queue."""
        if self.session:
            queue_operations = QueueOperations(self.session)
            await queue_operations.shuffle_queue_command(ctx)
        else:
            await ctx.send("No music queue to shuffle.")

    @commands.command(name="clear", description="Clear the music queue.")
    async def clear(self, ctx):
        """Clear the current music queue."""
        if self.session:
            queue_operations = QueueOperations(self.session)
            await queue_operations.clear_command(ctx)
        else:
            await ctx.send("The music queue is already empty.")
            
    @commands.command(name='leave', description='Makes the bot leave the voice channel.')
    async def leave(self, interactions):
        try:
            voice_manager = VoiceManager()
            await voice_manager.leave(interactions)
        except Exception as e:
            raise e
async def setup(bot):
    await bot.add_cog(Music(bot))
