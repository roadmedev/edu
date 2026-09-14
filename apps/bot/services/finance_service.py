from services.api_client import get


async def get_finance_summary() -> dict:
    return await get("/admin/finance")


async def get_finance_history(history_type: str) -> dict:
    return await get(f"/admin/finance/history?type={history_type}")