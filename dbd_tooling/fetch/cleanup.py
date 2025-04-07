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


def main():
    if not file_exists(powers_perks_json):
        print(f"error: {powers_perks_json} file does not exist")
        sys.exit(1)

    killers = read_json_dic(powers_perks_json)

    if os.path.exists(powers_perks_json):
        os.remove(powers_perks_json)
    save_powers_metadata(killers)


if __name__ == "__main__":
    main()
