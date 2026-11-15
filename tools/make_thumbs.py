#!/usr/bin/env python
"""Build the figures of the homepage.

Two files are written for every work:

    assets/img/teasers/<key>.webp   the image on the card
    assets/img/figures/<key>.webp   the same figure at full size, opened by a click on the card

The figure chosen for a work is always used whole: its white border is trimmed and it is centred
on a white canvas with a fixed margin. Most cards use the same 1200 x 750 px (16:10) canvas, so
they line up whatever the shape of the original figure. A figure that is much wider than 16:10
(``WIDE``) would fill less than half of that canvas; it gets a canvas of its own shape and is
shown across the full width of its card.

    python tools/make_thumbs.py            # rebuild everything
    python tools/make_thumbs.py sbls qcv   # rebuild some

The figures of the papers are read from the PNG files shipped with the code repositories. If the
PDF of a paper is found in the workspace and PyMuPDF is installed, the figure is rendered from
the PDF instead, at a higher resolution (the PDF is only read). The crop boxes are the ones in
``scripts/extract_paper_figures.py`` of each repository.

Requires Pillow, and matplotlib + numpy for the drawn teaser.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageChops

HOME = Path(__file__).resolve().parents[1]
WORKSPACE = HOME.parent
TEASERS = HOME / "assets" / "img" / "teasers"
FULL = HOME / "assets" / "img" / "figures"

CARD = (1200, 750)  # canvas of a normal card image
CARD_MARGIN = 44  # px on every side
WIDE_WIDTH = 1704  # canvas width of a wide card image: twice the 852 px text column
WIDE_MARGIN = 36
FULL_MAX = (2400, 1800)  # largest size of the enlarged figure
FULL_MARGIN = 40

# key -> the figure that represents the work best (always used whole, never cropped to fit)
FIGURES: dict[str, str] = {
    "sbls": "SBLS/code/sbls/assets/paper_figures/fig01.png",
    "qcv": "QCV/code/qcv/assets/paper_figures/fig01.png",
    "mrime": "MRIME-CD_EDECO/code/mrime/assets/paper_figures/fig02.png",
    "edeco": "MRIME-CD_EDECO/code/edeco/assets/paper_figures/fig01.png",
    "ap": "AP-Deployment_Cell-Free-ISAC/code/cell-free-isac-ap-deployment/assets/paper_figures/fig01.png",
    "vdopd": "VD-OPD/code/vd-opd/assets/paper_figures/fig01.png",
    "sigma": "SIGMA/code/sigma/assets/paper_figures/fig01.png",
    "resplat": "4DReSplat/code/4dresplat/assets/paper_figures/fig01.png",
}

# key -> (PDF in the workspace, 1-based page, crop box in PDF points) of the same figure
PDF_CROPS: dict[str, tuple[str, int, tuple[float, float, float, float]]] = {
    "sbls": ("SBLS/paper/*.pdf", 1, (322.0, 212.0, 556.0, 357.0)),
    "qcv": ("QCV/paper/*.pdf", 1, (317.0, 212.0, 560.0, 453.0)),
    "mrime": ("MRIME-CD_EDECO/paper/s10586*.pdf", 7, (50.5, 56.2, 545.2, 364.9)),
    "edeco": ("MRIME-CD_EDECO/paper/biomimetics*.pdf", 7, (94.0, 246.0, 508.5, 546.0)),
    "ap": ("AP-Deployment_Cell-Free-ISAC/paper/*.pdf", 2, (334.0, 81.0, 542.0, 251.0)),
    "vdopd": ("VD-OPD/paper/*.pdf", 2, (127.0, 80.0, 485.5, 220.5)),
    "sigma": ("SIGMA/paper/*.pdf", 2, (104.0, 78.0, 508.0, 208.0)),
    "resplat": ("4DReSplat/*.pdf", 1, (108.0, 223.1, 504.0, 396.8)),
}

# figures much wider than 16:10, shown across the full width of the card
WIDE = {"vdopd", "sigma", "resplat"}

# key -> (card image, enlarged image): figures of the projects, drawn by their repositories
READY: dict[str, tuple[str, str]] = {
    "teamgame": (
        "AP-Deployment_Cell-Free-ISAC/code/cell-free-isac-multiagent/figures/teaser.png",
        "AP-Deployment_Cell-Free-ISAC/code/cell-free-isac-multiagent/figures/teaser.png",
    ),
    "sciagent": (  # card: box titles only, in large type; enlarged: the detailed diagram
        "AI-for-Science-Agent/code/sci-evidence-agent/figures/teaser_1600x1000.png",
        "AI-for-Science-Agent/code/sci-evidence-agent/figures/architecture.png",
    ),
    "gate": (
        "AI-Virtual-Cell/code/perturbation-baseline-gate/figures/teaser_baselines_pearson.png",
        "AI-Virtual-Cell/code/perturbation-baseline-gate/figures/teaser_baselines_pearson.png",
    ),
}

SIMULATOR = "AP-Deployment_Cell-Free-ISAC/code/sionna-isac-simulation"


def trim(image: Image.Image) -> Image.Image:
    """Remove the white border of a figure."""
    background = Image.new("RGB", image.size, "white")
    box = ImageChops.difference(image, background).getbbox()
    return image.crop(box) if box else image


def place(image: Image.Image, canvas_size: tuple[int, int], margin: int) -> Image.Image:
    """Centre ``image`` on a white canvas, scaled to fit inside the margins."""
    inner = (canvas_size[0] - 2 * margin, canvas_size[1] - 2 * margin)
    scale = min(inner[0] / image.width, inner[1] / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    canvas = Image.new("RGB", canvas_size, "white")
    canvas.paste(
        image.resize(size, Image.LANCZOS),
        ((canvas_size[0] - size[0]) // 2, (canvas_size[1] - size[1]) // 2),
    )
    return canvas


def card(image: Image.Image, wide: bool) -> Image.Image:
    """The image on the card: the common 16:10 canvas, or a canvas of the figure's own shape."""
    image = trim(image)
    if not wide:
        return place(image, CARD, CARD_MARGIN)
    inner = WIDE_WIDTH - 2 * WIDE_MARGIN
    height = round(image.height * inner / image.width) + 2 * WIDE_MARGIN
    return place(image, (WIDE_WIDTH, height), WIDE_MARGIN)


