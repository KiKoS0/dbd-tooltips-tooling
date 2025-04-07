import os
from pathlib import Path
from urllib import request

from dbd_tooling.fetch.utils import browser_user_agent
from dbd_tooling.fetch.shared import path_src_reg

Path(f"{os.getcwd()}/data/images/icons").mkdir(parents=True, exist_ok=True)

paths = set()
with open(f"{os.getcwd()}/data/icons.txt", encoding="utf-8") as f:
    for line in f:
        paths.add(line.strip())

for p in paths:
    match = path_src_reg.match(p)
    req = request.Request(p, data=None, headers={"User-Agent": browser_user_agent()})

    file_name = match.group(2)

    with open(f"data/images/icons/{file_name}", "wb") as f:
        f.write(request.urlopen(req).read())

    print(file_name)
