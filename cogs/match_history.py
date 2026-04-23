"""
Match History Command
Displays your team's recent match history
"""

import discord
from discord.ext import commands
from discord import app_commands
from api.faceit_api import FaceitAPI
import config

class MatchHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faceit_api = FaceitAPI()
    
    @app_commands.command(
        name="matchhistory",
        description="Shows your team's recent match history"
    )
    @app_commands.describe(limit="Number of matches to display (1-50, default: 10)")
    async def match_history(self, interaction: discord.Interaction, limit: int = config.DEFAULT_MATCH_HISTORY_LIMIT):
        """Display recent match history"""
        await interaction.response.defer()
        
        # Validate limit
        if limit < 1 or limit > 50:
            embed = discord.Embed(
                title="Invalid Limit",
                description="Limit must be between 1 and 50.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        try:
            # TODO: Fetch match history from FACEIT API
            matches = await self.faceit_api.get_team_match_history(config.TEAM_FACEIT_ID, limit)
            
            if not matches:
                embed = discord.Embed(
                    title="No Match History",
                    description="Your team has no completed matches yet.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create embed
            embed = discord.Embed(
                title="📈 Match History",
                description=f"Last {len(matches)} matches",
                color=discord.Color.blue()
            )
            
            # Add matches to embed
            for idx, match in enumerate(matches, 1):
                opponent = match.get('opponent_name', 'Unknown')
                team_score = match.get('team_score', 0)
                opponent_score = match.get('opponent_score', 0)
                result = "W" if team_score > opponent_score else "L" if team_score < opponent_score else "D"
                
                field_value = f"{result} | {team_score}-{opponent_score} vs {opponent}"
                embed.add_field(
                    name=f"Match {idx}",
                    value=field_value,
                    inline=False
                )
            
            embed.set_footer(text="Use /lastmatch for detailed stats on your most recent match")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to fetch match history: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Load the Match History cog"""
    await bot.add_cog(MatchHistory(bot))
