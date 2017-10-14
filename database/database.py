import peewee

import infra.storage

models = []


class BotModel(peewee.Model):
    class Meta:
        database = infra.storage.db

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        models.append(cls)
