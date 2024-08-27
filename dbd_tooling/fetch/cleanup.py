import os
import sys
from dbd_tooling.fetch.powers_addons import save_powers_metadata

from dbd_tooling.fetch.shared import (
    powers_perks_json,
)
from dbd_tooling.fetch.utils import (
    file_exists,
    read_json_dic,
)


def _remove_power_imgs(dic, item, until):
    imgs = dic[item]["power_imgs_paths"]

    keep = imgs[:until]
    remove = imgs[until:]

    for r in remove:
        if os.path.exists(r):
            os.remove(r)

    dic[item]["power_imgs_paths"] = keep
    return dic


def main():
    if not file_exists(powers_perks_json):
        print(f"error: {powers_perks_json} file does not exist")
        sys.exit(1)

    killers = read_json_dic(powers_perks_json)

    dic = _remove_power_imgs(killers, "Pig", 1)
    dic = _remove_power_imgs(killers, "Knight", 3)
    dic = _remove_power_imgs(killers, "Jeffrey_Hawk", 2)

    if os.path.exists(powers_perks_json):
        os.remove(powers_perks_json)
    save_powers_metadata(dic)


if __name__ == "__main__":
    main()
