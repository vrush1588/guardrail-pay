# Guardrail — Demo Script

About 4 minutes. Each scene has what to **do** on screen and what to **say**.

## Before you start

Set up 10 minutes early. Rehearse at the same time of day you'll present: the saved Gemini
answers are kept separately for daytime and for 11 pm–5 am.

- [ ] Free port 8000: in PowerShell, `Get-NetTCPConnection -LocalPort 8000` should show nothing.
      If it shows a process, stop it.
- [ ] Start the server without `--reload`: `uvicorn app.main:app`
- [ ] Check the startup line says `Shield: Gemini gemini-2.5-flash` and `Alerts: Zapier`, and
      note the PayPal mode (`mock` or `sandbox`).
- [ ] Open the guardian dashboard (`/guardian.html`) on the left half of the screen and the
      senior phone screen (`/senior.html`) on the right.
- [ ] Open your email inbox in a third tab, ready to switch to.
- [ ] Check the Zap is published and on in Zapier.
- [ ] Do one dry run, then click **Demo data** to reset. It clears everything and sends no emails.
- [ ] Zoom the browser to about 125% so the judges can read the screens.
- [ ] For a phone recording: from the Render (https) link, install **Family Pay** (`/senior.html`) and
      **Guardian** (`/guardian.html`) via Chrome **⋮ → Install app**, so both icons are on the home screen.
- [ ] Turn the laptop volume up and play the `/phone.html` call once, so the browser loads its voice.
      Press **R** to reset it. If audio fails on the day, tap 🔊 during the call for captions only.

## Opening (0:00–0:30)

Show the guardian dashboard, empty. Speak to camera.

> "Grandma Rose gets a call: *your grandson is in jail, send $800 bail tonight, and don't tell
> his parents.* By the time anyone in the family hears about it, the money is gone. Kids buying
> game items at midnight is the same problem on a smaller scale.
>
> Banks warn the person being pressured, and they're the one least able to stop and think.
> **Guardrail brings the family in before the money moves.** PayPal holds the payment, an AI
> checks it for scams, and a guardian decides."

## Scene 1: the guardian's dashboard (0:30–1:00)

| Do | Say |
| --- | --- |
| Click **Demo data** (top right). Wait for the three payments to appear. | "This is the guardian's view. Every payment from the family goes through here. Here's a typical day." |
| Point at the $5 School Cafe row in *All payments*, status **Sent**. | "Leo's $5 lunch: a known payee, a normal amount. Shield says low risk, so it went straight through." |
| Point at the GameWorld Store card under *Needs your decision*. | "Leo again, $60 on a game at 11:40 pm. That's 6 times his usual spend and over the family's $50 limit, so it's held." |
| Point at the Mike Turner card: **HIGH RISK** badge, the red *Shield AI* box and the grey *Family rule triggered* box. | "And the $800 bail-money message to Grandma, blocked. Shield, our AI, read the note and spotted the classic grandparent scam." |
| Point at *Shield telemetry* and *Family rules* (right column on a laptop). | "These are the family's own rules. They can only make Shield stricter, never looser." |

## Scene 2: a safe payment goes straight through (1:00–1:20)

| Do | Say |
| --- | --- |
| Switch to the senior phone screen. Click the **School Cafe $5** quick-fill under the form, then **Send**. | "Now I'm Grandma Rose. A normal payment: $5 to the school cafe." |
| "Payment sent" appears. | "No friction. Guardrail stays out of the way when things are normal, which is most of the time." |

## Scene 3: the scam is caught (1:20–2:30)

This is the key moment, so slow down here.

| Do | Say |
| --- | --- |
| Switch the senior tab to `/phone.html`. Tap the **Sunday Garden Show** card (or press **C**). The phone rings. | "Grandma Rose is watching her garden show when an unknown number calls." |
| Tap **Accept**. Let the call play: the voice speaks and captions appear. | Stay quiet and let the judges hear it: *"Grandma, it's me… I need $800 for bail tonight… send it to my lawyer, Kevin Brooks… don't tell Mom and Dad."* |
| When the call ends, tap the glowing **Family Guardian** icon. The form is already filled in with Kevin Brooks, $800 and the note. Tap **Send**. | "She does exactly what he asked. She opens her payment app and sends $800." |
| The "Wait. This payment may be a scam" screen appears. Point at the reasons. | "Guardrail stops her, calmly, in words she understands: the amount is far above usual, the note is urgent, and bail money is a common scam. Nothing has been sent; PayPal is only holding the money." |
| Point at **Call my family**, **Cancel** and **Send anyway**. Don't click them (Call my family opens a calling screen; End closes it). | "She stays in control. Even *Send anyway* doesn't send: it asks the family first." |
| Switch to the email tab. The Zapier alert arrives with the subject *"Grandma Rose is trying to send $800.00 USD to Kevin Brooks. Shield says high risk."* | "At the same moment, her guardian gets this email through Zapier, with the reasons and a link to the dashboard." |
| Switch to the guardian dashboard. The new Kevin Brooks card is at the top of *Needs your decision*. Click **Call Grandma first: what to ask** | "Before deciding, the guardian should call Grandma. Shield writes what to ask." |
| Read one or two questions from the script panel. | "*Did you talk to your grandson yourself today, using the phone number you always use for him?* It never tells her to call Mike back, because Mike may be the scammer." |

