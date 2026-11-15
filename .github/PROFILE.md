# Profile maintenance

The profile follows the approved paper-and-pencil design: cream paper, olive ink, coral accents, a taped avatar, hand-drawn headings, three linked project rows and a public contribution circuit. The visible title is simply `Activity`; do not add the removed Chinese label.

GitHub removes custom HTML styles and scripts from READMEs. The artwork is therefore self-contained SVG, with separate desktop/mobile and light/dark variants selected by native `<picture>` sources. Each project is a real HTML link around its image. Image alt text preserves project descriptions and the About me content for screen readers. There are no remote image badges, external font requests or embedded scripts.

## Updating content

Edit `profile.json`, then run:

```sh
python build_readme.py
python -m unittest discover -s tests -v
```

This rebuilds `README.md` and `assets/profile/*.svg`. Commit source and generated artwork together. Preview both themes at desktop and phone widths. `scripts/render_artwork.py` owns the palette, spacing and drawing geometry.

Technology icons are vendored Devicon files; project symbols are Lucide. Exact source revisions, hashes and licenses are in `assets/icons/`. The avatar is bundled in `assets/avatar.jpg`.

Text uses LXGW WenKai and Caveat outlines, so readers do not need either font installed. Font licenses and provenance are in `assets/type/`. `glyphs.json` includes the current copy and printable ASCII. For new Chinese characters, install the optional authoring tool `fonttools`, download the two licensed fonts from the documented sources, then run:

```sh
python scripts/compile_glyphs.py /path/to/LXGWWenKai-Regular.ttf /path/to/Caveat.ttf
python build_readme.py
```

Hourly generation requires only the Python standard library, not FontTools or system fonts.

## Public contribution refresh

`.github/workflows/profile.yml` runs hourly at minute 17, on relevant source changes and on manual dispatch. It runs the tests, fetches the **unauthenticated public** calendar from `https://github.com/users/Bincode1/contributions`, and then regenerates all artwork. It never sends an authorization header or copies the owner's signed-in private activity.

`scripts/style_activity.py` parses the actual dates, counts and contribution levels. It checks for a complete, contiguous year and recognizable counts before replacing artwork. A partial response, login page or rate limit fails the workflow instead of publishing an empty map. Nodes retain their intensity throughout the animation; only a warm pulse moves along the connecting line. Reduced-motion readers see a static map. Every day, count and level is retained in `assets/activity.json` and in the SVG data attributes.

The fetch time is recorded in UTC and shown in UTC+8 below Activity. Restyling a saved source without an explicit source timestamp never advances that time. GitHub can delay scheduled jobs and contribution indexing, so this is an hourly snapshot, not a real-time commit feed. Only the default branch receives scheduled runs.

The old README and snake workflows have been consolidated into this single workflow, avoiding two bots writing the same README concurrently.
