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
    return fix_description_icons(html)


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
        key = "data-src" if "data-src" in img.attrs else "src"
        img["src"] = absolute_link(img[key])

        drop_key_set = set(img.attrs) & filter_attr_name_set
        for key in drop_key_set:
            del img.attrs[key]

    # There exists two icons for each platform (PC and mobile).
    # The PC one had always been hidden by default in style but not
    # anymore. it's now done with external CSS classes.
    # So this should keep the old behavior.
    for span in sp.find_all("span", {"class": "pcView pcIconLink"}):
        span["style"] = "display: none;" + span.get("style", "")

    return sp.prettify(formatter="html")


def absolute_link(link):
    return (
        link if link.startswith("https://") else f"https://deadbydaylight.wiki.gg{link}"
    )


def minify(html):
    return minify_html.minify(
        html,
        minify_js=True,
        minify_css=True,
        remove_processing_instructions=True,
        keep_comments=False,
        keep_spaces_between_attributes=False,
    )


addon_rarities = ["common", "uncommon", "very-rare", "ultra-rare", "rare"]


def addon_rarity(element):
    background_element_classes = (
        element.select(".game-element-container.addon-container")[0]
        .find(True, recursive=False)
        .get("class")
    )
    rarity_match = None
    for rarity in addon_rarities:
        if any(
            re.search(rf"\b{rarity}\b", class_name)
            for class_name in background_element_classes
        ):
            rarity_match = rarity
            break

    if rarity_match is None:
        raise ValueError(
            f"No addon rarity found. for: {element}\nclasses: {background_element_classes}"
        )

    return rarity_match


def browser_user_agent():
    """Return a random user agent string."""
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0"
