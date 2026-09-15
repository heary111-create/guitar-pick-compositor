# Final quality checklist

Check every item independently.

## Geometry and placement

- Canvas dimensions reduce exactly to 3:4.
- The upper and lower halves are equal in height.
- The pick is entirely inside the upper half, centered, and approximately 40% of the upper-half height unless the user specifies another size.
- Negative space is balanced and the pick is not stretched.

## Background and cutout

- Background is bright warm off-white with subtle woven variation.
- No stitches, patch edges, seams, fraying, checkerboards, white frames, strips, or rectangular halos are visible.
- Pick edge is clean with a restrained contact shadow; transparent padding does not appear as a rectangle.

## Source integrity

- `source_pixel_identity` is `true` in every validation report.
- `source_pixel_sha256` and `embedded_pixel_sha256` match.
- `source_scaled_or_cropped` is `false`.
- Only the area outside the reported `source_rectangle_xywh` may differ from the source.

## Content

- Each pick was generated in a separate call with only its matching source.
- Main subject remains recognizable.
- No new words, logos, watermarks, or decorative lines were added.
- Existing text in the lower source remains at original pixels; do not treat it as newly generated text.
