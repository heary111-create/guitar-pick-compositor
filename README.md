# Guitar Pick Compositor

`guitar-pick-compositor` is a Codex skill for turning each supplied image into an independently generated guitar pick and assembling a verified portrait 3:4 presentation.

The image model creates only the transparent pick. A deterministic Python helper creates the bright woven upper background, places the original source image at native decoded pixels in the lower half, and verifies pixel identity after export.

## What it does

- Runs one image-generation call per source so subjects and styles do not bleed between items.
- Requests one complete plastic guitar pick with a genuine transparent background.
- Creates a 3:4 canvas split equally between the pick presentation and original image.
- Keeps the pick small, centered, and surrounded by generous whitespace.
- Never resizes or crops the source rectangle unless the user explicitly overrides that rule.
- Writes SHA-256 and pixel-array validation results for each finished layout.

## Installation

Copy this repository to your personal Codex skills directory as `guitar-pick-compositor`. The resulting path should contain `SKILL.md` at its root.

Invoke it explicitly with:

```text
Use $guitar-pick-compositor to create one independent guitar pick per attached image and assemble verified 3:4 layouts.
```

It also permits normal automatic discovery for matching guitar-pick layout requests.

## Requirements

- Codex with the built-in image-generation tool for creating the pick assets.
- Python 3.10 or newer.
- Pillow and NumPy for deterministic compositing and validation.
- Opaque source images and generated pick PNGs containing both transparent and opaque alpha values.

## Helper usage

After saving one transparent pick PNG for every source image, keep both lists in the same order:

```powershell
python scripts/build_layouts.py `
  --sources source-1.png source-2.png `
  --picks pick-1.png pick-2.png `
  --output-dir output/guitar-picks
```

Each numbered output folder contains `composite-3x4.png`, `pick-transparent.png`, and `validation.json`. The output root also contains `validation-summary.json`.

## Repository map

- `SKILL.md` — routing, invariants, and required workflow.
- `agents/openai.yaml` — Codex interface metadata and invocation policy.
- `references/prompt-template.md` — canonical prompt scaffold for one independent pick.
- `references/quality-checklist.md` — visual and pixel-integrity checks.
- `scripts/build_layouts.py` — deterministic compositor and validator.
- `scripts/validate_repository.py` — repository structure check.
- `tests/` — script behavior tests using synthetic images only.

## Privacy and publication scope

No user source images, generated picks, finished layouts, machine paths, or private reference textures are included in this repository. The woven background is generated procedurally by the helper.

## Limitations

- A prompt requesting transparency does not guarantee alpha; the saved PNG must be inspected and invalid picks are rejected.
- The helper accepts opaque rectangular source images. It deliberately rejects sources containing transparency because flattening them would violate exact pixel preservation.
- Pixel identity refers to decoded RGB pixels embedded in the output PNG, not byte-for-byte identity with the original compressed file.
- Image-generation quality still depends on the available model and the supplied visual reference.

## Validation

```powershell
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

The tests create temporary synthetic images; they do not upload or retain user content.

## License

Licensed under the MIT License. See `LICENSE`.
