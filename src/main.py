from operator import itemgetter
from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import pandas as pd
import aiofiles

import crud, pedantic_models

app = FastAPI()

@app.post("/create_item/", response_model=pedantic_models.Item)
def create_item(
    item: pedantic_models.ItemCreate
):
    return crud.create_product(item=item)

@app.get("/items/", response_model=list[pedantic_models.Item])
def read_items(limit: int = 100):
    items = crud.get_products(limit=limit)
    return items

@app.get("/items/{id}/")
def delete_item(id: int):
    crud.delete_product(id=id)

@app.post("/create_items/")
def create_items(
    item: pedantic_models.ItemCreate
):
    crud.create_product(item=item)

@app.post("/upload_file/")
async def upload_file(file: UploadFile):
    # TODO: 
    async with aiofiles.open('../parserProject/new_file.xlsx', 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk
    return {"filename": file.filename}

@app.get("/download-file")
def download_file(path: str):
    return FileResponse(path=path, filename=path)