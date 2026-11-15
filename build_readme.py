"""Render the native GitHub profile from its curated content file."""
import json
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def build_readme(profile, activity=None):
    skills = ''.join(
        f'<img src="assets/icons/{escape(s["icon"])}.svg" width="36" height="36" alt="{escape(s["label"])}" title="{escape(s["label"])}">&nbsp;&nbsp;'
        for s in profile['skills']
    )
    rows = []
    for p in profile['featured_projects']:
        rows.append(f'''<tr>
<td width="800">
<img src="assets/icons/{escape(p['icon'])}.svg" width="20" height="20" align="absmiddle" alt="">&nbsp;
<a href="{escape(p['url'], quote=True)}"><strong>{escape(p['name'])}</strong></a><br>
{escape(p['description'])}<br>
<sub>{escape(p['stack'])}</sub>
</td>
</tr>''')
    about = '\n'.join(profile['about'])
    projects = '\n'.join(rows)
    name = escape(profile['display_name'])
    if activity:
        generated = datetime.fromisoformat(activity['generated_at'].replace('Z', '+00:00'))
        if generated.tzinfo is None:
            raise ValueError('Activity generation time must include a timezone.')
        updated = generated.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
        freshness = f'更新于 {updated}（UTC+8） · 每小时自动刷新'
    else:
        freshness = '每小时自动刷新 · 首次更新待工作流运行'
    return f'''### Hello, 我是 {name}! 👋

<p>{skills}</p>

#### About me

```text
{about}
```

#### Projects

<table width="100%">
{projects}
</table>

[全部项目 ↗](https://github.com/{profile['github_username']}?tab=repositories)

#### Activity

<sub>{freshness}</sub>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/activity-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/activity-light.svg">
  <img src="assets/activity-light.svg" width="100%" alt="Bincode1 的 GitHub 贡献图，使用柔和配色的贪吃蛇动画。">
</picture>
'''

def main():
    profile = json.loads((ROOT / 'profile.json').read_text(encoding='utf-8'))
    metadata = ROOT / 'assets' / 'activity.json'
    activity = json.loads(metadata.read_text(encoding='utf-8')) if metadata.exists() else None
    (ROOT / 'README.md').write_text(build_readme(profile, activity), encoding='utf-8')

if __name__ == '__main__':
    main()
