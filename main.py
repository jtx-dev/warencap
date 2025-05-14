import discord
from discord.ext import commands
from spanlp.palabrota import Palabrota
import os
import webserver
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

palabrota = Palabrota(censor_char="*", exclude="weon")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='w:', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == bot.user:
        return

    # Verificar si el mensaje contiene palabras inapropiadas
    if palabrota.contains_palabrota(message.content) == True:
        # Censurar el mensaje
        censored_message = palabrota.censor(message.content)

        # Eliminar el mensaje original
        try:
            await message.delete()
            # Enviar un mensaje censurado (opcional)
            await message.channel.send(f"Mensaje de {message.author.mention} censurado: `{censored_message}`")
            # O podrías enviar un mensaje más simple:
            # await message.channel.send(f"{message.author.mention}, tu mensaje contenía contenido inapropiado y ha sido censurado.")
        except discord.errors.NotFound:
            print(f"Error: No se encontró el mensaje para eliminar en {message.channel.id}")
        except discord.errors.Forbidden:
            print(f"Error: El bot no tiene permisos para eliminar mensajes en {message.channel.id}")

    # Procesar otros comandos del bot (si los hubiera)
    await bot.process_commands(message)
webserver.keep_alive()
bot.run(DISCORD_TOKEN)