#ADMIN_ID=806342686
import asyncio
from aiogram import Bot, Dispatcher
from config_reader import config
import logging
import handlers
import sqlite3
from initdb import init_db
from handlers import user_commands, bot_messages

# Initialize bot and dispatcher
bot = Bot(config.bot_token.get_secret_value())
dp = Dispatcher()

# Initialize database
init_db()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Include routers
    dp.include_routers(
        user_commands,
        bot_messages,
    )
    
    # Start polling
    logger.info('Starting bot...')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
        