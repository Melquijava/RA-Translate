from discord import app_commands
from discord.ext import commands

from utils.formatters import success_embed, error_embed


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sobre", description="Mostra informações sobre o bot.")
    async def sobre(self, interaction):
        text = (
            "**RA Translate**\n"
            "Bot de tradução, correção e aprendizado de inglês para Discord.\n\n"
            "**Desenvolvido por:** RA Corporation\n"
            "**Recursos:** tradução privada, tradução pública, correção, explicação, treino e conversa em inglês."
        )
        await interaction.response.send_message(embed=success_embed("Sobre", text), ephemeral=True)

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction, error):
        self.bot.logger.exception("Erro global em slash command: %s", error)
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=error_embed("Ocorreu um erro inesperado ao executar o comando."), ephemeral=True)
            else:
                await interaction.response.send_message(embed=error_embed("Ocorreu um erro inesperado ao executar o comando."), ephemeral=True)
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
