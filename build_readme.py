"""Build GitHub-compatible markup and the approved hand-drawn profile artwork."""
import json
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'scripts'))
import render_artwork


def picture(path, alt, mobile=True):
    sources = ''
    if mobile:
        sources += f'  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="{path}-mobile-dark.svg">\n'
        sources += f'  <source media="(max-width: 600px)" srcset="{path}-mobile-light.svg">\n'
    sources += f'  <source media="(prefers-color-scheme: dark)" srcset="{path}-dark.svg">\n'
    return f'<picture>\n{sources}  <img src="{path}-light.svg" width="100%" alt="{escape(alt, quote=True)}">\n</picture>'


def build_readme(profile, activity=None):
    info = profile['about']
    about = f'About me：{profile["display_name"]}。'+'；'.join(' / '.join(info[key]) for key in ('languages', 'frontend', 'focus'))+'。'+info['introduction']
    sections = [picture('assets/profile/about', about)]
    sections.append(picture('assets/profile/projects', 'Projects'))
    for i, project in enumerate(profile['featured_projects']):
        alt = f'{project["name"]}：{project["description"]} 技术栈：{project["stack"]}'
        sections.append(f'<a href="{escape(project["url"], quote=True)}">\n{picture(f"assets/profile/project-{i+1}", alt)}\n</a>')
    sections.append(f'[全部项目 ↗](https://github.com/{profile["github_username"]}?tab=repositories)')
    sections.append(picture('assets/activity', 'Activity：Bincode1 的公开贡献日历。绿色节点表示活跃日期，暖色光点沿线路移动，节点颜色始终保留。'))
    if activity:
        generated = datetime.fromisoformat(activity['generated_at'].replace('Z', '+00:00'))
        if generated.tzinfo is None:
            raise ValueError('Activity generation time must include a timezone.')
        updated = generated.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
        freshness = f'更新于 {updated}（UTC+8） · 公开贡献 · 每小时自动刷新'
    else:
        freshness = '公开贡献 · 每小时自动刷新 · 首次更新待工作流运行'
    sections.append(f'<sub>{freshness}</sub>')
    return '\n\n'.join(sections)+'\n'


def main():
    profile = json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
    render_artwork.ROOT = ROOT
    render_artwork.write_static(profile)
    metadata = ROOT/'assets'/'activity.json'
    activity = json.loads(metadata.read_text(encoding='utf-8')) if metadata.exists() else None
    (ROOT/'README.md').write_text(build_readme(profile, activity), encoding='utf-8')


if __name__ == '__main__':
    main()
