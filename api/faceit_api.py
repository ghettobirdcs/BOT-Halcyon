"""
FACEIT API Wrapper
Handles all API calls to the FACEIT platform
"""

import os
import aiohttp
import json
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FaceitAPI:
    """Wrapper for FACEIT API v4"""
    
    def __init__(self):
        self.api_key = os.getenv('FACEIT_API_KEY')
        self.base_url = "https://open.faceit.com/data/v4"
        
        if not self.api_key:
            raise ValueError("FACEIT_API_KEY not found in .env file")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    async def _make_request(self, endpoint: str) -> Optional[dict]:
        """Make an async GET request to the FACEIT API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"API Error {response.status}: {await response.text()}")
                        return None
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None

    def print_match_data(self, match: dict, title: str = "Match Data") -> None:
        """Pretty print match data to console"""
        print("\n" + "=" * 70)
        print(f"{title}")
        print("=" * 70)
        print(json.dumps(match, indent=2))
        print("=" * 70 + "\n")

    async def get_team_next_match(self, team_id: str) -> Optional[dict]:
        """Get team's earliest upcoming match across all pages"""
        team_matches = await self.get_team_matches(team_id, "upcoming")

        if team_matches:
            return team_matches[0]
        
        return None
    
    async def get_team_last_match(self, team_id: str) -> Optional[dict]:
        """Get the last completed league match for a team"""
        team_matches = await self.get_team_matches(team_id, "past")

        if team_matches:
            return team_matches[-1]

        return None
    
    async def get_team_matches(self, team_id: str, url_type: str) -> list:
        """Get recent match history for a team"""
        page = 1
        max_pages = 5  # Check up to 5 pages (500 results)
        team_matches = []  # Collect ALL team matches first
    
        while page <= max_pages or len(team_matches) < 5:
            endpoint = f"/championships/{os.getenv('CURRENT_ESEA_SEASON_ID')}/matches?type={url_type}&limit=100&offset={(page-1)*100}"
            data = await self._make_request(endpoint)
    
            if not data or 'items' not in data or len(data['items']) == 0:
                break
    
            # check each match to see if your team is playing
            for match in data['items']:
                match_id = match.get('match_id', None)  # NOTE: Used for API hit in _extract_team_stats
                teams = match.get('teams', {})
                faction1 = teams.get('faction1', {})
                faction2 = teams.get('faction2', {})
    
                team_id_1 = faction1.get('faction_id')
                team_id_2 = faction2.get('faction_id')

                team_score = 0
                opponent_score = 0
                
                # if your team is in this match, add it to the list
                if team_id_1 == team_id or team_id_2 == team_id:
                    if team_id_1 == team_id:
                        if url_type == "past":
                            results = match.get('results', {})
                            team_score = results.get('score', {}).get('faction1', 0)
                            opponent_score = results.get('score', {}).get('faction2', 0)

                        opponent_name = faction2.get('name', 'Unknown')
                        opponent_avatar = faction2.get('avatar'),
                        # TODO: faction1/2.get('roster').get('game_skill_level')?
                    else:
                        if url_type == "past":
                            results = match.get('results', {})
                            team_score = results.get('score', {}).get('faction2', 0)
                            opponent_score = results.get('score', {}).get('faction1', 0)

                        opponent_name = faction1.get('name', 'Unknown')
                        opponent_avatar = faction1.get('avatar'),

                    faceit_url = match.get('faceit_url').replace("{lang}", "en")

                    if url_type == "past":
                        map_pick = match.get('voting').get('map').get('pick')

                        team_matches.append({
                            'finished_at': match.get('finished_at'),
                            'opponent_name': opponent_name,
                            'team_score': team_score,
                            'opponent_score': opponent_score,
                            'opponent_avatar' : self._get_first_item(opponent_avatar),
                            'map_pick' : self._get_first_item(map_pick),
                            'faceit_url' : self._get_first_item(faceit_url),
                            'team_stats': await self._extract_team_stats(match_id, team_id)
                        })
                    else:
                        team_matches.append({
                            'competition_name': match.get('competition', {}).get('name', 'ESEA League'),
                            'scheduled_at': match.get('scheduled_at'),
                            'opponent_name': opponent_name,
                            'opponent_avatar' : self._get_first_item(opponent_avatar),
                            'faceit_url' : self._get_first_item(faceit_url)
                        })

            page += 1

        if url_type == "past":
            team_matches.sort(key=lambda x: x['finished_at'])
        else:
            team_matches.sort(key=lambda x: x['scheduled_at'])

        return team_matches
    
    async def get_player_stats(self, player_name: str) -> Optional[dict]:
        """Get stats for a specific player by FACEIT username"""
        endpoint = f"/players?nickname={player_name}"
        player_data = await self._make_request(endpoint)
        
        if not player_data:
            return None

        # DEBUG: Print player data to console
        # self.print_match_data(player_data)
        
        player_id = player_data.get('player_id')
        player_elo = player_data.get('games', {}).get('cs2', {}).get('faceit_elo', 0)
        player_level = player_data.get('games', {}).get('cs2', {}).get('skill_level', 0)
        player_url = player_data.get('faceit_url', False)

        # Get detailed player stats for CS2
        stats_endpoint = f"/players/{player_id}/stats/cs2"
        stats_data = await self._make_request(stats_endpoint)

        # DEBUG: Print player stats to console
        # if stats_data:
        #     self.print_match_data(stats_data)
        
        result = {
            'steam64_id': player_data.get('steam_id_64'),
            'nickname': player_data.get('nickname'),
            'avatar': player_data.get('avatar'),
            'elo' : player_elo,
            'level' : player_level,
            'url' : player_url
        }
        
        if stats_data:
            result['cs2_stats'] = {  # Only shows stats for CS2, not CSGO
                'matches': stats_data.get('lifetime', {}).get('Matches', 0),
                'avg_kd_ratio': stats_data.get('lifetime', {}).get('Average K/D Ratio', 'N/A'),
                'avg_headshot_percent': stats_data.get('lifetime', {}).get('Average Headshots %', 'N/A'),
                'win_rate': stats_data.get('lifetime', {}).get('Win Rate %', 0),
                'recent_results': stats_data.get('lifetime', {}).get('Recent Results', [])
            }
        
        return result

    def _get_first_item(self, value):
        """Extract first item from list or return value as-is"""
        if isinstance(value, list) and len(value) > 0 or isinstance(value, tuple) and len(value) > 0:
            return value[0]
        return value

    async def _extract_team_stats(self, match_id: dict, team_id: str) -> Optional[dict]:
        """Extract team statistics from a match object"""
        endpoint = f"/matches/{match_id}/stats"
        match_data = await self._make_request(endpoint)

        if not match_data:
            return None

        # DEBUG: Print match_data
        # self.print_match_data(match_data)

        teams = match_data.get('rounds', {})[0].get('teams', {})
        home_team = teams[0]

        for team in teams:
            if team.get('team_id', None) == team_id:
                home_team = team
                break
        
        players_data = home_team.get('players', {})

        most_kills = 0
        most_mvps = 0
        most_kills_nickname = "Unknown"
        most_mvps_nickname = "Unknown"

        for player in players_data:
            nickname = player.get('nickname', None)
            stats = player.get('player_stats', {})

            kills = int(stats.get('Kills', 0))
            mvps = int(stats.get('MVPs', 0))

            if kills > most_kills:
                most_kills = kills
                most_kills_nickname = nickname

            if mvps > most_mvps:
                most_mvps = mvps
                most_mvps_nickname = nickname

        return {
            'most_kills': most_kills,
            'most_kills_nickname': most_kills_nickname,
            'most_mvps': most_mvps,
            'most_mvps_nickname': most_mvps_nickname
        }
