from discord import app_commands
from discord.ext import commands

from utils.checks import validate_interaction
from utils.formatters import success_embed, error_embed


class LearningCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="corrigir", description="Corrige uma frase em inglês e explica em português.")
    @app_commands.describe(texto="Frase em inglês")
    async def corrigir(self, interaction, texto: str):
        await interaction.response.defer(ephemeral=True)
        valid, result = await validate_interaction(self.bot, interaction, texto)
        if not valid:
            await interaction.followup.send(embed=error_embed(result), ephemeral=True)
            return

        output = await self.bot.openai_service.correct_english(result)
        await interaction.followup.send(embed=success_embed("Correção", output), ephemeral=True)

    @app_commands.command(name="explicar", description="Explica a estrutura e vocabulário da frase.")
    @app_commands.describe(texto="Texto em português ou inglês")
    async def explicar(self, interaction, texto: str):
        await interaction.response.defer(ephemeral=True)
        valid, result = await validate_interaction(self.bot, interaction, texto)
        if not valid:
            await interaction.followup.send(embed=error_embed(result), ephemeral=True)
            return

        output = await self.bot.openai_service.explain_text(result)
        await interaction.followup.send(embed=success_embed("Explicação", output), ephemeral=True)

    @app_commands.command(name="chat_en", description="Converse em inglês com o bot.")
    @app_commands.describe(mensagem="Mensagem em inglês")
    async def chat_en(self, interaction, mensagem: str):
        await interaction.response.defer(ephemeral=True)
        valid, result = await validate_interaction(self.bot, interaction, mensagem)
        if not valid:
            await interaction.followup.send(embed=error_embed(result), ephemeral=True)
            return

        output = await self.bot.openai_service.chat_en(result)
        await interaction.followup.send(embed=success_embed("English Chat", output), ephemeral=True)

    @app_commands.command(name="chat_pt", description="Pergunte em português sobre inglês.")
    @app_commands.describe(pergunta="Pergunta sobre inglês")
    async def chat_pt(self, interaction, pergunta: str):
        await interaction.response.defer(ephemeral=True)
        valid, result = await validate_interaction(self.bot, interaction, pergunta)
        if not valid:
            await interaction.followup.send(embed=error_embed(result), ephemeral=True)
            return

        output = await self.bot.openai_service.chat_pt(result)
        await interaction.followup.send(embed=success_embed("Professor", output), ephemeral=True)

    @app_commands.command(name="treinar", description="Gera um mini exercício de inglês.")
    @app_commands.describe(modo="Ex: vocabulário, gramática, conversação, programação")
    async def treinar(self, interaction, modo: str):
        await interaction.response.defer(ephemeral=True)
        valid, result = await validate_interaction(self.bot, interaction, modo)
        if not valid:
            await interaction.followup.send(embed=error_embed(result), ephemeral=True)
            return

        cfg = await self.bot.config_service.get_guild_config(interaction.guild.id)
        if not cfg.get("learning_enabled", True):
            await interaction.followup.send(embed=error_embed("Os comandos de aprendizado estão desativados neste servidor."), ephemeral=True)
            return

        output = await self.bot.openai_service.training(result)
        await interaction.followup.send(embed=success_embed("Treino", output), ephemeral=True)


async def setup(bot):
    await bot.add_cog(LearningCog(bot))
