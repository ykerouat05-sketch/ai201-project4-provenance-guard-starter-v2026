# Milestone 1: Trace a Submission Before You Build One

**Project:** Provenance Guard (a local web service that estimates whether a piece of writing was produced by a person or by an AI)

**Purpose of this document:** to trace how a text submission *would* travel through the system, using only what the repository's code actually does today, and to be explicit about what is built and what is only planned.

**Method:** I read `app.py`, `detector.py`, `stylometry.py`, `scoring.py`, `audit.py`, `config.py`, and `RUNNING.md`. I did not run the model, did not start the server, and did not change any source file. Because of that, **this document contains no measured scores.** Where numbers appear, they come from constants in the code or from arithmetic on those constants, and I say so.

**Status legend used throughout**

| Tag | Meaning |
|---|---|
| **EXISTS** | Implemented and working in the current code |
| **STUB** | A function or route exists but returns a placeholder |
| **PLANNED** | Described only in comments or docstrings; no code yet |
| **PARTIAL / PLACEHOLDER** | Some real code exists, but part of it is missing or filled with placeholder values |

---

## 1. Submission Architecture

A submission is a piece of text plus an identifier for who sent it. The intended path has seven steps. The route that ties them together (`POST /submit`) is still a stub, so several steps below are PLANNED even though some of the pieces they call already exist.

### The path at a glance

```
curl / client
     │  POST /submit  {"text": "...", "creator_id": "..."}
     ▼
[1] HTTP request ──► [2] Flask route submit() ──► [3] Input validation
                                                        │
                                   ┌────────────────────┴──────────────────┐
                                   ▼                                       ▼
                     [4] detector.model_signal()            [5] stylometry.style_signal()
                              model_score                            style_score
                                   └────────────────────┬──────────────────┘
                                                        ▼
                                  [6] scoring.combine_signals() → score_to_label()
                                                        ▼
                                  [7] audit.log_decision() + JSON response
```

### The seven steps

| # | Component | Receives | Does | Produces | Status |
|---|---|---|---|---|---|
| 1 | **HTTP request** | A `curl` command (or any client) sending JSON with `text` and `creator_id` to `http://127.0.0.1:5000/submit` | Carries the data over HTTP. Host and port come from `config.py` (`127.0.0.1`, `5000` by default) | A request that Flask receives | **EXISTS** |
| 2 | **Flask app and route** (`app.py`, `submit()`) | The request | `@app.post("/submit")` routes it to `submit()`. The function parses the body with `request.get_json(silent=True) or {}` | A Python dict named `payload` | **PARTIAL.** Parsing exists. Everything after it in `submit()` is a stub that returns HTTP 501 |
| 3 | **Input validation** | `payload["text"]`, `payload["creator_id"]` | Should reject missing, empty, wrongly typed, or enormous text | Either an error response or text that is safe to score | **PLANNED.** `app.py` says only that I must decide what to do on bad input |
| 4 | **Signal 1** (`detector.py`, `model_signal`) | A string | Runs the local gpt2 model, computes perplexity, converts it to a 0–1 score | `model_score` (higher means more AI-like) | **EXISTS.** Not yet called by `/submit` |
| 5 | **Signal 2** (`stylometry.py`, `style_signal`) | A string | Should measure the *shape* of the text (sentence lengths, vocabulary variety, punctuation) | `style_score` (higher means more AI-like) | **STUB.** Always returns `0.5` |
| 6 | **Combine and label** (`scoring.py`) | `model_score` and `style_score` | `combine_signals` merges them into one score. `score_to_label` compares that score to the thresholds in `config.py` | `combined_score`, a `guess` (`"ai"`, `"human"`, or `"unsure"`) and label text | **PLACEHOLDER.** `combine_signals` already returns a 50/50 weighted average, but the label text is literally the string `"PLACEHOLDER …"` |
| 7 | **Log and respond** (`audit.py` and `jsonify`) | All the values above plus a `content_id` | `audit.log_decision(...)` appends one JSON line to `logs/audit.jsonl`. The route then returns the JSON response | The response the writer sees, and a permanent log entry | **PARTIAL.** The logger exists and works. Nothing in `/submit` calls it yet |

### Notes on specific steps

