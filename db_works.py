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
    insert_answer(placeholder)


def insert_answer(answer):
    collection = db.answers
    existing_data = get_main_of_form(answer['name'])
    answer['main'] = existing_data is None
    print(answer)
    collection.insert_one(answer)


def get_forms():
    collection = db.forms
    forms = [form['title'] for form in collection.find()]
    return forms


def get_form(form_title: str, json=False):
    collection = db.forms
    form = collection.find_one({'title': form_title})
    if json:
        form.pop("_id")
    return form


def form_field_length(form_title: str):
    form = get_form(form_title)
    return len(form['fields'])


def check_format(answer):
    content = answer['content']
    form_title = answer['name']
    form_fields = get_form(form_title)['fields']
    if len(content) != form_field_length(form_title):
        return False
    for i in range(len(content)):
        if form_fields[i]['field_type'] != 'text' and form_fields[i]['field_type'] != 'file':
            for value in content[i]['field_values']:
                flag = False
                vals = form_fields[i]['field_values'].values() if type(form_fields[i]['field_values']) is dict \
                    else form_fields[i]['field_values']
                for form_field in vals:
                    if value == form_field:
                        flag = True
                if not flag:
                    return False
    return True


def check_collisions(answer, force=False):
    content = answer['content']
    existing_data = get_main_of_form(answer['name'])
    if existing_data is None or force:
        return {"status": 201, "message": "Successfully created answer"}
    existing_data = existing_data['content']
    collisions = []
    collision_count = 0
    for i in range(len(content)):
        key = 'field_values'
        try:
            vals = content[i][key]
        except KeyError:
            key = 'field_value'
            vals = content[i][key]
        if vals != existing_data[i][key] or not existing_data[i][key]:
            collisions.append({'collision_id': collision_count, "form": answer['name'], 'field_id': i + 1,
                               'field_value': existing_data[i][key], 'new_field_value': vals})
            collision_count += 1
    if collision_count == 0:
        return {"status": 400, "message": "Duplicate"}
    else:
        return {"status": 409, "collisions": collisions}


def fill_empty(answer):
    content = answer['content']
    existing_whole = get_main_of_form(answer['name'])
    existing_data = existing_whole['content']
    for i in range(len(content)):
        key = 'field_values'
        try:
            vals = content[i][key]
        except KeyError:
            key = 'field_value'
            vals = content[i][key]
        if not existing_data[i][key]:
            existing_data[i][key] = vals
    db.answers.find_one_and_update({"name": existing_whole['name'], 'user': existing_whole['user'],
                                    'date': existing_whole['date']}, {'$set': {"content": existing_data}})


def append_files(answer):
    content = answer['content']
    existing_whole = get_main_of_form(answer['name'])
    existing_data = existing_whole['content']
    form = get_form(answer['name'])
    for i in range(len(content)):
        key = 'field_values'
        try:
            vals = content[i][key]
        except KeyError:
            key = 'field_value'
            vals = content[i][key]
        field_type = form['fields'][i]['field_type']
        if existing_data[i][key] != vals and (field_type == "checkbox" or field_type == 'file'):
            for val in vals:
                if val not in existing_data[i][key]:
                    existing_data[i][key].append(val)
    db.answers.find_one_and_update({"name": existing_whole['name'], 'user': existing_whole['user'],
                                    'date': existing_whole['date']}, {'$set': {"content": existing_data}})


def get_main_of_form(collection_name, json=False):
    collection = db.answers
    try:
        c = collection.find_one({'name': collection_name, 'main': True})
    except IndexError:
        return None
    if json:
        c.pop("_id")
    return c


def save_file(name, filetype, binary):
    db.files.insert_one({'name': name, 'type': filetype, 'data': binary})


def file_exists(filename):
    file = db.files.find_one({'name': filename})
    return file is not None


def get_file(filename):
    file = db.files.find_one({'name': filename})
    if not file:
        return None
    return file['data']


def save_session(jsn):
    collection = db.sessions
    if collection.count_documents({"token": jsn['token']}) == 0:
        collection.insert_one(jsn)


if __name__ == '__main__':
    # insert_placeholder_form()
    # insert_placeholder_dorogi_answer()
    # get_forms()
    # print(form_field_length('Dorogi'))
    with open('placeholder_answer.json', 'r', encoding='utf-8') as f:
        jsn = json.loads(f.read())
    # print(check_format(jsn))
    # get_first_in_collection('Dorogi')

    jsn['content'][4]['field_values'] = ["Кабель", "Бокс", "Болт 20x5"]
    print(check_collisions(jsn))
