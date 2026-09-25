from aiogram.filters import BaseFilter


class RoleFilter(BaseFilter):
    def __init__(self, *roles: str):
        self.roles = set(roles)

    async def __call__(self, event, user: dict | None = None) -> bool:
        return user is not None and user["role"] in self.roles