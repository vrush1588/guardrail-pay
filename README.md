# Guardrail

**Family payment safety on PayPal rails.** Before money leaves a grandparent's or a
child's account, an AI checks it for scams. If a payment looks risky, PayPal *holds*
the funds and a family guardian decides whether it goes through.

Built for the *Build What's Next with PayPal and AI* hackathon.

## The problem

Scams aimed at older adults ("your grandson is in jail, send bail money now, don't tell
his parents") and impulse purchases by children both work the same way: the money is
gone before anyone else in the family knows. Banks and apps only warn the person being
pressured, who is the one least able to stop and think.

## What Guardrail does

1. **A senior or child sends a payment** from a simple phone screen.
2. **PayPal authorizes the payment instead of capturing it.** The funds are reserved,
   but nothing is sent yet.
3. **Shield, our AI, scores the payment for scam risk.** It looks at the recipient, the
   amount compared with what this person usually sends, the time of day, and the note.
4. **The family's own rules have the final say:** a spending cap, approval for new
   recipients, a cooling-off period for new payees, and a pause-everything switch.
5. **Safe payments are captured right away.** Risky ones show the sender a calm
   "Wait. This payment may be a scam" screen with the reasons, and go to the guardian.
6. **On the dashboard, the guardian approves (PayPal capture) or cancels (PayPal void).**
   A cancelled payment never leaves the account. The senior's screen updates live.

Every AI verdict, rule decision, PayPal step and guardian action is written to an
audit log.

### The core safety rule: the AI can only make things stricter

The AI is never allowed to approve a payment on its own.
[`apply_guardrails()`](app/guardrails.py) combines Shield's verdict with the family
rules and keeps whichever is **stricter**:

- Shield can hold or block a payment, but it can't overrule a family rule that holds it.
- If Shield fails (an API error, invalid output, or overload), the payment is **held**,
  never allowed.
- A risk level we don't recognise counts as a block.
- A runtime check raises an error if the final verdict is ever looser than either input.

## How PayPal is used

All PayPal calls are in [`app/services/paypal.py`](app/services/paypal.py) and run
against the free **PayPal Sandbox**. Credentials stay on the server; the AI never sees
them or any PayPal ids.

| PayPal API | What Guardrail uses it for |
|---|---|
| **OAuth 2.0** (`/v1/oauth2/token`) | Server-side login with the app's client id and secret; the token is cached |
| **Orders v2, `intent: AUTHORIZE`** (`/v2/checkout/orders`) | Creates every payment as an authorization, so the money is reserved but not sent |
| **PayPal checkout approval** (the `payer-action` link) | The sender logs in to PayPal and approves the payment, then returns to Guardrail |
| **Authorize order** (`/v2/checkout/orders/{id}/authorize`) | Puts the hold on the funds. This hold is what makes the guardian step possible |
| **Capture authorization** (`/v2/payments/authorizations/{id}/capture`) | Sends the money: safe payments right away, risky ones once a guardian approves |
| **Void authorization** (`/v2/payments/authorizations/{id}/void`) | Releases the hold when a guardian cancels, so nothing is charged |

Every call sends a `PayPal-Request-Id`, so retries are idempotent. PayPal errors,
including their `debug_id`, are logged in the audit log, and the user sees a clear
message instead of a crash. If an automatic capture fails, the funds stay held and the
payment goes to the guardian.

## How AI is used (Tools)

| Tool | How we use it |
|---|---|
| **Google Gemini 2.5 Flash** via the `google-genai` SDK | **Shield**, the scam-risk scorer in [`app/services/shield.py`](app/services/shield.py) |

- **Structured output:** Gemini must return JSON that matches a Pydantic schema
  (`risk_level`, `signals`, `reason`), using `response_mime_type="application/json"`
  with `response_schema` and `temperature=0`. Invalid output is retried once, then the
  payment is held.
- **Plain-language explanations:** the `signals` it writes are shown directly to the
  senior and the guardian, for example "You have never paid Mike before." They are
  short, calm sentences a grandparent can understand.
- **Prompt-injection defence:** the payment note may have been written by the scammer,
  so the system prompt tells Shield to treat it only as evidence and never follow
  instructions inside it. Shield also can't approve anything on its own (see above).
- **Minimal data:** Shield sees only the payment facts: sender, recipient, amount,
  usual amount, hour and note.
- **Reliable demo:** Gemini's answers are saved in `data/shield_cache.json` and replayed
  for the same payment, so the demo works during Gemini rate limits or outages. Without
  a `GEMINI_API_KEY`, Shield uses built-in offline heuristics, so the app runs with no
  keys at all.

**Other tools:** FastAPI, Pydantic, httpx, Tailwind CSS. The UI was designed with Google
Stitch.

## Run it

You need Python 3.11 or newer. The app runs with no keys at all (offline Shield,
mock PayPal), so you can try it before setting anything up.

```bash
git clone https://github.com/vrush1588/guardrail-pay.git
cd guardrail-pay
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app
```

Open these side by side:

- **Senior phone screen:** http://127.0.0.1:8000/senior.html
- **Guardian dashboard:** http://127.0.0.1:8000/guardian.html
- API docs: http://127.0.0.1:8000/docs

On startup the server prints which modes are on, for example
`PayPal: sandbox https://api-m.sandbox.paypal.com, Shield: Gemini gemini-2.5-flash`.

### Turn on Gemini

Get a free key at https://aistudio.google.com/apikey and set `GEMINI_API_KEY` in `.env`.

### Turn on the PayPal Sandbox

1. Log in at https://developer.paypal.com. Under **Apps & Credentials**, choose
   **Sandbox** and create an app.
2. Copy the app's **Client ID** and **Secret** into `.env`, and set `PAYPAL_MODE=sandbox`.
3. Under **Testing Tools → Sandbox Accounts**, note the email and password of the
   *Personal* test account. That is the "senior" who logs in on PayPal to approve.
4. Restart the server. If a key is missing, startup fails with a message saying which.

Each payment from the senior screen now opens PayPal, where the senior logs in with the
sandbox Personal account and approves. Back in Guardrail, the funds are authorized, Shield
scores the payment, and the guardian's Approve and Cancel run real captures and voids.
You can check them under the sandbox account's activity. **Load demo data** always uses
mock PayPal ids, because no one is there to approve those payments on PayPal.

If PayPal rejects an order because of the account's country or currency, add a US
sandbox *Business* account and make it the app's account.

## Demo walkthrough (about 3 minutes)

1. **Guardian → Load demo data.** Three payments come in:
   - $800 to "Mike Turner", a new recipient: *"URGENT - your grandson needs bail money
     tonight, don't tell his parents"* → Shield: **high** → **blocked**, waiting for the guardian
   - $5 to School Cafe, a known payee → **low** → **sent** right away
   - $60 to GameWorld Store from Leo (age 12) at 11:40 pm, 6 times his usual amount and
     over the $50 family cap → **medium** → **held**
2. **Senior → click "School Cafe $5" → Send.** The payment goes through: "Payment sent".
3. **Senior → click "Mike Turner $800" → Send.** The senior sees *"Wait. This payment may be a
   scam"* with Shield's reasons, and can Call my family, Cancel, or Send anyway (which
   asks the family).
