from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json

with open("json/config.json", 'r') as cfg:
    config = json.loads(cfg.read())

with open('txt/history.txt', 'r', encoding='UTF-8') as file:
    history = file.read()

with open('txt/digest.txt', 'r', encoding='UTF-8') as file:
    digest = file.read()

storage = MemoryStorage()
bot = Bot(config['TOKEN_API'])
dp = Dispatcher(bot, storage=storage)
