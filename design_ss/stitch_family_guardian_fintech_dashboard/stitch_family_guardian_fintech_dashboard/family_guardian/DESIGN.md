---
name: Family Guardian
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#434655'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#747686'
  outline-variant: '#c4c5d7'
  surface-tint: '#2151da'
  primary: '#0037b0'
  on-primary: '#ffffff'
  primary-container: '#1d4ed8'
  on-primary-container: '#cad3ff'
  inverse-primary: '#b7c4ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#8e0026'
  on-tertiary: '#ffffff'
  tertiary-container: '#ba0035'
  on-tertiary-container: '#ffc7c9'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b7c4ff'
  on-primary-fixed: '#001551'
  on-primary-fixed-variant: '#0039b5'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#ffdada'
  tertiary-fixed-dim: '#ffb3b6'
  on-tertiary-fixed: '#40000c'
  on-tertiary-fixed-variant: '#920028'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display:
    fontFamily: Inter
    fontSize: 2.75rem
    fontWeight: '700'
    lineHeight: 3.25rem
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Inter
    fontSize: 2rem
    fontWeight: '600'
    lineHeight: 2.5rem
    letterSpacing: -0.025em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 1.625rem
    fontWeight: '600'
    lineHeight: 2.125rem
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 1.375rem
    fontWeight: '600'
    lineHeight: 1.875rem
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: '600'
    lineHeight: 1.625rem
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 1.0625rem
    fontWeight: '400'
    lineHeight: 1.625rem
  body-md:
    fontFamily: Inter
    fontSize: 0.9375rem
    fontWeight: '400'
    lineHeight: 1.5rem
  body-sm:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: '400'
    lineHeight: 1.25rem
  label-lg:
    fontFamily: Inter
    fontSize: 0.9375rem
    fontWeight: '500'
    lineHeight: 1.25rem
  label-md:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: '500'
    lineHeight: 1.125rem
  label-sm:
    fontFamily: Inter
    fontSize: 0.6875rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system projects quiet authority, institutional reliability, and calm reassurance. Built for modern family finance and digital risk management, it balances rigorous bank-grade clarity with parental approachability. The emotional target is immediate situational control without alarmism: data is presented objectively, alerts are unambiguous, and actions are direct.

The aesthetic follows an understated Modern Utilitarian style. It eliminates superficial embellishments—forbidding neon glows, decorative drop shadows, glassy textures, and gradients. Structure is established through crisp mathematical layouts, deliberate typographic scale, and purposeful functional color coding.

## Colors

The palette is anchored by crisp neutral surfaces and authoritative deep slates, reserving high-chroma tones strictly for actionable context and real-time state alerts.

### Roles & Foundations
- **Primary (`#1d4ed8`)**: Core brand trust blue. Used for primary interactive triggers, active navigation highlights, verified states, and key call-to-actions.
- **Secondary (`#0f172a`)**: Deep slate navy. The principal baseline for high-contrast headlines, critical microcopy, and prominent structural framing.
- **Tertiary / Critical (`#e11d48`)**: High-risk crimson rose. Reserved strictly for real-time security threats, unauthorized transactions, blocked access, and emergency parental interventions.
- **Neutral (`#64748b`)**: Balanced cool slate. Dictates secondary text labels, inactive icons, divider strokes, and supportive descriptive details.

### Functional States
- **Warning Amber (`#d97706`)**: Approaching spend limits, unknown device logins, and non-blocking permissions.
- **Success Emerald (`#059669`)**: Cleared security checks, completed transfers, and active protective shielding.
- **Surface Foundations**: Canvas background (`#f8fafc`), card container background (`#ffffff`), muted highlight wash (`#f1f5f9`), and hairline containment borders (`#e2e8f0`).

## Typography

Inter serves as the universal typeface across all roles to guarantee crisp, screen-optimized rendering across diverse resolutions. The system prioritizes dense tabular legibility and rapid skimming over decorative novelty.

- **Headlines**: Weighted at semi-bold (600) to bold (700) with tight tracking to anchor dashboard views, account overviews, and card titles.
- **Body**: Regular weight (400) calibrated with generous line height for zero eye strain across dense transaction ledgers, activity logs, and system explanations.
- **Labels & Micro-copy**: Medium (500) to semi-bold (600) weights, with uppercase tracking applied strictly to `label-sm` for system metrics, category tags, and alert metadata.

## Layout & Spacing

The layout is built on an exact 8-point base unit grid (with 4px half-steps for compact micro-components like status indicators and inline icons).

