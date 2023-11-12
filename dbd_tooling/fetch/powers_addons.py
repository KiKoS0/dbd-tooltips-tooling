import os
import asyncio
import json
import re
from pathlib import Path
from urllib import request
from urllib.parse import unquote
from urllib.request import urljoin

import aiohttp
import requests
from bs4 import BeautifulSoup

from dbd_tooling.fetch.shared import (
    DATA_FOLDER_PATH,
    LINK_SRC_PATTERN,
    PERKS_URL,
    addons_perks_path,
    link_src_reg,
    powers_perks_json,
    powers_perks_path,
)
from dbd_tooling.fetch.utils import file_exists, slugify

icons = set()


def poor_demo(characters):
    characters["Demogorgon"] = {"name": "Demogorgon", "link": "/wiki/The_Demogorgon"}
    return characters


def get_killer_powers(characters):
    res = {}
    for k, v in poor_demo(characters).items():
        res[k] = v
        res[k]["power_name"], res[k]["power_imgs"], res[k]["addons"] = get_killers_data(
            v["link"]
        )

    return res


def dl_power_icons(killers):
    res = {}
    for k, v in killers.items():
        res[k] = v
        power_folder_path = f"{powers_perks_path}/{slugify(k)}"
        Path(power_folder_path).mkdir(parents=True, exist_ok=True)
        i = 0
        power_paths = []
        for img_link in v["power_imgs"]:
            power_img_path = f"{power_folder_path}/{slugify(v['name'])}_{i}.png"
            power_paths.append(power_img_path)
            i += 1
            if not file_exists(power_img_path):
                print(f"Downloading {img_link}")
                f = open(power_img_path, "wb")
                f.write(request.urlopen(img_link).read())
                f.close()
        res[k]["power_imgs_paths"] = power_paths
    return res


async def dl_addons_icons(session, k, v):
    res = v
    addon_folder_path = f"{addons_perks_path}/{slugify(k)}"
    Path(addon_folder_path).mkdir(parents=True, exist_ok=True)
    for addon_id, addon_data in v["addons"].items():
        img_link = addon_data["img_src"]
        addon_img_path = f"{addon_folder_path}/{slugify(addon_data['name'])}.png"
        if not file_exists(addon_img_path):
            print(f"Downloading {img_link}")
            try:
                async with session.get(img_link) as resp:
                    f = open(addon_img_path, "wb")
                    f.write(await resp.read())
                    f.close()
            except:
                print(f"Failed to download: {img_link}")
        else:
            print(f"Exists: {img_link}")
        res["addons"][addon_id]["img_path"] = os.path.relpath(
            addon_img_path, os.getcwd()
        )
    return (k, res)


async def dl_addons_icons_async(killers):
    res = {}
    asynctasks = []
    async with aiohttp.ClientSession() as session:
        for k, v in killers.items():
            task = dl_addons_icons(session, k, v)
            asynctasks.append(asyncio.create_task(task))
        task_results = await asyncio.gather(*asynctasks)
    res = {key: val for key, val in task_results}
    return res


def save_powers_metadata(powers):
    Path(DATA_FOLDER_PATH).mkdir(parents=True, exist_ok=True)
    if not file_exists(powers_perks_json):
        print(f"Dumping powers to {powers_perks_json}")
        with open(powers_perks_json, "w", encoding="utf-8") as fp:
            json.dump(powers, fp, indent=4, sort_keys=True)


def fix_nemesis_link(link):
    return "/wiki/Nemesis_T-Type" if link == "/wiki/Nemesis" else link


