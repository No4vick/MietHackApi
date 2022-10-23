from typing import Union, List

from fastapi import FastAPI, Request, Response, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import db_works as db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Options(BaseModel):
    name: str
    content: list


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/save-answer", status_code=201)
async def save_answer(request: Request, options: Options,
                      response: Response):  # , files: Union[List[UploadFile], None] = None):
    result = await request.json()
    print(result)
    force = request.headers.get('force') is not None
    if request.headers.get('token') != "test":
        # response.status_code = status.HTTP_401_UNAUTHORIZED
        # return
        print("no token!")
    if not db.check_format(result):
        return {'status': 400, 'message': "Incorrect format"}
    collision_result = db.check_collisions(result, force)
    if collision_result['status'] == 201:
        db.insert_answer(result)
    else:
        db.fill_empty(result)
    response.status_code = collision_result['status']
    return collision_result


@app.get("/form/{form}")
async def get_form_data(form: str):
    data = db.get_form(form, True)
    return {"form": form, "data": data}


@app.get("/form/{form}/data")
async def get_form_data(form: str):
    data = db.get_main_of_form(form, True)
    return {"form": form, "data": data}


@app.get("/form/{form}/data/{user}")
async def get_form_data(form: str):
    data = db.get_main_of_form(form, True)
    return {"form": form, "data": data}


@app.get("/form-names")
async def send_form_names():
    return {"names": db.get_forms()}


@app.post("/upload")
async def upload_file(files: Union[List[UploadFile], None] = None):
    for file in files:
        filename = file.filename
        if db.file_exists(filename):
            continue
        filetype = file.content_type
        binary = await file.read()
        db.save_file(filename, filetype, binary)
    return {'status': 200, "message": "Success"}


@app.get("/download/{filename}")
async def download_file(filename: str):
    file = db.get_file(filename)
    return Response(content=file, media_type="image/png")


@app.get("/session-save")
async def save_session(req: Request):
    result = await req.json()
    db.save_session(result)
    return {"status": 200, 'message': 'Success'}
