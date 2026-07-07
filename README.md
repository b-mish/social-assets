# social-assets

Public image assets + automation playbook for the travel sites' social posts
(Facebook + Instagram via Composio MCP).

- **[PLAYBOOK.md](PLAYBOOK.md)** — full repeatable workflow (setup, image hosting, slide generation, publish steps, content rules, checklist).
- `tools/gen.py` — builds 1080×1080 HTML slides (Pexels bg + Hebrew RTL overlay) for headless-Chrome screenshots.
- `georgia/`, etc. — published image assets, served via raw.githubusercontent.com.

No secrets are stored in this repo.

## Automated publishing pipeline

- `queue/` — scheduled posts (one JSON per post, schema in `publisher/publish.py` docstring)
- `published/` — archive of published posts (moved here automatically, enriched with post IDs)
- `assets/<site>/<campaign>/` — slide JPEGs referenced by raw.githubusercontent.com URLs
- `publisher/publish.py` — runs from GitHub Actions every 30 min, publishes due posts via Composio
- Content prep happens locally via the `social-publisher` Claude Code skill.
