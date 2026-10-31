# guardrail

Family payment safety for the PayPal + AI hackathon. A senior sends money, the payment is
held, Shield scores it for scam risk, and risky payments wait for a guardian to approve
(capture) or cancel (void).

Shield runs on **Gemini** (`gemini-2.5-flash`) when `GEMINI_API_KEY` is set in `.env`,
and falls back to offline mock heuristics without it. PayPal is still a **mock**.

## Run it

Needs Python 3.11+.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # optional for now: nothing reads the keys yet

uvicorn app.main:app --reload
```

Then open:

- Senior: http://127.0.0.1:8000/senior.html
- Guardian: http://127.0.0.1:8000/guardian.html

API docs: http://127.0.0.1:8000/docs

## Demo flow

1. Guardian screen → **Load demo data**. You get three payments:
   - $800 to Mike Turner (new, "urgent bail money") → Shield **high** → **block**, held for guardian
   - $5 to School Cafe (known) → Shield **low** → **allow**, sent straight away
   - $60 to GameWorld Store (child, 11:40 pm, 6× usual, over the $50 family limit) →
     Shield **medium** → **hold**
2. Senior screen → send $800 to Mike Turner → the scam alert appears.
3. Guardian screen → the payment shows up under "Needs your decision" → **Approve** or
   **Cancel**. The senior screen updates within a couple of seconds.

## How it fits together

```
POST /api/payments
  -> paypal.create_order + authorize_order   (funds held, nothing sent)
  -> shield.score(payment)                   (AI risk: low / medium / high; retry once, then fail -> hold)
  -> apply_guardrails(payment, ai_verdict, rules)
                                             (caps, new payees, cooling-off, pause: can only make it stricter)
  -> every Shield decision, rules verdict and guardian action -> audit log
  -> allow: capture -> "approved"
     hold/block: "held_for_guardian" -> guardian approves (capture) or cancels (void)
```

| File | What it is |
|---|---|
| `app/main.py` | FastAPI app, endpoints, the pipeline, serves `frontend/` |
| `app/guardrails.py` | **The stricter-only rule** (`apply_guardrails`) |
| `app/services/shield.py` | Shield: Pydantic-validated JSON, one retry, `ShieldError` on failure. Only `_call_model()` is mock. `# TODO: replace with real Gemini call` |
| `app/services/paypal.py` | PayPal seam: stubs returning fake ids. `# TODO: replace with real PayPal sandbox calls` |
| `app/store.py` | In-memory store (resets on restart): payments, audit log, guardian rules, known payees |
| `app/models.py` | Pydantic models: `Payment`, `Risk`, `ShieldResult`, `GuardianRules`, `AuditEntry` |

### Endpoints

| Method | Path | |
|---|---|---|
| POST | `/api/payments` | Create, score and route a payment |
| GET | `/api/payments` | List all payments (newest first) |
| GET | `/api/payments/{id}` | One payment |
| POST | `/api/payments/{id}/approve` | Guardian approves → capture |
| POST | `/api/payments/{id}/cancel` | Guardian cancels → void |
| GET | `/api/rules` | Current guardian rules |
| GET | `/api/audit` | Audit log (Shield, rules, guardian) |
| POST | `/api/seed` | Reset and load the three demo scenarios |