def full(image: Image.Image) -> Image.Image:
    """The enlarged figure: trimmed, never upscaled, with a small white margin."""
    image = trim(image)
    inner = (FULL_MAX[0] - 2 * FULL_MARGIN, FULL_MAX[1] - 2 * FULL_MARGIN)
    scale = min(1.0, inner[0] / image.width, inner[1] / image.height)
    size = (round(image.width * scale), round(image.height * scale))
    return place(image, (size[0] + 2 * FULL_MARGIN, size[1] + 2 * FULL_MARGIN), FULL_MARGIN)


def save(folder: Path, key: str, image: Image.Image, quality: int) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{key}.webp"
    image.save(path, "WEBP", quality=quality, method=6)
    print(f"  {folder.name}/{path.name:14s} {image.width:4d} x {image.height:4d}  "
          f"{path.stat().st_size / 1024:4.0f} KB")


def write(key: str, card_source: Image.Image, full_source: Image.Image) -> None:
    save(TEASERS, key, card(card_source, key in WIDE), 88)
    save(FULL, key, full(full_source), 90)


def paper_figure(key: str) -> Image.Image:
    """The figure of a paper: rendered from the PDF when possible, else the repository's PNG."""
    pattern, page_number, box = PDF_CROPS[key]
    pdfs = sorted(p for p in WORKSPACE.glob(pattern) if "supplement" not in p.name.lower())
    try:
        import fitz  # PyMuPDF
    except ImportError:
        fitz = None
    if fitz is not None and len(pdfs) == 1:
        dpi = min(900, math.ceil(FULL_MAX[0] * 72 / (box[2] - box[0])))
        with fitz.open(pdfs[0]) as document:
            pixmap = document[page_number - 1].get_pixmap(clip=fitz.Rect(*box), dpi=dpi, alpha=False)
        print(f"{key}: page {page_number} of the PDF at {dpi} dpi")
        return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    print(f"{key}: {FIGURES[key]}")
    return Image.open(WORKSPACE / FIGURES[key]).convert("RGB")


def from_paper(key: str) -> None:
    image = paper_figure(key)
    write(key, image, image)


def from_ready(key: str) -> None:
    small, large = READY[key]
    print(f"{key}: {small}")
    write(key, Image.open(WORKSPACE / small).convert("RGB"), Image.open(WORKSPACE / large).convert("RGB"))


