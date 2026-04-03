import discord


def info_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    embed.set_footer(text="RA Translate • RA Corporation")
    return embed


def success_embed(title: str, text: str) -> discord.Embed:
    return info_embed(title, text)


def error_embed(text: str) -> discord.Embed:
    return info_embed("Erro", text)
