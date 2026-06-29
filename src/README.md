# Source import area

Place the latest Claude-generated website HTML here as `src/index.html`.

## Initial import targets

- `src/index.html`: current single-file website export.
- `src/roi-calculator.html`: standalone ROI calculator source, if it remains separate during import.

## After import

Once the HTML is committed, decide whether to keep the site as a static single-file build for launch or split it into shared assets:

- `src/styles/` for CSS.
- `src/scripts/` for JavaScript.
- `src/pages/` for page-level HTML.
- `src/components/` for shared nav, footer, forms, CTA, cards, and calculator markup.

Do not split the file until the imported baseline is committed. That keeps the first diff traceable to the known Claude output.
