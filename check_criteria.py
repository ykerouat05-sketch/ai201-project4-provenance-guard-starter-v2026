#!/usr/bin/env python3
"""
Check the five criteria in `criteria.md` against real evidence.  <- UNIT 8, MILESTONE 3

`run_eval.py` sends the samples and records what came back. It does not decide
whether a trial passed. This does that arithmetic, and only that: every number
below is quoted from `criteria.md`, and changing one here does not change the
criterion — it only makes this script disagree with it.

Criteria 1-3 are measured from an evaluation run plus the audit log:

    python run_eval.py --label before
    python check_criteria.py --run results/run_<date>_before.md

Criteria 4 and 5 are about requests `run_eval.py` cannot send — an appeal needs
a content_id that only exists after a submission, and a bad-input case needs a
body that isn't a JSON object at all. This script sends those itself, against a
service you started, and writes the evidence next to the run:

    python app.py                                    # one terminal
    python check_criteria.py --appeals               # another
    python check_criteria.py --bad-input
    python check_criteria.py --run results/run_<date>_before.md \
        --appeal-evidence results/appeals_<date>.json \
        --bad-input-evidence results/bad_input_<date>.json

A criterion whose evidence is missing comes back NOT EVALUATED. It never comes
back PASS — a target you did not measure is not a target you met.

This script never writes to the audit log and never changes an entry. The
service writes its own log when these checks send it requests, which is the
point of criteria 4 and 5.

⚠️ Reports from here carry sample ids and scores, never submitted writing.
"""

import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

import config

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass


# ── The numbers, straight out of criteria.md ─────────────────────────────────

MAX_FALSE_POSITIVES = 3       # 1: at most 3 of the 10 H samples may get "ai"
MIN_MEAN_GAP = 0.30           # 2: mean(A combined) - mean(H combined)
MIN_AI_ABOVE_HUMAN_MEAN = 2   # 2: at least 2 of the 5 A samples above mean(H)
MIN_PER_LABEL = 5             # 3: per label, samples expected AND given it
VALID_APPEALS = 3             # 4: 3 of 3 valid appeals
MAX_TEXT_CHARS = config.MAX_TEXT_CHARS   # 5: row 5, the 413 boundary

PASS, FAIL, NOT_EVALUATED = "PASS", "FAIL", "NOT EVALUATED"


class Result:
    """One criterion's verdict, with the arithmetic that produced it."""

    def __init__(self, number, name, required):
        self.number = number
        self.name = name
        self.required = required
        self.calculation = []
        self.observed = []
        self.verdict = NOT_EVALUATED
        self.notes = []

    def decide(self, passed):
        self.verdict = PASS if passed else FAIL
        return self

    def unevaluated(self, why):
        self.verdict = NOT_EVALUATED
        self.notes.append(why)
        return self


# ── Reading the evidence ─────────────────────────────────────────────────────

def load_manifest(path: Path):
    """
    {sample_id: {"group": "H", "expected_guess": "human"}} from test_set/manifest.csv.

    criteria.md fixes expected_guess before the first trial, so it is read here
    and never inferred from what came back.
    """
    samples = {}
    problems = []
    if not path.exists():
        return samples, [f"No manifest at {path}"]

    with path.open(encoding="utf-8-sig", newline="") as f:
        for n, row in enumerate(csv.DictReader(f), 2):
            sample = (row.get("id") or "").strip()
            if not sample:
                problems.append(f"{path.name} line {n}: no id")
                continue
            if sample in samples:
                problems.append(f"{path.name} line {n}: '{sample}' appears twice")
                continue
            expected = (row.get("expected_guess") or "").strip().lower()
            if expected not in ("ai", "human", "unsure"):
                problems.append(
                    f"{path.name} line {n}: '{sample}' has expected_guess "
                    f"'{expected or '(blank)'}' — it must be ai, human or unsure")
            samples[sample] = {
                "group": (row.get("group") or "").strip().upper(),
                "expected_guess": expected,
            }
    return samples, problems


SCENARIO_HEADING = re.compile(r"^### (.+)$", re.M)
JSON_BLOCK = re.compile(r"```json\n(.*?)\n```", re.S)


