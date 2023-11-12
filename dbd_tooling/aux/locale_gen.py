import json
import os
import re

from dbd_tooling.fetch.shared import (
    DATA_FOLDER_PATH,
)

file_names = os.listdir("dbd_tooling/fetch/locales")

supported_locales = ["en"]

locale_regex = re.compile(r"(\w{2})\.py")
for file_name in file_names:
    if match := locale_regex.match(file_name):
        supported_locales.append(match.group(1).lower())

with open(f"{DATA_FOLDER_PATH}/supported_locales.json", "w", encoding="utf-8") as fp:
    json.dump(supported_locales, fp, indent=4, sort_keys=True)
