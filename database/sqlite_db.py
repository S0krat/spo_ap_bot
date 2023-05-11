import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('users.db')
    cur = base.cursor()
    if base:
        print("Database connected!")
    base.execute("CREATE TABLE IF NOT EXISTS users ("
                 "id int PRIMARY KEY, "
                 "admin bool, "
                 "name varchar(255))")
    base.commit()


def check_member(user_id):
    cur.execute(f"SELECT admin FROM users WHERE id={user_id}")
    return cur.fetchall()


def add_new_member(data):
    query = 'INSERT INTO users (id, admin, name) VALUES (?, 0, ?)'
    cur.execute(query, data)
    base.commit()


def get_user_ids():
    cur.execute(f"SELECT id FROM users")
    return cur.fetchall()
