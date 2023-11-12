import json
import re
import unicodedata
from pathlib import Path

import minify_html
from bs4 import BeautifulSoup


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def read_json_dic(filepath):
    with open(filepath, encoding="utf-8") as handle:
        dictdump = json.loads(handle.read())
    return dictdump


def file_exists(filename):
    return Path(filename).is_file()


def fix_description(html):
    sp = BeautifulSoup(html, "html.parser")
    formatted_html = sp("div", {"class": "formattedPerkDesc"})[0]
    return fix_description_icons(formatted_html.prettify(formatter="html"))


def fix_description_icons(html):
    """Fixing the lazy loaded icons assigning url to img['src']
    and clearing not needed attrs
    """
    sp = BeautifulSoup(html, "html.parser")
    filter_attr_name_set = {
        "data-image-name",
        "data-image-key",
        "data-src",
        "class",
        "loading",
    }
    imgs = sp.find_all("img")
    for img in imgs:
        img["src"] = img["data-src"]
        drop_key_set = set(img.attrs) & filter_attr_name_set
        for key in drop_key_set:
            del img.attrs[key]

    return sp.prettify(formatter="html")


def minify(html):
    return minify_html.minify(
        html,
        minify_js=True,
        minify_css=True,
        remove_processing_instructions=True,
        keep_comments=False,
        keep_spaces_between_attributes=False,
    )