def load_run(path: Path):
    """
    The trials out of a run_eval.py report: [[record, ...], ...], one list per trial.

    The report is what gets committed, so it is also what gets checked — rather
    than a second file that could drift away from the evidence you submitted.
    """
    if not path.exists():
        return [], [f"No run report at {path}"]

    text = path.read_text(encoding="utf-8")
    headings = list(SCENARIO_HEADING.finditer(text))
    if not headings:
        return [], [f"{path.name} has no '### <scenario>' sections — is it a run_eval report?"]

    trials, problems = [], []
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        for n, block in enumerate(JSON_BLOCK.finditer(text[heading.start():end]), 1):
            try:
                records = json.loads(block.group(1))
            except json.JSONDecodeError as exc:
                problems.append(f"{path.name}: trial {n} of '{heading.group(1)}' won't parse ({exc})")
                continue
            if not isinstance(records, list):
                problems.append(f"{path.name}: trial {n} of '{heading.group(1)}' isn't a list")
                continue
            while len(trials) < n:
                trials.append([])
            trials[n - 1].extend(records)
    return trials, problems


def load_audit(path: Path):
    """Every audit entry, oldest first. Read-only — nothing here writes."""
    if not path.exists():
        return [], [f"No audit log at {path}"]
    entries, problems = [], []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            problems.append(f"{path.name} line {n} won't parse — skipped")
    return entries, problems


def decisions_by_content_id(entries):
    """
    {content_id: [decision entry, ...]} — a list, so duplicates stay visible.

    A decision carries no `event` key; appeals and rejections do. Matching is by
    content_id alone, never by position, because the log holds every request the
    service ever handled and an evaluation run is a few rows in the middle of it.
    """
    index = {}
    for entry in entries:
        if "event" in entry:
            continue
        content_id = entry.get("content_id")
        if isinstance(content_id, str):
            index.setdefault(content_id, []).append(entry)
    return index


def combined_scores(records, index):
    """
    {sample_id: combined_score} for one trial, plus what could not be matched.

    criteria.md says the combined score comes from the log, matched by the
    content_id the response returned. Anything that cannot be matched exactly
    once is reported rather than guessed at.
    """
    scores, missing, duplicated = {}, [], []
    for record in records:
        sample = record.get("sample")
        content_id = record.get("content_id")
        if not content_id:
            missing.append(f"{sample} (no content_id in the response)")
            continue
        matches = index.get(content_id, [])
        if not matches:
            missing.append(f"{sample} ({content_id[:8]}… not in the log)")
            continue
        if len(matches) > 1:
            duplicated.append(f"{sample} ({content_id[:8]}… has {len(matches)} decision entries)")
            continue
        score = matches[0].get("combined_score")
        if not isinstance(score, (int, float)):
            missing.append(f"{sample} (combined_score is {score!r} in the log)")
            continue
        scores[sample] = float(score)
    return scores, missing, duplicated


def guesses(records):
    """{sample_id: guess} for one trial, and the samples that got no guess."""
    found, unanswered = {}, []
    for record in records:
        sample = record.get("sample")
        guess = record.get("guess")
        if isinstance(guess, str) and guess:
            found[sample] = guess
        else:
            unanswered.append(f"{sample} (status {record.get('status')})")
    return found, unanswered


def group_ids(manifest, group):
    return [s for s, meta in manifest.items() if meta["group"] == group]


def mean(values):
    return sum(values) / len(values)


# ── Criteria 1-3, from the run and the log ───────────────────────────────────

def criterion_1(trials, manifest):
    result = Result(1, "False positives",
                    f"at most {MAX_FALSE_POSITIVES} of the 10 human samples get "
                    f'guess "ai", in each of the three trials')
    humans = group_ids(manifest, "H")
    if not humans:
        return result.unevaluated("no samples in group H in the manifest")
    if not trials:
        return result.unevaluated("no trials in the run report")

    passed = True
    for n, records in enumerate(trials, 1):
        found, unanswered = guesses(records)
        seen = [s for s in humans if s in found]
        flagged = [s for s in seen if found[s] == "ai"]
        result.calculation.append(
            f"trial {n}: count of H samples with guess == \"ai\"")
        result.observed.append(
            f"trial {n}: {len(flagged)} of {len(seen)} H samples classified"
            + (f" — {', '.join(flagged)}" if flagged else ""))
        if len(seen) < len(humans):
            missed = [s for s in humans if s not in found]
            result.unevaluated(
                f"trial {n}: {len(missed)} H sample(s) got no guess ({', '.join(missed)})")
            return result
        if len(flagged) > MAX_FALSE_POSITIVES:
            passed = False
    return result.decide(passed)


