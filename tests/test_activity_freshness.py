import importlib.util
import json
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


readme = load('profile_readme', ROOT/'build_readme.py')
activity = load('profile_activity', ROOT/'scripts'/'style_activity.py')
artwork = activity.render_artwork
PROFILE = json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))


def calendar_html(start=date(2025, 11, 17), count=13):
    # GitHub renders the calendar row-by-row rather than chronologically.
    days = [start+timedelta(days=i) for i in range(365)]
    parts = []
    for i in sorted(range(365), key=lambda i: (i % 7, i // 7)):
        value = count if i == 2 else 0
        level = 3 if value else 0
        ident = f'contribution-day-component-{i}'
        tip = f'{value} contributions on November 19th.' if value else 'No contributions on November 17th.'
        parts.append(f'<td id="{ident}" data-date="{days[i]}" data-level="{level}"></td><tool-tip for="{ident}">{tip}</tool-tip>')
    return ''.join(parts)


class ActivityFreshnessTests(unittest.TestCase):
    def test_unknown_source_time_is_not_presented_as_fresh(self):
        self.assertIn('首次更新待工作流运行', readme.build_readme(PROFILE))

    def test_readme_shows_source_time_in_user_timezone(self):
        html = readme.build_readme(PROFILE, {'generated_at':'2026-11-15T05:21:28Z'})
        self.assertIn('更新于 2026-11-15 13:21（UTC+8）', html)
        self.assertIn('每小时自动刷新', html)
        for project in PROFILE['featured_projects']:
            self.assertIn(f'href="{project["url"]}"', html)
            self.assertIn(project['description'], html)

    def test_parser_sorts_real_dates_and_keeps_counts(self):
        days = activity.parse_calendar(calendar_html())
        self.assertEqual(len(days), 365)
        self.assertEqual(days[0]['date'], '2025-11-17')
        self.assertEqual(days[2], {'date':'2025-11-19', 'count':13, 'level':3})
        self.assertEqual(sum(d['count'] for d in days), 13)

    def test_about_artwork_and_alt_text_share_curated_content(self):
        profile = dict(PROFILE, display_name='New name', about=dict(PROFILE['about'], introduction='Hello there.'))
        html = readme.build_readme(profile)
        with patch.object(artwork, 'ROOT', ROOT):
            svg = artwork.about(profile, 'light')
        for text in ('New name', 'Hello there.'):
            self.assertIn(text, html)
            self.assertIn(text, svg)

    def test_new_generation_records_time_hash_and_calendar(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'assets').mkdir()
            (root/'profile.json').write_text(json.dumps(PROFILE), encoding='utf-8')
            source = root/'raw.html'
            source.write_text(calendar_html(), encoding='utf-8')
            with patch.object(activity, 'ROOT', root), patch.object(artwork, 'write_activity') as render:
                activity.main([str(source), '--generated-at', '2026-11-15T05:21:28Z'])
                self.assertEqual(len(render.call_args.args[0]), 365)
            metadata = json.loads((root/'assets'/'activity.json').read_text())
            self.assertEqual(metadata['generated_at'], '2026-11-15T05:21:28Z')
            self.assertEqual((metadata['days'], metadata['active_days'], metadata['total_contributions']), (365,1,13))
            self.assertEqual(len(metadata['source_sha256']), 64)

    def test_restyling_saved_source_does_not_claim_a_new_fetch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'assets').mkdir()
            (root/'profile.json').write_text(json.dumps(PROFILE), encoding='utf-8')
            old = {'generated_at':'2026-11-15T05:21:28Z'}
            (root/'assets'/'activity.json').write_text(json.dumps(old))
            source = root/'raw.html'
            source.write_text(calendar_html(), encoding='utf-8')
            with patch.object(activity, 'ROOT', root), patch.object(artwork, 'write_activity'):
                activity.main([str(source)])
            self.assertEqual(json.loads((root/'assets'/'activity.json').read_text()), old)

    def test_incomplete_or_unknown_counts_fail_before_rendering(self):
        for source in ('<h1>Rate limited</h1>', calendar_html().replace('13 contributions', 'Unknown contributions')):
            with self.subTest(source=source[:20]), self.assertRaises(ValueError):
                activity.parse_calendar(source)

    def test_dates_cannot_be_duplicated_or_missing(self):
        source = calendar_html().replace('2025-11-18', '2025-11-17')
        with self.assertRaisesRegex(ValueError, 'unique and contiguous'):
            activity.parse_calendar(source)

    def test_svg_uses_actual_weekdays_and_keeps_every_day(self):
        days = activity.parse_calendar(calendar_html())
        with patch.object(artwork, 'ROOT', ROOT):
            svg = ET.fromstring(artwork.activity(days, 'light', mobile=True))
        marks = [e for e in svg.iter() if 'data-date' in e.attrib]
        self.assertEqual(len(marks), 365)
        self.assertEqual(len({e.get('data-date') for e in marks}), 365)
        monday = next(e for e in marks if e.get('data-date') == '2025-11-17')
        wednesday = next(e for e in marks if e.get('data-date') == '2025-11-19')
        self.assertEqual(float(wednesday.get('cy'))-float(monday.get('cy')), 52)
        self.assertEqual(wednesday.get('data-count'), '13')
        self.assertEqual(wednesday.tag.rsplit('}',1)[-1], 'ellipse')

    def test_zero_activity_is_a_valid_calendar_and_no_fabricated_route(self):
        days = activity.parse_calendar(calendar_html(count=0))
        with patch.object(artwork, 'ROOT', ROOT):
            svg = ET.fromstring(artwork.activity(days, 'dark'))
        self.assertEqual(len([e for e in svg.iter() if e.get('data-count') == '0']), 365)
        self.assertFalse(any(e.get('class') == 'pulse' for e in svg.iter()))


if __name__ == '__main__':
    unittest.main()
