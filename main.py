
import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
BASE_URL = os.environ["RENDER_EXTERNAL_URL"].rstrip("/")
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", "10000"))

if not WEBHOOK_SECRET or len(WEBHOOK_SECRET) < 32:
    raise RuntimeError("WEBHOOK_SECRET must be at least 32 characters")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Hello! Your Telegram bot is running on Render.\n"
        "Send /help to see available commands."
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help"
    )


async def health(request: web.Request):
    return web.json_response({"status": "ok"})


async def on_startup(app: web.Application):
    await bot.set_webhook(
        url=f"{BASE_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=False,
    )
    logger.info("Telegram webhook registered")


async def on_shutdown(app: web.Application):
    await bot.session.close()


def create_app():
    app = web.Application()
    app.router.add_get("/", health)

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    web.run_app(
        create_app(),
        host="0.0.0.0",
        port=PORT,
  )
  