def criterion_2(trials, manifest, index):
    result = Result(2, "Score spread",
                    f"mean(A) - mean(H) >= {MIN_MEAN_GAP:.2f}, and at least "
                    f"{MIN_AI_ABOVE_HUMAN_MEAN} of the 5 A samples above mean(H), "
                    f"in each of the three trials")
    humans, ais = group_ids(manifest, "H"), group_ids(manifest, "A")
    if not humans or not ais:
        return result.unevaluated("the manifest needs samples in groups H and A")
    if not trials:
        return result.unevaluated("no trials in the run report")

    passed = True
    for n, records in enumerate(trials, 1):
        scores, missing, duplicated = combined_scores(records, index)
        for note in duplicated:
            result.notes.append(f"trial {n}: duplicate audit match — {note}")
        wanted = humans + ais
        absent = [s for s in wanted if s not in scores]
        if absent:
            for note in missing:
                result.notes.append(f"trial {n}: unmatched — {note}")
            return result.unevaluated(
                f"trial {n}: no combined_score for {len(absent)} of {len(wanted)} "
                f"samples ({', '.join(absent[:6])}{'…' if len(absent) > 6 else ''})")

        human_mean = mean([scores[s] for s in humans])
        ai_mean = mean([scores[s] for s in ais])
        gap = ai_mean - human_mean
        above = [s for s in ais if scores[s] > human_mean]

        result.calculation.append(
            f"trial {n}: mean(A)={ai_mean:.4f} - mean(H)={human_mean:.4f}; "
            f"A samples above mean(H)")
        result.observed.append(
            f"trial {n}: gap {gap:.4f} ({'ok' if gap >= MIN_MEAN_GAP else 'short'}), "
            f"{len(above)} of {len(ais)} above mean(H)"
            + (f" — {', '.join(above)}" if above else ""))
        if gap < MIN_MEAN_GAP or len(above) < MIN_AI_ABOVE_HUMAN_MEAN:
            passed = False
    return result.decide(passed)


def criterion_3(trials, manifest):
    result = Result(3, "Label coverage",
                    f"for each of ai, human and unsure, at least {MIN_PER_LABEL} "
                    f"samples expected to get it actually get it, in each trial")
    if not manifest:
        return result.unevaluated("no manifest, so no expected_guess to check against")
    if not trials:
        return result.unevaluated("no trials in the run report")

    passed = True
    for n, records in enumerate(trials, 1):
        found, unanswered = guesses(records)
        if unanswered:
            result.notes.append(
                f"trial {n}: {len(unanswered)} sample(s) got no guess — {', '.join(unanswered[:4])}")
        counts = {}
        for label in ("ai", "human", "unsure"):
            expected = [s for s, meta in manifest.items() if meta["expected_guess"] == label]
            matched = [s for s in expected if found.get(s) == label]
            counts[label] = (len(matched), len(expected))
            if len(matched) < MIN_PER_LABEL:
                passed = False
        result.calculation.append(
            f"trial {n}: per label, samples whose expected_guess is that label "
            f"and whose guess is the same label")
        result.observed.append(
            f"trial {n}: " + ", ".join(
                f"{label} {got}/{total} expected" for label, (got, total) in counts.items()))
    return result.decide(passed)


# ── Criteria 4 and 5, from evidence this script collects ─────────────────────

