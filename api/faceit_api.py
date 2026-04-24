"""
FACEIT API Wrapper
Handles all API calls to the FACEIT platform
"""

import os
import aiohttp
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

    async def get_team_next_match(self, team_id: str) -> Optional[dict]:
        """Get team's earliest upcoming match across all pages"""
        page = 1
        max_pages = 5  # Check up to 5 pages (500 results)
        team_matches = []  # Collect ALL team matches first
    
        while page <= max_pages:
            endpoint = f"/championships/{os.getenv('CURRENT_ESEA_SEASON_ID')}/matches?type=upcoming&limit=100&offset={(page-1)*100}"
            data = await self._make_request(endpoint)
    
            if not data or 'items' not in data or len(data['items']) == 0:
                break
    
            # check each match to see if your team is playing
            for match in data['items']:
                teams = match.get('teams', {})
                faction1 = teams.get('faction1', {})
                faction2 = teams.get('faction2', {})
    
                team_id_1 = faction1.get('faction_id')
                team_id_2 = faction2.get('faction_id')
                
                # if your team is in this match, add it to the list
                if team_id_1 == team_id:
                    team_matches.append({
                        'match_id': match.get('match_id'),
                        'scheduled_at': match.get('scheduled_at'),
                        'opponent_name': faction2.get('name', 'Unknown'),
                        'competition_name': match.get('competition', {}).get('name', 'ESEA League')
                    })
                elif team_id_2 == team_id:
                    team_matches.append({
                        'match_id': match.get('match_id'),
                        'scheduled_at': match.get('scheduled_at'),
                        'opponent_name': faction1.get('name', 'Unknown'),
                        'competition_name': match.get('competition', {}).get('name', 'ESEA League')
                    })
    
            page += 1
        
        # Return the earliest match (sorted by scheduled_at)
        if team_matches:
            earliest_match = min(team_matches, key=lambda x: x.get('scheduled_at', 0))
            return earliest_match
        
        return None
    
    async def get_team_last_match(self, team_id: str) -> Optional[dict]:
        """Get the last completed league match for a team"""
        page = 1
        max_pages = 5  # Check up to 5 pages (500 results)
        team_matches = []

        while page <= max_pages:
            endpoint = f"/championships/{os.getenv('CURRENT_ESEA_SEASON_ID')}/matches?type=past&limit=100&offset={(page-1)*100}"
            data = await self._make_request(endpoint)
            
            if data and 'items' in data and len(data['items']) > 0:
                # Find the first finished match
                for match in data['items']:
                    teams = match.get('teams', {})
                    faction1 = teams.get('faction1', {})
                    faction2 = teams.get('faction2', {})
        
                    team_id_1 = faction1.get('faction_id')
                    team_id_2 = faction2.get('faction_id')

                    if team_id_1 == team_id or team_id_2 == team_id:
                        # Parse match results
                        results = match.get('results', {})
                        
                        if team_id_1 == team_id:
                            team_score = results.get('score', {}).get('faction1', 0)
                            opponent_score = results.get('score', {}).get('faction2', 0)
                            opponent_name = faction2.get('name', 'Unknown')
                            team_name = faction1.get('name', 'Unknown')
                        else:
                            team_score = results.get('score', {}).get('faction2', 0)
                            opponent_score = results.get('score', {}).get('faction1', 0)
                            opponent_name = faction1.get('name', 'Unknown')
                            team_name = faction2.get('name', 'Unknown')

                        team_matches.append({
                            'match_id': match.get('match_id'),
                            'finished_at': match.get('finished_at'),
                            'team_name': team_name,
                            'opponent_name': opponent_name,
                            'team_score': team_score,
                            'opponent_score': opponent_score,
                            'team_stats': await self._extract_team_stats(match)
                        })

            page += 1

        if team_matches:
            latest_match = max(team_matches, key=lambda x: x.get('finished_at', 0))
            return latest_match

        return None
    
    async def get_team_match_history(self, team_id: str, limit: int = 10) -> list:
        """Get recent match history for a team"""
        endpoint = f"/teams/{team_id}/matches"
        data = await self._make_request(endpoint)
        
        matches = []
        if data and 'items' in data:
            count = 0
            for match_item in data['items']:
                if match_item.get('status') == 'FINISHED' and count < limit:
                    results = match_item.get('results', {})
                    matches.append({
                        'match_id': match_item.get('match_id'),
                        'opponent_name': match_item.get('opponent', {}).get('name', 'Unknown'),
                        'team_score': results.get('score', 0),
                        'opponent_score': results.get('opponent_score', 0),
                        'date': match_item.get('finished_at')
                    })
                    count += 1
        return matches
    
    async def get_player_stats(self, player_name: str) -> Optional[dict]:
        """Get stats for a specific player by FACEIT username"""
        endpoint = f"/players?nickname={player_name}"
        player_data = await self._make_request(endpoint)
        
        if not player_data:
            return None
        
        player_id = player_data.get('player_id')
        
        # Get detailed player stats for CS2
        stats_endpoint = f"/players/{player_id}/stats/CS2"
        stats_data = await self._make_request(stats_endpoint)
        
        result = {
            'nickname': player_data.get('nickname'),
            'avatar': player_data.get('avatar'),
            'elo': player_data.get('elo'),
            'win_rate': player_data.get('game_player_stats', {}).get('win_rate', 'N/A')
        }
        
        if stats_data:
            result['cs2_stats'] = {
                'kd_ratio': stats_data.get('lifetime', {}).get('K/D Ratio', 'N/A'),
                'headshot_percent': stats_data.get('lifetime', {}).get('Headshot %', 'N/A'),
                'avg_kills': stats_data.get('lifetime', {}).get('Average Kills', 'N/A')
            }
        
        return result
    
    async def _extract_team_stats(self, match: dict) -> dict:
        """Extract team statistics from a match object"""
        stats = match.get('statistics', {})
        return {
            'kd_ratio': stats.get('K/D Ratio', 'N/A'),
            'headshot_percent': stats.get('Headshot %', 'N/A')
        }
