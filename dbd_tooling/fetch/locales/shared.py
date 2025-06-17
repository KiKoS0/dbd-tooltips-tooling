import json
from pathlib import Path

import aiohttp
import requests
from bs4 import BeautifulSoup

from time import sleep

from dbd_tooling.fetch.shared import (
    DATA_FOLDER_PATH,
)
from dbd_tooling.fetch.utils import file_exists

perks_locale_folder_path = f"{DATA_FOLDER_PATH}/locales"


async def get_perks(perks, cb):
    res = {}
    async with aiohttp.ClientSession() as session:
        for k, v in perks.items():
            name, desc = await get_perk_data(session, v["link"], cb)
            if name and desc:
                res[k] = v
                res[k]["name"] = name
                res[k]["desc"] = desc

                sleep(1)  # Avoid rate limiting
            else:
                continue
    return res


def perk_has_language(lang, perk):
    return lang in perk["locales"].keys()


def save_perks_metadata(perks, file_path):
    Path(perks_locale_folder_path).mkdir(parents=True, exist_ok=True)
    if not file_exists(file_path):
        print(f"Dumping perks to {file_path}")
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(perks, fp, indent=4, sort_keys=True)


async def get_perk_data(session, link, cb):
    try:
        async with session.get(link, max_redirects=30) as page:
            soup = BeautifulSoup(await page.text(), "html.parser")
            return cb(soup, link)

    except aiohttp.client_exceptions.TooManyRedirects:
        page = requests.get(link, timeout=30)
        soup = BeautifulSoup(page.text, "html.parser")
        return cb(soup, link)
