import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_BOT_TOKEN: str | None = os.getenv('DISCORD_BOT_TOKEN')
REQUIRED_ROLE: str = os.getenv('REQUIRED_ROLE', 'Gexy')

# Groq AI Configuration
GROQ_API_KEY: str | None = os.getenv('GROQ_API_KEY')

# Movie Database Configuration
TMDB_KEY: str | None = os.getenv('TMDB_KEY')
OMDB_KEY: str | None = os.getenv('OMDB_KEY')
TRAKT_ID: str | None = os.getenv('TRAKT_ID')
