import telebot
import config
import random

from telebot import types

# Загружаем список интересных фактов
f = open('history.txt', 'r', encoding='UTF-8')
history = f.read()
f.close()
#f = open('tests.txt', 'r', encoding='UTF-8')
#tests = f.read()
with open("tests.txt") as inp:
    lines = inp.readlines()
#f.close()
#linelist = []
#for line in f:
    #linelist.append(line)
f.close()
f = open('themes.txt', 'r', encoding='UTF-8')
themes = f.read()
f.close()
f = open('diegest.txt', 'r', encoding='UTF-8')
digest = f.read()
f.close()
# Создаем бота
bot = telebot.TeleBot(config.TOKEN)
# Команда start

@bot.message_handler(commands=["start"])
def start(m, res=False):
        # Добавляем кнопки
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("Тесты")
        item2=types.KeyboardButton("История отряда")
        item3 = types.KeyboardButton("Конспект")
        item4 = types.KeyboardButton("Дайджест")
        markup.add(item1)
        markup.add(item2)
        markup.add(item3)
        markup.add(item4)
        bot.send_message(m.chat.id, 'Нажмите:\nТесты - чтобы проверить свои знания!\nИстория отряда - чтобы узнать много нового!\nКонспект - чтобы получить материал по пропущенному занятию\nДайджест - чтобы узнать, что ждет тебя впереди',  reply_markup=markup)
# Получение сообщений от юзера
def print_history(message):
    answer = history
    bot.send_message(message.chat.id, answer)

def print_digest(message):
    answer = digest
    bot.send_message(message.chat.id, answer)
"""
 def quiz(message,line:str):
     kb = types.InlineKeyboardMarkup()
     kb_1 = types.InlineKeyboardButton(text=line[1], callback_data='101')
     kb_2 = types.InlineKeyboardButton(text=line[2], callback_data='102')
     kb_3 = types.InlineKeyboardButton(text=line[3], callback_data='103')
     kb.add(kb_1, kb_2, kb_3)
     bot.send_message(message.chat.id, line[0], reply_markup=kb)
    #my_quiz = await bot.send_poll(sender_id, question, answers, type='quiz', correct_option_id=index_rigth_answer, explanation=explanation)
    #return my_quiz
"''"""
@bot.message_handler(content_types=["text"])

def handle_text(message):
    stop = 1
    # ИСТОРИЯ
    if message.text.strip() == 'История отряда':
        print_history(message)

    #ДАЙДЖЕСТ
    elif message.text.strip() == 'Дайджест':
        print_digest(message)

    # КОНСПЕКТ
    elif message.text.strip() == 'Конспект':
            answer = themes
            bot.send_message(message.chat.id,
                             'Напишите номер темы, по которой хочешь конспект')
            bot.send_message(message.chat.id, answer)


    elif message.text.strip() == 'Тесты':
        line = random.choice(lines)[:-1].split(";")
        kb = types.InlineKeyboardMarkup()
        kb_1 = types.InlineKeyboardButton(text=line[1], callback_data='101')
        kb_2 = types.InlineKeyboardButton(text=line[2], callback_data='102')
        kb_3 = types.InlineKeyboardButton(text=line[3], callback_data='103')
        kb.add(kb_1, kb_2, kb_3)
        bot.send_message(message.chat.id, line[0], reply_markup=kb)
        #quiz(message, line)
        #stop =1
        #bot.send_message(message.chat.id,
                         #'Напишите "хватит", когда захотите закончить')
        """
        line = random.choice(lines)[:-1].split(";")
        kb =types.InlineKeyboardMarkup()
        kb_1 = types.InlineKeyboardButton(text=line[1], callback_data='101')
        kb_2 = types.InlineKeyboardButton(text=line[2], callback_data='102')
        kb_3 = types.InlineKeyboardButton(text=line[3], callback_data='103')
        kb.add(kb_1, kb_2, kb_3)
        bot.send_message(message.chat.id, line[0], reply_markup=kb)

"""
            #bot.send_message(message.chat.id, answer)


    elif message.text.strip() == 'Дальше':

        line = random.choice(lines)[:-1].split(";")
        kb = types.InlineKeyboardMarkup()
        kb_1 = types.InlineKeyboardButton(text=line[1], callback_data='101')
        kb_2 = types.InlineKeyboardButton(text=line[2], callback_data='102')
        kb_3 = types.InlineKeyboardButton(text=line[3], callback_data='103')
        kb.add(kb_1, kb_2, kb_3)
        bot.send_message(message.chat.id, line[0], reply_markup=kb)

    elif message.text.strip().isdigit():

        doc1 = 'consp'
        doc2 = message.text.strip()
        doc3 = '.pdf'
        if int(doc2)<14:
            answer = "Держи"
            bot.send_document(message.chat.id, open(doc1 + doc2 + doc3, "rb"))
            bot.send_message(message.chat.id, answer)
        else:
            answer ="Введите правильный номер"
            bot.send_message(message.chat.id, answer)
    else:
        answer = "Сообщение не распознано"
        bot.send_message(message.chat.id, answer)

@bot.callback_query_handler(lambda call: True)
def callback_inline(call):
        if int(call.data)%100 == 1:
            bot.send_message(call.message.chat.id, 'Верно!')
            bot.send_message(call.message.chat.id, 'Напишите "Дальше", чтобы продолжить')
        else:
            bot.send_message(call.message.chat.id, 'Вы ошиблись:( Попробуйте снова')

       # elif call.data == '103':
         #   bot.send_message(call.message.chat.id, 'правда лох')

    # Отсылаем юзеру сообщение в его чат
    #bot.send_message(message.chat.id, answer)
# Запускаем бота
bot.polling(none_stop=True, interval=0)


bot = telebot.TeleBot(config.TOKEN)

"""
@bot.message_handler(commands=['start'])
def start_msg(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1) # вывод кнопок в 1 колонку
    one = types.InlineKeyboardButton('1', callback_data='one')
    two = types.InlineKeyboardButton('2', callback_data='two')
    three = types.InlineKeyboardButton('3', callback_data='three')
    # и так далее либо же сделать через цикл for, но у каждой кнопки должен быть свой callback
    keyboard.add(one, two, three)
    bot.send_message(message.chat.id, 'Вывод inline-клавиатуры', reply_markup=keyboard)


#обработка callback клавиатуры
@bot.callback_query_handler(func=lambda message: True)
def logic_inline(call):
    if message.data == 'one':
          bot.send_message(call.message.chat.id, 'Ты нажал на кнопку 1')
    elif message.data == 'two':
          bot.send_message(call.message.chat.id, 'Ты нажал на кнопку 2')
    elif message.data == 'three':
          bot.send_message(call.message.chat.id, 'Ты нажал на кнопку 3')


bot.polling()
"""