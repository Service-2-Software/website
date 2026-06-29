# Fonts

The S2S **wordmark** ("SERVICE 2 SOFTWARE" + the S² monogram) uses **TT Lakes
Condensed Bold**, a paid font.

Drop the licensed font files here:

```
assets/fonts/TTLakesCondensed-Bold.woff2
assets/fonts/TTLakesCondensed-Bold.woff   (optional fallback)
```

`assets/css/styles.css` already declares the `@font-face` for them. Until the
file is present, the wordmark falls back to **Oswald** (see `--font-wordmark`).

All other type loads from Google Fonts:
- **Oswald** — display headlines, eyebrows, buttons, nav
- **Barlow** — body copy
