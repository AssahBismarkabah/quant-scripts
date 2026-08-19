import json
import time
from pathlib import Path

import requests

OUT = Path(__file__).parent / 'outputs' / 'trades'
OUT.mkdir(exist_ok=True)
MANIFEST = 'https://beta.kingsets.com/manifest.json'
BASE = 'https://beta.kingsets.com'
MAX_ATTEMPTS = 4
BACKOFF_S = 10


def fetch(url, timeout=120):
    last = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            r = requests.get(url, timeout=timeout, stream=True)
            r.raise_for_status()
            return r
        except Exception as e:
            last = e
            if attempt < MAX_ATTEMPTS:
                time.sleep(BACKOFF_S * 2 ** (attempt - 1))
    raise last


def main():
    m = fetch(MANIFEST).json()
    paths = [f['path'] for f in m['files']
             if f['path'].startswith('kalshi/trades/')
             and f['path'].endswith('DAY.csv.gz')]
    print(f'{len(paths)} daily trade files in manifest', flush=True)
    for p in paths:
        name = Path(p).name
        dest = OUT / name
        if dest.exists() and dest.stat().st_size > 0:
            continue
        tmp = dest.with_suffix('.part')
        try:
            with fetch(BASE + '/' + p) as r, open(tmp, 'wb') as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
            tmp.rename(dest)
            print(f'done {name}', flush=True)
        except Exception as e:
            tmp.unlink(missing_ok=True)
            print(f'FAIL {name}: {e}', flush=True)


if __name__ == '__main__':
    main()