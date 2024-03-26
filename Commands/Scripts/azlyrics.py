from .requester import Requester
from .requests_utility import filter, soup_find_all_element, normalGet, googleGet, parseLyric
import os, time
class FetchLyrics(Requester):    
    def __init__(self, search_engine='', accuracy=0.5, proxies={}):
        self.search_engine = search_engine
        self.accuracy = accuracy
        self.proxies = proxies
        self.lyrics = ''
        self.lyrics_history = []
        self.artist = ''
        self.title = ''
        
        
    

    # v3.0.5: Re-coded ParseLyrics to be more efficient
    def parseLyric(page):
        divs = [i.text for i in soup_find_all_element(page)('div', {'class': None})]
        return max(divs, key=len)
    
    
    
    def getLyrics(self, url=None, ext='txt', save=False, path='', sleep=3):
        """
        Retrieve Lyrics for a given song details.
        
        Parameters: 
            url (str): url of the song's Azlyrics page. 
            ext (str): extension of the lyrics saved file, default is ".txt".
            save (bool): allow to or not to save lyrics in a file.
            sleep (float): cooldown before next request.  
        
        Returns:
            lyrics (str): Lyrics of the detected song.
        """

        # Best cooldown is 5 sec
        time.sleep(sleep)

        link = url

        if not url:
            # v3.0.5: No need for artist and title if url is found
            if not self.artist + self.title:
                raise ValueError("Both artist and title can't be empty!")
            if self.search_engine:
                # If user can't remember the artist,
                # he can search by title only
                
                # Get AZlyrics url via Google Search
                link = googleGet(
                            self.search_engine,
                            self.accuracy,
                            self.get,
                            self.artist,
                            self.title,
                            0,
                            self.proxies
                        )
                if not link:
                    return 0
            else:
                # Sometimes search engines block you
                # If happened use the normal get method
                link = normalGet(
                            self.artist,
                            self.title,
                            0)

        page = self.get(link, self.proxies)
        if page.status_code != 200:
            if not self.search_engine:
                print('Failed to find lyrics. Trying to get link from Google')
                self.search_engine = 'google'
                lyrics = self.getLyrics(url=url, ext=ext, save=save, path=path, sleep=sleep)
                self.search_engine = ''
                return lyrics
            else:
                print('Error',page.status_code)
                return 1

        # Getting Basic metadata from azlyrics
        metadata = [elm.text for elm in soup_find_all_element(page)('b')]
        
        # if metadata is empty, then it's not a valid page
        if not metadata:
            print('Error', 'no metadata')
            return 1
        
        # v3.0.4: Update title and artist attributes with exact names
        self.artist = filter(metadata[0][:-7], True)
        self.title = filter(metadata[1][1:-1], True)

        lyrics = parseLyric(page)
        self.lyrics = lyrics.strip()

        # Saving Lyrics
        if lyrics:
            if save:
                # v3.0.2: Adding custom path
                p = os.path.join(
                                path,
                                '{} - {}.{}'.format(
                                                self.title.title(),
                                                self.artist.title(),
                                                ext
                                                )
                                )
                
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(lyrics.strip())
            
            # Store lyrics for later usage
            self.lyrics_history.append(self.lyrics)
            return self.lyrics

        self.lyrics = 'No lyrics found :('
        return 2