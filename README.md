# GexBot

A Discord bot powered by Groq AI that provides chat functionality, random Gex images and quotes, and admin controls.

## Features

- **Smart Model Routing**: Simple messages use a fast model, complex requests use a more powerful model
- **Chat Sessions**: Use `~` prefix to continue conversations without typing `!chat` each time (5-minute timeout)
- **Rotating Status**: Bot cycles through different status messages every 5 minutes
- **Channel Memory**: Each channel maintains its own conversation history (last 10 messages)

## Setup

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | Yes | Your Discord bot token |
| `GROQ_API_KEY` | Yes | Your Groq API key |
| `REQUIRED_ROLE` | No | Role required to use commands (default: `Gexy`) |

### Dependencies

* discord.py - https://discordpy.readthedocs.io/en/latest/
* groq - Groq Python SDK
* python-dotenv - For loading environment variables

Install with:
```
pip install discord.py groq python-dotenv
```

### Text File

All quotes must be contained in the `textlist.txt` file located at the root of the project. Quotes are separated by line breaks. Quotation marks are not required.

### Images Folder

All image files must be of a valid image filetype and located in `./images/`. The bot pulls a random image from this directory.

### System Prompt

The AI personality is defined in `system_prompt.md`. Edit this file to customize the bot's behavior.

## Usage

To start the bot in the background:

`docker compose up -d`

To see the live logs:

`docker compose logs -f`

To stop the bot:

`docker compose down`

## Commands

All commands require the configured role (default: **Gexy**).

| Command | Description |
|---------|-------------|
| `!chat [message]` | Chat with the AI. Remembers the last 10 messages per channel. |
| `~[message]` | Continue chatting without the `!chat` prefix (active for 5 minutes after last chat). |
| `!clear` | Clears the chat history (memory) for the current channel. |
| `!roast [@user]` | Roast a user in Gex's signature sarcastic style. |
| `!vibecheck` | Analyze the current channel's vibe based on recent messages. |
| `!gex` | Displays a random image and quote attributed to Gex the Gecko. |
| `!remindme [time] [message]` | Set a reminder (e.g., `!remindme 30m check the oven`). |
| `!leaderboard` | See who uses GexBot the most. |
| `!status [action] [text]` | Changes the bot's status. Actions: `playing`, `watching`, `listening`. |
| `!help` | Lists valid commands and their actions. |

## Project Structure

```
GexBot/
├── bot.py              # Main bot file
├── config.py           # Centralized configuration (loads from .env)
├── cogs/
│   ├── chat.py         # Chat commands (!chat, !clear, !roast, !vibecheck, ~ shortcut)
│   ├── gex.py          # Gex command (!gex)
│   ├── admin.py        # Admin commands (!status)
│   └── utility.py      # Utility commands (!remind, !leaderboard)
├── system_prompt.md    # AI personality configuration
├── textlist.txt        # Hardcoded Gex quotes
├── images/             # Gex images
├── leaderboard.json    # Persistent leaderboard data (auto-generated)
├── .env                # Environment variables (not in repo)
├── .env.example        # Template for environment variables
└── docker-compose.yml
```
