import json
from pathlib import Path
from dbd_tooling.fetch.shared import DATA_FOLDER_PATH
from dbd_tooling.fetch.utils import file_exists


feature_flags_path = f"{DATA_FOLDER_PATH}/feature_flags.json"

feature_flags = {"disable-bugged-video-in-firefox": True}

Path(DATA_FOLDER_PATH).mkdir(parents=True, exist_ok=True)
if not file_exists(feature_flags_path):
    print(f"Dumping feature flags to {feature_flags_path}")
    with open(feature_flags_path, "w", encoding="utf-8") as fp:
        json.dump(feature_flags, fp, indent=4, sort_keys=True)
