# Simulate working and gives a random amount of money
import time, random
from Config.logging import setup_logging
from Config.config import conf
from Commands.utility import EmbedMessage
from Commands.database import Database
# Create a logger for this file
logger = setup_logging("work.py", conf.LOGS_PATH)

class Jobs():
    def __init__(self):
        # Create a job based on the user's level    
        self.jobs = {
            1: {"title": "cashier", "icon": "🛒", "min_earnings": 1, "max_earnings": 100, "description": "You work as a cashier in a small store. You earn between $1 and $100."},
            11: {"title": "waiter", "icon": "🍽️", "min_earnings": 101, "max_earnings": 200, "description": "You work as a waiter in a restaurant. You earn between $101 and $200."},
            21: {"title": "bartender", "icon": "🍹", "min_earnings": 201, "max_earnings": 300, "description": "You work as a bartender in a bar. You earn between $201 and $300."},
            31: {"title": "chef", "icon": "🍳", "min_earnings": 500, "max_earnings": 700, "description": "You work as a chef in a restaurant. You earn between $500 and $700."},
            41: {"title": "manager", "icon": "🗂️", "min_earnings": 800, "max_earnings": 1000, "description": "You work as a manager in a store. You earn between $800 and $1000."},
            51: {"title": "CEO", "icon": "💼", "min_earnings": 1000, "max_earnings": 2000, "description": "You work as a CEO in a company. You earn between $1000 and $2000."},
            61: {"title": "president", "icon": "🏛️", "min_earnings": 2000, "max_earnings": 3000, "description": "You work as a president in a company. You earn between $2000 and $3000."},
            71: {"title": "king", "icon": "👑", "min_earnings": 3000, "max_earnings": 4000, "description": "You work as a king in a kingdom. You earn between $3000 and $4000."},
            81: {"title": "god", "icon": "⚡", "min_earnings": 4000, "max_earnings": 5000, "description": "You work as a god in a universe. You earn between $4000 and $5000."},
            91: {"title": "creator", "icon": "🌌", "min_earnings": 5000, "max_earnings": 6000, "description": "You work as a creator of the universe. You earn between $5000 and $6000."}
        }
        
        
    def get_job(self, level):
        # Get the job corresponding to the user's level
        for lvl in sorted(self.jobs.keys(), reverse=True):
            if level >= lvl:
                return self.jobs[lvl]
        return None

class Work():
    def __init__(self):
        self.database = Database.getInstance()
        self.jobs = Jobs()
        self.embedMessage = EmbedMessage()
        
    def get_amount_earned(self, job):
        return random.randint(job["min_earnings"], job["max_earnings"])
        
    def has_worked(self, user):
        return user.get("last_work", 0) + 600 > time.time()
        
    async def work_command(self, interactions):
        try:
            # Get the user's data
            user = self.database.get_user(interactions)
            
            # Check if the user has worked in the last 10 minutes
            if self.has_worked(user):
                await interactions.response.send_message("You can only work every 10 minutes.")
                return        
                  
            # Get the user's job
            job = self.jobs.get_job(user.get("level", 1))
            
            # Get a random amount of money between the min and max earnings of the job
            amount_earned = self.get_amount_earned(job)

            # Update the user's balance
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"] + amount_earned, 0, True)

            # Send a message to the user
            await interactions.response.send_message(embed=self.embedMessage.create_work_embed(interactions, job, amount_earned, user["balance"] + amount_earned))
        except Exception as e:
            logger.error(f"Error in the work function in gambling.py: {e}")
            return