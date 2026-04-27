import os
import json
import aiohttp
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class LeetifyAPI:
    """Wrapper for LEETIFY API"""
    
    def __init__(self):
        self.api_key = os.getenv('LEETIFY_API_KEY')
        self.steam_key = os.getenv('STEAM_API_KEY')
        self.base_url = "https://api-public.cs-prod.leetify.com"
        
        if not self.api_key:
            raise ValueError("LEETIFY_API_KEY not found in .env file")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        # Initialize as None; we create it inside an async context later
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the internal aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def _make_request(self, endpoint: str) -> Optional[dict]:
        """Make an async GET request to the LEETIFY API"""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"API Error {response.status}: {await response.text()}")
                    return None
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None

    async def get_player_stats(self, steam_id: str) -> Optional[dict]:
        data = await self._make_request(f"/v3/profile?steam64_id={steam_id}")

        if data:
            return {
                'leetify_rating': data.get('ranks', {}).get('leetify', 0),
                'aim_rating': data.get('rating', {}).get('aim', 0),
                'utility_rating': data.get('rating', {}).get('utility', 0),
                'clutch_rating': data.get('rating', {}).get('clutch', 0),
                'flashbang_kills': data.get('stats', {}).get('flashbang_leading_to_kill', 0),
                'he_dmg': data.get('stats', {}).get('he_foes_damage_avg', 0),
                'preaim': data.get('stats', {}).get('preaim', 0),
                'reaction_time': data.get('stats', {}).get('reaction_time_ms', 0),
                'spray_accuracy': data.get('stats', {}).get('spray_accuracy', 0),
                'unused_utility': data.get('stats', {}).get('utility_on_death_avg', 0)
            }

        return None
