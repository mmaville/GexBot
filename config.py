import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_BOT_TOKEN: str | None = os.getenv('DISCORD_BOT_TOKEN')
REQUIRED_ROLE: str = os.getenv('REQUIRED_ROLE', 'Gexy')

# Groq AI Configuration
GROQ_API_KEY: str | None = os.getenv('GROQ_API_KEY')