- **`content_id`.** `app.py` imports `uuid` but never uses it. The `/appeal` docstring says it needs a `content_id` from the original submission, so `submit()` is expected to generate one. That generation is **PLANNED**, not written.
- **Cost of step 4.** The first call loads the gpt2 model into memory, which takes seconds. Later calls reuse it, because `detector.py` caches it in the module variable `_model`.
- **Step 6 and the stub.** With `style_score` stuck at `0.5` and equal weights (`0.5` each in `config.py`), the combined score can only fall between 0.25 and 0.75. This is arithmetic on the constants, not an experiment. The "human" label needs a combined score of 0.35 or lower, which would require `model_score` of 0.20 or lower while the style stub is in place.
- **Step 7 and appeals.** The log is append-only. An appeal is written as a *new* line next to the original decision instead of overwriting it.

---

## 2. The Two Signals

The project combines two independent signals because each looks at the text differently, and each has a different blind spot.

### Signal 1: `detector.py` (the model signal)

| Question | Answer (from the code) |
|---|---|
| **What does it measure?** | **Perplexity**: how surprised a language model is by the text. Lower perplexity means the model found the text easy to predict |
| **Model** | `gpt2`, running locally through `transformers` and `torch` (`config.DETECTOR_MODEL`). About 550 MB. No API key |
| **What does it return?** | A score from 0 to 1 where **higher means more likely AI**. The formula is `1 / (1 + (perplexity / 45) ** 1.6)`, so perplexity 45 maps to exactly 0.5 |
| **Input limits** | Only the first 400 tokens are scored (`DETECTOR_MAX_TOKENS`). Fewer than 3 tokens raises `ValueError`. A missing model raises `DetectorUnavailable` |

**Why the property might differ between humans and AI.** A language model writes by repeatedly choosing a likely next word. So text a model produced tends to be text another model finds predictable. Human writing tends to wander more, with odd word choices and specific details.

**Blind spot.** Predictability is not authorship. This signal rewards *common words in short, ordinary sentences*, and many real people write that way: someone writing in a second language who sticks to vocabulary they are sure of, a younger writer, or anyone who is deliberately plain. Writing like that can score as machine-like as machine writing does. The reverse also happens: dense, ornate prose full of rare words tends to look human to this signal. The code comments describe this as structural rather than a bug. I have not tested it myself.

### Signal 2: `stylometry.py` (the style signal)

| Question | Answer (from the code) |
|---|---|
| **Does the file exist?** | Yes, but it is mostly stubs. Only the helpers `sentences()` and `words()` are implemented |
| **What should it measure?** | Three things: `sentence_length_spread` (do sentence lengths vary?), `type_token_ratio` (unique words ÷ total words) and `punctuation_density` |
| **Current behavior** | The three measures return `0.0`. `style_signal()` returns `0.5` for every input |
| **Intended output** | A 0–1 score in the same direction as signal 1: higher means more AI |

**Why the property might differ between humans and AI.** The `stylometry.py` docstring argues that generated prose tends toward even, mid-length sentences and a narrower vocabulary, while human writing is "lumpier," for example a three-word sentence next to a forty-word one. This is the project's stated hypothesis. I did not verify it.

**Blind spot.** It cannot read. It does not know what the text says, so anything that changes the shape without changing the substance moves it: added typos, broken-up sentences, a pasted quotation. That is cheap to do on purpose. Its own docstring also warns that type-token ratio falls as text gets longer, so texts of different lengths are not directly comparable.

### Why the two signals might disagree

They measure different properties, so they can point in opposite directions on the same text:

| Situation | Signal 1 (predictability) | Signal 2 (shape) |
|---|---|---|
| A plain essay in short, common-word sentences, written by a person | May read **AI-like** | May read human if the sentence lengths vary |
| AI text with a few typos added and sentences split up | Still reads AI-like | May read **human-like** |
| Ornate human prose with long, even-length sentences | Reads human-like | May read AI-like |

When the two disagree, the combining rule in `scoring.combine_signals` decides the outcome. The docstring there notes that a simple average of 0.9 and 0.1 gives 0.5, which falls in the "unsure" band, and asks whether that is the behavior I want.

---

## 3. False Positive Scenario

A **false positive** here means a real person's original writing is labeled AI-generated.

### Important caveat

`/submit` is not built. I cannot show a real submission going through the whole pipeline. What follows traces the path the code is designed for. **Facts that come from the code are marked as such. Everything else is hypothetical.** I report no experimental scores because I did not run the model.

### The writer

A student who is learning English writes an essay in plain vocabulary and short sentences. They wrote every word themselves.

### Following the submission

