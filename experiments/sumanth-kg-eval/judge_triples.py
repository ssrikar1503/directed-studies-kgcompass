"""Reproducible triple judge using Claude Sonnet via the Anthropic API.

Re-runs the 50-triple accuracy judgement for Sumanth's group13 KG sample.
Requires: pip install anthropic, and ANTHROPIC_API_KEY in the environment
(or an `ant auth login` profile).

Usage:
    python judge_triples.py            # writes api_sonnet_verdicts.csv

The three source-paper texts must be in ./papers/ (created by pdftotext).
The paper texts are sent once as a cached system prefix, so the 50 calls
mostly read from cache (~90% input-cost reduction after the first call).
"""
import csv
import json
import pathlib
import re

import anthropic

MODEL = "claude-sonnet-5-5"
BASE = pathlib.Path(__file__).parent

PAPERS = {
    "schone": (BASE / "papers/schone2006_pig_iodine.txt").read_text(),
    "li": (BASE / "papers/li2012_fattening_pigs.txt").read_text(),
    "rottger": (BASE / "papers/rottger2011_broilers.txt").read_text(),
}

SYSTEM = [
    {
        "type": "text",
        "text": (
            "You are an independent scientific fact-checking judge for knowledge-graph "
            "triples extracted from animal science papers. Judge the SURFACE form of each "
            "triple (what a KG consumer would read), not its charitable intended meaning.\n"
            "Verdicts:\n"
            "- correct: directly supported by the paper text as stated.\n"
            "- imprecise: the idea is in the paper but the triple misstates it (wrong "
            "granularity, dropped condition such as 'excess', uninformative relation, "
            "slightly wrong head/tail entity).\n"
            "- wrong: contradicted by the paper, inverted direction, a cited claim the "
            "paper itself refutes, or garbled as stated.\n"
            "Answer ONLY with JSON: {\"verdict\": \"correct|imprecise|wrong\", "
            "\"evidence\": \"<one short sentence citing the paper passage>\"}\n\n"
            "=== PAPER 1: Schone et al. 2006 (pig iodine, Meat Science) ===\n"
            + PAPERS["schone"]
            + "\n\n=== PAPER 2: Li et al. 2012 (fattening pigs, Eur J Nutr) ===\n"
            + PAPERS["li"]
            + "\n\n=== PAPER 3: Rottger et al. 2011 (broilers, Br Poult Sci) ===\n"
            + PAPERS["rottger"]
        ),
        "cache_control": {"type": "ephemeral"},
    }
]

client = anthropic.Anthropic()
rows = list(csv.DictReader(open(BASE / "sample50.csv")))
out = []
for r in rows:
    prompt = (
        f"Triple: ({r['subject']}) --[{r['relation']}]--> ({r['object']})\n"
        f"Stated effect direction: {r['effect']}\n"
        f"Source paper(s): {r['papers']}\n"
        f"Extractor's own description: {r['descriptions']}\n"
        "Judge this triple against the cited paper(s)."
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    m = re.search(r"\{.*\}", text, re.S)
    try:
        v = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        v = {}
    out.append(
        [r["idx"], v.get("verdict", "PARSE_ERROR"), v.get("evidence", text[:160])]
    )
    print(r["idx"], out[-1][1])

with open(BASE / "api_sonnet_verdicts.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["idx", "verdict", "evidence"])
    w.writerows(out)
print("wrote api_sonnet_verdicts.csv")
