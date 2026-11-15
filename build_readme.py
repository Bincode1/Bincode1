"""Render the native GitHub profile from its curated content file."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def build_readme(profile):
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

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/activity-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/activity-light.svg">
  <img src="assets/activity-light.svg" width="100%" alt="Bincode1 的 GitHub 贡献图，使用柔和配色的贪吃蛇动画。">
</picture>
'''

def main():
    profile = json.loads((ROOT / 'profile.json').read_text(encoding='utf-8'))
    (ROOT / 'README.md').write_text(build_readme(profile), encoding='utf-8')

if __name__ == '__main__':
    main()
