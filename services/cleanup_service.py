import json
import time
from pathlib import Path

from discord.ext import tasks


def utc_ts() -> int:
    return int(time.time())


class CleanupService:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.temp_dir = data_dir / "temp"
        self.guilds_dir = data_dir / "guilds"
        self.retention_days = int(__import__("os").getenv("TEMP_RETENTION_DAYS", "30"))
        self._task = None

    def start(self, bot) -> None:
        if self._task is not None:
            return

        @tasks.loop(hours=12)
        async def cleanup_loop() -> None:
            now = utc_ts()
            retention_seconds = self.retention_days * 86400

            for file in self.temp_dir.glob("*.json"):
                try:
                    if now - int(file.stat().st_mtime) > retention_seconds:
                        file.unlink(missing_ok=True)
                except Exception:
                    continue

            for file in self.guilds_dir.glob("*.json"):
                try:
                    data = json.loads(file.read_text(encoding="utf-8"))
                    usage = data.get("daily_usage", {})
                    fresh_usage = {}
                    for key, value in usage.items():
                        try:
                            date_part = key.split(":", 1)[0]
                            epoch = int(time.mktime(time.strptime(date_part, "%Y-%m-%d")))
                            if now - epoch <= retention_seconds:
                                fresh_usage[key] = value
                        except Exception:
                            continue
                    data["daily_usage"] = fresh_usage
                    file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception:
                    continue

        @cleanup_loop.before_loop
        async def before_cleanup() -> None:
            await bot.wait_until_ready()

        self._task = cleanup_loop
        self._task.start()
