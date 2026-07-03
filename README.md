# How to Choose an LLM in 2026 — A Data-Driven Value Analysis

A Python analysis of 453 LLMs (across 47 providers) to answer a simple question: **which models are actually worth paying for, and which are just riding on brand name?**

Built entirely with `pandas` and `matplotlib` — no ML, just data cleaning, aggregation, and a couple of algorithms written from scratch (Pareto frontier, dominated-model detection).

## Dataset

[LLM Price-Performance Tracker](https://www.kaggle.com/datasets/kanchana1990/llm-price-performance-tracker-march-2026) (Kaggle, March 2026 snapshot) — pricing, speed, and benchmark scores (intelligence index, coding, math, reasoning, chatbot preference) for 453 models, sourced from Artificial Analysis and Arena AI.

313 of the 453 models have complete cost + intelligence data and form the core of this analysis.

## What's in here

| File | What it is |
|---|---|
| `analysis.py` | Full analysis script — run this top to bottom |
| `value_frontier.png` | Chart: intelligence vs. cost, with the Pareto frontier highlighted |
| `speed_vs_cost.png` | Chart: does price buy you speed? (spoiler: no) |
| `provider_landscape.png` | Chart: providers by typical model quality vs. cost |
| `LLM_Value_Analysis_Report.md` | Full write-up of all findings |

## Key findings

**1. Only 5% of models are a genuinely good deal.** Of 313 models, just 16 are on the "value frontier" — meaning no cheaper model matches their intelligence. Everything else is mathematically a worse deal than something already on the market.

**2. You don't pay for speed.** Correlation between cost and output speed: **-0.20**. Pricier models trend *slightly slower*, not faster — premium pricing buys reasoning depth, not throughput.

**3. Open-source isn't a shortcut to quality.** Open-source models are ~9x cheaper on the median, but proprietary models are nearly 2x smarter on a typical basis. Open-source only wins at the very top of the pack, not on average.

**4. Legacy flagships are a silent tax.** 97% of models are "dominated" (beaten on both cost and intelligence by something else) — mostly older generations losing to their own successors. GPT-4, o1-family, and Claude 3/4 Opus are the worst offenders. 8 of the 15 worst-dominated models are Claude Opus variants alone.

**5. There's no single "best" model.** OpenAI wins coding and math, Google wins reasoning and knowledge QA, Anthropic wins human preference (chatbot arena). Gemini 3.1 Pro Preview is the strongest generalist, landing top-3 in 3 of 5 categories.

**6. Volume ≠ quality.** Alibaba ships the most models (60) but ranks low on median intelligence. OpenAI and Google have the single smartest models but rank mid-pack on median — wide portfolios (nano to flagship) drag the typical model down. Anthropic's tighter lineup is more consistently strong.

## Methodology notes

- **Value frontier**: sort models by cost ascending, keep a model only if its intelligence score beats every cheaper model seen so far.
- **Dominated models**: a model is dominated if another model is at least as cheap AND at least as smart, with a strict improvement on at least one dimension. O(n²) comparison, fine at this scale (~98k comparisons for 313 models).
- All aggregate stats use **median**, not mean, where possible — providers and license types have skewed distributions (a few outlier flagships), and mean would overstate "typical" quality.

## Running it

```bash
pip install pandas matplotlib
python analysis.py
```

Requires the dataset CSV in the same directory (see Dataset section above for the Kaggle link).

## Limitations

- Single snapshot in time (March 2026) — this is a fast-moving market, re-run periodically.
- Benchmark scores (coding, math, reasoning) are third-party evaluations (Artificial Analysis, Arena AI) — treat as directional, not gospel.
- `chatbot_arena_elo` has heavy missing data (~46 of 453 models) — the human-preference ranking is based on a much smaller sample than the others.
