import asyncio
import re
import sqlite3
from aiohttp import ClientSession
from bs4 import BeautifulSoup

EXPLORED_URL = "https://ru.wikipedia.org/wiki/Python"
DEPTH_EXPLORING = 2
DB_NAME = "urls.db"

def run_bd(url, depth, from_url_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    sql = """
            INSERT INTO pages (url, request_depth)
                VALUES (?, ?);
          """
    cursor.execute(sql, (url, depth))
    new_id = cursor.lastrowid
    if from_url_id:
        sql = """
                INSERT INTO refs (from_page_id, link_id)
                    VALUES (?, ?);
              """
        cursor.execute(sql, (from_url_id, new_id))
    conn.commit()
    conn.close()
    return new_id


def findUrls(html):
    bs = BeautifulSoup(html, "html.parser")
    article = bs.find('div', id="mw-content-text")
    if article:
        hrefs = [url_prefix + a['href']
                 for a in article.findAll('a', href=re.compile(r'^/wiki/.*'))]
    else:
        hrefs = []
    return hrefs


async def fetch(session, url, depth, from_url_id):
    if(depth > DEPTH_EXPLORING):
        return
    async with session.get(url) as response:
        status = response.status
        if status != 200:
            return
        new_id = run_bd(url, depth, from_url_id)
        html = await response.text()
        hrefs = findUrls(html)
        tasks = []
        for href in hrefs:
            task = asyncio.ensure_future(
                fetch(session, href, depth + 1, new_id))
            tasks.append(task)
        if tasks:
            await asyncio.wait(tasks)

async def main(url):
    async with ClientSession() as session:
        depth = 1
        from_url = 0
        await fetch(session, url, depth, from_url)
    print("Done!")

if __name__ == "__main__":
    url_prefix = EXPLORED_URL[:EXPLORED_URL.find('/wiki/')]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(EXPLORED_URL))
