import logging
import os
from datetime import datetime
from typing import Text

from peewee import *
from playhouse.shortcuts import (  # these can be used to convert an item to or from json http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#model_to_dict
    dict_to_model, model_to_dict)
from playhouse.sqlite_ext import RowIDField

#Creates a SQLite Database.
db = SqliteDatabase("data.db", pragmas={'foreign_keys': 1})

def iter_table(model_dict):
    """Iterates through a dictionary of tables, confirming they exist and creating them if necessary."""
    for key in model_dict:
        if not db.table_exists(key):
            db.connect(reuse_if_open=True)
            db.create_tables([model_dict[key]])
            #print(f"Created table '{key}'")
            db.close()

class BaseModel(Model):
    """Base Model class used for creating new tables."""
    class Meta:
        database = db

class MeetingSession(BaseModel):
    """Stores our Meeting Information"""
    id = AutoField()
    period = TextField() 
    day = TextField()
    timeStarted = TextField()
    URL = TextField()

class PreviousRecord(BaseModel):
    """Previous Information, used before but deprecated."""
    id = AutoField()
    lastDay = TextField()

class SetupStatus(BaseModel):
    """Setup Class and Information."""
    id = AutoField()
    setupStatus = BooleanField(default=False)
    blockSchedule = BooleanField(default=False)
    startDate = DateTimeField()
    startDay = TextField()
    yearInteger = IntegerField()

tables = {"meetingsession": MeetingSession, "previousrecord": PreviousRecord, "setupstatus": SetupStatus}
iter_table(tables)
