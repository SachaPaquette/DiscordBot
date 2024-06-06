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
```

##### Usage

```bash

# Run the bot
python discordbot.py
```

## Commands Available

- /health: Health check for the bot.
- /join: Join the voice channel.
- /leave: Leave the voice channel.
- /ping <username>: Ping a user.
- /play <url>: Play a song.
- /skip: Skip the current song.
- /nowplaying: Display the current song.
- /queue: Display the queue.
- /clear: Clear the queue.
- /pause: Pause the current song.
- /resume: Resume the current song.
- /shuffle: Shuffle the queue.
- /lyrics: Display the lyrics of the current song.
- /userinfo <member>: Display user information.
- /gamble <amount>: Gamble your money.
- /leaderboard: Display the leaderboard.
- /rank: Display your rank.
- /work: Work to earn money.
- /balance: Display your bank balance.
- /slots <bet>: Play the slots.
- /case: Open a Counter-Strike case.

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
