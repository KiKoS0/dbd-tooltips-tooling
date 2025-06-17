import json
from pathlib import Path

import aiohttp
import requests
from bs4 import BeautifulSoup
import asyncio
import random

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    }

    soup = None
    max_retries = 5
    base_delay = 1  # Start with 1 second
    total_wait = 0
    max_total_wait = 45

    for attempt in range(max_retries + 1):
        # Add random delay between 0.5-2 seconds to appear more human
        if attempt > 0:
            human_delay = random.uniform(0.5, 2.0)
            await asyncio.sleep(human_delay)

        try:
            async with session.get(link, headers=headers, max_redirects=30) as page:
                soup = BeautifulSoup(await page.text(), "html.parser")
                return cb(soup, link)
        except aiohttp.client_exceptions.TooManyRedirects:
            page = requests.get(link, headers=headers, timeout=30)
            soup = BeautifulSoup(page.text, "html.parser")
            return cb(soup, link)
        except Exception as e:
            if attempt == max_retries:
                # Final attempt failed - dump soup and raise
                if soup is not None:
                    with open("dump_locale.html", "w", encoding="utf-8") as f:
                        f.write(str(soup))
                    print(f"Final attempt failed. Exception: {e}")
                    print("HTML content dumped to dump_locale.html")
                    
                    # Don't fail entirely, some pages are just broken so just let the cb handle(skip) them
                    return cb(soup, link)
                raise

            # Calculate delay for backoff with jitter
            base_backoff = base_delay * (2**attempt)
            jitter = random.uniform(0.8, 1.2)  # Add 20% jitter
            delay = min(base_backoff * jitter, max_total_wait - total_wait)
            if total_wait + delay > max_total_wait:
                delay = max_total_wait - total_wait

            if delay <= 0:
                # No more time left for retries
                if soup is not None:
                    with open("dump_locale.html", "w", encoding="utf-8") as f:
                        f.write(str(soup))
                    print(f"Max wait time exceeded. Exception: {e}")
                    print("HTML content dumped to dump_locale.html")
                raise

            print(
                f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f} seconds..."
            )
            await asyncio.sleep(delay)
            total_wait += delay