def criterion_4(evidence):
    result = Result(4, "Appeal path",
                    f"{VALID_APPEALS} of {VALID_APPEALS} valid appeals return 200 and add "
                    f"exactly one under_review entry; a repeat adds one more; "
                    f"404 for an unknown content_id and 400 for a bad body, each "
                    f"adding one rejected entry and no appeal entry")
    if not evidence:
        return result.unevaluated(
            "no appeal evidence — run `python check_criteria.py --appeals` first")

    checks = evidence.get("checks", [])
    failed = [c for c in checks if not c.get("ok")]
    valid = [c for c in checks if c.get("kind") == "valid"]
    result.calculation.append(
        "each appeal: HTTP status, the change in entries for that content_id, "
        "the new entry's event/status/reasoning, and the original entry unchanged")
    result.observed.append(
        f"{len(checks) - len(failed)} of {len(checks)} checks held "
        f"({len(valid)} valid appeals)")
    for check in failed:
        result.observed.append(f"  failed: {check['label']} — {check.get('detail', '')}")
    if len(valid) < VALID_APPEALS:
        return result.unevaluated(
            f"only {len(valid)} valid appeals were run, and the criterion names {VALID_APPEALS}")
    return result.decide(not failed)


def criterion_5(evidence):
    result = Result(5, "Bad input",
                    "each of the nine inputs returns its status with a non-empty "
                    "error and message, rows 1-8 add exactly one rejected entry, "
                    "no unhandled 5xx, and /ping and /health still answer")
    if not evidence:
        return result.unevaluated(
            "no bad-input evidence — run `python check_criteria.py --bad-input` first")

    rows = evidence.get("rows", [])
    skipped = [r for r in rows if r.get("skipped")]
    failed = [r for r in rows if not r.get("ok") and not r.get("skipped")]
    result.calculation.append(
        "per row: HTTP status against criteria.md, the response's error and "
        "message, the count of new rejected entries, then GET /ping and /health")
    result.observed.append(
        f"{len(rows) - len(failed) - len(skipped)} of {len(rows)} rows held, "
        f"{len(failed)} failed, {len(skipped)} not evaluated")
    for row in failed:
        result.observed.append(f"  failed: row {row['row']} {row['label']} — {row.get('detail', '')}")
    for row in skipped:
        result.notes.append(f"row {row['row']} {row['label']}: {row.get('detail', '')}")
    if skipped:
        if failed:
            return result.decide(False)
        return result.unevaluated(f"{len(skipped)} row(s) were not evaluated")
    return result.decide(not failed)


# ── Collecting criteria 4 and 5 evidence from a running service ──────────────

FILLER = ("This paragraph exists so the appeal checks have something to appeal "
          "against. It is not a sample from the test set and no criterion is "
          "measured from its score. It just has to be long enough to score.")


def _rejected_count(session, url):
    entries = session.get(f"{url}/log", timeout=30).json()["entries"]
    return sum(1 for e in entries if e.get("event") == "rejected")


def _entries_for(session, url, content_id):
    entries = session.get(f"{url}/log", timeout=30).json()["entries"]
    return [e for e in entries if e.get("content_id") == content_id]


