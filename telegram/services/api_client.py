# services/api_client.py
import aiohttp

from config import API_URL


async def post(endpoint: str, payload: dict) -> dict:
    """POST so'rov yuborish"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}{endpoint}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status >= 400:
                    try:
                        data = await resp.json()
                        return {"error": data.get("error", f"Server {resp.status}")}
                    except Exception:
                        return {"error": f"Server {resp.status} qaytardi"}
                return await resp.json()
    except aiohttp.ClientError as e:
        return {"error": f"Tarmoq xatosi: {e}"}
    except Exception as e:
        return {"error": f"Kutilmagan xato: {e}"}


async def get(endpoint: str) -> dict:
    """GET so'rov yuborish"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}{endpoint}",
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    try:
                        data = await resp.json()
                        return {"error": data.get("error", f"Server {resp.status} qaytardi")}
                    except Exception:
                        return {"error": f"Server {resp.status} qaytardi"}
                return await resp.json()
    except aiohttp.ClientError as e:
        return {"error": f"Tarmoq xatosi: {e}"}
    except Exception as e:
        return {"error": f"Kutilmagan xato: {e}"}


async def put(endpoint: str, payload: dict) -> dict:
    """PUT so'rov yuborish"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{API_URL}{endpoint}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status >= 400:
                    try:
                        data = await resp.json()
                        return {"error": data.get("error", f"Server {resp.status}")}
                    except Exception:
                        return {"error": f"Server {resp.status} qaytardi"}
                return await resp.json()
    except aiohttp.ClientError as e:
        return {"error": f"Tarmoq xatosi: {e}"}
    except Exception as e:
        return {"error": f"Kutilmagan xato: {e}"}


async def delete(endpoint: str) -> dict:
    """DELETE so'rov yuborish"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{API_URL}{endpoint}",
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status >= 400:
                    try:
                        data = await resp.json()
                        return {"error": data.get("error", f"Server {resp.status}")}
                    except Exception:
                        return {"error": f"Server {resp.status} qaytardi"}
                return await resp.json()
    except aiohttp.ClientError as e:
        return {"error": f"Tarmoq xatosi: {e}"}
    except Exception as e:
        return {"error": f"Kutilmagan xato: {e}"}