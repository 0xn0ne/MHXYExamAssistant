import peewee
from playhouse.db_url import connect
from playhouse.shortcuts import model_to_dict
import re

db = connect('sqlite:\\database.db', autocommit=True, autorollback=True)

class BaseModel(peewee.Model):
    class Meta:
        database = db

    def to_dict(self):
        return model_to_dict(self)

    @classmethod
    def get_by(cls, *exprs):
        try:
            return cls.get(*exprs)
        except cls.DoesNotExist:
            return

    @classmethod
    def get_by_pk(cls, value):
        try:
            return cls.get(cls._meta.primary_key == value)
        except cls.DoesNotExist:
            return

    @classmethod
    def exists_by_pk(cls, value):
        return cls.select().where(cls._meta.primary_key == value).exists()

class Question(BaseModel):
    question = peewee.TextField(unique=True, index=True)
    answer = peewee.TextField(index=True)

    @classmethod
    def new(cls, question, answer):
        return cls.create(question=question, answer=answer)

    @classmethod
    def get_by_q(cls, value):
        try:
            return cls.get(cls.question == value)
        except cls.DoesNotExist:
            return

    @classmethod
    def search_by_q(cls, value):
        try:
            return [i.question, i.answer for i in cls.select().where(cls.question % value)]
        except cls.DoesNotExist:
            return

db.create_tables([Question], safe=True)