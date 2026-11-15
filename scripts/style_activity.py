"""Restyle a real snk output, keeping its calendar and computed snake route."""
import re
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
    css += '\n@media(prefers-reduced-motion:reduce){.c,.s{animation:none!important}.s{display:none}}'
    style.text = css
    return ET.tostring(root, encoding='unicode')+'\n'

def main():
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    out = ROOT / 'assets'
    out.mkdir(exist_ok=True)
    for mode in PALETTES:
        (out / f'activity-{mode}.svg').write_text(restyle(source, mode), encoding='utf-8')
    print('Saved dark and light activity SVGs; route and calendar preserved.')

if __name__ == '__main__':
    main()
