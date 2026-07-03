"""
LLM Value Analysis — How to Choose an LLM in 2026
---------------------------------------------------
Analyzing the LLM Price-Performance Tracker (Kaggle, March 2026) to figure out
which models are actually worth paying for, and which ones are just riding on
brand name.

Six questions I wanted answered:
1. Which models give you the most intelligence for your money? (value frontier)
2. Does paying more actually get you a faster model?
3. Is open-source really as good as people say?
4. Which models are just a bad deal at this point?
5. Is there one "best" model, or does it depend on what you're doing?
6. Which providers are consistently good vs. just have one hit model?
"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('llm_price_performance_tracker_2026-03-31.csv')
print(f"Loaded {df.shape[0]} models with {df.shape[1]} columns")

# A lot of models are missing either a price or a benchmark score, so for most
# of this analysis I'll only look at rows where we actually have both.
core = df.dropna(subset=['blended_cost_usd_per_1m', 'aa_intelligence_index']).copy()
print(f"{core.shape[0]} models have both a price and an intelligence score — using these going forward")


# =========================================================
# 1. VALUE FRONTIER — where does your money actually buy you something?
# =========================================================
# The idea: sort models cheapest to priciest, then walk through them and only
# keep a model if it's smarter than every cheaper model we've already seen.
# Anything that doesn't set a new "smartest so far" record is a bad deal —
# something cheaper already matches or beats it.

cheapest_first = core.sort_values('blended_cost_usd_per_1m')

frontier_models = []
best_intelligence_so_far = -1

for _, model in cheapest_first.iterrows():
    if model['aa_intelligence_index'] > best_intelligence_so_far:
        frontier_models.append(model)
        best_intelligence_so_far = model['aa_intelligence_index']

frontier = pd.DataFrame(frontier_models)
print(f"\n{len(frontier)} of {len(core)} models are actually 'good deals' (on the value frontier):")
print(frontier[['model_name', 'provider', 'blended_cost_usd_per_1m', 'aa_intelligence_index']])

plt.figure(figsize=(9, 5.5))
plt.scatter(core['blended_cost_usd_per_1m'], core['aa_intelligence_index'],
            alpha=0.4, label='All models')
plt.plot(frontier['blended_cost_usd_per_1m'], frontier['aa_intelligence_index'],
         color='red', marker='o', label='Value Frontier')
plt.xscale('log')
plt.xlabel('Blended Cost ($ per 1M tokens)')
plt.ylabel('Intelligence Index')
plt.title('LLM Value Frontier: Intelligence vs. Cost')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('value_frontier.png', dpi=150, bbox_inches='tight')
plt.show()


# =========================================================
# 2. SPEED vs COST — are you paying extra to get a faster model?
# =========================================================

speed_data = df.dropna(subset=['blended_cost_usd_per_1m', 'output_tokens_per_second']).copy()

speed_cost_correlation = speed_data['blended_cost_usd_per_1m'].corr(speed_data['output_tokens_per_second'])
print(f"\nCorrelation between cost and speed: {speed_cost_correlation:.2f}")
# Spoiler: it's basically zero, slightly negative. You're not paying for speed.

print("\nFastest models overall:")
print(speed_data.sort_values('output_tokens_per_second', ascending=False)
      .head(10)[['model_name', 'provider', 'output_tokens_per_second', 'blended_cost_usd_per_1m']])

print("\nMost expensive models — let's see how fast they actually are:")
print(speed_data.sort_values('blended_cost_usd_per_1m', ascending=False)
      .head(10)[['model_name', 'provider', 'blended_cost_usd_per_1m', 'output_tokens_per_second']])

plt.figure(figsize=(9, 5.5))
plt.scatter(speed_data['blended_cost_usd_per_1m'], speed_data['output_tokens_per_second'], alpha=0.4)
plt.xscale('log')
plt.xlabel('Blended Cost ($ per 1M tokens)')
plt.ylabel('Output Speed (tokens/second)')
plt.title(f'Speed vs. Cost (correlation = {speed_cost_correlation:.2f})')
plt.grid(True, alpha=0.3)
plt.savefig('speed_vs_cost.png', dpi=150, bbox_inches='tight')
plt.show()


# =========================================================
# 3. OPEN SOURCE vs PROPRIETARY — is the hype justified?
# =========================================================

by_license = core.groupby('is_open_source').agg(
    n_models=('model_name', 'count'),
    median_cost=('blended_cost_usd_per_1m', 'median'),
    mean_cost=('blended_cost_usd_per_1m', 'mean'),
    median_intelligence=('aa_intelligence_index', 'median'),
    mean_intelligence=('aa_intelligence_index', 'mean'),
    best_intelligence=('aa_intelligence_index', 'max'),
).round(2)

print("\nOpen-source vs. proprietary, side by side:")
print(by_license)
# Open-source is way cheaper on the median, but proprietary models are
# noticeably smarter *on average*. Open-source only really competes with
# proprietary at the very top of the pack, not typically.


# =========================================================
# 4. DOMINATED MODELS — who's just not worth it anymore?
# =========================================================
# A model is "dominated" if there's another model that's at least as cheap
# AND at least as smart (and strictly better on one of the two). If that's
# true, there's genuinely no reason to pick the dominated model.

ranked = core.reset_index(drop=True)
costs = ranked['blended_cost_usd_per_1m'].values
intelligence = ranked['aa_intelligence_index'].values

dominated_rows = []
for i in range(len(ranked)):
    for j in range(len(ranked)):
        if i == j:
            continue
        cheaper_or_equal = costs[j] <= costs[i]
        smarter_or_equal = intelligence[j] >= intelligence[i]
        strictly_better_somewhere = costs[j] < costs[i] or intelligence[j] > intelligence[i]
        if cheaper_or_equal and smarter_or_equal and strictly_better_somewhere:
            dominated_rows.append(i)
            break  # one reason to call it dominated is enough, move to the next model

dominated = ranked.iloc[dominated_rows]
print(f"\n{len(dominated)} of {len(ranked)} models ({len(dominated) / len(ranked) * 100:.0f}%) "
      f"are beaten on both price and intelligence by something else")

print("\nWorst offenders — expensive AND clearly outclassed:")
print(dominated.sort_values('blended_cost_usd_per_1m', ascending=False)
      .head(15)[['model_name', 'provider', 'blended_cost_usd_per_1m', 'aa_intelligence_index', 'is_open_source']])
# A lot of these are just older generations of the same model family
# (GPT-4, o1, Claude 3/4 Opus) — basically a "legacy tax" for not upgrading.


# =========================================================
# 5. BEST MODEL PER USE CASE — there's no single "best" model
# =========================================================

def top_models_for(benchmark_column, n=5):
    """Return the top n models ranked by a given benchmark column."""
    available = df.dropna(subset=[benchmark_column, 'blended_cost_usd_per_1m']).copy()
    return available.sort_values(benchmark_column, ascending=False).head(n)[
        ['model_name', 'provider', benchmark_column, 'blended_cost_usd_per_1m', 'is_open_source']
    ]

use_cases = {
    'BEST FOR CODING': 'aa_coding_index',
    'BEST FOR MATH': 'aa_math_index',
    'BEST FOR KNOWLEDGE / DOCUMENT QA': 'mmlu_pro',
    'BEST FOR HARD REASONING': 'gpqa_diamond',
    'BEST GENERAL CHATBOT (human preference)': 'chatbot_arena_elo',
}

for label, column in use_cases.items():
    print(f"\n=== {label} ===")
    print(top_models_for(column))
# Different providers win different categories — OpenAI for coding/math,
# Google for reasoning/knowledge, Anthropic for chatbot preference.
# "Best model" really means "best model for what you're doing."


# =========================================================
# 6. PROVIDER LANDSCAPE — who's consistently good vs. one-hit-wonders?
# =========================================================

by_provider = core.groupby('provider').agg(
    n_models=('model_name', 'count'),
    median_cost=('blended_cost_usd_per_1m', 'median'),
    median_intelligence=('aa_intelligence_index', 'median'),
    best_intelligence=('aa_intelligence_index', 'max'),
).round(2)

# Ignore providers with only 1-2 models — not enough to call it a "typical" lineup
by_provider = by_provider[by_provider['n_models'] >= 3].sort_values('median_intelligence', ascending=False)

print("\nProviders ranked by typical (median) model quality:")
print(by_provider)

plt.figure(figsize=(9, 6))
plt.scatter(by_provider['median_cost'], by_provider['median_intelligence'],
            s=by_provider['n_models'] * 15, alpha=0.5)  # bigger bubble = more models

for provider_name, row in by_provider.iterrows():
    plt.annotate(provider_name, (row['median_cost'], row['median_intelligence']), fontsize=8)

plt.xscale('log')
plt.xlabel('Median Cost ($ per 1M tokens)')
plt.ylabel('Median Intelligence Index')
plt.title('Provider Landscape (bubble size = number of models)')
plt.grid(True, alpha=0.3)
plt.savefig('provider_landscape.png', dpi=150, bbox_inches='tight')
plt.show()
# Interesting twist: OpenAI and Google have the single smartest models,
# but rank mid-pack on median — they ship a wide range from nano to
# flagship, which drags the "typical" model down. Smaller labs with a
# tighter lineup (Anthropic, Xiaomi, MiniMax) look more consistent.