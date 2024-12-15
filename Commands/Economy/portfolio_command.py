from enum import Enum
import yfinance as yf
import discord
from Config.logging import setup_logging
from Commands.Services.database import Database
from Config.config import conf
# Create a logger for this file
logger = setup_logging("stocks.py", conf.LOGS_PATH)


class Portfolio():
    def __init__(self):
        self.database = Database.getInstance()

    async def portfolio_command(self, interactions):
        try:
            user = self.database.get_user(interactions)
            stocks = user.get("stocks", {})

            if not stocks:
                await self.send_no_stocks_message(interactions)
                return

            embed = await self.create_portfolio_embed(interactions, stocks)
            await interactions.response.send_message(embed=embed)
        except Exception as e:
            await self.handle_error(interactions, e)

    async def send_no_stocks_message(self, interactions):
        await interactions.response.send_message(f"{interactions.user.mention}, you do not own any stocks.")

    async def create_portfolio_embed(self, interactions, stocks):
        embed = discord.Embed(
            title=f"{interactions.user.display_name}'s Portfolio",
            color=discord.Color.blue()
        )

        for stock_symbol, stock in stocks.items():
            stock_info, current_price = await self.fetch_stock_info(stock)
            if current_price is None:
                await self.send_price_unavailable_message(interactions, stock['symbol'])
                return

            change = self.calculate_change(current_price, stock)
            embed.add_field(
                name=f"{stock_info['symbol']}",
                value=(
                    f"Shares: {stock['amount']}\n"
                    f"Current Price: ${current_price:.2f}\n"
                    f"Total Value: ${(current_price * stock['amount']):.2f}\n"
                    f"Change: {change:.2f}%"
                ),
                inline=False
            )
        return embed

    async def fetch_stock_info(self, stock):
        stock_data = yf.Ticker(stock['symbol'])
        stock_info = stock_data.info
        current_price = stock_info.get(
            'currentPrice') or stock_info.get('regularMarketDayHigh')
        return stock_info, current_price

    async def send_price_unavailable_message(self, interactions, symbol):
        await interactions.response.send_message(f"{interactions.user.mention}, price information for {symbol} is unavailable.")

    def calculate_change(self, current_price, stock):
        return ((current_price * stock['amount']) - stock['total_price']) / stock['total_price'] * 100

    async def handle_error(self, interactions, error):
        await interactions.response.send_message(f"{interactions.user.mention}, there was an error processing your request.")
        logger.error(f"Error in the portfolio_command function: {error}")
