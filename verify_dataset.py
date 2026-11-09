#!/usr/bin/env python3
"""
Check the test set hasn't changed since you froze it.  <- UNIT 8, MILESTONE 3

    python verify_dataset.py                 # check — changes nothing
    python verify_dataset.py --write-hashes  # record hashes for new files

`criteria.md` says the 20 samples are written down before the first trial and
that none is added, removed or edited once a trial has started. Nothing enforces
that by itself: a file edited between trial 2 and trial 3 looks exactly like a
file that wasn't. A hash recorded up front is what turns that rule into
something you can check, so run the plain command before every trial.

Hashing is SHA-256 over the file's text as UTF-8, with CRLF and CR line endings
normalised to LF first. Git rewrites line endings on Windows checkouts, so
hashing raw bytes would report a file as edited when only the checkout changed.

**Verifying never writes.** Recording a hash is a separate command you have to
ask for, and even then it will not quietly replace a hash that is already there
— a changed file is the thing this script exists to notice, not to paper over.

Three outcomes, and they are not the same thing:

    VERIFIED    every sample is present and matches its recorded hash
    INCOMPLETE  the set isn't finished yet, so nothing is being claimed
    FAILED      something is present and wrong — a mismatch, a duplicate, a
                bad label, a malformed row
"""

import argparse
import csv
import hashlib
import sys
from pathlib import Path

import config
import stylometry

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass


# ── The shape of the set, from criteria.md ───────────────────────────────────

EXPECTED_IDS = ([f"H{i:02d}" for i in range(1, 11)]
                + [f"A{i:02d}" for i in range(1, 6)]
                + [f"B{i:02d}" for i in range(1, 6)])
EXPECTED_LABEL = {"H": "human", "A": "ai", "B": "unsure"}
VALID_LABELS = ("ai", "human", "unsure")

MIN_WORDS, MAX_WORDS = 80, 300          # criteria.md: every sample, 80-300 words
PLAIN_MAX_AVG_SENTENCE = 3.0            # criteria.md: plain is <= 3 words a sentence
MIN_PLAIN_H = 4                         # criteria.md: at least 4 of the 10 H samples

COLUMNS = ["id", "group", "file", "word_count", "expected_guess", "sha256",
           "avg_sentence_length", "plain", "ai_tool", "ai_model", "prompt",
           "generated_on", "settings", "attempt", "edited"]

VERIFIED, INCOMPLETE, FAILED = "VERIFIED", "INCOMPLETE", "FAILED"


# ── Hashing ──────────────────────────────────────────────────────────────────

def normalised_text(path: Path) -> str:
    """The file's text with CRLF and lone CR turned into LF."""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(normalised_text(path).encode("utf-8")).hexdigest()


def measure(path: Path):
    """word_count, avg_sentence_length and plain, by criteria.md's own rule."""
    text = normalised_text(path)
    words = len(stylometry.words(text))
    sentences = len(stylometry.sentences(text))
    if sentences == 0:
        return words, None, None
    average = words / sentences
    return words, round(average, 2), "yes" if average <= PLAIN_MAX_AVG_SENTENCE else "no"


# ── Reading the manifest ─────────────────────────────────────────────────────

def read_manifest(path: Path):
    """Rows as written, plus everything structurally wrong with them."""
    problems = []
    if not path.exists():
        return [], [], [f"No manifest at {path}"]

    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = []
        for line, row in enumerate(reader, 2):
            if None in row and row[None]:
                problems.append(f"line {line}: more fields than the header has")
            missing = [c for c in COLUMNS if c in fieldnames and row.get(c) is None]
            if missing:
                problems.append(f"line {line}: fewer fields than the header has "
                                f"(no value for {', '.join(missing)})")
            row.pop(None, None)
            row["_line"] = line
            rows.append(row)

    for column in COLUMNS:
        if column not in fieldnames:
            problems.append(f"the manifest has no `{column}` column")

    seen_ids, seen_files = {}, {}
    for row in rows:
        sample = (row.get("id") or "").strip()
        if not sample:
            problems.append(f"line {row['_line']}: no id")
            continue
        if sample in seen_ids:
            problems.append(f"line {row['_line']}: id '{sample}' already used on "
                            f"line {seen_ids[sample]}")
        else:
            seen_ids[sample] = row["_line"]

        filename = (row.get("file") or "").strip()
        if filename:
            if filename in seen_files:
                problems.append(f"line {row['_line']}: file '{filename}' already used "
                                f"on line {seen_files[filename]}")
            else:
                seen_files[filename] = row["_line"]

    return rows, fieldnames, problems