- **Desktop (1024px+)**: A structured 12-column fluid grid governed by a 24px (`1.5rem`) gutter and a 32px (`2rem`) outer margin. Maximum viewport containment sits at 1280px.
- **Tablet (768px - 1023px)**: An 8-column layout with 24px gutters and 24px canvas margins.
- **Mobile (below 768px)**: A 4-column layout utilizing 16px (`1rem`) gutters and 16px (`1rem`) canvas margins. Side-by-side metric tiles collapse into singular, vertically stacked records.

Information hierarchy relies on precise layout grouping: `space-xs` and `space-sm` bind related text-and-icon pairs, `space-md` organizes interior card regions, and `space-lg` to `space-xl` separates distinct contextual sections.

## Elevation & Depth

This design system rejects diffuse ambient drop shadows, blurred depth maps, and multi-tier elevation models in favor of a crisp planar framework.

- **Containment via Borders**: Surfaces are segmented strictly through 1px solid hairline borders (`#e2e8f0`). Cards sit directly on the muted background (`#f8fafc`) using a solid white canvas (`#ffffff`).
- **Surface Nesting**: Inner contextual modules (such as filter trays, secondary audit trails, and input wells) use subtle tonal shading (`#f1f5f9` or `#f8fafc`) bound by the same 1px border.
- **Popovers & Overlays**: Modals and dropdown flyouts float with a single, controlled keyline border (`#cbd5e1`) alongside a minimal, non-colored functional edge shadow: `0 4px 12px rgba(15, 23, 42, 0.08)`.

## Shapes

A disciplined "Soft" shape logic (0.25rem / 4px base radius) is maintained to avoid the juvenile connotations of hyper-rounded pill styling while remaining warmer than rigid brutalist right angles.

- **Standard Elements (4px / 0.25rem)**: Checkboxes, toggle switches, inline badges, and table rows.
- **Medium Elements (8px / 0.5rem - `rounded-lg`)**: Primary action buttons, text input fields, notification banners, and modal dialogs.
- **Large Containers (12px / 0.75rem - `rounded-xl`)**: Primary dashboard cards, financial overview tiles, and child device monitoring panels.

## Components

### Buttons
- **Primary**: Solid Trust Blue (`#1d4ed8`) fill, white text (`#ffffff`), `rounded-lg` (8px), no border. Hover transitions to `#1e40af`.
- **Secondary / Ghost**: Pure white background with a 1px solid border (`#e2e8f0`) and deep slate text (`#0f172a`). Hover shifts to `#f8fafc` with border `#cbd5e1`.
- **Critical / Destructive**: Crimson Rose fill (`#e11d48`) with white text for irrevocable safety overrides or account actions.

### Cards
Constructed using a `#ffffff` background bounded by a 1px solid `#e2e8f0` border and `rounded-xl` (12px) corners. Padding is uniform at `1.5rem` (`space-lg`). Cards do not employ elevation lift on hover unless configured as an explicit navigation target, in which case the border transitions to `#cbd5e1`.

### Status Chips & Badges
Compact, non-pill rectangles with a 4px corner radius. Styled using a 10% tinted background of the functional state paired with high-contrast text:
- **Critical Alert**: Background `#ffe4e6`, Text `#be123c`, 1px solid `#fecdd3`.
- **Warning**: Background `#fef3c7`, Text `#b45309`, 1px solid `#fde68a`.
- **Protected / Active**: Background `#d1fae5`, Text `#047857`, 1px solid `#a7f3d0`.
- **Neutral / Paused**: Background `#f1f5f9`, Text `#475569`, 1px solid `#e2e8f0`.

### Form Inputs
Height calibrated to 40px with `rounded-lg` (8px) corners, 1px border (`#cbd5e1`), and clean interior padding (`0.75rem`). Default background is `#ffffff`. Focus state swaps border to Primary Blue (`#1d4ed8`) with a matching 1px outer keyline (`#1d4ed8`), avoiding diffuse halo glows.

### Lists & Ledgers
Data records (e.g., transaction feeds, device screentime logs, URL access filters) are laid out as divided lists separated by 1px horizontal rules (`#f1f5f9`). Alternating zebra fills are prohibited; rows differentiate strictly on clean typographical hierarchy and crisp right-aligned state chips.

### Safety-Specific Patterns
- **Device Status Tile**: Displays an individual family member or device with an integrated status dot (8px solid circle), network telemetry label, and quick-toggle security lock.
- **Risk Monitor Banner**: Full-width container anchored at the top of security modules when unverified activity occurs; leverages the High Risk Crimson styling with an immediate primary button resolution path.