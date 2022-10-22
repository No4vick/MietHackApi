from fastapi import FastAPI, Request, Response, status, UploadFile
from pydantic import BaseModel

import db_works as db

app = FastAPI()


class Options(BaseModel):
    name: str
    content: list


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/save-answer", status_code=201)
async def add_mail(request: Request, options: Options,
                   response: Response):  # , files: Union[List[UploadFile], None] = None):
    result = await request.json()
    print(result)
    if request.headers.get('token') != "test":
        # response.status_code = status.HTTP_401_UNAUTHORIZED
        # return
        print("no token!")
    db.insert_answer(result)
    response.status_code = status.HTTP_201_CREATED
    return {"lol": "kek", "token": request.headers.get('token')}


@app.get("/form-names")
async def send_form_names(request: Request, response: Response):
    return {"names": db.get_forms()}
