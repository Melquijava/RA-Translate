from typing import Optional, Tuple
import time

import discord

from utils.constants import MAX_TEXT_LENGTH


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def validate_text(text: str) -> Tuple[bool, str]:
    text = normalize_text(text)

    if not text:
        return False, "O texto não pode estar vazio."

    if len(text) > MAX_TEXT_LENGTH:
        return False, f"O texto ultrapassa o limite de {MAX_TEXT_LENGTH} caracteres."

    if text.startswith("http://") or text.startswith("https://"):
        return False, "Envie uma frase ou pergunta, não apenas um link isolado."

    return True, text


async def validate_interaction(bot, interaction: discord.Interaction, text: str) -> Tuple[bool, Optional[str]]:
    if interaction.guild is None:
        return False, "Esse comando só pode ser usado dentro de um servidor."

    ok, cleaned = validate_text(text)
    if not ok:
        return False, cleaned

    cfg = await bot.config_service.get_guild_config(interaction.guild.id)

    cooldown_seconds = int(cfg.get("cooldown_seconds", 8))
    in_cooldown, remaining = await bot.cooldown_service.check_cooldown(
        interaction.guild.id,
        interaction.user.id,
        cooldown_seconds,
    )
    if in_cooldown:
        return False, f"Aguarde {remaining}s para usar outro comando."

    limit = int(cfg.get("daily_limit", 20))

    # 0 ou menor = ilimitado
    if limit > 0:
        usage = cfg.setdefault("daily_usage", {})
        today = time.strftime("%Y-%m-%d", time.gmtime())
        key = f"{today}:{interaction.user.id}"
        current = int(usage.get(key, 0))

        if current >= limit:
            return False, f"Você atingiu o limite diário de {limit} usos neste servidor."

        usage[key] = current + 1
        await bot.config_service.save_guild_config(interaction.guild.id, cfg)

    return True, cleaned


async def check_public_channel(bot, interaction: discord.Interaction) -> Tuple[bool, str]:
    if interaction.guild is None:
        return False, "Esse comando só pode ser usado dentro de um servidor."

    cfg = await bot.config_service.get_guild_config(interaction.guild.id)
    english_channel_id = cfg.get("english_channel_id")
    allowed_public_channels = set(cfg.get("allowed_public_channels", []))

    if not cfg.get("public_enabled", True):
        return False, "As respostas públicas estão desativadas neste servidor."

    current_channel_id = interaction.channel_id

    if english_channel_id and current_channel_id == english_channel_id:
        return True, "ok"

    if current_channel_id in allowed_public_channels:
        return True, "ok"

    return False, "Esse comando só pode ser usado no canal de inglês configurado."