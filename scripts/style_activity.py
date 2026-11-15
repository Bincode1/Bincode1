"""Restyle a real snk output, keeping its calendar and computed snake route."""
import re
import argparse
import hashlib
import json
from datetime import datetime
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ET.register_namespace('', 'http://www.w3.org/2000/svg')
NS = '{http://www.w3.org/2000/svg}'
ROOT = Path(__file__).resolve().parents[1]
PALETTES = {
    'light': ['#d8dee4', '#57606a', '#eff2f5', '#eff2f5', '#d6e9df', '#a0cdb3', '#65a985', '#357454'],
    'dark': ['#242d35', '#d4e4d9', '#161e26', '#161e26', '#213e32', '#32654a', '#52926b', '#82b68d'],
}

def restyle(source, mode):
    root = ET.fromstring(source)
    root.set('viewBox', '-16 -24 880 152')
    root.set('width', '880')
    root.set('height', '152')
    root.set('role', 'img')
    root.set('aria-label', 'GitHub contributions for Bincode1')
    title = ET.Element(NS+'title')
    title.text = 'Bincode1 · GitHub contributions'
    root.insert(0, title)
    style = root.find(NS+'style')
    if style is None:
        raise ValueError('Expected snk SVG with its animation stylesheet.')
    keys = ['cb', 'cs', 'ce', 'c0', 'c1', 'c2', 'c3', 'c4']
    variables = ':root{'+''.join(f'--{k}:{v};' for k,v in zip(keys,PALETTES[mode]))+'}'
    css = re.sub(r':root\{[^}]+\}', variables, style.text)
    css = re.sub(r'\b\d+ms\b', '32000ms', css)
    # Keep the actual contribution cells at their original coordinates, with
    # softer corners. The lower collection meter is intentionally removed.
    for parent in root.iter():
        for child in list(parent):
            classes = child.get('class', '').split()
            if 'u' in classes:
                parent.remove(child)
            elif 'c' in classes:
                child.set('rx', '2.5')
                child.set('ry', '2.5')
    # The contribution map is persistent; only the snake follows its route.
    # Override the upstream per-cell fill animations without changing the
    # original contribution-level fills or any snake keyframes.
    css += '\n.c{animation:none!important}'
    css += '\n@media(prefers-reduced-motion:reduce){.c,.s{animation:none!important}.s{display:none}}'
    style.text = css
    return ET.tostring(root, encoding='unicode')+'\n'

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('--generated-at', help='UTC time from the workflow that just fetched this source; omit when restyling an existing snapshot.')
    args = parser.parse_args(argv)
    source = Path(args.source).read_text(encoding='utf-8')
    out = ROOT / 'assets'
    out.mkdir(exist_ok=True)
    for mode in PALETTES:
        (out / f'activity-{mode}.svg').write_text(restyle(source, mode), encoding='utf-8')
    if args.generated_at:
        generated = datetime.fromisoformat(args.generated_at.replace('Z', '+00:00'))
        if generated.tzinfo is None:
            raise ValueError('Generation time must include a timezone.')
        cells = [e for e in ET.fromstring(source).iter() if 'c' in e.get('class', '').split()]
        metadata = {
            'generated_at': args.generated_at,
            'source': 'GitHub public profile contribution calendar',
            'source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
            'days': len(cells),
            'active_days': sum(len(e.get('class', '').split()) > 1 for e in cells),
        }
        (out / 'activity.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    print('Saved dark and light activity SVGs; route and calendar preserved.')

if __name__ == '__main__':
    main()
