# tools/

## export_transcript.py

Turns a Claude Code session log (`.jsonl`) into a clean "how it was built" transcript, in two formats:

- **`.md`** - plain-text record that renders on GitHub.
- **`.html`** - messaging-app chat view (right-aligned blue bubbles for Batu with his memoji avatar, left-aligned green bubbles for Claude, skill invocations as pills, tool actions as muted "behind the scenes" notes). Self-contained: the avatar is embedded as a data URI.

### Usage

```bash
python3 tools/export_transcript.py <session.jsonl> <output.md> "<App title>" <session-short-id>
```

The matching `.html` is written next to the `.md` automatically.
Batu's avatar is read from `assets/avatar-batu.png` and embedded once per page.

### Where the session logs live

Claude Code stores logs under `~/.claude/projects/<slugified-cwd>/<session-id>.jsonl`.
The apps in this repo were built in these sessions:

| App | project dir slug | session id |
|-----|------------------|------------|
| `apps/budget2` | `-Users-batuhangundogdu-Claude-Code-Workshop-apps-budget2` | `ad7e0ced-4255-4b3a-b4bd-04a17e828aa6` |
| `apps/research` | `-Users-batuhangundogdu-Claude-Code-Workshop` | `45bef914-d73d-4e9b-8652-bff31b1b8904` |
| `apps/quiz` | `-Users-batuhangundogdu-Claude-Code-Workshop` | `978c7a29-a496-4f01-ba38-ecd68f467e53` |

### What it keeps vs. drops

- **Keeps:** user prompts (verbatim), Claude's prose, skill invocations, and AskUserQuestion Q&A (with Batu's chosen answer).
- **Drops:** harness-injected skill text (`isMeta` records), thinking, tool output, and system/meta records.
- **Collapses:** every tool call into a one-line summary.

### Planned: embed generated images (for the data-viz demo)

Not yet implemented. When the data-visualization session exists, extend the exporter to embed **every image in the session** inline as image cards:

1. image/SVG files Claude saves to the app folder (matplotlib/plotly `savefig`, etc.) - read from disk at export time;
2. inline images already in the log (images Claude read back, `preview_screenshot` results) - decode the base64 from the tool results.

Place each image right after the tool action that produced it, embedded as a data URI to keep the HTML self-contained.
