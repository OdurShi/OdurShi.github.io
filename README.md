# Personal homepage

A single static page: `index.html`, one stylesheet, one small script. No build step and no
external requests, so it can be opened from disk or served by any static host.

```text
index.html                 all content
assets/css/style.css       design tokens (colors, type) at the top, then components
assets/js/main.js          header hairline, active navigation link
assets/img/profile.jpg     portrait (square, 480 px or larger)
assets/img/teasers/*.webp  one teaser per paper or project, all 1200 x 750 px
tools/make_thumbs.py       builds the teasers (same canvas, margin and background for all)
favicon.ico, assets/img/favicon.svg
```

## Preview

```bash
python3 -m http.server 4173 --directory .
```

then open <http://localhost:4173>.

## Updating

- **Photo**: replace `assets/img/profile.jpg` (keep the file name).
- **CV**: not linked at the moment. To add it, put the PDF in `assets/cv/` and add a link to the
  navigation and to the list of links under the introduction.
- **News**: add an `<li class="row">` at the top of the list in the `News` section.
- **Publications and projects**: copy an `<article class="pub">` block. Teasers must all have
  the same size: add the source figure and its crop box to `tools/make_thumbs.py` and run
  `python tools/make_thumbs.py <key>`; it writes `assets/img/teasers/<key>.webp` on a
  1200 x 750 canvas with the same margin as the others. Use `class="badge"` for published
  work and `class="badge review"` for work under review or projects.
- **Colors and fonts**: the variables at the top of `assets/css/style.css`.

## Publishing with GitHub Pages

1. Create a public repository named `OdurShi.github.io`.
2. Push the contents of this folder to its `main` branch.
3. In the repository settings, under Pages, choose "Deploy from a branch", `main`, `/ (root)`.

The site is then served at <https://odurshi.github.io>. The empty `.nojekyll` file tells GitHub
Pages to serve the files as they are.
