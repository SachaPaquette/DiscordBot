class conf:
    FFMPEG_OPTIONS = {
                    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    "options": "-vn",
                }
    
    LOGS_PATH = "./Config/Logs/DiscordBot.log"
    
    # Create a regex pattern to match a URL (https and http)
    REGEX_URL_PATTERN = r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,})"
    
    # Set the options for YoutubeDL
    YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}