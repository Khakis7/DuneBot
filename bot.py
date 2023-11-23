import discord
import os
import json
import logging
import aiosqlite
import typing
import functools
import asyncio

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv

from Modules import abcModule, DraftModule, RankedModule, RegisterModule, ReportModule, VotingModule, UtilityModule, BanModule

from database import DatabaseManager

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

intents = discord.Intents.default()
intents.message_content = True

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

ACTIVE_MODULE = [DraftModule, RankedModule, ReportModule, VotingModule, UtilityModule, RegisterModule]

# Typing
COMMAND_T = Callable[[List[str]], Awaitable[None]]

class DiscordBot(nextcord.Client):
    def __init__(self) -> None:
        super().__init__(allowed_mentions=nextcord.AllowedMentions(everyone=False), intents=nextcord.Intents.all())

        self.logger = logger
        self.config = config
        self.logger.info('Initialization Complete')\

    @property
    def session(self) -> AsyncSession:
        return Session()

    # async def setup_hook(self) -> None:
    #     await self.init_db()
    #     self.database = DatabaseManager(
    #         connection=await aiosqlite.connect(
    #             f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
    #         )
    #     )
    #     self.logger.info('Setup Hook Complete - Database Initialized')
    
    # async def init_db(self) -> None:
    #     async with aiosqlite.connect(
    #         f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
    #     ) as db:
    #         with open(
    #             f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
    #         ) as file:
    #             await db.executescript(file.read())
    #         await db.commit()

    async def load_modules(self):
        logger.info("Loading modules ...")
        for moduleClass in ACTIVE_MODULE:
            logger.info(f"Loading module: {moduleClass.__name__}")
            module = moduleClass(client=self)
            self.modules.append(module)
            asyncio.create_task(module.on_ready())
            self.commands.update(module.commands)
            for k, v in module.events.items():
                self.event[k] = self.event.get(k, []) + v

    def get_module(self, module_cls):
        for module in self.modules:
            if isinstance(module, module_cls):
                return module
        return None

    async def on_message(self, message: discord.Message) -> None:
        """
        The code in this event is executed every time someone sends a message, with or without the prefix

        :param message: The message that was sent.
        """
        if message.author == self.user or message.author.bot:
            return
        
        await self.process_command(message)

    @to_thread
    async def process_command(self, message):
        try:
            # Command List!
            if message.content.startswith('.register'):
                user, bot_message = await register_user(message, self.database)

                self.logger.info(bot_message)
                await message.channel.send(bot_message)
                return
            
            if message.content.startswith('.report'):
                player_results, bot_message = await report_match(message, self.database)

                await message.channel.send(bot_message)
                return
        except Exception as e:
            await message.channel.send(
                f"An unexcepted exception occured:```diff\n-[ERROR]\n{traceback.format_exc()}```")

load_dotenv()

bot = DiscordBot()
bot.run(os.getenv("TOKEN"))