If the email hasn't arrived after 15 seconds, carry on and come back to the inbox at the end of Scene 4.

## Scene 4: the guardian decides (2:30–3:10)

| Do | Say |
| --- | --- |
| On the Kevin Brooks card, click **Cancel payment**. Keep the senior screen in view. | "Grandma says she never spoke to her grandson. So I cancel." |
| Within 2 seconds the senior screen changes to "Payment cancelled". | "PayPal voids the hold. The $800 never left her account, and her screen updates straight away." |
| In *All payments*, click **Refund** on the School Cafe row and confirm. The status changes to **Refunded**. | "And if something gets through and turns out to be wrong later, the guardian can refund it, again through PayPal." |
| Mention the time limit; don't wait for it. | "If no one answers within 24 hours, the hold is voided automatically. Silence means no." |
| Optional: open `/api/audit`. | "Every AI verdict, rule decision and guardian action is logged." |

## Under the hood (3:10–3:40)

Show the README's "How it fits together" diagram, or stay on the dashboard.

> "Under the hood, every payment is a PayPal order with **intent AUTHORIZE**. The money is
> reserved, not sent. Safe payments are **captured** right away. Risky ones wait for the
> guardian: Approve **captures**, Cancel **voids**, and Refund uses the **refunds** API.
>
> Shield runs on **Gemini 2.5 Flash** with schema-checked JSON output. It treats the payment
> note as evidence only, so a scammer can't talk it into approving. And the key design rule:
> **the AI can only make a payment stricter.** If Gemini fails or is overloaded, the payment is
> held, never allowed.
>
> **Zapier** delivers the guardian's alert."

Say one of these about PayPal, depending on the startup line:

- **Sandbox mode:** "All of this runs against the real PayPal Sandbox. In sandbox mode, Grandma
  approves each payment on PayPal's own page before it's held."
- **Mock mode:** "For this recording PayPal runs in mock mode. The real Sandbox integration is in
  the repo behind one setting, `PAYPAL_MODE=sandbox`."

## Closing (3:40–4:00)

> "Guardrail: **PayPal holds the money, AI spots the scam, and the family has the final say.**
> Next we'd add PayPal webhooks, a settings screen for the family rules, and approving straight
> from the alert. Thank you."

## If something goes wrong

| Problem | What to do |
| --- | --- |
| Gemini is down or rate-limited | Use only the **School Cafe $5** and **Mike Turner $800** quick-fills, and click **Demo data** first. Those all replay saved answers. A typed-in payment calls Gemini live and may be held as "Shield could not check this payment". If that happens, say "that's the fail-safe: if the AI can't check it, it's held." |
| The Zapier email is slow | Carry on and show the inbox at the end. Keep a screenshot of an earlier alert email as a backup. |
| Port 8000 is already in use | `Get-NetTCPConnection -LocalPort 8000`, then `Stop-Process -Id <id>`, and start the server again. |
| Presenting between 11 pm and 5 am | The saved answers are for daytime, so Shield calls Gemini live. Rehearse at the real time, or run that rehearsal once with Gemini up so the late-night answers get saved. |
| Two scam cards are showing | Expected: Mike Turner is from the demo data, Kevin Brooks is the one Grandma just sent. |
| The screen looks wrong after a dry run | Click **Demo data** to reset everything. |

## Likely judge questions

| Question | Short answer |
| --- | --- |
| Why authorize instead of just paying? | The authorization is the hold. The money is reserved but not sent, which gives the guardian time to decide. Capture sends it, void releases it. |
| What if the AI is wrong? | It can only make things stricter. A false alarm costs one tap from the guardian; it can never approve something the family rules hold. If the AI fails, the payment is held. |
| Can a scammer trick the AI through the payment note? | The prompt tells Shield to treat the note only as evidence and never follow instructions in it. Even if it were fooled, it can't approve a payment the rules hold. |
| What if the guardian never answers? | After 24 hours the hold is voided automatically and nothing is sent. |
| Doesn't this take control away from the senior? | Normal payments go straight through. For a risky one she sees the reasons and can still choose Send anyway, which asks the family. |
| What does the AI see? | Only the payment facts: sender, recipient, amount, usual amount, time and note. No PayPal ids or credentials. |
| How does it stay fast and cheap? | Gemini 2.5 Flash, and answers are saved and replayed for repeat payments. |
| What would you build next? | PayPal webhooks instead of polling, a rules settings screen, and approve or cancel straight from the alert. |
