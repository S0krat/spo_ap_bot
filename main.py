from aiogram import executor
from start_bot import dp
from handlers import user, admin
from database.sqlite_db import sql_start


if __name__ == '__main__':
    sql_start()
    user.register_handlers_user(dp)
    admin.register_handlers_admin(dp)
    executor.start_polling(dp, skip_updates=True)
