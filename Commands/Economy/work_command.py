# Simulate working and gives a random amount of money
import time
import random
import json
from Config.logging import setup_logging
from Config.config import conf
from Commands.Services.utility import EmbedMessage
from Commands.Services.database import Database
# Create a logger for this file
logger = setup_logging("work.py", conf.LOGS_PATH)


class Jobs():
    def __init__(self, filename="Commands/Economy/EconomyData/jobs.json"):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                self.jobs = json.load(file)

            # Convert job levels (keys) to integers and store them in a new dictionary
            self.jobs = {int(key): value for key, value in self.jobs.items()}

            # Sort the job levels in descending order
            self.sorted_job_levels = sorted(self.jobs.keys(), reverse=True)

        except Exception as e:
            logger.error(f"Error loading jobs.json: {e}")
            self.jobs = {}
            self.sorted_job_levels = []

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
                interactions, fields=["balance", "level", "last_work", "experience"]
            )
            if not user:
                await interactions.response.send_message("User not found in the database.")
                logger.error("User not found: Check if the database entry exists.")
                return

            # Check if the user has worked in the last 10 minutes
            if self.has_worked(user):
                await interactions.response.send_message("You can only work every 10 minutes.")
                return

            # Get the user's job
            job = self.jobs.get_job(user.get("level", 1))
            if not job:
                await interactions.response.send_message("No job found for your level.")
                logger.error(f"No job found for level: {user.get('level', 1)}")
                return

            # Get a random amount of money between the min and max earnings of the job
            amount_earned = self.get_amount_earned(job)

            # Update the user's balance
            self.database.update_user_balance(
                interactions.guild.id, interactions.user.id, user["balance"] + amount_earned, 0, True
            )

            # Send a message to the user
            embed = self.embedMessage.create_work_embed(
                interactions, job, amount_earned, user["balance"] + amount_earned
            )
            await interactions.response.send_message(embed=embed)

        except Exception as e:
            logger.error(f"Error in the work function in work_command.py: {e}")
            await interactions.response.send_message("An unexpected error occurred.")

