import os

import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv('.env')
client = MongoClient(os.getenv('DB_URL'))
db = client['autodoor']


def create_placeholder_form():
    collection = db.forms
    placeholder = [
        {
            "field_id": 1,
            "field_name": "Выполненные работы"
        }
    ]
