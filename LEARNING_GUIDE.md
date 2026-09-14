# KGCompass Basics - Learn From Zero

This guide assumes you know nothing. Follow it top to bottom. Each step has:
what the idea is (in plain words), why you need it for the project, and a real
YouTube video (every link tested and working).

Total watch time is about 6-7 hours. Spread it over 1-2 weeks. Do not binge it
in one day, you will remember nothing.

---

## Step 1: What is a graph? (the math kind, not a chart)

**Plain words:** A graph is just dots connected by lines. The dots are called
nodes (or vertices) and the lines are called edges. Your friend circle is a
graph: people are nodes, friendships are edges. Google Maps is a graph:
intersections are nodes, roads are edges.

**Why you need it:** A knowledge graph is literally this, nothing scarier.

**Watch:** Introduction to Graph Theory: A Computer Science Perspective (Reducible, ~16 min)
https://www.youtube.com/watch?v=LFKZLXVO-Dg

---

## Step 2: What is a Knowledge Graph?

**Plain words:** A knowledge graph is a graph where nodes are real-world things
(people, places, proteins, companies) and edges are facts connecting them.
Facts are stored as triples: (head, relation, tail).
Example: (Einstein, born_in, Germany). Millions of these triples together form
a web of knowledge a computer can search and reason over. Google uses one to
show those info boxes when you search a celebrity.

**Why you need it:** This is the entire output of your project. GraphJudge's
whole job is building these triples from plain text, correctly.

**Watch:** What is a Knowledge Graph? (IBM, ~5 min)
https://www.youtube.com/watch?v=y7sXDpffzQQ

---

## Step 3: What is a neural network?

**Plain words:** A neural network is a big pile of simple math units (numbers
multiplied by weights, added up, squashed). You show it examples, it adjusts
its weights to get better at predicting. That adjusting is called training.
That is all "learning" means here.

**Why you need it:** LLMs are giant neural networks. You cannot understand
fine-tuning without this.

**Watch:** But what is a neural network? (3Blue1Brown, ~18 min)
https://www.youtube.com/watch?v=aircAruvnKk

---

## Step 4: What is a Large Language Model (LLM)?

**Plain words:** An LLM (like ChatGPT or Claude) is a neural network trained on
huge amounts of text to do one simple thing: predict the next word. Do that
extremely well at extremely large scale and it starts writing essays, code and,
for us, extracting facts from documents.

**Why you need it:** In your project, LLMs are the workers. One LLM extracts
triples from text, another LLM checks if those triples are true.

**Watch (short version first):** Large Language Models explained briefly (3Blue1Brown, ~8 min)
https://www.youtube.com/watch?v=LPZh9BOjkQs

**Watch (full picture, do this one too):** [1hr Talk] Intro to Large Language Models (Andrej Karpathy, ~1 hr)
https://www.youtube.com/watch?v=zjkBMFhNj_g

---

## Step 5: What are embeddings? (how computers understand words)

**Plain words:** Computers cannot read words, only numbers. An embedding turns
a word into a list of numbers such that similar words get similar numbers.
"King" and "queen" end up close together, "king" and "banana" far apart.
Meaning becomes geometry.

**Why you need it:** The paper's evaluation metric (G-BERTScore) compares
triples by embedding similarity instead of exact spelling. Also every KG
retrieval system you will build uses embeddings.

**Watch:** Word Embedding and Word2Vec, Clearly Explained!!! (StatQuest, ~16 min)
https://www.youtube.com/watch?v=viZrOnJclY0

---

## Step 6: Transformers and attention (the engine inside LLMs)

**Plain words:** The transformer is the architecture every modern LLM uses.
Its trick is "attention": when processing a word, the model looks back at all
other words and decides which ones matter for it. In "the bank of the river",
attention is how the model knows "bank" means riverside, not money.

**Why you need it:** Every model name in the paper (LLaMA, GPT, BERT) is a
transformer. You need only the intuition, not the full math.

**Watch:** Transformers, the tech behind LLMs (3Blue1Brown, ~27 min)
https://www.youtube.com/watch?v=wjZofJX0v4M

