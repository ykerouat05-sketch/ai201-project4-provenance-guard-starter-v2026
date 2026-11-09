# The fixed test set

The 20 samples criteria 1-3 are measured on. `criteria.md` is the source of
truth for every rule here; this file only says what still has to be written and
how to record it.

**Nothing in here has been written yet.** `manifest.csv` holds the 20 rows with
their ids, groups, filenames and expected labels. Every measured field is blank
until the file it describes exists.

## The rules that make this set usable

From `criteria.md`:

- The set is written down **before the first trial**. Once a trial has started,
  no sample is added, removed or edited.
- `expected_guess` is fixed before the first trial and never changed afterwards.
  It is already filled in: `human` for H, `ai` for A, `unsure` for B.
- Every sample is **80-300 words**.
- A text appears in **at most one** of `calibration/`, `reference_set/` and
  `test_set/`. The four texts in `calibration/` are a different set and must not
  be copied in here.

## H01-H10 — your own writing (10 samples) — NOT WRITTEN

Write these yourself, by hand, in a plain text editor.

- **Ten samples**, 80-300 words each.
- **At least four must be plain.** Plain means an **average sentence length of
  three words or fewer**, computed as
  `len(stylometry.words(text)) / len(stylometry.sentences(text))`.
- **Do not use AI to write, rewrite, polish, expand or edit these.** That
  includes grammar suggestions. The criterion these feed measures how often the
  service accuses a real writer, and it is meaningless with anything but your
  own writing.
- Save each as UTF-8 text, one document per file, no title line: `H01.txt` …
  `H10.txt`.

A note on the four plain samples: three words per sentence is short. An 80-word
sample needs about 27 sentences. That is deliberate — plain, choppy writing is
where the model signal is expected to be weakest, so an easy sample set would
not test anything.

## A01-A05 — AI-generated (5 samples) — NOT WRITTEN

Five AI texts, 80-300 words each, pasted in **unedited**. Drafts for these were
approved in discussion but were never saved to the project, so these files are
empty and the decision about where their text comes from is still open.

Whatever is used, record in `manifest.csv` at the moment the file is created,
and never afterwards:

| Column | What goes in it |
|---|---|
| `ai_tool` | The product or interface used |
| `ai_model` | The exact model name and version the tool showed |
| `prompt` | The prompt, copied verbatim |
| `generated_on` | `YYYY-MM-DD` |
| `settings` | Temperature and so on, or `not shown` |
| `attempt` | `first output`, or that it was picked from several |
| `edited` | `no` for every A sample, by definition |

Leave nothing to memory. A guessed model name or date is worse than a blank.

## B01-B05 — borderline (5 samples) — NOT WRITTEN

Mixed text expected to land between the two. The approved types:

| id | Type | Who writes which part |
|---|---|---|
| B01 | Lightly edited AI text, on a new topic | AI draft, then **you** edit it by hand |
| B02 | Heavily rewritten AI idea list | AI draft, then **you** rewrite it sentence by sentence |
| B03 | A human opening with an AI middle | **You** write the opening; the middle is AI |
| B04 | Your own formulaic writing | **You** — a cover letter, a lab-report paragraph |
| B05 | AI text asked to be casual | AI, from a prompt asking for an informal register |

`expected_guess` is `unsure` for all five. That is a **test expectation**, not a
prediction: whether the finished system agrees is exactly what criterion 3
measures.

For B01, B02, B03 and B05, record the AI provenance columns for the AI part, and
put `yes` in `edited` wherever you changed the text.

## When the files exist

Fill the measured columns with the tool, not by hand:

```
python verify_dataset.py --write-hashes
```

That fills `sha256`, `word_count`, `avg_sentence_length` and `plain` for every
file that exists, and refuses to overwrite a hash that is already recorded.

Then, before every trial:

```
python verify_dataset.py
```

It re-hashes each file and compares. A sample that changed after the first trial
breaks the rule the whole set exists to enforce, so this is the check that
catches it.

## What is still missing

| Group | Files | Status |
|---|---|---|
| H01-H10 | 10 | Not written. Yours to write |
| A01-A05 | 5 | Not written. Source undecided |
| B01-B05 | 5 | Not written. Needs both an AI part and your part |

`manifest.csv` has every row and every expected label. Everything measured is
blank, and no hash exists, so `verify_dataset.py` reports the set as
**INCOMPLETE** until the files are there.
