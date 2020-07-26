# GexBot
A discord bot that provides a random image from the designated folder, along with a random quote from a text file.

## Setup

1. Clone the repository to a server/computer.

1. Create or select a bot in the [Discord Developer Portal](https://discord.com/developers). (`Applications` > `New Application`) or (`Applications` > `My Applications` > `bot-name`).

2. Select `Settings` > `Bot` to display the `Build-a-Bot` page.

3. Find the Token section of the page and click `Copy` to obtain the token.

4. Paste the token into the value of the `discord_token` parameter in `bot.py`.

5. Navigate to the local repository on the machine and run the command `python bot.py` to initiaze the bot.

### Dependencies

* DiscordPy - https://discordpy.readthedocs.io/en/latest/

### Text File

All quotes must be contained in the `textlist.txt` file located at the root of the project. Quotes are separated by line breaks. Quotation marks are not required.

### Images Folder

All image files must be of a valid image filetype and located in `./images/`. The bot pulls a random image from this directory.

## Usage

* `!gex` - This command displays a random image and quote of Gex the Gecco.
