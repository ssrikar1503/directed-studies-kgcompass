# KG Evaluation Codebase

The complete, reproducible pipeline behind `KG_Quality_Evaluation_Report.docx`.
Pure-Python (stdlib only) except where noted. Every number in the report comes
out of these scripts.

## Pipeline

```
triples.csv exports            sample50.csv              verdicts (2 judges)
(stores/<group>/export/)   ->  sample_triples.py     ->  manual / judge_triples.py
        |                                                      |
        v                                                      v
analyze_graphs.py                                        agreement.py
per_group_quality.csv                                    84% / 94% agreement
contradictions.csv
```

## Scripts

| Script | What it does | Needs |
|---|---|---|
| `analyze_graphs.py <dir-or-file>` | Structural quality + contradiction census per graph. Works on a directory of exports or ONE file - including the 35 MB all-papers triples.csv | stdlib |
| `sample_triples.py <triples.csv> --seed 42 -n 50` | Seeded sample for judging (seed 42 reproduces `sample50.csv`) | stdlib |
| `../judge_triples.py` | LLM judge: every sampled triple vs the full source-paper texts, Claude Sonnet (`claude-sonnet-5-5`), papers as a cached prompt prefix | `pip install anthropic`, API key, paper .txt files in `../papers/` |
| `agreement.py <a.csv> <b.csv>` | Inter-judge agreement (exact, binary, flips, cross-tab) | stdlib |

## Reproducing the report numbers

```bash
# 1. structural analysis over all group exports (39 graphs, 83,554 triples)
python code/analyze_graphs.py all-groups/csv -o all-groups

# 2. the judged sample (group13)
python code/sample_triples.py all-groups/csv/<group13 file>.csv --seed 42 -o sample50.csv

# 3. judge with the API (or judge manually with evidence comments)
python judge_triples.py          # -> api_sonnet_verdicts.csv

# 4. agreement between judges
python code/agreement.py sample50_judged.csv sonnet_verdicts.csv
```

## Running on the all-papers graph (setting B)

The combined graph's triples.csv (~35 MB) exceeded the Drive connector limit,
so it is not in this repo. From the AnimalRAG project root:

```bash
python code/analyze_graphs.py knowledge_graph/stores/<full-store>/export/triples.csv -o full-graph
```

Runs in under a minute. Expect the contradiction count to rise relative to the
per-group graphs: cross-paper entity merging creates more same-subject-object
pairs with opposing findings.

## What the contradiction detector flags (and does not)

A pair is flagged when the SAME subject and object carry (a) a negated relation
and an affirmative counterpart (has no effect on / affects), or (b) an increase
and a decrease relation. It is lexical and conservative - paraphrase conflicts
("improves" vs "has no benefit for") with different objects are NOT caught, so
the 495 figure is a lower bound. A flagged pair is not automatically an
extraction error: some are genuinely conflicting findings across papers that
need conditions (dose, species, study) attached - triage decides which.
