"""
FACEIT API Wrapper
Handles all API calls to the FACEIT platform
"""

import asyncio
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
        self.base_url = os.getenv('FACEIT_API_BASE_URL')
        self.season_id = os.getenv('CURRENT_ESEA_SEASON_ID')
        
        if not self.api_key:
            raise ValueError("FACEIT_API_KEY not found in .env file")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Connection": "keep-alive"
        }

        # Initialize as None; we create it inside an async context later
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the internal aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            self.session = aiohttp.ClientSession(headers=self.headers, timeout=timeout)
        return self.session
    
    async def _make_request(self, endpoint: str, retries: int = 3) -> Optional[dict]:
        """Make an async GET request to the FACEIT API"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries):
            try:
                async with session.get(url) as response:
                    text = await response.text()

                    # Cloudfare detection
                    if text.startswith("<!DOCTYPE html>"):
                        print("Cloudfare block detected")
                        await asyncio.sleep(2 + attempt)
                        continue

                    if response.status == 200:
                        try:
                            return await response.json()
                        except Exception:
                            print("JSON parse failed, raw response:")
                            print(text[:300])
                            return None

                    print(f"API Error {response.status}: {text[:200]}")

            except asyncio.TimeoutError:
                print("Request timed out, retrying...")
            except Exception as e:
                print(f"Request error: {str(e)}")

            await asyncio.sleep(1.5 + attempt)

        return None
    

    # -----------------------------
    # TEAM MATCHES
    # -----------------------------

    async def get_team_matches(self, team_id: str, url_type: str) -> list:
        """Get recent match history for a team"""
        page = 1
        max_pages = 5  # Check up to 5 pages (500 results)
        team_matches = []  # Collect ALL team matches first
    
        while page <= max_pages:
            endpoint = f"/championships/{self.season_id}/matches?type={url_type}&limit=100&offset={(page-1)*100}"
            print(self.season_id)
            data = await self._make_request(endpoint)
    
            if not data or not data.get('items'):
                break
    
            # check each match to see if your team is playing
            for match in data['items']:
                teams = match.get('teams', {})
                faction1 = teams.get('faction1', {})
                faction2 = teams.get('faction2', {})
    
                team_id_1 = faction1.get('faction_id')
                team_id_2 = faction2.get('faction_id')

                if team_id_1 != team_id and team_id_2 != team_id:
                    continue

                is_faction1 = team_id_1 == team_id

                opponent = faction2 if is_faction1 else faction1
                opponent_name = opponent.get('name', 'Unknown')
                opponent_avatar = opponent.get('avatar')

                faceit_url = (match.get('faceit_url') or "").replace("{lang}", "en")

                result = {
                    'opponent_name': opponent_name,
                    'opponent_avatar': opponent_avatar,
                    'faceit_url': faceit_url
                }

                # TODO: faction1/2.get('roster').get('game_skill_level')?
                if url_type == "past":
                    results = match.get('results', {}).get('score', {})
                    result.update({
                        'finished_at': match.get('finished_at'),
                        'team_score': results.get('faction1' if is_faction1 else 'faction2', 0),
                        'opponent_score': results.get('faction2' if is_faction1 else 'faction1', 0),
                        'map_pick': match.get('voting', {}).get('map', {}).get('pick'),
                        'team_stats': await self._extract_team_stats(match.get('match_id'), team_id)
                    })
                else:
                    result.update({
                        'competition_name': match.get('competition', {}).get('name', 'ESEA League'),
                        'scheduled_at': match.get('scheduled_at')
                    })

                team_matches.append(result)

                # Rate limiting protection
                await asyncio.sleep(0.5)

            page += 1

        if url_type == "past":
            team_matches.sort(key=lambda x: x['finished_at'])
        else:
            team_matches.sort(key=lambda x: x['scheduled_at'])

        return team_matches

    async def get_team_next_match(self, team_id: str):
        matches = await self.get_team_matches(team_id, "upcoming")
        return matches[0] if matches else None

    async def get_team_last_match(self, team_id: str):
        matches = await self.get_team_matches(team_id, "past")
        return matches[-1] if matches else None
    

    # -----------------------------
    # PLAYER STATS
    # -----------------------------

    async def get_player_stats(self, player_name: str) -> Optional[dict]:
        """Get stats for a specific player by FACEIT username"""
        endpoint = f"/players?nickname={player_name}"
        player_data = await self._make_request(endpoint)
        
        if not player_data:
            return None

        # DEBUG: Print player data to console
        # self.print_match_data(player_data)
        
        player_id = player_data.get('player_id')

        # Get detailed player stats for CS2
        stats_endpoint = f"/players/{player_id}/stats/cs2"
        stats_data = await self._make_request(stats_endpoint)

        result = {
            'steam64_id': player_data.get('steam_id_64'),
            'nickname': player_data.get('nickname'),
            'avatar': player_data.get('avatar'),
            'elo': player_data.get('games', {}).get('cs2', {}).get('faceit_elo', 0),
            'level': player_data.get('games', {}).get('cs2', {}).get('skill_level', 0),
            'url': player_data.get('faceit_url', False)
        }

        # DEBUG: Print player stats to console
        # if stats_data:
        #     self.print_match_data(stats_data)
        
        if stats_data:
            lifetime = stats_data.get('lifetime', {})
            result['cs2_stats'] = {
                'matches': lifetime.get('Matches', 0),
                'avg_kd_ratio': lifetime.get('Average K/D Ratio', 'N/A'),
                'avg_headshot_percent': lifetime.get('Average Headshots %', 'N/A'),
                'win_rate': lifetime.get('Win Rate %', 0),
                'recent_results': lifetime.get('Recent Results', [])
            }
        
        return result

    
    # -----------------------------
    # MATCH STATS
    # -----------------------------

    async def _extract_team_stats(self, match_id: dict, team_id: str) -> Optional[dict]:
        """Extract team statistics from a match object"""
        if not match_id:
            return None

        endpoint = f"/matches/{match_id}/stats"
        match_data = await self._make_request(endpoint)

        if not match_data:
            return None

        # DEBUG: Print match_data
        # self.print_match_data(match_data)

        rounds = match_data.get('rounds', [])
        if not rounds:
            return None

        teams = rounds[0].get('teams', [])

        team_data = next((t for t in teams if t.get('team_id') == team_id), None)
        if not team_data:
            return None

        players = team_data.get('players', [])

        most_kills = 0
        most_mvps = 0
        most_kills_nickname = "Unknown"
        most_mvps_nickname = "Unknown"

        for player in players:
            stats = player.get('player_stats', {})
            kills = int(stats.get('Kills', 0))
            mvps = int(stats.get('MVPs', 0))

            if kills > most_kills:
                most_kills = kills
                most_kills_nickname = player.get('nickname')

            if mvps > most_mvps:
                most_mvps = mvps
                most_mvps_nickname = player.get('nickname')

        return {
            'most_kills': most_kills,
            'most_kills_nickname': most_kills_nickname,
            'most_mvps': most_mvps,
            'most_mvps_nickname': most_mvps_nickname
        }

    # def _unwrap(self, value):
    #     if isinstance(value, (list, tuple)):
    #         return value[0] if value else None
    #     return value

    def print_match_data(self, match: dict, title: str = "Match Data") -> None:
        """Pretty print match data to console"""
        print("\n" + "=" * 70)
        print(f"{title}")
        print("=" * 70)
        print(json.dumps(match, indent=2))
        print("=" * 70 + "\n")
