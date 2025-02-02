import aiohttp
from typing import Any

def build_request(base_url: str, method: str | None = None, **query_params) -> str:
    params = "&".join(f"{k}={v}" for k, v in query_params.items())
    if method:
        return f"{base_url}/method/{method}?{params}"
    return f"{base_url}?{params}"

async def send_request(url, headers: dict[str, Any] | None = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()
