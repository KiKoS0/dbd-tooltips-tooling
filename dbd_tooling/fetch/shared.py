import re

DATA_FOLDER_PATH = "data"
IMAGES_FOLDER_PATH = f"{DATA_FOLDER_PATH}/images"
PERKS_URL = "https://deadbydaylight.fandom.com/wiki/Perks"

perks_folder_path = f"{IMAGES_FOLDER_PATH}/perks"

survivors_perks_json = f"{DATA_FOLDER_PATH}/survivors.json"
killers_perks_json = f"{DATA_FOLDER_PATH}/killers.json"
powers_perks_json = f"{DATA_FOLDER_PATH}/powers.json"


survivors_perks_path = f"{perks_folder_path}/survivors"
killers_perks_path = f"{perks_folder_path}/killers"

LINK_SRC_PATTERN = r'src="([^"]*/images/\w+/\w+/([^/]+)/[^"]+)"'
link_src_reg = re.compile(LINK_SRC_PATTERN)

addons_perks_path = f"{IMAGES_FOLDER_PATH}/addons"
powers_perks_path = f"{IMAGES_FOLDER_PATH}/powers"
