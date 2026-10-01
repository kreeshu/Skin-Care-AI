"""Summarise the SkinCare AI Google Forms survey export.

Usage:
    python3 analyse_sus.py responses.csv
    python3 analyse_sus.py --selftest

Column titles are matched by the prefixes used in create_form.gs.
"""
import csv
import statistics
import sys
from collections import Counter


def sus_score(ratings):
    """Standard SUS: odd items score r-1, even items 5-r, sum times 2.5."""
    assert len(ratings) == 10
    return 2.5 * sum((r - 1) if i % 2 == 0 else (5 - r) for i, r in enumerate(ratings))


def mean_sd(values):
    return statistics.mean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)


def summarise(rows):
    cols = list(rows[0].keys())
    sus_cols = sorted((c for c in cols if c.startswith("SUS")), key=lambda c: int(c[3:c.index(".")]))
    scores = [sus_score([int(r[c]) for c in sus_cols]) for r in rows]
    m, sd = mean_sd(scores)
    print(f"Participants: {len(rows)}")
    print(f"SUS: mean {m:.1f}, SD {sd:.1f}, range {min(scores):.1f}-{max(scores):.1f}")

    for c in cols:
        if c.endswith(": did you complete it?"):
            done = sum(r[c].startswith("Yes") for r in rows)
            print(f"{c.split(':')[0]}: completed {done}/{len(rows)} ({100 * done / len(rows):.0f}%)", end="")
            ease = [int(r[c.replace('did you complete it?', 'how easy was it?')]) for r in rows]
            print(f", ease mean {statistics.mean(ease):.2f}")

    for c in cols:
        if c in ("Age group", "How would you describe your skin type?",
                 "Have you used a skincare or beauty app before?", "Which photo did you use in the app?",
                 "Did you notice the message saying the app does not give medical advice?") \
                or c.startswith('When a concern is marked "uncertain"'):
            print(f"{c}: {dict(Counter(r[c] for r in rows))}")
        elif c.startswith(("The results matched", "I trust", "The reasons shown", "I would consider")):
            vals = [int(r[c]) for r in rows]
            print(f"{c}: mean {statistics.mean(vals):.2f}")
    return scores


def selftest():
    assert sus_score([5, 1] * 5) == 100.0
    assert sus_score([1, 5] * 5) == 0.0
    assert sus_score([3] * 10) == 50.0
    row = {f"SUS{i}. item": "3" for i in range(1, 11)}
    row.update({"Task 1 - x: did you complete it?": "Yes, without help", "Task 1 - x: how easy was it?": "4"})
    assert summarise([row, dict(row)]) == [50.0, 50.0]
    print("selftest ok")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--selftest":
        selftest()
    else:
        with open(sys.argv[1], newline="", encoding="utf-8") as f:
            summarise(list(csv.DictReader(f)))
