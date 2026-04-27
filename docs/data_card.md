# DiffSpot Data Card

## Summary

- **Total instances**: 6,000
- **Splits**: 1,500 easy + 1,500 medium + 1,500 hard + 1,500 no-diff
- **Granularity**: CSS-attribute-level mutations (12 operators)
- **GT source**: programmatic (HTML mutation operator records)
- **License**: CC BY-NC 4.0 (see [`LICENSE-DATA.md`](../LICENSE-DATA.md))

## Splits

| Split | # items | # mutations per item | Mix |
|---|---|---|---|
| `easy`    | 1,500 | 1 | high-significance only |
| `medium`  | 1,500 | 2 | mixed significance |
| `hard`    | 1,500 | 3 | includes low-significance |
| `no_diff` | 1,500 | 0 | re-rendering of same HTML, allows minor render noise |

## Mutation operators

| Operator | Category | Significance |
|---|---|---|
| `color`        | color       | high |
| `remove`       | structure   | high |
| `text`         | content     | high |
| `layout`       | layout      | high |
| `order_swap`   | structure   | high |
| `visibility`   | visibility  | high |
| `font_size`    | font        | low |
| `border`       | border      | low |
| `rounded`      | border      | low |
| `spacing`      | spacing     | low |
| `alignment`    | alignment   | low |
| `opacity`      | opacity     | low |

## Domain & language distribution

- **Domains**: 15 categories, no single domain > 15%
- **Languages**: en 90% / ja 7.7% / zh 1.8% / ko 0.6%
- **URL uniqueness**: every (image_a, image_b) pair comes from a unique URL across the entire benchmark

## Source pipeline

```
~3M rendered web pages (proprietary crawl)
    -> auto-filter (HTML length, PII, NSFW, dynamic-content tags, height)
~2M candidates
    -> stratified sample (15 domains x 3 complexity buckets)
~10K candidates
    -> VLM visual quality check + domain re-classification
~8K usable candidates
    -> final selection
6K test set (frozen)

Selection rate: 0.17%
```

## What's distributed

- Pre-rendered screenshot pairs (PNG)
- Programmatic GT for has-diff items: list of (operator, target_element_xpath, before_value, after_value)
- English natural-language GT description
- Per-item metadata: id, split, domain, language, mutation_types

What is **not** distributed: the original third-party HTML/CSS/JS.

## Known limitations

- All mutations are programmatic — does not cover human-introduced design changes that programmatic operators can't express
- Screenshot rendering uses a single viewport size (TBD); cross-viewport diffs are out of scope
- The no-diff split allows minor browser-rendering noise; this is intentional but means a perfectly nitpicky model can score above 0% hallucination on this split

## Intended uses

- Evaluating VLMs on web-UI visual change detection
- Studying VLM failure modes by mutation type and difficulty
- Reference distribution for training data targeting visual diff capability

## Out-of-scope uses

- Production UI regression testing without further validation
- Commercial use without separate licensing
