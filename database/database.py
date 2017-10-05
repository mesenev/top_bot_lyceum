import peewee

db = peewee.SqliteDatabase('people.db')


class BotModel(peewee.Model):
    class Meta:
        database = db
