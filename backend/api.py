import asyncio
import json
import re
import tomllib
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

EH_CATEGORY = {
    # 同人志
    "Doujinshi": "2",
    # 漫画
    "Manga": "4",
    # 艺术家CG
    "Artist CG": "8",
    # 游戏CG
    "Game CG": "16",
    # 西方
    "Western": "512",
    # 非H
    "Non-H": "256",
    # 图片集
    "Image Set": "32",
    # 角色扮演
    "Cosplay": "64",
    # 亚洲
    "Asian Porn": "128",
    # 杂项
    "Misc": "1",
}


@dataclass
class GalleryInfo:
    """画廊信息"""

    gid: int
    token: str
    title: str
    title_jpn: str
    category: str
    thumb: str
    uploader: str
    posted: str
    filecount: int
    filesize: int
    expunged: bool
    rating: float
    tags: str | int
    archiver_key: str | None
    parent_gid: int | None
    parent_key: str | None
    first_gid: int | None
    first_key: str | None


@dataclass
class SearchResult:
    """搜索结果"""

    gid: int
    token: str
    title: str
    thumb: str
    torrent: str


class EHentaiError(Exception):
    """EHentai API 基础异常类"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UnableDownload(EHentaiError):
    """无法下载异常"""

    def __init__(self):
        super().__init__("账号无GP/下载流量，无法下载！")


class FailedGetDownloadUrl(EHentaiError):
    """获取下载地址失败异常"""

    def __init__(self, gid: int):
        super().__init__(f"获取下载地址失败: {gid}")


class IPBlocking(EHentaiError):
    """IP被封锁异常"""

    def __init__(self):
        super().__init__("IP已被Ehentai封锁，请更换代理")


class EHentaiAPI:
    def __init__(
        self,
        cookies: dict | None,
        proxy: str | None,
    ):
        self.ehentai_url = "https://e-hentai.org"
        self.exhentai_url = "https://exhentai.org"
        self.cookies = cookies
        self.proxy = proxy
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip",
        }
        self.update_headers()
        self.url = None

    async def initialize(self):
        """初始化 API，检查权限并设置 URL"""
        self.url = await self.check_ex_permission()

    def update_headers(self):
        """更新 headers 中的 Cookie"""
        if self.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            logger.debug(f"更新 Cookie: {cookie_str}")
            self.headers["Cookie"] = cookie_str
        else:
            logger.debug("没有 Cookie")

    def _get_verify_setting(self) -> bool:
        """根据proxy设置确定verify值"""
        return False if self.proxy else True

    def parse_search_response(self, res: httpx.Response) -> list[SearchResult]:
        """解析搜索响应"""
        soup = BeautifulSoup(res.text, "html.parser")
        galleries = []
        gallery_cells = soup.find_all("td", class_="gl3c")
        for cell in gallery_cells:
            link = cell.find("a")
            if not link:
                continue

            href = link.get("href", "")
            if not href:
                continue

            match = re.match(
                r"https://(?:e-)?(?:ex)?hentai\.org/g/(\d+)/([a-f0-9]+)/", href
            )
            if not match:
                continue
            gid, token = match.groups()
            glink = cell.find("div", class_="glink")
            title = glink.text if glink else ""
            thumb_row = cell.parent
            thumb_div = thumb_row.find("div", class_="glthumb")
            if thumb_div:
                thumb_img = thumb_div.find("img")
                if thumb_img:
                    # 优先使用 data-src，如果没有则使用 src
                    thumb_url = thumb_img.get("data-src", "") or thumb_img.get(
                        "src", ""
                    )
                else:
                    thumb_url = ""
            else:
                thumb_url = ""
                # 获取种子链接
            torrent_url = ""
            torrent_cell = thumb_row.find("td", class_="gl2c")
            if torrent_cell:
                torrent_link = torrent_cell.find(
                    "a", href=lambda x: x and "gallerytorrents.php" in x
                )
                if torrent_link:
                    torrent_url = torrent_link["href"]

            galleries.append(
                SearchResult(
                    gid=gid,
                    token=token,
                    title=title,
                    thumb=thumb_url,
                    torrent=torrent_url,
                )
            )
            logger.info(f"找到 {len(galleries)} 个画廊")
        return galleries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    async def check_ex_permission(self) -> str:
        """检查是否具有 exhentai 访问权限"""
        try:
            async with httpx.AsyncClient(
                proxy=self.proxy,
                timeout=30.0,
                verify=self._get_verify_setting(),
                follow_redirects=True,
            ) as client:
                res = await client.get(
                    self.exhentai_url, headers=self.headers, follow_redirects=True
                )
                logger.debug(res)
                if res.status_code == 200 and res.text:
                    logger.info("成功连接到 exhentai")
                    return self.exhentai_url
                else:
                    logger.warning(f"exhentai 返回状态码: {res.status_code}")
                    return self.ehentai_url

        except Exception as e:
            logger.error(f"检查 exhentai 权限失败: {e}")

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
        """
        搜索画廊

        Args:
            query: 搜索关键词
            page: 页码 (从0开始)
            category: 分类筛选
            min_rating: 最低评分
            **kwargs: 其他搜索参数

        Returns:
            SearchResult: 搜索结果
        """
        logger.debug(f"search: {query}, {page}, {category}, {min_rating}")
        if category:
            category_id = self.category_to_id(category)
            search_url = f"{self.url}/?f_cats={category_id}"
            logger.debug(f"category_id: {category_id}")
            if not category_id:
                logger.error(f"无效的分类: {category}")
        else:
            search_url = f"{self.url}/?"

        try:
            # 构建搜索URL
            search_url += f"&f_search={query}&page={page}"
            if min_rating:
                search_url += f"&advanced=1&f_srdd={min_rating}"
            logger.debug(f"search_url: {search_url}")

            async with httpx.AsyncClient(
                proxy=self.proxy,
                timeout=30.0,
                verify=self._get_verify_setting(),
                follow_redirects=True,
            ) as client:
                res = await client.get(search_url, headers=self.headers)
                if res.status_code != 200:
                    logger.debug(f"搜索请求失败，状态码: {res.status_code}")
                    return SearchResult(gid=0, token="", title="")

                # 保存响应内容用于调试
                with open("search_response.html", "w", encoding="utf-8") as f:
                    f.write(res.text)

            return self.parse_search_response(res)

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True,
    )
    async def get_gallery_info(self, url: str) -> GalleryInfo:
        """
        从 URL 中获取画廊信息

        Args:
            url: (单个)画廊URL

        Returns:
            GalleryInfo: 画廊信息
        """
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

            async with httpx.AsyncClient(
                proxy=self.proxy,
                timeout=30.0,
                verify=self._get_verify_setting(),
                follow_redirects=True,
            ) as client:
                res = await client.post(
                    f"{self.url}/api.php", headers=self.headers, json=params
                )
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
    async def random_gallery(self):
        """
        随机画廊
        """
        logger.debug("随机画廊")
        try:
            request_url = f"{self.url}/tag/random"
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
                return self.parse_search_response(res)

        except Exception as e:
            logger.error(f"随机画廊请求失败: {e}")
            raise


async def main():
    # 读取配置文件
    try:
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        logger.error("配置文件不存在, 请先创建 config.toml 文件")
        return

    cookies = config["cookies"]
    proxy = config.get("proxy", None)

    api = EHentaiAPI(cookies, proxy)
    await api.initialize()
    # result = await api.get_gallery_info("https://exhentai.org/g/3310647/d0c337ea6e")
    # logger.info(result.title)
    # logger.info(api.url)
    result = await api.search("difa", category="doujinshi,manga", min_rating=4)
    logger.info(result)


if __name__ == "__main__":
    asyncio.run(main())
