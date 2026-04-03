import os
import logging
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from services.config_service import ConfigService
from services.cooldown_service import CooldownService
from services.openai_service import OpenAIService
from services.cleanup_service import CleanupService

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "ra_translate.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("ra_translate")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

if not DISCORD_TOKEN:
    raise RuntimeError("Defina DISCORD_TOKEN no arquivo .env")
if not OPENAI_API_KEY:
    raise RuntimeError("Defina OPENAI_API_KEY no arquivo .env")


class RATranslateBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.messages = True
        intents.message_content = True

        super().__init__(command_prefix="!", intents=intents)

        self.data_dir = DATA_DIR
        self.config_service = ConfigService(DATA_DIR)
        self.cooldown_service = CooldownService(DATA_DIR)
        self.openai_service = OpenAIService(OPENAI_API_KEY, OPENAI_MODEL)
        self.cleanup_service = CleanupService(DATA_DIR)
        self.logger = logger

    async def setup_hook(self) -> None:
        initial_extensions = [
            "cogs.translate",
            "cogs.learning",
            "cogs.admin",
            "cogs.utility",
        ]

        for extension in initial_extensions:
            await self.load_extension(extension)
            logger.info("Cog carregada: %s", extension)

        self.cleanup_service.start(self)
        await self.tree.sync()
        logger.info("Slash commands sincronizados.")

    async def on_ready(self) -> None:
        logger.info("Bot online como %s (%s)", self.user, self.user.id)


bot = RATranslateBot()
bot.run(DISCORD_TOKEN)
