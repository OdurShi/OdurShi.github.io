# Personal homepage

A single static page: `index.html`, one stylesheet, one small script. No build step and no
external requests, so it can be opened from disk or served by any static host.

```text
index.html                 all content
assets/css/style.css       design tokens (colors, type) at the top, then components
assets/js/main.js          header hairline, active navigation link, click-to-enlarge figures
assets/img/profile.jpg     portrait (square, 480 px or larger)
assets/img/teasers/*.webp  the image on the card of each paper or project: 1200 x 750 px, except
                           three wide figures that keep their own shape and span the card
assets/img/figures/*.webp  the same figures at full size, opened by a click on a card image
tools/make_thumbs.py       builds both sets (same margin and background for all)
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
- **Publications and projects**: copy an `<article class="pub">` block. Add the figure to
  `tools/make_thumbs.py` and run `python tools/make_thumbs.py <key>`; it writes the card image
  `assets/img/teasers/<key>.webp` (a 1200 x 750 canvas with the same margin as the others) and
  the full-size figure `assets/img/figures/<key>.webp`. In the block, the `<img>` points to the
  card image and the surrounding link to the full-size figure. A figure much wider than 16:10
  goes into `WIDE` in the script and gets `class="pub pub--wide"`: it is then shown across the
  card in its own shape, and the `width` and `height` of its `<img>` are the size the script
  prints. Use `class="badge"` for published work and `class="badge review"` for work under
  review or projects.
- **Colors and fonts**: the variables at the top of `assets/css/style.css`.

## Publishing with GitHub Pages

1. Create a public repository named `OdurShi.github.io`.
2. Push the contents of this folder to its `main` branch.
3. In the repository settings, under Pages, choose "Deploy from a branch", `main`, `/ (root)`.

The site is served at <https://odurshi.com>. The `CNAME` file holds this custom domain; its DNS
records (four `A`, four `AAAA` and a `www` `CNAME` record, all "DNS only" at Cloudflare) point to
GitHub Pages, and <https://odurshi.github.io> redirects to it. The empty `.nojekyll` file tells
GitHub Pages to serve the files as they are.
