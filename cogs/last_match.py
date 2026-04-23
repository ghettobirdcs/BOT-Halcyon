"""
Last Match Command
Displays basic statistics from your team's most recent league match
"""

import discord
from discord.ext import commands
from discord import app_commands
from api.faceit_api import FaceitAPI
import config

class LastMatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faceit_api = FaceitAPI()
    
    @app_commands.command(name="lastmatch", description="Displays stats from your team's most recent league match")
    async def last_match(self, interaction: discord.Interaction):
        """Display stats from the last match"""
        await interaction.response.defer()
        
        try:
            # TODO: Fetch last match from FACEIT API
            last_match_data = await self.faceit_api.get_team_last_match(config.TEAM_FACEIT_ID)
            
            if not last_match_data:
                embed = discord.Embed(
                    title="No Match History",
                    description="Your team has no completed matches yet.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Parse match data
            team_name = last_match_data.get('team_name', 'Your Team')
            opponent = last_match_data.get('opponent_name', 'Unknown')
            team_score = last_match_data.get('team_score', 0)
            opponent_score = last_match_data.get('opponent_score', 0)
            result = "✅ Win" if team_score > opponent_score else "❌ Loss" if team_score < opponent_score else "🤝 Draw"
            
            # Create embed
            embed = discord.Embed(
                title="📊 Last League Match",
                color=discord.Color.green() if team_score > opponent_score else discord.Color.red()
            )
            embed.add_field(name="Result", value=result, inline=True)
            embed.add_field(name="Score", value=f"{team_score} - {opponent_score}", inline=True)
            embed.add_field(name="Opponent", value=opponent, inline=False)
            
            # Add team stats if available
            if 'team_stats' in last_match_data:
                stats = last_match_data['team_stats']
                embed.add_field(name="Team K/D", value=stats.get('kd_ratio', 'N/A'), inline=True)
                embed.add_field(name="Headshot %", value=stats.get('headshot_percent', 'N/A'), inline=True)
            
            embed.set_footer(text="Use /matchhistory to see more recent matches")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to fetch last match: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Load the Last Match cog"""
    await bot.add_cog(LastMatch(bot))
