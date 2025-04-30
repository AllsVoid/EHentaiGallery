import asyncio
import json
import re
import tomllib
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from eh_config import API_ENDPOINTS, CHOICE_ENDPOINTS, DEFAULT_HEADERS, EH_CATEGORY
from eh_error import EHentaiError, FailedGetDownloadUrl, IPBlocking, UnableDownload
from eh_http import EHTTPClient
from gallery import GalleryInfo, SearchResult
from loguru import logger
from parse import parse_search_response
from tenacity import retry, stop_after_attempt, wait_exponential


class EHentaiAPI:
    def __init__(
        self,
        cookies: dict | None,
        proxy: str | None,
    ):
        self.ehentai_url = API_ENDPOINTS["ehentai"]
        self.exhentai_url = API_ENDPOINTS["exhentai"]
        self.http_client = EHTTPClient(cookies=cookies, proxy=proxy)
        self.url = None

    async def initialize(self):
        """初始化 API，检查权限并设置 URL"""
        self.url = await self.check_ex_permission()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    async def check_ex_permission(self) -> str:
        """检查是否具有 exhentai 访问权限"""
        try:
            res = await self.http_client.get(self.exhentai_url)
            logger.debug(res)
            if res.status_code == 200 and res.text:
                logger.info("成功连接到 exhentai")
                return self.exhentai_url
            else:
                logger.warning(f"exhentai 返回状态码: {res.status_code}")
                return self.ehentai_url
        except Exception as e:
            logger.error(f"检查 exhentai 权限失败: {e}")
            return self.ehentai_url

    def category_to_id(self, category: str) -> int:
        """将分类转换为 ID"""
        category_id = 0
        for c in range(len(category.split(","))):
            c = category.split(",")[c].strip().title()
            if c in EH_CATEGORY:
                category_id += int(EH_CATEGORY[c])
        category_id = 1023 - category_id
        return category_id

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    async def search(
        self,
        query: str,
        page: int = 0,
        category: str | None = None,
        min_rating: int | None = None,
        **kwargs,
    ) -> list[SearchResult]:
        """搜索画廊"""
        logger.debug(f"search: {query}, {page}, {category}, {min_rating}")
        try:
            # 构建搜索URL
            search_url = f"{self.url}/?"
            if category:
                category_id = self.category_to_id(category)
                search_url += f"f_cats={category_id}&"
                logger.debug(f"category_id: {category_id}")
                if not category_id:
                    logger.error(f"无效的分类: {category}")

            search_url += f"f_search={query}&page={page}"
            if min_rating:
                search_url += f"&advanced=1&f_srdd={min_rating}"
            logger.debug(f"search_url: {search_url}")

            res = await self.http_client.get(search_url)
            if res.status_code != 200:
                logger.debug(f"搜索请求失败，状态码: {res.status_code}")
                return SearchResult(gid=0, token="", title="")

            return parse_search_response(res)
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    async def get_gallery_info(self, url: str) -> GalleryInfo:
        """获取画廊信息"""
        try:
            logger.debug(url)
            match = re.match(
                r"https://(?:e-)?(?:ex)?hentai\.org/g/(\d+)/([a-f0-9]+)", url
            )
            if not match:
                logger.error("无效的画廊URL")
                return None

            gid, token = match.groups()
            logger.debug(f"gid: {gid}, token: {token}")
            params = {"method": "gdata", "gidlist": [[int(gid), token]], "namespace": 1}

            res = await self.http_client.post(f"{self.url}/api.php", json=params)
            if res.status_code != 200:
                logger.error(f"获取画廊信息失败，状态码: {res.status_code}")
                return None

            try:
                logger.debug(res.headers)
                data = res.json()
                logger.debug(data)
            except json.decoder.JSONDecodeError as e:
                logger.error(f"获取画廊信息失败: 解码JSON时出错: {e}")
                return None

            if not data.get("gmetadata"):
                return None

            g = data["gmetadata"][0]
            return GalleryInfo(
                gid=g["gid"],
                token=g["token"],
                title=g["title"],
                title_jpn=g.get("title_jpn", ""),
                category=g["category"],
                thumb=g["thumb"],
                uploader=g["uploader"],
                posted=g["posted"],
                filecount=g["filecount"],
                filesize=g["filesize"],
                expunged=g["expunged"],
                rating=float(g["rating"]),
                tags=g["tags"],
                archiver_key=g.get("archiver_key"),
                parent_gid=g.get("parent_gid"),
                parent_key=g.get("parent_key"),
                first_gid=g.get("first_gid"),
                first_key=g.get("first_key"),
            )

        except Exception as e:
            logger.error(f"获取画廊信息失败: {e}")
            raise

    async def test_fastapi(self):
        return "FastAPI is working!"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    async def preview_gallery_images(self, url: str):
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    async def choice_gallery(self, choice: str = "random"):
        """
        随机画廊

        Args:
            choice: 获取类型
                random: 随机画廊
                topt: 总排行
                topy: 年排行
                topm: 月排行
                topd: 日排行

        Returns:
            list[SearchResult]: 随机画廊列表
        """
        logger.debug("随机画廊")

        try:
            request_url = f"{self.ehentai_url}/{CHOICE_ENDPOINTS[choice]}"
            logger.debug(f"request_url: {request_url}")
            async with httpx.AsyncClient(
                proxy=self.proxy,
                timeout=30.0,
                verify=self._get_verify_setting(),
                follow_redirects=True,
            ) as client:
                res = await client.get(request_url, headers=self.headers)
                if res.status_code != 200:
                    logger.error(f"随机画廊请求失败，状态码: {res.status_code}")
                    return None
                return parse_search_response(res)

        except Exception as e:
            logger.error(f"随机画廊请求失败: {e}")
            raise
