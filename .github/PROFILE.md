# Profile maintenance

Edit `profile.json`, then run `python build_readme.py`. The README keeps the original greeting, native GitHub typography, About me, project links and contribution animation.

Technology icons are vendored from Devicon and project symbols from Lucide. Their exact source revisions, file hashes and any modifications are in `assets/icons/SOURCES.json`; both licenses are included alongside the files. Run `python scripts/download_icons.py` only when intentionally refreshing those assets.

The Activity images retain the real public-profile calendar and snake route from Platane/snk. `scripts/style_activity.py` applies light and dark palettes, removes the bottom meter and slows the loop to 32 seconds. Contribution cells keep their original level colors throughout the loop; the snake moves over the grid without erasing it. Reduced-motion viewers get the static contribution calendar. The workflow refreshes every hour at minute 17, and supports manual dispatch on a preview branch. GitHub may delay scheduled runs and contribution indexing, so this is not a real-time commit feed.

After fetching a new source, the workflow passes its UTC generation time to the styling script. The script writes `assets/activity.json` with that time, source hash and calendar cell counts, then the workflow regenerates the README to show the time in UTC+8. Restyling an older SVG without `--generated-at` never advances the displayed source time. Only the default branch receives scheduled runs; a draft branch must be refreshed manually.

The workflow uses the repository's default GitHub token. Its calendar reflects the user's public profile visibility settings; private activity visible only to the signed-in owner is not assumed to be public and is not copied from the owner's browser session.

Project descriptions are based on the public repository READMEs. The old BiliBrain-Python link has been replaced with the current MediaMind repository. Preview changes before merging, especially the project table at 320px and the Activity picture in both GitHub themes.