# ── Verifying ────────────────────────────────────────────────────────────────

class Check:
    def __init__(self, sample):
        self.sample = sample
        self.state = ""      # ok / missing / mismatch / error
        self.detail = ""


def verify(folder: Path):
    """Returns (verdict, checks, problems). Writes nothing, ever."""
    manifest_path = folder / "manifest.csv"
    rows, _, problems = read_manifest(manifest_path)
    by_id = {}
    for row in rows:
        sample = (row.get("id") or "").strip()
        if sample and sample not in by_id:
            by_id[sample] = row

    for sample in by_id:
        if sample not in EXPECTED_IDS:
            problems.append(f"'{sample}' is not one of the 20 ids criteria.md names")

    checks, plain_h, present_h = [], 0, 0

    for sample in EXPECTED_IDS:
        check = Check(sample)
        checks.append(check)
        row = by_id.get(sample)
        if row is None:
            check.state = "missing"
            check.detail = "no row in the manifest"
            continue

        group = (row.get("group") or "").strip().upper()
        if group != sample[0]:
            check.state = "error"
            check.detail = f"group is '{group}', expected '{sample[0]}'"
            continue

        label = (row.get("expected_guess") or "").strip().lower()
        if label not in VALID_LABELS:
            check.state = "error"
            check.detail = (f"expected_guess is '{label or '(blank)'}' — "
                            f"it must be ai, human or unsure")
            continue
        if label != EXPECTED_LABEL[group]:
            check.state = "error"
            check.detail = (f"expected_guess is '{label}', but group {group} "
                            f"samples are '{EXPECTED_LABEL[group]}'")
            continue

        filename = (row.get("file") or "").strip()
        if not filename:
            check.state = "missing"
            check.detail = "no file named in the manifest"
            continue

        path = folder / filename
        if not path.exists():
            check.state = "missing"
            check.detail = f"{filename} does not exist"
            continue

        recorded = (row.get("sha256") or "").strip().lower()
        try:
            actual = sha256_of(path)
            words, average, plain = measure(path)
        except (UnicodeDecodeError, OSError) as exc:
            check.state = "error"
            check.detail = f"{filename} could not be read as UTF-8 text ({exc})"
            continue

        if not recorded:
            check.state = "missing"
            check.detail = (f"{filename} exists but has no recorded hash — "
                            f"run --write-hashes")
            continue

        if recorded != actual:
            check.state = "mismatch"
            check.detail = (f"{filename} has changed since its hash was recorded "
                            f"(recorded {recorded[:12]}…, now {actual[:12]}…)")
            continue

        check.state = "ok"
        check.detail = f"{words} words"

        if not MIN_WORDS <= words <= MAX_WORDS:
            check.state = "error"
            check.detail = (f"{words} words — criteria.md says every sample is "
                            f"{MIN_WORDS}-{MAX_WORDS}")
            continue

        if group == "H":
            present_h += 1
            if plain == "yes":
                plain_h += 1
            recorded_plain = (row.get("plain") or "").strip().lower()
            if recorded_plain and recorded_plain != plain:
                check.state = "error"
                check.detail = (f"manifest says plain='{recorded_plain}', but the "
                                f"file averages {average} words a sentence")

    if present_h == 10 and plain_h < MIN_PLAIN_H:
        problems.append(f"only {plain_h} of the 10 H samples are plain — "
                        f"criteria.md asks for at least {MIN_PLAIN_H}")

    failed = [c for c in checks if c.state in ("mismatch", "error")]
    missing = [c for c in checks if c.state == "missing"]

    if failed or problems:
        verdict = FAILED if failed else INCOMPLETE
        # A structural problem with files present is a failure; with the set
        # unfinished it is just more of what is unfinished.
        if problems and not failed and not missing:
            verdict = FAILED
    elif missing:
        verdict = INCOMPLETE
    else:
        verdict = VERIFIED
    return verdict, checks, problems


