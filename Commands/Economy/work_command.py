# Simulate working and gives a random amount of money
from dataclasses import dataclass
from enum import Enum
import time
import random
from Config.logging import setup_logging
from Config.config import conf
from Commands.Services.utility import EmbedMessage
from Commands.Services.database import Database
# Create a logger for this file
logger = setup_logging("work.py", conf.LOGS_PATH)


class JobTitles(Enum):
    CASHIER = 1
    WAITER = 2
    BARTENDER = 3
    CHEF = 4
    MANAGER = 5
    CEO = 6
    PRESIDENT = 7
    KING = 8
    GOD = 9
    CREATOR = 10


class Jobs():
    def __init__(self):

        # Create a job based on the user's level
        self.jobs = {
            1: {"title": JobTitles.CASHIER.name, "icon": "🛒",  "earnings_range": (1, 100), "description": "You work as a cashier in a small store. You earn between $1 and $100."},
            11: {"title": JobTitles.WAITER.name, "icon": "🍽️", "earnings_range": (101, 200), "description": "You work as a waiter in a restaurant. You earn between $101 and $200."},
            21: {"title": JobTitles.BARTENDER.name, "icon": "🍹", "earnings_range": (201, 300), "description": "You work as a bartender in a bar. You earn between $201 and $300."},
            31: {"title": JobTitles.CHEF.name, "icon": "🍳", "earnings_range": (500, 700), "description": "You work as a chef in a restaurant. You earn between $500 and $700."},
            41: {"title": JobTitles.MANAGER.name, "icon": "🗂️", "earnings_range": (800, 1000), "description": "You work as a manager in a store. You earn between $800 and $1000."},
            51: {"title": JobTitles.CEO.name, "icon": "💼", "earnings_range": (1000, 2000), "description": "You work as a CEO in a company. You earn between $1000 and $2000."},
            61: {"title": JobTitles.PRESIDENT.name, "icon": "🏛️", "earnings_range": (2000, 3000), "description": "You work as a president in a company. You earn between $2000 and $3000."},
            71: {"title": JobTitles.KING.name, "icon": "👑", "earnings_range": (3000, 4000), "description": "You work as a king in a kingdom. You earn between $3000 and $4000."},
            81: {"title": JobTitles.GOD.name, "icon": "⚡", "earnings_range": (4000, 5000), "description": "You work as a god in a universe. You earn between $4000 and $5000."},
            91: {"title": JobTitles.CREATOR.name, "icon": "🌌", "earnings_range": (5000, 6000), "description": "You work as a creator of the universe. You earn between $5000 and $6000."}
        }
        self.sorted_job_levels = sorted(self.jobs.keys(), reverse=True)

    def get_job(self, level):
        for job_level in self.sorted_job_levels:
            if level >= job_level:
                return self.jobs[job_level]
        return None


class Work():
    def __init__(self):
        self.database = Database.getInstance()
        self.jobs = Jobs()
        self.embedMessage = EmbedMessage()
        self.work_cooldown = 600

    def get_amount_earned(self, job):
        return random.randint(job["earnings_range"][0], job["earnings_range"][1])

    def has_worked(self, user):
        return user.get("last_work", 0) + self.work_cooldown > time.time()

    async def work_command(self, interactions):
        try:
            # Get the user's data
            user = self.database.get_user(
                interactions, fields=["balance", "level", "last_work"])

            # Check if the user has worked in the last 10 minutes
            if self.has_worked(user):
                await interactions.response.send_message("You can only work every 10 minutes.")
                return
            # Get the user's job
            job = self.jobs.get_job(user.get("level", 1))
            # Get a random amount of money between the min and max earnings of the job
            amount_earned = self.get_amount_earned(job)

            # Update the user's balance
            self.database.update_user_balance(
                interactions.guild.id, interactions.user.id, user["balance"] + amount_earned, 0, True)

            # Send a message to the user
            await interactions.response.send_message(embed=self.embedMessage.create_work_embed(interactions, job, amount_earned, user["balance"] + amount_earned))
        except Exception as e:
            logger.error(f"Error in the work function in work_command.py: {e}")
            return
