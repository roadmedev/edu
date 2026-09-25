import httpx


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class ApiClient:
    def __init__(self, base_url: str, api_key: str):
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"X-Bot-Key": api_key},
            timeout=15.0,
        )

    async def request(self, method: str, path: str, **kwargs):
        try:
            resp = await self._http.request(method, path, **kwargs)
        except httpx.HTTPError as e:
            raise ApiError(0, f"Backendga ulanib bo'lmadi: {e}") from e

        if resp.status_code >= 400:
            try:
                message = resp.json().get("error", resp.text)
            except ValueError:
                message = resp.text
            raise ApiError(resp.status_code, message)
        return resp.json()

    async def get(self, path: str, **kw):
        return await self.request("GET", path, **kw)

    async def post(self, path: str, **kw):
        return await self.request("POST", path, **kw)

    async def patch(self, path: str, **kw):
        return await self.request("PATCH", path, **kw)

    async def delete(self, path: str, **kw):
        return await self.request("DELETE", path, **kw)

    async def close(self):
        await self._http.aclose()