| Step | What would happen | Basis |
|---|---|---|
| Request | The student's text and `creator_id` are sent to `POST /submit` | Design |
| Today's actual behavior | The route returns HTTP **501** `not_implemented`. Nothing is scored, labeled or logged | **Code** |
| Validation | Not built. The text is accepted or not depending on rules I have not written yet | **Planned** |
| Signal 1 | gpt2 would measure perplexity. Plain, common-word writing is the pattern the code comments warn can score machine-like, so `model_score` could come out high | **Hypothesis** supported by the comments in `detector.py`. Not measured |
| Signal 2 | Currently a stub: `style_score` is always `0.5`. Once built, it could push the score either way | **Code** (stub) / **Planned** |
| Combine | `0.5 × model_score + 0.5 × style_score` | **Code** (placeholder weights in `config.py`) |
| Label | The combined score is compared with the thresholds below | **Code** |
| Log | A line would be appended to `logs/audit.jsonl` | **Planned wiring** |

### The two scores' roles

Both scores are numbers from 0 to 1 where higher means more AI-like. Each contributes half of the combined score under the placeholder weights. In the false-positive case, signal 1 is the likely source of the accusation. Signal 2 acts as a brake only if it is built to read the text as human. While it is a stub fixed at `0.5`, it pulls every score toward the middle.

### The thresholds (from `config.py`)

| Combined score | Label | Meaning |
|---|---|---|
| **at or below 0.35** (`HUMAN_THRESHOLD`) | `human` | High-confidence human |
| **between 0.35 and 0.65** | `unsure` | The system will not commit |
| **at or above 0.65** (`AI_THRESHOLD`) | `ai` | High-confidence AI |

The comparisons in `score_to_label` use `>=` for AI and `<=` for human, so a score of exactly 0.65 is labeled AI and exactly 0.35 is labeled human. The thresholds were chosen by the starter project. They are not tuned to any data I have seen.

**What the stub makes possible.** Since the combined score can only range from 0.25 to 0.75 while `style_score` is `0.5`, a `model_score` above 0.80 would produce a combined score above 0.65, and therefore the AI label. That is arithmetic, not an observation.

### What label the user receives

- **Today:** none. They receive a 501 error.
- **After Milestone 5, if the false positive occurs:** the AI label text. That text has not been written. `score_to_label` currently returns the literal string `"PLACEHOLDER — write the high-confidence AI label."`

### Appeal functionality today

| Piece | State |
|---|---|
| `POST /appeal` | **STUB.** It returns HTTP 501 `not_implemented` and echoes the request back |
| `audit.log_appeal(content_id, creator_id, reasoning)` | **EXISTS.** Appends an event with `status: "under_review"`. It does not alter the original decision |
| `audit.entries_for(content_id)` | **EXISTS.** Can check that an id is real |
| Re-checking or human review | **Does not exist.** The `/appeal` docstring says no automatic re-checking is needed. The code has no reviewer workflow |

So, today, a falsely accused writer has no working way to object. Once `/appeal` is built, it would record the objection and mark the item under review, but nothing in the code would act on it.

### Ways to reduce false positives (all PROPOSED, none implemented)

| Idea | Trade-off |
|---|---|
| Widen the "unsure" band, for example AI only at 0.80 or higher | Fewer false accusations, more AI text passes |
| Weight the more human-leaning signal higher | Same trade-off |
| Require both signals to agree before assigning the AI label | Fewer false accusations, more AI text labeled "unsure" |
| Write the "unsure" label so that it explains uncertainty without accusing | Costs nothing in accuracy; helps the writer |
| Reject or flag very short text instead of scoring it | Short text gives unreliable readings |
| Finish `/appeal` and make it easy to find in the label text | Gives wrongly labeled writers a path to challenge |

`config.py` states that no setting avoids the trade: there are only settings that decide who pays for it.

---

## 4. API Contracts

All details below come from `app.py` as it exists now.

### `POST /submit`

**Input (intended)**

| Field | Type | Required | Notes |
|---|---|---|---|
| `text` | string | Yes | The writing to evaluate |
| `creator_id` | string | Yes | Who submitted it |

No validation is implemented, so these are expectations from the docstring, not enforced rules.

**Example request**

```bash
curl -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d '{"text": "some writing", "creator_id": "me"}'
```

On Windows PowerShell, use `curl.exe` and keep the command on one line (see `RUNNING.md`).

**Current behavior**

- HTTP status: **501**, for every request.
- Body, as returned today:

```json
{
  "error": "not_implemented",
  "message": "POST /submit isn't built yet — see the TODO in app.py.",
  "you_sent": {
    "text_length": 12,
    "creator_id": "me"
  }
}
```

| Field | Meaning |
|---|---|
| `error` | Always `"not_implemented"` |
| `message` | A fixed explanation |
| `you_sent.text_length` | `len()` of the submitted `text`, or `0` if `text` is absent |
| `you_sent.creator_id` | The submitted `creator_id`, or `null` if absent |

