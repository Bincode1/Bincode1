"""Compile open-font outlines for portable SVG text (optional: pip install fonttools)."""
import argparse
import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('body_font', help='LXGW WenKai Regular TTF')
    parser.add_argument('heading_font', help='Caveat TTF')
    args = parser.parse_args()
    # ASCII supports changing dates, counts, repository names and tech stacks.
    texts = (ROOT/'profile.json').read_text(encoding='utf-8')
    texts += (ROOT/'scripts'/'render_artwork.py').read_text(encoding='utf-8')
    chars = sorted(set(texts) | set(chr(i) for i in range(32, 127)))
    result = {}
    for name, path in [('body', args.body_font), ('heading', args.heading_font)]:
        font = TTFont(path)
        glyphs = font.getGlyphSet()
        cmap = font.getBestCmap()
        outlines = {}
        for char in chars:
            if ord(char) not in cmap:
                continue
            glyph = glyphs[cmap[ord(char)]]
            pen = SVGPathPen(glyphs, ntos=lambda n: format(n, '.1f').rstrip('0').rstrip('.') if n else '0')
            glyph.draw(pen)
            outlines[char] = [glyph.width, pen.getCommands()]
        result[name] = {'units': font['head'].unitsPerEm, 'glyphs': outlines}
    out = ROOT/'assets'/'type'
    out.mkdir(exist_ok=True)
    (out/'glyphs.json').write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
