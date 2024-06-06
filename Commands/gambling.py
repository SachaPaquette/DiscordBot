from Commands.database import Database
from Commands.utility import Utility
from .UserProfile.user import User
import random
import time


class Gambling():
    
    def __init__(self, server_id):
        self.database = Database.getInstance()
        self.collection = self.database.get_collection(server_id)
        self.users = {}
        
    def get_user_id(self, interaction):
        """
        Retrieves the user id from the interaction object.
        
        Parameters:
        - interaction: The interaction object.
        
        Returns:
        - user_id: The user id.
        """
        return interaction.user.id

    def get_slot_symbols(self):
        symbols = ['🍒', '🍋', '🍊', '🍉', '⭐', '🔔', '7️⃣']
        return random.choices(symbols, k=3)
    
    def calculate_payout(self, symbols, bet):
        if symbols[0] == symbols[1] == symbols[2]:
            if symbols[0] == '7️⃣':
                return bet * 10
            return bet * 5
        elif symbols[0] == symbols[1] or symbols[1] == symbols[2] or symbols[0] == symbols[2]:
            return bet * 2
        else:
            return -bet
        
    async def gamble(self, interactions, bet: int):
        if bet <= 0:
            await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
            return
        
        user_id = self.get_user_id(interactions)
        user = self.database.get_user(interactions.guild.id,user_id)
        
        if user["balance"] < bet:
            await interactions.response.send_message("You don't have enough money to bet that amount.")
            return

        symbols = self.get_slot_symbols()
        
        payout = self.calculate_payout(symbols, bet)
        user["balance"] += payout
        # Update the user's balance
        self.database.update_user_balance(interactions.guild.id,user_id, user["balance"])
        
        if payout > 0: 
            # Update the user's experience
            self.database.update_user_experience(interactions.guild.id,user_id, payout)
        # Send initial message
        result_message = await interactions.response.send_message(f'{interactions.user.mention} spun the slots!', ephemeral=False)
        
        # React to the message with slot symbols
        result_message = await interactions.original_response()

        # Edit the original message to include the result
        await result_message.edit(content=None, embed=Utility.create_gambling_embed_message(symbols, payout, user["balance"]))
       
    async def balance(self, interactions):
        user_id = self.get_user_id(interactions)
        user = self.database.get_user(interactions.guild.id,user_id)
        
        
        await interactions.response.send_message(f'Your balance is {user["balance"]} dollars.')
            
            
    async def work(self, interactions):
        # Simulate working and gives a random amount of money
        user_id = self.get_user_id(interactions)
        user = self.database.get_user(interactions.guild.id,user_id)

  
        
        # Check if the user has worked in the last 10 minutes
        if "last_work" in user:
            if user["last_work"] + 600 > time.time():
                await interactions.response.send_message("You can only work every 10 minutes.")
                return
        
        user["balance"] += random.randint(1, 100)
        
        
        self.database.update_user_balance(interactions.guild.id, user_id, user["balance"], True)
        await interactions.response.send_message(f"Congratulations! You now have {user['balance']} dollars.")
            
class Slot9x9Machine():
    def __init__(self, server_id):
        self.reels = ['🍒', '🍋', '🍊', '🍉', '🍇', '⭐', '🔔', '💎', '7️⃣']
        self.grid = []
        self.database = Database.getInstance()
        self.collection = self.database.get_collection(server_id)
        self.users = {}

    def spin(self):
        self.grid = [[random.choice(self.reels) for _ in range(3)] for _ in range(3)]
        return self.grid

    def check_winnings(self):
        # Define payouts for specific patterns
        payouts = {
            '🍒': 10,
            '🍋': 5,
            '🍊': 5,
            '🍉': 20,
            '🍇': 15,
            '⭐': 25,
            '🔔': 30,
            '💎': 50,
            '7️⃣': 100
        }
        
        total_payout = 0

        # Check rows and columns for identical symbols
        for i in range(3):
            if len(set(self.grid[i])) == 1:
                total_payout += payouts[self.grid[i][0]]
            if len(set([self.grid[j][i] for j in range(3)])) == 1:
                total_payout += payouts[self.grid[0][i]]

        # Check diagonals for identical symbols
        if len(set([self.grid[i][i] for i in range(3)])) == 1:
            total_payout += payouts[self.grid[0][0]]
        if len(set([self.grid[i][2 - i] for i in range(3)])) == 1:
            total_payout += payouts[self.grid[0][2]]

        return total_payout
    
    async def play(self, interactions, bet: int):
            if bet <= 0:
                await interactions.response.send_message(f'{interactions.user.mention}, you must bet a positive amount.')
                return
            
            user_id = str(interactions.user.id)
            user = self.database.get_user(interactions.guild.id, user_id)
            
            if user["balance"] < bet:
                await interactions.response.send_message("You don't have enough money to bet that amount.")
                return
            
            slot_machine = Slot9x9Machine()
            slot_machine.spin()
            payout = slot_machine.check_winnings()
            
            user["balance"] += (payout - bet)
            
            # Update the user's balance
            self.database.update_user_balance(interactions.guild.id, user_id, user["balance"])
            
            if payout > 0:
                # Update the user's experience
                self.database.update_user_experience(interactions.guild.id, user_id, payout)
            
            # Send initial message
            result_message = await interactions.response.send_message(f'{interactions.user.mention} spun the slots!', ephemeral=False)
            
            # React to the message with slot symbols
            result_message = await interactions.original_response()

            # Edit the original message to include the result
            embed = Utility.create_slots_9x9_embed_message(slot_machine.grid, bet, payout, user["balance"])
            await result_message.edit(content=None, embed=embed)