from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from datetime import datetime, timedelta
import json
import os
import asyncio

API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

WARRANTY_FILE = "warranties.json"

if not os.path.exists(WARRANTY_FILE):
    with open(WARRANTY_FILE, "w") as f:
        json.dump({}, f)

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Активация гарантии"), KeyboardButton(text="Статус")],
            [KeyboardButton(text="📅 Скачать ПО"), KeyboardButton(text="⌨️ Горячие клавиши")],
            [KeyboardButton(text="📚 FAQ по MacBook"), KeyboardButton(text="🛠 Обратиться за ремонтом")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("👋 Привет! Выберите действие из меню ниже:", reply_markup=get_main_keyboard())

@router.message(lambda message: message.text.lower() == "активация гарантии")
async def handle_activation_button(message: types.Message):
    await message.answer("Введите номер вашей покупки для регистрации гарантии:")

@router.message(lambda message: message.text.lower() == "статус")
async def handle_status_button(message: types.Message):
    await check_status(message)

@router.message(lambda message: message.text == "📅 Скачать ПО")
async def download_software(message: types.Message):
    await message.answer("Вот ссылка на загрузку ПО:\nhttps://drive.google.com/drive/folders/1DEJhKjVoX_Csh3OLn9tu28gqAXlnM9Nv?usp=share_link")

@router.message(lambda message: message.text == "⌨️ Горячие клавиши")
async def show_hotkeys(message: types.Message):
    text = (
        "⌨️ <b>Горячие клавиши Mac</b>\n"
        "<b>1. Основные</b>\n"
        "⌘Cmd + C / V / X — Копировать / Вставить / Вырезать\n"
        "⌘Cmd + Z / Shift + Z — Отмена / Вернуть\n"
        "⌘Cmd + A / F / P / S — Выделить всё / Поиск / Печать / Сохранить\n"
        "<b>2. Работа с текстом</b>\n"
        "⌘Cmd + B / I / U — Жирный / Курсив / Подчёркнутый\n"
        "⌥Option + ←/→ — Перемещение по словам\n"
        "⌥Option + Delete — Удалить слово\n"
        "Fn + Delete — Удалить вперёд\n"
        "<b>3. Окна и вкладки</b>\n"
        "⌘Cmd + W / T — Закрыть / Новая вкладка\n"
        "⌘Cmd + H / Tab / ~ — Скрыть / Переключение окон\n"
        "<b>4. Скриншоты</b>\n"
        "⌘Cmd + Shift + 3 / 4 / 5 — Скриншоты и запись экрана\n"
        "<b>5. Finder</b>\n"
        "⌘Cmd + N — Новое окно\n"
        "⌘Cmd + Shift + N — Новая папка\n"
        "⌘Cmd + Delete — В корзину\n"
        "<b>6. Системные</b>\n"
        "⌘Cmd + Space — Spotlight\n"
        "⌥Option + ⌘Cmd + Esc — Принудительное закрытие\n"
        "<b>7. Продвинутые</b>\n"
        "⌘Cmd + Option + D — Скрыть/показать Dock\n"
        "Control + ⌘Cmd + D — Определение слова"
    )
    await message.answer(text)

@router.message(lambda message: message.text == "📚 FAQ по MacBook")
async def send_faq(message: types.Message):
    await message.answer(
        "📚 Ознакомьтесь с официальным руководством пользователя Mac от Apple:\n"
        "🔗 <a href='https://support.apple.com/ru-ru/mac'>Официальное руководство Apple</a>"
    )

@router.message(lambda message: message.text == "🛠 Обратиться за ремонтом")
async def contact_for_repair(message: types.Message):
    await message.answer("🛠 По вопросам ремонта пишите сюда: @AntonPotur")

@router.message(lambda message: message.text.isdigit())
async def register_warranty(message: types.Message):
    user_id = str(message.from_user.id)
    purchase_id = message.text
    expire_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    with open(WARRANTY_FILE, "r+") as f:
        data = json.load(f)
        data[user_id] = {
            "purchase_id": purchase_id,
            "registered_at": datetime.now().strftime("%Y-%m-%d"),
            "expires_at": expire_date
        }
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

    await message.answer(
        f"✅ Гарантия на покупку №{purchase_id} зарегистрирована.\n"
        f"📅 Срок действия до: {expire_date}.\n"
        f"Примеры гарантийных случаев:\n"
       f"— 1. Аппаратные дефекты💻\n\n* Не работает клавиатура или тачпад.\n* Перегрев и внезапное выключение из-за брака системы охлаждения.\n* Неисправность USB-портов или разъёма зарядки.\n* Нестабильная работа материнской платы (ноутбук не включается).\n\n— 2. Проблемы с батареей🪫\n\n* Быстрая разрядка (например, за 30 минут).\n* Батарея не заряжается или вздулась.\n\n— Не гарантийные случаи❌\n\n* Повреждения из-за удара, воды или неправильного использования.\n* Проблемы из-за самостоятельного ремонта или установки неоригинальных деталей.\n\n"
        f"Подробности — у продавца.\n"
        f"💡Присоединяйтесь к нашему каналу! Делимся увлекательными tech-новостями и топовыми скидками на гаджеты❤️: @apoturaev"
    )

async def check_status(message: types.Message):
    user_id = str(message.from_user.id)

    try:
        with open(WARRANTY_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        await message.answer("❗ У вас пока нет зарегистрированной гарантии.")
        return

    if user_id not in data:
        await message.answer("❗ У вас пока нет зарегистрированной гарантии.")
        return

    warranty = data[user_id]
    expires = datetime.strptime(warranty["expires_at"], "%Y-%m-%d")
    now = datetime.now()

    if now <= expires:
        days_left = (expires - now).days
        await message.answer(
            f"📦 Покупка №{warranty['purchase_id']}\n"
            f"✅ Гарантия активна до {warranty['expires_at']} (ещё {days_left} дн.)"
        )
    else:
        await message.answer(
            f"⚠️ Гарантия на покупку №{warranty['purchase_id']} истекла {warranty['expires_at']}."
        )

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=PORT)
