import azapi
from Commands.music import SongSession
import re
class LyricsOperations: 
    def __init__(self, bot):
        self.bot = bot

    def parse_song_title(self, song_title):
        try:
            # The song title is the Youtube video title. There is no specific format for it. (ex. "Song Title - Artist")
            regex_pattern = f"^(.+?)[-\|♦\(](.+?)(?:(?<=\()\b[^\)]+\b(?=\)))?.*$"
            # Get the song title and artist name from the Youtube video title
            song_title, artist_name = re.search(regex_pattern, song_title).groups()
            
            # Return the song title
            return song_title
        except Exception as e:
            print(f"Error while parsing song title: {e}")
            return None
        
    async def get_lyrics(self, song_title):
        try:
            # Create an AZlyrics object
            API = azapi.AZlyrics('google', accuracy=0.5)

            # Get the song's title
            song_title= self.parse_song_title(song_title)
            
            # Assign the song title to the AZlyrics object
            API.title = song_title
            # Get the lyrics of the song
            lyrics = API.getLyrics(save=False)
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
            print(lyrics)
            
            # Check if the lyrics is None
            if lyrics is None:
                await interactions.edit_original_response('No lyrics found.')
                return
            
            # Send the lyrics (edit the original response)
            await interactions.edit_original_response(content=lyrics)
        except Exception as e:
            await interactions.response.send_message('No lyrics found.')
            print(f"Error while searching for lyrics: {e}")