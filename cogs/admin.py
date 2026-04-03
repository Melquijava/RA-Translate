import discord
from discord import app_commands
from discord.ext import commands

from utils.formatters import success_embed, error_embed


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="configurar_canal_ingles",
        description="Define o canal oficial de inglês do servidor."
    )
    @app_commands.describe(canal="Canal de texto")
    @app_commands.checks.has_permissions(administrator=True)
    async def configurar_canal_ingles(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):
        await interaction.response.defer(ephemeral=True)

        cfg = await self.bot.config_service.get_guild_config(interaction.guild.id)
        cfg["english_channel_id"] = canal.id
        await self.bot.config_service.save_guild_config(interaction.guild.id, cfg)

        await interaction.followup.send(
            embed=success_embed(
                "Configuração salva",
                f"Canal de inglês definido como {canal.mention}."
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="configurar_limite_diario",
        description="Define o limite diário de usos por usuário neste servidor."
    )
    @app_commands.describe(
        quantidade="Use 0 para ilimitado, ou qualquer número acima de 0"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def configurar_limite_diario(
        self,
        interaction: discord.Interaction,
        quantidade: app_commands.Range[int, 0, 10000]
    ):
        await interaction.response.defer(ephemeral=True)

        cfg = await self.bot.config_service.get_guild_config(interaction.guild.id)
        cfg["daily_limit"] = int(quantidade)
        await self.bot.config_service.save_guild_config(interaction.guild.id, cfg)

        if quantidade == 0:
            mensagem = "O limite diário foi definido como **ilimitado** neste servidor."
        else:
            mensagem = f"O limite diário foi definido como **{quantidade} usos por usuário**."

        await interaction.followup.send(
            embed=success_embed("Configuração salva", mensagem),
            ephemeral=True,
        )

    @app_commands.command(
        name="ver_config",
        description="Mostra as configurações atuais do RA Translate."
    )
    async def ver_config(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        cfg = await self.bot.config_service.get_guild_config(interaction.guild.id)

        english_channel = "Não configurado"
        if cfg.get("english_channel_id"):
            channel = interaction.guild.get_channel(cfg["english_channel_id"])
            english_channel = channel.mention if channel else f"ID {cfg['english_channel_id']}"

        allowed_channels = []
        for cid in cfg.get("allowed_public_channels", []):
            ch = interaction.guild.get_channel(cid)
            allowed_channels.append(ch.mention if ch else f"ID {cid}")

        limite = int(cfg.get("daily_limit", 20))
        limite_texto = "Ilimitado" if limite <= 0 else f"{limite} usos por usuário"

        description = (
            f"**Canal de inglês:** {english_channel}\n"
            f"**Canais públicos extras:** {', '.join(allowed_channels) if allowed_channels else 'Nenhum'}\n"
            f"**Idioma padrão:** {cfg.get('default_language', 'pt-BR')}\n"
            f"**Respostas públicas:** {'Ativado' if cfg.get('public_enabled', True) else 'Desativado'}\n"
            f"**Modo aprendizado:** {'Ativado' if cfg.get('learning_enabled', True) else 'Desativado'}\n"
            f"**Cooldown:** {cfg.get('cooldown_seconds', 8)}s\n"
            f"**Limite diário:** {limite_texto}"
        )

        await interaction.followup.send(
            embed=success_embed("Configurações", description),
            ephemeral=True
        )

    @configurar_canal_ingles.error
    @configurar_limite_diario.error
    async def admin_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            mensagem = "Você precisa ser administrador para usar este comando."
        else:
            mensagem = "Ocorreu um erro inesperado."

        if interaction.response.is_done():
            await interaction.followup.send(
                embed=error_embed(mensagem),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=error_embed(mensagem),
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(AdminCog(bot))