# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---

## Test set and trial method (used by criteria 1–3)

These criteria describe how the **finished** system must behave. Today
`POST /submit` and `POST /appeal` both return 501, so none of them can be met
yet.

### The fixed test set

The 20 samples live in a folder named `test_set/` at the repo root:

- one plain-text file per sample: `H01.txt`–`H10.txt`, `A01.txt`–`A05.txt`,
  `B01.txt`–`B05.txt`;
- one `test_set/manifest.csv`, one row per sample.

The set is written down before the first trial. No sample is added, removed or
edited once the first trial has started.

| Group | Count | What it is |
|---|---|---|
| **Human samples (H)** | 10 | Text I wrote myself, 80–300 words each. At least 4 of the 10 are **plain** (defined below). |
| **AI samples (A)** | 5 | Text produced by an AI tool from a prompt, 80–300 words, pasted in unedited. |
| **Borderline samples (B)** | 5 | Mixed text I expect to land between the two, such as AI text I edited by hand, or my own very formulaic writing. |

**Plain writing.** A human sample is plain if its **average sentence length is
at most 3 words**, computed as
`len(stylometry.words(text)) / len(stylometry.sentences(text))` with the helpers
already in `stylometry.py`. The manifest records this number for every H sample.

**Manifest columns.**

- Every sample: `id`, `group`, `file`, `word_count`, `expected_guess`.
- H samples also: `avg_sentence_length`, `plain` (yes or no).
- A samples also: `ai_tool`, `ai_model`, `prompt` (verbatim), `generated_on`
  (YYYY-MM-DD), `settings` (or "not shown"), `attempt` (first output, or picked
  from several), `edited` (always `no`).

**`expected_guess`** is `ai`, `human` or `unsure`: the label each sample is
meant to receive. It is filled in for every sample **before the first trial**
and never changed afterwards.

### A trial

A **trial** is one pass of all 20 samples through `POST /submit`, one after
another. I run **three trials**, back to back, and write down each trial's start
and end time. Each criterion must hold in **every** trial.

- **`creator_id`:** each sample uses its own id (`H01`, `A03`, `B02`, and so on)
  and the same id in all three trials. Trials are told apart by their time
  window in the log. Each id is used once per trial, so per-id rate limits do
  not interfere. The appeal and bad-input tests use other prefixes (`appeal_`,
  `bad_`).
- **Where each number comes from:** `guess`, `model_score` and `style_score` are
  read from the `/submit` response. The **combined score** is not in the
  response, so I take the `content_id` from the response and read
  `combined_score` from the matching entry in `GET /log`.
- **"High-confidence AI"** always means `guess` equal to `"ai"`, which is a
  combined score at or above `AI_THRESHOLD` in `config.py`.

---

## 1. False positives

At most **3 of the 10** human samples (H) may get `guess = "ai"`, in **each** of
the three trials. A trial with 4 or more is a miss.

**Why this target:** I accept up to 3 wrongly labeled samples in 10 because a
wrong label is not meant to be the final word: the label text is meant to
explain our uncertainty without accusing, and every writer can appeal
(criterion 4). This reasoning only holds if both of those actually work, which
is why the appeal criterion matters as much as this one.

---

## 2. Score spread

In **each** of the three trials, both of these must hold:

1. The arithmetic mean of the **combined score** of the 5 AI samples (A) minus
   the arithmetic mean of the combined score of the 10 human samples (H) is
   **at least 0.30**.
2. **At least 2 of the 5** AI samples have a combined score **above** the mean
   combined score of the 10 human samples.

The borderline samples (B) are not part of this criterion.

**Why this target:** The 0.30 matches the width of the "unsure" band (0.35 to
0.65), used as a yardstick: it asks the two groups to be about one band apart on
average, and it does not guarantee they land in different labels. An average can
hide overlap, so on top of the gap between group means I added a rule on
individual AI scores. I set it to 2 of 5 on purpose, as a light check, because I
don't yet know what this system can do.

---

## 3. Label coverage

In **each** of the three trials, for each of the three `guess` values `"ai"`,
`"human"` and `"unsure"`, **at least 5 samples** whose `expected_guess` is that
value must receive exactly that `guess`. A sample that gets a different label
does not count toward coverage of the label it received.

**Why this target:** A label that can never appear is not a real outcome. Without
all three labels the system effectively has two outcomes, and "unsure" is the
one that protects a writer from a wrongful accusation.

---

## 4. Appeal path

I check every appeal this way. Before the appeal, I run `GET /log` and save the
entries for that `content_id` and how many there are. After the appeal I run
`GET /log` again and compare entries for that same `content_id` only (other
requests in between would change the total).

A **valid appeal** is a `content_id` returned by an earlier `/submit` (any
label) plus a non-empty `reasoning` string. For **3 of 3** valid appeals:

- `POST /appeal` returns **HTTP 200**.
- The entries for that `content_id` are **exactly one longer**. The new last
  entry has `event = "appeal"`, `status = "under_review"` and my `reasoning`
  text.
- The original decision entry is **identical**, field for field, to the copy I
  saved before the appeal.
- Appealing the same `content_id` a second time also returns 200 and adds
  **one more** entry, so each appeal is recorded.

These requests are rejected. Each returns the status shown, adds **0** `appeal`
entries, writes **one** `rejected` entry, leaves the original entry unchanged,
and has a non-empty `error` and `message` in its JSON body:

| Request | Required status |
|---|---|
| `content_id` does not exist in the log | **404** |
| `reasoning` missing, empty or whitespace-only | **400** |
| `content_id` missing or not a string, or the body is not a JSON object | **400** |

**Why this target:** Silent failures are the danger. A mistyped id, or an empty
appeal that quietly disappears, looks to the writer like a broken endpoint, so
those cases must be rejected visibly and logged.

---

## 5. Bad input

`POST /submit` must return the status in the table for each of these nine
inputs. The response body is valid JSON with a non-empty `error` and a non-empty
`message`.

| # | Input | Required status |
|---|---|---|
| 1 | `text` field missing | **400** |
| 2 | `text` empty or whitespace-only | **400** |
| 3 | `text` is `null` | **400** |
| 4 | `text` is a number or a list | **400** |
| 5 | `text` longer than **5,000 characters** (exactly 5,000 is allowed) | **413** |
| 6 | Text the detector refuses to score, such as a single word | **400** |
| 7 | Body is not JSON, or is JSON but not an object | **400** |
| 8 | `creator_id` missing, blank or not a string | **400** |
| 9 | The detector model cannot load | **503** |

Rules that apply to all nine:

- Never an unhandled 500. Row 9 is the only 5xx allowed.
- After each request, `POST /ping` returns 200 with `"ok": true`, and
  `GET /health` returns 200 with `"ok": true`.
- For rows 1–8, the log gains **exactly one** new entry with
  `event = "rejected"`, counted by comparing `rejected` entries before and
  after. Its `creator_id` is `"unknown"` if none was sent.
- Characters are counted as the length of the Python string.
- To test row 9, start the service with `AI201_DETECTOR_MODEL` set to a model
  name that does not exist. `GET /health` should then still answer, with
  `detector_loaded` equal to `false`.

**Why this target:** A crash is one of the most common real failures. One
malformed request must not take the service down for everyone else, which is why
`/ping` and `/health` are checked after each bad request.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
