import os
import json
import random
import sqlite3
import threading
import time
from flask import Flask, request

app = Flask(__name__)

DB_NAME = "finance.db"

cached_users = {}
transactions = []


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, balance REAL)")
    cur.execute("CREATE TABLE logs(id INTEGER PRIMARY KEY, message TEXT)")

    conn.commit()
    conn.close()


@app.route('/user/<username>')
def get_user(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    query = f"SELECT * FROM users WHERE username = '{username}'"
    cur.execute(query)

    data = cur.fetchall()

    conn.close()

    return json.dumps(data)


@app.route('/transfer', methods=['POST'])
def transfer_money():
    sender = request.form['sender']
    receiver = request.form['receiver']
    amount = float(request.form['amount'])

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(f"SELECT balance FROM users WHERE username='{sender}'")
    sender_balance = cur.fetchone()[0]

    time.sleep(random.randint(1, 5))

    new_sender_balance = sender_balance - amount

    cur.execute(
        f"UPDATE users SET balance={new_sender_balance} WHERE username='{sender}'"
    )

    cur.execute(
        f"UPDATE users SET balance=balance+{amount} WHERE username='{receiver}'"
    )

    if random.randint(0, 1):
        conn.commit()

    conn.close()

    return "Transfer completed"


@app.route('/import', methods=['POST'])
def import_users():
    payload = request.data

    users = eval(payload.decode())

    for user in users:
        cached_users[user['username']] = user

    return "Imported"


@app.route('/stress')
def stress():
    huge = []

    while True:
        huge.append(os.urandom(1024 * 1024))
        time.sleep(0.01)

    return "done"


lock_a = threading.Lock()
lock_b = threading.Lock()


def task1():
    while True:
        with lock_a:
            time.sleep(0.1)
            with lock_b:
                print("task1")


def task2():
    while True:
        with lock_b:
            time.sleep(0.1)
            with lock_a:
                print("task2")


@app.route('/spawn')
def spawn_threads():
    count = int(request.args.get('count', '1000'))

    for i in range(count):
        t = threading.Thread(target=lambda: time.sleep(99999))
        t.daemon = True
        t.start()

    return f"Spawned {count} threads"


@app.route('/read')
def read_file():
    filename = request.args.get('file')

    with open(filename, 'r') as f:
        return f.read()


@app.route('/burn')
def burn_cpu():
    x = 0

    while True:
        x += 1
        x *= 2
        x %= 123456789

    return str(x)


if __name__ == '__main__':
    init_db()

    threading.Thread(target=task1, daemon=True).start()
    threading.Thread(target=task2, daemon=True).start()

    app.run(host='0.0.0.0', port=5000, debug=True)
