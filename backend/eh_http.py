import httpx
from eh_config import DEFAULT_HEADERS
from loguru import logger


class EHTTPClient:
    def __init__(
        self,
        cookies: dict | None = None,
        proxy: str | None = None,
    ):
        self.cookies = cookies
        self.proxy = proxy
        self.headers = DEFAULT_HEADERS
        self._update_headers()

    def _update_headers(self):
        """更新headers中的Cookie"""
        if self.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            self.headers["Cookie"] = cookie_str

    def _get_verify_setting(self) -> bool:
        """根据proxy设置确定verify值"""
        return False if self.proxy else True

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """统一的请求方法"""
        async with httpx.AsyncClient(
            proxy=self.proxy,
            timeout=30.0,
            verify=self._get_verify_setting(),
            follow_redirects=True,
        ) as client:
            response = await client.request(
                method=method, url=url, headers=self.headers, **kwargs
            )
            return response

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET请求"""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST请求"""
        return await self.request("POST", url, **kwargs)
