# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->



---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**

**Why that might differ between human and AI writing:**

**What it can't see:**

### Signal two — the style signal

**What it measures:**

**Why that might differ between human and AI writing:**

**What it can't see:**

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

**The numbers:**

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```powershell
PS> curl.exe -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d '{\"text\": \"I went to the store on Saturday to buy some food. The store was busy and I waited in line for a long time. After that I went home and made dinner for my family. It was a good day and I was happy.\", \"creator_id\": \"me\"}'
```

```json
{
  "confidence": 0.0,
  "content_id": "c6f4156d-96d4-45db-b32d-f102e3b842d5",
  "guess": "placeholder",
  "label": "PLACEHOLDER",
  "model_score": 0.93
}
```

*Milestone 3 snapshot: only the first signal (`model_score`) is connected.
`guess`, `confidence` and `label` are placeholders, and there is no
`style_score` yet. Those arrive in Milestones 4 and 5.*

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```powershell
PS> curl.exe "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": null,
      "content_id": "d0010a8e-e81c-4c29-8aa6-56db7cc7556f",
      "creator_id": "me",
      "guess": "placeholder",
      "label": null,
      "model_score": 0.93,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-03T05:11:00+00:00"
    },
    {
      "combined_score": null,
      "content_id": "c6f4156d-96d4-45db-b32d-f102e3b842d5",
      "creator_id": "me",
      "guess": "placeholder",
      "label": null,
      "model_score": 0.93,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-03T05:16:50+00:00"
    }
  ]
}
```

The second entry is the submission above (same `content_id`). The first is an
earlier submission of the same text.

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

Provenance Guard uses rate limiting on the `/submit` endpoint to prevent
automated scripts and abusive users from overwhelming the service or repeatedly
testing its detection thresholds.

**My limits:** 5 per minute, 50 per day

- **5 requests per minute**
- **50 requests per day**

**Why those numbers and not others:**

These limits balance legitimate use with protection against automated
submissions. A normal user should have enough requests to submit their work. A
script that sends many variations under one `creator_id` is held to 5 a minute
and 50 a day. A script that changes its `creator_id` on every request is not
slowed by this mechanism (see "What a caller counts as").

**What a caller counts as:**

Requests are tracked using the `creator_id` (`app.py::rate_limit_key`). The
caller's address is used as the fallback when `creator_id` is missing, blank or
not a string, or when the request body isn't a JSON object.

- Every request to `/submit` counts, **including ones rejected with a 400**. In a
  test, five requests with no `text` from one `creator_id` were answered `400`
  five times, and the sixth got `429`.
- Because the key is the `creator_id`, one caller who invents a new `creator_id`
  each time gets a fresh allowance each time. One household sharing a single
  `creator_id` would share one allowance.
- The counters are kept in memory (`RATE_LIMIT_STORAGE = "memory://"`), so a
  restart of the service clears them.

**When a limit is exceeded:**

The service returns HTTP `429 Too Many Requests` with this JSON body, where
`limit` names the limit that was hit (`5 per 1 minute` or `50 per 1 day`):

```json
{"error": "rate_limited", "limit": "50 per 1 day", "message": "Too many submissions. Try again shortly."}
```

Every rate-limit rejection is written to the audit log, by `audit.log_rejection`
in the 429 handler, as an entry like this:

