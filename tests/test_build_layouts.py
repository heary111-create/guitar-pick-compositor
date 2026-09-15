from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_layouts.py"


class BuildLayoutsTests(unittest.TestCase):
    def make_source(self, path: Path) -> Image.Image:
        y, x = np.mgrid[0:61, 0:73]
        array = np.stack(((x * 3) % 256, (y * 4) % 256, (x + y * 2) % 256), axis=2).astype(np.uint8)
        image = Image.fromarray(array, "RGB")
        image.save(path)
        return image

    def make_pick(self, path: Path, transparent: bool = True) -> None:
        mode = "RGBA" if transparent else "RGB"
        fill = (0, 0, 0, 0) if transparent else (20, 20, 20)
        image = Image.new(mode, (100, 120), fill)
        draw = ImageDraw.Draw(image)
        color = (40, 130, 220, 255) if transparent else (40, 130, 220)
        draw.polygon([(15, 15), (85, 15), (50, 108)], fill=color)
        image.save(path)

    def test_builds_exact_3x4_and_preserves_source_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            source_path = temp / "source.png"
            pick_path = temp / "pick.png"
            output = temp / "output"
            source = self.make_source(source_path)
            self.make_pick(pick_path)

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--sources",
                    str(source_path),
                    "--picks",
                    str(pick_path),
                    "--output-dir",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads((output / "01" / "validation.json").read_text(encoding="utf-8"))
            final = Image.open(output / "01" / "composite-3x4.png").convert("RGB")
            self.assertEqual(final.size, (93, 124))
            self.assertEqual(report["aspect_ratio"], "3:4")
            self.assertTrue(report["source_pixel_identity"])
            self.assertFalse(report["source_scaled_or_cropped"])
            x, y, width, height = report["source_rectangle_xywh"]
            embedded = final.crop((x, y, x + width, y + height))
            np.testing.assert_array_equal(np.asarray(embedded), np.asarray(source))

    def test_rejects_pick_without_transparency(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            source_path = temp / "source.png"
            pick_path = temp / "pick.png"
            self.make_source(source_path)
            self.make_pick(pick_path, transparent=False)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--sources",
                    str(source_path),
                    "--picks",
                    str(pick_path),
                    "--output-dir",
                    str(temp / "output"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("genuine transparent", result.stderr)


if __name__ == "__main__":
    unittest.main()