def get_killers_data(link):
    link = fix_nemesis_link(link)
    print(link)
    link = urljoin(PERKS_URL, link)
    page = requests.get(link, timeout=30)
    soup = BeautifulSoup(page.text, "html.parser")
    regex = re.compile(r"Power:_(.*)$")
    name_regex = re.compile(r"Power: (.*)$")
    power_spans = soup.find_all("span", {"id": regex})
    correct_span = power_spans[0] if len(power_spans) < 2 else power_spans[1]
    power_name = name_regex.match(correct_span.text.strip()).group(1)

    power_imgs = []
    power_img = correct_span.parent.find_next_sibling("div", {"class": "floatright"})
    while power_img is not None:
        power_img_link = power_img.find("a")
        if power_img_link.find("img") is not None:
            power_img_link = power_img.find("a")["href"].replace(
                "latest", "latest/scale-to-width-down/256"
            )
            power_imgs.append(power_img_link)
        power_img = power_img.find_next_sibling("div", {"class": "floatright"})

    addons = get_killer_addons(soup)

    return (power_name, power_imgs, addons)


def get_killer_addons(soup):
    regex = re.compile(r"Add-ons_(.*)$")
    addon_span = soup.find("span", {"id": regex})
    addon_table = addon_span.parent.find_next_sibling("table", {"class": "wikitable"})
    addons = {}
    for row in addon_table.find_all("tr")[1:]:
        columns = row.find_all("th")
        link = columns[1].find("a")
        addon_link = link["href"]
        addon_id = unquote(addon_link).replace("/wiki/", "")
        addon_name = link.text.strip()
        addon_description = row.find("td")

        imgs = addon_description.find_all("img")
        for img in imgs:
            img["src"] = img["data-src"]

        addon_description = addon_description.encode_contents().decode("utf-8")

        all_matches = link_src_reg.findall(addon_description)
        _ = [icons.add(m[0]) for m in all_matches]
        addon_description = re.sub(
            LINK_SRC_PATTERN,
            lambda x: f'src="images/icons/{x.group(2)}"',
            addon_description,
        )

        if img_soup := columns[0].find("img"):
            perk_icon_webp_alt = img_soup["alt"]
            perk_icon_webp_src = (
                img_soup["src"]
                if img_soup["src"].startswith("https")
                else img_soup["data-src"]
            )
            # Get a larger 256x256 image
            perk_icon_webp_src = re.sub(r"\/\d+\?cb\=", r"/256?cb=", perk_icon_webp_src)
        else:
            perk_icon_webp_alt = None
            perk_icon_webp_src = None

        addons[addon_id] = {
            "name": addon_name,
            "link": addon_link,
            "description": addon_description,
            "img_src": perk_icon_webp_src,
            "img_alt": perk_icon_webp_alt,
        }
    return addons


def get_table_rows(table):
    perks = {}
    characters = {}
    for row in table.find_all("tr")[1:]:
        columns = row.find_all("th")
        link = columns[1].find("a")
        perk_link = link["href"]
        perk_id = unquote(perk_link).replace("/wiki/", "")
        perk_name = link.text.strip()
        perk_character = columns[2].find("a").text if columns[2].find("a") else "ALL"

        perks[perk_id] = {
            "name": perk_name,
            "link": perk_link,
            "character": perk_character,
        }
        if link := columns[2].find("a"):
            character_href = link["href"]
            character_id = unquote(character_href).replace("/wiki/", "")
            character_name = link.text.strip()
            characters[character_id] = {
                "name": character_name,
                "link": character_href,
            }
    return perks, characters


async def main():
    page = requests.get(PERKS_URL, timeout=30)
    soup = BeautifulSoup(page.text, "html.parser")
    res = (
        soup.find("div", {"id": "mw-content-text"})
        .find("div")
        .findChildren("table", {"class": "wikitable sortable"}, recursive=False)
    )
    if len(res) != 2:
        print("There is an error somewhere")
        raise RuntimeError("More than 2 tables in the wiki found")
    surv_table, kill_table = [res[0], res[1]]
    kill_perks, kill_characters = get_table_rows(kill_table)

    # Filter out killers (early on release) that don't have addons
    # del kill_characters['Dredge']

    kill_characters = get_killer_powers(kill_characters)
    dl_power_icons(kill_characters)
    kill_characters = await dl_addons_icons_async(kill_characters)
    save_powers_metadata(kill_characters)

    for i in icons:
        print(i)
    with open(f"{DATA_FOLDER_PATH}/icons.txt", "a", encoding="utf-8") as f:
        for i in icons:
            f.write(f"{i}\n")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
