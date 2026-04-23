"""
Configuration file for Bot Halcyon
Update these values with your team's information
"""

# FACEIT Team ID for your CS2 league team
# You can find this in your team's FACEIT URL: https://www.faceit.com/en/teams/YOUR_TEAM_ID
TEAM_FACEIT_ID = "YOUR_TEAM_FACEIT_ID_HERE"

# Discord Guild ID (optional, used for slash command testing)
# Right-click your Discord server and enable Developer Mode to get this
DISCORD_GUILD_ID = None  # Set to your guild ID (int) or leave as None

# Bot prefix for text commands (if using them)
BOT_PREFIX = "/"

# FACEIT API Base URL
FACEIT_API_BASE_URL = "https://open.faceit.com/api/v4"

# Default match history limit
DEFAULT_MATCH_HISTORY_LIMIT = 10

# Match statistics to display
DISPLAY_STATS = [
    "K/D Ratio",
    "Headshot %",
    "Average Kills",
    "Win Rate",
    "Recent Form"
]
