from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
from .config import DriverConfig
from selenium.common.exceptions import WebDriverException
import sys


def check_chrome_installed():
    """
    Function to check if Google Chrome is installed on the user's system.
    """
    try:
        # Try to install ChromeDriver 
        ChromeDriverManager().install()
    except WebDriverException:
        # Chrome is not installed on the system
        print("Chrome is not installed on your system. Please install it and try again.")
        sys.exit()

def configure_browser_options(options, user_agents, crx_path):
    """
    Configures the browser options for automated testing.

    Args:
        options (Options): The browser options object.
        user_agents (list): List of user agents to choose from.
        crx_path (str): The path to the extension file.

    Returns:
        None
    """
    # Disable logging (1: INFO, 2: WARNING, 3: ERROR)
    options.add_argument("--log-level=3")
    # Disable the "DevTools listening on ws://
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # Disable the "Chrome is being controlled by automated test software" notification
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # Turn-off userAutomationExtension 
    options.add_experimental_option("useAutomationExtension", False)
    # Set a random user agent (pretend to be a real browser)
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    # Add the extension to the driver (for ad blocking)
    options.add_extension(crx_path)
    # Adding argument to disable the AutomationControlled flag
    options.add_argument("--disable-blink-features=AutomationControlled")

def driver_setup():
    """
    Set up and configure the web driver for automated browser testing.

    Returns:
        WebDriver: The configured web driver instance.
    Raises:
        Exception: If an error occurs during the driver setup process.
    """
    try:
        # Set up the driver options
        options = Options()
        # Keep the browser open after the script finishes executing (for debugging)
        #options.add_experimental_option('detach', True)
        # Run in headless mode (without opening a browser window)
        #options.add_argument('--headless')
        # Disable logging and configure other options
        configure_browser_options(options, DriverConfig.USER_AGENTS, DriverConfig.CRX_PATH)
        # ChromeDriverManager will install the latest version of ChromeDriver
        driver = webdriver.Chrome(service=Service(
            check_chrome_installed()), options=options)
        # Changing the property of the navigator value for webdriver to undefined
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        # put the browser in focus
        #driver.switch_to.window(driver.current_window_handle)
        # Return the driver instance
        return driver
    except Exception as e:
        # Raise the exception
        raise e


"""def driver_setup():
    #options = Options()
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3")
    #options.add_argument("--headless")
    options.headless = False
    options.add_argument(f"user-agent={random.choice(Config.USER_AGENTS)}")
    options.add_extension(Config.CRX_PATH)
    options.add_argument(f'--load-extension={Config.EXTENSION_PATH}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--no-sandbox=False')
    options.set_capability("detach", True) # Keep the browser open after the script finishes executing (for debugging)
    # add proxy to the driver
    #options.add_argument(f"--proxy-server={Config.PROXY_LIST}")
    
    driver = uc.Chrome(options=options)
    
    return driver"""