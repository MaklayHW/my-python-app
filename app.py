from flask import Flask, request
import psycopg2
import os
import time

app = Flask(__name__)


def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST', 'db'),
                database=os.environ.get('DB_NAME', 'mydb'),
                user=os.environ.get('DB_USER', 'user'),
                password=os.environ.get('DB_PASSWORD', 'password')
            )
            return conn
        except Exception as e:
            print(f"Ошибка подключения: {e}. Осталось попыток: {retries - 1}")
            retries -= 1
            time.sleep(3)
    raise Exception("Не удалось подключиться к базе данных после 5 попыток")


def init_db():
    """Создаёт таблицу messages, если она не существует"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Таблица messages успешно создана или уже существует")
    except Exception as e:
        print(f"Ошибка при создании таблицы: {e}")


# Инициализируем базу данных
print("Инициализация базы данных...")
init_db()
print("Готово!")


@app.route('/')
def index():
    return '''
    <h1>Приложение с базой данных</h1>
    <p><a href="/add?text=Привет">Добавить запись: Привет</a></p>
    <p><a href="/add?text=Мир">Добавить запись: Мир</a></p>
    <p><a href="/list">Посмотреть все записи</a></p>
    '''


@app.route('/add')
def add():
    text = request.args.get('text', '')
    if not text:
        return '<h2>Ошибка: текст не передан</h2><p><a href="/">Назад</a></p>'

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO messages (text) VALUES (%s)', (text,))
    conn.commit()
    cur.close()
    conn.close()
    return f'<h2>Добавлено: {text}</h2><p><a href="/">Назад</a></p>'


@app.route('/list')
def list_messages():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT text, created_at FROM messages ORDER BY id DESC')
    messages = cur.fetchall()
    cur.close()
    conn.close()

    if not messages:
        return '<h2>Нет записей</h2><p><a href="/">Назад</a></p>'

    html = '<h2>Все записи:</h2><ul>'
    for msg in messages:
        html += f'<li>{msg[0]} — {msg[1]}</li>'
    html += '</ul><p><a href="/">Назад</a></p>'
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)