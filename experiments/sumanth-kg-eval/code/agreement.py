"""Inter-judge agreement between two verdict CSVs (columns incl. idx, verdict).

Usage:
    python agreement.py <judge_a.csv> <judge_b.csv>
"""
import csv
import sys
from collections import Counter


def load(path):
    return {r["idx"]: r["verdict"].strip().lower()
            for r in csv.DictReader(open(path))}


def main():
    a, b = load(sys.argv[1]), load(sys.argv[2])
    keys = sorted(set(a) & set(b), key=int)
    n = len(keys)
    exact = sum(1 for k in keys if a[k] == b[k])
    binary = sum(1 for k in keys if (a[k] == "correct") == (b[k] == "correct"))
    flips = sum(1 for k in keys if {a[k], b[k]} == {"correct", "wrong"})
    print(f"n={n}")
    print(f"exact 3-way agreement: {exact}/{n} = {100*exact/n:.0f}%")
    print(f"binary (correct vs flawed): {binary}/{n} = {100*binary/n:.0f}%")
    print(f"correct<->wrong flips: {flips}")
    print("cross-tab:", dict(Counter((a[k], b[k]) for k in keys)))
    print("\ndisagreements:")
    for k in keys:
        if a[k] != b[k]:
            print(f"  idx {k}: {a[k]} vs {b[k]}")


if __name__ == "__main__":
    main()
