# Discord Bot
A Discord bot built with discord.py for managing music, gambling, user interactions, and more.

### Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Commands](#commands-available)
- [Dependencies](#dependencies)
- [License](#license)

## Installation

```bash

# Clone the repository
git clone https://github.com/SachaPaquette/DiscordBot.git

# Change directory to the project folder
cd DiscordBot/

# Install dependencies
pip install -r requirements.txt 
```

## Configuration

Create a .env file that is in the root of the project and add your discord token.

```bash
# .env file content
DISCORD_TOKEN="your_discord_token"
BOT_OWNER_ID="your_id" (This lets you use commands that are only for the admin)
GENERAL_CHANNEL_NAME="your_discord_general_channel"
MONGO_DB_ADDRESS="your_mongo_db_address" (local address is: "mongodb://localhost:27017")
```

##### Usage

```bash

# Run the bot
python discordbot.py
```

## Commands Available

### Games
- /case: Open a Counter-Strike case.
- /sticker: Open a Counter-Strike capsule of stickers.
- /gamble &lt;amount&gt;: Gamble your money.
- /slots &lt;bet&gt;: Play the slots.
- /blackjack: Play a game of blackjack.
- /stocks &lt;option&gt; : Buy or sell a stock.
- /portfolio: Display your stocks owned.
- /work: Work to earn money.
- /balance: Display your bank balance.

### Music
- /play &lt;url&gt;: Play a song.
- /skip: Skip the current song.
- /nowplaying: Display the current song.
- /queue: Display the queue.
- /clear: Clear the queue.
- /pause: Pause the current song.
- /resume: Resume the current song.
- /shuffle: Shuffle the queue.
- /lyrics: Display the lyrics of the current song.

### Users
- /userinfo &lt;member&gt;: Display user information.
- /rank: Display your rank.
- /ping &lt;username&gt;: Ping a user.
- /leaderboard: Display the leaderboard.

### Extra
- /health: Health check for the bot (Also syncs the slash commands with Discord).

## Dependencies

List of external libraries the project relies on.

    discord.py
    youtube-dl
    yt-dlp
    nacl
    dotenv
    whois



## License

This project is licensed under the MIT License.
