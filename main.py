import discord
from discord.ext import commands
from utils.commands import setup_commands
from config import TOKEN

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    setup_commands(bot)

bot.run(TOKEN)
