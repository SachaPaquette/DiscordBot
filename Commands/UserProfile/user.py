import json
class User():
    # The constructor method for the User class
    def __init__(self, user_id: int, balance: int, experience: int):
        self.user_id = user_id
        self.balance = balance
        self.experience = experience 
        self.level = self.calculate_level()
        
    def levels(self):
        """
        Returns a list of experience points required for each level from the JSON file.
        """
        with open("Commands/UserProfile/levels.json") as f:
            return json.load(f)['levels']
        
        
    def calculate_level(self):
        """
        Calculates the user's level based on their experience points. Using Runescape's formula.
        """
        
        low = 0
        levels = self.levels()
        high = len(levels) - 1
        
        while low <= high:
            mid = (low + high) // 2
            if self.experience < levels[mid]:
                high = mid - 1
            elif self.experience >= levels[mid]:
                low = mid + 1
        
        return high
    
    def return_user(self):
        """
        Create a user object.
        """
        return {"user_id": self.user_id, "balance": self.balance, "experience": self.experience, "level": self.level}

    def give_experience(self, experience):
        """
        Give experience to the user.
        """
        self.experience += experience
        self.level = self.calculate_level()
        return self.experience
    
    def give_balance(self, amount):
        """
        Give balance to the user.
        """
        self.balance += amount
        return self.balance
    
    

    
    

    