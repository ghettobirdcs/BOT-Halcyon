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
    @app_commands.describe(player_name="FACEIT username")
    async def player_stats(self, interaction: discord.Interaction, player_name: str):
        """Display player statistics from FACEIT"""
        await interaction.response.defer()
        
        try:
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
            elo = player_data.get('elo', 0)
            level = player_data.get('level', 0) 
            url = player_data.get('url', None)
            memberships = player_data.get('memberships', ())

            # Embed color based on faceit level
            if level < 4:
                color = discord.Color.green()
            elif level < 8:
                color = discord.Color.yellow()
            elif level < 10:
                color = discord.Color.orange()
            else:
                color = discord.Color.red()

            # Create embed
            embed = discord.Embed(
                title=f"📊 {nickname}'s Stats",
                color=color
            )
            
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)
            if url:
                url = url.replace("{lang}", "en")
            
            # Add general stats
            embed.add_field(
                name="Level",
                value=level,
                inline=True
            )
            embed.add_field(
                name="Elo Rating",
                value=elo,
                inline=True
            )
            embed.add_field(
                name="Memberships",
                value=memberships,
                inline=True
            )
            embed.add_field(
                name="FACEIT",
                value=f"[View Profile]({url})",
                inline=True
            )

            # Add CS2 specific stats
            if 'cs2_stats' in player_data:
                stats = player_data['cs2_stats']

                matches = stats.get('matches', 0)
                avg_kd_ratio = stats.get('avg_kd_ratio', 0)
                avg_headshot_percent = stats.get('avg_headshot_percent', 0)
                win_rate = stats.get('win_rate', 0)
                recent_results = stats.get('recent_results', ())
                
                formatted_results = ""
                for result in recent_results:
                    if result == "1":
                        formatted_results += "W "
                    elif result == "0":
                        formatted_results += "L "

                embed.add_field(
                    name="CS2 Matches",
                    value=matches,
                    inline=True
                )
                embed.add_field(
                    name="Avg. K/D Ratio",
                    value=avg_kd_ratio,
                    inline=True
                )
                embed.add_field(
                    name="Avg. Headshots",
                    value=avg_headshot_percent + ' %',
                    inline=True
                )
                embed.add_field(
                    name="Avg. Win Rate",
                    value=win_rate + ' %',
                    inline=True
                )
                embed.add_field(
                    name="Recent Results",
                    value=formatted_results,
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
