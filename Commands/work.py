# Simulate working and gives a random amount of money
import time, random
from Config.logging import setup_logging
from Config.config import conf
from Commands.database import Database
# Create a logger for this file
logger = setup_logging("work.py", conf.LOGS_PATH)

class Jobs():
    def __init__(self):
        # Create job based on the user's level
        # Between level 1 and 10, the user can work as a cashier
        # Between level 11 and 20, the user can work as a waiter
        # Between level 21 and 30, the user can work as a bartender
        # Between level 31 and 40, the user can work as a chef
        # Between level 41 and 50, the user can work as a manager
        # Between level 51 and 60, the user can work as a CEO
        # Between level 61 and 70, the user can work as a president
        # Between level 71 and 80, the user can work as a king
        # Between level 81 and 90, the user can work as a god
        # Between level 91 and 99, the user can work as a creator
        
        self.jobs = {
            1: {"title": "cashier", "min_earnings": 1, "max_earnings": 100, "description": "You work as a cashier in a small store. You earn between $1 and $100."},
            11: {"title": "waiter", "min_earnings": 101, "max_earnings": 200, "description": "You work as a waiter in a restaurant. You earn between $101 and $200."},
            21: {"title": "bartender", "min_earnings": 201, "max_earnings": 300, "description": "You work as a bartender in a bar. You earn between $201 and $300."},
            31: {"title": "chef", "min_earnings": 500, "max_earnings": 700, "description": "You work as a chef in a restaurant. You earn between $500 and $700."},
            41: {"title": "manager", "min_earnings": 800, "max_earnings": 1000, "description": "You work as a manager in a store. You earn between $800 and $1000."},
            51: {"title": "CEO", "min_earnings": 1000, "max_earnings": 2000, "description": "You work as a CEO in a company. You earn between $1000 and $2000."},
            61: {"title": "president", "min_earnings": 2000, "max_earnings": 3000, "description": "You work as a president in a company. You earn between $2000 and $3000."},
            71: {"title": "king", "min_earnings": 3000, "max_earnings": 4000, "description": "You work as a king in a kingdom. You earn between $3000 and $4000."},
            81: {"title": "god", "min_earnings": 4000, "max_earnings": 5000, "description": "You work as a god in a universe. You earn between $4000 and $5000."},
            91: {"title": "creator", "min_earnings": 5000, "max_earnings": 6000, "description": "You work as a creator of the universe. You earn between $5000 and $6000."}
        }
        
    def get_job(self, level):
        # Get the job based on the user's level
        low = 0
        high = len(self.jobs) - 1
        while low <= high:
            mid = (low + high) // 2
            if level < list(self.jobs.keys())[mid]:
                high = mid - 1
            elif level >= list(self.jobs.keys())[mid]:
                low = mid + 1
        return self.jobs[list(self.jobs.keys())[high]]
    
        

class Work():
    def __init__(self):
        self.database = Database.getInstance()
        self.jobs = Jobs()
    async def work_command(self, interactions):
        try:
            # Get the user's data
            user = self.database.get_user(interactions.guild.id, interactions.user.id)
            # Check if the user has worked in the last 10 minutes
            if user.get("last_work", 0) + 600 > time.time():
                await interactions.response.send_message("You can only work every 10 minutes.")
                return              
            # Get the user's job
            job = self.jobs.get_job(user.get("level", 1))
            
            # Get a random amount of money between the min and max earnings of the job
            amount_earned = random.randint(job["min_earnings"], job["max_earnings"])

            # Update the user's balance
            self.database.update_user_balance(interactions.guild.id, interactions.user.id, user["balance"] + amount_earned, 0, True)
            # Send a message to the user
            await interactions.response.send_message(f"Congratulations! You worked as a {job['title']} and earned ${amount_earned}, you now have {(user['balance'] + amount_earned):.2f} dollars.")
        except Exception as e:
            logger.error(f"Error in the work function in gambling.py: {e}")
            return