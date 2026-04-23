"""
Next Match Command
Displays the starting time for your team's next league match
"""

import discord
from discord.ext import commands
from discord import app_commands
from api.faceit_api import FaceitAPI
import config
from datetime import datetime

class NextMatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faceit_api = FaceitAPI()
    
    @app_commands.command(name="nextmatch", description="Shows your team's next scheduled league match")
    async def next_match(self, interaction: discord.Interaction):
        """Display the next match for the team"""
        await interaction.response.defer()
        
        try:
            # TODO: Fetch next match from FACEIT API
            # This should get the team's upcoming matches
            next_match_data = await self.faceit_api.get_team_next_match(config.TEAM_FACEIT_ID)
            
            if not next_match_data:
                embed = discord.Embed(
                    title="No Upcoming Matches",
                    description="Your team has no scheduled matches at this time.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Parse match data
            match_time = datetime.fromisoformat(next_match_data.get('scheduled_at', ''))
            opponent = next_match_data.get('opponent_name', 'Unknown')
            match_id = next_match_data.get('match_id', 'N/A')
            competition = next_match_data.get('competition_name', 'ESEA League')
            
            # Create embed
            embed = discord.Embed(
                title="📅 Next League Match",
                color=discord.Color.blue()
            )
            embed.add_field(name="Opponent", value=opponent, inline=False)
            embed.add_field(name="Competition", value=competition, inline=True)
            embed.add_field(name="Scheduled Time", value=f"<t:{int(match_time.timestamp())}:F>", inline=True)
            embed.add_field(name="Match ID", value=match_id, inline=False)
            embed.set_footer(text="Use /matchdetails with the match ID for more information")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to fetch next match: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Load the Next Match cog"""
    await bot.add_cog(NextMatch(bot))
