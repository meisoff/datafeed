from operator import itemgetter
from fastapi import Depends, FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse
import pandas as pd
import aiofiles

import crud, parser_timer

app = FastAPI()

@app.get("/get_items")
def get_items():
    items = list(crud.get_five_file_infos())
    return {"items": items, "err": 0}

@app.post("/upload_settings")
def upload_settings(request: dict):
    print(request)
    parser_timer.set_time(request['time'])
    parser_timer.set_days(request['week']) 
    return {"err": 0}

@app.post("/upload_file")
async def upload_file(file: UploadFile):
    async with aiofiles.open('new_file.xlsx', 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk
    
    return {"err": 0}

@app.get("/get_file")
def download_file(index: int):
    file_info = list(crud.get_file_info_by_index(index=index))
    return FileResponse(path=f"../{file_info[0]['name']}", media_type='application/octet-stream', filename=file_info[0]['name'])