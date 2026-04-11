import json
from pathlib import Path


ROOT = Path(__file__).parent
PROFILE_FILE = ROOT / "profile.json"
README_FILE = ROOT / "README.md"


TOPIC_ICONS = {
    "Java": "https://raw.githubusercontent.com/github/explore/main/topics/java/java.png",
    "Python": "https://raw.githubusercontent.com/github/explore/main/topics/python/python.png",
    "Vue": "https://raw.githubusercontent.com/github/explore/main/topics/vue/vue.png",
}


def load_profile():
    with PROFILE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def render_icons(skills):
    lines = []
    for item in skills:
        icon = TOPIC_ICONS.get(item["label"])
        if icon:
            lines.append(f'<code><img height="26" src="{icon}"></code>')
    return "\n".join(lines)


def render_badges(profile):
    username = profile["github_username"]
    projects = profile["featured_projects"]
    return "\n".join(
        [
            f"[![visitor](https://visitor-badge.glitch.me/badge?page_id={username.lower()}.{username.lower()})](https://github.com/{username})",
            f"[![GitHub](https://img.shields.io/badge/github-{username}-181717)](https://github.com/{username})",
            f"[![one-text-code](https://img.shields.io/badge/project-one--text--code-blue)]({projects[0]['url']})",
            f"[![BiliBrain-Python](https://img.shields.io/badge/project-BiliBrain--Python-orange)]({projects[1]['url']})",
        ]
    )


def render_about_block(profile):
    lines = list(profile["about"]) + profile["current_focus"]
    text = "\n".join(lines)
    return f"```text\n{text}\n```"


def render_projects(profile):
    return "\n".join(
        f"* <a href='{item['url']}' target='_blank' title='{item['name']}'>{item['name']}</a> - {item['description']}"
        for item in profile["featured_projects"]
    )


def render_stats(profile):
    username = profile["github_username"]
    username_lower = username.lower()
    return f"""<p>
  <img
  width="334"
  src="https://github-readme-stats.vercel.app/api/top-langs/?username={username_lower}&langs_count=8&layout=compact&bg_color=30,e96443,904e95&title_color=fff&text_color=fff"
  />
  <img
  width="507"
  src="https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&&theme=radical&layout=compact"
  />
</p>"""


def render_snake(profile):
    username = profile["github_username"]
    return f"![github contribution grid snake animation](https://github.com/{username}/{username}/blob/output/github-contribution-grid-snake.svg)"


def build_readme(profile):
    display_name = profile["display_name"]
    username = profile["github_username"]

    return f"""### Hello, 我是{display_name}! 👋

{render_icons(profile["skills"])}

{render_badges(profile)}

<table width="800px">
<tr>
<td valign="top" width="50%">

#### 👨‍💻 About Me

<!-- code_time starts -->

{render_about_block(profile)}

<!-- code_time ends -->
</td>

<td valign="top" width="50%">

#### 🚀 Featured Projects

<!-- blog starts -->
{render_projects(profile)}
<!-- blog ends -->

</td>
</tr>

</table>

{render_stats(profile)}

{render_snake(profile)}
"""


def main():
    profile = load_profile()
    README_FILE.write_text(build_readme(profile), encoding="utf-8")


if __name__ == "__main__":
    main()
