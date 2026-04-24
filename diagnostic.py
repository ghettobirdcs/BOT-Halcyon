import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

async def diagnose_matches():
    """Diagnose why a specific match isn't showing up"""
    api_key = os.getenv('FACEIT_API_KEY')
    team_id = "ff8b71f7-a8c3-4ead-b6a7-a34fca359f1e"  # Your Halcyon team ID
    
    base_url = "https://open.faceit.com/data/v4"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    print("Fetching matches with limit=500...")
    print("=" * 70)
    
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/championships/{os.getenv('CURRENT_ESEA_SEASON_ID')}/matches"
        params = {"limit": 100, "type": "upcoming"}
        
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                matches = data.get('items', [])
                
                print(f"Total matches returned: {len(matches)}\n")
                
                # Look for Lazarus match
                for idx, match in enumerate(matches):
                    scheduled = match.get('scheduled_at', 'N/A')
                    match_id = match.get('match_id', 'N/A')
                    
                    teams = match.get('teams', {})
                    faction1 = teams.get('faction1', {})
                    faction2 = teams.get('faction2', {})
                    
                    team1_name = faction1.get('name', 'Unknown')
                    team2_name = faction2.get('name', 'Unknown')
                    
                    # Highlight Lazarus or Halcyon matches
                    if 'lazarus' in team1_name.lower() or 'lazarus' in team2_name.lower():
                        print(f"Match {idx + 1}:")
                        print(f"  ID: {match_id}")
                        print(f"  Teams: {team1_name} vs {team2_name}")
                        print(f"  Scheduled: {scheduled}")
                        print(f"  Status: {match.get('status', 'N/A')}")
                        print()
                        print("  ^^^ LAZARUS MATCH FOUND ^^^")
                    if 'halcyon' in team1_name.lower() or 'halcyon' in team2_name.lower():
                        print(f"Match {idx + 1}:")
                        print(f"  ID: {match_id}")
                        print(f"  Teams: {team1_name} vs {team2_name}")
                        print(f"  Scheduled: {scheduled}")
                        print(f"  Status: {match.get('status', 'N/A')}")
                        print()
                        print("  ^^^ HALCYON MATCH FOUND ^^^")
            else:
                print(f"Error: {response.status}")
                print(await response.text())

asyncio.run(diagnose_matches())
