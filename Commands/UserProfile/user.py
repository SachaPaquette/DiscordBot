
class User():
    # The constructor method for the User class
    def __init__(self, user_id: int, balance: int, experience: int):
        self.user_id = user_id
        self.balance = balance
        self.experience = experience 
        self.level = self.calculate_level()
        
    def calculate_level(self):
        """
        Calculates the user's level based on their experience points. Using Runescape's formula.
        """
        
        levels = [0, 83, 174, 276, 388, 512, 650, 801, 969, 1154, 1358, 1584, 1833, 2107, 2411, 2746, 3115, 3523, 3973, 4470, 5018, 5624, 6291, 7028, 7842, 8740, 9730, 10824, 12031, 13363, 14833, 16456, 18247, 20224, 22406, 24815, 27473, 30408, 33648, 37224, 41171, 45529, 50339, 55649, 61512, 67983, 75127, 83014, 91721, 101333, 111945, 123660, 136594, 150872, 166636, 184040, 203254, 224466, 247886, 273742, 302288, 333804, 368599, 407015, 449428, 496254, 547953, 605032, 668051, 737627, 814445, 899257, 992895, 1096278, 1210421, 1336443, 1475581, 1629200, 1798808, 1986068, 2192818, 2421087, 2673114, 2951373, 3258594, 3597792, 3972294, 4385776, 4842295, 5346332, 5902831, 6517253, 7195629, 7944614, 8771558, 9684577, 10692629, 11805606, 13034431]
        
        low = 0
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
    
    

    
    

    