# DeepEval Session — Presentation

Slide deck for the internal session on testing AI agents with DeepEval,
grounded in this repo (`standard_agent`, `chatbot_agent`, `rag_agent`).

- **Deck:** `deepeval-session.md` (Marp Markdown)
- **Flow:** Black-box → White-box, across Standard → Chatbot → RAG agents.

## Render it

### Option A — VS Code (no install)

1. Install the **"Marp for VS Code"** extension.
2. Open `deepeval-session.md`.
3. Click the preview icon, or run **"Marp: Export slide deck…"** for PDF/PPTX/HTML.

### Option B — CLI

```bash
# one-off, no global install
npx @marp-team/marp-cli deepeval-session.md -o deepeval-session.html   # HTML
npx @marp-team/marp-cli deepeval-session.md --pdf                       # PDF
npx @marp-team/marp-cli deepeval-session.md --pptx                      # PowerPoint

# live preview while editing
npx @marp-team/marp-cli -p -w deepeval-session.md
```

> PDF/PPTX export uses a headless Chromium that Marp downloads on first run.

## Presenter notes

Each slide has speaker notes in `<!-- -->` HTML comments. Marp surfaces
these in the VS Code presenter view and in exported PPTX notes.

## Editing tips

- Slides are separated by `---`.
- Title/section slides use `<!-- _class: lead -->`.
- Theme/colors live in the `style:` block of the front matter.
