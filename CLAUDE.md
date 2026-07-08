# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file Streamlit dashboard, `Cycle Time Efficiency.py`, that analyzes manufacturing tooling cycle-time efficiency (CT Efficiency = Expected Hours / Used Hours). There is no build step, package structure, or test suite — everything lives in this one ~1500-line script.

## Commands

Install dependencies:
```
pip install -r requirements.txt
```

Run the app locally:
```
streamlit run "Cycle Time Efficiency.py"
```

In the devcontainer/Codespaces, the app auto-starts via `postAttachCommand` in `.devcontainer/devcontainer.json` on port 8501, with CORS/XSRF protection disabled for preview convenience.

There is no linter, formatter, or test suite configured — verify changes by running the app and exercising the affected tab/filter/dialog in the browser.

## Architecture

The script executes top-to-bottom as a Streamlit script (rerun on every interaction), organized into numbered sections marked by `# ====` banners:

1. **Page config** — `st.set_page_config`.
2. **CSS** — a large injected `<style>` block implementing the dark theme, card styling, and print/PDF layout overrides. Custom dashboard elements (`.dash-card`, `.kpi-title`, `.metric-row`, etc.) are hand-built HTML/CSS rendered via `st.markdown(..., unsafe_allow_html=True)`, not native Streamlit widgets — this is deliberate, keep styling consistent with these classes rather than introducing native `st.metric` cards.
3. **Data loading** (`load_base_data`, `@st.cache_data`) — generates a **synthetic** dataset with `np.random.seed(42)`. There is no real data source; every tooling record is randomly assigned into one of three `Tolerance_Status` buckets (`Fast`, `Slow`, `Within`) with hardcoded target totals (hours, shots, financials) that are distributed across records via `exact_distribute` (largest-remainder rounding to hit exact integer targets). When modifying the data model, preserve this "hardcoded totals distributed via weights" pattern so KPI totals stay deterministic.
4. **Sidebar filters & financials** — time range, custom date picker, labor/machine rate inputs (used to scale `Base_Fin_Gain`/`Base_Fin_Loss` into `Financial_Gain`/`Financial_Loss` via `rate_scalar`), and cascading `multiselect` filters (OEM → Supplier → Toolmaker → Plant → Tooling Type → Product → Part → Tooling) that progressively narrow `filtered_df`. All downstream sections read only from `filtered_df`.
5. **Global calculations & helpers** — aggregate KPIs (`gained_hrs`, `lost_fin`, etc.), `calc_weighted_eff` (shot/hour-weighted efficiency), `format_hm` (hours→"XH YM"), and `compute_comprehensive_row` — the central per-group rollup function (used for both Tooling ID and Supplier grouping) that produces the full detail-table row (ACT, WACT, fast/slow splits, financials, `Performance Status`). Column-order lists for these detail tables are duplicated at each call site rather than factored into a shared constant — when adding a column, update every occurrence of the `cols = [...]` list.
6. **Helper renderers** — `render_entity_details` and `render_ranking_tooling_drilldown` are factored out of the `@st.dialog` functions specifically to avoid Streamlit's nested-dialog restriction (a dialog can't open another dialog; these are called as plain functions inside an already-open dialog to render "drill one level deeper" content inline, using `st.session_state` to persist the drilldown selection across reruns).
7. **Dialogs/popups** (`@st.dialog`) — modal detail views (widget breakdown, entity drilldown, "see all" rankings, total-toolings breakdown). Dialogs are invoked lazily via a single `dialog_action` tuple set during widget rendering and dispatched once at the bottom of the script (section 9) — this indirection exists because Streamlit dialogs must be triggered from top-level script flow, not from arbitrary nested callbacks.
8. **Main UI layout** — three tabs: **Overview Summary** (gain/loss KPI cards + per-category top-3 fastest/slowest charts for Supplier/Tooling Type/Product/Part), **Comparison Analysis** (compare tools or suppliers making the same part, dual-axis bar+line chart), **Full Rankings & Details** (complete ranked tables per category with drilldown).
9. **Dialog invocation router** — reads `dialog_action` and calls the matching dialog function; must run after all tabs so any button click within a tab this rerun gets dispatched.

### Key conventions

- **Performance Status thresholds** are fixed and repeated across the file: efficiency `> 105%` = `Fast` (green), `< 95%` = `Slow` (red/yellow depending on context), else `Within` (green). Colors: `Fast` = `#d9534f` (red, since fast tooling wear implies risk), `Slow` = `#eab308` (yellow), `Within` = `#5cb85c` (green) — note the color mapping is inverted from typical "green=fast" intuition; keep it consistent with existing charts.
- **Drilldown pattern**: selectbox + separate "View" button, gated with `st.session_state` so the detail panel persists across reruns until a new selection is confirmed. New drilldowns should follow this same selectbox-then-button-then-session_state pattern rather than rendering on selectbox change alone (which would fire before the user finishes browsing options).
- **PDF export** (`export_pdf_ui`) injects a JS button (via `components.html`) that force-displays all tab panels, triggers a resize (so Plotly redraws), calls `window.print()`, then reverts — paired with the `@media print` CSS block in section 2.
- All monetary/hour/shot figures flow from the same `filtered_df`; avoid introducing a second source of truth — add new metrics as columns on `filtered_df` or derive them in `compute_comprehensive_row`/`generate_ranking_table_data`.

## Git workflow

After every meaningful code change in this repo, automatically `git add`, commit with a clear, descriptive message, and `git push` to the `origin` remote — do this without asking for confirmation first. "Meaningful" means a change that alters app behavior, fixes a bug, or adds/removes functionality; trivial or purely exploratory edits don't need a commit. Still avoid destructive git operations (force-push, reset --hard, etc.) without explicit approval.
