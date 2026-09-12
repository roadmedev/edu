import aiohttp

from config import API_URL


async def post(endpoint: str, payload: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}{endpoint}", json=payload) as resp:
            return await resp.json()