"""Fetch the unauthenticated public GitHub calendar and render contribution artwork."""
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_artwork


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tips = {}
        self.current_tip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'data-date' in attrs and 'data-level' in attrs:
            ident = attrs['id']
            if ident in self.cells:
                raise ValueError('Duplicate contribution day id')
            self.cells[ident] = {'date': attrs['data-date'], 'level': int(attrs['data-level'])}
        elif tag == 'tool-tip' and attrs.get('for', '').startswith('contribution-day-'):
            self.current_tip = attrs['for']
            self.tips[self.current_tip] = ''

    def handle_data(self, data):
        if self.current_tip is not None:
            self.tips[self.current_tip] += data

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.current_tip = None


def parse_calendar(source):
    parser = CalendarParser()
    parser.feed(source)
    days = []
    for ident, cell in parser.cells.items():
        tip = ' '.join(parser.tips.get(ident, '').split())
        match = re.match(r'([\d,]+) contributions? on ', tip)
        if tip.startswith('No contributions on '):
            count = 0
        elif match:
            count = int(match[1].replace(',', ''))
        else:
            raise ValueError(f'Unrecognized public contribution count for {cell["date"]}: {tip!r}')
        if not 0 <= cell['level'] <= 4 or (count == 0) != (cell['level'] == 0):
            raise ValueError('Contribution count and intensity disagree')
        date.fromisoformat(cell['date'])
        days.append(dict(cell, count=count))
    days.sort(key=lambda d: d['date'])
    if not 365 <= len(days) <= 371:
        raise ValueError(f'Expected a full public contribution year, got {len(days)} days')
    for previous, current in zip(days, days[1:]):
        if date.fromisoformat(current['date'])-date.fromisoformat(previous['date']) != timedelta(days=1):
            raise ValueError('Public contribution dates must be unique and contiguous')
    return days


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('source', nargs='?', help='Saved public-calendar HTML; omit to fetch without authentication')
    parser.add_argument('--generated-at', help='Actual source fetch time; never advances when restyling a saved source')
    args = parser.parse_args(argv)
    profile = json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
    if args.source:
        source = Path(args.source).read_text(encoding='utf-8')
    else:
        # No Authorization header or browser cookies: public contributions only.
        request = Request(f'https://github.com/users/{profile["github_username"]}/contributions', headers={'User-Agent': 'Bincode1-profile-artwork', 'Accept-Language': 'en-US'})
        with urlopen(request, timeout=45) as response:
            source = response.read().decode('utf-8')
        args.generated_at = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    days = parse_calendar(source)
    if args.generated_at:
        stamp = datetime.fromisoformat(args.generated_at.replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('Generation time must include a timezone')
    # Validate the complete response before replacing any generated asset.
    render_artwork.ROOT = ROOT
    render_artwork.write_activity(days)
    if args.generated_at:
        metadata = {
            'generated_at': args.generated_at,
            'source': 'GitHub public profile contribution calendar (unauthenticated)',
            'source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
            'days': len(days),
            'active_days': sum(d['count'] > 0 for d in days),
            'total_contributions': sum(d['count'] for d in days),
            'calendar': days,
        }
        (ROOT/'assets'/'activity.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Saved public calendar: {len(days)} days, {sum(d["count"] for d in days)} contributions; dark/light and desktop/mobile artwork.')


if __name__ == '__main__':
    main()
