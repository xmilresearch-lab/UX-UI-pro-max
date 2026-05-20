# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**UI/UX Pro Max** (v2.5.0, package name `ui-ux-pro-max`) is an AI-powered design intelligence toolkit. It ships a searchable database of 67 UI styles, 161 color palettes, 57 font pairings, 99 UX guidelines, and 25 chart types across 15+ tech stacks. It works as a skill/workflow for AI coding assistants (Claude Code, Cursor, Windsurf, Copilot, Codex, and more).

- **Author**: NextLevelBuilder
- **License**: MIT
- **Install (end users)**: `npx uipro-cli init --ai <platform>`

## Repository Layout

```
src/ui-ux-pro-max/          ← Source of Truth for all data and scripts
  data/                     # Canonical CSV databases
    products.csv            # 161 product types (SaaS, e-commerce, portfolio…)
    styles.csv              # 67 UI styles + AI prompts + CSS keywords
    colors.csv              # 161 color palettes by product type
    typography.csv          # 57 font pairings with Google Fonts imports
    charts.csv              # 25 chart types + library recommendations
    ux-guidelines.csv       # 99 UX best practices and anti-patterns
    landing.csv             # Page structure and CTA strategies
    icons.csv, design.csv, ui-reasoning.csv, react-performance.csv, app-interface.csv, draft.csv
    stacks/                 # Per-stack guidelines (react, nextjs, vue, svelte, …)
  scripts/
    search.py               # CLI entry point (BM25 + regex hybrid engine)
    core.py                 # Search engine implementation
    design_system.py        # Design system token generation
    _sync_all.py            # Sync src/ → cli/assets/ (run before CLI publish)
  templates/
    base/skill-content.md   # Common SKILL.md content
    base/quick-reference.md # Quick reference section (Claude only)
    platforms/*.json        # Platform-specific configs (claude, cursor, …)

cli/                        # Published to npm as `uipro-cli`
  src/
    commands/init.ts        # `uipro init` command — template generation + install
    utils/template.ts       # Template rendering engine
  assets/                   # Bundled copy of src/ui-ux-pro-max/ (~564KB)

.claude/skills/             # Claude Code skills (symlink tree → src/)
  ui-ux-pro-max/            # Primary design intelligence skill
  banner-design/            # Banner generation skill
  brand/                    # Brand voice & visual identity skill
  design/                   # Comprehensive design skill
  design-system/            # Token architecture & component specs skill
  slides/                   # HTML presentation generation skill
  ui-styling/               # shadcn/ui + Tailwind styling skill

.claude-plugin/             # Claude Marketplace publishing metadata
  plugin.json
  marketplace.json

skill.json                  # Skill manifest (name, version, platforms, install cmd)
```

## Search Command

```bash
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

**Domains**: `product` · `style` · `typography` · `color` · `landing` · `chart` · `ux`

**Stack search**:
```bash
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --stack <stack>
```
Available stacks: `html-tailwind` (default) · `react` · `nextjs` · `astro` · `vue` · `nuxtjs` · `nuxt-ui` · `svelte` · `swiftui` · `react-native` · `flutter` · `shadcn` · `jetpack-compose`

The engine uses BM25 ranking combined with regex matching. Domain is auto-detected when `--domain` is omitted.

## Sync Rules — Source of Truth is `src/ui-ux-pro-max/`

**Always edit here first.** Symlinks in `.claude/`, `.factory/`, `.shared/` auto-pick up changes.

| What changed | How to propagate |
|---|---|
| `data/*.csv` or `data/stacks/*.csv` | Automatic via symlinks |
| `scripts/*.py` | Automatic via symlinks |
| `templates/base/*.md` or `templates/platforms/*.json` | Automatic via symlinks |
| CLI publish prep | Run `python3 src/ui-ux-pro-max/scripts/_sync_all.py` to copy `src/` → `cli/assets/` |

## CLI Development (`cli/`)

- **Runtime**: Bun (preferred) or Node.js
- **Build**: `cd cli && bun run build` → compiles `src/index.ts` → `dist/`
- **Dev**: `cd cli && bun run dev` → runs TypeScript directly
- **Publish prep**: run `_sync_all.py` first, then `prepublishOnly` runs `bun run build` automatically
- **Dependencies**: `commander`, `chalk`, `ora`, `prompts`

## GitHub Workflows

- **`.github/workflows/claude.yml`**: Claude Code integration for AI-assisted PRs.
- **`.github/workflows/claude-code-review.yml`**: Automated code review on PRs.
- **`.github/workflows/python-package-conda.yml`**: Python package build/test via Conda.

## Prerequisites

- Python 3.x (no external dependencies for `search.py`)
- Bun or Node.js (for CLI development)

## Git Workflow

Never push directly to `main`. Always:

1. Create a branch: `git checkout -b feat/...` or `fix/...`
2. Commit changes
3. Push branch: `git push -u origin <branch>`
4. Create PR: `gh pr create`

## Key Conventions

- **Never edit files in `cli/assets/`** directly — they are generated copies. Edit in `src/` and run `_sync_all.py`.
- **Symlinks** in `.claude/skills/ui-ux-pro-max/` point into `src/ui-ux-pro-max/` — no manual sync needed for skill use.
- When adding a new CSV column, update `core.py` and `search.py` to handle the new field.
- Platform config files in `templates/platforms/` control per-platform skill installation format; keep them consistent with `skill.json`.
