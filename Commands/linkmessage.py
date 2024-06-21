import re
import aiohttp
import whois
import tldextract
from Config.config import conf
from Config.logging import setup_logging
from Config.config import conf
# Create a logger for this file
logger = setup_logging("linkmessage.py", conf.LOGS_PATH)
class LinkMessage:
    def __init__(self, bot):
        self.bot = bot

    async def on_message_command(self, message):
        try:
            # Ignore message that is a command
            if message.content.startswith("/"):
                return
            
            # Check if the message contains a URL
            if re.search(conf.REGEX_URL_PATTERN, message.content):
                
                # Get the URL from the message
                url = re.search(conf.REGEX_URL_PATTERN, message.content).group(0)

                # Get the domain information
                domain_info = self.get_domain_info(url)
                # Format the domain information 
                formatted_domain_info = self.format_domain_info_message(domain_info)
                
                # Check if the domain information is None
                if formatted_domain_info is None:
                    return
                
                # Send the domain information
                await message.channel.send(formatted_domain_info)
        except Exception as e:
            logger.error(f"Error while handling message: {e}")
            return
        
    
    def extract_domain_from_url(self, url):
        """
        Extracts the domain name from a given URL. (e.g. https://www.google.com -> google.com)

        Args:
            url (str): The URL from which to extract the domain name.

        Returns:
            str: The domain name and suffix (e.g. google.com).
        """
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
            logger.error(f"Error while getting domain information: {e}")
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
            logger.error(f"Error while formatting domain info message: {e}")
            return None