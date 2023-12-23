import re
import aiohttp
import whois
class LinkMessage:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        # Ignore messages sent by the bot
        if message.author == self.bot.user:
            return
        
        # Ignore message that is a command
        if message.content.startswith("!"):
            return
        
        # Create a regex pattern to match a URL (https and http)
        pattern = r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,})"
        
        # Check if the message contains a URL
        if re.search(pattern, message.content):
            
            # Get the URL from the message
            url = re.search(pattern, message.content).group(0)
            print(url)
            # Get the domain information
            domain_info = self.get_domain_info(url)
            
                   
            return domain_info
                        
    def get_domain_info(self,url):
        try:
            # Get WHOIS information for the domain
            domain_info = whois.query(url)
            print(domain_info)
            # Extract the specific information you need
            ip_address = domain_info.get('ip', None)
            origin = domain_info.get('country', None)
            creation_date = domain_info.get('creation_date', None)
            name_servers = domain_info.get('name_servers', None)
            domain_name = domain_info.get('domain_name', None)
            
            
            return {
                'IP': ip_address,
                'ORIGIN': origin,
                'CREATION_DATE': creation_date,
                'NAME_SERV': name_servers,
                'NAME_DOMAIN': domain_name
            }
        except Exception as e:
            print(f"Error while getting domain information: {e}")
            return None
                
    
