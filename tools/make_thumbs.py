#!/usr/bin/env python
"""Build the teaser images of the homepage, all with the same size and framing.

Every teaser is a 1200 x 750 px (16:10) white canvas. The figure chosen for a work is used
whole: its white border is trimmed, it is scaled to fit inside the canvas minus a fixed margin,
and centred. Because every file has the same pixel size, margin and background, the cards on
the page line up whatever the shape of the original figure.

    python tools/make_thumbs.py            # rebuild all teasers
    python tools/make_thumbs.py sbls qcv   # rebuild some

Requires Pillow (and matplotlib + numpy for the drawn teaser).
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops

HOME = Path(__file__).resolve().parents[1]
WORKSPACE = HOME.parent
OUT = HOME / "assets" / "img" / "teasers"

CANVAS = (1200, 750)
MARGIN = 44  # px on every side

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

# key -> an image that is already a finished 16:10 figure (it is only resized to the canvas)
READY: dict[str, str] = {
    "teamgame": "AP-Deployment_Cell-Free-ISAC/code/cell-free-isac-multiagent/figures/teaser.png",
    "sciagent": "AI-for-Science-Agent/code/sci-evidence-agent/figures/teaser_1600x1000.png",
    "gate": "AI-Virtual-Cell/code/perturbation-baseline-gate/figures/teaser_baselines_pearson.png",
}


def trim(image: Image.Image) -> Image.Image:
    """Remove the white border of a figure."""
    background = Image.new("RGB", image.size, "white")
    box = ImageChops.difference(image, background).getbbox()
    return image.crop(box) if box else image


def frame(image: Image.Image) -> Image.Image:
    """Centre ``image`` on the canvas, scaled to fit inside the margins."""
    inner = (CANVAS[0] - 2 * MARGIN, CANVAS[1] - 2 * MARGIN)
    scale = min(inner[0] / image.width, inner[1] / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    resized = image.resize(size, Image.LANCZOS)
    canvas = Image.new("RGB", CANVAS, "white")
    canvas.paste(resized, ((CANVAS[0] - size[0]) // 2, (CANVAS[1] - size[1]) // 2))
    return canvas


def save(key: str, canvas: Image.Image) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{key}.webp"
    canvas.save(path, "WEBP", quality=88, method=6)
    print(f"{key:8s} {canvas.size[0]}x{canvas.size[1]}  {path.stat().st_size / 1024:5.0f} KB")


def from_figure(key: str) -> None:
    image = Image.open(WORKSPACE / FIGURES[key]).convert("RGB")
    save(key, frame(trim(image)))


def from_ready(key: str) -> None:
    image = Image.open(WORKSPACE / READY[key]).convert("RGB")
    save(key, frame(trim(image)))


def draw_simulator() -> None:
    """Two radio maps from the ray-traced database of the 3-D ISAC simulator."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    base = WORKSPACE / "AP-Deployment_Cell-Free-ISAC/code/sionna-isac-simulation/simulation"
    gains = np.load(base / "paris_pg_database_3d.npy").reshape(-1, 125, 125).astype(np.float64)
    sites = np.load(base / "candidate_positions_3d.npy")
    floor = 1e-16
    best = 10 * np.log10(np.maximum(gains.max(axis=0), floor))
    index = int(np.argmax((gains > 1e-11).sum(axis=(1, 2))))  # the site that covers most cells
    single = 10 * np.log10(np.maximum(gains[index], floor))
    extent = (-250, 250, -250, 250)

    fig, axes = plt.subplots(1, 2, figsize=(12, 7.5), dpi=100)
    fig.subplots_adjust(left=0.07, right=0.9, bottom=0.2, top=0.93, wspace=0.12)
    panels = ((best, "Best site per cell (847 candidates)"), (single, "One candidate site"))
    for ax, (values, title) in zip(axes, panels):
        image = ax.imshow(values, origin="lower", extent=extent, cmap="viridis", vmin=-150, vmax=-70)
        ax.set_title(title, fontsize=17, color="#1b1a17", pad=10)
        ax.set_xlabel("x (m)", fontsize=14)
        ax.tick_params(labelsize=12, length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
    axes[0].set_ylabel("y (m)", fontsize=14)
    axes[0].scatter(sites[:, 0], sites[:, 1], s=7, c="white", edgecolors="none", alpha=0.75)
    axes[1].scatter([sites[index, 0]], [sites[index, 1]], s=160, marker="*", c="#ffd166", edgecolors="#1b1a17", linewidths=0.8)
    axes[1].set_yticklabels([])
    bar = fig.colorbar(image, cax=fig.add_axes([0.915, 0.2, 0.014, 0.73]))
    bar.set_label("path gain (dB)", fontsize=14)
    bar.ax.tick_params(labelsize=12, length=0)
    bar.outline.set_visible(False)

    path = OUT / "_simulator.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    save("simulator", frame(trim(Image.open(path).convert("RGB"))))
    path.unlink()


DRAWN = {"simulator": draw_simulator}


def main(keys: list[str]) -> int:
    for key in keys or [*FIGURES, *READY, *DRAWN]:
        if key in FIGURES:
            from_figure(key)
        elif key in READY:
            from_ready(key)
        elif key in DRAWN:
            DRAWN[key]()
        else:
            print(f"unknown teaser {key!r}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
