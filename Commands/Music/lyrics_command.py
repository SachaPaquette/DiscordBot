import re
from ..Scripts import azlyrics
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("lyrics.py", conf.LOGS_PATH)
class LyricsOperations: 
    def __init__(self, bot):
        self.bot = bot
        self.fetch_lyrics = azlyrics.FetchLyrics('google', accuracy=0.5)
    def parse_song_title(self, song_title):
        try:
            # The song title is the Youtube video title. There is no specific format for it. (ex. "Song Title - Artist")
            match = re.compile(r'^(?P<artist>.+?)\s*[-|:|by|]\s*(?P<title>.+?)(\s*\(.*?\)|\s*\[.*?\]|\s*Official.*|)$', re.IGNORECASE).match(song_title)
            if match is None:
                raise Exception("Invalid song title format")
            # Return the song title
            return match.group('title'), match.group('artist')
        except Exception as e:
            logger.error(f"Error while parsing song title: {e}")
            return None
        
    async def get_lyrics(self, song_title):
        try:
            # Get the song's title
            song_name, artist_name = self.parse_song_title(song_title)
            print(song_name, artist_name)
            # Assign the song title to the AZlyrics object
            self.fetch_lyrics.title = song_name
            self.fetch_lyrics.artist = artist_name

            # Return the lyrics
            return self.fetch_lyrics.getLyrics(save=False)
        except Exception as e:
            logger.error(f"Error while getting lyrics: {e}")
            return None

    async def lyrics_command(self, interactions, song_session):
        """Searches for lyrics of the song you want"""
        try:
            if not song_session:
                await self.send_message(interactions, 'No song is currently playing.')
                return

            await self.send_message(interactions, "Searching for lyrics...")
            original_message = await interactions.original_response()

            lyrics = await self.get_lyrics(song_session.get_song_title())

            if not lyrics:
                await original_message.edit(content='No lyrics found.')
                return

            await self.send_lyrics(interactions, original_message, lyrics)
        except Exception as e:
            await original_message.edit(content='No lyrics found.')
            logger.error(f"Error while searching for lyrics: {e}")
            
    async def send_message(self, interactions, content):
        """Helper function to send a message"""
        await interactions.response.send_message(content)
       
    async def send_lyrics(self, interactions, original_message, lyrics):
        """Helper function to send lyrics in chunks"""
        if len(lyrics) > 2000:
            await original_message.edit(content=lyrics[:2000])
            for i in range(2000, len(lyrics), 2000):
                await interactions.followup.send(lyrics[i:i+2000])
        else:
            await original_message.edit(content=lyrics)