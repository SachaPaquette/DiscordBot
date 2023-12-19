# Discord Music Bot
### Simple Discord bot to play music and much more!

### Table of Contents

    [Installation](#installation)
    [Commands](#commands-available)
    [Dependencies](#dependencies)
    [Configuration](#configuration)
    [License](#license)

## Installation

```bash

# Clone the repository
git clone https://github.com/SachaPaquette/DiscordBot.git

# Change directory to the project folder
cd DiscordBot\

# Install dependencies
pip install -r requirements.txt 
```

##### Usage

```bash

# Run the bot
python discordbot.py
```
## Commands Available
    !health: Check if the bot is alive.
    !join: Join the voice channel.
    !leave: Leave the voice channel.
    !ping <username>: Ping a user.
    !skip: Skip the current song.
    !play <url>: Play a song.
    !nowplaying: Display the current song.
    !queue: Display the queue.
    !clear: Clear the queue.
    !pause: Pause the current song.
    !resume: Resume the current song.
    !shuffle: Shuffle the queue.
    !userinfo <member>: Display user information.

## Dependencies

List of external libraries the project relies on.

    discord.py
    youtube-dl
    yt-dlp
    nacl
    dotenv

## Configuration

Create a .env file that is in the root of the project and add your discord token.
```bash
# .env file content
DISCORD_TOKEN="your_discord_token"
```


## License

This project is licensed under the MIT License.
