"""Draw a seeded random sample of triples from a triples.csv for manual judging.

Usage:
    python sample_triples.py <triples.csv> [-n 50] [--seed 42] [-o sample.csv]

Seed 42 with n=50 on group13's export reproduces sample50.csv exactly.
"""
import argparse
import csv
import random


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("triples_csv")
    ap.add_argument("-n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("-o", "--out", default="sample.csv")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.triples_csv, encoding="utf-8",
                                    errors="replace")))
    random.seed(args.seed)
    sample = random.sample(rows, min(args.n, len(rows)))
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["idx", "subject", "relation", "object", "effect",
                    "papers", "descriptions"])
        for i, r in enumerate(sample):
            w.writerow([i, r["subject"], r["relation"], r["object"], r["effect"],
                        r["papers"][:120], r["descriptions"][:200]])
    print(f"wrote {args.out}: {len(sample)} triples (seed {args.seed})")


if __name__ == "__main__":
    main()