# ── Recording hashes, only when asked ────────────────────────────────────────

def write_hashes(folder: Path, force: bool):
    manifest_path = folder / "manifest.csv"
    rows, fieldnames, problems = read_manifest(manifest_path)
    if problems:
        print("The manifest has problems. Fix these before recording hashes:\n",
              file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    written, skipped, refused = [], [], []
    for row in rows:
        sample = (row.get("id") or "").strip()
        filename = (row.get("file") or "").strip()
        path = folder / filename if filename else None
        if not path or not path.exists():
            skipped.append(f"{sample}: no file yet")
            continue

        actual = sha256_of(path)
        recorded = (row.get("sha256") or "").strip().lower()
        if recorded and recorded != actual and not force:
            refused.append(f"{sample}: {filename} no longer matches its recorded hash. "
                           f"If you meant to change it, say so with --force")
            continue
        if recorded == actual:
            skipped.append(f"{sample}: already recorded and unchanged")
            continue

        words, average, plain = measure(path)
        row["sha256"] = actual
        row["word_count"] = str(words)
        if (row.get("group") or "").strip().upper() == "H":
            row["avg_sentence_length"] = "" if average is None else str(average)
            row["plain"] = plain or ""
        written.append(f"{sample}: {filename} ({words} words)")

    if refused and not force:
        print("Refused to replace a recorded hash:\n", file=sys.stderr)
        for note in refused:
            print(f"  - {note}", file=sys.stderr)
        print("\nNothing was written.", file=sys.stderr)
        return 1

    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames or COLUMNS)
        writer.writeheader()
        for row in rows:
            row.pop("_line", None)
            writer.writerow(row)

    for note in written:
        print(f"  recorded  {note}")
    for note in skipped:
        print(f"  skipped   {note}")
    print(f"\n{len(written)} hash(es) recorded, {len(skipped)} skipped.")
    if written:
        print("Check it before you rely on it:  python verify_dataset.py")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--set", dest="folder", default=str(config.ROOT / "test_set"),
                        help="the dataset folder (default: test_set)")
    parser.add_argument("--write-hashes", action="store_true",
                        help="record a hash for every file that doesn't have one")
    parser.add_argument("--force", action="store_true",
                        help="with --write-hashes: replace a hash whose file changed")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"No dataset folder at {folder}.", file=sys.stderr)
        return 1

    if args.write_hashes:
        return write_hashes(folder, args.force)

    verdict, checks, problems = verify(folder)

    for check in checks:
        mark = {"ok": "ok      ", "missing": "missing ",
                "mismatch": "CHANGED ", "error": "ERROR   "}[check.state]
        print(f"  {mark}{check.sample}  {check.detail}")

    if problems:
        print("\nProblems with the manifest:")
        for problem in problems:
            print(f"  - {problem}")

    counts = {state: sum(1 for c in checks if c.state == state)
              for state in ("ok", "missing", "mismatch", "error")}
    print(f"\n{counts['ok']} verified, {counts['missing']} not there yet, "
          f"{counts['mismatch']} changed, {counts['error']} wrong")
    print(f"\n{verdict}")

    if verdict == INCOMPLETE:
        print("The set isn't finished, so this is not a pass. See test_set/README.md.")
    elif verdict == FAILED:
        print("Something present is wrong. A CHANGED file after a trial has started "
              "breaks the rule the set exists to enforce.")
    else:
        print(f"All {len(EXPECTED_IDS)} samples match the hashes recorded for them.")

    return {VERIFIED: 0, FAILED: 1, INCOMPLETE: 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
