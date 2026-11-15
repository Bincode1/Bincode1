"""Render the approved paper-and-pencil profile as self-contained GitHub SVGs."""
import base64
from datetime import date, timedelta
from html import escape
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
PALETTES = {
    'light': dict(bg='#ffffff', fg='#41483c', muted='#6c7667', paper='#fff9eb', chart='#fffdf6', ink='#68765c', line='#d5dacd', green='#7d9d5a', coral='#bc6f5f', tape='#f5df9e', flow='#dd9a72'),
    'dark': dict(bg='#0d1117', fg='#e6e7db', muted='#a2ac9b', paper='#242a24', chart='#202720', ink='#a8b69a', line='#3b473b', green='#adcb87', coral='#e2a091', tape='#5a5134', flow='#f0c193'),
}


class Artwork:
    def __init__(self, width, height, mode, title):
        self.width, self.height = width, height
        self.p = PALETTES[mode]
        self.parts = []
        self.glyphs = json.loads((ROOT/'assets'/'type'/'glyphs.json').read_text(encoding='utf-8'))
        self.used = {}
        self.title = title

    def add(self, markup):
        self.parts.append(markup)

    def text_width(self, text, size, font='body'):
        f = self.glyphs[font]
        return sum(f['glyphs'].get(c, self.glyphs['body']['glyphs'].get(c, [f['units'], '']))[0] * size/f['units'] for c in text)

    def text(self, text, x, y, size=14, color='fg', font='body', anchor='start'):
        width = self.text_width(text, size, font)
        if anchor == 'end':
            x -= width
        elif anchor == 'middle':
            x -= width/2
        fill = self.p.get(color, color)
        uses = []
        for char in text:
            chosen = font if char in self.glyphs[font]['glyphs'] else 'body'
            f = self.glyphs[chosen]
            if char not in f['glyphs']:
                raise ValueError(f'Missing glyph {char!r}; refresh assets/type/glyphs.json with compile_glyphs.py')
            advance, path = f['glyphs'][char]
            ident = f'g-{chosen}-{ord(char):x}'
            self.used[ident] = path
            scale = size/f['units']
            if path:
                uses.append(f'<use href="#{ident}" transform="translate({x:.2f} {y:.2f}) scale({scale:.6f} {-scale:.6f})"/>')
            x += advance*scale
        self.add(f'<g fill="{fill}" aria-label="{escape(text, quote=True)}">'+''.join(uses)+'</g>')
        return width

    def wrapped(self, text, x, y, width, size=14, color='fg', leading=24):
        line = ''
        for char in text:
            if line and self.text_width(line+char, size) > width:
                self.text(line.rstrip(), x, y, size, color)
                y += leading
                line = ''
            line += char
        if line:
            self.text(line.rstrip(), x, y, size, color)
        return y

    def heading(self, text, x=3, y=34, color='tape'):
        width = self.text_width(text, 35, 'heading')
        self.add(f'<path d="M{x} {y+3} Q{x+width/2:.1f} {y+1} {x+width:.1f} {y-1}" fill="none" stroke="{self.p[color]}" stroke-width="7" opacity=".7"/>')
        self.text(text, x, y, 35, font='heading')

    def icon(self, name, x, y, size=23, color=None):
        icon = ET.parse(ROOT/'assets'/'icons'/f'{name}.svg').getroot()
        for key in ('width', 'height'):
            icon.set(key, str(size))
        icon.set('x', str(x))
        icon.set('y', str(y))
        if color:
            icon.set('stroke', self.p[color])
        self.add(ET.tostring(icon, encoding='unicode'))

    def finish(self):
        definitions = ''.join(f'<path id="{ident}" d="{path}"/>' for ident, path in self.used.items())
        return (f'<svg xmlns="{NS}" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img" aria-label="{escape(self.title, quote=True)}">'
                f'<title>{escape(self.title)}</title><defs>{definitions}</defs>' + ''.join(self.parts)+'</svg>\n')