By reading the code (not by testing), a body whose `text` is not a string, or a JSON body that is a non-empty list, would raise an exception and produce a 500 instead of a 501. That is one reason input validation matters.

**Planned response fields** (from the `submit()` docstring; not yet returned)

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Identifier used later by `/appeal` |
| `guess` | string | `"ai"`, `"human"` or `"unsure"` |
| `confidence` | number | The docstring shows `0.0` as a placeholder. Its exact definition is not specified |
| `label` | string | The sentence a reader sees |
| `model_score` | number | Signal 1 output |
| `style_score` | number | Signal 2 output |

The docstring says both signal scores must be in the response because the unit 8 scripts read them. Planned error codes are not specified.

### `GET /health`

**Input requirements:** none. No body, no parameters.

**Status:** 200.

**Response fields** (exactly the keys in the code)

| Field | Type | Meaning |
|---|---|---|
| `ok` | boolean | Always `true`. If you got an answer, the service is up |
| `detector_model` | string | The model name from `config.DETECTOR_MODEL` (`"gpt2"` unless the `AI201_DETECTOR_MODEL` environment variable overrides it) |
| `detector_loaded` | boolean | Whether the model is currently in memory in this running process |
| `rate_limiting` | boolean | From `config.RATE_LIMITING_ENABLED`. `false` unless `AI201_RATE_LIMITS=1` |
| `log_entries` | integer | Number of readable entries in `logs/audit.jsonl` |

**Example shape** (illustrative; I did not run the server, so these values are what the defaults would give on a fresh start with an empty log):

```json
{
  "ok": true,
  "detector_model": "gpt2",
  "detector_loaded": false,
  "rate_limiting": false,
  "log_entries": 0
}
```

**What `detector_loaded` means.** It is computed as `detector._model is not None`. It becomes `true` only after something calls the loader, either a scoring call or `warm_up()`. It does **not** mean "the model files have been downloaded." A downloaded model can still report `false` until it is loaded into the running process. `RUNNING.md` also says that if it flips back to `false` between requests, something is reloading the model on every call.

### `POST /ping`

**What it does.** It echoes back the `message` field and identifies the service. It does no scoring, loads no model and writes no log.

**Example request**

```bash
curl -X POST http://127.0.0.1:5000/ping -H "Content-Type: application/json" -d '{"message": "hello"}'
```

**Response** (HTTP 200)

```json
{
  "ok": true,
  "you_sent": "hello",
  "service": "provenance-guard"
}
```

If no message is sent, `you_sent` is `null`.

**Why it is useful as a control endpoint.** It depends on almost nothing: no model, no signals, no log. If `/ping` answers but `/submit` fails, the problem is in my `/submit` handler. If `/ping` fails too, the service itself is broken. For that reason, the starter says to leave it alone.

### Other existing routes

| Route | State | Notes |
|---|---|---|
| `GET /log` | **EXISTS** | Returns `{"count": n, "entries": [...]}`. Accepts an optional `?limit=N` query parameter |
| `POST /appeal` | **STUB** | Returns HTTP 501. Planned input: `content_id` and `reasoning` |

---

## Current State at a Glance

| Component | State |
|---|---|
| `POST /ping`, `GET /health`, `GET /log` | EXISTS |
| `POST /submit` | STUB (501) |
| `POST /appeal` | STUB (501) |
| `detector.py` | EXISTS |
| `audit.py` | EXISTS |
| `stylometry.py` | STUB (helpers implemented; measures return `0.0`; `style_signal` returns `0.5`) |
| `scoring.combine_signals` | Placeholder 50/50 average |
| `scoring.score_to_label` | Threshold logic exists; label text is placeholder |
| Rate limiting | Off (unit 8) |

---

## Conclusion: What I Learned

- A web service is a chain of small pieces. Each one receives something, transforms it and hands it on. Tracing the chain first shows where each decision gets made.
- The starter has real working parts (`/ping`, `/health`, `/log`, the detector and the audit logger) and clearly marked gaps (`/submit`, `/appeal`, the style signal, the labels). I now know which is which.
- The model signal measures **predictability, not authorship**. That is why a plain human writer can be mislabeled, and why a second signal is worth building.
- The style signal has the opposite weakness: it cannot read, so it is easy to fool.
- The thresholds (0.35 and 0.65) are where fairness is decided. A wider "unsure" band protects writers and lets more AI text through. No setting avoids the trade.
- An appeal path matters because a wrongly accused writer has otherwise no recourse. It is still unbuilt.
- `/ping` is a control: when something breaks, test it first.
