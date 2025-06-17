import asyncio

from dbd_tooling.fetch.locales.shared import (
    get_perks,
    perk_has_language,
    perks_locale_folder_path,
    save_perks_metadata,
)
from dbd_tooling.fetch.utils import read_json_dic
from dbd_tooling.fetch.shared import (
    killers_perks_json,
    survivors_perks_json,
)

survivors_locale_perks_json = f"{perks_locale_folder_path}/survivors_de.json"
killers_locale_perks_json = f"{perks_locale_folder_path}/killers_de.json"


def get_perk_data_internal(soup, link):
    tables = soup.find_all("table", {"class": "wikitable"})
    perk_table = tables[0]
    rows = perk_table.find_all("tr")

    name_row = rows[0].find_all("th")[1]

    name = try_get_name(name_row)
    print(name)

    desc = rows[0].find_all("td")[0].encode_contents().decode("utf-8")
    return (name, desc)


def try_get_name(name_row):
    smalls = name_row.find_all("small")
    if smalls:
        for child in smalls:
            child.extract()

    return name_row.text.strip()


async def main():
    survivor_perks = read_json_dic(survivors_perks_json)
    killer_perks = read_json_dic(killers_perks_json)

    having_translations = {
        k: {"link": v["locales"]["de"]}
        for k, v in survivor_perks.items()
        if perk_has_language("de", v)
    }
    data = await get_perks(
        having_translations,
        # {
        #     "ww": {
        #         "link": "https://deadbydaylight.wiki.gg/de/wiki/Der_Ruf_einer_Krankenschwester"
        #     },
        #     "ww2": {
        #         "link": "https://deadbydaylight.wiki.gg/de/wiki/Wir_schaffen_das"
        #     },
        # },
        get_perk_data_internal,
    )
    save_perks_metadata(data, survivors_locale_perks_json)

    having_translations = {
        k: {"link": v["locales"]["de"]}
        for k, v in killer_perks.items()
        if perk_has_language("de", v)
    }

    data = await get_perks(having_translations, get_perk_data_internal)
    save_perks_metadata(data, killers_locale_perks_json)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