def about(profile, mode, mobile=False):
    w, h = (340, 562) if mobile else (900, 370)
    info = profile['about']
    a = Artwork(w, h, mode, 'About me: '+profile['display_name']+'。'+info['introduction'])
    a.heading('About me')
    a.add(f'<path d="M153 13 l4 23 m-15 -8 24 -7 m-20 -8 18 20 m-23 -13 26 10" fill="none" stroke="{a.p["coral"]}" stroke-width="1.1"/>')
    p = a.p
    a.add(f'<rect x="5" y="57" width="{w-10}" height="{h-63}" rx="9" fill="{p["green"]}" opacity=".2"/>')
    a.add(f'<rect x="2" y="53" width="{w-9}" height="{h-63}" rx="9" fill="{p["paper"]}" stroke="{p["ink"]}" stroke-width="1.3"/>')
    a.add(f'<rect x="4" y="51" width="{w-11}" height="{h-62}" rx="7" fill="none" stroke="{p["ink"]}" opacity=".22"/>')
    a.text('profile.toml', 22, 82, 22, font='heading')
    for x in (w-90, w-70, w-50):
        a.add(f'<circle cx="{x}" cy="75" r="3" fill="{p["coral"]}"/>')
    a.add(f'<path d="M3 99 H{w-7}" stroke="{p["ink"]}" stroke-dasharray="2 3" opacity=".3"/>')
    # The avatar is bundled, so GitHub does not depend on an external image host.
    avatar = base64.b64encode((ROOT/'assets'/'avatar.jpg').read_bytes()).decode()
    px, py = (w-115, 119) if mobile else (w-126, 151)
    a.add(f'<g transform="rotate(4 {px+45} {py+50})"><rect x="{px+2}" y="{py+3}" width="90" height="111" fill="{p["ink"]}" opacity=".15"/><rect x="{px}" y="{py}" width="90" height="111" fill="{p["chart"]}" stroke="{p["ink"]}"/><image x="{px+7}" y="{py+7}" width="76" height="76" href="data:image/jpeg;base64,{avatar}"/>')
    a.text('me :)', px+45, py+101, 21, 'coral', 'heading', 'middle')
    a.add(f'<path d="M{px+19} {py-7} l48 -3 -1 16 -49 0Z" fill="{p["tape"]}" opacity=".94"/></g>')
    if mobile:
        a.text('hello :)', 27, 183, 35, 'coral', 'heading')
    keys = ['name', 'languages', 'frontend', 'focus']
    values = [json.dumps(profile['display_name'], ensure_ascii=False)] + [json.dumps(info[key], ensure_ascii=False) for key in keys[1:]]
    for i, (key, value) in enumerate(zip(keys, values)):
        y = 262+i*49 if mobile else 137+i*32
        a.text(key, 23, y, 16 if mobile else 14, 'coral')
        a.text('=', 111 if mobile else 123, y, 14, 'muted')
        vx, vy = (36, y+21) if mobile else (147, y)
        if i == 3:
            a.add(f'<path d="M{vx-2} {vy+2} q85 4 170 -2" fill="none" stroke="{p["green"]}" stroke-width="7" opacity=".25"/>')
        a.text(value, vx, vy, 15 if mobile else 14)
    a.text('# '+info['introduction'], 22, 466 if mobile else 280, 15, 'muted')
    a.text('toolbox', 22, 510 if mobile else 332, 21, 'muted', 'heading')
    for i, skill in enumerate(profile['skills']):
        x, y = (112+(i%3)*33, 489+(i//3)*30) if mobile else (100+i*36, 311)
        a.icon(skill['icon'], x, y)
    return a.finish()


def project(profile, index, mode, mobile=False):
    item = profile['featured_projects'][index]
    w = 340 if mobile else 900
    a = Artwork(w, 230, mode, item['name']+'：'+item['description']+' '+item['stack'])
    a.icon(item['icon'], 9, 14, 21, ['coral', 'green', 'ink'][index%3])
    title_size = 22 if mobile else 19
    a.text(item['name'], 49, 31, title_size)
    a.add(f'<path d="M49 35 H{49+a.text_width(item["name"], title_size):.1f}" stroke="{a.p["green"]}" opacity=".18" stroke-width="5"/>')
    a.text('↗', w-18, 29, 20, 'muted', anchor='end')
    bottom = a.wrapped(item['description'], 49, 60, w-83, 17 if mobile else 14, leading=28 if mobile else 24)
    bottom = a.wrapped(item['stack'], 49, bottom+28, w-75, 14 if mobile else 12, 'muted', 23 if mobile else 20)
    a.height = bottom+25
    if index < len(profile['featured_projects'])-1:
        a.add(f'<path d="M4 {a.height-2} H{w-5}" stroke="{a.p["ink"]}" stroke-dasharray="2 3" opacity=".32"/>')
    return a.finish()


def section_heading(text, mode, mobile=False):
    a = Artwork(340 if mobile else 900, 58, mode, text)
    a.heading(text, color='coral' if text == 'Projects' else 'tape')
    return a.finish()


def activity(days, mode, mobile=False):
    w, h = (340, 380) if mobile else (900, 365)
    active = [d for d in days if d['count'] > 0]
    total = sum(d['count'] for d in days)
    title = f'{days[0]["date"]} 至 {days[-1]["date"]}，{total} 次公开贡献，{len(active)} 个活跃日。'
    a = Artwork(w, h, mode, title)
    a.heading('Activity')
    a.text(f'{total} 次公开贡献 · {len(active)} 个活跃日', 4 if mobile else w-5, 65 if mobile else 30, 12, 'muted', anchor='start' if mobile else 'end')
    top = 85 if mobile else 60
    bottom = h-31
    p = a.p
    a.add(f'<rect x="1" y="{top}" width="{w-2}" height="{bottom-top}" rx="9" fill="{p["chart"]}" stroke="{p["ink"]}" stroke-opacity=".55"/>')
    a.add(f'<path d="M{w-82} {top-7} l59 3 -2 12 -59 -3Z" fill="{p["coral"]}" opacity=".35"/>')
    for x in range(9, w-3, 16):
        for y in range(top+8, bottom-2, 16):
            a.add(f'<circle cx="{x}" cy="{y}" r=".55" fill="{p["line"]}" opacity=".4"/>')
    start, end = [date.fromisoformat(d['date']) for d in (days[0], days[-1])]
    offset = (start.weekday()+1)%7
    cols = (offset+len(days)+6)//7
    left, right = 35, w-29
    dx = (right-left)/max(1, cols-1)
    chart_top, dy = top+40, 26
    for row, label in enumerate('日一二三四五六'):
        a.text(label, 13, chart_top+row*dy+4, 11, 'muted')
    points = []
    for i, day in enumerate(days):
        col, row = divmod(offset+i, 7)
        x, y = left+col*dx, chart_top+row*dy
        if day['count']:
            points.append((x, y, day))
        else:
            a.add(f'<circle class="day" data-date="{day["date"]}" data-count="0" cx="{x:.2f}" cy="{y:.2f}" r="{max(.7,min(1.4,dx*.13)):.2f}" fill="{p["line"]}" opacity=".7"/>')
    route = ''
    for i, (x, y, day) in enumerate(points):
        if not i:
            route = f'M{x:.2f} {y:.2f}'
            continue
        ax, ay, _ = points[i-1]
        turn = 1 if y >= ay else -1
        r = min(4, abs(y-ay)/2, abs(x-ax)/2)
        route += f' Q{(ax+x)/2:.2f} {ay+((i%3)-1)*1.2:.2f} {x-r:.2f} {ay:.2f} Q{x:.2f} {ay:.2f} {x:.2f} {ay+turn*r:.2f} L{x:.2f} {y:.2f}'
    if len(points) > 1:
        a.add(f'<path d="{route}" fill="none" stroke="{p["ink"]}" stroke-width=".7" opacity=".18" transform="translate(.8 .7)"/>')
        a.add(f'<path d="{route}" fill="none" stroke="{p["green"]}" stroke-width="1.4" opacity=".5"/>')
        a.add(f'<style>.pulse{{animation:flow 11s linear infinite}}@keyframes flow{{to{{stroke-dashoffset:-264}}}}@media(prefers-reduced-motion:reduce){{.pulse{{display:none}}}}</style><path class="pulse" d="{route}" fill="none" stroke="{p["flow"]}" stroke-width="2" stroke-linecap="round" stroke-dasharray="3 85"/>')
    for i, (x, y, day) in enumerate(points):
        r = max(1.6, min(5.2, dx*.37))*(.8+day['level']*.06)
        a.add(f'<ellipse class="day active" data-date="{day["date"]}" data-count="{day["count"]}" data-level="{day["level"]}" cx="{x:.2f}" cy="{y:.2f}" rx="{r:.2f}" ry="{r*(1.05 if i%2 else .96):.2f}" fill="{p["green"]}" fill-opacity="{.35+day["level"]*.16:.2f}" stroke="{p["ink"]}" stroke-width=".9"><title>{day["date"]} · {day["count"]} 次公开贡献</title></ellipse>')
    # Labels follow the actual rolling calendar, including the new-year boundary.
    ticks = [0, (cols-1)//2, cols-1] if mobile else [round((cols-1)*i/4) for i in range(5)]
    for i, col in enumerate(ticks):
        stamp = min(end, max(start, start+timedelta(days=col*7-offset)))
        label = stamp.strftime('%Y.%m') if i in (0,len(ticks)-1) else f'{stamp.month:02}月'
        a.text(label, left+col*dx, bottom-44, 12, 'muted', anchor='start' if i == 0 else 'end' if i == len(ticks)-1 else 'middle')
    a.add(f'<circle cx="17" cy="{bottom-19}" r="4" fill="{p["green"]}"/>')
    a.text('亮点 = 活跃日期', 28, bottom-15, 11, 'muted')
    a.text('少', w-106, bottom-15, 11, 'muted')
    for i in range(4):
        a.add(f'<rect x="{w-89+i*13}" y="{bottom-24}" width="9" height="9" rx="3" fill="{p["green"]}" opacity="{.4+i*.2:.1f}"/>')
    a.text('多', w-23, bottom-15, 11, 'muted')
    if mobile:
        a.text(f'{start} → {end}', 4, h-10, 11, 'muted')
    else:
        a.text(f'{start} → {end}', 4, h-9, 11, 'muted')
        a.text('公开贡献 · 每小时刷新', w-4, h-9, 11, 'muted', anchor='end')
    return a.finish()


def write_static(profile):
    out = ROOT/'assets'/'profile'
    out.mkdir(exist_ok=True)
    for mode in PALETTES:
        for mobile in (False, True):
            suffix = f'{"mobile-" if mobile else ""}{mode}'
            (out/f'projects-{suffix}.svg').write_text(section_heading('Projects', mode, mobile), encoding='utf-8')
            (out/f'about-{suffix}.svg').write_text(about(profile, mode, mobile), encoding='utf-8')
            for i in range(len(profile['featured_projects'])):
                (out/f'project-{i+1}-{suffix}.svg').write_text(project(profile, i, mode, mobile), encoding='utf-8')


def write_activity(days):
    for mode in PALETTES:
        for mobile in (False, True):
            suffix = f'{"mobile-" if mobile else ""}{mode}'
            (ROOT/'assets'/f'activity-{suffix}.svg').write_text(activity(days, mode, mobile), encoding='utf-8')
