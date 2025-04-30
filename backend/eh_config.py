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

API_ENDPOINTS = {
    "ehentai": "https://e-hentai.org",
    "exhentai": "https://exhentai.org",
}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip",
}

CHOICE_ENDPOINTS = {
    "random": "tag/random",
    "topt": "toplist.php?tl=11",
    "topy": "toplist.php?tl=12",
    "topm": "toplist.php?tl=13",
    "topd": "toplist.php?tl=15",
}
