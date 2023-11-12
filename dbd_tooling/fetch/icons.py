import os
import re
from pathlib import Path
from urllib.request import urlretrieve

Path(f"{os.getcwd()}/data/images/icons").mkdir(parents=True, exist_ok=True)

link_src_pattern = r'([^"]*/images/\w+/\w+/([^/]+)/[^"]+)'
link_src_reg = re.compile(link_src_pattern)

paths = set()
with open(f"{os.getcwd()}/data/icons.txt", encoding="utf-8") as f:
    for line in f:
        paths.add(line.strip())

for p in paths:
    match = link_src_reg.match(p)
    urlretrieve(p, f"data/images/icons/{match.group(2)}")
    print(match.group(2))