4. **Guardian:** the payment appears under *Needs your decision* with Shield's reasons
   and the family rules it hit → **Cancel**. The funds are voided, nothing is sent, and
   the senior's screen updates within 2 seconds.
5. Open http://127.0.0.1:8000/api/audit to see every decision Shield, the rules and the
   guardian made.

## How it fits together

```
Senior screen ── POST /api/payments
                   │
                   ├─ PayPal: create order (intent AUTHORIZE)
                   │    └─ sandbox: senior approves on PayPal → /api/paypal/return
                   ├─ PayPal: authorize            funds held, nothing sent
                   ├─ Shield (Gemini): score       low / medium / high + reasons
                   ├─ apply_guardrails             family rules; can only get stricter
                   │
                   ├─ allow ─────────► PayPal capture  → "approved"
                   └─ hold / block ──► guardian dashboard
                                         ├─ Approve → PayPal capture
                                         └─ Cancel  → PayPal void
Every step is written to the audit log.
```

| File | What it does |
|---|---|
| [`app/main.py`](app/main.py) | FastAPI app: endpoints, the payment pipeline, PayPal return/cancel, serves `frontend/` |
| [`app/guardrails.py`](app/guardrails.py) | `apply_guardrails()`, the stricter-only rule |
| [`app/services/shield.py`](app/services/shield.py) | Shield: Gemini call, schema validation, retry, cache, offline fallback |
| [`app/services/paypal.py`](app/services/paypal.py) | PayPal: OAuth, Orders v2 (authorize), capture, void; mock mode |
| [`app/store.py`](app/store.py) | In-memory store: payments, audit log, family rules, known payees |
| [`app/models.py`](app/models.py) | Pydantic models for payments, risk, Shield output, rules, audit entries |
| [`frontend/`](frontend/) | `senior.html` (phone), `guardian.html` (dashboard): static HTML + Tailwind, no build step |

### API

| Method | Path | |
|---|---|---|
| POST | `/api/payments` | Create a payment (PayPal order, then hold, score and route it) |
| GET | `/api/payments` | List payments, newest first (the dashboards poll this) |
| GET | `/api/payments/{id}` | One payment |
| POST | `/api/payments/{id}/approve` | Guardian approves → PayPal capture |
| POST | `/api/payments/{id}/cancel` | Guardian cancels → PayPal void |
| GET | `/api/paypal/return`, `/api/paypal/cancel` | Where PayPal sends the payer after approving or cancelling |
| GET | `/api/rules` | The family rules |
| GET | `/api/audit` | Audit log |
| POST | `/api/seed` | Reset and load the three demo payments |

### Configuration (`.env`)

| Variable | Default | |
|---|---|---|
| `PAYPAL_MODE` | `mock` | `sandbox` makes real PayPal Sandbox calls |
| `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET` | | Sandbox app credentials (needed when `PAYPAL_MODE=sandbox`) |
| `PAYPAL_BASE` | `https://api-m.sandbox.paypal.com` | PayPal API base URL |
| `GEMINI_API_KEY` | | Turns on Gemini; without it Shield uses offline heuristics |
| `GEMINI_MODEL` | `gemini-2.5-flash` | |
| `SHIELD_CACHE` | on | `0` always calls Gemini instead of replaying saved answers |
| `GUARDRAIL_BASE_URL` | `http://127.0.0.1:8000` | Public URL of the app, used for PayPal's return links |

## Limitations and next steps

This is a hackathon prototype:

- Data is kept in memory (one family, resets on restart), and the dashboards poll instead
  of using webhooks.
- There are no user accounts. The senior and guardian screens are open pages.

Next steps: PayPal **webhooks** with signature verification instead of polling,
**refunds** for payments a guardian later finds were scams, automatically voiding holds
the guardian hasn't answered, a settings screen for the family rules, and SMS or push
alerts to guardians.

## License

[MIT](LICENSE)
