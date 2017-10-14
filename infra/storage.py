import peewee

import database

db = peewee.SqliteDatabase('database.db')


def setup_database():
    db.connect()
    db.create_tables(database.models, safe=True)