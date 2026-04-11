import json
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).parent
PROFILE_FILE = ROOT / "profile.json"
README_FILE = ROOT / "README.md"


def load_profile():
    with PROFILE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def badge(label, color, logo=None, link=None, message=None, logo_color=None):
    message = message or label
    label_part = quote(str(label), safe="")
    message_part = quote(str(message), safe="")
    url = f"https://img.shields.io/badge/{label_part}-{message_part}-{color}?style=for-the-badge"
    if logo:
        url += f"&logo={quote(str(logo), safe='')}"
    if logo_color:
        url += f"&logoColor={quote(str(logo_color), safe='')}"
    image = f"![{label}]({url})"
    return f"[{image}]({link})" if link else image


def render_socials(items):
    return " ".join(
        badge(
            item["label"],
            item.get("color", "2EA44F"),
            logo=item.get("logo"),
            logo_color=item.get("logoColor"),
            link=item["url"],
        )
        for item in items
    )


def render_skills(items):
    return " ".join(
        badge(
            item["label"],
            item.get("color", "555555"),
            logo=item.get("logo"),
            logo_color=item.get("logoColor"),
            message=item["label"],
        )
        for item in items
    )


def render_list(items, prefix="- "):
    return "\n".join(f"{prefix}{item}" for item in items)


def render_focus_html(items):
    content = "".join(f"<li>{item}</li>" for item in items)
    return f"<ul>{content}</ul>"


def render_project_html(items):
    content = "".join(
        f"<li><a href=\"{item['url']}\">{item['name']}</a>: {item['description']}</li>"
        for item in items
    )
    return f"<ul>{content}</ul>"


def render_highlight_table(current_focus_items, project_items):
    focus_html = render_focus_html(current_focus_items)
    project_html = render_project_html(project_items)
    return f"""
<table>
  <tr>
    <td valign="top" width="50%">

<strong>近期重点</strong>
<br />
<br />
{focus_html}

    </td>
    <td valign="top" width="50%">

<strong>精选项目</strong>
<br />
<br />
{project_html}

    </td>
  </tr>
</table>
""".strip()


def render_stats(username):
    stats_dark = (
        "https://github-readme-stats.vercel.app/api"
        f"?username={username}&show_icons=true&include_all_commits=true"
        "&rank_icon=percentile&theme=tokyonight&hide_border=true"
    )
    stats_light = (
        "https://github-readme-stats.vercel.app/api"
        f"?username={username}&show_icons=true&include_all_commits=true"
        "&rank_icon=percentile&theme=default&hide_border=true"
    )
    langs_dark = (
        "https://github-readme-stats.vercel.app/api/top-langs"
        f"?username={username}&layout=compact&langs_count=8"
        "&size_weight=0.5&count_weight=0.5&theme=tokyonight&hide_border=true"
    )
    langs_light = (
        "https://github-readme-stats.vercel.app/api/top-langs"
        f"?username={username}&layout=compact&langs_count=8"
        "&size_weight=0.5&count_weight=0.5&theme=default&hide_border=true"
    )

    return f"""
<p>
  <picture>
    <source
      srcset="{stats_dark}"
      media="(prefers-color-scheme: dark)"
    />
    <source
      srcset="{stats_light}"
      media="(prefers-color-scheme: light), (prefers-color-scheme: no-preference)"
    />
    <img height="180" src="{stats_light}" alt="{username} GitHub stats" />
  </picture>
  <picture>
    <source
      srcset="{langs_dark}"
      media="(prefers-color-scheme: dark)"
    />
    <source
      srcset="{langs_light}"
      media="(prefers-color-scheme: light), (prefers-color-scheme: no-preference)"
    />
    <img height="180" src="{langs_light}" alt="{username} top languages" />
  </picture>
</p>
""".strip()


def render_snake(username):
    base = f"https://raw.githubusercontent.com/{username}/{username}/output"
    return f"""
<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="{base}/github-snake-dark.svg"
  />
  <source
    media="(prefers-color-scheme: light), (prefers-color-scheme: no-preference)"
    srcset="{base}/github-snake.svg"
  />
  <img alt="github contribution snake" src="{base}/github-snake.svg" />
</picture>
""".strip()


def build_readme(profile):
    username = profile["github_username"]
    display_name = profile["display_name"]
    headline = profile["headline"]
    location = profile["location"]
    about_items = list(profile["about"])
    about_items.extend(
        [
            f"所在地：`{location}`",
            f"GitHub：[`@{username}`](https://github.com/{username})",
        ]
    )
    about = render_list(about_items)
    skills = render_skills(profile["skills"])
    socials = render_socials(profile["social_links"])
    visitor_badge = (
        f"https://komarev.com/ghpvc/?username={username}"
        "&style=for-the-badge&color=0e75b6"
    )
    followers_badge = (
        f"https://img.shields.io/github/followers/{username}"
        "?style=for-the-badge&logo=github"
    )

    return f"""# Hi there, 我是 {display_name} 👋

> {headline}

<p>{socials}</p>

<p>
  <img src="{visitor_badge}" alt="profile views" />
  <img src="{followers_badge}" alt="GitHub followers" />
</p>

## 关于我

{about}

## 技术栈

{skills}

## 主页亮点

{render_highlight_table(profile["current_focus"], profile["featured_projects"])}

## GitHub 数据

{render_stats(username)}

## Contribution Snake

{render_snake(username)}

## 一句话

> {profile["quote"]}

---

如果你正在使用这个模板：

1. 把仓库名改成你的 GitHub 用户名。
2. 修改 [`profile.json`](./profile.json) 里的名字、链接、项目和技能。
3. 运行 `python build_readme.py` 重新生成主页。
4. 推送到 GitHub 后，Actions 会自动更新 README 和贡献蛇图。
"""


def main():
    profile = load_profile()
    readme = build_readme(profile)
    README_FILE.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
