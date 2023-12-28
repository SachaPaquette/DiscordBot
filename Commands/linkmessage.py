import re
import aiohttp
import whois
import tldextract
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

            # Get the domain information
            domain_info = self.get_domain_info(url)
            
            formatted_domain_info = self.format_domain_info_message(domain_info)
            # Return the domain information                   
            return formatted_domain_info
        
    def extract_domain_from_url(self, url):
        # Extract the domain from the URL using tldextract
        ext = tldextract.extract(url)
        # Return the domain name and suffix (e.g. google.com)
        return f"{ext.domain}.{ext.suffix}"
                        
    def get_domain_info(self, url):
        try:
            # Extract the domain from the URL
            domain = self.extract_domain_from_url(url)

            # Get WHOIS information for the domain
            domain_info = whois.whois(domain)

            # Extract the information from the WHOIS response

            # Get the country of origin
            origin = domain_info.get('country', None)
            # Get the creation date 
            creation_date = domain_info.get('creation_date', None)
            # Format the creation date to a string (e.g. 2020-01-01 00:00:00)
            creation_date_formatted = creation_date[0].strftime("%Y-%m-%d %H:%M:%S")
            # Get the name servers
            name_servers = domain_info.get('name_servers', None)
            # Get the domain name
            domain_name = domain_info.get('domain_name', None)
            # Get the organization
            organization = domain_info.get('org', None)

            # Return the information as a dictionary
            return {
                'ORIGIN': origin,
                'CREATION_DATE': creation_date_formatted,
                'NAME_SERV': name_servers,
                'NAME_DOMAIN': domain_name,
                'ORGANIZATION': organization
            }
        except Exception as e:
            print(f"Error while getting domain information: {e}")
            return None
                
    
    def format_domain_info_message(self, domain_info):
        try:
            return (
                f"**Origin:** {domain_info['ORIGIN']}\n"
                f"**Creation Date:** {domain_info['CREATION_DATE']}\n"
                f"**Name Servers:** {', '.join(domain_info['NAME_SERV'])}\n"
                f"**Name Domain:** {', '.join(domain_info['NAME_DOMAIN'])}\n"
                f"**Organization:** {domain_info['ORGANIZATION']}"
                )
            
        except Exception as e:
            print(f"Error while formatting domain info message: {e}")
            return None