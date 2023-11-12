import asyncio
import re

from dbd_tooling.fetch.locales.shared import (
    get_perks,
    perk_has_language,
    perks_locale_folder_path,
    save_perks_metadata,
)
from dbd_tooling.fetch.shared import (
    LINK_SRC_PATTERN,
)
from dbd_tooling.fetch.utils import fix_description, minify, read_json_dic
from dbd_tooling.fetch.shared import (
    killers_perks_json,
    survivors_perks_json,
)

survivors_locale_perks_json = f"{perks_locale_folder_path}/survivors_fr.json"
killers_locale_perks_json = f"{perks_locale_folder_path}/killers_fr.json"


def get_perk_data_internal(soup, link):
    try:
        tables = soup.find_all("table", {"class": "wikitable"})
        perk_table = tables[0]
        rows = perk_table.find_all("tr")

        name = soup.find_all("h1", {"id": "firstHeading"})[0].text.strip()

        desc = fix_description(
            rows[3].find_all("td")[0].encode_contents().decode("utf-8")
        )

        desc = re.sub(
            LINK_SRC_PATTERN, lambda x: f'src="images/icons/{x.group(2)}"', desc
        )

        desc = minify(desc)

        print(name)

        return (name, desc)
    except:
        print(f"Failed parsing: {link} Skipping...")
        return (None, None)


async def main():
    survivor_perks = read_json_dic(survivors_perks_json)
    killer_perks = read_json_dic(killers_perks_json)

    having_translations = {
        k: {"link": v["locales"]["fr"]}
        for k, v in survivor_perks.items()
        if perk_has_language("fr", v)
    }

    data = await get_perks(
        having_translations,
        get_perk_data_internal,
    )
    save_perks_metadata(data, survivors_locale_perks_json)

    having_translations = {
        k: {"link": v["locales"]["fr"]}
        for k, v in killer_perks.items()
        if perk_has_language("fr", v)
    }

    data = await get_perks(having_translations, get_perk_data_internal)
    save_perks_metadata(data, killers_locale_perks_json)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
