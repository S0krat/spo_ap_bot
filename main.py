from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import json

with open("config.json", 'r') as cfg:
    config = json.loads(cfg.read())

with open('txtfiles/history.txt', 'r', encoding='UTF-8') as file:
    history = file.read()

with open('txtfiles/diegest.txt', 'r', encoding='UTF-8') as file:
    digest = file.read()

bot = Bot(config['TOKEN_API'])
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
                           text="Привет! Я бот...\nИспользуй клавиатуру для взаимодействия со мной.",
                           reply_markup=kb)
    await message.delete()


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
