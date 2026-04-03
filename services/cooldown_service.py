import json
import time
from pathlib import Path
from typing import Tuple


def utc_ts() -> int:
    return int(time.time())


def today_key() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


class CooldownService:
    def __init__(self, data_dir: Path):
        self.temp_dir = data_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def check_cooldown(self, guild_id: int, user_id: int, cooldown_seconds: int) -> Tuple[bool, int]:
        path = self.temp_dir / f"cooldown_{guild_id}_{user_id}.json"
        now = utc_ts()

        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                expires_at = int(data.get("expires_at", 0))
                if expires_at > now:
                    return True, expires_at - now
            except Exception:
                pass

        path.write_text(json.dumps({"expires_at": now + cooldown_seconds}), encoding="utf-8")
        return False, 0
