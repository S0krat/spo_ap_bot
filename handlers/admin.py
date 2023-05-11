from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import json
from start_bot import config, bot
from database.sqlite_db import get_user_ids, check_member


class AdminStatesGroup(StatesGroup):  # Класс, где хранятся все состояния
    get_file_from_admin = State()
    get_file_name_from_admin = State()
    get_del_number_from_admin = State()
    pic_or_text = State()


async def create_command(message: types.Message):
    if message.from_user.id in config['ADMIN']:
        with open("json/file_ids.json", 'r', encoding='UTF-8') as files_json:
            files = json.loads(files_json.read()).keys()
        cons = "В данный момент в боте находятся файлы:\n"
        for counter, name in enumerate(files):
            cons += f"{counter + 1}. " + name + ".\n"
        await message.answer(cons)
        await message.answer("Кидай файл сюда!")
        await AdminStatesGroup.get_file_from_admin.set()
    else:
        await message.answer("У тебя нет доступа к этому действию 😡")


async def delete_command(message: types.Message):
    if message.from_user.id in config['ADMIN']:
        with open("json/file_ids.json", 'r', encoding='UTF-8') as files_json:
            files = json.loads(files_json.read()).keys()
        cons = "В данный момент в боте находятся файлы:\n"
        for counter, name in enumerate(files):
            cons += f"{counter + 1}. " + name + ".\n"
        await message.answer(cons)
        await message.answer("Напиши порядковый номер файла, который хочешь удалить.\n"
                             "Если не хочешь ничего удалять напиши /cancel")
        await AdminStatesGroup.get_del_number_from_admin.set()
    else:
        await message.answer("У тебя нет доступа к этому действию 😡")


async def message_command(message: types.Message, state: FSMContext):
    if check_member(message.from_user.id)[0][0] == 1:
        mes = message.text[9:]
        if mes:
            await message.answer("Отправь картинку, если хочешь дополнить текст рассылки картинкой\n"
                                 "Отправь 'Нет', если хочешь отправить сообщение без картинки")
            await AdminStatesGroup.pic_or_text.set()
            async with state.proxy() as data:
                data['mes'] = mes
        else:
            await message.answer("Данная команда работает так:\n/message text\nПосле этого я спрошу у тебя, "
                                 "хочешь ли ты добавить картинку к тексту или нет")
    else:
        await message.answer("У тебя нет прав на это действие")


async def pic_message(message: types.Message, state: FSMContext):
    photo = message.photo[0].file_id
    async with state.proxy() as data:
        user_ids = get_user_ids()
        for user_id in user_ids:
            await bot.send_photo(chat_id=user_id[0], photo=photo, caption=data['mes'])
    await state.finish()


async def text_message(message: types.Message, state: FSMContext):
    if message.text.lower() == "нет":
        async with state.proxy() as data:
            await bot.send_message(message.chat.id, text=data['mes'])
        await state.finish()
    else:
        await message.answer("Отправь картинку, если хочешь дополнить текст рассылки картинкой\n"
                             "Отправь 'Нет', если хочешь отправить сообщение без картинки\n"
                             "Отправь '/cancel', если хочешь отменить процедуру рассылки.")


async def get_file_from_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['document'] = message.document.file_id
    await message.answer(
        "Прекрасно! Теперь напиши название этого файла, которое будет отображаться в списке файлов.")
    await AdminStatesGroup.next()


async def gffa_exception(message: types.Message, state: FSMContext):
    await message.answer("Я жду от тебя файл!\n"
                         "Если хочешь отменить предыдущее действие напиши /cancel")


async def get_file_name_from_admin(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.TEXT:
        with open("json/file_ids.json", 'r', encoding='UTF-8') as files_json:
            files = json.loads(files_json.read())
        async with state.proxy() as data:
            files.update({message.text: data['document']})
        with open("json/file_ids.json", 'w', encoding='UTF-8') as files_json:
            json.dump(files, files_json, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))
        await message.answer(f"Ура! Новый файл с названием '{message.text}' успешно создан!")
        await state.finish()
    else:
        await message.answer("Я жду от тебя название файла!\nЕсли хочешь отменить создание файла, напиши /cancel")


async def get_del_number_from_admin(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        num = int(message.text)
        with open("json/file_ids.json", 'r', encoding='UTF-8') as files_json:
            files = json.loads(files_json.read())
        if 0 < num <= len(files):
            name = list(files.keys())[num - 1]
            files.pop(name)
            with open("json/file_ids.json", 'w', encoding='UTF-8') as files_json:
                json.dump(files, files_json, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))
            await message.answer(f"Конспект '{name}' успешно удалён!")
            await state.finish()
        else:
            await message.answer("Конспекта с таким номером нет в списке...\nНапиши команду /cancel для отмены.")
    else:
        await message.answer("Ты ввёл не число!\nНапиши команду \\cancel для отмены.")


def register_handlers_admin(dispatcher: Dispatcher):
    dispatcher.register_message_handler(create_command, commands=['create'])
    dispatcher.register_message_handler(delete_command, commands=['delete'])
    dispatcher.register_message_handler(message_command, commands=['message'])
    dispatcher.register_message_handler(pic_message, content_types=['photo'],
                                        state=AdminStatesGroup.pic_or_text)
    dispatcher.register_message_handler(text_message,
                                        state=AdminStatesGroup.pic_or_text)
    dispatcher.register_message_handler(get_file_from_admin, content_types=['document'],
                                        state=AdminStatesGroup.get_file_from_admin)
    dispatcher.register_message_handler(gffa_exception, content_types=['text'],
                                        state=AdminStatesGroup.get_file_from_admin)
    dispatcher.register_message_handler(get_file_name_from_admin,
                                        state=AdminStatesGroup.get_file_name_from_admin)
    dispatcher.register_message_handler(get_del_number_from_admin, content_types=['text'],
                                        state=AdminStatesGroup.get_del_number_from_admin)
