import sqlite3
import os
from sqlite3 import Error
import logging


def create_connection(path, l: logging.Logger = logging.getLogger()):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        l.error(f"The error '{e}' occurred")

    return connection


def create_table():
    c = create_connection('./backend/api_keys.sqlite')
    cursor = c.cursor()
    cursor.execute('create table api_keys(key text primary key , user text);')
    c.commit()
    c.close()


def create_default():
    c = create_connection('./backend/api_keys.sqlite')
    cursor = c.cursor()
    if os.path.exists("./backend/rootUserToken.txt"):
        with open("./backend/rootUserToken.txt") as f:
            token = str(f.readline())
    else:
        token = 'Brhyd7MpfC'

    cursor.execute(f'insert into main.api_keys (key, user) values ("{token}", "rootUser");')
    c.commit()
    c.close()