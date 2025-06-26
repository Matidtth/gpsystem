import discord
from discord.ext import commands
import os
import asyncio
import json
from keep_alive import keep_alive
from bot_commands import BotCommands
from whitelist_system import WhitelistSystem
from reaction_logger import ReactionLogger
from warn_system import WarnSystem
from job_system import JobSystem
from rating_system import RatingSystem
from suggestion_system import SuggestionSystem


# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='pc!', intents=intents)

# Initialize systems
bot_commands = BotCommands(bot)
whitelist_system = WhitelistSystem(bot)
reaction_logger = ReactionLogger(bot)
warn_system = WarnSystem(bot)
job_system = JobSystem(bot)
rating_system = RatingSystem(bot)
suggestion_system = SuggestionSystem(bot)


@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión y está listo!')
    print(f'Bot ID: {bot.user.id}')

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Sincronizados {len(synced)} comandos slash')
    except Exception as e:
        print(f'Error sincronizando comandos: {e}')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Comando no encontrado",
            description=
            f"El comando que intentaste usar no existe. Usa `pc!help` para ver los comandos disponibles.",
            color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Argumento faltante",
            description=f"Te falta un argumento requerido: `{error.param}`",
            color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="❌ Error",
                              description=f"Ocurrió un error: {str(error)}",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
        print(f'Error no manejado: {error}')


@bot.command(name='ping')
async def ping(ctx):
    """Comando de prueba para verificar latencia"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!",
                          description=f"Latencia: {latency}ms",
                          color=discord.Color.green())
    await ctx.send(embed=embed)


@bot.command(name='ayuda')
async def help_command(ctx):
    """Muestra la lista de comandos disponibles organizados por categorías"""
    embed = discord.Embed(
        title="🤖 Comandos del Bot - Puro Chile RP",
        description="Lista completa de comandos organizados por categorías",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    # Sistema de Calificaciones
    embed.add_field(
        name="📊 Sistema de Calificaciones",
        value="⭐ `pc!calificar @staff [puntos] [motivo]` - Calificar staff (-5 a +5)\n"
              "📈 `pc!vercalificaciones [@staff]` - Ver calificaciones de staff\n"
              "🏆 `pc!topcalificaciones` - Ranking de mejor staff calificado",
        inline=False
    )
    
    # Sistema de Warns
    embed.add_field(
        name="⚠️ Sistema de Sanciones",
        value="🚨 `pc!sancionar @usuario [motivo]` - Agregar advertencia (Solo Staff)\n"
              "📋 `pc!verwarns @usuario` - Ver advertencias (Solo Staff)\n"
              "🗑️ `pc!removewarn @usuario [ID]` - Eliminar advertencia (Solo Staff)\n"
              "🔥 `pc!resetwarns @usuario` - Eliminar todas las advertencias (Solo Staff)",
        inline=False
    )
    
    # Otros Sistemas
    embed.add_field(
        name="🔧 Otros Sistemas",
        value="🚨 `pc!entorno` - Servicios de emergencia (Policía, Médicos, Mecánicos)\n"
              "📝 `pc!whitelist` - Crear canal privado para whitelist\n"
              "✅ `pc!confirmar` - Cuestionario formal de whitelist\n"
              "🔄 `pc!reset-whitelist @usuario` - Resetear whitelist (Solo Staff)\n"
              "💼 `pc!postular` - Postular a trabajos secundarios\n"
              "💡 `pc!sugerencia [texto]` - Enviar sugerencia comunitaria\n"
              "🏓 `pc!ping` - Verificar latencia del bot",
        inline=False
    )

    # Add protection systems info
    embed.add_field(name="🛡️ Sistemas de Protección Activos",
                    value="• **Sistema de Reacciones**: Registro completo de actividad\n• **Control de Acceso**: Comandos administrativos protegidos por roles",
                    inline=False)

    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
    embed.set_footer(text="Puro Chile RP - Bot de Servicios", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
    
    await ctx.send(embed=embed)

# Remove the default help command
bot.remove_command('help')


# Initialize data directories
async def init_data_directories():
    """Initialize data directories and files"""
    os.makedirs('data', exist_ok=True)

    # Initialize whitelist applications file
    if not os.path.exists('data/whitelist_applications.json'):
        with open('data/whitelist_applications.json', 'w') as f:
            json.dump([], f)

    # Initialize reaction logs file
    if not os.path.exists('data/reaction_logs.json'):
        with open('data/reaction_logs.json', 'w') as f:
            json.dump([], f)
    
    # Initialize suggestions file
    if not os.path.exists('data/suggestions.json'):
        with open('data/suggestions.json', 'w') as f:
            json.dump([], f)


async def main():
    """Main function to run the bot"""
    await init_data_directories()
    
    # Initialize rating system database
    await rating_system.init_database()

    # Start keep_alive server for 24/7 uptime
    keep_alive()

    # Get bot token from environment
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print(
            "❌ Error: DISCORD_BOT_TOKEN no encontrado en las variables de entorno"
        )
        return

    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Error: Token de bot inválido")
    except Exception as e:
        print(f"❌ Error iniciando el bot: {e}")


if __name__ == '__main__':
    asyncio.run(main())

