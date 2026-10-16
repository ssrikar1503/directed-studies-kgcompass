"""Full-coverage bad-triple catalog over ALL triples in every graph export.

Combines (a) deterministic detectors that run on every one of the 83,554
triples, and (b) the LLM-judged verdicts (950 sampled triples, judged against
source papers) where they exist. Output: one row per flagged triple with
category(ies), severity, reason, and detection method.

Usage: python flag_bad_triples.py <csv-dir> <verdicts-dir> <samples-dir> -o bad_triples.csv
"""
import argparse
import csv
import glob
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from analyze_graphs import (GROUP_BY_ROWS, TRIVIAL_RELATIONS, VAGUE_ENTITIES,
                            NEG_PAT, POS_INC, POS_DEC, AFFIRMATIVE)

CHANGE_RELS = POS_INC | POS_DEC | {"improves", "enhances", "affects", "influences"}
BARE_CONTAINERS = {
    "liver", "kidney", "blood serum", "serum", "plasma", "meat", "milk",
    "muscle", "skin", "thyroid gland", "pancreas", "spleen", "egg", "bone",
    "rumen", "intestine", "gut", "brain", "heart", "fat", "tissue", "blood",
    "urine", "feces", "carcass", "colon", "stomach", "lung",
}
GARBLED_PAT = re.compile(
    r"(-lrb-|-rrb-|&#|[a-z]/[A-Z]\d|\d/[A-Z]\d|\s/\s|//|\\\\|�)", re.I)

SEV_RANK = {"high": 3, "medium": 2, "low": 1}


