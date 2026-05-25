---
version: alpha
name: LLM Wiki Builder
description: Dark, dense, keyboard-first desktop app for LLM-driven knowledge curation. Local-first, minimal friction, Inbox Zero metaphor.
colors:
  # Core palette — dark slate foundation with functional accent mapping
  bg-primary: "#020617"          # app background
  bg-secondary: "#0f172a"        # cards, panels
  bg-tertiary: "#1e293b"         # hover states, borders
  border-subtle: "#334155"       # dividers
  text-primary: "#f1f5f9"        # headings, primary content
  text-secondary: "#94a3b8"      # body, descriptions
  text-muted: "#475569"          # hints, disabled
  # Semantic accents
  accent-cyan: "#22d3ee"         # primary actions, active states, links
  accent-emerald: "#34d399"      # success, confirmed answers
  accent-rose: "#f43f5e"         # high priority, destructive actions
  accent-amber: "#f59e0b"        # medium priority, warnings
  accent-violet: "#8b5cf6"       # generate queries, integration
  # Derived opacities (for fill backgrounds)
  accent-cyan-10: "rgba(34, 211, 238, 0.10)"
  accent-emerald-10: "rgba(52, 211, 153, 0.10)"
  accent-rose-10: "rgba(244, 63, 94, 0.10)"
  accent-amber-10: "rgba(245, 158, 11, 0.10)"
  accent-violet-10: "rgba(139, 92, 246, 0.10)"
typography:
  # Display
  display:
    fontFamily: "Inter, Noto Sans JP, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  # Headings
  h1:
    fontFamily: "Inter, Noto Sans JP, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  h2:
    fontFamily: "Inter, Noto Sans JP, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.4
  h3:
    fontFamily: "Inter, Noto Sans JP, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.5
  # Body
  body-md:
    fontFamily: "Inter, Noto Sans JP, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
  body-sm:
    fontFamily: "Inter, Noto Sans JP, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.5
  # Mono (for IDs, code, shortcuts)
  mono-sm:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.5
  mono-xs:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "0.6875rem"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  2xl: "32px"
shadow:
  subtle: "0 1px 3px rgba(0,0,0,0.3)"
  card: "0 4px 6px -1px rgba(0,0,0,0.4), 0 2px 4px -2px rgba(0,0,0,0.3)"
  modal: "0 25px 50px -12px rgba(0,0,0,0.7)"
