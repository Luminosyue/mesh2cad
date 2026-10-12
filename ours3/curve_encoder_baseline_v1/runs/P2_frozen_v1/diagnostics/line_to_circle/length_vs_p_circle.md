# LINE length vs P(CIRCLE) — P2 test

n_LINE=16486, LINE→CIRCLE hard FP=1248

## Correlation

- Pearson(length, P(CIRCLE)) = **0.4716**
- Pearson(log10 length, P(CIRCLE)) = **0.3751**
- Spearman(length, P(CIRCLE)) = **0.0278**
- Spearman(log10 length, P(CIRCLE)) = **0.0278**

## Length deciles (GT=LINE)

| decile | n | length med | P(CIRCLE) mean | P(CIRCLE) med | P(CIRCLE) P90 | FP rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0–10% | 1649 | 0.01813 | 0.020 | 0.003 | 0.063 | 0.1% |
| 10–20% | 1647 | 0.0434 | 0.032 | 0.005 | 0.104 | 0.1% |
| 20–30% | 1649 | 0.09647 | 0.034 | 0.005 | 0.088 | 1.0% |
| 30–40% | 1615 | 0.1626 | 0.019 | 0.003 | 0.039 | 0.4% |
| 40–50% | 1670 | 0.2411 | 0.025 | 0.007 | 0.055 | 0.5% |
| 50–60% | 1654 | 0.4232 | 0.035 | 0.005 | 0.059 | 1.8% |
| 60–70% | 1617 | 0.796 | 0.107 | 0.004 | 0.576 | 10.7% |
| 70–80% | 1687 | 1.475 | 0.050 | 0.002 | 0.033 | 4.9% |
| 80–90% | 1639 | 3.464 | 0.092 | 0.000 | 0.475 | 10.0% |
| 90–100% | 1659 | 7.94 | 0.399 | 0.357 | 0.912 | 46.0% |

## Verdict

Spearman across *all* LINEs is weak (0.028) because Q1–Q6 are flat near zero.
The effect is a **heavy-tail / threshold** pattern, not a smooth linear rise:

| | bottom decile (shortest) | top decile (longest) |
| --- | ---: | ---: |
| length median | 0.01813 | 7.94 |
| mean P(CIRCLE) | 0.020 | 0.399 |
| median P(CIRCLE) | 0.003 | 0.357 |
| P90 P(CIRCLE) | 0.063 | 0.912 |
| hard FP rate | 0.1% | 46.0% |

- Top/bottom mean P(CIRCLE) ratio ≈ **19.5×**
- Pearson(length, P(CIRCLE)) = **0.472** (pulled by the long tail)
- **Sit solid for long LINE:** once length enters the upper deciles, CIRCLE logit/prob rises sharply and FP explodes (46% in Q10). Classifier has a spurious **scale → circle** association concentrated on long segments.

Figure: `length_vs_p_circle.png`
