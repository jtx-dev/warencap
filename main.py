import discord
from discord.ext import commands
from spanlp.palabrota import Palabrota
import os
import webserver
import asyncio

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TIEMPO_MUTE = 180
MAX_ADVERTENCIAS = 3  # Define el número máximo de advertencias antes del muteo

advertencias = {}
muteados = {}
palabrota = Palabrota(censor_char="*", exclude={"weon", "mano"})
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='w:', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

async def aplicar_sancion(usuario: discord.Member):
    usuario_id = usuario.id
    advertencias[usuario_id] = advertencias.get(usuario_id, 0) + 1
    await usuario.send(f"¡Advertencia! Por favor, evita usar lenguaje inapropiado. Llevas {advertencias[usuario_id]} advertencias.")
    if advertencias[usuario_id] >= MAX_ADVERTENCIAS and usuario_id not in muteados:
        await mutear(usuario)

async def mutear(usuario: discord.Member):
    usuario_id = usuario.id
    muteados[usuario_id] = True
    rol_mute = discord.utils.get(usuario.guild.roles, name="Muted")

    if rol_mute:
        await usuario.add_roles(rol_mute, reason=f"Alcanzó el límite de {MAX_ADVERTENCIAS} advertencias por malas palabras.")
        await usuario.send(f"Has sido muteado temporalmente por usar lenguaje inapropiado. Se te desmuteará en {TIEMPO_MUTE} segundos.")
        await asyncio.sleep(TIEMPO_MUTE)
        await desmutear(usuario)
    else:
        await usuario.send("No se encontró el rol 'Muted' en este servidor. No se pudo aplicar el muteo.")
        muteados.pop(usuario_id, None)

async def desmutear(usuario: discord.Member):
    usuario_id = usuario.id
    if usuario_id in muteados:
        muteados.pop(usuario_id, None)
        rol_mute = discord.utils.get(usuario.guild.roles, name="Muted")
        if rol_mute:
            await usuario.remove_roles(rol_mute, reason="Fin del tiempo de muteo.")
            await usuario.send("Se te ha desmuteado.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if palabrota.contains_palabrota(message.content):
        censored_message = palabrota.censor(message.content)
        try:
            await message.delete()
            await message.channel.send(f"Mensaje de {message.author.mention} censurado: `{censored_message}`")
            await aplicar_sancion(message.author)
        except discord.errors.NotFound:
            print(f"Error: No se encontró el mensaje para eliminar en {message.channel.id}")
        except discord.errors.Forbidden:
            print(f"Error: El bot no tiene permisos para eliminar mensajes en {message.channel.id}")

    await bot.process_commands(message)

webserver.keep_alive()
bot.run(DISCORD_TOKEN)
