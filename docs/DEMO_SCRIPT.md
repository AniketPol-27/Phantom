# Phantom Demo Video Script

## Format

- **Total length:** 3 minutes maximum (hard cap — judges stop watching past 3:00)
- **Format:** Screen recording with voiceover narration
- **Resolution:** 1920×1080 minimum, 60fps preferred
- **Background:** Clean desktop, no notifications, no other tabs
- **Tools:** Loom, OBS Studio, or QuickTime Screen Recording
- **Audio:** Use a USB or headset mic, not the built-in laptop mic
- **Pace:** Speak ~150 words/min — slower than feels natural

---

## Pre-Recording Checklist

Run through this list before hitting record. Skipping any item risks an unusable take.

1. ✅ Phantom MCP server running locally (`uv run python -m src.server`)
2. ✅ ngrok tunnel active and the public HTTPS URL noted down
3. ✅ Po workspace open and authenticated
4. ✅ Phantom MCP server registered in Po MCP Servers config
5. ✅ Pre-Visit Intelligence Agent loaded and ready
6. ✅ Test patient (Maria Santos) loaded into the FHIR server
7. ✅ Browser zoom set to **125%** (so text is readable on small screens)
8. ✅ macOS notifications turned **off** (Do Not Disturb on)
9. ✅ Slack, email, and other distracting apps quit
10. ✅ Architecture diagram image ready in a separate tab/window for Scene 3
11. ✅ Stopwatch or timer visible to keep scenes on time
12. ✅ Script printed or open on a second screen for easy reference

---

## Scene-by-Scene Breakdown

### Scene 1: Hook (0:00 – 0:15)

**Visual:** Open on a clinician's desktop view — Po workspace open, EHR-style interface in the background. A single large text overlay appears: *"What if a clinician could simulate a decision before making it?"*

**Voiceover:**
> "Every day, clinicians make decisions about medications, doses, and diagnoses — with no way to simulate what happens next. Until now."

**Why this scene matters:** Hooks the judge with the core problem in 5 seconds. The "until now" creates anticipation for the reveal.

---

### Scene 2: The Problem (0:15 – 0:35)

**Visual:** Show a real-looking patient chart with 24 months of labs — eGFR declining from 62 to 49, HbA1c climbing from 7.2 to 8.2, weight gaining from 88 to 91 kg. Highlight these trends with subtle red arrows. Then show a clinician's calendar: 8 patients, 90 seconds per chart.

**Voiceover:**
> "This patient has diabetes, kidney disease, and rising weight — three connected systems trending in the wrong direction. Her primary care doctor has 90 seconds to review her chart before she walks in. Even an experienced clinician can't simulate what adding empagliflozin will do to her eGFR trajectory while balancing her potassium risk on lisinopril and spironolactone — not in 90 seconds."

**Why this scene matters:** Grounds the abstract problem in a concrete, sympathetic case. Judges feel the time pressure.

---

### Scene 3: The Solution (0:35 – 0:55)

**Visual:** Cut to the Phantom architecture diagram — Clinician → Po Workspace → Pre-Visit Agent → Phantom MCP Server → FHIR Server. Animate the arrows in sequence as the voiceover describes each layer. Show the SHARP context badge and FHIR R4 badge prominently.

**Voiceover:**
> "Phantom is a clinical simulation MCP server. It transforms FHIR patient data into a computational digital twin, then exposes three tools — build patient model, simulate scenario, compare interventions — that any AI agent on Prompt Opinion can equip. We've built a Pre-Visit Intelligence Agent on top to demonstrate the workflow."

**Why this scene matters:** Names the product, shows the standards-compliant architecture, and frames Phantom as a horizontal capability that benefits the whole ecosystem — not just one agent.

---

### Scene 4: Live Demo Setup (0:55 – 1:15)

**Visual:** Switch to the Po workspace. Show the **Configuration → MCP Servers** page with Phantom registered, the **"Prompt Opinion FHIR Context"** extension toggle set to ON, and the FHIR scopes listed. Briefly cursor over each badge.

**Voiceover:**
> "Here's Phantom registered as an MCP server in Prompt Opinion, with the SHARP-on-MCP FHIR Context extension enabled. That means patient context flows automatically from the EHR session through the agent — no manual patient ID passing, no broken integrations."

**Why this scene matters:** Proves you've actually integrated with Po properly and shows you understand SHARP. Judges who built the platform will recognize their own UI.

---

### Scene 5: Live Demo — Tool Invocation (1:15 – 2:00)

**Visual:** Open the Pre-Visit Intelligence Agent chat. Type the prompt:

> *"Prep me for my next patient."*

Show the agent's "thinking" indicator, then show each tool call appearing in real time:
1. `build_patient_model` — show the JSON response collapsed
2. `simulate_scenario` (inaction) — show response collapsed
3. `simulate_scenario` (diagnostic gap) — show response collapsed
4. `compare_interventions` — show response collapsed

Briefly expand one of the tool responses to show the structured output (highlight the trial citation, e.g., "DAPA-CKD, PMID 32970396").

**Voiceover:**
> "I type 'prep me for my next patient.' The agent decides to call build_patient_model first — that fetches Maria's FHIR data and constructs the digital twin. Then it simulates inaction — what happens if we do nothing for twelve months. Then it checks for diagnostic gaps. Then it compares treatment options. Every output cites a real clinical trial. No hallucination."

**Why this scene matters:** This is the moment judges see Phantom actually work. The trial citation is the trust moment — proves it's evidence-grounded, not LLM guessing.

---

### Scene 6: The Briefing (2:00 – 2:30)

