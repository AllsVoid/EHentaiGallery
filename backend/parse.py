import re

from bs4 import BeautifulSoup
from gallery import SearchResult


def parse_search_response(res) -> list[SearchResult]:
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
                thumb_url = thumb_img.get("data-src", "") or thumb_img.get("src", "")
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
    return galleries
