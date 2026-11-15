# Profile maintenance

Edit `profile.json`, then run `python build_readme.py`. The README keeps the original greeting, native GitHub typography, About me, project links and contribution animation.

Technology icons are vendored from Devicon and project symbols from Lucide. Their exact source revisions, file hashes and any modifications are in `assets/icons/SOURCES.json`; both licenses are included alongside the files. Run `python scripts/download_icons.py` only when intentionally refreshing those assets.

The Activity images retain the real calendar and snake route from Platane/snk. `scripts/style_activity.py` applies light and dark palettes, removes the bottom meter and slows the loop to 32 seconds. Reduced-motion viewers get the static contribution calendar. The existing daily workflow updates the images directly in `assets/`, so all README image sources stay repository-relative.

Project descriptions are based on the public repository READMEs. The old BiliBrain-Python link has been replaced with the current MediaMind repository. Preview changes before merging, especially the project table at 320px and the Activity picture in both GitHub themes.
