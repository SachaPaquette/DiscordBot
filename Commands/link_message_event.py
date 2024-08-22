import datetime
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
            if not re.search(conf.REGEX_URL_PATTERN, message.content):
                return

            # Get the URL from the message
            url = re.search(conf.REGEX_URL_PATTERN, message.content).group(0)

            # Get the domain information
            domain_info = self.get_domain_info(url)

            # Check if the domain information is None
            if domain_info is None:
                return

            # Format the domain information
            formatted_domain_info = self.format_domain_info_message(
                domain_info)

            # Check if the domain information is None
            if formatted_domain_info is None:
                return

            # Reply to the message with the domain information
            await message.reply(formatted_domain_info)

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
        # Return the domain name and suffix (e.g. google.com)
        return f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}"

    def get_domain_info(self, url):
        try:
            # Get WHOIS information for the domain
            domain_info = whois.whois(self.extract_domain_from_url(url))
            return {
                'ORIGIN': domain_info.get('country', None),
                'CREATION_DATE': domain_info.get('creation_date', None),
                'NAME_SERV': domain_info.get('name_servers', None),
                'NAME_DOMAIN': domain_info.get('domain_name', None),
                'ORGANIZATION': domain_info.get('org', None)
            }
        except Exception as e:
            logger.error(f"Error while getting domain information: {e}")
            return None

    def format_domain_info_message(self, domain_info):
        try:
            def format_list_or_none(value):
                if isinstance(value, list):
                    return ', '.join([str(item) if isinstance(item, datetime.datetime) else item for item in value])
                return value if value else 'Not available'

            return (
                f"**Origin:** {domain_info['ORIGIN']}\n"
                f"**Creation Date:** {format_list_or_none(domain_info['CREATION_DATE'])}\n"
                f"**Name Servers:** {format_list_or_none(domain_info['NAME_SERV'])}\n"
                f"**Name Domain:** {format_list_or_none(domain_info['NAME_DOMAIN'])}\n"
                f"**Organization:** {domain_info['ORGANIZATION'] or 'Not available'}"
            )

        except Exception as e:
            logger.error(f"Error while formatting domain info message: {e}")
            return None
