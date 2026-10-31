# Guardrail — Project Spec (CLAUDE.md)

## What it is

Guardrail is a family payment safety app built on PayPal rails, for the
"Build What's Next with PayPal and AI" hackathon. Every outbound payment flows
THROUGH our app, so we insert an AI safety gate before money moves. Hero demo:
a senior tries to send money to an unknown recipient; our AI ("Shield") scores it
for scam risk; high-risk payments are HELD (authorized, not captured) until a
guardian approves (capture) or cancels (void).

## Core principle (our pitch — implement for real, not as a comment)

PayPal holds the money. The AI scores the risk. Hard rules in OUR code (spending
caps, new-recipient limits, cooling-off delay, global pause switch) have the FINAL
say. The AI can only ever make a payment STRICTER, never looser — it can hold or
block, but can never approve a payment the rules forbid. A model failure also fails
stricter (hold for manual review). Put this in one well-named function:
`apply_guardrails(payment, ai_verdict, rules)`. Every AI decision and guardian action
is written to an audit log.

## Stack

- **Backend:** Python 3.11+, FastAPI + uvicorn. One `uvicorn` command runs everything.
- **Frontend:** static HTML + Tailwind (Play CDN) + Inter font, no build step, `fetch()`
  to the backend. Served by FastAPI via `StaticFiles`.
- **Store:** in-memory module (dict of payments + an audit log list). NO database.
- **Validation:** Pydantic (NOT Zod — this is Python). Pydantic models validate both
  our API I/O and the AI's JSON output.
- **Config:** read secrets from `.env` (python-dotenv). `.env` in `.gitignore`; `.env.example`
  committed with placeholders.

## AI — Shield (`services/shield.py`)

- Google Gemini API, model: `gemini-2.5-flash` (free tier; swappable later).
- SDK: the new unified `google-genai` package (`pip install google-genai`,
  `from google import genai`). Do NOT use the deprecated `google-generativeai`.
- Input to the model: recipient (new or known), amount vs. the person's normal
  pattern, time of day, and any message/note text.
- Output: STRICT structured JSON validated by a Pydantic model:
  `{ risk_level: "low"|"medium"|"high", signals: [str], reason: str }`.
  Use Gemini's structured-output config (`response_mime_type="application/json"` plus
  a response schema) so output is reliable. Validate with Pydantic; on invalid
  output, retry ONCE; if it still fails, HOLD for manual review (fail stricter).
- Shield also writes the plain-language alert wording shown to senior/child/guardian.
- Map `risk_level` -> verdict: high -> block/hold, medium -> hold, low -> allow.
  Final status is decided by `apply_guardrails`, never by Shield alone.

## PayPal — all on the free Sandbox (`services/paypal.py`)

Credentials stay server-side; the AI never sees them.

**MUST-HAVE (build these for real):**

- **OAuth 2.0 token API:** authenticate backend with sandbox client id + secret.
- **Orders API v2 (intent AUTHORIZE):** create each payment as an authorization —
  money reserved, not charged. This is the "hold" that enables the guardian step.
- **Payments API (capture authorization):** charge the money after auto-approval by
  rules or guardian approval.
- **Payments API (void authorization):** release a held payment when a guardian cancels
  or it expires — nothing is charged.

**STRETCH (only after the hero flow works end to end):**

- **Refunds API:** reverse an already-captured payment at a guardian's request.
- **Webhooks API** (authorization.created, capture.completed, payment voided) with
  signature verification, to sync dashboards.

> **NOTE:** webhooks need a public URL (tunnel) + verification. For the demo we use
> POLLING (dashboards call `GET /api/payments` on an interval). Document webhooks in
> the README as the production architecture; implement only if time allows.

## Data model (Pydantic)

- **Payment:** id, sender, recipient_name, recipient_is_new (bool), amount, currency,
  note, status (`"pending_review"|"held_for_guardian"|"approved"|"cancelled"`),
  risk `{ risk_level, signals, reason, verdict }`, paypal `{ order_id, authorization_id,
  capture_id }`, created_at.
- **GuardianRules:** max_amount, allow_new_recipients, cooling_off_minutes, paused (bool).
- **AuditEntry:** timestamp, actor (`"shield"|"rules"|"guardian"`), action, payment_id, detail.

## Backend endpoints

| Method | Path | Behaviour |
|---|---|---|
| POST | `/api/payments` | create; run `shield.score()` then `apply_guardrails()`; set status; (real PayPal: create AUTHORIZE order here) |
| GET | `/api/payments` | list (dashboards poll this) |
| GET | `/api/payments/{id}` | one payment |
| POST | `/api/payments/{id}/approve` | guardian approves -> CAPTURE authorization |
| POST | `/api/payments/{id}/cancel` | guardian cancels -> VOID authorization |
| POST | `/api/seed` | load 3 demo scenarios |
| GET | `/api/audit` | the audit log |

Stretch: `POST /api/payments/{id}/refund`; `POST /api/webhooks/paypal`.

## Seed scenarios (`/api/seed`)

- **(a)** $800 to "Mike Turner", new recipient, note mentions urgent bail money -> high
- **(b)** $5 to "School Cafe", known recipient -> low
- **(c)** $60 to "GameWorld Store", child purchase, borderline, late at night -> medium

## Frontend

- **`frontend/senior.html`:** mobile phone-frame. Send form -> `POST /api/payments`;
  on hold/block show the "Wait. This payment may be a scam." interception screen with
  Shield's reasons + actions (Call my family / Cancel / Send anyway-asks family).
- **`frontend/guardian.html`:** desktop dashboard. Polls `GET /api/payments`; shows held
  payments with amount/recipient/reasons + Approve/Cancel; "Load demo data" -> `/api/seed`;
  shows counts (checked / held / blocked). Match DESIGN.md tokens.

Stretch screens: child view, safety-rules settings, mobile guardian alerts.

## Design tokens (from DESIGN.md)

Primary `#1d4ed8`, crimson/risk `#e11d48`, warning amber `#d97706`, success `#059669`,
Inter font, 1px borders `#e2e8f0`, rounded-xl cards, no heavy shadows.

## Env (`.env.example`)

`PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`, `PAYPAL_BASE=https://api-m.sandbox.paypal.com`,
`GEMINI_API_KEY`