def simulator_card(scene: Image.Image, best, sites) -> Image.Image:
    """The scene rendering filling the card, with the radio map as an inset."""
    import numpy as np
    from matplotlib import colormaps
    from PIL import ImageDraw

    scale = max(CARD[0] / scene.width, CARD[1] / scene.height)
    cover = scene.resize((round(scene.width * scale), round(scene.height * scale)), Image.LANCZOS)
    x0, y0 = (cover.width - CARD[0]) // 2, (cover.height - CARD[1]) // 2
    canvas = cover.crop((x0, y0, x0 + CARD[0], y0 + CARD[1]))

    side, border, offset = 318, 7, 34
    values = np.clip((best + 150.0) / 80.0, 0.0, 1.0)[::-1]  # -150 .. -70 dB, north at the top
    colours = (colormaps["viridis"](values)[..., :3] * 255).astype(np.uint8)
    radio = Image.fromarray(colours).resize((side * 2, side * 2), Image.NEAREST)
    draw = ImageDraw.Draw(radio)
    for x, y in {(float(x), float(y)) for x, y in sites[:, :2]}:
        cx, cy = (x + 250.0) / 500.0 * side * 2, (250.0 - y) / 500.0 * side * 2
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill="white")
    radio = radio.resize((side, side), Image.LANCZOS)
    framed = Image.new("RGB", (side + 2 * border, side + 2 * border), "white")
    framed.paste(radio, (border, border))
    # bottom left: the bottom right corner of a card holds the enlarge icon
    canvas.paste(framed, (offset, CARD[1] - framed.height - offset))
    return canvas


def draw_simulator() -> None:
    """Card: the ray-traced scene with a radio map from its path-gain database as an inset.
    Enlarged: the scene next to the same map with its axes and colour scale."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    base = WORKSPACE / SIMULATOR
    scene = trim(Image.open(base / "docs" / "figures" / "scene_preview.png").convert("RGB"))
    gains = np.load(base / "simulation" / "paris_pg_database_3d.npy")
    gains = gains.reshape(-1, 125, 125).astype(np.float64)
    sites = np.load(base / "simulation" / "candidate_positions_3d.npy")
    best = 10 * np.log10(np.maximum(gains.max(axis=0), 1e-16))

    # Both panels have the same height; the scene keeps its own aspect ratio.
    ink = "#1b1a17"
    width, height, side = 12.0, 7.5, 3.9  # inches; ``side`` is the height of both panels
    bottom = (height - side) / 2 - 0.1
    scene_width = side * scene.width / scene.height
    fig = plt.figure(figsize=(width, height), dpi=200)

    def axes(x0: float, w: float):
        return fig.add_axes((x0 / width, bottom / height, w / width, side / height))

    left = axes(0.35, scene_width)
    left.imshow(np.asarray(scene), aspect="auto")
    left.axis("off")
    left.set_title("Ray-traced 3-D scene (Paris, Étoile)", fontsize=17, color=ink, pad=12)

    map_x0 = 0.35 + scene_width + 0.95
    right = axes(map_x0, side)
    image = right.imshow(best, origin="lower", extent=(-250, 250, -250, 250), cmap="viridis",
                         vmin=-150, vmax=-70, aspect="auto")
    right.scatter(sites[:, 0], sites[:, 1], s=6, c="white", edgecolors="none", alpha=0.75)
    right.set_title("Best path gain over 847 AP sites", fontsize=17, color=ink, pad=12)
    right.set_xlabel("x (m)", fontsize=14)
    right.set_ylabel("y (m)", fontsize=14, labelpad=2)
    right.tick_params(labelsize=12, length=0)
    for spine in right.spines.values():
        spine.set_visible(False)
    bar = fig.colorbar(image, cax=axes(map_x0 + side + 0.15, 0.16))
    bar.set_label("path gain (dB)", fontsize=14)
    bar.ax.tick_params(labelsize=12, length=0)
    bar.outline.set_visible(False)

    path = FULL / "_simulator.png"
    FULL.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    drawn = Image.open(path).convert("RGB")
    path.unlink()
    print("simulator: drawn from the scene preview and the path-gain database")
    save(TEASERS, "simulator", simulator_card(scene, best, sites), 88)
    save(FULL, "simulator", full(drawn), 90)


DRAWN = {"simulator": draw_simulator}


def main(keys: list[str]) -> int:
    for key in keys or [*FIGURES, *READY, *DRAWN]:
        if key in FIGURES:
            from_paper(key)
        elif key in READY:
            from_ready(key)
        elif key in DRAWN:
            DRAWN[key]()
        else:
            print(f"unknown figure {key!r}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
