from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import json
import random
from start_bot import bot, config, history, digest
from database.sqlite_db import check_member, add_new_member


class UserStatesGroup(StatesGroup):
    get_name = State()
    get_file_number = State()
    get_test_number = State()
    get_test_answer = State()


async def start_command(message: types.Message):
    if status := check_member(message.from_user.id):
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        tests_key = KeyboardButton("Тесты")
        history_key = KeyboardButton("История команды")
        notes_key = KeyboardButton("Конспекты")
        digest_key = KeyboardButton("Дайджест")
        kb.add(tests_key).insert(history_key).add(notes_key).insert(digest_key)
        if status[0]:
            await bot.send_message(chat_id=message.chat.id,
                                   text="Ты администратор данного бота!\nТебе доступны команды:\n"
                                        "/create - Добавить новый файл в бота\n/delete - удалить файл из бота",
                                   reply_markup=kb)
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text="Привет! Я бот...\nИспользуй клавиатуру для взаимодействия со мной.",
                                   reply_markup=kb)
    else:
        await message.answer("Привет! Я бот... \nНапиши, пожалуйста, своё имя и фамилию в следующем сообщении, "
                             "чтобы я внёс тебя в список участников!")
        await UserStatesGroup.get_name.set()


async def unclear_command(message: types.Message):  # Обработчик любых сообщений без состояния
    if message.text == "Тесты":
        with open("json/tests.json", 'r', encoding='UTF-8') as tests_json:
            tests = json.loads(tests_json.read()).keys()
        if tests:
            ans = "На данный момент доступны тесты:\n"
            for counter, test in enumerate(tests):
                ans += f"{counter + 1}. " + test + ".\n"
            ans += "Чтобы выбрать тест для прохождения, напиши порядковый номер теста.\n" \
                   "Если не хочешь проходить тест, напиши команду /cancel"
            await UserStatesGroup.get_test_number.set()
            await message.answer(text=ans)
        else:
            await message.answer("Тестов пока что нет 🥺")
    elif message.text == "История команды":
        await message.answer(text=history)
    elif message.text == "Конспекты":
        with open("json/file_ids.json", 'r', encoding='UTF-8') as files_json:
            files = json.loads(files_json.read()).keys()
        if files:
            cons = "Выбери конспект, который хочешь получить:\n"
            for counter, name in enumerate(files):
                cons += f"{counter + 1}. " + name + ".\n"
            cons += "Чтобы выбрать конспект, отправь число, соответствующее порядку конспекта в списке 😁"
            await UserStatesGroup.get_file_number.set()
            await message.answer(text=cons)
        else:
            await message.answer(text="Конспектов пока что нет 🥺")
    elif message.text == "Дайджест":
        await message.answer(text=digest)
    else:
        await message.answer(text="Я не понимаю этого сообщения 🥺")


async def cancel_command(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.answer("Вы отменили предыдущее действие!")


async def get_name(message: types.Message, state: FSMContext):
    add_new_member([message.from_user.id, message.text])
    await state.finish()


async def get_file_number(message: types.Message, state: FSMContext):  # конспекта у пользователя
    if message.text.isdigit():
        num = int(message.text)
        with open("json/file_ids.json", 'r', encoding='UTF-8') as files_json:
            file_ids = [*json.loads(files_json.read()).values()]
        if 0 < num <= len(file_ids):
            await bot.send_document(chat_id=message.chat.id, document=file_ids[num - 1])
            await state.finish()
        else:
            await message.answer("Конспекта с таким номером нет в списке...\nНапиши команду /cancel для отмены.")
    else:
        await message.answer("Ты ввёл не число!\nНапиши команду /cancel для отмены.")


async def get_test_number(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        num = int(message.text)
        with open("json/tests.json", 'r', encoding='UTF-8') as tests_json:
            tests = [*json.loads(tests_json.read()).values()]
        if 0 < num <= len(tests):
            async with state.proxy() as data:
                data['test'] = tests[num - 1]
                data['question'] = 0
                data['answer'] = ""
            await message.answer("Начинается тест. Чтобы ответить на вопрос теста:\n1. Если предоставлены варианты "
                                 "ответа, напишите порядковый номер ответа.\n2. Если варианты ответа не предоставлены, "
                                 "напишите ответ словом (словами).")
            await UserStatesGroup.next()
            await get_test_answer(message, state)
        else:
            await message.answer("Теста с таким номером нет в списке...\nНапиши команду /cancel для отмены.")
    else:
        await message.answer("Ты ввёл не число!\nНапиши команду /cancel для отмены.")


async def get_test_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['question'] != 0:
            if message.text == data['correct']:
                data['answer'] += '+'
            else:
                data['answer'] += '-'
            if data['question'] == len(data['test']):
                await message.answer(f"Тест завершён! Ваши результаты: {data['answer']}")
                await state.finish()
                await bot.send_message(config['ADMIN'][0], f"Пользователь {message.from_user.full_name} прошёл тест "
                                                           f"с результатами {data['answer']}")
                return
        question = list(data['test'].keys())[data['question']]
        options = data['test'][question]
        if type(options) == list:
            data['correct'] = options[0]
            random.shuffle(options)
            data['correct'] = str(options.index(data['correct']) + 1)
            for counter, option in enumerate(options):
                question += f"\n{counter + 1}. {option}"
        else:
            data['correct'] = options
        data['question'] += 1
    await message.answer(question)


def register_handlers_user(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start_command, commands=['start'])
    dispatcher.register_message_handler(unclear_command)
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')
    dispatcher.register_message_handler(get_name, state=UserStatesGroup.get_name)
    dispatcher.register_message_handler(get_file_number, state=UserStatesGroup.get_file_number)
    dispatcher.register_message_handler(get_test_number, state=UserStatesGroup.get_test_number)
    dispatcher.register_message_handler(get_test_answer, state=UserStatesGroup.get_test_answer)
