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
