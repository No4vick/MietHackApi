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
async def save_answer(request: Request, options: Options,
                   response: Response):  # , files: Union[List[UploadFile], None] = None):
    result = await request.json()
    print(result)
    if request.headers.get('token') != "test":
        # response.status_code = status.HTTP_401_UNAUTHORIZED
        # return
        print("no token!")
    if not db.check_format(result):
        return {'status': 400, 'message': "Incorrect format"}
    collision_result = db.check_collisions(result)
    if collision_result['status'] == 201:
        db.insert_answer(result)
    response.status_code = collision_result['status']
    return collision_result


@app.get("/form/{form}")
async def get_form_data(form: str):
    data = db.get_form(form, True)
    return {"form": form, "data": data}


@app.get("/form/{form}/data")
async def get_form_data(form: str):
    data = db.get_first_in_collection(form, True)
    return {"form": form, "data": data}


@app.get("/form-names")
async def send_form_names(request: Request, response: Response):
    return {"names": db.get_forms()}
