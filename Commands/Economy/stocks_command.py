
import yfinance as yf
import discord
from Config.logging import setup_logging
from Commands.Services.database import Database
from Config.config import conf
# Create a logger for this file
logger = setup_logging("stocks.py", conf.LOGS_PATH)
from enum import Enum
class Options(Enum):
    BUY = "buy"
    SELL = "sell"

class Stocks():
    def __init__(self):
        self.database = Database.getInstance()
        
    async def stocks_command(self, interactions, option: Options, stock: str, quantity: float):
        try:
            # Check if the stock is in the list of stocks
            if not self.is_stock_valid(stock):
                await interactions.response.send_message(
                    f'{interactions.user.mention}, that stock is not in the list of stocks.'
                )
                return
            
            # Fetch stock information
            stock_info = self.get_stock_info(stock)
            
            # Check if the user has enough money to buy the stock
            user = self.database.get_user(interactions)
            
            # Send initial processing message
            message = await interactions.response.send_message(
                f"{interactions.user.mention}, processing your request to {option.value} {quantity} shares of {stock}."
            )
            message = await interactions.original_response()
            
            # Execute the buy or sell command
            if option == Options.BUY:
                await self.handle_buy(interactions, stock_info, quantity, user, message)
            elif option == Options.SELL:
                await self.handle_sell(interactions, stock_info, quantity, user, message)
        except Exception as e:
            logger.error(f"Error in the stocks_command function: {e}")

    def is_stock_valid(self, stock: str) -> bool:
        """
        Check if the stock is in the list of valid stocks.
        """
        return stock in self.finance.return_stock()

    def get_stock_info(self, stock: str) -> dict:
        """
        Retrieve stock information using yfinance.
        """
        return yf.Ticker(stock).info

    async def handle_buy(self, interactions, stock_info: dict, quantity: float, user: dict, message):
        """
        Handle buying stocks.
        """
        # Implement buy stock logic here
        await self.buy_stock(interactions, stock_info, quantity, user, message)

    async def handle_sell(self, interactions, stock_info: dict, quantity: float, user: dict, message):
        """
        Handle selling stocks.
        """
        # Implement sell stock logic here
        await self.sell_stock(interactions, stock_info, quantity, user, message)
            
            
    def get_stock_price(self, stock_info):
        """
        Get the current price of the stock, falling back to regularMarketPreviousClose if necessary.
        """
        return stock_info.get("currentPrice", stock_info.get("regularMarketPreviousClose"))

    def has_sufficient_balance(self, user, stock_price, quantity):
        """
        Check if the user has sufficient balance to buy the specified quantity of stock.
        """
        return user["balance"] >= stock_price * quantity

            
    async def buy_stock(self, interactions, stock_info, quantity, user, message):
        try:
            # Check for currentPrice or use regularMarketPreviousClose as a fallback
            stock_price = self.get_stock_price(stock_info)
            
            if not stock_price:
                await message.edit(content=f"{interactions.user.mention}, the stock price information is unavailable.")
                return

            if not self.has_sufficient_balance(user, stock_price, quantity):
                await message.edit(content=f"{interactions.user.mention}, you don't have enough money to buy that stock.")
                return
            
            # Add the stock to the user's portfolio
            self.database.add_stocks(interactions.guild.id, interactions.user.id, stock_info, quantity, stock_price)
            
            await message.edit(content=f"{interactions.user.mention}, you have bought {quantity} shares of {stock_info['symbol']} for ${(stock_price * quantity):.2f}.")
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
            await message.edit(content=f"{interactions.user.mention}, you have sold {quantity} shares of {stock_info['symbol']} for ${(stock_info['currentPrice'] * quantity):.2f}.")
            
            return
        except Exception as e:
            await message.edit(content=f"{interactions.user.mention}, there was an error processing your request.")
            logger.error(f"Error in the sell_stock function in stocks.py: {e}")
            return