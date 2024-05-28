
from Commands.music import SongSession
import re, time
from .Scripts import azlyrics
class LyricsOperations: 
    def __init__(self, bot):
        self.bot = bot
        self.fetch_lyrics = azlyrics.FetchLyrics('google', accuracy=0.5)
    def parse_song_title(self, song_title):
        try:
            # The song title is the Youtube video title. There is no specific format for it. (ex. "Song Title - Artist")
            regex_pattern = f"^(.+?)[-\|♦\(](.+?)(?:(?<=\()\b[^\)]+\b(?=\)))?.*$"
            pattern = re.compile(
            r'^(?P<artist>.+?)\s*[-|:|by|]\s*(?P<title>.+?)(\s*\(.*?\)|\s*\[.*?\]|\s*Official.*|)$', re.IGNORECASE)
            match = pattern.match(song_title)
            if match:
                artist_name = match.group('artist')
                song_title = match.group('title')
            else:
                artist_name = None
                song_title = None
 
            # Return the song title
            return song_title, artist_name
        except Exception as e:
            print(f"Error while parsing song title: {e}")
            return None
        
    async def get_lyrics(self, song_title):
        try:
            # Get the song's title
            song_title, artist_name = self.parse_song_title(song_title)
            
            # Assign the song title to the AZlyrics object
            self.fetch_lyrics.title = song_title
            self.fetch_lyrics.artist = artist_name
            # Get the lyrics of the song
            lyrics = self.fetch_lyrics.getLyrics(save=False)
            # Return the lyrics
            return lyrics
        except Exception as e:
            print(f"Error while getting lyrics: {e}")
            return None
        
        

    async def lyrics_command(self, interactions, song_session):
        """Searches for lyrics of the song you want"""
        try:
            # Send a message that the bot is searching for lyrics (since this command takes a while to execute and the bot will timeout if it doesn't send a message within a couple of seconds)
            await interactions.response.send_message("Searching for lyrics...")
            
            # get the lyrics of the song
            lyrics = await self.get_lyrics(song_session.get_song_title())
            
            # Check if the lyrics is None
            if lyrics is None:
                await interactions.response.send_message('No lyrics found.')
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
            await interactions.followup.send('No lyrics found.')
            print(f"Error while searching for lyrics: {e}")