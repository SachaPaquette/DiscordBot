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

        # Calculate initial score
        for card in hand:
            value = card[:-1]
            if value in ['J', 'Q', 'K']:
                score += 10
            elif value == 'A':
                aces += 1
            else:
                score += int(value)

        # Adjust score for aces
        while aces:
            if score + 11 <= 21:
                score += 11
            else:
                score += 1
            aces -= 1

        return score
    
    async def send_or_edit_message(self, interactions, message):
        if self.message:
            await self.message.edit(content=message)
        else:
            await interactions.response.send_message(message)
            self.message = await interactions.original_response()
        
        
    def initialize_game(self, bet, user, interactions):
            self.create_deck()
            self.deal_cards()
            
            # Set the bet, user, and interactions
            self.bet = bet
            self.user = user
            self.interactions = interactions

            self.player_score = self.calculate_score(self.player_hand)
            self.dealer_score = self.calculate_score(self.dealer_hand)
            
    async def check_blackjack(self):
        if self.player_score == 21:
            await self.blackjack_win()
            return
        if self.dealer_score == 21:
            await self.blackjack_lose()
            return
        return
    
    def validate_bet(self, bet):
        try:
            if bet <= 0:
                return False
            return True
        except Exception as e:
            print(f"Error in the validate_bet function in blackjack.py: {e}")
            return False
            
    async def check_user_balance(self, user, bet):
        if not self.utility.has_sufficient_balance(user, bet):
            await self.send_or_edit_message(self.interactions, f'{self.interactions.user.mention}, you don\'t have enough money to bet that amount.')
            return False
        return True
    
    async def blackjack_command(self, interactions, bet: float):
        try: 
            
            # Check if the bet is positive
            if self.validate_bet(bet) == False:
                await self.send_or_edit_message(interactions, f'{interactions.user.mention}, you must bet a positive amount.')
                return
            
            # Check if the user has enough money
            user = self.database.get_user(interactions)
            if not await self.check_user_balance(user, bet):
                return
            
            # Initialize the game
            self.initialize_game(bet, user, interactions)
            
            # Update the user's balance
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"] - bet, bet)
            
            # Check if the player has blackjack
            await self.check_blackjack()
            
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
            # Check if the interaction is from the same user
            if not self.check_user(interactions):
                return
            
            await interactions.response.defer()

            # Dealer's turn
            dealer_busted = self.dealer_turn()

            # Determine the outcome
            if dealer_busted:
                await self.blackjack_win()
            else:
                await self.blackjack_results()

        except Exception as e:
            print(f"Error in the hold function in blackjack.py: {e}")
            return

    def dealer_turn(self):
        while self.dealer_score < 17:
            self.dealer_hand, self.dealer_score = self.calculate_hit(self.dealer_hand, self.dealer_score)
            if self.dealer_score > 21:
                return True
        return False

    async def hit(self, interactions):
        try:
            # Check if the interaction is from the same user
            if interactions.user.id != self.interactions.user.id:
                return

            # Acknowledge the interaction
            await interactions.response.defer()

            # Player hits
            self.player_hand, self.player_score = self.calculate_hit(self.player_hand, self.player_score)

            # Check if player has busted or got blackjack
            if self.player_score > 21:
                await self.blackjack_results()
            elif self.player_score == 21:
                await self.blackjack_results()
            else:
                # Update player's hand
                await self.send_player_hand_update()

        except Exception as e:
            print(f"Error in the hit function in blackjack.py: {e}")
            return
        
    def calculate_hit(self, hand, score):
        hand.append(self.deck.pop())
        score = self.calculate_score(hand)
        return hand, score
    
    async def player_hit(self):
        self.player_hand.append(self.deck.pop())
        self.player_score = self.calculate_score(self.player_hand)

    async def send_player_hand_update(self):
        players_hand = " ".join(self.player_hand)
        await self.send_or_edit_message(self.interactions, f'Your hand is {players_hand} and is worth {self.player_score}. The dealer\'s hand is {self.dealer_hand[0]} and a hidden card.')
    
    async def blackjack_results(self):

        # Check player status
        if self.player_score > 21:
            await self.blackjack_lose()
        elif self.player_score == 21:
            await self.hold(self.interactions)
        else:
            # Dealer's turn
            self.dealer_turn()

            # Determine result
            if self.dealer_score > 21:
                await self.blackjack_win()
            elif self.player_score > self.dealer_score:
                await self.blackjack_win()
            elif self.player_score == self.dealer_score:
                await self.blackjack_tie()
            else:
                await self.blackjack_lose()

        # Remove buttons after game result
        await self.remove_buttons()

    async def blackjack_win(self):
        self.user["balance"] += self.bet * 2
        await self.send_or_edit_message(self.interactions, f'You had: {self.player_score}. The dealer had: {self.dealer_score}, {self.interactions.user.mention} won {self.bet * 2} dollars!')
        return  
    
    async def blackjack_lose(self):
        await self.send_or_edit_message(self.interactions, f'You had: {self.player_score}. The dealer had: {self.dealer_score}, {self.interactions.user.mention} lost {self.bet} dollars!')
        return
    
    async def blackjack_tie(self):
        self.user["balance"] += self.bet
        await self.send_or_edit_message(self.interactions, f'{self.interactions.user.mention} tied with the dealer!')
        return
        
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
        if not self.check_user(interactions):
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
        
    def check_user(self, interactions):
        if interactions.user.id != self.interactions.user.id:
            return False
        return True