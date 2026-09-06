---
name: frontend-design
description: Use when writing any HTML page, CSS, layout or color, before the first line of markup, so the result does not read as a generated template.
---

# Frontend design

Your untrained default is a centered card on a dark purple gradient, a
glassmorphic blur, a generic sans-serif and seven font sizes. Do not produce it.
The three steps below are ordered: pick a direction, write its tokens, then
style. Styling before the token block is how the generic look gets back in.

## 1. Pick exactly one direction

| Direction | `--paper` | `--ink` | `--accent` | `--font` | `--radius` | `color-scheme` |
|---|---|---|---|---|---|---|
| Editorial | `#fffdf8` | `#14110d` | `#8a2f22` | `ui-serif, Georgia, "Times New Roman", serif` | `0` | `light` |
| Brutalist | `#ffffff` | `#000000` | `#0000ee` | `ui-sans-serif, system-ui, sans-serif` | `0` | `light` |
| Terminal | `#0d0f0c` | `#d6d3c4` | `#ffb000` | `ui-monospace, Menlo, Consolas, monospace` | `0` | `dark` |
| Warm minimal | `#faf8f5` | `#1a1a1a` | `#b8743a` | `ui-sans-serif, system-ui, sans-serif` | `4px` | `light` |

Take the whole row or none of it. Borrowing one direction's serif into another
direction's palette is what produces the generic look -- it is the most common
way this goes wrong. System stacks only: no webfont, no CDN.

Editorial is large headings and whitespace, a magazine not a dashboard.
Brutalist is flat blocks and `2px solid` borders, no shadows. Terminal is boxy
and monospace throughout. Warm minimal is paper, thin rules, nothing else.

## 2. Write this block before any other CSS

```css
:root {
  color-scheme: light;                 /* the value from your row */
  --paper: #faf8f5;
  --ink: #1a1a1a;
  --ink-soft: color-mix(in srgb, var(--ink) 60%, var(--paper));
  --rule: color-mix(in srgb, var(--ink) 15%, var(--paper));
  --accent: #b8743a;
  --font: ui-sans-serif, system-ui, sans-serif;
  --text: 1rem;                        /* body */
  --display: 2.5rem;                   /* the one big heading */
  --small: 0.875rem;                   /* labels, meta */
  --radius: 4px;
  --gap: 8px;
  --speed: 120ms;
}
```

**Below `:root`, write no literal color, `font-family`, `font-size` or
`border-radius`. Only `var(...)`.** Three sizes exist because three tokens
exist. The two neutrals derive from the colors you already picked, so the
palette cannot drift.

`color-scheme` must match the palette you shipped. `light dark` without a real
`prefers-color-scheme` block renders dark form controls on your light page.

Spacing is `var(--gap)` or a `calc()` multiple of it. `4px` is allowed only
between two elements that read as one unit. Space inside an element must be
smaller than the space around it, or the grouping reads wrong.

## 3. Always include

```css
*:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

- The accent has exactly one job: the primary action, plus the focus ring above.
  Neutrals carry everything else. No gradient unless it is the point of the page.
- Every clickable element styles `:hover`, `:focus-visible` and `:active`
  distinctly. Disabled gets `cursor: not-allowed` and reduced opacity.
- Transition `transform`, `opacity`, `color`, `background-color` or
  `border-color`, always at `var(--speed)`. Never `width`, `height`, `top`,
  `left` or `margin`: those relayout on every frame.
- Every input gets a real `<label>`; a placeholder is not a label. Line height
  `1.5` for body, `1.1` for `--display`. Never center long body text.

## 4. Audit before you answer

Read back the file you wrote and count. Fix anything that fails, then report the
counts in your summary with the direction and accent you chose:

| Check | Pass |
|---|---|
| distinct `font-size` values | at most 3, every one a `var()` |
| distinct `font-family` values | 1 |
| distinct `border-radius` values | 1 |
| hex colors below `:root` | 0 |
| spacing values not a multiple of `--gap` | 0, except deliberate `4px` pairs |
| `color-scheme` vs. shipped palette | match |

If you cannot name your direction and your accent, you defaulted.
