"""
Last Match Command
Displays basic statistics from your team's most recent league match
"""

from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import maybe_coroutine
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
            last_match_data = await self.faceit_api.get_team_last_match(config.TEAM_FACEIT_ID)
            
            if not last_match_data:
                embed = discord.Embed(
                    title="No Match History",
                    description="Your team has no completed matches yet.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return

            # DEBUG: Print match data to console
            # self.faceit_api.print_match_data(last_match_data, "Last Match Data")
            
            # Parse match data
            opponent = last_match_data.get('opponent_name', 'Unknown')
            team_score = last_match_data.get('team_score', 0)
            opponent_score = last_match_data.get('opponent_score', 0)
            opponent_avatar = last_match_data.get('opponent_avatar')
            # TODO: avg_skill_lvl = last_match_data.get('skill_level')
            map_pick = last_match_data.get('map_pick')
            faceit_url = last_match_data.get('faceit_url')
            finished_at = last_match_data.get('finished_at', 0)
            timestamp = datetime.fromtimestamp(finished_at)
            result = "✅ Win" if team_score > opponent_score else "❌ Loss"
            
            # Create embed
            embed = discord.Embed(
                title="📊 Last League Match",
                color=discord.Color.green() if team_score > opponent_score else discord.Color.red()
            )

            if opponent_avatar:
                embed.set_thumbnail(url=opponent_avatar)

            if map_pick:
                map_pick = map_pick[3:].capitalize()

            embed.add_field(name="Opponent", value=opponent, inline=False)
            score_line = f"**{team_score}** - **{opponent_score}**"
            embed.add_field(name="Map", value=map_pick, inline=True)
            embed.add_field(name="Score", value=score_line, inline=True)
            embed.add_field(name="Result", value=result, inline=True)
            embed.add_field(name="Finished", value=f"<t:{int(timestamp.timestamp())}:F>", inline=False)
            
            # Add team stats if available
            if 'team_stats' in last_match_data:
                stats = last_match_data['team_stats']
                # TODO: Embed team statistics
                embed.add_field(name="Placeholder", value=stats.get('kd_ratio', 'N/A'), inline=True)
                embed.add_field(name="Placeholder", value=stats.get('headshot_percent', 'N/A'), inline=True)

            embed.add_field(name="Matchroom", value=faceit_url, inline=False)
            
            # TODO:
            # embed.set_footer(text="Use /matchhistory to see more recent matches")
            
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
