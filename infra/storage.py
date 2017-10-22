import peewee

db = peewee.SqliteDatabase('database.db')


def setup_database():
    import database
    db.connect()
    db.create_tables(database.models, safe=True)