**Optional deeper:** Attention in transformers, step-by-step (3Blue1Brown, ~26 min)
https://www.youtube.com/watch?v=eMlx5fFNoYc

---

## Step 7: Fine-tuning (teaching an existing model a new job)

**Plain words:** Training an LLM from scratch costs millions. Fine-tuning
takes an already-trained model and trains it a little more on your own small
dataset so it becomes an expert at your specific task. Like hiring an
experienced chef and teaching them your one signature dish.

**Why you need it:** The heart of GraphJudge. They fine-tune LLaMA-2-7B to
answer "is this triple true given this document, yes or no." That is the KASFT
module.

**Watch:** Fine-tuning Large Language Models (Shaw Talebi, ~15 min)
https://www.youtube.com/watch?v=eC6Hd1hFvos

---

## Step 8: LoRA (fine-tuning on a student budget)

**Plain words:** Full fine-tuning updates billions of weights, which needs
monster GPUs. LoRA freezes the original model and trains only a tiny add-on
(a "low-rank" patch), often under 1% of the weights. Result: nearly the same
quality at a fraction of the cost. This is why GraphJudge trains on a single
GPU in 500 steps.

**Why you need it:** When your team fine-tunes a judge model on TAMU's HPRC
cluster, you will use LoRA. Guaranteed.

**Watch:** What is LoRA? (AI Coffee Break, ~8 min)
https://www.youtube.com/watch?v=KEv-F5UkhxU

**Bonus:** LoRA explained by the inventor (Edward Hu, ~11 min)
https://www.youtube.com/watch?v=DhRoTONcyZE

---

## Step 9: RAG (why knowledge graphs matter downstream)

**Plain words:** LLMs make things up (hallucinate) and their knowledge goes
stale. RAG (Retrieval-Augmented Generation) fixes this: before answering, the
system first retrieves relevant documents or facts, then the LLM answers using
them. Like an open-book exam instead of memory. GraphRAG is the version where
the "book" is a knowledge graph.

**Why you need it:** This is WHY anyone cares about building clean KGs. Better
KG in, better answers out. It also connects directly to your LinkedIn KG
retrieval experience.

**Watch:** What is Retrieval-Augmented Generation (RAG)? (IBM, ~7 min)
https://www.youtube.com/watch?v=T-D1OfcDW1M

---

## Step 10 (optional, for later): Build a tiny GPT yourself

**Plain words:** The single best way to truly understand LLMs is to build a
baby one in code, line by line. Karpathy does exactly that in this legendary
video. Save it for a free weekend after the steps above.

**Watch:** Let's build GPT: from scratch, in code (Andrej Karpathy, ~2 hrs)
https://www.youtube.com/watch?v=kCc8FmEb1nY

---

## Now re-read the paper with new eyes

After steps 1-9, open `GraphJudge_KG_Construction_2411.17388.pdf` again and
translate it in your head:

| Paper term | What it actually is |
|---|---|
| Text-to-Graph (T2G) | turn a document into triples (Step 2) |
| ECTD module | ask GPT-4o-mini to clean the text and over-extract triples (Step 4) |
| KASFT module | LoRA fine-tune LLaMA-2-7B into a yes/no fact checker (Steps 7-8) |
| Graph Judgement | run every candidate triple past the fact checker, keep the yes's |
| G-BERTScore | grade triples by embedding similarity, not exact spelling (Step 5) |
| Hallucination | LLM invented a fact not in the document (Step 9) |

If every row of that table makes sense, you understand the paper better than
most people who cite it.

## Suggested schedule

- Day 1: Steps 1-2 (graphs + knowledge graphs, ~25 min)
- Day 2: Steps 3-4 short video (neural nets + LLMs, ~30 min)
- Day 3: Step 4 Karpathy talk (~1 hr)
- Day 4: Steps 5-6 (embeddings + transformers, ~45 min)
- Day 5: Steps 7-8 (fine-tuning + LoRA, ~25 min)
- Day 6: Step 9 (RAG, ~10 min) then re-read the paper with the table above
- Weekend, someday: Step 10

Tick videos off as you finish. Watch at 1.25x if it drags, pause and rewatch
anything confusing. Confusion then rewatch is how learning feels.
