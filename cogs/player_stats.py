"""
Player Stats Command
Displays statistics for a specific player from FACEIT
"""

import discord
from discord.ext import commands
from discord import app_commands
from api.faceit_api import FaceitAPI

class PlayerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faceit_api = FaceitAPI()
    
    @app_commands.command(
        name="playerstats",
        description="Get statistics for a specific player from FACEIT"
    )
    @app_commands.describe(player_name="FACEIT username or player name")
    async def player_stats(self, interaction: discord.Interaction, player_name: str):
        """Display player statistics from FACEIT"""
        await interaction.response.defer()
        
        try:
            # TODO: Fetch player stats from FACEIT API
            player_data = await self.faceit_api.get_player_stats(player_name)
            
            if not player_data:
                embed = discord.Embed(
                    title="Player Not Found",
                    description=f"Could not find player: {player_name}",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Parse player data
            nickname = player_data.get('nickname', player_name)
            avatar_url = player_data.get('avatar', None)
            
            # Create embed
            embed = discord.Embed(
                title=f"📊 {nickname}'s Stats",
                color=discord.Color.purple()
            )
            
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)
            
            # Add general stats
            embed.add_field(
                name="Elo Rating",
                value=player_data.get('elo', 'N/A'),
                inline=True
            )
            embed.add_field(
                name="Win Rate",
                value=player_data.get('win_rate', 'N/A'),
                inline=True
            )
            
            # Add CS2 specific stats
            if 'cs2_stats' in player_data:
                stats = player_data['cs2_stats']
                embed.add_field(
                    name="K/D Ratio",
                    value=stats.get('kd_ratio', 'N/A'),
                    inline=True
                )
                embed.add_field(
                    name="Headshot %",
                    value=stats.get('headshot_percent', 'N/A'),
                    inline=True
                )
                embed.add_field(
                    name="Average Kills",
                    value=stats.get('avg_kills', 'N/A'),
                    inline=True
                )
            
            embed.set_footer(text="Stats are updated from FACEIT")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to fetch player stats: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Load the Player Stats cog"""
    await bot.add_cog(PlayerStats(bot))
