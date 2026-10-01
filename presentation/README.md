# DeepEval Session — Presentation

Slide deck for the internal session on testing AI agents with DeepEval,
grounded in this repo (`standard_agent`, `chatbot_agent`, `rag_agent`).

There are **three** deliverables of the same 45-slide deck:

- **Plain** (`deepeval-session.*`) — clean light theme (blue headings, orange
  bold accents). No branding.
- **integrant — image** (`deepeval-session-integrant.*`) — Marp render with the
  **integrant** brand DNA (cyan `#20B9EC`, orange `#ED7D31`, logo footer).
  Pixel-perfect, but each slide is a flat **image** (not editable in PowerPoint).
- **integrant — editable** (`deepeval-session-integrant-editable.pptx`) — native
  PowerPoint built with `python-pptx` on the company template: real, **editable**
  text boxes, bullet lists, code blocks and tables, with the integrant logo,
  rules and orange corner square on every slide.

Both Marp versions share the same slide content — only the `style:` block differs.
Edit the narrative in `deepeval-session.md`, then port intended content changes
into `deepeval-session-integrant.md` (keep the two `style:` blocks as-is).

## Files

| File | Use |
|---|---|
| `deepeval-session.md` | Plain source deck (Marp Markdown) |
| `deepeval-session.html` / `.pptx` | Plain HTML / PowerPoint exports |
| `deepeval-session-integrant.md` | Branded source deck (Marp Markdown) |
| `deepeval-session-integrant.html` / `.pptx` | Branded HTML / image-based PowerPoint |
| `deepeval-session-integrant-editable.pptx` | **Editable** native PowerPoint (python-pptx) |
| `build_integrant_pptx.py` | Builds the editable branded `.pptx` from `deepeval-session.md` |
| `assets/integrant-logo.png` | Brand logo used in the branded footer |
| `Integrant-Basic-Presentation-En-Template.pptx` | Company template (brand-color source) |

## Render / export

### Option A — VS Code (no install)

1. Install the **"Marp for VS Code"** extension.
2. Open the `.md` you want (`deepeval-session.md` or `deepeval-session-integrant.md`).
3. Click the preview icon, or run **"Marp: Export slide deck…"** for PDF/PPTX/HTML.
   For the branded deck, enable *"Export: Allow Local Files"* in the Marp
   extension settings so the logo embeds.

### Option B — CLI

```bash
# ---- Plain deck ----
npx @marp-team/marp-cli deepeval-session.md -o deepeval-session.html
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  npx @marp-team/marp-cli deepeval-session.md --pptx -o deepeval-session.pptx

# ---- Branded (integrant) deck — needs --allow-local-files for the logo ----
npx @marp-team/marp-cli deepeval-session-integrant.md --allow-local-files \
  -o deepeval-session-integrant.html
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  npx @marp-team/marp-cli deepeval-session-integrant.md --allow-local-files \
  --pptx -o deepeval-session-integrant.pptx
```

> `--allow-local-files` is required for the branded logo footer to render.
> PowerPoint export needs a local Chrome; `CHROME_PATH` points Marp at it to
> skip a slow download. The PPTX renders each slide as a full-slide image
> (pixel-perfect to the HTML).

### Option C — Editable branded PowerPoint (python-pptx)

The Marp PPTX exports are flat images. To get a **fully editable** PowerPoint
on the company template (real text boxes, bullets, code blocks, tables):

```bash
python build_integrant_pptx.py   # -> deepeval-session-integrant-editable.pptx
```

Requires `python-pptx` and `pillow` (already in the project venv). The script
parses `deepeval-session.md` and lays out native shapes on the template's
layouts, drawing the integrant logo, rules and orange corner square per slide.
Re-run it after editing the deck content in `deepeval-session.md`.

## Presenter notes

Each slide has speaker notes in `<!-- -->` HTML comments. Marp surfaces
these in the VS Code presenter view.

## Editing / theming tips

- Slides are separated by `---`.
- Title/section slides use `<!-- _class: lead -->`.
- All colors, fonts, and (for the branded deck) the logo footer live in the
  `style:` block of each file's front matter:
  - **Plain**: headings blue `#0969da`, bold orange `#bc4c00`.
  - **integrant**: headings cyan `#20B9EC`, bold/accents orange `#ED7D31`,
    table headers cyan, page numbers orange, and `section::before` places the
    integrant logo bottom-left.
