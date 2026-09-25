import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    api_url: str
    api_key: str
    center_address: str = "o'quv markaz"
    admin_username: str = "mruzmetov"
    admin_ids: tuple[int, ...] = ()


def load_settings() -> Settings:
    try:
        raw_admins = os.getenv("ADMIN_IDS", "")
        admin_ids = tuple(int(x) for x in raw_admins.split(",") if x.strip().isdigit())
        return Settings(
            bot_token=os.environ["BOT_TOKEN"],
            api_url=os.environ["API_URL"].rstrip("/"),
            api_key=os.environ["API_KEY"],
            center_address=os.getenv("CENTER_ADDRESS", "o'quv markaz"),
            admin_username=os.getenv("ADMIN_USERNAME", "mruzmetov"),
            admin_ids=admin_ids,
        )
    except KeyError as e:
        raise RuntimeError(f".env faylida {e.args[0]} yo'q") from e


settings = load_settings()