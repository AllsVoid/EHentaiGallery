import asyncio
import tomllib
from datetime import datetime
from pathlib import Path

import uvicorn
from api import EHentaiAPI
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("config.toml", "rb") as f:
    config = tomllib.load(f)
cookies = config["cookies"]
proxy = config.get("proxy", None)

api = EHentaiAPI(cookies, proxy)


@app.get("/test")
async def test():
    return await api.test_fastapi()


@app.get("/s/{query}")
async def search(
    query: str,
    page: int | None = Query(None, description="页码，从0开始"),
    category: str | None = Query(None, description="分类筛选"),
    min_rating: int | None = Query(None, description="最低评分"),
):
    await api.initialize()
    logger.debug(f"search: {query}, {page}, {category}, {min_rating}")
    return await api.search(query, page, category, min_rating)


@app.get("/g/{url:path}")
async def get_gallery(url: str):
    await api.initialize()
    return await api.get_gallery_info(f"{url}")


@app.get("/choice/{choice}")
async def choice_gallery(choice: str = "random"):
    await api.initialize()
    return await api.choice_gallery(choice)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
