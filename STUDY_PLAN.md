# KGCompass Directed Studies - Study Plan

**Course:** ECEN 685-688 (Directed Studies) under Prof. Jian Tao
**Project:** KGCompass - knowledge graph construction and reasoning with LLMs
**Team:** Sumanth (Nalamalapu), Deepmoy Hazra, Srikar Sankranti
**Semester:** Fall 2026
**My angle:** I have built KG-based retrieval systems before and worked on KG problems with PhD interns at LinkedIn. Goal is to turn that experience into research output (papers) this semester.

---

## Project split: Capstone vs Directed Studies (confirmed with Sumanth, verify with Tao)

Both involve knowledge graphs. The boundary:

**Capstone (STAT 683) = BUILD.** Construct the animal science knowledge graph
end to end: data ingestion, extraction pipeline, the deployed KG, GitHub repo,
demo. Graded on deployment, repo, sponsor feedback, reports.

**Directed Studies (ECEN 685) = RESEARCH.** Use that KG as a testbed for two papers:
1. **Evaluation paper:** systematic comparison of KG-construction approaches
   (GraphJudge, PiVe, KGGen, iText2KG, RAKG) on the animal science domain.
2. **Pruning paper:** node/edge pruning strategies and their effect on KG
   accuracy. Complementary to GraphJudge: the judge filters bad triples during
   construction, pruning cleans the graph after construction.

One line for meetings: "Capstone builds the KG; directed studies experiments
on it." To confirm with Tao and Dr. Zhou: the capstone project of record
switching from LLHS to the animal science KG, and the scope split between the
two courses stated openly to both professors.

---

## Core paper (read first, know cold)

**GraphJudge - "Can LLMs be Good Graph Judge for Knowledge Graph Construction?"**
File: `GraphJudge_KG_Construction_2411.17388.pdf` (arXiv 2411.17388, HKUST + Huawei + PKU)
Code: https://github.com/hhy-huang/GraphJudge

One-paragraph summary to remember:
Text-to-graph (T2G) with a naive LLM fails in 3 ways: noise in real documents, missing domain knowledge, and hallucinated triples. GraphJudge fixes this with 3 modules: (1) ECTD - extract entities, rewrite the document entity-centric and clean, then over-generate candidate triples with GPT-4o-mini (recall first); (2) KASFT - LoRA fine-tune LLaMA-2-7B on a yes/no "is this triple true given this document" task, using ground-truth triples plus corrupted-tail negatives; (3) GJ - the fine-tuned 7B judge filters every candidate triple. Judge hits 90%+ accuracy, beating GPT-4o (~64-74%) at judging. SOTA F1 on REBEL-Sub, GenWiki, SCIERC, Re-DocRED using semantic metrics (G-BERTScore, G-BLEU, G-ROUGE). Trains on a single 48GB GPU, 500 steps.

The transferable pattern: **big model for recall, small fine-tuned model for precision.**

Open problems the authors admit (= paper opportunities):
- Only flat entity-level triples; richer knowledge units unexplored
- Ground-truth KGs used for eval are themselves questionable; no good self-supervised eval exists
- Better KG construction + evaluation methods are open

---

## Week-by-week plan

### Week 1 (Sep 2-8) - Foundations
- [x] Read GraphJudge fully, including appendices (prompt templates in Appendix I are directly reusable)
- [ ] Group kickoff meeting with Sumanth (context + materials)
- [ ] Clone the GraphJudge repo, read the code structure, see what runs without a GPU
- [ ] Write down 3 questions for Prof. Tao about the scope of KGCompass

### Week 2 (Sep 9-15) - Background reading
Read these (all cited in GraphJudge, they form the landscape):
- [ ] PiVe (arXiv 2305.12392) - iterative verifier prompting, the main rival idea
- [ ] KGGen (arXiv 2502.09956) - entity clustering to reduce KG sparsity
- [ ] iText2KG (arXiv 2409.03284) - incremental zero-shot KG construction
- [ ] RAKG (arXiv 2504.09823) - document-level retrieval-augmented KG construction
- [ ] GraphRAG (arXiv 2404.16130) - why KG quality matters downstream
- [ ] KG-LLaMA (arXiv 2308.13916) - the fine-tuning recipe KASFT is based on
Skim only: Pan et al. "Unifying LLMs and KGs: A Roadmap" for the big picture.

### Week 3 (Sep 16-22) - Reproduce
- [ ] Get GraphJudge (or a scaled-down version) running end to end on one dataset (REBEL-Sub sample)
- [ ] Check TAMU HPRC access for GPU time (also counts toward TAMIDS/HPRC short-course requirement for capstone)
- [ ] Swap in a current cheap model (e.g. Claude Haiku or GPT-4o-mini) for the ECTD module, compare
- [ ] Team sync: divide modules among the three of us

### Weeks 4-6 (Sep 23 - Oct 13) - Extend (pick 1-2 with the team + Tao)
Candidate directions, roughly ordered by feasibility:
1. **Better judges:** replace LLaMA-2-7B with a modern small model (Llama-3.x, Qwen, Phi); measure judgement accuracy vs cost
2. **Beyond triples:** judge richer knowledge units (n-ary relations, events, temporal facts) - directly attacks their stated limitation
3. **Self-supervised eval:** use the MCQ-retention trick from their Appendix G as an evaluation metric itself (no ground-truth KG needed) - novel and cheap
4. **Domain application:** build a domain KG (e.g. health/nutrition, ties into my LLHS capstone data, or an engineering domain Tao cares about)
5. **KG-for-RAG loop:** measure how judge-filtered KGs improve GraphRAG answer quality end to end

### Weeks 7-10 (Oct 14 - Nov 10) - Build and experiment
- [ ] Lock the research question, run main experiments
- [ ] Weekly progress notes (reuse for any required reports)
- [ ] Midpoint check-in with Prof. Tao

### Weeks 11-14 (Nov 11 - Dec 8) - Write
- [ ] Draft paper (workshop or arXiv preprint first; target venue with Tao's advice)
- [ ] Final presentation / report for ECEN 685
- [ ] Clean public GitHub repo

---

## Skills to sharpen along the way
- LoRA fine-tuning (peft + a 7B model) - do one small run early, even a toy one
- Prompt design for extraction (steal Appendix I templates as the starting point)
- KG eval metrics: G-BERTScore, G-BLEU, G-ROUGE (Appendix B has formulas)
- HPRC/Slurm basics for GPU jobs

## Standing rules for myself
- Every week: 1 paper read + 1 experiment or code step, however small
- Keep a running NOTES.md in this folder (what I read, what I ran, what broke)
- Be able to explain every part of anything I submit
- Ask Tao early about AI-tool usage policy and cite tools used

## Links
- GraphJudge paper: https://arxiv.org/abs/2411.17388
- GraphJudge code: https://github.com/hhy-huang/GraphJudge
- Prof. Tao TAU Group / Digital Twin Lab pages
