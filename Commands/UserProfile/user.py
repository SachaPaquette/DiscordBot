import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import discord
class User():
    # The constructor method for the User class
    def __init__(self, user_id: int, user_name:str, balance: int, experience: int):
        self.user_id = user_id
        self.user_name = user_name
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
        return {"user_id": self.user_id,"user_name": self.user_name, "balance": self.balance, "experience": self.experience, "level": self.calculate_level(), "total_bet": 0}
    
    def fetch_user(self, user_id):
        """
        Fetch a user from the database.
        """
        return self.collection.find_one({"user_id": user_id})

    def give_experience(self, experience):
        """
        Give experience to the user.
        """
        self.experience += experience
        self.level = self.calculate_level()
        print(self.level)
        return self.experience
    
    def give_balance(self, amount):
        """
        Give balance to the user.
        """
        self.balance += amount
        return self.balance

class UserCard():
    def __init__(self): 
        pass
    
    def create_user_card(self, username, rank, avatar_url):
        # Card dimensions
        card_width = 400
        card_height = 200
        border_size = 10
        avatar_size = 80
        background_color = (30, 30, 30)  # Dark gray
        text_color = (255, 255, 255)  # White
        border_color = (255, 215, 0)  # Gold

        # Load avatar image
        print(avatar_url)
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content))
        avatar = avatar.resize((avatar_size, avatar_size))

        # Create card background
        card = Image.new("RGB", (card_width, card_height), background_color)

        # Draw the border
        draw = ImageDraw.Draw(card)
        draw.rectangle([0, 0, card_width, card_height], outline=border_color, width=border_size)

        # Add avatar with border
        avatar_with_border = ImageOps.expand(avatar, border=border_size//2, fill=border_color)
        card.paste(avatar_with_border, (border_size + 10, card_height // 2 - avatar_size // 2))

        # Load a font
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Change this to the path of your desired font
        font = ImageFont.truetype(font_path, 24)
        small_font = ImageFont.truetype(font_path, 18)

        # Add username and rank text
        text_x = border_size + avatar_size + 30
        draw.text((text_x, card_height // 2 - 30), username, font=font, fill=text_color)
        draw.text((text_x, card_height // 2 + 10), f"Rank: {rank}", font=small_font, fill=text_color)

        # Save the image to a BytesIO object
        image_bytes = BytesIO()
        
        card.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        
        file = discord.File(image_bytes, filename="user_card.png")

        return file
    
    

    