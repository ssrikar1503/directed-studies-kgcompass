# Evaluation of Sumanth's AnimalRAG Knowledge Graph (group13)

Date: Oct 14, 2026. Evaluator: Srikar (directed studies), using our GraphJudge-style
triple-accuracy methodology + the GraphJudge metric code.

## What was evaluated

From the "Animal science KG" Drive (AnimalRAG_Local-main), group13
(Iodine_Thyroid_Content): 3 papers, 134 chunks, 271 entities, **474 relations**
(`stores/group13/export/triples.csv`). A seeded random sample of **50 triples**
(seed 42, covers all 3 papers) was judged against the FULL TEXT of all three
source papers (Schone 2006 pig iodine; Li 2012 fattening pigs; Rottger 2011
broilers), read end to end.

## Headline numbers

| Metric | Value |
|---|---|
| Strict triple accuracy (fully correct) | **58%** (29/50) |
| Lenient accuracy (correct + imprecise) | 84% (42/50) |
| Imprecise (right idea, wrong granularity/condition) | 26% (13/50) |
| Wrong (contradicted, inverted, garbled, context-leak) | **16%** (8/50) |
| GraphJudge metric precision (pred vs judged-correct reference) | 0.58 |

Structural scan of all 474 triples: **127 distinct relation types, 63 used exactly
once** (relation-vocabulary explosion); 0 duplicate s-r-o; 0 self-loops; 7
vague-entity triples; 22 triples backed by 2+ papers.

## Error taxonomy (with real examples from the graph)

1. **Object/subject truncation (most common imprecision).**
   "high dietary iodine → increases → *blood serum*" (should be *serum iodine
   concentration*); "KI → increases → *liver*"; "iodine supplementation →
   increases → *iodine*" (tautology). The entity kept is a container, not the
   quantity that changed.
2. **Condition dropping.** "iodine → causes → hypothyroidism" (source says
   *excess* iodine); "iodine → poses no risk to → human health" (source says no
   risk *from pork at these feed levels*). Same failure class as our gossypol
   example from the Arieli review.
3. **In-graph contradictions.** Triple 39 "iodine does not affect fattening
   performance" vs triple 42 "iodine affects fattening performance" — both in
   the same graph, extracted from the same paper. Also the hypothyroidism pair
   (19/43 vs 33). A GraphRAG answer can retrieve either side.
4. **Surface inversion.** "rape → reduces → thyroid gland": the source shows
   rapeseed ENLARGES the thyroid while reducing its iodine stores. The triple
   asserts the opposite of the gland-size finding.
5. **Citation-context leak.** "swine feed → improves → human iodine supply" is a
   CITED aim from the intro; the paper's own conclusion is that pork's
   contribution is marginal. Extraction cannot tell reported claims from findings.
6. **Garbled triples.** "potassium iodide → is source of → milk"; "spleen → is
   part of → empty body" (the source explicitly defines empty body as the
   carcase WITHOUT innards).
7. **Trivial/methodological triples.** ~7/50 are of the form "X is measured in Y"
   (ash in feed, DM in feed, serum for iodine). True but near-zero knowledge
   value — prime pruning candidates.

## What this means for the project

- **Validates Prof. Tao's directive empirically:** at the answer level, Sumanth's
  own RESULTS.md shows the LLM judge mostly could not distinguish systems on
  faithfulness (83% ties) — yet at the triple level, 16% of facts are wrong and
  26% degraded. Triple errors are invisible to answer-level judging, which is
  exactly why triple-level verification must come first.
- **A GraphJudge-style filter would catch most of the 16%:** every "wrong" case
  above fails a direct "is this true given the source chunk?" check. The chunk
  ids are already in the export, so judge inputs can be built mechanically.
- **Pruning agenda gets concrete targets:** singleton relations (63), trivial
  measurement triples, and uninformative relations ("is related to",
  "is associated with") — all identifiable without any LLM.
- **Research angle confirmed on real data:** condition-dropping and
  citation-context leaks are systematic, and flat triples cannot represent
  "excess iodine", "in pigs at 10,000 ug/kg", or "cited vs concluded". Richer
  knowledge units / qualified triples is a publishable direction with evidence
  from our own pipeline.

## Files

- `group13_triples.csv` — full export (474 triples) from Sumanth's pipeline
- `sample50.csv` / `sample50_judged.csv` — the sample and per-triple verdicts
  with evidence comments
- `eval_pred.txt` / `eval_gold.txt` — inputs used for the GraphJudge metric run

## Caveats

- One group of 38; 50 of 474 triples; single human-LLM judge (me). Numbers are
  an estimate, not a benchmark. Next step is scaling the same judging to more
  groups with the released GraphJudge LoRA weights on HPRC, using each triple's
  own source chunks as context.
- "Correct" includes trivially true triples; a usefulness-weighted score would
  be lower for both counts.
