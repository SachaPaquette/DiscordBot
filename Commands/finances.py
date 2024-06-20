# Command to get the live price of a stock

import yfinance as yf
import discord
from Config.logging import setup_logging
from Commands.database import Database
from Config.config import conf
# Create a logger for this file
logger = setup_logging("finance.py", conf.LOGS_PATH)
from enum import Enum
with open("Commands/Finances/tickers.txt") as f:
    STOCKS = f.read().splitlines()

class Stock(Enum):

    AAPL = "AAPL"
    MSFT = "MSFT"
    AMZN = "AMZN"
    GOOGL = "GOOGL"
    FB = "FB"
    TSLA = "TSLA"
    BRK_B = "BRK.B"
    JPM = "JPM"
    JNJ = "JNJ"
    V = "V"
    PG = "PG"
    UNH = "UNH"
    MA = "MA"
    A= "A"

    
class Finance():
    def __init__(self):
        self.database = Database.getInstance()
        
    async def finance_command(self, interactions, stock: Stock):
        try:
            stock_data = yf.Ticker(stock.value)
            stock_info = stock_data.info
            print(stock_info)
            
        except Exception as e:
            logger.error(f"Error in the finance function in finance.py: {e}")
            return