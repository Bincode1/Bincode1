"""Vendor upstream SVG icons and their license; no runtime CDN dependency."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'icons'
REV = '32fe1d3b3f36ad11f90ab94f7db59738139c2bf6'
BASE = f'https://raw.githubusercontent.com/devicons/devicon/{REV}'
ICONS = {
    'java': 'java/java-original.svg',
    'python': 'python/python-original.svg',
    'vue': 'vuejs/vuejs-original.svg',
    'typescript': 'typescript/typescript-original.svg',
    'fastapi': 'fastapi/fastapi-original.svg',
    'git': 'git/git-original.svg',
}

def download(item):
    name, path = item
    url = f'{BASE}/icons/{path}'
    with urlopen(url, timeout=30) as response:
        data = response.read()
    (ROOT / f'{name}.svg').write_bytes(data)
    return {'file': f'{name}.svg', 'source': url, 'sha256': hashlib.sha256(data).hexdigest()}

ROOT.mkdir(parents=True, exist_ok=True)
with ThreadPoolExecutor(max_workers=6) as pool:
    manifest = list(pool.map(download, ICONS.items()))
with urlopen(f'{BASE}/LICENSE', timeout=30) as response:
    (ROOT / 'LICENSE.devicon').write_bytes(response.read())
lucide_rev = '55782beff3a0133df79c417eb68f96e8f19e2404'
lucide_base = f'https://raw.githubusercontent.com/lucide-icons/lucide/{lucide_rev}'
for name in ['clapperboard', 'map', 'code-xml']:
    url = f'{lucide_base}/icons/{name}.svg'
    with urlopen(url, timeout=30) as response:
        data = response.read().decode('utf-8').replace('stroke="currentColor"', 'stroke="#4493f8"').encode('utf-8')
    (ROOT / f'{name}.svg').write_bytes(data)
    manifest.append({'file': f'{name}.svg', 'source': url, 'modification': 'Set stroke to GitHub blue #4493f8 for dark and light backgrounds.', 'sha256': hashlib.sha256(data).hexdigest()})
with urlopen(f'{lucide_base}/LICENSE', timeout=30) as response:
    (ROOT / 'LICENSE.lucide').write_bytes(response.read())
(ROOT / 'SOURCES.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(f'Downloaded {len(manifest)} SVGs from Devicon and Lucide, with licenses.')
