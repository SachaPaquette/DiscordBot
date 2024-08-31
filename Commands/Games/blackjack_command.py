from Commands.Services.database import Database
from Commands.Services.utility import Utility
from ..UserProfile.user import User
import random
import time
from Config.logging import setup_logging
from Config.config import conf
import discord
from discord.ui import Button, View
# Create a logger for this file
logger = setup_logging("blackjack.py", conf.LOGS_PATH)

class BlackJack():
    def __init__(self):
        self.database = Database.getInstance()
        self.utility = Utility()
        self.deck = []
        self.dealer_hand = []
        self.player_hand = []
        self.dealer_score = 0
        self.player_score = 0
        self.bet = 0
        self.user = None
        self.interactions = None
        self.message = None
        
    def create_deck(self):
        suits = ['♠', '♣', '♦', '♥']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        for suit in suits:
            for value in values:
                self.deck.append(value + suit)
        random.shuffle(self.deck)
        
    def deal_cards(self):
        # Deal two cards to the player and dealer
        # Loop twice to deal two cards
        for _ in range(2):
            self.player_hand.append(self.deck.pop())
            self.dealer_hand.append(self.deck.pop())
        
        
    def calculate_score(self, hand):
        score = 0
        aces = 0
        for card in hand:
            value = card[:-1]
            if value in ['J', 'Q', 'K']:
                score += 10
            elif value == 'A':
                aces += 1
            else:
                score += int(value)
        for i in range(aces):
            if score + 11 <= 21:
                score += 11
            else:
                score += 1
        return score
    
    async def send_or_edit_message(self, interactions, message):
        if self.message:
            await self.message.edit(content=message)
        else:
            await interactions.response.send_message(message)
            self.message = await interactions.original_response()
        
    
    async def blackjack_command(self, interactions, bet: float):
        try: 
            
            # Check if the bet is positive
            if bet <= 0:
                await self.send_or_edit_message(interactions, f'{interactions.user.mention}, you must bet a positive amount.')
                return
            
            # Check if the user has enough money
            user = self.database.get_user(interactions)
            if self.utility.has_sufficient_balance(user, bet) == False:
                await self.send_or_edit_message(interactions,f'{interactions.user.mention}, you don\'t have enough money to bet that amount.')
                return
            
            # Create the deck
            self.create_deck()
            
            # Deal the cards
            self.deal_cards()
            
            # Set the bet, user, and interactions
            self.bet = bet
            self.user = user
            self.interactions = interactions
            
            # Calculate the score of the player and dealer
            self.player_score = self.calculate_score(self.player_hand)
            self.dealer_score = self.calculate_score(self.dealer_hand)
            
            # Remove the bet from the user's balance
            user["balance"] -= bet
            
            # Update the user's balance
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"], bet)
            
            # Check if the player has blackjack
            if self.player_score == 21:
                await self.blackjack_win()
                return
            
            # Send the initial message
            await self.send_or_edit_message(interactions,f'{interactions.user.mention} has bet {bet} dollars. Your hand is {self.player_hand[0]} and {self.player_hand[1]} and is worth {self.calculate_score(self.player_hand)}. The dealer\'s hand is {self.dealer_hand[0]} and a hidden card.')
            
            # If this is the first time the message is sent, save the message
            if self.message is None:
                self.message = await interactions.original_response()
            
            # Add the buttons
            await self.add_buttons(interactions, self.message)
            
            

        except Exception as e:
            print(f"Error in the blackjack function in blackjack.py: {e}")
            return
    async def hold(self, interactions):
        try:
            if interactions.user.id != self.interactions.user.id:
                return
            # Acknowledge the interaction
            await interactions.response.defer()
            while self.dealer_score < 17:
                self.dealer_hand.append(self.deck.pop())
                self.dealer_score = self.calculate_score(self.dealer_hand)
                if self.dealer_score > 21:
                    await self.blackjack_win()
                    return
            if self.player_score > self.dealer_score:
                await self.blackjack_win()
            elif self.player_score == self.dealer_score:
                await self.blackjack_tie()
            else:
                await self.blackjack_lose()
            
            return
        except Exception as e:
            print(f"Error in the hold function in blackjack.py: {e}")
            return
        
    async def hit(self, interactions):
        try:
            if interactions.user.id != self.interactions.user.id:
                return
            # Acknowledge the interaction
            await interactions.response.defer()
            self.player_hand.append(self.deck.pop())
            self.player_score = self.calculate_score(self.player_hand)
            if self.player_score > 21:
                await self.blackjack_lose()
            elif self.player_score == 21:
                await self.hold(interactions)
            else:
                players_hand = ""
                for card in self.player_hand:
                    players_hand += card + " "
                    
                await self.send_or_edit_message(self.interactions, f'Your hand is {players_hand} and is worth {self.calculate_score(self.player_hand)}. The dealer\'s hand is {self.dealer_hand[0]} and a hidden card.')
            
            return
        
        except Exception as e:
            print(f"Error in the hit function in blackjack.py: {e}")
            return
    async def blackjack_win(self):
        self.user["balance"] += self.bet * 2
        self.database.update_user_balance(self.interactions.guild.id, self.interactions.user.id, self.user["balance"], self.bet)
        await self.send_or_edit_message(self.interactions, f'The dealer had: {self.dealer_score}, {self.interactions.user.mention} won {self.bet * 2} dollars!')
        await self.remove_buttons()
    async def blackjack_lose(self):
        self.database.update_user_balance(self.interactions.guild.id, self.interactions.user.id, self.user["balance"], self.bet)
        await self.send_or_edit_message(self.interactions, f'The dealer had: {self.dealer_score}, {self.interactions.user.mention} lost {self.bet} dollars!')
        await self.remove_buttons()
        
    async def blackjack_tie(self):
        self.user["balance"] += self.bet
        self.database.update_user_balance(self.interactions.guild.id, self.interactions.user.id, self.user["balance"], self.bet)
        await self.send_or_edit_message(self.interactions, f'{self.interactions.user.mention} tied with the dealer!')
        await self.remove_buttons()
    async def add_buttons(self, interactions, message):
        hit_button = Button(style=discord.ButtonStyle.green, label="Hit", custom_id="hit")
        hold_button = Button(style=discord.ButtonStyle.red, label="Hold", custom_id="hold")
        
        async def hit_callback(interactions):
            await self.hit(interactions)
        
        async def hold_callback(interactions):
            await self.hold(interactions)

        hit_button.callback = hit_callback
        hold_button.callback = hold_callback
 
        # Add buttons to the message
        view = View(timeout=None)
        view.add_item(hit_button)
        view.add_item(hold_button)
        await message.edit(view=view)
        
    async def remove_buttons(self):
        replay_button = Button(style=discord.ButtonStyle.green, label="Replay", custom_id="replay")
        async def replay_callback(interactions):
            await self.replay(interactions)
            
        replay_button.callback = replay_callback
        view = View(timeout=None)
        view.add_item(replay_button)
        await self.message.edit(view=view)
        
    async def replay(self, interactions):
        # Check if the user is the same
        if interactions.user.id != self.interactions.user.id:
            return
        
        # Acknowledge the interaction
        await interactions.response.defer()
        # Reset the game
        self.deck = []
        self.dealer_hand = []
        self.player_hand = []
        self.dealer_score = 0
        self.player_score = 0
    
        
        await self.blackjack_command(interactions, self.bet)