# Animal Science Corpus - Notes

Source: Google Drive folder "AnimalScience" shared by psurabhi@tamu.edu (Sep 22, 2026).
Drive folder: https://drive.google.com/drive/folders/16zTl7eiMs9rkvDt5BMAWDre6UMPwR5DR

## Structure

| Subfolder | Drive ID | Contents |
|---|---|---|
| AnimalScience/ | 1PyaLWL_OGtBjHBy_BY1mc2PqjRtQYBSr | ~50 PDFs: animal nutrition reviews and studies (dairy cattle, poultry, pigs, feed additives, mycotoxins, gut microbiome) |
| Papers/ | 1UADjumZdjdRELG_1AcoEDbHv_i-TIPX_ | ~55 PDFs, Zotero-style names (beef quality, methane, phosphorus, insects as feed, AMR, meat packaging) |
| Outputs/ | 1Ya5q6DPrfO0wptmPlrgFWbtrHb-8mmww | 4 case_*.json - QA cases from the team's existing RAG pipeline |

Total corpus: ~105 papers. Re-list any folder with a Drive parentId query when needed.

## The existing pipeline (from Outputs/case_*.json)

Case format: `{user_query, expanded_queries[], response}` - a query-expansion RAG:
- Example query: "What kind of effect does monensin have on risk of metritis?"
- ~40 expanded search queries generated per question
- Earliest case (Sep 3): answer says "the provided text does not mention..." (retrieval miss)
- Later case (Sep 4): organized, multi-source cited answer (Russell & Houlihan 2003,
  Castillo et al. 2004, Broderick 2018, Dorne et al. 2013)

Implication: the team already has a text-RAG baseline and test questions. Our KG /
GraphRAG built from the same corpus should be evaluated against these same cases.

## First extraction sample (done)

`extraction-samples/arieli1998_wcs_triples.csv` - 35 triples from Arieli 1998
"Whole cottonseed in dairy cattle feeding: a review" (31 kept with quoted evidence,
4 rejected with reasons: overstatement, contradiction, inconsistent support).
This mirrors the GraphJudge workflow: over-extract, judge each triple against the text.

Starter relation vocabulary used (to discuss with team):
`type of, contains, increases, decreases, depends on, has property, favors,
comparable to, toxic to, safe for, causes, detoxifies, serves as, is`

Note the rejected examples: they are exactly the LLM failure modes from the GraphJudge
paper appearing in a real domain paper - overstated causal claims where the source says
"variable", and species-conditional facts (gossypol toxic to monogastrics but NOT to
ruminant females) that a naive extractor flattens incorrectly. Conditional/species-scoped
facts are a strong candidate for the "richer knowledge units" research angle.

## Next steps

1. Batch-download the corpus locally (browser zip is fastest) for pipeline runs
2. Run ECTD-style extraction over 5-10 papers; grow the triple inspection sheet
3. Map the 4 QA cases to triples the KG must contain to answer them (monensin ->
   methane/rumen fermentation facts are already in this corpus)
4. Team labeling: turn inspection sheets into the domain gold set
