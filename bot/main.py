import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers import router as commands_router
from callback_queries import router as queries_router
from bot_states import router as states_router


commands = [
    types.BotCommand(command="/start", description="Вывести меню"),
]


async def main():
    bot = Bot(token=config.tg_token)
    await bot.set_my_commands(commands)
    dp = Dispatcher(bot=bot, storage=MemoryStorage())
    dp.include_router(commands_router)
    dp.include_router(queries_router)
    dp.include_router(states_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
