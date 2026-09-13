import aiohttp

from config import API_URL


async def post(endpoint: str, payload: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}{endpoint}", json=payload) as resp:
            return await resp.json()


async def get(endpoint: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}{endpoint}") as resp:
            if resp.status != 200:
                return {"error": f"Server {resp.status} qaytardi", "user": None}
            return await resp.json()