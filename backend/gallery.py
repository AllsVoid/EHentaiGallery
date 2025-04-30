from dataclasses import dataclass


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
