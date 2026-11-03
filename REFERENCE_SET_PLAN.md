# Reference set: collection and analysis plan

Status: **plan only.** No `reference_set/` folder exists, no volunteer has been
contacted, and no reference text has been collected or generated.

## Purpose and limits

The reference set is for **exploring how the three style measures are
distributed** and for choosing **candidate normalization limits** for
`stylometry.py`. It does **not** measure detector accuracy. Final evaluation is
done separately on `test_set/`, and nothing here is ever used to tune against
`test_set/`.

It is kept apart from the other sets:

| Set | Purpose | ID prefix |
|---|---|---|
| `calibration/` | Four inputs used to inspect the raw measures | none |
| `reference_set/` (not yet created) | Distributions and candidate limits | `R` |
| `test_set/` (not yet created) | Final evaluation against `criteria.md` | `H`, `A`, `B` |

A text appears in at most one of these sets.

## How decisions are marked

- **Approved** means I decided it myself in the design discussion.
- **Proposed default** means I asked the assistant to finish the decisions, and
  it supplied the value. I have not yet reviewed these and can change any of
  them before recruiting or collecting. A proposed default carries no approval.

## Scope (approved)

Scope B: my own writing, contemporary volunteer writing given with explicit
informed permission, and AI-generated writing from different models and prompts.
Historical public-domain writing is **not** in the first version and may be
reconsidered later as a separate subgroup.

## Gate before any recruiting (not yet done)

Ask the course instructor and the university, and get answers in writing if
possible:

- Does collecting writing from volunteers for this project count as human-subjects
  research, and does it need an IRB review, determination or exemption?
- Does the course allow volunteer text in the repository, and may the repository
  be public or must it stay private?
- Are there rules on recruiting classmates, on handling other students' writing,
  on where such data may be stored, and on how long consent records must be kept?
  (Approved retention below, "thread deleted at the commit", may need to change.)
- Is there required consent wording?

If review is required, this plan waits for it.

## Human writing

| Item | Decision | Status |
|---|---|---|
| Minimum volunteers before analysis | **10**, counted as volunteers who consented, delivered at least one text and have not withdrawn at the freeze | Approved |
| Expected volunteers | 10 to 15 | Approved |
| Maximum texts per writer | **5**, and my own writing follows the same cap | Approved |
| If the minimum is not reached | Keep recruiting (no analysis until it is) | Approved |
| Contemporary writing with known provenance | The priority. Provenance is labeled `self-reported`, never "verified" | Approved |
| Length of every text | 80 to 300 words | Approved |

## Volunteer consent and privacy (approved)

- **Consent method:** a private message with explicit written agreement.
- **Channel:** a messaging app, one conversation per volunteer, never a group chat.
- **Identity link:** only the consent thread. No separate list of identities and
  labels. The repository holds only a random label (such as `W07`).
- **Collected:** the text, the label, and a few broad answers. No names, email
  addresses, student IDs, or unnecessary demographic detail. Allow "prefer not to
  say".
- **Texts stay outside the repository** until the collection freeze, and are then
  committed together.
- **Withdrawal:** possible until the volunteer's text is committed. After that,
  removal from a public repository or its history cannot be guaranteed, and the
  consent statement must say so.
- **Reminder:** before the commit, each volunteer gets a reminder, and the commit
  waits **3 days from the moment it is sent**. Volunteers are asked to confirm.
- **Silence:** a volunteer who does not reply has their text committed after the
  3 days, and the consent statement says this in plain words.
- **Thread destruction:** each consent thread is deleted when the window closes,
  at the commit. After that only the manifest line remains: label, consent date
  and method.
- The consent statement must also say: who may read the texts (me, and course
  staff once submitted), whether any text is ever shown to an AI assistant, that
  volunteers keep their copyright and allow use in the repository, that the text
  must be fresh and written without AI help, that saying no has no consequence,
  and that volunteers are adults.

## AI-generated writing (proposed defaults)

| Item | Proposed default |
|---|---|
| Models | At least 3 different models from at least 2 providers, each recorded with name, version, platform and date |
| Cap per model | No single model supplies more than 40% of the AI texts |
| Prompt styles | At least 4: neutral essay, student voice, casual, and "vary your sentence lengths" |
| Cap per prompt style | No single prompt style supplies more than 35% of the AI texts |
| Number of AI texts | Between 0.8 and 1.25 times the number of human texts |
| `gpt2` (the detector's own model) | Not in the main AI group. May be added only as a separately labeled subgroup |
| Provenance | Verbatim prompt, visible settings, whether the first output or one of several was used, and whether it was edited |

## Topic, genre and length coverage (proposed defaults)

| Item | Proposed default |
|---|---|
| Topics | At least 5 distinct topics, none more than 30% of a group |
| Genres | At least 3 (personal narrative, explanation or essay, informal message or opinion), none more than 50% of a group |
| Length | All texts 80 to 300 words, and each of the bands 80 to 150, 151 to 220 and 221 to 300 holds at least 20% of a group |

## Preserving the data

- Every text is saved exactly as received, in `texts/`, and never edited. A
  SHA-256 hash of each file is recorded in the manifest.
- Any cleanup is a **separate file** with a change log. Texts are never silently
  changed.
- A text that carries a volunteer's personal detail by accident may need to stay
  out of the repository, and that exception is documented.

## Freeze process

- **Collection freeze (approved concept, proposed mechanics):** when the minimum
  is met and the reminders and the 3-day wait are done, the set is committed as
  one version and tagged `reference-v1`. After that nothing is added to or edited
  in that version.
- **Evaluation freeze (approved concept, proposed mechanics):** the analysis
  configuration (statistics, percentile rule, scripts) is saved and committed
  **before** the final evaluation on `test_set/` is run.
- A later change creates a **new version** (`reference-v2`) with a changelog.
  The frozen version is never modified silently.

## Analysis (proposed defaults)

1. **Composition report first,** before any analysis: overall counts, and counts
   per writer, model, prompt style, topic, genre, length band and provenance
   basis. The report states that a set balanced on purpose does **not** represent
   real submissions.
2. Compute the three raw measures (spread, type-token ratio on the first 75
   words, punctuation density) for every text with a committed script.
3. Describe each measure's distribution for human and AI separately, and by
   subgroup, with extra attention to plain writers.
4. **Candidate limits:** the 5th and 95th percentiles of the pooled reference
   values, per measure, as the pre-set primary rule. The 10th and 90th
   percentiles, and the observed minimum and maximum, are reported only to show
   how sensitive the result is. The observed minimum and maximum are **not**
   adopted automatically.
5. Report saturation (the share of texts at exactly 0 or 1) and a split-half
   stability check: choose on one half, check on the other.
6. Re-check whether each measure's direction (higher means more AI-like) holds on
   the larger set. If it does not, that is my decision to make, not something the
   code should hide.
7. The final limits are my decision, with a written reason for each citing the
   reference-set statistics.

## Still undecided (these need data first)

- The actual normalization limits for each measure.
- The neutral value used when a measure has too little text to work with.
- `style_signal` itself (the plain average of the three normalized measures).

## Already approved and recorded elsewhere

- N = 75 for the type-token ratio, in `calibration/manifest.md`.
