"""
FACEIT API Wrapper
Handles all API calls to the FACEIT platform
"""

import os
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FaceitAPI:
    """Wrapper for FACEIT API v4"""
    
    def __init__(self):
        self.api_key = os.getenv('FACEIT_API_KEY')
        self.base_url = "https://open.faceit.com/api/v4"
        
        if not self.api_key:
            raise ValueError("FACEIT_API_KEY not found in .env file")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    async def _make_request(self, endpoint: str) -> dict:
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
    
    async def get_team_next_match(self, team_id: str) -> dict:
        """Get the next match for a team"""
        # TODO: Implement FACEIT API call to get next match
        # Endpoint: /teams/{team_id}/matches?status=UPCOMING
        endpoint = f"/teams/{team_id}/matches?status=UPCOMING&limit=1"
        data = await self._make_request(endpoint)
        
        if data and 'items' in data and len(data['items']) > 0:
            match = data['items'][0]
            return {
                'match_id': match.get('match_id'),
                'scheduled_at': match.get('scheduled_at'),
                'opponent_name': match.get('opponent', {}).get('name', 'Unknown'),
                'competition_name': match.get('competition', {}).get('name', 'ESEA League')
            }
        return None
    
    async def get_team_last_match(self, team_id: str) -> dict:
        """Get the last completed match for a team"""
        # TODO: Implement FACEIT API call to get last match
        # Endpoint: /teams/{team_id}/matches?status=FINISHED
        endpoint = f"/teams/{team_id}/matches?status=FINISHED&limit=1"
        data = await self._make_request(endpoint)
        
        if data and 'items' in data and len(data['items']) > 0:
            match = data['items'][0]
            # Parse match results
            results = match.get('results', {})
            team_score = results.get('score', 0)
            opponent_score = results.get('opponent_score', 0)
            
            return {
                'match_id': match.get('match_id'),
                'team_name': match.get('team', {}).get('name', 'Your Team'),
                'opponent_name': match.get('opponent', {}).get('name', 'Unknown'),
                'team_score': team_score,
                'opponent_score': opponent_score,
                'team_stats': await self._extract_team_stats(match)
            }
        return None
    
    async def get_team_match_history(self, team_id: str, limit: int = 10) -> list:
        """Get recent match history for a team"""
        # TODO: Implement FACEIT API call to get match history
        # Endpoint: /teams/{team_id}/matches
        endpoint = f"/teams/{team_id}/matches?status=FINISHED&limit={limit}"
        data = await self._make_request(endpoint)
        
        matches = []
        if data and 'items' in data:
            for match in data['items']:
                results = match.get('results', {})
                matches.append({
                    'match_id': match.get('match_id'),
                    'opponent_name': match.get('opponent', {}).get('name', 'Unknown'),
                    'team_score': results.get('score', 0),
                    'opponent_score': results.get('opponent_score', 0),
                    'date': match.get('finished_at')
                })
        return matches
    
    async def get_player_stats(self, player_name: str) -> dict:
        """Get stats for a specific player by FACEIT username"""
        # TODO: Implement FACEIT API call to get player stats
        # Endpoint: /players?nickname={player_name}
        endpoint = f"/players?nickname={player_name}"
        player_data = await self._make_request(endpoint)
        
        if not player_data:
            return None
        
        player_id = player_data.get('player_id')
        
        # Get detailed player stats
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
        # TODO: Parse match statistics
        return {
            'kd_ratio': 'N/A',
            'headshot_percent': 'N/A'
        }
