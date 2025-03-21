import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER
from aiogram.types import ChatMemberUpdated, Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения (для локального тестирования)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # На Koyeb dotenv не нужен

# Инициализация бота
API_TOKEN = os.getenv("BOT_TOKEN")  # Изменил на BOT_TOKEN для стандартизации
if not API_TOKEN:
    logger.error("BOT_TOKEN не задан в переменных окружения")
    raise ValueError("BOT_TOKEN не задан")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_name = message.from_user.first_name
    logger.info(f"Пользователь {user_name} вызвал команду /start в чате {message.chat.id}")
    await message.answer(f"Привет, {user_name}! Я бот, который приветствует новых участников и сообщает об уходе из группы.")

# Обработчик для новых участников
@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def on_user_join(update: ChatMemberUpdated):
    if update.new_chat_member.status == "member":
        user_name = update.new_chat_member.user.first_name
        logger.info(f"Новый участник {user_name}加入 в чат {update.chat.id}")
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"Привет, {user_name}! Добро пожаловать в группу!"
        )

# Обработчик для покидания группы
@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT | KICKED))
async def on_user_leave(update: ChatMemberUpdated):
    if update.new_chat_member.status in ["left", "kicked"]:
        user_name = update.new_chat_member.user.first_name
        logger.info(f"Участник {user_name} покинул чат {update.chat.id}")
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"{user_name} покинул группу."
        )

# Настройка вебхука при запуске
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    webhook_url = f"https://{os.getenv('KOYEB_PUBLIC_DOMAIN')}/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"Вебхук установлен на {webhook_url}")

# Удаление вебхука при завершении работы
async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.delete_webhook()
    logger.info("Вебхук удален, бот остановлен")

# Обработчик для проверки здоровья (health check)
async def health_check(request):
    return web.Response(text="OK", status=200)

# Запуск бота с вебхуком
if __name__ == "__main__":
    # Создаем приложение aiohttp
    app = web.Application()
    
    # Добавляем маршрут для проверки здоровья
    app.router.add_get("/health", health_check)
    
    # Настраиваем обработчик вебхуков для aiogram
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    # Добавляем функции on_startup и on_shutdown
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # Запускаем приложение
    web.run_app(app, host="0.0.0.0", port=int(os.getenv('PORT', 8080)))