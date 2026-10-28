# Tasks for the owner

Real2Simulation · Meta Global AI Developer Hackathon · owner: Koushik
Created Oct 27, 2026; revised the same day (no filming; public clips instead). Times are Asia/Dhaka. Step IDs (S01, S02…) match [final plan.html](08%20Real2Simulation/final%20plan.html).

Tick a box when it's done. Agents can't do these for you: they need your accounts, your voice, or your go-ahead.

## Your time budget

You have an Algorithm course presentation video due before Nov 3, and finals start Nov 5 (Statistics first). The plan keeps your hackathon work to **about 4 hours in total**:

| When | What | Time |
|---|---|---|
| Oct 27–28 | Section 1 (keys) and approving the clip list | about 1.5 h |
| Oct 29 – Nov 2 | Answer agent questions, batched once a day | 10–15 min a day |
| Nov 3 or 4 | Record the voice-over for the demo video (optional) | about 1 h |
| Nov 4, by 18:00 | Make the repo public, submit, post on X | about 45 min |

**Stop-work is now Nov 4, 18:00 Dhaka** (was 22:00), so you can rest before the exam. The organiser's hard deadline is still Nov 5, 8:00 AM Dhaka.

## 1. Accounts and keys (S01) — tonight or tomorrow

- [x] Submit every credit form (Meta $150, Baseten, Modal, Fireworks). *Done Oct 27.*
- [x] Muse Spark Open access: the Baseten key is in the event `.env`. *Done Oct 27.*
- [x] **Sign-in uses Clerk's built-in options only** (decided Oct 27): Google through Clerk's shared credentials, plus email one-time passcode (OTP); passwords are optional, not required. No custom Google OAuth client is used; the Google Cloud test client was deleted and its project is pending deletion. *Untested end to end: Google sign-in and email OTP. Production Google is deferred to S22, only if time allows.*
- [x] Meta Billing credit and $150 Spend Limit notification: Koushik reports all Meta Model API tasks complete on Oct 27. Billing details have not been independently verified. The notification is an alert, not a billing cap; enforce the $120 routine stop and $30 demo reserve separately.
- [x] Create a **Meta Model API key** and add it to the event `.env`. *Done Oct 27; test call to muse-spark-1.3 returned HTTP 200.*
- [x] Add the Modal and Fireworks credentials to local `.env`. All three fields are populated; Modal token authentication and Fireworks authenticated model listing passed on Oct 27. GPU execution and inference remain untested. Never send keys in chat. Clerk and Railway will be used through their CLIs, and Railway through its plugin; supply application credentials securely when required.
- [x] Railway **dev** deploys approved in chat on Oct 27; recorded in [DECISIONS_LOG.md](DECISIONS_LOG.md). Judging deployment still needs separate approval.

## 2. Approve the public clip list (S02) — about 10 minutes, Oct 28

You don't film anything. An agent collects about 10 clips from sources that allow reuse and editing, and writes `clips.csv` with each clip's source link, licence, credit line, frame rate and the known-size object used for scale.

- [ ] Read `clips.csv` and approve it (or strike any clip you don't like). Tell me in chat: "Clip list approved."

What the agent may use:

- **NASA** footage (public domain). The Apollo 15 hammer-and-feather drop on Wikimedia Commons is confirmed public domain: it lets the app measure the Moon's g.
- **Wikimedia Commons** clips under public domain, CC0, CC BY or CC BY-SA, credited.
- **Pexels** and **Pixabay** clips, whose licences allow free use and editing.

What it may not use: YouTube downloads, any clip marked "non-commercial" (NC) or "no derivatives" (ND), or anything without a clear licence. The event rules forbid footage without rights, so "almost any sample" isn't safe: a judge or organiser can disqualify an entry for it.

How the demo still shows "prediction vs reality" without your own throws: the app watches only the **first part** of a clip (the first half of a flight, the first bounce, the first few swings), predicts the rest, then overlays its prediction on the real frames it never saw.

## 3. AWS (only after the quota is approved)

Right now AWS can't start a GPU machine (quota is 0), so there's nothing to do except wait.

- [ ] When AWS approves the two us-east-2 quota requests, tell me.
- [ ] **Then**, before the first GPU session, create the **$50 GPU budget** (Billing → Budgets → Create budget → Cost budget, $50/month, filter Service = EC2, email alerts at 50%, 80% and 100%). It only sends warning emails; it never stops a machine. Your two existing $25 budgets are already past their thresholds, so they'll keep emailing; that's harmless.
- [ ] After every GPU session, check that the instance is **stopped**.

## 4. Approvals only you can give (during the build)

- [ ] Deploys to the Railway **judging** environment (S23, Nov 3).
- [ ] Making the repository **public** (S25, Nov 4). The rules require it, but only after the secret scan is clean.
- [ ] Any purchase, plan upgrade, or acceptance of legal terms.

## 5. Later in the build (all optional except the last three)

- [ ] *Optional:* **Agents 102: Best Practices for Verifiable Agents** — Oct 28, 10:00 PM. Skip it if you're busy; the agents will read the recording notes if any are posted.
- [ ] *Optional:* **Fireworks session on Muse open models** — Oct 30, 10:00 PM.
- [ ] *Optional:* ask in Discord #office-hours (weekdays 8–9 PM until Oct 30, 9–10 PM from Nov 2): "Is a physics measurement app that also writes lab reports clear of the 'simple AI for Education chatbot' anti-project?"
- [x] Accept Discord rules plus the saved **Hackathon Credit Terms.pdf** as sufficient for L05. *Koushik reconfirmed Oct 27. The full waiver remains unread; this is an owner decision, not proof of full legal-text review. If the waiver becomes available, read it and flag conflicts.*
- [ ] **Demo video voice-over (S24, Nov 3 or 4, about 1 hour):** the agent records the screen and writes the script and captions; you read the script into a microphone. If you have no time, the video ships with captions only.
- [ ] **Submit (S26) by Nov 4, 6:00 PM Dhaka** (hard deadline Nov 5, 8:00 AM): repo link, video link, live link, a judge note with guest access and a demo account. Check that you're listed on the submission page.
- [ ] **Post the demo on X** and **submit the post link** through the hackathon platform (Most Viral prize, engagement counted until Nov 8).
