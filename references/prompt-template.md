# Independent guitar-pick prompt

Use one invocation per source image. Replace the bracketed subject notes after visually identifying only the principal elements that should appear on the pick.

```text
Use case: product-mockup
Asset type: isolated guitar-pick cutout for later deterministic compositing
Input image: Image 1 is the sole visual reference and supplies the subject, palette, and design elements.
Primary request: Create one complete, physically believable plastic guitar pick featuring [the main subject and two or three defining visual elements from Image 1]. Recompose those elements coherently inside the rounded triangular pick boundary while keeping the subject recognizable.
Style/medium: realistic premium printed plastic guitar pick, subtle resin depth, clean beveled edge, restrained gloss.
Composition/framing: exactly one pick, fully visible, upright, centered, front-facing with only slight natural perspective; generous transparent margin.
Lighting/mood: soft studio lighting; retain the source image's dominant palette and mood.
Text: none.
Constraints: output only the guitar pick; genuinely transparent background with preserved alpha; clean antialiased silhouette; no crop; no external scene; no hand holding the pick; no fabric; no case; no extra objects; no logo; no watermark.
Avoid: any source caption unless explicitly requested, new letters, checkerboard rendered into pixels, rectangular panels, white frames, seams, stitching, fringes, captions, and decorative lines.
```

## Prompt decisions

- Describe recognizable subject content, palette, and composition; do not copy irrelevant background detail.
- If the source contains text, exclude it from the pick by default. The lower-half original will retain it exactly.
- Preserve the original medium when it matters: photographic sources stay photographic; illustrations stay illustrated.
- For multiple images, keep the shared product/material wording stable but adapt the subject line separately. Do not include information from another source.
- Ask for actual transparency. A displayed black or checkerboard surround is acceptable only if inspection of the saved PNG confirms those pixels are transparent.
