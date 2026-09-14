# Directed Studies - KGCompass (ECEN 685, Fall 2026)

Knowledge graph construction and evaluation research under Prof. Jian Tao,
TAU Group, Texas A&M University.

## Focus

Implementing and extending **GraphJudge** ("Can LLMs be Good Graph Judge for
Knowledge Graph Construction?", EMNLP 2025, arXiv 2411.17388) toward an animal
science knowledge graph with verified triplet accuracy, feeding two research
directions: evaluation of KG-construction approaches, and graph pruning for
accuracy.

## Repo contents

- `STUDY_PLAN.md` - semester plan, capstone vs directed studies split
- `IMPLEMENTATION_PLAN.md` - phased plan for reproducing and extending GraphJudge
- `LEARNING_GUIDE.md` - beginner path into KGs and LLMs (all videos verified)
- `RESULTS_DEMO.md` - first reproduction results and the precision/recall lesson
- `experiments/scierc-demo/` - prediction files, gold subset, and the device
  patch from the first local run of the GraphJudge evaluation pipeline
- `AI_USAGE.md` - disclosure of AI tool usage in this work

Not tracked here: the upstream GraphJudge clone (get it from
https://github.com/hhy-huang/GraphJudge) and the paper PDF (arXiv 2411.17388).

## Reproducing the demo

```bash
git clone https://github.com/hhy-huang/GraphJudge
cd GraphJudge
python3 -m venv .venv && source .venv/bin/activate
pip install torch numpy scipy scikit-learn networkx nltk rouge_score bert_score spacy tqdm pandas
git apply ../experiments/scierc-demo/device-fix.patch   # mac: cuda:7 -> mps/cpu
mkdir -p datasets/GPT4o_mini_result_SCIERC/Demo
cp ../experiments/scierc-demo/*.txt datasets/GPT4o_mini_result_SCIERC/Demo/
cd graph_evaluation
python metrics/eval.py \
  --pred_file ../datasets/GPT4o_mini_result_SCIERC/Demo/claude_naive_graphs.txt \
  --gold_file ../datasets/GPT4o_mini_result_SCIERC/Demo/gold_subset.txt
```
