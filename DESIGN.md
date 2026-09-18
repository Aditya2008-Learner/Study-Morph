# AS Study — Design System Document

> **App names in this repo are not uniform.** The backend titles the product "Assignment Sorter & AI Study Assistant"; the landing page brands it "Lumina Study Platform"; the chat assistant calls itself "Antigravity Academic AI". **This is the first design debt item to fix (see [Branding](#branding)).** For a system description, this document uses the working name **AS Study**.

---

## 1. Design Read

**This is a dense product UI, not a marketing page.** AS Study is an education dashboard for a B.Tech CSE student: 11 tool views around assignments, question banks, quizzes, OCR notes, grading, and RAG chat. Screens are **scannable first, decorated never**.

The visual language is **quiet competence**:

- **Lead with content.** Hierarchy, whitespace, and structure carry every screen before color does.
- **Desaturated, substance-first surfaces.** Dark slate default, light slate alternate. One service color, used once for a purpose.
- **One vivid accent.** The emerald from the brand mark is the *only* semantic color that is allowed to "pop". Everything else falls back to inks and grays.
- **Tone is UI text.** Structure interface copy with lists, segments, and plain labels, not decorative flourishes.

### Current-state audit (what the code actually ships today)

| Area | Observed state |
|---|---|
| Shell | `styles.css` + `components.css` drive an app shell (sidebar, header, view panels) that exists in the *committed* `index.html` but was **replaced in the working tree by the "Lumina" landing page**. `app.js` and both stylesheets still target the app shell, so restoring/refactoring it must keep these element IDs. |
| Theme | Two themes: `data-theme="dark"` (default, hardcoded `:root`) and `data-theme="light"` override block. |
| Identity | Marketing page (Instrument Serif, emerald, dark) and app shell (Inter, emerald + cyan accents) do **not** feel like the same product. |
| Typography | Inter (app) vs Inter + Instrument Serif (landing). Mono (JetBrains Mono) reserved for numbers, labels, and keys. |
| Color | Emerald `#059669` primary, cyan `#0891b2` accent, blue-tinted shadows leak into both themes (see [Color](#color)). |
| Iconography | Font Awesome 6.5.1 everywhere, `strokeWidth` irrelevant (fills). All UI glyphs come from FA, not hand-rolled SVGs. |
| Components | Buttons, badges, cards, grid, forms, dropzone, flashcards, quiz, chat, modal, toasts, progress bar, status indicators. |

---

## 2. Design Principles

1. **Scannability** — a screen is usable at a glance. Lead with the data; show hierarchy, whitespace before color; structure before decoration.
2. **Quiet competence** — information surfaces are desaturated and minimal. The content is the design.
3. **Vivid accent** — emerald is the single accent. It is used for actions, active state, and success signal only. Screens are otherwise black/white.
4. **Tone is UI text** — use lists, segments, and plain text to structure interface copy. No emoji, no decorative flourishes, no text-art.

---

## 3. Color

### 3.1 Palette (canonical tokens)

Tokens are declared on `:root` and overridden under `[data-theme="light"]` in `src/static/css/styles.css`.

| Token | Dark | Light | Use |
|---|---|---|---|
| `--primary` | `#059669` | `#059669` *(same)* | **The single accent.** Primary action buttons, active nav, links, progress fill, success. |
| `--primary-hover` | `#047857` | `#047857` | Hover for primary actions. |
| `--primary-dim` | `rgba(5,150,105,0.12)` | `rgba(37,99,235,0.08)` ⚠️ | Focus rings, selected states, soft icon wells. **Bug: light theme dim is blue-tinted and mismatches the emerald brand.** |
| `--accent` | `#0891b2` | `#0891b2` | Secondary informational accent (citations, cyan stat text). |
| `--success` | `#059669` | `#059669` | Positive state. Same value as primary by design. |
| `--warning` | `#d97706` | `#d97706` | Warning state. |
| `--danger` | `#dc2626` | `#dc2626` | Destructive / error state. |
| `--bg-main` | `#fafaf9` ⚠️ | `#f8fafc` ⚠️ | App canvas. **Two different named grays (stone vs slate) between and *within* themes — see bug below.** |
| `--bg-card` | `#ffffff` | `#ffffff` | Card / input surface. |
| `--bg-card-hover` | `#f5f5f4` | `#f1f5f9` | Hover fills. *Again stone-vs-slate.* |
| `--bg-header` | `rgba(10,14,26,0.88)` | `rgba(255,255,255,0.92)` | Sticky top header (blurred). |
| `--border-color` | `#e7e5e4` | `#e2e8f0` | Default hairline. |
| `--border-light` | `#d6d3d1` | `#cbd5e1` | Stronger hairline (hover borders, input focus). |
| `--text-main` | `#1c1917` ⚠️ | `#0f172a` | Primary text. **Dark theme text is warm stone on an often-slate background; light theme is slate.** |
| `--text-secondary` | `#57534e` | `#334155` | Secondary text. |
| `--text-muted` / `--text-dim` | `#a8a29e` | `#475569` / `#94a3b8` | Muted and optional metadata. |

**Shadows** (tinted, never pure black on light surfaces):

- `--shadow-sm: 0 1px 3px rgba(0,0,0,0.3)` (dark) / light `0 1px 2px rgba(0,0,0,0.06)`
- `--shadow-md`, `--shadow-lg` scale up progressively.
- `--shadow-glow: 0 0 24px rgba(5,150,105,0.25)` — reserved for the emerald brand glow only (dropzone hover, active brand mark).

### 3.2 Rules

- **One accent.** Emerald is the accent. Cyan is the *informational* secondary, warning amber and danger red are *state* colors. Nothing else may carry hue.
- **No pure `#000` / `#fff` as fills.** Use off-blacks and off-whites; they preserve depth.
- **State colors are load-bearing.** Difficulty maps: `Easy → success`, `Medium → primary`, `Hard → warning`, `Advanced → danger` (see `diffBadges` in `app.js`).
- **Badge tints** use a background = `rgba(<hue>, 0.12)` with a `border: 1px solid rgba(<hue>, 0.25)` — never flat fills.

### 3.3 Known debt (fix list)

1. **`--primary-dim` light override is blue** (`rgba(37,99,235,0.08)`). Should be emerald `rgba(5,150,105,0.12)` to match the brand.
2. **Mixed gray families.** Dark theme is stone (`#57534e`, `#e7e5e4`, warm text), light theme is slate (`#334155`, `#e2e8f0`, cool text). Pick **one** neutral family and derive both themes from it.
3. **Hardcoded blue shadows** leak in: `.nav-item.active` uses `box-shadow: 0 2px 8px rgba(37,99,235,0.3)`; `.btn-primary:hover` uses the same blue. Should be emerald-tinted.
4. **Body background mix** `linear-gradient(160deg, #fafaf9 0%, #0a1122 40%, #f5f5f4 70%, #e7e5e4 100%)` embeds a hard navy band that matches neither theme token. A flat `--bg-main` canvas is the intended system.
5. `.badge-purple` (`rgba(139,92,246,…)`) is used once (`Generator` badge) — a palette one-off. Either promote purple to a documented token or map it to the accent.

---

## 4. Typography

### 4.1 Stacks

| Role | Stack | Notes |
|---|---|---|
| Sans (app + landing) | `Inter` (`--font-sans`) | `300,400,500,600,700,800` loaded from Google Fonts. A neutral humanist sans is the right default for an education tool (see skill §4.1, Inter override allowed for neutral / accessibility-first). |
| Serif (marketing only) | `Instrument Serif` | **Banned in the product UI.** Reserved for the landing page's editorial hero (`Study. Practice. Track.`). Do not mix families inside headlines (skill §4.1 emphasis rule). |
| Mono | `JetBrains Mono` (`--font-mono`) | Numbers, kbd hints, code, metadata labels, percentage values. |

### 4.2 Scale

Declared as `--font-scale-*` in `styles.css`. Body base is **15px** (`html { font-size: 15px }`).

| Token | Size | Typical use |
|---|---|---|
| `--font-scale-xs` | `0.7rem` | Badges, kbd shortcuts, status rows |
| `--font-scale-sm` | `0.8rem` | Body secondary, form labels, nav items |
| `--font-scale-md` | `0.95rem` | Default body, card titles |
| `--font-scale-lg` | `1.05rem` | Page titles, section headers |
| `--font-scale-xl` | `1.15rem` | Sub-feature headings |
| `--font-scale-xxl` | `2.2rem` | Course page H1 |

Line heights: `--line-tight 1.05`, `--line-normal 1.45`, `--line-relaxed 1.55`.

### 4.3 Voice

- **Task-first verbs.** `Generate Assignment`, `Start Timed Quiz`, `Save Assignment`, `Find Papers`. No filler verbs (elevate, unleash, seamless).
- **One register per screen.** Technical metadata is mono and muted; action labels are terse sentence case. No decorative middot chains; separate with hairlines or columns.
- **No em-dashes.** Use commas, colons, or periods (skill §9.G). Hyphens only for compound words and ranges.
- **Chat brand is inconsistent.** `app.js` renders "Antigravity Academic AI"; the committed shell's chat welcome also says "Antigravity Academic AI", but the landing calls the product "Lumina". Pick one product name and use it in every assistant-facing string.

---

## 5. Space, Shape, Elevation

### 5.1 Spacing scale (base 4 in `rem`)

```
--space-1  .25rem  --space-2  .5rem   --space-3  .75rem  --space-4  1rem
--space-5  1.25rem --space-6  1.5rem  --space-8  2rem    --space-10 2.5rem --space-12 3rem
```

- Content column gap: `--space-4` (grids) / `--space-5` (view sections).
- Cards: `--space-5` padding inside; `--space-4`/`--space-6` between cards.
- Standardize on `gap` (not margins-between-siblings) for stacked UI groups.

### 5.2 Radii (single system)

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | `6px` | Buttons, inputs, selects, nav items, question rows, small chips |
| `--radius-md` | `10px` | Cards, chat bubbles, search bar, dropzone surface |
| `--radius-lg` | `14px` | Flashcard faces, dropzone |
| `--radius-xl` | `20px` | Modal surface |

**Shape rule:** interactive controls are `sm`; containers are `md`; the flashcard and modal are the only `lg`/`xl`. Pill (`9999px`) is reserved for **badges, progress bars, and the landing CTAs** only — never for cards or buttons in the product UI. One radius per shape family, applied everywhere (skill §4.4).

### 5.3 Elevation

- **Elevation communicates hierarchy, not decoration** (skill §4.4). The shell uses overlay borders (`1px hairline`) and tinted shadows, not heavy cards-on-cards.
- Cards exist only where surface separation matters (data tiles, form blocks). Within a card, divide rows with `divide-y` hairlines rather than nested cards.
- Tinted shadows: dark theme shadows carry a black tint scaled by depth; light theme shadows are near-invisible (`0.06`/`0.08`/`0.10`). Never pure-black drops on light surfaces.

### 5.4 Layout constants

- `--sidebar-w: 256px` → collapses to **60px icon rail** at `≤1024px`.
- `--header-h: 56px` sticky header, `backdrop-filter: blur(12px)`.
- Grid: `grid-cols-1/2/3/4` in `components.css` (`gap: var(--space-4)`). View panels collapse to single column at `≤768px`.
- Content region: `--space-5` vertical, `--space-6` horizontal padding on the scroll container.
- Never `h-screen` for full-viewport elements; use `min-h-[100dvh]` where a viewport-relative height is needed (skill §3.E).

---

## 6. Components

### 6.1 Buttons (`components.css` `.btn`)

Base: inline-flex, `--radius-sm`, weight 600, `gap` between icon/label, `:active` pressed via `scale(0.97)`, disabled at `opacity: 0.5`.

| Variant | Fill | Text | Use |
|---|---|---|---|
| `.btn-primary` | `--primary` | white | **Primary action per view.** One per view at most. |
| `.btn-secondary` | `--bg-card` + hairline | `--text-main` | Default action, secondary tools. |
| `.btn-success` | `--success` | white | Positive confirm (Grader's "Check & Grade"). |
| `.btn-danger` | `--danger` | white | Destructive. |
| `.btn-warning` | `--warning` | white | Warning. |
| `.btn-info` | `--accent` | white | Informational (Study Now). |

Sizes: `.btn-sm` (0.25/0.55rem), `.btn-lg`, `.btn-icon` (32×32 square).

**Rules:** labels stay on one line at desktop; text contrast ≥ WCAG AA 4.5:1 on every fill; no two buttons with the same intent on one screen. Loading swaps label to a spinner icon + "Generating..." (see `app.js`).

### 6.2 Badges (`components.css` `.badge`)

Pill, weight 600, `--radius` pill. Semantic map:

- `badge-primary` (emerald dim) — neutral/active metadata (e.g. "Primary")
- `badge-success` (emerald) — easy, completed, saved
- `badge-warning` (amber) — medium-perplexing, hard
- `badge-danger` (red) — advanced, unresolved
- `badge-info` (cyan) — type metadata, tags
- `badge-blue` (violet) ⚠️ — one-off, see debt #5

Badges communicate **semantic state**, not decoration. A badge must be the only hue on its row unless it is genuinely distinguishing items.

### 6.3 Cards

- 1px hairline (`--border-color`), `--radius-md`, `--space-5` padding, tinted `--shadow-sm`.
- Hover: tighten border (`--border-light`) + `--shadow-md`. Never float cards with `translateY` in dense data screens; that motion is for the landing cards only.
- `.card-header`: title (`.card-title`, 0.95rem / 700) left, actions/badges right, hairline below.

### 6.4 Forms

- **Label above input** (`.form-label`, 0.75rem / 600 / `--text-muted`). Labels never double as placeholders (skill §4.6).
- `.form-input` / `.form-select` / `.form-textarea`: hairline, `--bg-main` fill, `--radius-sm`.
- Focus: `border-color: var(--primary)` + a `2px` ring of `--primary-dim`. The ring is the focus signal — preserve it in both themes.
- Placeholder text: `--text-dim`, must stay ≥ 4.5:1 in light theme.

### 6.5 Data entities

- **Assignment card** (`.assignment-card`): subject title (700), meta row (muted, icon-prefixed), status row, up to 4 topic badges, question count.
- **PYQ card** (`.pyq-card`): title, metadata line (college · Sem · year · exam type), Source action.
- **Notebook card** (`.notebook-card`): name, type · size · subject · sem, summary clamp, topic badges.
- **Curriculum card** (`.curriculum-card`): code + name, meta (Sem · credits · category), module breakdown, and 3 actions (Study Now / Generate Assignment / Quiz).
- **Question row** (`.question-item`): question text clamp, difficulty/type/marks/source badges, `View` + `Generate Similar`.

### 6.6 Special components

| Component | Surface | Interaction notes |
|---|---|---|
| `.dropzone` | 2px dashed hairline, `--radius-lg` | Drag-over → emerald border + `--bg-primary-dim` + `--shadow-glow`. |
| `.flashcard-wrapper/.inner/.face` | 3D flip, `--radius-lg`, `--shadow-lg` | Front = dark gradient; back = deeper navy-blue gradient. **Debt: blue gradient faces don't match the emerald brand — consider emerald-tinted grads.** |
| `.quiz-option` | card row + circular `.opt-indicator` (A/B/C/D) | Selected = primary tint; correct = success tint; wrong = danger tint. Pointer-events frozen after answer, 1200ms advance. |
| `.chat-bubble` | user = emerald→blue gradient fill right-aligned ⚠️; assistant = `--bg-main` left, hairline | ⚠️ the user bubble uses **blue** `linear-gradient(135deg,#1e40af,#2563eb)`. Convert to emerald or a neutral ink (debt). |
| `.modal-backdrop/.content` | `rgba(0,0,0,0.7)` + `blur(4px)`; `--radius-xl` surface | Mutation-modal and detail-modal share this system. |
| `.toast` | flat semantic fill, `--shadow-lg`, bottom-right stack | `toast-success/-error/-info`. Auto-dismiss 3.5s. |
| `.progress-bar` (+ `.progress-bar-fill`) | 5px track `--bg-main`, pill, emerald fill | Used on quiz results. |
| `.status-indicator` | 7px dot + glow | C-core = cyan, others = emerald. 7px dot only for live engine state, once per footer. |

---

## 7. Layout & Navigation (Information Architecture)

### 7.1 App shell (`app-container` → `sidebar` + `main-wrapper`)

- **Sidebar** (256px, icon rail at `≤1024px`): brand mark + name, two nav groups, engine-status footer.
  - *Core Repository:* Assignments, Previous Year Papers, Notebook OCR & Notes, Question Bank, Curriculum Browser.
  - *AI Study Tools:* Assignment Generator, Helper & Grader, Note Maker & Flashcards, AI Quiz & Weakness Radar, RAG Academic Chat, Recommendations.
- **Top header** (56px, blurred): current-view title, global search (with `Ctrl K` kbd hint), theme toggle, primary "New Assignment".
- **Content region**: horizontally scrollable view panels, each `.view-panel` toggled by `switchView()`; only one `.active`.

**IA rule:** view order is fixed by the sidebar. Titles come from `viewTitles` in `app.js` (`switchView` sets both `.active` panel and the header title). Preserve the `data-view` ↔ `id="view-*"` ↔ nav-title contract when refactoring.

### 7.2 Landing → app bridge

The landing page's `.study-link` CTAs call `studyTopic(courseCode, courseName, …)` which **opens `course.html` directly** (`/static/templates/course.html?course=…&name=…`). In-app "Study Now" calls the same `window.studyTopic`, but switches to the *in-app* curriculum/question-bank panel instead. Two different destinations behind one function name is a UX debt (see [Known debt](#8-known-debt--roadmap)).

### 7.3 Keyboard & a11y

- `Ctrl K` → global search (hinted by `.kbd-shortcut`).
- Focus rings are the `--primary-dim` 2px ring (both themes).
- Motion honors `prefers-reduced-motion`: `.reveal` collapses to static (already present in `styles.css` and the landing).
- Landing + course pages declare `lang="en"`; app shell uses font-awesome `aria-hidden` on glyphs and real text labels next to them. Keep the pattern.

---

## 8. Theme Modes

- **Default: `data-theme="dark"`** (set on `<html>` in `index.html`; `app.js` reads/keeps it via `state.theme`).
- **Light:** toggled by the header button (`#theme-toggle-btn`), sets `data-theme="light"`, swaps moon→sun icon.
- **One mode active per view; sections never invert** (skill §4.11). A hardcoded hex inside a `[data-theme="light"]`-only override is a bug, not a feature.

**Token strategy:** CSS variables swapped on `[data-theme="light"]`. Do *not* introduce Tailwind `dark:` variants into these vanilla sheets; keep one strategy (skill §8.A).

**Priority fixes for correct theming:** (1) unify `--primary-dim`; (2) unify the neutral gray family; (3) move hardcoded blue shadows to emerald tokens; (4) replace the navy body gradient with `--bg-main`; (5) audit every literal `#…` in `app.js` templates (many inline `rgba` on success/danger/accent) and promote to tokens so both themes stay consistent.

---

## 9. Motion & Interaction States

- **`MOTION_INTENSITY = 3`.** No ambient animation. All motion is *motivated* (skill §5): view switch `fadeIn 0.18s`; card hover hairlines; `:active` button press; confetti on success (already referenced in shell). Scroll-reveal is a landing-only device.
- **Reduced motion:** everything above collapses to instant/static under `prefers-reduced-motion` (enforced in `styles.css` and landing).
- **Loading / empty / error states are required on every data panel** (skill §4.5). Current pattern: inline muted text ("Loading…", "No assignments found.", "Failed to load.") — adequate; when a panel grows, use a skeleton matching the card grid.
- **Tactile feedback:** `:active` on buttons → `scale(0.97)`; cards do not lift (`translateY`) in the dense app, only on the landing.

---

## 10. Accessibility

- **Contrast:** body text ≥ 4.5:1 in both themes (audit `--text-muted` at 475569 on `#f8fafc` and `#a8a29e` on `#fafaf9`; borderline in dark). Buttons: white on emerald `#059669` ≈ 3.5:1 — acceptable for large/UI text, but raise to `#047857` (or white at 600px+ weight) for small buttons of 0.75rem. **Audit `.btn-sm` in light mode.**
- **Focus visibility:** the 2px `--primary-dim` ring is the keyboard focus signal on every control; keep it.
- **Labels:** every input has a visible `.form-label` (no placeholder-as-label). Icons carry `aria-hidden` plus adjacent real text. The nav `#dropdown` equivalents are `<a>`/`<button>` with real labels.
- **Reduced motion + reduced transparency honored** (`prefers-reduced-motion` present; `backdrop-filter` on the header should have a solid-fill fallback for `prefers-reduced-transparency`).

---

## 11. Branding

- **Pick one product identity.** Recommended: **"AS Study — AI Academic Assistant"** (keeps the "Assignment Sorter" heritage and the graduating-cap mark, aligns the chat persona and the landing hero). Set it in:
  - SVG/`<title>` → both HTML documents
  - `viewTitles`-adjacent strings in `app.js`
  - Footer/copyright line
  - Chat assistant display name (currently "Antigravity Academic AI")
- **Brand mark:** 34×34 (app) / 28×28 (landing) rounded square, emerald→cyan gradient `linear-gradient(135deg,#059669,#0891b2)`, white glyph. The gradient is the brand's only gradient; keep it identical in both surfaces.
- **Landing editorial voice** ("Study. *Practice.* Track.") may use Instrument Serif italics in the hero only; the app shell stays Inter.

---

## 12. Known Debt & Roadmap

Prioritized for a design-consistency pass (each is verifiable in `styles.css`, `components.css`, `index.html`, `course.html`, `app.js`):

1. **Restore/decide the app shell.** Working-tree `index.html` is the marketing page; `app.js` + both stylesheets target an app shell that exists only in `git show HEAD:src/static/templates/index.html`. Either restore that shell (and keep it served at `/`) or re-architect the marketing page to embed/route to it. Until this is resolved, the product UI and the landing page diverge.
2. **One product name** across title, chat persona, and footer.
3. **Unify gray families** (stone vs slate) — pick one neutral for both themes.
4. **Emerald-only accent:** fix `--primary-dim` light override, blue nav/button shadows, blue chat-bubble gradient, and the blue flashcard-back gradient.
5. **Remove the navy body gradient** in favor of `--bg-main`.
6. **Resolve `.badge-purple`** (promote to a token or map to accent).
7. **Single `studyTopic` navigation path** — landing and in-app "Study Now" should route to the same destination.
8. **Accessibility audit of `.btn-sm` contrast** in light theme.
9. **Hook the dangling `ai-status-text`**: the shell footer references `#ai-status-text` (AI Reasoning row) which `loadStatus()` never sets — either wire it up or drop the row.

---

## 13. Definition of Done (design gate)

Before a UI change is "done" in this project:

- [ ] Uses tokens only; no new hardcoded hex in HTML/JS templates.
- [ ] Leaves the single accent (emerald) intact; state colors unchanged in meaning.
- [ ] One radius family per shape type; one spacing scale.
- [ ] Label-above-input; no placeholder-as-label.
- [ ] Buttons ≥ WCAG AA contrast in **both** themes (re-verify in light).
- [ ] Loading / empty / error states present for any new data region.
- [ ] Reduced-motion fallback for any new animation.
- [ ] No em-dash; one copy register; task-first verbs.
- [ ] The shell still serves `/` and `switchView` still resolves every `data-view` to a `#view-*` panel.