import yfinance as yf
import discord
from Config.logging import setup_logging
from Commands.database import Database
from Config.config import conf
# Create a logger for this file
logger = setup_logging("stocks.py", conf.LOGS_PATH)
from enum import Enum
from Commands.finances import Finance
class Portfolio():
    def __init__(self):
        self.database = Database.getInstance()
        self.finance = Finance()
        
    async def portfolio_command(self, interactions):
        try:
            user = self.database.get_user(interactions.guild.id, interactions.user.id)
            
            # Get the stocks that the user owns and the quantity of each stock
            stocks = user.get("stocks", {})
            if len(stocks) == 0:
                await interactions.response.send_message(f"{interactions.user.mention}, you do not own any stocks.")
                return
            
            embed = discord.Embed(title=f"{interactions.user.display_name}'s Portfolio", color=discord.Color.blue())
            
            for stock_symbol, stock in stocks.items():
                # Get the stock data
                stock_data = yf.Ticker(stock["symbol"])
                stock_info = stock_data.info

                # Determine the current price of the stock
                current_price = stock_info.get("currentPrice") or stock_info.get("regularMarketPreviousClose")
                
                # If the current price is not available, send a message to the user
                if current_price is None:
                    await interactions.response.send_message(f"{interactions.user.mention}, price information for {stock['symbol']} is unavailable.")
                    return

                # Calculate the change in price (in percentage) since the stock was bought
                change = (((current_price * stock["amount"])  - stock["total_price"]) / stock["total_price"]) * 100
                # Add field for each stock in the embed
                embed.add_field(
                    name=f"{stock_info['symbol']}",
                    value=(
                        f"Shares: {stock['amount']}\n"
                        f"Current Price: ${current_price:.2f}\n"
                        f"Total Value: ${(current_price * stock["amount"]):.2f}\n"
                        f"Change: {change:.2f}%"
                    ),
                    inline=False
                )
            # Send the embed to the user
            await interactions.response.send_message(embed=embed)
        except Exception as e:
            await interactions.response.send_message(f"{interactions.user.mention}, there was an error processing your request.")
            logger.error(f"Error in the portfolio_command function: {e}")
            return