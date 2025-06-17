import asyncio
import json
import re
from pathlib import Path
from urllib.parse import unquote
from urllib.request import urljoin

import aiohttp
import requests
from bs4 import BeautifulSoup

from dbd_tooling.fetch.shared import (
    DATA_FOLDER_PATH,
    LINK_SRC_PATTERN,
    PERKS_URL,
    killers_perks_json,
    killers_perks_path,
    link_src_reg,
    perks_folder_path,
    survivors_perks_json,
    survivors_perks_path,
)
from dbd_tooling.fetch.im_gen import generate_perk_frames, generate_perk_gif
from dbd_tooling.fetch.utils import (
    file_exists,
    fix_description,
    fix_description_icons,
    read_json_dic,
    remove_extension_if_exists,
    slugify,
    absolute_link,
)

icons = set()

skip_perks = [
    "Surge",
    "Mindbreaker",
    "Cruel_Limits",
    "Better_Together",
    "Fixated",
    "Camaraderie",
]


def get_table_rows(table):
    perks = {}
    characters = {}
    for row in table.find_all("tr")[1:]:
        columns = row.find_all("th")
        link = columns[1].find("a")
        perk_link = link["href"]
        perk_id = unquote(perk_link).replace("/wiki/", "")
        perk_name = link.text.strip()
        perk_character = (
            columns[2].find("a")["title"].strip() if columns[2].find("a") else "ALL"
        )
        if perk_id not in skip_perks:
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


async def get_perk_data(session, rel_link):
    link = urljoin(PERKS_URL, rel_link)
    try:
        async with session.get(link, max_redirects=30) as page:
            soup = BeautifulSoup(await page.text(), "html.parser")
            return get_perk_data_internal(soup)

    except aiohttp.client_exceptions.TooManyRedirects:
        page = requests.get(link, timeout=30)
        soup = BeautifulSoup(page.text, "html.parser")
        return get_perk_data_internal(soup)


def get_perk_data_internal(soup):
    img_col = soup.find("div", {"class": "perkIcon"}).find(
        "div", {"class": "perkIconImage"}
    )
    desc = soup.find("div", {"class": "perkDesc"}).encode_contents().decode("utf-8")
    desc = fix_description(desc)
    (wrapped_changelogs, changelogs) = get_perk_changelog(soup)
    desc += wrapped_changelogs

    all_matches = link_src_reg.findall(desc)
    _ = [icons.add(m[0]) for m in all_matches]
    desc = re.sub(link_src_reg, lambda x: f'src="images/icons/{x.group(2)}"', desc)

    all_matches = link_src_reg.findall(changelogs)
    _ = [icons.add(m[0]) for m in all_matches]
    changelogs = fix_description_icons(changelogs)
    changelogs = re.sub(
        LINK_SRC_PATTERN, lambda x: f'src="images/icons/{x.group(2)}"', changelogs
    )

    if img_soup := img_col.find("img"):
        perk_icon_webp_alt = remove_extension_if_exists(
            img_soup["alt"].replace("IconPerks", "").strip().capitalize()
        )
        perk_icon_webp_src = img_col.find("img")

        img_src_key = "data-src" if perk_icon_webp_src.has_attr("data-src") else "src"
        perk_icon_webp_src = absolute_link(perk_icon_webp_src[img_src_key])

        perk_icon_webp_src = re.sub(
            r"latest\/.*$", "latest/scale-to-width-down/256", perk_icon_webp_src
        )
        print(f"perk = {perk_icon_webp_alt}  = {perk_icon_webp_src}")
    else:
        perk_icon_webp_alt = None
        perk_icon_webp_src = None

    # Translations
    langs = soup.find_all("a", {"class": "interlanguage-link-target"})
    langs = {lang["lang"]: absolute_link(lang["href"]) for lang in langs}

    return (perk_icon_webp_alt, perk_icon_webp_src, desc, changelogs, langs)


patch_notes_to_include = [
    "8.5.0",
    "8.5.1",
    "8.5.2",
    "8.6.0",
    "8.6.1",
    "8.6.2",
    "8.7.0",
    "8.7.1",
    "8.7.2",
    "9.0.0",
]


def get_perk_changelog(soup):
    res = ""
    html_to_add = r'<hr style="opacity:0.2" noshade="noshade"><div class="changelogs">'

    for patch_version in patch_notes_to_include:
        if latest_patch_span := soup.find("span", {"id": f"Patch_{patch_version}"}):
            patch_link_header = latest_patch_span.find("a") or latest_patch_span.find(
                "span"
            )
            if patch_link_header:
                patch_link_header.name = "a"
                patch_link_header["style"] = "text-decoration: none;color: #e2ce97;"
                res += latest_patch_span.prettify(formatter="html")

                # Sometimes the patch notes have only one element which is put simply in a <p> tag
                patch_notes = latest_patch_span.parent.find_next_sibling(
                    "ul"
                ) or latest_patch_span.parent.find_next_sibling("p")

                res += patch_notes.prettify(formatter="html")
    return (html_to_add + res + "</div>" if res != "" else "", res)

