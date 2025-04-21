import asyncio
import tomllib
from datetime import datetime
from loguru import logger
from pathlib import Path
from api import EHentaiAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ere import search_gallery, test
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("config.toml", "rb") as f:
    cookies = tomllib.load(f)

api = EHentaiAPI(cookies, None)

@app.get("/test")
async def test():
    return await api.test_fastapi()

@app.get("/s/{query}?{page}")
# async def search(query: str):
#     return await search_gallery(query)
async def search(query: str, page: int):
    await api.initialize()
    return await api.search(query)


# @app.get("/g/{url:path}")
# async def get_gallery(url: str):
#     return await test()
@app.get("/g/{url:path}")
async def get_gallery(url: str):
    await api.initialize()
    return await api.get_gallery_info(f"{url}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 


