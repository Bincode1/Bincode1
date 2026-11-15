import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('PROFILE_SOURCE_DIR', Path(__file__).resolve().parents[1]))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

readme = load('profile_readme', ROOT/'build_readme.py')
activity = load('profile_activity', ROOT/'scripts'/'style_activity.py')
PROFILE = {'display_name':'Bincode1','github_username':'Bincode1','skills':[],'featured_projects':[],'about':[]}
SOURCE = '''<svg xmlns="http://www.w3.org/2000/svg"><style>:root{--ce:#fff}.c{animation:none 1000ms linear infinite}.c.c0{fill:var(--c1)}</style><rect class="c" x="0" y="0"/><rect class="c c0" x="16" y="0"/></svg>'''

class ActivityFreshnessTests(unittest.TestCase):
    def test_unknown_source_time_is_not_presented_as_fresh(self):
        self.assertIn('首次更新待工作流运行', readme.build_readme(PROFILE))

    def test_readme_shows_source_time_in_user_timezone(self):
        html = readme.build_readme(PROFILE, {'generated_at':'2026-11-15T05:21:28Z'})
        self.assertIn('更新于 2026-11-15 13:21（UTC+8）', html)
        self.assertIn('每小时自动刷新', html)

    def test_new_generation_records_its_time_and_source_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root/'raw.svg'
            source.write_text(SOURCE, encoding='utf-8')
            with patch.object(activity, 'ROOT', root):
                activity.main([str(source), '--generated-at', '2026-11-15T05:21:28Z'])
            metadata = json.loads((root/'assets'/'activity.json').read_text())
            self.assertEqual(metadata['generated_at'], '2026-11-15T05:21:28Z')
            self.assertEqual((metadata['days'], metadata['active_days']), (2,1))
            self.assertEqual(len(metadata['source_sha256']), 64)

    def test_restyling_an_old_source_keeps_its_original_generation_time(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'assets').mkdir()
            old = {'generated_at':'2026-11-15T05:21:28Z'}
            (root/'assets'/'activity.json').write_text(json.dumps(old))
            source = root/'raw.svg'
            source.write_text(SOURCE, encoding='utf-8')
            with patch.object(activity, 'ROOT', root):
                activity.main([str(source)])
            self.assertEqual(json.loads((root/'assets'/'activity.json').read_text()), old)

if __name__ == '__main__':
    unittest.main()
