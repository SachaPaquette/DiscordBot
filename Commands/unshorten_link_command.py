from Config.logging import setup_logging
from Config.config import conf
logger = setup_logging("unshorten_link.py", conf.LOGS_PATH)
import requests 
import urllib.parse
class Unshorten_URL():
    def unshorten_url(self, url):
        try:
            if url is None:
                return None
            
            # Check if the URL is valid
            result = urllib.parse.urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL")
            
            # Use a user agent to identify the request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0"
            }
            response = requests.get(url, allow_redirects=True, timeout=10, headers=headers)
            
            # Check if the response was successful
            if response.status_code != 200:
                raise Exception(f"Failed to unshorten URL. Status code: {response.status_code}")
            
            # Check if the unshortened URL is different from the original
            unshortened_url = response.url
            if unshortened_url == url:
                return None
            
            return unshortened_url
        except requests.exceptions.RequestException as e:
            logger.error(f"ERROR - Request Exception while unshortening URL: {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error while unshortening URL: {e}")
            return None
    
    async def unshorten_link_command(self, interactions, url: str):
        try:
            # Unshorten the URL
            unshortened_url = self.unshorten_url(url)
            
            # Check if the unshortened URL is None
            if unshortened_url is None:
                await interactions.response.send_message("Failed to unshorten the URL.")
                return 
            
            # Reply to the interaction with the unshortened URL
            await interactions.response.send_message(f"Unshortened URL: {unshortened_url}")
        except Exception as e:
            logger.error(f"Error while unshortening link: {e}")
            return None
        
