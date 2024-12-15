from .requester import Requester
from .requests_utility import filter, soup_find_all_element, normalGet, googleGet, parseLyric
import os, time
class FetchLyrics(Requester):    
    def __init__(self, search_engine='', accuracy=0.5, proxies={}):
        self.search_engine = search_engine
        self.accuracy = accuracy
        self.proxies = proxies
        self.lyrics = ''
        self.artist = ''
        self.title = ''
        
    def parseLyric(page):
        divs = [i.text for i in soup_find_all_element(page)('div', {'class': None})]
        return max(divs, key=len)

    def getLyrics(self, url=None, ext='txt', save=False, path='', sleep=3):
        """
        Retrieve Lyrics for a given song details.
        
        Parameters: 
            url (str): URL of the song's Azlyrics page. 
            ext (str): Extension of the lyrics saved file, default is ".txt".
            save (bool): Allow to save lyrics in a file.
            path (str): Path to save the lyrics file.
            sleep (float): Cooldown before next request.  
        
        Returns:
            lyrics (str): Lyrics of the detected song.
        """
        try:
            time.sleep(sleep)
            link = self.get_lyrics_link(url)
            if not link:
                return None
            
            page = self.get(link, self.proxies)
            if page.status_code != 200:
                if not self.search_engine:
                    print('Failed to find lyrics. Trying to get link from Google')
                    self.search_engine = 'google'
                    lyrics = self.getLyrics(url=url, ext=ext, save=save, path=path, sleep=sleep)
                    self.search_engine = ''
                    return lyrics
                else:
                    print('Error', page.status_code)
                    return None

            self.extract_metadata(page)
            lyrics = parseLyric(page)
            self.lyrics = lyrics.strip()
            return self.lyrics
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_lyrics_link(self, url):
        if url:
            return url
        elif not self.artist or not self.title:
            raise ValueError("Both artist and title can't be empty!")
        elif self.search_engine:
            return self.google_get(self.artist, self.title)
        else:
            return self.normal_get(self.artist, self.title)

    def google_get(self, artist, title):
        # Replace this with the actual implementation
        return googleGet(self.search_engine, self.accuracy, self.get, artist, title, 0, self.proxies)

    def normal_get(self, artist, title):
        # Replace this with the actual implementation
        return normalGet(artist, title, 0)

    def extract_metadata(self, page):
        metadata = [elm.text for elm in soup_find_all_element(page)('b')]
        if not metadata:
            print('Error', 'no metadata')
            raise ValueError("Invalid page, no metadata found")
        self.artist = filter(metadata[0][:-7], True)
        self.title = filter(metadata[1][1:-1], True)
