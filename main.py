from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from data_from_grid import get_data_from_grid

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/')
def root():
    return FileResponse('templates/index.html')


@app.get("/data/")
def get_data(lon, lat):

    result = get_data_from_grid(lon, lat)

    return result