components:
  # Sidebar item — project list row
  sidebar-item:
    backgroundColor: "transparent"
    textColor: "{text-secondary}"
    rounded: "{rounded.lg}"
    padding: "10px 12px"
  sidebar-item-active:
    backgroundColor: "{accent-cyan-10}"
    textColor: "{accent-cyan}"
    border: "1px solid rgba(34,211,238,0.2)"
    rounded: "{rounded.lg}"
    padding: "10px 12px"
  sidebar-item-hover:
    backgroundColor: "rgba(30,41,59,0.5)"
    textColor: "{text-primary}"
  # Query card in inbox list
  query-card:
    backgroundColor: "{bg-secondary}"
    border: "1px solid transparent"
    rounded: "{rounded.lg}"
    padding: "12px"
  query-card-active:
    backgroundColor: "{bg-secondary}"
    border: "1px solid rgba(34,211,238,0.3)"
    rounded: "{rounded.lg}"
    padding: "12px"
  query-card-hover:
    backgroundColor: "{bg-tertiary}"
    border: "1px solid rgba(51,65,85,0.8)"
  # Priority indicators
  priority-high:
    borderLeft: "3px solid {accent-rose}"
    backgroundColor: "{accent-rose-10}"
  priority-medium:
    borderLeft: "3px solid {accent-amber}"
    backgroundColor: "{accent-amber-10}"
  priority-low:
    borderLeft: "3px solid {accent-emerald}"
    backgroundColor: "{accent-emerald-10}"
  # Answer buttons
  answer-btn:
    backgroundColor: "{bg-secondary}"
    textColor: "{text-secondary}"
    border: "1px solid {border-subtle}"
    rounded: "{rounded.xl}"
    padding: "12px 16px"
  answer-btn-hover:
    backgroundColor: "{accent-cyan-10}"
    border: "1px solid rgba(34,211,238,0.3)"
    textColor: "{text-primary}"
  answer-btn-selected:
    backgroundColor: "{accent-cyan-10}"
    border: "1px solid {accent-cyan}"
    textColor: "{accent-cyan}"
  # Primary CTA
  button-primary:
    backgroundColor: "{accent-cyan}"
    textColor: "#020617"
    rounded: "{rounded.lg}"
    padding: "10px 24px"
    typography:
      fontWeight: 600
      fontSize: "0.875rem"
  button-primary-hover:
    backgroundColor: "#67e8f9"
  button-primary-disabled:
    backgroundColor: "rgba(34,211,238,0.3)"
    textColor: "#475569"
  # Danger / Skip
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{text-muted}"
    rounded: "{rounded.lg}"
    padding: "10px 16px"
  button-ghost-hover:
    backgroundColor: "{bg-tertiary}"
    textColor: "{text-secondary}"
  # Form inputs
  input:
    backgroundColor: "{bg-secondary}"
    border: "1px solid {border-subtle}"
    textColor: "{text-primary}"
    rounded: "{rounded.lg}"
    padding: "8px 12px"
  input-focus:
    border: "1px solid rgba(34,211,238,0.5)"
    outline: "2px solid rgba(34,211,238,0.1)"
  # Badge / Tag
  badge:
    backgroundColor: "{bg-tertiary}"
    textColor: "{text-secondary}"
    rounded: "{rounded.full}"
    padding: "2px 8px"
    typography:
      fontSize: "0.6875rem"
      fontWeight: 500
  badge-accent:
    backgroundColor: "{accent-cyan-10}"
    textColor: "{accent-cyan}"
    border: "1px solid rgba(34,211,238,0.2)"
---

## Overview

LLM Wiki Builder is a local-first desktop application for turning unstructured knowledge (raw notes, clippings, RSS feeds) into structured Markdown wikis through LLM-driven curation. The design follows the philosophy of "maximal information density, minimal friction."

The visual language is dark-first (no light mode in v1), keyboard-centric, and uses color only for semantic meaning (priority levels, action types). Every interaction aims for "tap/keystroke to answer" — no typing required for 90% of queries.

## Colors

