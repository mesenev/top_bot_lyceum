import peewee

db = peewee.SqliteDatabase('database.db')


class BotModel(peewee.Model):
    class Meta:
        database = db
