from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import json

with open("config.json", 'r') as cfg:  # Открытие внешних файлов
    config = json.loads(cfg.read())

with open('txtfiles/history.txt', 'r', encoding='UTF-8') as file:
    history = file.read()

with open('txtfiles/diegest.txt', 'r', encoding='UTF-8') as file:
    digest = file.read()

storage = MemoryStorage()  # Создаём ячейку памяти для сохранения текущего состояния
bot = Bot(config['TOKEN_API'])
dp = Dispatcher(bot, storage=storage)

kb = ReplyKeyboardMarkup(resize_keyboard=True)  # Создаём начальную клавиатуру
tests_key = KeyboardButton("Тесты")
history_key = KeyboardButton("История команды")
notes_key = KeyboardButton("Конспекты")
digest_key = KeyboardButton("Дайджест")
kb.add(tests_key).insert(history_key).add(notes_key).insert(digest_key)


class ProfileStatesGroup(StatesGroup):  # Класс, где хранятся все состояния
    get_file_number = State()
    get_file_from_admin = State()
    get_file_name_from_admin = State()
    get_del_number_from_admin = State()


@dp.message_handler(commands=['start'])  # Обработчик команды /start
async def start_command(message: types.Message):
    if message.from_user.id in config['ADMIN']:
        kb.add(KeyboardButton("Добавить новый файл"))
        kb.insert(KeyboardButton("Удалить файл"))
        await message.answer("Ты администратор данного бота 😎")
    await bot.send_message(chat_id=message.chat.id,
                           text="Привет! Я бот...\nИспользуй клавиатуру для взаимодействия со мной.",
                           reply_markup=kb)


@dp.message_handler()
async def unclear_command(message: types.Message):  # Обработчик любых сообщений без состояния
    if message.text == "Тесты":
        await message.answer(text="Я пока что не могу давать тебе тесты 🥺")
    elif message.text == "История команды":
        await message.answer(text=history)
    elif message.text == "Конспекты":
        with open("file_ids.json", 'r', encoding='UTF-8') as files_json:
            files = json.loads(files_json.read()).keys()
        if files:
            cons = "Выбери конспект, который хочешь получить:\n"
            for counter, name in enumerate(files):
                cons += f"{counter + 1}. " + name + ".\n"
            cons += "Чтобы выбрать конспект, отправь число, соответствующее порядку конспекта в списке 😁"
            await ProfileStatesGroup.get_file_number.set()
            await message.answer(text=cons)
        else:
            await message.answer(text="Конспектов пока что нет 🥺")
    elif message.text == "Дайджест":
        await message.answer(text=digest)
    elif message.text == "Добавить новый файл":
        if message.from_user.id in config['ADMIN']:
            with open("file_ids.json", 'r', encoding='UTF-8') as files_json:
                files = json.loads(files_json.read()).keys()
            cons = "В данный момент в боте находятся файлы:\n"
            for counter, name in enumerate(files):
                cons += f"{counter + 1}. " + name + ".\n"
            await message.answer(cons)
            await message.answer("Кидай файл сюда!")
            await ProfileStatesGroup.get_file_from_admin.set()
        else:
            await message.answer("У тебя нет доступа к этому действию 😡")
    elif message.text == "Удалить файл":
        if message.from_user.id in config['ADMIN']:
            with open("file_ids.json", 'r', encoding='UTF-8') as files_json:
                files = json.loads(files_json.read()).keys()
            cons = "В данный момент в боте находятся файлы:\n"
            for counter, name in enumerate(files):
                cons += f"{counter + 1}. " + name + ".\n"
            await message.answer(cons)
            await message.answer("Напиши порядковый номер файла, который хочешь удалить.\n"
                                 "Если не хочешь ничего удалять напиши /cancel")
            await ProfileStatesGroup.get_del_number_from_admin.set()
    else:
        await message.answer(text="Я не понимаю этого сообщения 🥺")


@dp.message_handler(commands=['cancel'], state='*')  # Обработчик команды /cancel для выхода из состояния
async def cancel_command(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.answer("Вы отменили предыдущее действие!")


@dp.message_handler(content_types=['document'], state=ProfileStatesGroup.get_file_from_admin)
async def get_file_from_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['document'] = message.document.file_id
    await message.answer(
        "Прекрасно! Теперь напиши название этого файла, которое будет отображаться в списке файлов.")
    await ProfileStatesGroup.next()


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.get_file_from_admin)
async def gffa_exception(message: types.Message, state: FSMContext):
    await message.answer("Я жду от тебя файл, а не признание в любви!\n"
                         "Если хочешь отменить предыдущее действие напиши /cancel")


@dp.message_handler(state=ProfileStatesGroup.get_file_name_from_admin)
async def get_file_name_from_admin(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.TEXT:
        with open("file_ids.json", 'r', encoding='UTF-8') as files_json:
            files = json.loads(files_json.read())
        async with state.proxy() as data:
            files.update({message.text: data['document']})
        with open("file_ids.json", 'w', encoding='UTF-8') as files_json:
            json.dump(files, files_json, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))
        await message.answer(f"Ура! Новый файл с названием '{message.text}' успешно создан!")
        await state.finish()
    else:
        await message.answer("Я жду от тебя название файла!\nЕсли хочешь отменить создание файла, напиши /cancel")


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.get_del_number_from_admin)
async def get_del_number_from_admin(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        num = int(message.text)
        with open("file_ids.json", 'r', encoding='UTF-8') as files_json:
            files = json.loads(files_json.read())
        if 0 < num <= len(files):
            name = list(files.keys())[num - 1]
            files.pop(name)
            with open("file_ids.json", 'w', encoding='UTF-8') as files_json:
                json.dump(files, files_json, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))
            await message.answer(f"Конспект '{name}' успешно удалён!")
            await state.finish()
        else:
            await message.answer("Конспекта с таким номером нет в списке...\nНапиши команду /cancel для отмены.")
    else:
        await message.answer("Ты ввёл не число!\nНапиши команду \\cancel для отмены.")


@dp.message_handler(state=ProfileStatesGroup.get_file_number)  # Обработчик состояния получения номера
async def get_file_number(message: types.Message, state: FSMContext):  # конспекта у пользователя
    if message.text.isdigit():
        num = int(message.text)
        with open("file_ids.json", 'r', encoding='UTF-8') as files_json:
            file_ids = [*json.loads(files_json.read()).values()]
        if 0 < num <= len(file_ids):
            await bot.send_document(chat_id=message.chat.id, document=file_ids[num - 1])
            await state.finish()
        else:
            await message.answer("Конспекта с таким номером нет в списке...\nНапиши команду /cancel для отмены.")
    else:
        await message.answer("Ты ввёл не число!\nНапиши команду \\cancel для отмены.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