```json
{"timestamp": "2026-11-08T22:30:18+00:00", "creator_id": "flood_tester", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

Rate limiting is enabled by `RATE_LIMITING_ENABLED = True` in `config.py`, with
`RATE_LIMIT_PER_MINUTE = 5` and `RATE_LIMIT_PER_DAY = 50`. The decorator on
`/submit` reads those values when the service starts.

**The run of status codes when I pushed past it:**

`python run_attacks.py --flood 15`, 15 submissions as one `creator_id`
(`flood_tester`). The report is `results/flood_2026-11-08_1730.md`.

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

**The daily limit, tested separately:**

The per-minute limit stops a normal run before the daily one can be reached, so
the daily limit was tested in an isolated script. It raised the per-minute limit
to 100 **in memory only**, kept the daily limit at 50, and wrote to a temporary
log, so `config.py` and the real audit log were not touched. It sent 51 requests
with one `creator_id`: the first 50 returned `200` and the 51st returned `429`
with `"limit": "50 per 1 day"`. That rejection was logged, and a different
`creator_id` sent right afterwards was still accepted with `200`.

---

## Attack Run — Before

`python run_attacks.py --set attack_set --label before` against commit `de5eeb5`.
The full table is `results/attack_run_2026-11-08_1753_before.md`.

**What was running.** A real `model_score`, but `guess`, `label` and `confidence`
are still placeholders, and `style_score` and `combined_score` are `null`
(Milestones 4 and 5 aren't built). This is a baseline of an unfinished
classifier, not of the finished system.

| Family | Attacks | HTTP statuses |
|---|---|---|
| `evasion` | 10 | 200 × 10 |
| `false_positive` | 8 | 200 × 8 |
| `prompt_injection` | 6 | 200 × 6 |
| `malformed` | 20 | 400 × 10, 200 × 8, 429 × 2 |
| `flood_same_creator` | 12 | 200 × 5, 429 × 7 |
| **All** | **56** | **200 × 37, 400 × 10, 429 × 9** |

No row was skipped (32 + 24 records in the two files, 56 attacks run), and the
runner marked none as BROKE: there was no 5xx, crash or dropped connection. The
**Verdict** column is left blank on purpose, because no label thresholds exist
yet to judge against.

**What the run does show**

- *Server stability.* All 56 requests got an answer, including a 60,000-character
  text, control characters, deeply nested JSON and bodies that weren't JSON.
- *Input validation.* Ten malformed requests got `400` and each left a `rejected`
  entry (`empty_text`, `text_not_scoreable`, `missing_text`, `invalid_text`).
  Eight were accepted with `200`: odd text (control characters, punctuation only,
  one very long word, emoji only, right-to-left script, 60,000 characters), a
  request with no `creator_id`, and one whose `creator_id` is an object. So there
  is no length cap yet, and `creator_id` is not checked: the missing one was
  logged as `null` and the object was logged as an object.
- *Rate limiting.* The flood family got five `200`s and then seven `429`s, logged
  as `5 per 1 minute`. Two malformed requests (`RQ10`, `RQ11`) also got `429`.
  Both have no `creator_id`. The likely explanation is that they share the
  caller-address bucket with the other requests that had none (`RQ02`, `RQ06`,
  `RQ07`, `RQ08`, `RQ09`), so the requests after the fifth in that minute were
  limited. This is consistent with the code (a missing or non-string
  `creator_id` falls back to the caller's address) and with the log order, but
  the log does not record which bucket counted a request, so it was not directly
  observed. **Either way, this run doesn't show how the service handles those
  two inputs**, because the limiter answered first.
- *The log is complete.* Every one of the 56 attacks left exactly one audit
  entry: 37 decisions, 10 validation rejections and 9 rate-limit rejections. The
  submitted text itself is not stored in the audit log: no entry has a text
  field. Other fields the caller controls are logged as sent, for example a
  `creator_id` that was an object (the `RQ06` entry below).

**What the run does not show.** Every row says `placeholder` and `0.000`. That
`0.000` is the Score column, which the runner fills from `confidence` (a
placeholder), so it describes no attack. A `200` only means the text was scored,
not that an attack was detected or defeated. The only real signal is
`model_score`, in each attack's detail:

- Seven of the eight `false_positive` inputs have a `model_score` of 0.6175 or
  higher (up to 0.8816), and one has 0.3223. That isn't a label: the thresholds
  apply to a combined score that doesn't exist yet, so whether any of these
  writers would be accused is unknown.
- Junk inputs score at both extremes (control characters 0.0, punctuation only
  0.0112, one very long word 0.9976, emoji only 0.9969, 60,000 characters 0.9876),
  which says nothing about authorship.
- All six `prompt_injection` inputs were scored without error. The service uses
  the text only to score it, so that is the extent of what this run shows.



**Ten audit log entries from the run**

Copied from `results/audit_extract.json` (a `GET /log` snapshot of 77 entries;
entries 22 to 77 are this run), in log order:

| # | Attack | What it shows |
|---|---|---|
| 1 | `FP06` | A `false_positive` input: a high `model_score` with a placeholder `guess` |
| 2 | `MF01` | Whitespace-only text rejected as `empty_text` |
| 3 | `MF02` | A single character rejected by the detector as `text_not_scoreable` |
| 4 | `MF08` | A 60,000-character text accepted, so there is no length cap yet |
| 5 | `RQ03` | `text` that is a number, rejected as `invalid_text` |
| 6 | `RQ06` | An object as `creator_id`, accepted and logged as an object |
| 7 | `RQ07`–`RQ09` | A body that isn't a JSON object, rejected as `missing_text` under `unknown` (the three are indistinguishable in the log) |
| 8 | `RQ10` or `RQ11` | Rate-limited under `unknown`; entries 63 and 64 are identical in the log, so the two can't be told apart. The limiter answered before the input was handled |
| 9 | `FL01_05` | The last flood request allowed before the limit |
| 10 | `FL01_06` | The first flood request rejected with `429` |

```json
{"combined_score": null, "content_id": "41f17824-3f25-4f27-963b-d30fef10dd4e", "creator_id": "attacker_FP06", "guess": "placeholder", "label": null, "model_score": 0.8814, "status": "decided", "style_score": null, "timestamp": "2026-11-08T22:53:09+00:00"}
{"creator_id": "attacker_MF01", "event": "rejected", "reason": "empty_text", "status": "rejected", "timestamp": "2026-11-08T22:53:10+00:00"}
{"creator_id": "attacker_MF02", "event": "rejected", "reason": "text_not_scoreable", "status": "rejected", "timestamp": "2026-11-08T22:53:10+00:00"}
{"combined_score": null, "content_id": "98fe6275-929c-4a61-b8f8-a2291186c0b4", "creator_id": "attacker_MF08", "guess": "placeholder", "label": null, "model_score": 0.9876, "status": "decided", "style_score": null, "timestamp": "2026-11-08T22:53:12+00:00"}
{"creator_id": "attacker_RQ03", "event": "rejected", "reason": "invalid_text", "status": "rejected", "timestamp": "2026-11-08T22:53:12+00:00"}
{"combined_score": null, "content_id": "02be91d0-f646-4590-a2f4-f149ed26ec51", "creator_id": {"id": "x"}, "guess": "placeholder", "label": null, "model_score": 0.0492, "status": "decided", "style_score": null, "timestamp": "2026-11-08T22:53:12+00:00"}
{"creator_id": "unknown", "event": "rejected", "reason": "missing_text", "status": "rejected", "timestamp": "2026-11-08T22:53:12+00:00"}
{"creator_id": "unknown", "event": "rejected", "limit": "5 per 1 minute", "reason": "rate_limited", "status": "rejected", "timestamp": "2026-11-08T22:53:12+00:00"}
{"combined_score": null, "content_id": "94ba6b64-a00b-4850-bb64-acf17535eeef", "creator_id": "attacker_flood", "guess": "placeholder", "label": null, "model_score": 0.0287, "status": "decided", "style_score": null, "timestamp": "2026-11-08T22:53:13+00:00"}
{"creator_id": "attacker_flood", "event": "rejected", "limit": "5 per 1 minute", "reason": "rate_limited", "status": "rejected", "timestamp": "2026-11-08T22:53:13+00:00"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

Criteria 1–3 need `test_set/` (20 fixed samples with `expected_guess`) run three
times through `run_eval.py` and scored by `check_criteria.py`. No sample files
exist yet — `test_set/` holds only `manifest.csv` and `README.md` — so **no
trial has run**. Criteria 4 and 5 are not trial-based; they are checked directly
against a running service by `check_criteria.py --appeals` and
`check_criteria.py --bad-input`, and that evidence does exist.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives | at most 3 of 10 H samples get `guess = "ai"`, each of 3 trials | no trial run | no trial run | no trial run | **NOT EVALUABLE** |
| 2. Score spread | mean(A) − mean(H) combined score ≥ 0.30, and ≥2 of 5 A samples above mean(H), each of 3 trials | no trial run | no trial run | no trial run | **NOT EVALUABLE** |
| 3. Label coverage | ≥5 samples per label whose `expected_guess` matches their `guess`, each of 3 trials | no trial run | no trial run | no trial run | **NOT EVALUABLE** |
| 4. Appeal path | 3 of 3 valid appeals 200 + one `under_review` entry; repeat recorded; 404/400 rejections, one `rejected` entry each | — not trial-based, see evidence below — | | | **MET** |
| 5. Bad input | nine rows with required status, no unhandled 5xx except row 9, one `rejected` entry per row 1–8, `/ping`/`/health` answer | — not trial-based, see evidence below — | | | **MET**, with 2 documented limitations |

**Not MISSED — NOT EVALUABLE.** Criteria 1–3 are not reported as failed targets.
There is no label, no `style_score`, and no `combined_score` to measure them
against yet (see Diagnoses, below), so nothing has been judged against those
targets either way.

### Evidence for criteria 4 and 5

Collected against an **isolated** test service: `app.py` run with its audit log
pointed at a temporary file, on a non-default port, so the project's own
`logs/audit.jsonl` was never written to by these checks.

**Criterion 4 — `results/appeals_2026-11-09_2234_m4.json`.** All 10 checks held:
3 valid appeals (each 200, exactly one new `under_review` entry, the original
decision entry confirmed unchanged beforehand), a repeat appeal on the same
`content_id` (200, one more entry), and the four rejections — unknown
`content_id` (404), missing `content_id` (400), empty/whitespace/non-string
`reasoning` (400), and a non-object body (400) — each adding one `rejected`
entry and zero `appeal` entries.

**Criterion 5 — two files, because row 9 needs a different service.**
`AI201_DETECTOR_MODEL` is read once at startup, so a service can either load a
real model (for rows 1–8) or fail to load one (for row 9), never both at once:

- `results/bad_input_2026-11-09_2235_m4.json` — rows 1–8, against a normal
  service. Every row returned its required status (400 for rows 1–4 and 6–8,
  413 for text over 5,000 characters, 200 for exactly 5,000), each rejection
  added exactly one `rejected` entry, no row returned a 5xx, and `/ping` and
  `/health` still answered 200 afterwards.
- `results/bad_input_2026-11-09_2235_m4_row9_brokenmodel.json` — row 9, against
  a service started with a model name that doesn't exist. It returned 503, and
  `/health` reported `detector_loaded: false`.
- `results/criteria_2026-11-09_2235_m4.md` is the generated report. Read on its
  own, it shows criterion 5 as NOT EVALUATED, because `check_criteria.py` takes
  one `--bad-input-evidence` file per run and the file it was given doesn't
  cover row 9 (that requires the second file, above). That is the tool
  describing its own single-file input honestly, not evidence that row 9 is
  untested — the second file supplies it.

**Two limitations in this evidence, stated plainly:**

1. `/ping` and `/health` were checked **once, after the whole batch** of bad
   inputs in each service, not after every individual request as `criteria.md`
   literally asks. Each row's own status was still checked directly against its
   required value, so an in-row crash would have shown up as that row failing
   regardless — but a transient failure that recovered before the final check
   would not have been caught.
2. For row 9, `detector_loaded: false` was observed live in `GET /health`
   during collection, but that value is not persisted in the evidence file —
   the file only records that `/health` returned 200. The 503 status itself
   **is** in the file.

Neither limitation changes the verdict; both are recorded here so the evidence
isn't claimed to be more complete than it is.

**Real output**, pasted as text, naming the file and function that produced it
(`check_criteria.py::check_appeals`, from `results/appeals_2026-11-09_2234_m4.json`):

```json
{
  "label": "valid appeal 1",
  "kind": "valid",
  "ok": true
}
```

No equivalent trial output exists for criteria 1–3 — there is no trial to paste.

**Diagnoses**

*Criteria 1–3, confirmed from the code, not from running anything:*

| Stage | State |
|---|---|
| Route (`app.py::submit`) | Imports `detector` only — never `stylometry` or `scoring` |
| Signal one (`detector.model_signal`) | Real; every decision entry has a non-null `model_score` |
| Signal two (`stylometry.style_signal`) | `return 0.5` — a constant, for every input |
| Combining rule (`scoring.combine_signals`) | Implemented but never called by `/submit` |
| Label mapping (`scoring.score_to_label`) | Implemented but never called by `/submit`; `guess` is hardcoded to the literal string `"placeholder"` |

One stage is unfinished (signal two), and that single gap is why the next two
stages are unreachable: `/submit` has nothing to pass them, so it never calls
them, so `style_score`, `combined_score` and `label` are `null` in every one of
the 47 decision entries in the audit log. This is a pipeline that stops partway
through, not three independent failures — fixing signal two is the one change
that reopens criteria 1–3. No claim is made here about what any label or score
*would* be once that stage exists.

*Historical baseline (`results/attack_run_2026-11-08_1753_before.md`, against
commit `de5eeb5`), distinct from the current-code evidence above:* 0 of 56
attacks were auto-marked BROKE. Three confirmed misses, all at the **route**
stage, all the same mechanism — an attacker-controlled field reaching the log
with no check on it: `MF08` (60,000-character text accepted; no length check
existed), `RQ02` (missing `creator_id` accepted and logged as `null`), `RQ06`
(an object as `creator_id` accepted and logged as an object). Current-code
evidence under criterion 5 (row 5, over 5,000 characters → 413; row 8, missing
or non-string `creator_id` → 400) shows the same three cases now rejected — but
no fresh attack-set run exists against current code, so this is drawn from the
criterion-5 evidence above, not from a re-run of the attack set itself.



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
