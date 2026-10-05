# PayPilot

**An AI payment agent for freelance milestones.**

Freelancers worry about not getting paid. Clients worry about paying for work that doesn't meet the agreement. PayPilot helps both sides:

1. The freelancer and client agree on milestones, prices, and acceptance criteria.
2. The freelancer submits evidence (repo link, screenshots, demo).
3. An AI model checks the evidence against each criterion and returns pass, fail, or unclear, with reasons.
4. The client reviews the AI report and approves or disputes. The AI only recommends, and a human decides.
5. On approval, PayPal creates and sends the milestone invoice. A webhook confirms payment and updates both dashboards.

## How PayPal is used
- Invoicing API v2: create, send, and track milestone invoices
- Webhooks: confirm payments in real time
- OAuth 2.0: authenticate API calls (sandbox)

## How AI is used
- Evidence review against acceptance criteria, with structured JSON output
- Acceptance-criteria drafting from a plain-language description

## Safety guardrails
- No payment without explicit client approval
- The AI never sees PayPal credentials
- Full audit log of every AI and payment action
- Kill switch to pause the agent

## Built during the PayPal AI Hackathon
Started on Oct 5, 2026. See the commit history.

## Tech stack
TypeScript, Next.js, PostgreSQL, Prisma, Tailwind CSS, Render# paypilot-ai
AI payment agent for freelancers and clients. Claude/Gemini reviews milestone evidence against agreed acceptance criteria, the client approves, and PayPal Invoicing + Webhooks handle payment. Human approval, audit log, and kill switch built in. Built for the PayPal AI Hackathon.
