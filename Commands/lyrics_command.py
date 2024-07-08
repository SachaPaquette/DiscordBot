import re
from .Scripts import azlyrics
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
            # Check if the song session is None
            if song_session is None:
                await interactions.response.send_message('No song is currently playing.')
                return
            
            # Send a message that the bot is searching for lyrics (since this command takes a while to execute and the bot will timeout if it doesn't send a message within a couple of seconds)
            await interactions.response.send_message("Searching for lyrics...")
            original_message = await interactions.original_response()
            # get the lyrics of the song
            lyrics = await self.get_lyrics(song_session.get_song_title())
            
            # Check if the lyrics is None
            if lyrics is None:
                await original_message.edit(content='No lyrics found.')
                return
            
            # Format the lyrics since itc can be too long (max 2000 characters) and discord will not allow it
            # Send the first 2000 characters of the lyrics
            # And then send the rest of the lyrics in other messages
            if len(lyrics) > 2000:
                for i in range(0, len(lyrics), 2000):
                    await interactions.followup.send(lyrics[i:i+2000])
            else:
                await interactions.followup.send(lyrics)

        except Exception as e:
            await original_message.edit(content='No lyrics found.')
            logger.error(f"Error while searching for lyrics: {e}")