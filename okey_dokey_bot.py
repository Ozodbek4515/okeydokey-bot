import os
from aiogram import Bot, Dispatcher, executor, types

# Telegram tokenni environment variable orqali olish
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Bot va dispatcher yaratish
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Salom! Fast food botga xush kelibsiz!")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Siz yubordingiz: " + message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)