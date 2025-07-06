from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import json
import os
import asyncio

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
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
            [KeyboardButton(text="📥 Скачать ПО"), KeyboardButton(text="⌨️ Горячие клавиши")],
            [KeyboardButton(text="📚 FAQ по MacBook"), KeyboardButton(text="🛠 Обратиться за ремонтом")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard

@router.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.answer("👋 Привет! Выберите действие из меню ниже:", reply_markup=get_main_keyboard())

@router.message(lambda message: message.text.lower() == "активация гарантии")
async def handle_activation_button(message: types.Message):
    await message.answer("Введите номер вашей покупки для регистрации гарантии:")

@router.message(lambda message: message.text.lower() == "статус")
async def handle_status_button(message: types.Message):
    await check_status(message)

@router.message(lambda message: message.text == "📥 Скачать ПО")
async def download_software(message: types.Message):
    await message.answer("Вот ссылка на загрузку ПО:
https://drive.google.com/drive/folders/1DEJhKjVoX_Csh3OLn9tu28gqAXlnM9Nv?usp=share_link")

@router.message(lambda message: message.text == "⌨️ Горячие клавиши")
async def show_hotkeys(message: types.Message):
    text = (
        "⌨️ <b>Горячие клавиши Mac</b>

"
        "<b>1. Основные</b>
"
        "⌘Cmd + C / V / X — Копировать / Вставить / Вырезать
"
        "⌘Cmd + Z / Shift + Z — Отмена / Вернуть
"
        "⌘Cmd + A / F / P / S — Выделить всё / Поиск / Печать / Сохранить

"
        "<b>2. Работа с текстом</b>
"
        "⌘Cmd + B / I / U — Жирный / Курсив / Подчёркнутый
"
        "⌥Option + ←/→ — Перемещение по словам
"
        "⌥Option + Delete — Удалить слово
"
        "Fn + Delete — Удалить вперёд

"
        "<b>3. Окна и вкладки</b>
"
        "⌘Cmd + W / T — Закрыть / Новая вкладка
"
        "⌘Cmd + H / Tab / ~ — Скрыть / Переключение окон

"
        "<b>4. Скриншоты</b>
"
        "⌘Cmd + Shift + 3 / 4 / 5 — Скриншоты и запись экрана

"
        "<b>5. Finder</b>
"
        "⌘Cmd + N — Новое окно
"
        "⌘Cmd + Shift + N — Новая папка
"
        "⌘Cmd + Delete — В корзину

"
        "<b>6. Системные</b>
"
        "⌘Cmd + Space — Spotlight
"
        "⌥Option + ⌘Cmd + Esc — Принудительное закрытие

"
        "<b>7. Продвинутые</b>
"
        "⌘Cmd + Option + D — Скрыть/показать Dock
"
        "Control + ⌘Cmd + D — Определение слова
"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(lambda message: message.text == "📚 FAQ по MacBook")
async def send_faq(message: types.Message):
    await message.answer(
        "📚 Ознакомьтесь с официальным руководством пользователя Mac от Apple:
"
        "🔗 <a href='https://support.apple.com/ru-ru/mac'>Официальное руководство Apple</a>",
        parse_mode="HTML"
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
        f"✅ Гарантия на покупку №{purchase_id} зарегистрирована.
"
        f"📅 Срок действия до: {expire_date}.

"
        f"Примеры гарантийных случаев:
"
        f"— Не включается
— Не заряжается
— Проблемы с экраном

"
        f"❗ Повреждения из-за воды, падений или вмешательства не покрываются гарантией.
"
        f"Подробности — у продавца.

"
        f"💡 Канал с новостями и скидками: @apoturaev"
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
            f"📦 Покупка №{warranty['purchase_id']}
"
            f"✅ Гарантия активна до {warranty['expires_at']} (ещё {days_left} дн.)"
        )
    else:
        await message.answer(
            f"⚠️ Гарантия на покупку №{warranty['purchase_id']} истекла {warranty['expires_at']}."
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
