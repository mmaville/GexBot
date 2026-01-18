# GexBot
A Discord bot that sends a random Gex image along with a random quote.

## Setup

1. Clone the repository to a server/computer.

2. Install the required dependencies:
   ```
   pip install discord.py python-dotenv
   ```

3. Create or select a bot in the [Discord Developer Portal](https://discord.com/developers):
   - `Applications` > `New Application` (or select an existing one)
   - Navigate to `Bot` in the left sidebar
   - Click `Reset Token` or `Copy` to obtain the bot token

4. Create a `.env` file in the project root and add your token:
   ```
   DISCORD_TOKEN=your_token_here
   ```

5. Run the bot from the project directory:
   ```
   python bot.py
   ```

### Requirements

- Python 3.8+
- [discord.py](https://discordpy.readthedocs.io/en/latest/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

### Text File

Quotes are stored in `textlist.txt` at the root of the project. Each quote is on its own line.

### Images Folder

Image files are stored in `./images/`. The bot selects a random image from this directory.

## Usage

`!gex` - Sends a random image and quote of Gex the Gecko.
