import azapi
from Commands.music import SongSession
class LyricsOperations: 
    def __init__(self, bot):
        self.bot = bot

    async def lyrics_command(self, interactions):
        """Searches for lyrics of the song you want"""
        try:
            API = azapi.AZlyrics('google', accuracy=0.5)
            print(SongSession.current_song)
            API.title = SongSession.current_song
            print(API)
            API.getLyrics(save=True, ext='lrc')
            print(API.lyrics)
        except:
            await interactions.response.send_message('No lyrics found.')