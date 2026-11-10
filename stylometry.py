"""
Signal two: the style signal.

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three raw measures are implemented below (Milestone 5, T5.1):

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

`raw_features()` bundles all three. They are **raw, uncalibrated numbers** —
not a validated indicator of AI authorship on their own. Turning them into a
single 0–1 signal needs normalization bounds, a neutral value and a combining
rule, none of which exist yet; that is `style_signal()` below, still a stub,
and deliberately not wired into `/submit`.

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one. This is this
project's working hypothesis, not something the four calibration texts (see
`calibration/manifest.md`) were large enough to confirm.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Call a function on its own from a terminal to see what it does:

    python stylometry.py "some text to look at"

Automated checks live in `test_stylometry.py`:

    python test_stylometry.py
"""

import re
import statistics


def _require_text(text) -> None:
    """
    Fail predictably on non-string input, instead of an AttributeError from
    deep inside a regex or a .lower() call on whatever `text` actually is.

    `app.py::submit` already rejects non-string text before anything in this
    module runs, so in the deployed path this never fires — it's a second,
    independent guard so these functions are safe to call directly too, for
    example from a test or from a future calibration script.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    _require_text(text)
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    _require_text(text)
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

#
# Raw measures only. Normalizing them onto 0–1, choosing N, and the neutral value
# for "not enough text" are decided after inspecting real raw values. Until
# then a measure that has some text but too little to work with returns None,
# meaning "no information". Text with no words at all is a separate case:
# type_token_ratio and punctuation_density return 0.0 for it.
#
# Direction, for all three: a HIGHER raw value means MORE AI-LIKE. That is the
# author's own hypothesis, and for the first two it is the opposite of the
# usual one. It is provisional until tested on the calibration inputs.

# The marks punctuation_density counts. Sentence-ending marks (. ? !), hyphens
# inside words and apostrophes in contractions are deliberately NOT counted.
PUNCTUATION_MARKS = frozenset(",;:—–()[]{}")


def sentence_length_spread(text: str) -> float | None:
    """
    How much sentence length varies, as a coefficient of variation.

    Sentence length is the number of `words()` in each sentence from
    `sentences()`. The measure is the standard deviation of those lengths
    (`statistics.stdev`, the sample version) divided by their mean, so a long
    text and a short one are comparable. Higher means more varied lengths,
    which this project reads as more AI-like.

    Returns None when there is not enough to measure: fewer than two sentences
    (stdev needs two values) or a mean of zero words per sentence.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    if len(lengths) < 2:
        return None

    mean = statistics.mean(lengths)
    if mean == 0:
        return None

    return statistics.stdev(lengths) / mean


def type_token_ratio(text: str, n_words: int | None = None) -> float | None:
    """
    Unique words over total words, between 0 and 1. Higher means more varied
    vocabulary, which this project reads as more AI-like.

    This ratio falls as text gets longer, because common words repeat. So the
    plan is to measure it on a fixed-size slice: the first `n_words` words.

        n_words=None   use every word (raw value, for inspection only)
        n_words=N      use the first N words

    Returns 0.0 when the text has no words at all. Returns None when there is
    some text but not enough to measure: fewer than `n_words` words when a slice
    length is given.
    """
    tokens = words(text)
    if not tokens:
        return 0.0

    if n_words is not None:
        if len(tokens) < n_words:
            return None
        tokens = tokens[:n_words]

    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    Selected punctuation marks per word. Higher means more punctuation, which
    this project reads as more AI-like.

    Counted: commas, semicolons, colons, em dashes, en dashes, square brackets,
    curly braces and parentheses (see PUNCTUATION_MARKS). Not counted: full
    stops, question marks, exclamation marks, hyphens inside words,
    apostrophes.

    The denominator is the number of `words()`. Text with no words returns 0.0.
    """
    word_count = len(words(text))
    if word_count == 0:
        return 0.0

    marks = sum(1 for ch in text if ch in PUNCTUATION_MARKS)
    return marks / word_count


# ── Raw feature extraction, bundled ──────────────────────────────────────────
#
# This is the boundary T5.1 draws: everything above and this function compute
# raw numbers only, deterministically, from the text alone. Nothing here picks
# normalization bounds, a neutral value, weights or thresholds — that is
# `style_signal()`, below, which stays a stub until those are decided from the
# reference set (see REFERENCE_SET_PLAN.md).

def raw_features(text: str) -> dict:
    """
    All three raw measures for one text, as a dict:

        {"sentence_length_spread": ..., "type_token_ratio": ..., "punctuation_density": ...}

    Each value is exactly what calling that measure directly would return —
    `type_token_ratio` here uses the whole text (`n_words=None`), since the
    first-75-word slice is a normalization-stage decision (see
    `calibration/manifest.md`), not a raw measurement.

    These numbers are **not a validated signal**. They are the uncalibrated
    inputs `style_signal()` will eventually normalize and combine. Do not read
    a particular value here as evidence of AI or human authorship on its own.

    Raises TypeError if `text` is not a string. Safe on empty, whitespace-only
    and very short text — each measure returns its own documented `None` or
    `0.0` rather than raising.
    """
    _require_text(text)
    return {
        "sentence_length_spread": sentence_length_spread(text),
        "type_token_ratio": type_token_ratio(text),
        "punctuation_density": punctuation_density(text),
    }


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.
    """
    # TODO: replace this
    return 0.5


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI, "
          f"still a stub)")
    print("\nThe three measures above are real and deterministic. style_signal is "
          "still fixed\nat 0.5 — normalization and combining are a later step.")