# ASYNC VERSION it's triggering cloudflare rate limiting

# async def get_perks(perks):
#     res = {}
#     asynctasks = []
#     async with aiohttp.ClientSession() as session:
#         for k, v in perks.items():
#             task = get_perk_data(session, v["link"])
#             asynctasks.append(asyncio.create_task(task))
#         task_results = await asyncio.gather(*asynctasks)

#     for index, (k, v) in enumerate(perks.items()):
#         res[k] = v
#         (icon_alt, icon_src, desc, changelogs, locales) = task_results[index]
#         res[k]["icon_alt"] = icon_alt
#         res[k]["icon_src"] = icon_src
#         res[k]["description"] = desc
#         res[k]["changelogs"] = changelogs
#         res[k]["locales"] = locales
#         print(res[k]["icon_alt"])
#     return res


async def get_perks(perks):
    res = {}
    async with aiohttp.ClientSession() as session:
        for k, v in perks.items():
            icon_alt, icon_src, desc, changelogs, locales = await get_perk_data(
                session, v["link"]
            )

            res[k] = v
            res[k]["icon_alt"] = icon_alt
            res[k]["icon_src"] = icon_src
            res[k]["description"] = desc
            res[k]["changelogs"] = changelogs
            res[k]["locales"] = locales
            print(res[k]["icon_alt"])

    return res


def save_perks_metadata(perks, file_path):
    Path(perks_folder_path).mkdir(parents=True, exist_ok=True)
    if not file_exists(file_path):
        print(f"Dumping perks to {file_path}")
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(perks, fp, indent=4, sort_keys=True)


async def dl_perk_icon(session, folder_path, k, v):
    res = v
    perk_folder_path = f"{folder_path}/{slugify(k)}"
    Path(perk_folder_path).mkdir(parents=True, exist_ok=True)

    if v["icon_alt"]:
        icon_path = f"{perk_folder_path}/{v['icon_alt']}.png"
        if not file_exists(icon_path):
            print(f"Downloading {v['icon_src']}")
            async with session.get(v["icon_src"]) as resp:
                f = open(icon_path, "wb")
                f.write(await resp.read())
                f.close()

        res["frames"] = generate_perk_frames(icon_path, perk_folder_path)
        res["icon"] = icon_path
        res["gif"] = f"{perk_folder_path}/{v['icon_alt']}.gif"

        generate_perk_gif(res["frames"], res["gif"])
    return (k, v)


async def dl_perks_icons(perks, folder_path):
    res = {}
    asynctasks = []
    async with aiohttp.ClientSession() as session:
        for k, v in perks.items():
            task = dl_perk_icon(session, folder_path, k, v)
            asynctasks.append(asyncio.create_task(task))
        task_results = await asyncio.gather(*asynctasks)
    res = {key: val for key, val in task_results}
    return res


async def main():
    page = requests.get(PERKS_URL, timeout=30)
    soup = BeautifulSoup(page.text, "html.parser")
    res = (
        soup.find("div", {"id": "mw-content-text"})
        .find("div")
        .findChildren(
            "table", {"class": "wikitable overflowScroll sortable"}, recursive=False
        )
    )
    if len(res) != 2:
        print("There is an error somewhere")
        raise RuntimeError("More than 2 tables in the wiki found")
    surv_table, kill_table = [res[0], res[1]]
    surv_perks, _surv_characters = get_table_rows(surv_table)
    kill_perks, _kill_characters = get_table_rows(kill_table)

    if not file_exists(killers_perks_json):
        kill_perks = await get_perks(kill_perks)
    else:
        kill_perks = read_json_dic(killers_perks_json)

    kill_perks = await dl_perks_icons(kill_perks, killers_perks_path)

    save_perks_metadata(kill_perks, killers_perks_json)

    if not file_exists(survivors_perks_json):
        surv_perks = await get_perks(surv_perks)
    else:
        surv_perks = read_json_dic(survivors_perks_json)

    surv_perks = await dl_perks_icons(surv_perks, survivors_perks_path)

    save_perks_metadata(surv_perks, survivors_perks_json)

    for i in icons:
        print(i)

    with open(f"{DATA_FOLDER_PATH}/icons.txt", "w", encoding="utf-8") as f:
        for i in icons:
            f.write(f"{i}\n")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
