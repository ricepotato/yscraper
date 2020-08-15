import os
import time
import shutil
import sys
import tempfile
import requests
import logging

from urllib.parse import urlparse
from bs4 import BeautifulSoup

CHUNK_SIZE = 8 * 1024
UPLOAD_FILEPATH = "/mnt/c/Users/sukju/Downloads/avscrap"

log = logging.getLogger("app.main")
handler = logging.StreamHandler()
log.setLevel(logging.INFO)
log.addHandler(handler)


def download_image(image_url):
    res = urlparse(image_url)
    filename = res.path.split("/")[-1]
    log.info("downloading... url=%s", image_url)
    r = requests.get(image_url, stream=True)
    filepath = tempfile.mktemp()
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
            f.write(chunk)

    dest = os.path.join(UPLOAD_FILEPATH, filename)
    log.info("copy file. filename=%s", filename)
    shutil.copy(filepath, dest)

    return dest


def get_post(id):
    image_urls = []
    POST_URL = f"https://avsee09.tv/bbs/board.php?bo_table=community&wr_id={id}"
    log.info("getting post. url=%s", POST_URL)
    res = requests.get(POST_URL)
    # with open("post.html", "r") as f:
    #    text = f.read()
    # f.write(res.text)
    text = res.text
    soup = BeautifulSoup(text, "html.parser")
    images = soup.select("div.view-img img")
    for img in images:
        image_url = img.attrs["src"]
        image_urls.append(image_url)
    return image_urls


def get_list(page=1):
    id_list = []
    FORUM_URL = f"https://avsee09.tv/bbs/board.php?bo_table=community&page={page}"
    log.info("getting list. url=%s", FORUM_URL)
    res = requests.get(FORUM_URL)
    text = res.text
    soup = BeautifulSoup(text, "html.parser")
    res = soup.select("#list-body > li")
    for item in res:
        link = item.select("div.wr-subject > a")
        title = link[0].text.strip()
        link_url = link[0].attrs["href"]
        tag_span = link[0].select("span.tack-icon")
        # 사진 & 영상만
        if "bg-green" not in tag_span[0].attrs["class"]:
            continue
        print(title)
        print(link_url)
        wr_id = link_url.split("wr_id=")[-1]
        wr_id = wr_id.split("&")[0]
        id_list.append(wr_id)

    return id_list


def main():
    id_list = []
    pages = [1, 2, 3, 4, 5]
    for page in pages:
        time.sleep(1)
        res = get_list(page)
        id_list += res
    for wr_id in id_list:
        image_urls = get_post(wr_id)
        for url in image_urls:
            time.sleep(1)
            download_image(url)
    return 0


if __name__ == "__main__":
    exitcode = main()
    sys.exit(exitcode)
