import json
import time
import asyncio
from pathlib import Path
from typing import Any, Dict

from utils.constants import DEFAULT_COOLDOWN_SECONDS, DEFAULT_DAILY_LIMIT


def utc_ts() -> int:
    return int(time.time())


class ConfigService:
    def __init__(self, data_dir: Path):
        self.guilds_dir = data_dir / "guilds"
        self.guilds_dir.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, asyncio.Lock] = {}

    def _path(self, guild_id: int) -> Path:
        return self.guilds_dir / f"{guild_id}.json"

    def _lock(self, guild_id: int) -> asyncio.Lock:
        key = str(guild_id)
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    def default_config(self, guild_id: int) -> Dict[str, Any]:
        return {
            "guild_id": guild_id,
            "english_channel_id": None,
            "allowed_public_channels": [],
            "default_language": "pt-BR",
            "public_enabled": True,
            "learning_enabled": True,
            "cooldown_seconds": DEFAULT_COOLDOWN_SECONDS,
            "daily_limit": DEFAULT_DAILY_LIMIT,
            "daily_usage": {},
            "created_at": utc_ts(),
            "updated_at": utc_ts(),
        }

    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        path = self._path(guild_id)
        if not path.exists():
            return self.default_config(guild_id)

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            merged = self.default_config(guild_id)
            merged.update(data)
            return merged
        except Exception:
            backup = path.with_suffix(".corrupted.json")
            try:
                path.replace(backup)
            except Exception:
                pass
            return self.default_config(guild_id)

    async def save_guild_config(self, guild_id: int, config: Dict[str, Any]) -> None:
        config["updated_at"] = utc_ts()
        lock = self._lock(guild_id)
        async with lock:
            path = self._path(guild_id)
            temp_path = path.with_suffix(".tmp")
            temp_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
            temp_path.replace(path)
