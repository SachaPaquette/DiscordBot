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


    
class Finance():
    def __init__(self):
        self.database = Database.getInstance()
        
    async def finance_command(self, interactions, stock: str, quantity: int):
        try:
            # Check if the stock is in the list of stocks
            if stock not in STOCKS:
                await interactions.response.send_message(f'{interactions.user.mention}, that stock is not in the list of stocks.')
                return
            
            
            stock_data = yf.Ticker(stock)
            stock_info = stock_data.info
            
            
        except Exception as e:
            logger.error(f"Error in the finance function in finance.py: {e}")
            return
        
    def return_stock(self):
        return STOCKS