import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

API_TOKEN = '8034025979:AAHeoS5yOGe-1pqTgDIXQSxxxn0JCqUap90'
ADMIN_ID = 7485152383

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- States ---
class OrderFood(StatesGroup):
    choosing_language = State()
    choosing_food = State()
    getting_location = State()
    getting_phone = State()

# --- Language Buttons ---
language_kb = ReplyKeyboardMarkup(resize_keyboard=True)
language_kb.add("O'zbekcha 🇺🇿", "Русский 🇷🇺")

# --- Food Menu Buttons ---
menu_kb_uz = ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb_uz.add("🌯 Lavash", "🍔 Burger", "🥤 Ichimliklar", "✅ Buyurtma berish")

menu_kb_ru = ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb_ru.add("🌯 Лаваш", "🍔 Бургер", "🥤 Напитки", "✅ Оформить заказ")

# --- Location & Contact ---
location_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
location_kb.add(KeyboardButton("📍 Lokatsiyani yuborish", request_location=True))

phone_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
phone_kb.add(KeyboardButton("📞 Raqamni yuborish", request_contact=True))

# --- Handlers ---
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("Tilni tanlang / Выберите язык", reply_markup=language_kb)
    await OrderFood.choosing_language.set()

@dp.message_handler(state=OrderFood.choosing_language)
async def choose_language(message: types.Message, state: FSMContext):
    if message.text == "O'zbekcha 🇺🇿":
        await state.update_data(language='uz')
        await message.answer("🍽 Okey Dokey menyusiga xush kelibsiz!", reply_markup=menu_kb_uz)
    elif message.text == "Русский 🇷🇺":
        await state.update_data(language='ru')
        await message.answer("🍽 Добро пожаловать в меню Okey Dokey!", reply_markup=menu_kb_ru)
    await OrderFood.choosing_food.set()

@dp.message_handler(lambda msg: msg.text.startswith("✅"), state=OrderFood.choosing_food)
async def ask_location(message: types.Message):
    await message.answer("📍 Iltimos, lokatsiyangizni yuboring:", reply_markup=location_kb)
    await OrderFood.getting_location.set()

@dp.message_handler(content_types=types.ContentType.LOCATION, state=OrderFood.getting_location)
async def ask_phone(message: types.Message, state: FSMContext):
    await state.update_data(location=message.location)
    await message.answer("📞 Endi telefon raqamingizni yuboring:", reply_markup=phone_kb)
    await OrderFood.getting_phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=OrderFood.getting_phone)
async def send_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    location = data.get('location')
    language = data.get('language')

    order_text = f"📦 Yangi buyurtma!\n\n"
    order_text += f"🌍 Lokatsiya: https://maps.google.com/?q={location.latitude},{location.longitude}\n"
    order_text += f"📞 Telefon: {message.contact.phone_number}\n"
    order_text += f"🌐 Til: {'O‘zbekcha' if language == 'uz' else 'Русский'}"

    await bot.send_message(chat_id=ADMIN_ID, text=order_text)
    await message.answer("✅ Buyurtmangiz qabul qilindi! Tez orada bog‘lanamiz.", reply_markup=ReplyKeyboardRemove())
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