def load_llm_verdicts(verdicts_dir, samples_dir):
    """(group, subject, relation, object) -> (verdict, evidence)"""
    out = {}
    for vf in glob.glob(os.path.join(verdicts_dir, "g*_verdicts.csv")):
        gid = os.path.basename(vf).split("_")[0]
        sf = os.path.join(samples_dir, f"{gid}_sample.csv")
        if not os.path.exists(sf):
            continue
        sample = {r["idx"]: r for r in csv.DictReader(open(sf))}
        for r in csv.DictReader(open(vf)):
            t = sample.get(r["idx"])
            if t is None:
                continue
            key = (gid, t["subject"].strip().lower(), t["relation"].strip().lower(),
                   t["object"].strip().lower())
            out[key] = (r["verdict"].strip().lower(), r["evidence"].strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_dir")
    ap.add_argument("verdicts_dir")
    ap.add_argument("samples_dir")
    ap.add_argument("-o", "--out", default="bad_triples.csv")
    args = ap.parse_args()

    llm = load_llm_verdicts(args.verdicts_dir, args.samples_dir)

    rows_out = []
    total = 0
    cat_counter = Counter()
    for f in sorted(glob.glob(os.path.join(args.csv_dir, "*.csv"))):
        rows = list(csv.DictReader(open(f, encoding="utf-8", errors="replace")))
        label = GROUP_BY_ROWS.get(len(rows), os.path.basename(f))
        gid = label.split()[0]
        total += len(rows)

        rels_count = Counter(r["relation"].strip().lower() for r in rows)

        # contradiction membership: same (s,o), opposing relations
        pair_rels = defaultdict(set)
        for r in rows:
            pair_rels[(r["subject"].strip().lower(), r["object"].strip().lower())].add(
                r["relation"].strip().lower())
        contra_pairs = set()
        for (s, o), rl in pair_rels.items():
            rl = list(rl)
            if len(rl) < 2:
                continue
            negs = [x for x in rl if NEG_PAT.search(x)]
            affs = [x for x in rl if not NEG_PAT.search(x)]
            strong = [a for a in affs if a in AFFIRMATIVE or a in POS_INC or a in POS_DEC]
            if (negs and strong) or (
                any(a in POS_INC for a in rl) and any(a in POS_DEC for a in rl)):
                contra_pairs.add((s, o))

        for r in rows:
            s = r["subject"].strip()
            rel = r["relation"].strip()
            o = r["object"].strip()
            sl, rl_, ol = s.lower(), rel.lower(), o.lower()
            cats, reasons, sev = [], [], "low"

            key = (gid, sl, rl_, ol)
            if key in llm:
                verdict, evidence = llm[key]
                if verdict == "wrong":
                    cats.append("llm_confirmed_wrong")
                    reasons.append("LLM judge vs source paper: WRONG - " + evidence)
                    sev = "high"
                elif verdict == "imprecise":
                    cats.append("llm_confirmed_imprecise")
                    reasons.append("LLM judge vs source paper: IMPRECISE - " + evidence)
                    sev = max(sev, "medium", key=lambda x: SEV_RANK[x])

            if (sl, ol) in contra_pairs and (
                rl_ in AFFIRMATIVE or rl_ in POS_INC or rl_ in POS_DEC
                or NEG_PAT.search(rl_)):
                cats.append("contradiction_pair")
                others = [x for x in pair_rels[(sl, ol)] if x != rl_]
                reasons.append(
                    f"Opposing relation(s) exist for same subject+object: {others} - "
                    "both cannot be true unqualified; needs triage (extraction error "
                    "vs conditional finding)")
                sev = "high"

            if GARBLED_PAT.search(sl) or GARBLED_PAT.search(ol):
                cats.append("garbled_entity")
                reasons.append("Entity text contains OCR/parser artifacts "
                               "(e.g. -LRB-, stray slashes, mangled notation)")
                sev = "high"

            if rl_ in CHANGE_RELS and ol in BARE_CONTAINERS:
                cats.append("granularity_truncation")
                reasons.append(
                    f"Change-relation '{rel}' with bare organ/fluid object '{o}' - "
                    "the measured quantity (e.g. a concentration IN the organ) was "
                    "dropped; 'increases liver' pattern")
                sev = max(sev, "medium", key=lambda x: SEV_RANK[x])

            if sl in VAGUE_ENTITIES or ol in VAGUE_ENTITIES:
                cats.append("vague_entity")
                reasons.append("Subject or object is a vague non-entity "
                               "(it/this/study/results/...) - unusable as a graph node")
                sev = max(sev, "medium", key=lambda x: SEV_RANK[x])

            if rl_ in TRIVIAL_RELATIONS and rl_ in {"is measured in", "is measured for",
                                                    "is related to", "is associated with"}:
                cats.append("trivial_low_value")
                reasons.append(f"Relation '{rel}' carries near-zero knowledge value - "
                               "methodological or uninformative; pruning candidate")

            if rels_count[rl_] == 1:
                cats.append("nonstandard_rare_relation")
                reasons.append("Relation type used only once in this graph - "
                               "vocabulary-explosion artifact; normalization candidate")

            if cats:
                cat_counter.update(cats)
                rows_out.append([
                    gid, label.split(" ", 1)[-1], s, rel, o, r.get("effect", ""),
                    ";".join(cats), sev, " | ".join(reasons),
                    "llm_judge+rule" if key in llm and len(cats) > 1
                    else ("llm_judge" if key in llm else "rule"),
                    r.get("papers", "")[:160],
                ])

    sev_order = {"high": 0, "medium": 1, "low": 2}
    rows_out.sort(key=lambda x: (sev_order[x[7]], x[0]))
    with open(args.out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["group", "topic", "subject", "relation", "object", "effect",
                    "categories", "severity", "reason", "method", "source_papers"])
        w.writerows(rows_out)

    print(f"triples scanned: {total:,} | flagged: {len(rows_out):,} "
          f"({100*len(rows_out)/total:.1f}%)")
    for c, n in cat_counter.most_common():
        print(f"  {c}: {n:,}")
    sev_c = Counter(x[7] for x in rows_out)
    print("severity:", dict(sev_c))


if __name__ == "__main__":
    main()
