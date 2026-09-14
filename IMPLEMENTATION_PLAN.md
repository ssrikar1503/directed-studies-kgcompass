# GraphJudge Implementation Plan

Prof. Tao's ask: study arXiv 2411.17388 and implement it.
Repo cloned at: `Desktop/Directed Studies/GraphJudge/` (official code, EMNLP 2025 main conference)

## Three lucky breaks (know these before the meeting)

1. **The paper was accepted to EMNLP 2025 main conference.** Solid, peer-reviewed foundation to build on.
2. **The authors released their fine-tuned LoRA judge weights** at
   huggingface.co/HaoyuHuang2/graphjudger. We can run the judge WITHOUT
   training anything first.
3. **The repo ships the intermediate GPT-4o-mini outputs** (53MB under
   `datasets/GPT4o_mini_result_*`). So the expensive ECTD stage is already
   done for the 3 benchmark datasets. We can test judging and evaluation with
   zero API cost.

## The pipeline, mapped to the repo

| Paper module | Repo file | Needs |
|---|---|---|
| ECTD step 1: entity extraction + denoise | `chat/run_chatgpt_entity.py` | OpenAI API key |
| ECTD step 2: triple generation | `chat/run_chatgpt_triple.py` | OpenAI API key |
| KASFT: fine-tune the judge | `graph_judger/lora_finetune_{dataset}_context.py` | big GPU (HPRC) |
| GJ: judge inference (filter triples) | `graph_judger/lora_infer_batch.py` | GPU or Mac (mps supported) |
| Data glue between stages | `datasets/prepare_KGCom.ipynb` (3 cells) | just Python |
| Evaluation (G-BS / G-BL / G-RO) | `graph_evaluation/eval.sh` | BERT model download |
| Naive LLM baseline | `chat/run_chatgpt.py` | OpenAI API key |

## Phase 0 - Environment (do first, ~30 min)

```bash
cd "$HOME/Desktop/Directed Studies/GraphJudge"
python3 -m venv .venv
source .venv/bin/activate
pip install torch transformers peft datasets pandas tqdm openai bert-score jupyter sentencepiece accelerate
```

Note: repo has no requirements.txt, the list above is read from the imports.

## Phase 1 - Run evaluation on shipped results (no API key, no GPU)

Goal: understand the metrics end of the pipeline first, since Tao said
evaluation is the hard part.

1. Look at `datasets/GPT4o_mini_result_SCIERC/` (smallest dataset, 350 train / 100 test KGs)
2. Open `graph_evaluation/eval.sh`, point it at a shipped
   `test_generated_graphs.txt` and the ground truth
3. Run it, get G-BERTScore / G-BLEU / G-ROUGE numbers
4. Compare with Table 1 in the paper. If numbers are in the ballpark, we
   understand the eval machinery. This alone is a great first progress update
   for Tao.

## Phase 2 - Run the judge with released weights (Mac or HPRC)

1. Download LoRA weights from HF: `HaoyuHuang2/graphjudger`
2. Base model: `NousResearch/Llama-2-7b-hf` (needs ~14GB in fp16; on the Mac
   use mps, it will be slow but works for a small slice; full runs go to HPRC)
3. Edit `graph_judger/lora_infer_batch.py`: set `LORA_WEIGHTS` path, remove the
   hardcoded `CUDA_VISIBLE_DEVICES` line for Mac
4. Judge a small sample (50 triples) of SCIERC candidates, then run cell 3 of
   `prepare_KGCom.ipynb` to filter, then re-run Phase 1 eval on the filtered
   graph. Seeing the F1 jump = the whole paper reproduced in miniature.

## Phase 3 - Fine-tune our own judge (HPRC)

1. Get HPRC account + GPU allocation (also satisfies a capstone short-course requirement)
2. Run cell 1 of `prepare_KGCom.ipynb` to build training instructions
3. `python lora_finetune_scierc_context.py` (settings from paper Appendix C:
   batch 128, lr 3e-4, 500 steps, LoRA rank 8 on q_proj/v_proj, single 48GB GPU)
4. Compare our judge vs the released one on the same test slice

## Phase 4 - Adapt to animal science (the actual project)

This is where implementation becomes research:
1. Collect an animal science corpus with the team (papers, extension documents, whatever Tao provides)
2. Re-run ECTD on it. Two options for the LLM: OpenAI gpt-4o-mini like the
   paper, or swap `api_model()` in the chat scripts to another provider
   (the function is 10 lines, easy to swap)
3. Build graph-judgement training data for the domain (needs some ground-truth
   triples: hand-label a small gold set as a team, this doubles as the
   evaluation gold standard Tao asked about)
4. Fine-tune the judge on animal science, filter, evaluate
5. Everything beyond this (comparing approaches, pruning the graph) feeds the
   two directed-studies papers

## Division of labor suggestion (raise in team meeting)

- Triplet accuracy checking (Tao already assigned to Sumanth) = the GJ module
- One person owns ECTD + data prep for the animal science corpus
- One person owns evaluation metrics + gold-standard labeling process
- Fine-tuning runs shared once HPRC access exists

## Watch-outs

- `chat/*.py` scripts have `api_key = ""` hardcoded at the top; put keys in an
  env variable instead and never commit them
- `lora_infer_batch.py` pins an old transformers behavior (LlamaTokenizer
  assert); if installs fight, create the venv with the versions from ~2023:
  `transformers==4.34`, `peft==0.5.0` as a fallback
- The notebook `prepare_KGCom.ipynb` is the glue for everything; read it early
- Paper metrics use bert-score which downloads a BERT model on first run (fine)
