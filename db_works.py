import json
import os

import pymongo
from pymongo import MongoClient
from bson import BSON
from bson.json_util import loads, dumps

# from dotenv import load_dotenv
# load_dotenv('.env')
client = MongoClient(os.getenv('DB_URL'))
db = client['autodoor']


def insert_placeholder_form():
    collection = db.forms
    with open('placeholder_form.json', 'r', encoding='utf-8') as f:
        placeholder = loads(f.read())
    collection.insert_one(placeholder)


def insert_placeholder_dorogi_answer():
    collection = db['Dorogi']
    with open('placeholder_answer.json', 'r', encoding='utf-8') as f:
        placeholder = loads(f.read())
    collection.insert_one(placeholder)


def insert_answer(answer):
    collection = db[answer['name']]
    answer.pop('name')
    print(answer)
    collection.insert_one(answer)


def get_forms():
    collection = db.forms
    forms = [form['title'] for form in collection.find()]
    return forms

if __name__ == '__main__':
    # insert_placeholder_form()
    # insert_placeholder_dorogi_answer()
    get_forms()