**Visual:** Show the rendered Pre-Visit Briefing. Scroll through it deliberately, highlighting three sections:
1. **Trajectory Alert** — "eGFR projected to drop to 41 in 12 months without intervention"
2. **Decision Point table** — empagliflozin vs semaglutide vs tirzepatide for this specific patient
3. **Diagnostic Gaps** — CKD-associated anemia, MASLD pattern detected

Pause briefly on each section so judges can read.

**Voiceover:**
> "Thirty seconds later, the clinician has a one-page briefing. Trajectory alert — Maria's eGFR is projected to hit 41 in twelve months without intervention. Decision point — here's how empagliflozin, semaglutide, and tirzepatide compare for *her specific* labs and comorbidities, ranked. Diagnostic gaps — her hemoglobin is trending down, suggesting CKD-associated anemia. Her ALT is persistently elevated — possible MASLD. None of this required the clinician to read 71 lab values."

**Why this scene matters:** This is where judges see the clinical value. The briefing is the deliverable — it's tangible, scannable, and obviously useful.

---

### Scene 7: Standards & Composability (2:30 – 2:50)

**Visual:** Show four standards badges — **MCP**, **A2A**, **SHARP**, **FHIR R4** — animated in sequence. Then cut to a conceptual diagram showing multiple agent types (Cardiology Agent, Nephrology Agent, Pharmacy Agent, Care Coordination Agent) all pointing to a single Phantom MCP Server.

**Voiceover:**
> "Phantom is built on every relevant standard — MCP, A2A, SHARP-on-MCP, FHIR R4. That means every agent on the Prompt Opinion marketplace can equip Phantom. Build the evidence base once. Reuse it everywhere. That's the marketplace multiplier effect."

**Why this scene matters:** Positions Phantom as infrastructure, not just an app. Judges thinking about platform value will hear this loud and clear.

---

### Scene 8: Close (2:50 – 3:00)

**Visual:** Phantom logo or wordmark, repo URL, hackathon badge.

**Voiceover:**
> "Phantom. The patient digital twin for clinical reasoning. Built for Agents Assemble."

**Why this scene matters:** Memorable close. Repeats the tagline so judges remember the project name.

---

## Backup Plans

### If a tool call fails during recording

**Don't restart the take.** Instead:
1. Stop talking, pause for 3 seconds
2. Cut to the architecture diagram (Scene 3 visual) and continue voiceover
3. In post-production, splice in a pre-recorded successful tool call from a backup take

**Pre-record a backup take of Scene 5** ahead of time so you have safety footage.

### If the ngrok URL changes mid-recording

This shouldn't happen if ngrok stays open. But if it does:
1. Stop the take
2. Restart ngrok, update the URL in Po MCP server config
3. Restart from Scene 4

### If the agent gives a bad response

**Don't try to fix it on camera.** Stop, restart the agent session, and re-record from Scene 5. Judges will not see your retries.

### If you're running over time at the 2:30 mark

Skip Scene 7 entirely and jump to Scene 8 close. Standards badges can be added as a static overlay during the close instead.

---

## Post-Recording Edits

1. **Add intro card** (0:00–0:02): Phantom logo + "Agents Assemble Hackathon Submission"
2. **Add captions** for clinical terms (eGFR, HbA1c, ASCVD, FIB-4, MASLD) — judges may not be clinicians
3. **Add architecture diagram overlay** during Scene 3 (semi-transparent, lower-third)
4. **Add Po platform logo** in lower-right corner when Po UI first appears (Scene 4)
5. **Color-grade** for consistency — slight desaturation gives a clean, professional look
6. **Add subtle background music** (royalty-free, low volume — no lyrics)
7. **Add end card** (2:58–3:00): repo URL, team names, "Built with MCP + SHARP + FHIR"
8. **Export at 1080p, H.264, mp4** — universal compatibility

---

## Two Alternative Versions

### Version B: Narrative-First (use if live demo is unreliable)

Same 3-minute structure, but flips the ratio: 60% talking-head explaining the *why* with diagrams and screenshots, 40% pre-recorded screen capture. Use this if your demo environment is fragile or if you want to emphasize the clinical reasoning over the technical execution.

**Scene allocation:**
- 0:00–0:30 — Hook + Problem (talking head with diagram overlays)
- 0:30–1:00 — Solution + Architecture (animated architecture diagram)
- 1:00–1:50 — Pre-recorded demo with voiceover
- 1:50–2:20 — Briefing walkthrough (static screenshot with annotations)
- 2:20–2:50 — Standards & marketplace value (talking head)
- 2:50–3:00 — Close

### Version C: Architecture-Heavy (use if judges are highly technical)

For a more technically sophisticated audience, spend more time on the SHARP integration, the FastMCP capabilities patching, and the multi-system simulation engine.

**Scene allocation:**
- 0:00–0:15 — Hook
- 0:15–0:45 — Problem
- 0:45–1:30 — Architecture deep-dive (SHARP context flow, capability advertising, JWT extraction)
- 1:30–2:15 — Live demo (compressed)
- 2:15–2:45 — Evidence base showcase (drug knowledge, trial data structure)
- 2:45–3:00 — Close

---

## Recording Day Tips

- **Do a dry run first** — record one full take with no intent to use it, just to surface issues
- **Watch the dry run with the audio muted** — does the visual flow make sense without narration? It should
- **Then watch with audio only** — does the script work without visuals? It should
- **Re-record problem sections individually** rather than re-recording the whole video
- **Keep takes** — even bad ones may have salvageable moments
- **Sleep on it** — record in the morning, edit in the afternoon, ship the next day. Tired editing is bad editing.