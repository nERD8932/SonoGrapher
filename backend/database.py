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
    c = create_connection('./api_keys.sqlite')
    c.execute('create table api_keys(key text primary key , user text);')

def create_default():
    c = create_connection('./api_keys.sqlite')
    c.execute('create table if not exists api_keys(key text primary key , user text);')
    if os.path.exists("./backend/rootUserToken.txt"):
        token = ""
        with open("./backend/rootUserToken.txt") as f:
            token = f.read()
        if token != "":
            c.execute(f'insert into api_keys (key, user) values ("rootUser", "{token}");')