from math import floor
import bs4, re, time, os
from urllib.parse import quote
from Config import config


def soup_find_element(page):
    # v3.0
    # Changed page.text -> page.content.decode() to support variant unicodes
    soup = bs4.BeautifulSoup(
                        page.content.decode(),
                        "html.parser"
                        )
    return soup.find

def soup_find_all_element(page):
    # v3.0
    # Changed page.text -> page.content.decode() to support variant unicodes
    soup = bs4.BeautifulSoup(
                        page.content.decode(),
                        "html.parser"
                        )
    return soup.findAll


def filter(inpt, isFile=False):
    if isFile:
        return ''.join(i for i in inpt if i not in r'<>:"/\|?*')
    return ''.join(i.lower() for i in inpt if i.lower() in config.conf.letters)

def normalGet(artist='', title='', _type=0):
    art, tit = filter(artist), filter(title)
    if _type:
        print('https://www.azlyrics.com/{}/{}.html'.format(art[0], art))
        return 'https://www.azlyrics.com/{}/{}.html'.format(art[0], art)
    return 'https://www.azlyrics.com/lyrics/{}/{}.html'.format(art, tit)

def parseLyric(page):
    divs = [i.text for i in soup_find_all_element(page)('div', {'class': None})]
    return max(divs, key=len)

def googleGet(search_engine, acc, get_func, artist='', title='', _type=0, proxies={}):
        # Encode artist and title to avoid url encoding errors
        data = artist + ' ' * (title != '' and artist != '') + title
        encoded_data = quote(data.replace(' ', '+'))

        # Perform a search (for accuracy) [Custom search engine]
        search_engines = {
            'google': 'https://www.google.com/search?q=',
            'duckduckgo': 'https://duckduckgo.com/html/?q='
        }

        selected_search_engine = 'google'
        if search_engine in search_engines:
            selected_search_engine = search_engine

        google_page = get_func('{}{}+site%3Aazlyrics.com'.format(
                                        search_engines[selected_search_engine],
                                        encoded_data
                                        ),
                                proxies
                                )
        
        # Choose between lyrics or song according to function used
        regex = [
            r'(azlyrics\.com\/lyrics\/(\w+)\/(\w+).html)',
            r'(azlyrics\.com\/[a-z0-9]+\/(\w+).html)'
        ]
        
        # ex result: [('azlyrics.com/t/taylorswift.html', 'taylorswift')]
        # result[0][0] = 'azlyrics.com/t/taylorswift.html'
        results = re.findall(
                            regex[_type],
                            google_page.text
                            )

        if len(results):
            # calculate jaro similarity for artist and title
            jaro_artist = 1.0
            jaro_title = 1.0
            
            if artist:
                jaro_artist = jaro_distance(
                                            artist.replace(' ', ''),
                                            results[0][1]
                                            )
            if title:
                jaro_title = jaro_distance(
                                            title.replace(' ', ''),
                                            results[0][2]
                                            )
            
            if jaro_artist >= acc and jaro_title >= acc:
                return 'https://www.' + results[0][0]
            else:
                print('Similarity <', acc)
        else:
            print(search_engine.title(), 'found nothing!')
        
        return 0
    
    
    

  
def jaro_distance(s1, s2): 
    if (s1 == s2): 
        return 1.0
  
    len1, len2 = len(s1), len(s2)
    max_dist = floor(max(len1, len2) / 2) - 1
    match = 0
    hash_s1, hash_s2 = [0] * len(s1), [0] * len(s2)
  
    for i in range(len1):
        for j in range(max(0, i - max_dist),  
                       min(len2, i + max_dist + 1)):
            if (s1[i] == s2[j] and hash_s2[j] == 0):
                hash_s1[i], hash_s2[j] = 1, 1
                match += 1
                break

    if (match == 0): 
        return 0.0

    t = 0
    point = 0
  
    for i in range(len1): 
        if (hash_s1[i]): 
            while (hash_s2[point] == 0): 
                point += 1
  
            if (s1[i] != s2[point]): 
                point += 1
                t += 1
    t = t//2

    return (match/ len1 + match / len2 + 
            (match - t + 1) / match)/ 3.0