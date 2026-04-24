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
            # Fetch next match from FACEIT API
            next_match_data = await self.faceit_api.get_team_next_match(config.TEAM_FACEIT_ID)
            
            if not next_match_data:
                embed = discord.Embed(
                    title="No Upcoming Matches",
                    description="Your team has no scheduled matches at this time.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Parse match data with proper error handling
            opponent = next_match_data.get('opponent_name', 'Unknown')
            match_id = next_match_data.get('match_id', 'N/A')
            competition = next_match_data.get('competition_name', 'ESEA League')
            scheduled_at = next_match_data.get('scheduled_at')
        
            # Create embed
            embed = discord.Embed(
                title="📅 League Match",
                color=discord.Color.blue()
            )
            embed.add_field(name="Opponent", value=opponent, inline=False)
            embed.add_field(name="Competition", value=competition, inline=True)
        
            # Handle scheduled time safely
            if scheduled_at:
                try:
                    # Handle both ISO format and Unix timestamp
                    if isinstance(scheduled_at, str):
                        # Remove timezone info if present for fromisoformat
                        scheduled_at = scheduled_at.replace('Z', '+00:00')
                        match_time = datetime.fromisoformat(scheduled_at)
                    elif isinstance(scheduled_at, (int, float)):
                        match_time = datetime.fromtimestamp(scheduled_at)
                    else:
                        match_time = None
                    
                    if match_time:
                        embed.add_field(name="Scheduled Time", value=f"<t:{int(match_time.timestamp())}:F>", inline=True)
                    else:
                        embed.add_field(name="Scheduled Time", value="TBA", inline=True)
                except Exception as time_err:
                    print(f"Time parsing error: {time_err}, scheduled_at value: {scheduled_at}")
                    embed.add_field(name="Scheduled Time", value="TBA", inline=True)
            else:
                embed.add_field(name="Scheduled Time", value="TBA", inline=True)
            
            embed.add_field(name="Match ID", value=match_id, inline=False)
            # TODO: embed.set_footer(text="Use /matchdetails with the match ID for more information")
        
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"NextMatch Error: {e}")
            embed = discord.Embed(
                title="Error",
                description=f"Failed to fetch next match: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Load the Next Match cog"""
    await bot.add_cog(NextMatch(bot))
