import asyncio
import json
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_faceit_api():
    """Test FACEIT API endpoint"""
    api_key = os.getenv('FACEIT_API_KEY')
    team_id = "ff8b71f7-a8c3-4ead-b6a7-a34fca359f1e"
    
    if not api_key:
        print("ERROR: FACEIT_API_KEY not found in .env file")
        return
    
    base_url = "https://open.faceit.com/data/v4"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    # Test 1: Get team info (to verify team ID is correct)
    print("=" * 50)
    print("TEST 1: Fetching team info")
    print("=" * 50)
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/teams/{team_id}"
        async with session.get(url, headers=headers) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response: {json.dumps(data, indent=2)}\n")
    
    # Test 2: Get team matches
    print("=" * 50)
    print("TEST 2: Fetching team matches")
    print("=" * 50)
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/championships/{os.getenv('CURRENT_ESEA_SEASON_ID')}/matches?type=upcoming&limit=100"
        async with session.get(url, headers=headers) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response: {json.dumps(data, indent=2)}\n")

# Run the test
asyncio.run(test_faceit_api())
