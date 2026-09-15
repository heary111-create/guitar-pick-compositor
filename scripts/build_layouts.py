from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def pixel_hash(image: Image.Image) -> str:
    pixels = np.asarray(image.convert("RGB"), dtype=np.uint8)
    return hashlib.sha256(pixels.tobytes()).hexdigest()


def load_opaque_source(path: Path) -> Image.Image:
    image = Image.open(path)
    if "A" in image.getbands() and image.getchannel("A").getextrema()[0] < 255:
        raise ValueError(f"Source must be opaque to preserve an exact rectangular photo: {path}")
    return image.convert("RGB")


def load_transparent_pick(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    extrema = image.getchannel("A").getextrema()
    if extrema != (0, 255):
        raise ValueError(f"Pick must have genuine transparent and opaque pixels: {path}; alpha={extrema}")
    if image.getchannel("A").getbbox() is None:
        raise ValueError(f"Pick is fully transparent: {path}")
    # Generators may leave checkerboard or matte RGB values under pixels whose
    # alpha is zero. Those values are invisible in compliant viewers but can
    # leak through in faulty importers. Clear them without touching any visible
    # pixel or changing the alpha channel.
    pixels = np.asarray(image, dtype=np.uint8).copy()
    transparent = pixels[:, :, 3] == 0
    pixels[transparent, :3] = 0
    return Image.fromarray(pixels, "RGBA")


def bright_fabric(width: int, height: int) -> Image.Image:
    """Create a deterministic, seamless, stitch-free warm white woven field."""
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    warp = np.cos(2 * np.pi * x / 4.2) * (0.55 + 0.45 * np.cos(2 * np.pi * y / 8.4))
    weft = np.cos(2 * np.pi * y / 4.6) * (0.55 + 0.45 * np.cos(2 * np.pi * x / 9.2))
    fiber = 0.35 * np.sin(2 * np.pi * (x + y) / 19.0)
    detail = 1.15 * warp + 0.95 * weft + fiber
    base = np.array([246.0, 242.0, 238.0], dtype=np.float32)
    field = base[None, None, :] + detail[:, :, None]
    return Image.fromarray(np.uint8(np.clip(field, 0, 255)), "RGB")


def extended_lower(source: Image.Image, width: int, height: int) -> Image.Image:
    """Create a quiet photographic extension while leaving the source rectangle untouched."""
    src_w, src_h = source.size
    scale = max(width / src_w, height / src_h)
    resized = source.resize((math.ceil(src_w * scale), math.ceil(src_h * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - width) // 2
    y = (resized.height - height) // 2
    cover = resized.crop((x, y, x + width, y + height))
    radius = max(8, round(min(width, height) / 28))
    return cover.filter(ImageFilter.GaussianBlur(radius))


def resize_visible_pick(image: Image.Image, target_height: int) -> Image.Image:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("Pick has no visible pixels")
    cropped = image.crop(bbox)
    scale = target_height / cropped.height
    target_width = max(1, round(cropped.width * scale))
    return cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)


def canvas_geometry(src_w: int, src_h: int) -> tuple[int, int, int, int]:
    required_h = max(2 * src_h, math.ceil(4 * src_w / 3))
    canvas_h = math.ceil(required_h / 4) * 4
    canvas_w = canvas_h * 3 // 4
    top_h = canvas_h // 2
    bottom_h = canvas_h - top_h
    return canvas_w, canvas_h, top_h, bottom_h


def build_one(
    source_path: Path,
    pick_path: Path,
    output_dir: Path,
    pick_height_ratio: float,
    index: int,
) -> dict[str, object]:
    source = load_opaque_source(source_path)
    pick = load_transparent_pick(pick_path)
    src_w, src_h = source.size
    canvas_w, canvas_h, top_h, bottom_h = canvas_geometry(src_w, src_h)
    source_x = (canvas_w - src_w) // 2
    source_y = top_h + (bottom_h - src_h) // 2

    item_dir = output_dir / f"{index:02d}"
    item_dir.mkdir(parents=True, exist_ok=True)
    saved_pick = item_dir / "pick-transparent.png"
    pick.save(saved_pick, format="PNG", optimize=True)

    rendered = resize_visible_pick(pick, max(1, round(top_h * pick_height_ratio)))
    top = bright_fabric(canvas_w, top_h).convert("RGBA")
    pick_x = (canvas_w - rendered.width) // 2
    pick_y = (top_h - rendered.height) // 2
    if pick_x < 0 or pick_y < 0:
        raise ValueError(f"Pick is too large for upper half: {pick_path}")

    blur = max(5, round(rendered.height / 31))
    offset = max(4, round(rendered.height / 38))
    shadow_alpha = rendered.getchannel("A").filter(ImageFilter.GaussianBlur(blur))
    shadow_alpha = shadow_alpha.point(lambda value: round(value * 0.15))
    shadow = Image.new("RGBA", rendered.size, (42, 34, 30, 0))
    shadow.putalpha(shadow_alpha)
    top.alpha_composite(shadow, (pick_x, pick_y + offset))
    top.alpha_composite(rendered, (pick_x, pick_y))

    lower = extended_lower(source, canvas_w, bottom_h)
    lower.paste(source, (source_x, source_y - top_h))
    final = Image.new("RGB", (canvas_w, canvas_h))
    final.paste(top.convert("RGB"), (0, 0))
    final.paste(lower, (0, top_h))
    final_path = item_dir / "composite-3x4.png"
    final.save(final_path, format="PNG", optimize=True)

    checked = Image.open(final_path).convert("RGB")
    embedded = checked.crop((source_x, source_y, source_x + src_w, source_y + src_h))
    identity = np.array_equal(np.asarray(embedded), np.asarray(source))
    if not identity:
        raise AssertionError(f"Native source pixels changed in output: {source_path}")

    report: dict[str, object] = {
        "item": f"{index:02d}",
        "source_file": str(source_path.resolve()),
        "input_pick_file": str(pick_path.resolve()),
        "final_file": str(final_path.resolve()),
        "pick_file": str(saved_pick.resolve()),
        "dimensions_px": [canvas_w, canvas_h],
        "aspect_ratio": "3:4",
        "split": "50:50",
        "source_dimensions_px": [src_w, src_h],
        "source_rectangle_xywh": [source_x, source_y, src_w, src_h],
        "source_pixel_identity": identity,
        "source_pixel_sha256": pixel_hash(source),
        "embedded_pixel_sha256": pixel_hash(embedded),
        "pick_alpha_extrema": list(pick.getchannel("A").getextrema()),
        "pick_hidden_rgb_cleared": True,
        "pick_rendered_size_px": list(rendered.size),
        "pick_height_ratio_of_top": pick_height_ratio,
        "source_scaled_or_cropped": False,
        "text_added": False,
    }
    (item_dir / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build verified 3:4 guitar-pick layouts without scaling or cropping source images."
    )
    parser.add_argument("--sources", nargs="+", type=Path, required=True)
    parser.add_argument("--picks", nargs="+", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pick-height-ratio", type=float, default=0.40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if len(args.sources) != len(args.picks):
        raise SystemExit("--sources and --picks must contain the same number of paths")
    if not 0.15 <= args.pick_height_ratio <= 0.70:
        raise SystemExit("--pick-height-ratio must be between 0.15 and 0.70")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    reports = [
        build_one(
            source_path=source,
            pick_path=pick,
            output_dir=args.output_dir,
            pick_height_ratio=args.pick_height_ratio,
            index=index,
        )
        for index, (source, pick) in enumerate(zip(args.sources, args.picks), start=1)
    ]
    summary_path = args.output_dir / "validation-summary.json"
    summary_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"outputs": reports, "summary": str(summary_path.resolve())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
