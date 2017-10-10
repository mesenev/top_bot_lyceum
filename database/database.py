import peewee

db = peewee.SqliteDatabase('database.db')

models = []


class BotModel(peewee.Model):
    class Meta:
        database = db

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        models.append(cls)
