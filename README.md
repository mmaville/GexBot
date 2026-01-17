# GexBot
A discord bot that provides a random image from the designated folder, along with a random quote from a text file.

## Setup

TO-DO

### Dependencies

* DiscordPy - https://discordpy.readthedocs.io/en/latest/

### Text File

All quotes must be contained in the `textlist.txt` file located at the root of the project. Quotes are separated by line breaks. Quotation marks are not required.

### Images Folder

All image files must be of a valid image filetype and located in `./images/`. The bot pulls a random image from this directory.

## Usage

To start the bot in the background:

`docker compose up -d`

To see the live logs:

`docker compose logs -f`

To stop the bot:

`docker compose down`

### Commands

* `!gex` - Displays a random image and quote attributed to Gex the Gecco.
* `!chat` - Enter chat mode with GexBot. Remembers the last 10 messages.
* `!clear` - Deletes the existing chat histormy (memory).
* `!help` - Lists valid commands and their actions.
