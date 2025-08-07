import discord
import aiosqlite
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from utils.database_handler import setup_database

# Load environment variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Setup logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Define bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Called when the bot is ready and online."""
    print(f"We are Ready to go, {bot.user.name}")
    
    # Connect to the database and set up the table
    try:
        bot.db = await aiosqlite.connect('Main.db')
        await setup_database(bot.db) # <-- Add this line
        print("Successfully connected to database and verified table.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")

    # Load cogs
    # Make sure to add your new cog to the list of cogs to load
    cogs_to_load = ['cogs.start_cog']
    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f"Successfully loaded '{cog}'.")
        except Exception as e:
            print(f"Failed to load cog '{cog}'. Error: {e}")
    
    print(f"We are Ready to go, {bot.user.name}")


# Run the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)