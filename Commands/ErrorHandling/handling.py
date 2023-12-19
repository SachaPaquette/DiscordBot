class CommandErrorHandler:
    # Function to check if the URL is a valid Youtube URL
    def check_url_correct(url):
        if url is None:
            return False
        if not url.startswith("https://www.youtube.com/watch?v="):
            return False
        return True
    # Function to check if the URL and song title are valid (not None)
    def check_url_song_correct(url, song_title):
        # Check if the URL and song title are valid
        if url is None:
            return False
        if song_title is None:
            return False
        return True
    


    