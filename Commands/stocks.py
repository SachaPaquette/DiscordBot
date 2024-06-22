
import yfinance as yf
import discord
from Config.logging import setup_logging
from Commands.database import Database
from Config.config import conf
# Create a logger for this file
logger = setup_logging("stocks.py", conf.LOGS_PATH)
from enum import Enum
from Commands.finances import Finance
class Options(Enum):
    BUY = "buy"
    SELL = "sell"

class Stocks():
    def __init__(self):
        self.database = Database.getInstance()
        self.finance = Finance()
        
    async def stocks_command(self, interactions, option: Options, stock: str, quantity: float):
        try:
            # Check if the stock is in the list of stocks
            if stock not in self.finance.return_stock():
                await interactions.response.send_message(f'{interactions.user.mention}, that stock is not in the list of stocks.')
                return
            
            
            stock_data = yf.Ticker(stock)
            stock_info = stock_data.info
            
            # Check if the user has enough money to buy the stock
            user = self.database.get_user(interactions.guild.id, interactions.user.id)
            
            
            message = await interactions.response.send_message(interactions.user.mention + f", processing your request to {option.value} {quantity} shares of {stock}.")
            message = await interactions.original_response()
            
            if option == Options.BUY:
                await self.buy_stock(interactions, stock_info, quantity, user, message)
            elif option == Options.SELL:
                await self.sell_stock(interactions, stock_info, quantity, user, message)
            
            
        except Exception as e:
            logger.error(f"Error in the stocks function in stocks.py: {e}")
            return
        
    async def buy_stock(self, interactions, stock_info, quantity, user, message):
        try:
            # Check for currentPrice or use regularMarketPreviousClose as a fallback
            stock_price = stock_info.get("currentPrice", stock_info.get("regularMarketPreviousClose"))
            
            if not stock_price:
                await message.edit(content=f"{interactions.user.mention}, the stock price information is unavailable.")
                return

            if user["balance"] < stock_price * quantity:
                await message.edit(content=f"{interactions.user.mention}, you don't have enough money to buy that stock.")
                return
            
            # Add the stock to the user's portfolio
            self.database.add_stocks(interactions.guild.id, interactions.user.id, stock_info, quantity, stock_price)
            
            await message.edit(content=f"{interactions.user.mention}, you have bought {quantity} shares of {stock_info['symbol']} for ${stock_price * quantity}.")
            return
        except Exception as e:
            await message.edit(content=f"{interactions.user.mention}, there was an error processing your request.")
            logger.error(f"Error in the buy_stock function in stocks.py: {e}")
            return
    async def sell_stock(self, interactions, stock_info, quantity, user, message):
        try:
            # Check if the user has enough stocks to sell
            if user["stocks"][stock_info["symbol"]]["amount"] < quantity:
                await message.edit(content=f"{interactions.user.mention}, you don't have enough stocks to sell.")
                return
            
            # Sell the stock from the user's portfolio
            self.database.sell_stocks(interactions.guild.id, interactions.user.id, stock_info, quantity)
            await message.edit(content=f"{interactions.user.mention}, you have sold {quantity} shares of {stock_info['symbol']} for ${stock_info['currentPrice'] * quantity}.")
            
            return
        except Exception as e:
            await message.edit(content=f"{interactions.user.mention}, there was an error processing your request.")
            logger.error(f"Error in the sell_stock function in stocks.py: {e}")
            return