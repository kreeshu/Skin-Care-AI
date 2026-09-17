# Cosmetic Concern Annotation Guide

Annotate only what is visibly supported by the image. These are cosmetic observations, not diagnoses.

Use `Unknown / cannot judge` whenever framing, lighting, resolution, makeup, filters, or occlusion prevent a reliable decision. Do not convert uncertainty into `Absent`.

## Usability

Mark an image unusable when it is not facial skin, is a collage, is heavily edited, has a dominant watermark, is extremely blurry/dark/bright, or does not show enough relevant skin.

## Labels

| Label | Present | Not sufficient alone |
|---|---|---|
| `blemishes` | Visible pimples, inflamed spots, blackheads, or whiteheads | Scars or pigmentation without active-looking blemishes |
| `dark_spots` | Localized darker marks or visibly uneven pigmentation | Normal shadows, freckles alone, or lighting gradients |
| `redness` | Diffuse or localized redness distinguishable from normal tone | Warm lighting, blush, or uncertain color cast |
| `visible_pores` | Clearly visible/enlarged-looking facial pores at usable resolution | Compression noise or ordinary texture at extreme zoom |
| `fine_lines` | Clearly visible facial fine lines or wrinkles | Expression folds in a single exaggerated expression |

## Review Rules

- Review all five concerns independently.
- An image may contain multiple concerns.
- The hidden source label is context only; do not assume it is correct.
- Use `Absent` only when the concern could reasonably have been seen if present.
- Use `Unknown` for parts of the face not shown.
- Add a short note for obvious mislabels, stock images, watermarks, or duplicates.
