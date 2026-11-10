#!/usr/bin/env python3
"""
Unit tests for the stylometry raw-feature layer.  <- MILESTONE 5, T5.1

    python test_stylometry.py

Plain asserts, no test framework beyond the standard library, matching
`test.py`'s own style and this project's zero-new-dependency rule.

These tests check `sentences`, `words`, the three raw measures, and
`raw_features`. They do not touch `style_signal`, which stays a stub until
normalization is decided from the reference set, and nothing here chooses or
implies a normalization bound, a neutral value, a weight or a threshold.
"""

import sys

import stylometry as s

passed = []
failed = []


def check(label, condition, detail=""):
    if condition:
        passed.append(label)
        print(f"[ok]   {label}")
    else:
        failed.append(label)
        print(f"[FAIL] {label}" + (f" — {detail}" if detail else ""))


def same(a, b):
    """Equality that treats two NaN-free floats, None, and exact values alike."""
    return a == b


# ── sentences() / words() ────────────────────────────────────────────────────

check("sentences() splits on . ! ?",
      s.sentences("One sentence. Another! A third?") == ["One sentence.", "Another!", "A third?"])
check("sentences() drops empty pieces from extra whitespace",
      s.sentences("One.   Two.") == ["One.", "Two."])
check("words() lowercases and strips punctuation",
      s.words("Hello, WORLD! It's fine-ish.") == ["hello", "world", "it's", "fine", "ish"])
check("words() on text with no letters/digits returns an empty list",
      s.words("... !!! ???") == [])

# ── sentence_length_spread ───────────────────────────────────────────────────

# Hand-computed: sentence word counts [2, 2, 2, 2] -> stdev 0, mean 2 -> 0.0
uniform = "One two. One two. One two. One two."
check("sentence_length_spread: four equal-length sentences -> 0.0 (no spread)",
      same(s.sentence_length_spread(uniform), 0.0))

# Hand-computed: counts [1, 5] -> mean 3, stdev (sample) = sqrt(((1-3)**2+(5-3)**2)/1) = sqrt(8)
import math, statistics  # noqa: E402
mixed = "Go. One two three four five."
expected = statistics.stdev([1, 5]) / statistics.mean([1, 5])
check("sentence_length_spread: a 1-word and a 5-word sentence matches hand calculation",
      same(round(s.sentence_length_spread(mixed), 10), round(expected, 10)),
      f"got {s.sentence_length_spread(mixed)}, expected {expected}")

check("sentence_length_spread: one sentence -> None (stdev needs two values)",
      s.sentence_length_spread("Only one sentence here.") is None)
check("sentence_length_spread: empty text -> None",
      s.sentence_length_spread("") is None)
check("sentence_length_spread: whitespace-only text -> None",
      s.sentence_length_spread("   \n\t  ") is None)
check("sentence_length_spread: two sentences with zero mean words/sentence -> None",
      s.sentence_length_spread(". . .") is None)

# ── type_token_ratio ──────────────────────────────────────────────────────────

# "the cat sat on the mat" -> 6 words, 5 unique (the repeats) -> 5/6
check("type_token_ratio: whole text, hand-computed ratio",
      same(s.type_token_ratio("the cat sat on the mat"), 5 / 6))
check("type_token_ratio: no words at all -> 0.0",
      same(s.type_token_ratio("..."), 0.0))
check("type_token_ratio: empty text -> 0.0",
      same(s.type_token_ratio(""), 0.0))
check("type_token_ratio: whitespace-only text -> 0.0",
      same(s.type_token_ratio("   "), 0.0))

five_words = "alpha beta gamma delta alpha"  # 5 tokens, 4 unique
check("type_token_ratio: n_words slice, text shorter than N -> None",
      s.type_token_ratio(five_words, n_words=10) is None)
check("type_token_ratio: n_words slice, text exactly N long -> a value, not None",
      s.type_token_ratio(five_words, n_words=5) == 4 / 5)
