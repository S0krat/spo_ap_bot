from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

TOKEN_API = "6209644592:AAEkRoaDzFfFa1F6OxfoWmCjhhAlCkb-dxU"
HELP_COMMAND = """ 🤡<b>КОМАНДЫ БОТА</b>🤡
<b>Тесты</b> - <em>Тесты</em>
<b>История команды</b> - <em>История команды</em>
<b>Конспекты</b> - <em>Конспекты</em>
<b>Дайджест</b> - <em>Дайджест</em>"""

f = open('history.txt', 'r', encoding='UTF-8')
history = f.read()
f.close()
f = open('digest.txt', 'r', encoding='UTF-8')
digest = f.read()
f.close()

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
tests_key = KeyboardButton("Тесты")
history_key = KeyboardButton("История команды")
notes_key = KeyboardButton("Конспекты")
digest_key = KeyboardButton("Дайджест")
kb.add(tests_key).insert(history_key).add(notes_key).insert(digest_key)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text="Привет! Я бот...\nНапиши 🥵 /help 🥵 для вывода всех команд.",
                           reply_markup=kb)
    await message.delete()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer(text=HELP_COMMAND, parse_mode="HTML")


@dp.message_handler(commands=['sticker'])
async def sticker_command(message: types.Message):
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker="CAACAgIAAxkBAAEH9IZj_3URiPgO1XGM3J_U7DHziqpJGgACEyIAAoaSSUumfyCbHPyBqS4E")


@dp.message_handler()
async def unclear_command(message: types.Message):
    if message.text == "Тесты":
        await message.answer(text="Я пока что не могу давать тебе тесты 🥺")
    elif message.text == "История команды":
        await message.answer(text=history)
    elif message.text == "Конспекты":
        await message.answer(text="Я пока что не могу выдавать конспекты 🥺")
    elif message.text == "Дайджест":
        await message.answer(text=digest)
    else:
        await message.answer(text="Я не понимаю этого сообщения 🥺")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
