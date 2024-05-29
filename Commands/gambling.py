from Commands.database import Database
import random
import time

class Gambling():
    
    def __init__(self):
        self.database = Database.getInstance()
        self.collection = self.database.collection
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
        
    def roll_dice(self):
        """
        Simulates a dice roll.
        
        Returns:
        - result: The result of the dice roll.
        """
        import random
        return random.choice(["win", "lose"])

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
        user = self.database.get_user(user_id)
        
        if user is None:
            self.insert_user(user_id)
            user = self.collection.find_one({"user_id": user_id})

        if user["balance"] < bet:
            await interactions.response.send_message("You don't have enough money to bet that amount.")
            return

        symbols = self.get_slot_symbols()
        payout = self.calculate_payout(symbols, bet)
        user["balance"] += payout
        
        # Send initial message
        result_message = await interactions.response.send_message(f'{interactions.user.mention} spun the slots!', ephemeral=False)

        # React to the message with slot symbols
        result_message = await interactions.original_response()
        for symbol in symbols:
            await result_message.add_reaction(symbol)

        # Construct the result message
        if payout > 0:
            result_message_text = f'You won {payout} coins! Your new balance is {user["balance"]} coins.'
        elif payout < 0:
            result_message_text = f'You lost {bet} coins. Your new balance is {user["balance"]} coins.'
        else:
            result_message_text = f'You broke even. Your balance is still {user["balance"]} coins.'

        # Edit the original message to include the result
        await result_message.edit(content=result_message.content + "\n" + result_message_text)
       
    async def balance(self, interactions):
        user_id = self.get_user_id(interactions)
        user = self.database.get_user(user_id)
        
        if user is None:
            self.insert_user(user_id)
            user = self.collection.find_one({"user_id": user_id})
        
        await interactions.response.send_message(f'Your balance is {user["balance"]} dollars.')
            
            
    async def work(self, interactions):
        # Simulate working and gives a random amount of money
        user_id = self.get_user_id(interactions)
        user = self.database.get_user(user_id)

        if user is None:
            self.insert_user(user_id)
            user = self.collection.find_one({"user_id": user_id})
        
        # Check if the user has worked in the last 10 minutes
        if "last_work" in user:
            if user["last_work"] + 600 > time.time():
                await interactions.response.send_message("You can only work every 10 minutes.")
                return
        
        user["balance"] += random.randint(1, 100)
        
        self.collection.update_one({"user_id": user_id}, {"$set": {"balance": user["balance"], "last_work": time.time()}})
        
        await interactions.response.send_message(f"Congratulations! You earned {user['balance']} dollars.")
            
            