check("type_token_ratio: n_words slice only uses the first N words",
      same(s.type_token_ratio("alpha beta alpha gamma gamma gamma", n_words=3), 2 / 3),
      "first 3 words are alpha,beta,alpha -> 2 unique of 3")
check("type_token_ratio: extra words past N don't change the result",
      s.type_token_ratio("alpha beta alpha gamma gamma gamma", n_words=3)
      == s.type_token_ratio("alpha beta alpha zzz zzz zzz zzz zzz zzz zzz", n_words=3))

# ── punctuation_density ──────────────────────────────────────────────────────

# "a, b; c: d (e) [f] {g}" -> 7 words (a..g); marks , ; : ( ) [ ] { } = 9 -> 9/7
dense = "a, b; c: d (e) [f] {g}"
check("punctuation_density: counted marks over word count, hand-computed",
      same(s.punctuation_density(dense), 9 / 7), f"got {s.punctuation_density(dense)}")
check("punctuation_density: full stops are not counted",
      same(s.punctuation_density("One. Two. Three."), 0.0))
check("punctuation_density: question and exclamation marks are not counted",
      same(s.punctuation_density("What? Really! No."), 0.0))
check("punctuation_density: a hyphen inside a word is not counted",
      same(s.punctuation_density("a well-known fact"), 0.0))
check("punctuation_density: an apostrophe in a contraction is not counted",
      same(s.punctuation_density("it's fine, don't worry"), 1 / 4),
      "only the one comma counts; 4 words: it's, fine, don't, worry")
check("punctuation_density: no words at all -> 0.0",
      same(s.punctuation_density("!!! ..."), 0.0))
check("punctuation_density: empty text -> 0.0",
      same(s.punctuation_density(""), 0.0))

# ── invalid input: every public function fails predictably, not with an AttributeError ──

for fn in (s.sentences, s.words, s.sentence_length_spread, s.type_token_ratio,
          s.punctuation_density, s.raw_features):
    for bad in (None, 123, 1.5, [], {}, ("a",)):
        try:
            fn(bad)
            check(f"{fn.__name__}({bad!r}) raises TypeError", False, "did not raise")
        except TypeError:
            check(f"{fn.__name__}({bad!r}) raises TypeError", True)
        except Exception as exc:  # noqa: BLE001
            check(f"{fn.__name__}({bad!r}) raises TypeError", False,
                  f"raised {type(exc).__name__} instead")

# ── raw_features() ───────────────────────────────────────────────────────────

sample = "The cat sat on the mat. It did not move for a very long time indeed."
features = s.raw_features(sample)
check("raw_features() returns exactly the three documented keys",
      set(features) == {"sentence_length_spread", "type_token_ratio", "punctuation_density"})
check("raw_features()['sentence_length_spread'] matches calling the function directly",
      same(features["sentence_length_spread"], s.sentence_length_spread(sample)))
check("raw_features()['type_token_ratio'] matches the whole-text ratio (n_words=None)",
      same(features["type_token_ratio"], s.type_token_ratio(sample)))
check("raw_features()['punctuation_density'] matches calling the function directly",
      same(features["punctuation_density"], s.punctuation_density(sample)))
check("raw_features() on empty text returns the documented empty-text values",
      s.raw_features("") == {"sentence_length_spread": None, "type_token_ratio": 0.0,
                             "punctuation_density": 0.0})

# ── determinism: repeated calls on identical input give identical results ───

for label, text in (
    ("a normal multi-sentence text", sample),
    ("empty text", ""),
    ("whitespace-only text", "   \t\n  "),
    ("a single short word", "hi"),
    ("the zero-mean-sentences edge case", ". . ."),
    ("text with every counted punctuation mark", dense),
):
    first = (s.sentence_length_spread(text), s.type_token_ratio(text),
             s.punctuation_density(text), s.raw_features(text))
    second = (s.sentence_length_spread(text), s.type_token_ratio(text),
              s.punctuation_density(text), s.raw_features(text))
    third = s.raw_features(text)
    check(f"determinism: three calls agree exactly for {label!r}",
          first == second and second[3] == third,
          f"{first} vs {second} vs {third}")

print(f"\n{len(passed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