- **bg-primary (#020617):** Deepest slate. The canvas. Used only for the outermost app chrome.
- **bg-secondary (#0f172a):** Cards, panels, the sidebar. The primary surface.
- **bg-tertiary (#1e293b):** Hover states, subtle borders, elevated surfaces on hover.
- **accent-cyan (#22d3ee):** The only action color. Primary buttons, active states, links, selection. Cyan signals "forward motion."
- **accent-rose (#f43f5e):** High-priority queries, destructive actions, errors.
- **accent-amber (#f59e0b):** Medium-priority queries, warnings, attention without urgency.
- **accent-emerald (#34d399):** Success states, confirmed answers, low-priority items.
- **accent-violet (#8b5cf6):** Generate queries, integration actions — meta-operations that transform the system state.

Grayscale text runs from `#f1f5f9` (primary) down to `#475569` (muted/hints). No pure white (#fff) or pure black (#000) is used.

## Typography

Inter for UI chrome and body, Noto Sans JP for Japanese text, JetBrains Mono for technical identifiers (query IDs, file paths, keyboard shortcuts).

Font sizes are intentionally small — this is a dense information tool, not a marketing page. The largest type is 1.5rem for the app title. Query questions sit at 1.25rem. Everything else is 0.875rem or below.

Line heights are tight (1.2–1.6) to pack more content into the same viewport.

## Layout

The app uses a fixed three-pane layout:

1. **Sidebar (256px, collapsible to 64px):** Project list + global actions. Always visible on desktop.
2. **Query List (320px):** Scrollable list of pending queries, sorted by priority score descending. Each item shows: priority color bar, score, question preview, query type badge, raw file count.
3. **Answer Panel (flexible):** The active query expanded with full context, answer choices, optional free text, and submit actions.

On small viewports (below 1024px), the Query List becomes a collapsible drawer.

Key spacing rule: 16px between major sections, 12px within cards, 8px for related elements. No excessive whitespace — every pixel carries information.

## Elevation & Depth

No drop shadows for static elements. Shadows are reserved for:
- Modal overlays: `shadow-modal`
- Elevated cards on hover: `shadow-card`
- Active/focused input fields: subtle glow via outline

Depth is communicated primarily through border contrast, not shadow.

## Shapes

- **Cards and containers:** `lg (12px)` radius — soft but not round.
- **Buttons:** `lg (12px)` radius — matches cards for consistency.
- **Pills and badges:** `full` radius — distinct from action surfaces.
- **Inputs:** `lg (12px)` radius — visually grouped with buttons.

No sharp corners (0px radius) anywhere. Even the sidebar edges are slightly rounded at the top level.

## Components

### Query Card (Inbox List)

The most frequently viewed component. Must communicate:
- Priority at a glance (left border color)
- Whether it's the active selection (cyan border glow)
- How much raw material supports it (file count)
- What answer type it expects (badge)

On hover: background shifts to `bg-tertiary`, border appears. On active: cyan border glow.

### Answer Buttons (Query Types)

**Yes/No:** Two large side-by-side cards with emoji icons and secondary labels. Tap or `Y`/`N` key. Selected state fills with accent-cyan-10 and cyan border.

**Multiple Choice:** Vertical stack of rows with radio circles. Tap or `1`–`9` keys. Selected row gets cyan left border and background tint.

**Scale (1–5):** Horizontal row of five equally-sized buttons. Labels "Low" / "High" at ends. Tap or number keys.

**Select:** Same as Multiple Choice but with checkboxes, allowing multiple selections.

All answer types share: hover lift, keyboard shortcut display in hint bar, and an optional "Other / context" textarea below.

### Skip Action

Always present but de-emphasized. Ghost button style (`button-ghost`). Click or `S` key. Optional reason dropdown ("Not applicable", "Need more info", "Later").

### Submit Button

Primary CTA (`button-primary`). Disabled until an answer is selected. Label changes based on remaining queries: "Submit Answer →" or "Submit & Next".

### Sidebar Project Item

Two states:
- **Default:** transparent background, muted text, hover lifts to `bg-tertiary`.
- **Active:** cyan-tinted background (`accent-cyan-10`), cyan text, subtle border. A pulsing dot indicates "queries pending."

Inactive items show pending query count in muted text. Active item shows count in cyan.

### Wiki Browser (Phase 2 preview)

Read-only in Phase 1. Markdown rendered with the same color palette. Syntax highlighting for code blocks using cyan/emerald/violet accents on dark background. Internal wiki links (`[[Page Name]]`) rendered as cyan underlined text.

## Do's and Don'ts

- **Do** use keyboard shortcuts for everything. Every button must have a key equivalent.
- **Do** keep the Query List always visible. Context switching between queries should be one click.
- **Do** use color only for semantic meaning. Never use color alone to convey information — pair with text/position.
- **Do** animate transitions with `0.2s ease-out` — fast, not distracting.
- **Don't** show modal dialogs for routine actions. Inline confirmation or undo instead.
- **Don't** use light mode. The app is dark-first and will not support light mode in v1.
- **Don't** require typing for standard answers. Free text is always optional.
- **Don't** show raw LLM output (token streaming) in the UI. The app feels like a native tool, not a chat interface.
- **Don't** use border-radius below 8px. Everything should feel soft but not bubbly.
