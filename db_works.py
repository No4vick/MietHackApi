import json
import os

import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import BSON
from bson.json_util import loads, dumps

load_dotenv('.env')
client = MongoClient(os.getenv('DB_URL'))
db = client['autodoor']


def create_placeholder_form():
    collection = db.forms
    with open('placeholder_form.json', 'r', encoding='utf-8') as f:
        placeholder = loads(f.read())
    collection.insert_one(placeholder)


if __name__ == '__main__':
    create_placeholder_form()
