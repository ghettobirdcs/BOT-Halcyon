"""
Player Stats Command
Displays statistics for a specific player from FACEIT
"""

import discord
import os
import math
from discord.ext import commands
from discord import app_commands
from api.faceit_api import FaceitAPI
from api.leetify_api import LeetifyAPI

class PlayerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.faceit_api = FaceitAPI()
        self.leetify_api = LeetifyAPI()
    
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

            steam_id = player_data.get('steam64_id', None)
            leetify_data = None

            if steam_id:
                leetify_data = await self.leetify_api.get_player_stats(steam_id)
            
            # Parse player data
            nickname = player_data.get('nickname', player_name)
            avatar_url = player_data.get('avatar', None)
            elo = player_data.get('elo', 0)
            level = player_data.get('level', 0) 
            url = player_data.get('url', None)

            if not leetify_data:
                embed = discord.Embed(
                    title="Player has no Leetify",
                    description=f"Could not find player: {player_name}",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return

            # Parse LEETIFY data
            leetify_rating = leetify_data.get('leetify_rating', 0)
            aim_rating = leetify_data.get('aim_rating', 0)
            utility_rating = leetify_data.get('utility_rating', 0)
            clutch_rating = leetify_data.get('clutch_rating', 0)
            preaim = leetify_data.get('preaim', 0)
            spray_accuracy = leetify_data.get('spray_accuracy', 0)
            reaction_time = leetify_data.get('reaction_time', 0)
            flashbang_kills = leetify_data.get('flashbang_kills', 0)
            he_dmg = leetify_data.get('he_dmg', 0)
            unused_utility = leetify_data.get('unused_utility', 0)

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
                name="Leetify Rating",
                value=leetify_rating,
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

            embed.add_field(
                name="",
                value="",
                inline=False
            )

            embed.add_field(
                name="Aim",
                value=math.floor(aim_rating * 100) / 100,
                inline=True
            )

            embed.add_field(
                name="Utility",
                value=math.floor(utility_rating * 100) / 100,
                inline=True
            )

            embed.add_field(
                name="Clutch",
                value=math.floor((clutch_rating * 100) * 100) / 100,
                inline=True
            )
            
            embed.add_field(
                name="Killer Flashbangs",
                value=math.floor(flashbang_kills * 100) / 100,
                inline=True
            )

            embed.add_field(
                name="Avg. HE Damage",
                value=math.floor(he_dmg * 100) / 100,
                inline=True
            )

            embed.add_field(
                name="Preaim",
                value=f"{math.floor(preaim * 100) / 100}°",
                inline=True
            )

            embed.add_field(
                name="Reaction Time (ms)",
                value=math.floor(reaction_time * 100) / 100,
                inline=True
            )

            embed.add_field(
                name="Spray Accuracy",
                value=f"{math.floor(spray_accuracy * 100) / 100} %",
                inline=True
            )

            embed.add_field(
                name="Unused Utility",
                value=f"$ {math.floor(unused_utility * 100) / 100}",
                inline=True
            )

            embed.add_field(
                name="",
                value=f"[View on Leetify](https://leetify.com/app/profile/{steam_id})", 
                inline=False
            )

            # Add Leetify logo to embed (local png image)
            path = os.path.join("assets", "leetify_logo.png")
            leetify_logo = discord.File(path, filename="leetify_logo.png")
            embed.set_image(url="attachment://leetify_logo.png")

            embed.set_footer(text="Data provided by FACEIT, Leetify")
            
            await interaction.followup.send(embed=embed, file=leetify_logo)
            
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