def check_appeals(url, timeout):
    """
    Criterion 4, by the method criteria.md sets out: read GET /log for that
    content_id before and after, and compare only those entries.
    """
    import requests

    session = requests.Session()
    checks = []

    def record(label, kind, ok, detail=""):
        checks.append({"label": label, "kind": kind, "ok": bool(ok), "detail": detail})
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))

    content_ids = []
    for n in range(1, VALID_APPEALS + 1):
        response = session.post(f"{url}/submit",
                                json={"text": FILLER, "creator_id": f"appeal_{n}"},
                                timeout=timeout)
        if response.status_code != 200:
            record(f"submission {n} for the appeal test", "setup", False,
                   f"HTTP {response.status_code} — cannot appeal without a content_id")
            return {"checks": checks, "when": dt.datetime.now().isoformat(timespec="seconds")}
        content_ids.append(response.json()["content_id"])

    for n, content_id in enumerate(content_ids, 1):
        before = _entries_for(session, url, content_id)
        reasoning = f"I wrote this myself — appeal {n}."
        response = session.post(f"{url}/appeal",
                                json={"content_id": content_id, "reasoning": reasoning},
                                timeout=timeout)
        after = _entries_for(session, url, content_id)
        body = response.json() if response.content else {}
        new = after[len(before):]
        ok = (response.status_code == 200
              and len(after) == len(before) + 1
              and len(new) == 1
              and new[0].get("event") == "appeal"
              and new[0].get("status") == "under_review"
              and new[0].get("reasoning") == reasoning
              and body.get("status") == "under_review"
              and after[:len(before)] == before)
        record(f"valid appeal {n}", "valid", ok,
               f"HTTP {response.status_code}, entries {len(before)}->{len(after)}")

    content_id = content_ids[0]
    before = _entries_for(session, url, content_id)
    response = session.post(f"{url}/appeal",
                            json={"content_id": content_id, "reasoning": "Second appeal."},
                            timeout=timeout)
    after = _entries_for(session, url, content_id)
    record("repeat appeal on the same content_id", "repeat",
           response.status_code == 200 and len(after) == len(before) + 1
           and after[:len(before)] == before,
           f"HTTP {response.status_code}, entries {len(before)}->{len(after)}")

    rejections = [
        ("unknown content_id", 404, {"content_id": "no-such-content-id", "reasoning": "x"}),
        ("missing content_id", 400, {"reasoning": "x"}),
        ("empty reasoning", 400, {"content_id": content_ids[1], "reasoning": ""}),
        ("whitespace-only reasoning", 400, {"content_id": content_ids[1], "reasoning": "   "}),
        ("non-string reasoning", 400, {"content_id": content_ids[1], "reasoning": 42}),
        ("body is not a JSON object", 400, [1, 2]),
    ]
    for label, want, body in rejections:
        log_before = session.get(f"{url}/log", timeout=30).json()["entries"]
        rejected_before = sum(1 for e in log_before if e.get("event") == "rejected")
        appeals_before = sum(1 for e in log_before if e.get("event") == "appeal")
        response = session.post(f"{url}/appeal", json=body, timeout=timeout)
        log_after = session.get(f"{url}/log", timeout=30).json()["entries"]
        rejected_after = sum(1 for e in log_after if e.get("event") == "rejected")
        appeals_after = sum(1 for e in log_after if e.get("event") == "appeal")
        payload = response.json() if response.content else {}
        ok = (response.status_code == want
              and rejected_after == rejected_before + 1
              and appeals_after == appeals_before
              and bool(payload.get("error")) and bool(payload.get("message")))
        record(f"rejected appeal: {label}", "rejected", ok,
               f"HTTP {response.status_code} (wanted {want}), "
               f"+{rejected_after - rejected_before} rejected, "
               f"+{appeals_after - appeals_before} appeal")

    return {"checks": checks, "when": dt.datetime.now().isoformat(timespec="seconds")}


