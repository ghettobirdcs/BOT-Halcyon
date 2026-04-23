# Bot Halcyon - CS2 League Discord Bot

A Discord bot designed to track CS2 ESEA league matches and provide statistics from FACEIT for your team.

## Features

- **Next Match** - Display the starting time for your next league match
- **Last Match Stats** - Show basic statistics from your most recent league match
- **Match History** - Display your team's recent match history
- **Player Stats** - Get statistics for specific players from FACEIT

## Getting Started

### Prerequisites

- Python 3.8+
- Discord Bot Token
- FACEIT API Key

### Installation

1. Clone this repository
```bash
git clone https://github.com/ghettobirdcs/BOT-Halcyon.git
cd BOT-Halcyon
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory
```
DISCORD_TOKEN=your_bot_token_here
FACEIT_API_KEY=your_faceit_api_key_here
```

4. Update `config.py` with your team's FACEIT ID and Discord guild ID

5. Run the bot
```bash
python bot.py
```

## Configuration

Edit `config.py` to set:
- `TEAM_FACEIT_ID` - Your team's FACEIT ID
- `DISCORD_GUILD_ID` - Your Discord server ID (optional, for testing)

## Commands

- `/nextmatch` - Shows your team's next scheduled league match
- `/lastmatch` - Displays stats from your most recent match
- `/matchhistory [limit]` - Shows recent match history (default: 10 matches)
- `/playerstats <player_name>` - Gets statistics for a specific player

## Project Structure

```
BOT-Halcyon/
├── bot.py                 # Main bot file
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
├── cogs/                # Command modules
│   ├── __init__.py
│   ├── next_match.py
│   ├── last_match.py
│   ├── match_history.py
│   └── player_stats.py
├── api/
│   ├── __init__.py
│   └── faceit_api.py    # FACEIT API wrapper
└── README.md
```

## License

MIT
