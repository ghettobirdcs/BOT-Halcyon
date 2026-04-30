import aiohttp
import asyncio
from typing import Optional

def main():
    url = "https://open.faceit.com/data/v4/championships/e8f7dbd0-e336-4456-8fd8-723154d7453a/matches?type=past"

    headers = {
        "Authorization": f"Bearer 6bc49e77-8125-4afe-95fb-2c987469749d",
        "Accept": "application/json",
    }

    data = asyncio.run(make_request(headers, url))
    print(data)

async def make_request(headers: dict, url: str, retries: int = 3) -> Optional[dict]:
    """Make an async GET request to the FACEIT API"""
    async with aiohttp.ClientSession(headers=headers) as session: 
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

if __name__ == "__main__":
    main()