def bad_input_rows():
    """The nine rows of criterion 5, as request bodies."""
    long_text = ("word " * (MAX_TEXT_CHARS // 5 + 20))[:MAX_TEXT_CHARS + 1]
    return [
        (1, "text field missing", 400, {"creator_id": "bad_1"}, None),
        (2, "text empty or whitespace-only", 400, {"text": "   ", "creator_id": "bad_2"}, None),
        (3, "text is null", 400, {"text": None, "creator_id": "bad_3"}, None),
        (4, "text is a number", 400, {"text": 12345, "creator_id": "bad_4a"}, None),
        (4, "text is a list", 400, {"text": ["a", "b"], "creator_id": "bad_4b"}, None),
        (5, f"text longer than {MAX_TEXT_CHARS} characters", 413,
            {"text": long_text, "creator_id": "bad_5"}, None),
        (5, f"text of exactly {MAX_TEXT_CHARS} characters is allowed", 200,
            {"text": long_text[:MAX_TEXT_CHARS], "creator_id": "bad_5ok"}, None),
        (6, "text the detector refuses to score", 400, {"text": "hi", "creator_id": "bad_6"}, None),
        (7, "body is JSON but not an object", 400, None, ("[1, 2]", "application/json")),
        (7, "body is not JSON", 400, None, ("not json at all", "text/plain")),
        (8, "creator_id missing", 400, {"text": FILLER}, None),
        (8, "creator_id blank", 400, {"text": FILLER, "creator_id": "   "}, None),
        (8, "creator_id not a string", 400, {"text": FILLER, "creator_id": 7}, None),
    ]


def check_bad_input(url, timeout, include_503):
    """
    Criterion 5. Rows 1-8 are sent here; row 9 needs a service started against a
    model that cannot load, which is a different service, so it is only checked
    when you say you started one.
    """
    import requests

    session = requests.Session()
    rows = []

    def record(row, label, ok, detail="", skipped=False):
        rows.append({"row": row, "label": label, "ok": bool(ok),
                     "detail": detail, "skipped": bool(skipped)})
        mark = "skip" if skipped else ("ok  " if ok else "FAIL")
        print(f"  {mark}  row {row}: {label}" + (f" — {detail}" if detail else ""))

    for row, label, want, body, raw in bad_input_rows():
        rejected_before = _rejected_count(session, url)
        if raw is not None:
            response = session.post(f"{url}/submit", data=raw[0].encode("utf-8"),
                                    headers={"Content-Type": raw[1]}, timeout=timeout)
        else:
            response = session.post(f"{url}/submit", json=body, timeout=timeout)
        rejected_after = _rejected_count(session, url)
        payload = response.json() if response.content else {}
        added = rejected_after - rejected_before

        if response.status_code == 429:
            record(row, label, False,
                   "rate limited before the input was handled — wait a minute and "
                   "re-run, or this row says nothing", skipped=True)
            continue

        if want == 200:
            ok = response.status_code == 200 and added == 0
            record(row, label, ok, f"HTTP {response.status_code}, +{added} rejected")
            continue

        ok = (response.status_code == want
              and bool(payload.get("error")) and bool(payload.get("message"))
              and added == 1)
        record(row, label, ok,
               f"HTTP {response.status_code} (wanted {want}), +{added} rejected, "
               f"error={payload.get('error')!r}")

    if include_503:
        response = session.post(f"{url}/submit",
                                json={"text": FILLER, "creator_id": "bad_9"}, timeout=timeout)
        payload = response.json() if response.content else {}
        record(9, "detector model cannot load", response.status_code == 503 and bool(payload.get("error")),
               f"HTTP {response.status_code}")
    else:
        record(9, "detector model cannot load", False,
               "needs a service started with a model name that does not exist; "
               "re-run that service with --expect-503", skipped=True)

    for path in ("/ping", "/health"):
        if path == "/ping":
            response = session.post(f"{url}/ping", json={"message": "still there?"}, timeout=timeout)
        else:
            response = session.get(f"{url}/health", timeout=timeout)
        ok = response.status_code == 200 and (response.json() or {}).get("ok") is True
        record("-", f"{path} still answers after the bad input", ok, f"HTTP {response.status_code}")

    no_5xx = [r for r in rows if r["row"] != 9 and "HTTP 5" in r.get("detail", "")]
    record("-", "no unhandled 5xx on rows 1-8", not no_5xx,
           "; ".join(r["label"] for r in no_5xx) if no_5xx else "")

    return {"rows": rows, "when": dt.datetime.now().isoformat(timespec="seconds")}


# ── Reporting ────────────────────────────────────────────────────────────────

def render(results, sources, problems):
    lines = [
        "# Criteria check",
        "",
        "- Produced by: `check_criteria.py::main`",
        "- Targets quoted from: `criteria.md`",
        f"- {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Sample ids and scores only. No submitted writing appears in this report.",
        "",
    ]
    for label, value in sources.items():
        lines.append(f"- {label}: `{value}`")
    lines.append("")

    if problems:
        lines += ["## Problems reading the evidence", ""]
        lines += [f"- {p}" for p in problems] + [""]

    lines += ["| Criterion | Required | Observed | Verdict |", "|---|---|---|---|"]
    for result in results:
        observed = "<br>".join(result.observed) if result.observed else "—"
        lines.append(f"| {result.number}. {result.name} | {result.required} | "
                     f"{observed} | **{result.verdict}** |")
    lines.append("")

    for result in results:
        lines += [f"## {result.number}. {result.name}", "",
                  f"**Verdict:** {result.verdict}", "",
                  f"**Required by criteria.md:** {result.required}", ""]
        if result.calculation:
            lines += ["**Calculation**", ""] + [f"- {c}" for c in result.calculation] + [""]
        if result.observed:
            lines += ["**Observed**", ""] + [f"- {o}" for o in result.observed] + [""]
        if result.notes:
            lines += ["**Notes**", ""] + [f"- {n}" for n in result.notes] + [""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", help="a run_eval.py report, for criteria 1-3")
    parser.add_argument("--manifest", default=str(config.ROOT / "test_set" / "manifest.csv"))
    parser.add_argument("--log", default=str(config.AUDIT_LOG),
                        help="the audit log to read combined_score from")
    parser.add_argument("--appeal-evidence", help="JSON from --appeals")
    parser.add_argument("--bad-input-evidence", help="JSON from --bad-input")
    parser.add_argument("--appeals", action="store_true",
                        help="send the criterion 4 checks to a running service")
    parser.add_argument("--bad-input", action="store_true",
                        help="send the criterion 5 checks to a running service")
    parser.add_argument("--expect-503", action="store_true",
                        help="with --bad-input: this service was started with a model "
                             "that cannot load, so check row 9")
    parser.add_argument("--url", default=f"http://{config.HOST}:{config.PORT}")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--label", default="")
    parser.add_argument("--out", help="where to write the report (default: results/)")
    args = parser.parse_args()

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    config.RESULTS_DIR.mkdir(exist_ok=True)

    if args.appeals or args.bad_input:
        try:
            import requests
        except ImportError:
            print("The `requests` package isn't installed.\n"
                  "Run: pip install -r requirements.txt", file=sys.stderr)
            return 1
        try:
            requests.get(f"{args.url}/health", timeout=5)
        except Exception:  # noqa: BLE001
            print(f"Nothing answering at {args.url}. Start it:  python app.py",
                  file=sys.stderr)
            return 1

        if args.appeals:
            print(f"Criterion 4 — appeals, against {args.url}")
            evidence = check_appeals(args.url, args.timeout)
            path = Path(args.out) if args.out else config.RESULTS_DIR / f"appeals_{stamp}{label}.json"
        else:
            print(f"Criterion 5 — bad input, against {args.url}")
            evidence = check_bad_input(args.url, args.timeout, args.expect_503)
            path = Path(args.out) if args.out else config.RESULTS_DIR / f"bad_input_{stamp}{label}.json"
        path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        print(f"\nWrote {path}")
        print("Now pass it to the check:  python check_criteria.py --run <report> "
              f"--{'appeal' if args.appeals else 'bad-input'}-evidence {path}")
        return 0

    problems, sources = [], {}
    trials, manifest, index = [], {}, {}

    if args.run:
        sources["Run report"] = args.run
        trials, run_problems = load_run(Path(args.run))
        problems += run_problems
    else:
        problems.append("No --run given, so criteria 1-3 have no evidence")

    manifest_path = Path(args.manifest)
    sources["Manifest"] = str(manifest_path)
    manifest, manifest_problems = load_manifest(manifest_path)
    problems += manifest_problems

    log_path = Path(args.log)
    sources["Audit log"] = str(log_path)
    entries, log_problems = load_audit(log_path)
    problems += log_problems
    index = decisions_by_content_id(entries)

    appeal_evidence = bad_input_evidence = None
    if args.appeal_evidence:
        sources["Appeal evidence"] = args.appeal_evidence
        appeal_evidence = json.loads(Path(args.appeal_evidence).read_text(encoding="utf-8"))
    if args.bad_input_evidence:
        sources["Bad-input evidence"] = args.bad_input_evidence
        bad_input_evidence = json.loads(Path(args.bad_input_evidence).read_text(encoding="utf-8"))

    results = [
        criterion_1(trials, manifest),
        criterion_2(trials, manifest, index),
        criterion_3(trials, manifest),
        criterion_4(appeal_evidence),
        criterion_5(bad_input_evidence),
    ]

    report = render(results, sources, problems)
    path = Path(args.out) if args.out else config.RESULTS_DIR / f"criteria_{stamp}{label}.md"
    path.write_text(report, encoding="utf-8")

    for result in results:
        print(f"{result.verdict:<14} {result.number}. {result.name}")
        for note in result.notes:
            print(f"               - {note}")
    print(f"\nWrote {path}")
    print("Verdicts are this script's arithmetic on your evidence. The targets "
          "are criteria.md's.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
