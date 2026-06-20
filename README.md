# CNC-Step RaptorX-SL 3200/S20 — Sales Page

A single-file, trilingual (DE / NL / EN) static sales page for a used **CNC-Step
RaptorX-SL 3200/S20 gantry CNC router** (2018, ≈30 operating hours, €17,000 net).

Live: https://gertdam.github.io/cnc-step-raptorx-sl-3200/

## How it works
- **`index.html`** — the entire site: HTML + embedded CSS + JS. No build step, no
  dependencies. Language is auto-detected (browser → German fallback), switchable in the
  header, and remembered via `localStorage` / `?lang=` URL param.
- **`assets/`** — web-optimized images. `img/` = full (1600px), `thumb/` = gallery (600px),
  `hero/` = hero srcset. Generated from the raw photos by the script below.
- **`scripts/optimize-images.py`** — resizes + renames the raw `images/` (messy names,
  1–5 MB) into clean web assets, and **redacts the previous owner's PII** on the
  KinetiC-NC license screenshot before it is published.

## Local preview
```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Re-generate images
```bash
python3 scripts/optimize-images.py    # requires Pillow
```

## Deploy
GitHub Pages serves the repo root (`main` branch) directly. Push to publish.

## Notes
- **`.env` is git-ignored** (Gmail + Machineseeker credentials). Never commit it.
- The raw `images/` and `do-not-use original images/` folders are git-ignored — they hold
  the **unredacted** license original. Only the redacted `assets/` images are public.
