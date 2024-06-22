
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
            print(stock_info)
            
            # Check if the user has enough money to buy the stock
            user = self.database.get_user(interactions.guild.id, interactions.user.id)
            if user["balance"] < stock_info["currentPrice"] * quantity:
                await interactions.response.send_message("You don't have enough money to buy that stock.")
                return
            
            await interactions.response.send_message(interactions.user.mention + f", processing your request to {option.value} {quantity} shares of {stock}.")
            message = await interactions.original_response()
            
            if option == Options.BUY:
                
                print("buying")
                print(stock, quantity, user)
                await self.buy_stock(interactions, stock_info, quantity, user)
            elif option == Options.SELL:
                self.sell_stock(interactions, stock_info, quantity, user)
            
            await message.edit(content=f'{interactions.user.mention}, you have successfully {option.value}ed {quantity} shares of {stock}.')
            
        except Exception as e:
            logger.error(f"Error in the stocks function in stocks.py: {e}")
            return
        
    async def buy_stock(self, interactions, stock_info, quantity, user):
        
        # Add the stock to the user's portfolio
        await self.database.add_stocks(interactions.guild.id, interactions.user.id, stock_info, quantity)
        await interactions.response.send_message(f'{interactions.user.mention}, you have successfully bought {quantity} shares of {stock_info["symbol"]}.')
    
    async def sell_stock(self, interactions, stock_info, quantity, user):
        # Sell the stock from the user's portfolio
        await self.database.sell_stocks(interactions.guild.id, interactions.user.id, stock_info, quantity)
        await interactions.response.send_message(f'{interactions.user.mention}, you have successfully sold {quantity} shares of {stock_info["symbol"]}.')