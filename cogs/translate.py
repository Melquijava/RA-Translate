from discord import app_commands
from discord.ext import commands

from utils.checks import validate_interaction, check_public_channel
from utils.formatters import success_embed, error_embed


class TranslateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="traduzir", description="Traduz uma frase para inglês em resposta privada.")
    @app_commands.describe(texto="Texto em português")
    async def traduzir(self, interaction, texto: str):
        await interaction.response.defer(ephemeral=True)
        valid, result = await validate_interaction(self.bot, interaction, texto)
        if not valid:
            await interaction.followup.send(embed=error_embed(result), ephemeral=True)
            return

        output = await self.bot.openai_service.translate_private(result)
        await interaction.followup.send(embed=success_embed("Tradução", output), ephemeral=True)

    @app_commands.command(name="translate", description="Traduz e publica a frase em inglês no canal permitido.")
    @app_commands.describe(texto="Texto em português")
    async def translate(self, interaction, texto: str):
        await interaction.response.defer(ephemeral=True)
        valid, result = await validate_interaction(self.bot, interaction, texto)
        if not valid:
            await interaction.followup.send(embed=error_embed(result), ephemeral=True)
            return

        ok, message = await check_public_channel(self.bot, interaction)
        if not ok:
            await interaction.followup.send(embed=error_embed(message), ephemeral=True)
            return

        translated = await self.bot.openai_service.translate_public(result)
        await interaction.channel.send(f"{interaction.user.mention}: {translated}")
        await interaction.followup.send(embed=success_embed("Publicado", "Sua tradução foi enviada no canal."), ephemeral=True)


async def setup(bot):
    await bot.add_cog(TranslateCog(bot))
