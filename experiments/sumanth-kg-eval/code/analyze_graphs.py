"""Structural quality + contradiction census for AnimalRAG KG exports.

Input: a directory of triples.csv files (the knowledge_graph/stores/<group>/export/
format: subject, relation, object, effect, weight, contexts, descriptions, papers,
chunk_ids, subject_type, object_type). Works on one file too - including the
full all-papers graph.

Usage:
    python analyze_graphs.py <dir-or-file> [-o OUTDIR]

Outputs in OUTDIR (default .):
    per_group_quality.csv  - one row per graph: counts, relation vocabulary,
                             singleton/trivial/vague shares, contradiction pairs
    contradictions.csv     - every detected contradiction pair with both relations
"""
import argparse
import csv
import glob
import os
import re
import sys
from collections import Counter, defaultdict

# Row-count -> group label, from RESULTS.md (29 Sep - 1 Oct 2026 run).
# A file whose row count is not in this map is labeled by its filename.
GROUP_BY_ROWS = {
    2868: "g01 Review_Dairy_Based", 2864: "g02 Chicken_Calcium_Enriched",
    2510: "g03 Model_Production_Male", 2416: "g04 High_Dairy_Host",
    3535: "g05 Dairy_Impact_Goats", 2738: "g06 Selenium_Nutrition_Livestock",
    2858: "g07 Biohydrogenation_Unsat_Fatty", 982: "g08 What_Cryptoxanthin_Vitamin",
    2094: "g10 Cattle_Influence_Meat", 995: "g11 Alfalfa_Intake_Cattle",
    2660: "g12 Feed_Poultry_Additives", 474: "g13 Iodine_Thyroid_Content",
    2491: "g14 Acid_Milk_Fatty", 2842: "g15 Nutrition_Human_Novel",
    2513: "g16 Nutrition_Human_Products", 3262: "g17 Health_Human_Exposure",
    2257: "g18 Health_Human_Exposure2", 2118: "g20 Feed_Livestock_Feeds",
    3250: "g21 Intestinal_Microbiota_Pigs", 465: "g22 Gut_Supplementation_Soluble",
    2163: "g23 Acid_Fatty_Oil", 1273: "g24 Acid_Cla_Egg",
    1362: "g25 Amino_Acid_Ileal", 3132: "g26 Food_Human_Chain",
    2069: "g27 Meat_Quality_Factors", 2398: "g28 Feed_Human_Moringa",
    2686: "g29 Performance_Growth_Digest", 587: "g30 Performance_Digestive_Enzymes",
    960: "g31 Dairy_Farms_Food", 1569: "g32 Implications_Human_Health",
    2557: "g33 Pig_Antioxidant_Meta", 1791: "g34 Pig_Bovine_Metagenomic",
    3073: "g35 Properties_Nutritional_Pot", 1766: "g36 Farm_Animals_Lactation",
    1913: "g37 Carcass_Meat_Performance", 1321: "g38 Nutritional_Value_Meat",
    1612: "g40 Potential_Application_Garlic", 1633: "g41 Organic_Acids_Essential",
    3497: "testset",
}

TRIVIAL_RELATIONS = {
    "is measured in", "is component of", "is related to", "is associated with",
    "is present in", "is part of", "is measured for", "is used in",
    "is found in", "contains",
}
VAGUE_ENTITIES = {
    "it", "this", "study", "results", "effect", "diet", "research",
    "the study", "they", "model", "method", "data",
}
NEG_PAT = re.compile(r"\b(no|not|does not|has no|without)\b")
POS_INC = {"increases", "raises", "elevates", "enhances", "boosts",
           "increases content in", "increases in"}
POS_DEC = {"decreases", "reduces", "lowers", "diminishes", "suppresses"}
AFFIRMATIVE = {"affects", "influences", "impacts", "changes", "modifies",
               "increases", "decreases", "improves", "reduces"}


def analyze_file(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    label = GROUP_BY_ROWS.get(len(rows), os.path.basename(path))
    rels = Counter(r["relation"].strip().lower() for r in rows)
    singles = sum(1 for c in rels.values() if c == 1)
    trivial = sum(1 for r in rows if r["relation"].strip().lower() in TRIVIAL_RELATIONS)
    vague = sum(1 for r in rows
                if r["subject"].strip().lower() in VAGUE_ENTITIES
                or r["object"].strip().lower() in VAGUE_ENTITIES)
    sro = Counter((r["subject"].lower(), r["relation"].lower(), r["object"].lower())
                  for r in rows)
    dup = sum(1 for c in sro.values() if c > 1)
    selfloop = sum(1 for r in rows
                   if r["subject"].strip().lower() == r["object"].strip().lower())
    multi = sum(1 for r in rows if "|" in r.get("papers", ""))

    pair = defaultdict(set)
    for r in rows:
        pair[(r["subject"].strip().lower(), r["object"].strip().lower())].add(
            r["relation"].strip().lower())
    contradictions = []
    for (s, o), rl in pair.items():
        rl = list(rl)
        if len(rl) < 2:
            continue
        negs = [x for x in rl if NEG_PAT.search(x)]
        affs = [x for x in rl if not NEG_PAT.search(x)]
        hit = None
        strong_affs = [a for a in affs
                       if a in AFFIRMATIVE or a in POS_INC or a in POS_DEC]
        if negs and strong_affs:
            hit = (negs[0], strong_affs[0])
        elif any(a in POS_INC for a in rl) and any(a in POS_DEC for a in rl):
            hit = ([a for a in rl if a in POS_INC][0],
                   [a for a in rl if a in POS_DEC][0])
        if hit:
            contradictions.append([label, s, hit[0], hit[1], o])

    summary = [label, len(rows), len(rels), singles,
               round(100 * singles / max(len(rels), 1)),
               trivial, round(100 * trivial / max(len(rows), 1), 1),
               vague, dup, selfloop, multi, len(contradictions)]
    return summary, contradictions, rels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="directory of triples.csv files, or one file")
    ap.add_argument("-o", "--outdir", default=".")
    args = ap.parse_args()

    files = ([args.input] if os.path.isfile(args.input)
             else sorted(glob.glob(os.path.join(args.input, "*.csv"))))
    if not files:
        sys.exit("no csv files found")

    summaries, all_contr, agg_rel = [], [], Counter()
    for f in files:
        s, c, rels = analyze_file(f)
        summaries.append(s)
        all_contr.extend(c)
        agg_rel.update(rels)
    summaries.sort(key=lambda x: x[0])

    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir, "per_group_quality.csv"), "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["group", "triples", "unique_relations", "singleton_relations",
                    "singleton_pct_of_relations", "trivial_relation_triples",
                    "trivial_pct", "vague_entity_triples", "duplicate_sro",
                    "self_loops", "multi_paper_triples", "contradiction_pairs"])
        w.writerows(summaries)
    with open(os.path.join(args.outdir, "contradictions.csv"), "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["group", "subject", "relation_A", "relation_B", "object"])
        w.writerows(all_contr)

    total = sum(s[1] for s in summaries)
    print(f"graphs: {len(summaries)} | triples: {total:,}")
    print(f"distinct relations overall: {len(agg_rel):,} "
          f"(singletons {sum(1 for c in agg_rel.values() if c == 1):,})")
    print(f"contradiction pairs: {len(all_contr)}")
    print(f"top relations: {agg_rel.most_common(10)}")


if __name__ == "__main__":
    main()
