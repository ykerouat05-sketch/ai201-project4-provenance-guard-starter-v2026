# Calibration inputs

Four texts used to inspect the raw style measures and to choose the
normalization limits, the fixed-slice length N and the neutral value in
`stylometry.py` (Milestone 4).

**These are not test samples.** They are kept apart from `test_set/` on purpose.
Choosing limits from the same texts the Milestone 2 criteria are later measured
on would tune the system to its own test.

Topic for all four: everyday university life and student learning.
Length for all four: 80–300 words.

| File | Role | Written by | Source | Editing history | Status |
|---|---|---|---|---|---|
| `human_clear.txt` | Clearly human writing | Me (the project author) | Written by me, by hand, in VS Code | None | Saved, 110 words |
| `human_plain.txt` | Plain, conventional human writing | Me (the project author) | Written by me, by hand, in VS Code | None | Saved, 86 words |
| `ai_clear.txt` | Clearly AI-generated writing | AI assistant (Claude Code) | AI model: Claude Sonnet 5.5 (`claude-sonnet-5-5`), run inside Claude Code. Prompt: see below. Date: 2026-11-03 | None. Saved exactly as generated, 141 words | Drafted, awaiting my review |
| `ai_edited.txt` | Lightly edited AI writing | AI assistant, based on `ai_clear.txt` | Derived from `ai_clear.txt` by the same assistant on 2026-11-03. Not a separate generation | Six edits, listed below. 128 words | Drafted, awaiting my review |

### Generation prompt for `ai_clear.txt`

The exact instruction given to the assistant, from the project author's
message:

> draft sample #1 (clearly AI) and sample #4 (lightly edited version of sample
> #1). Use the topic of everyday university life and student learning. Keep each
> sample between 80 and 300 words.

No other settings were used or are visible to the assistant. The text was
written in one attempt and not selected from several.

### Edits from `ai_clear.txt` to `ai_edited.txt`

Sentence count is 8 in both files. Only these six sentences differ:

1. Sentence 1: "presents students with a wide range of opportunities and challenges" was
   changed to "gives students plenty of chances and challenges".
2. Sentence 2: removed "It is important to note that" and capitalised
   "Effective".
3. Sentence 3: "significantly enhance" was changed to "really improve".
4. Sentence 4: "Furthermore, collaboration with peers offers numerous benefits." was
   changed to "Working with classmates offers many benefits."
5. Sentence 6: "In addition," was changed to "Also,".
6. Sentence 7 ("Ultimately, …"): "a fulfilling university experience" was
   changed to "enjoying university".

## Style-signal design decisions made using these inputs

### Approved: N = 75 for the type-token ratio

The type-token ratio is measured on the **first 75 words** of a text
(`stylometry.type_token_ratio(text, n_words=75)`). Text with fewer than 75 words
gets the neutral value, which is not yet decided.

My reasons, in my own words:

- The intended valid input is 80–300 words.
- N = 75 lets every submission that meets the 80-word minimum get a measurement.
- It uses a longer, more informative slice than N = 25, 40 or 50.
- N = 85 would make valid 80-word submissions return no measurement.
- I chose N from the intended input range and measurement consistency, **not**
  because it separates the four calibration texts best.

Limits worth remembering: the four calibration texts are too few to justify any
N from their own values, and the ratio's ordering of them changed with N.

### Still undecided

- The low and high limits that normalize each raw measure onto 0–1.
- The neutral value used when there is too little text to measure.
- `style_signal` itself (the plain average of the three normalized measures).

### Exploratory status

The raw measurements on these four inputs are exploratory. They do not show that
higher values reliably mean more AI-like writing.

## Notes

- Each file is plain text, one document per file, with no title or header line.
- Word counts and measured values are recorded in the style-signal inspection
  step, not here.
- Fill in the AI model, prompt, date and edit list at the moment each AI file
  is created, and do not change them afterwards.
