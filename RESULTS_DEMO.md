# GraphJudge Pipeline - First Reproduction Results

Date: Sep 13, 2026
Setup: official GraphJudge repo, SCIERC dataset (first 15 test documents),
evaluated with the paper's own metrics code (`graph_evaluation/metrics/eval.py`).

## What was run

1. Environment: Python 3.13 venv, torch 2.14, bert-score, rouge, nltk, spacy
2. Extraction: Claude acted as the extraction LLM (the role GPT-4o-mini plays
   in the paper) on 15 SCIERC abstracts
   - Naive pass (recall-first, like the paper's baseline): 129 triples
   - Judged pass (strictly text-supported triples only, mimicking the GJ
     filter): 95 triples kept, 34 filtered out (26%)
3. Evaluation: the paper's exact metric scripts. One fix needed: the repo
   hardcodes `device="cuda:7"` in `graph_matching.py`; patched to fall back to
   mps/cpu on Mac.

## Results (15 docs, SCIERC)

| Metric | Naive | Judged | Change |
|---|---|---|---|
| G-BERTScore Precision | 0.9006 | 0.9391 | +0.039 |
| G-BLEU Precision | 0.7477 | 0.7842 | +0.037 |
| G-ROUGE Precision | 0.6913 | 0.7387 | +0.047 |
| G-BERTScore Recall | 0.7410 | 0.5725 | -0.169 |
| G-BERTScore F1 | 0.7842 | 0.6880 | -0.096 |
| Triple Match F1 | 0.2742 | 0.2491 | -0.025 |

Reference points from the paper (full 100-doc SCIERC): GPT-4o-mini baseline
G-BS F1 = 0.6882, GraphJudge = 0.7283. (Not directly comparable: we used 15
docs and a different extraction model.)

## The honest takeaway (bring this to the meeting)

Judging raised precision on every single metric - that is exactly the effect
the GJ module exists for. But our crude "delete anything questionable" filter
also threw away correct triples, so recall fell harder and F1 went down.

This is precisely WHY the paper fine-tunes a judge instead of using rules or
zero-shot filtering: a trained judge learns to remove only the actually-wrong
triples, keeping recall high while precision rises. Our mini-experiment
reproduces the problem the paper solves, and shows the evaluation machinery
works end to end on our hardware.

It also validates Tao's instruction: triplet accuracy (precision) is the thing
to control first, and the filter quality decides whether the KG improves or
just shrinks.

## Files

- Predictions: `GraphJudge/datasets/GPT4o_mini_result_SCIERC/Demo/`
  (claude_naive_graphs.txt, claude_judged_graphs.txt, gold_subset.txt)
- Patched: `GraphJudge/graph_evaluation/metrics/graph_matching.py` (device fix)
- Repro command:
  `cd GraphJudge/graph_evaluation && ../.venv/bin/python metrics/eval.py --pred_file ../datasets/GPT4o_mini_result_SCIERC/Demo/claude_naive_graphs.txt --gold_file ../datasets/GPT4o_mini_result_SCIERC/Demo/gold_subset.txt`

## Next steps

1. Run the real judge: download released LoRA weights (HaoyuHuang2/graphjudger)
   + Llama-2-7b base. 16GB Mac is borderline for a 7B model; plan for HPRC.
2. Scale to all 100 SCIERC test docs with a scripted extraction LLM (needs an
   API key: OpenAI to match the paper, or swap in Claude/other in
   chat/run_chatgpt_*.py, the api_model() function is 10 lines).
3. Then adapt to the animal science corpus.
