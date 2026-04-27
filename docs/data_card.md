# DiffSpot Data Card

## Summary

- **Total instances**: 4,400 (3,900 has-diff + 500 no-diff)
- **Granularity**: 13 CSS-property-level mutation operators in 4 families
- **Difficulty**: 3 tiers (Easy / Medium / Hard), magnitude-based stratification
- **GT source**: programmatic (HTML mutation operator records)
- **License**: CC BY-NC 4.0 (see [`LICENSE-DATA.md`](../LICENSE-DATA.md))

## Splits

The has-diff set is balanced: **13 operators × 3 difficulty tiers = 39 cells × 100 pairs = 3,900**.

| Split | # items | # mutations per item | Notes |
|---|---|---|---|
| `easy`    | 1,300 | 1 | largest-magnitude tier per operator |
| `medium`  | 1,300 | 1 | mid-magnitude tier |
| `hard`    | 1,300 | 1 | smallest-magnitude tier |
| `no_diff` |   500 | 0 | same HTML rendered twice; minor browser-level rendering noise allowed |

Each pair isolates a single mutation on a single targeted DOM element. Difficulty is strictly ordered **within** each operator — Hard is harder than Easy on the same operator, but cross-operator comparisons (e.g., Hard `letter_spacing` vs Easy `text`) reflect both intrinsic operator difficulty and parameter magnitude.

## Mutation operators

13 operators grouped into 4 families:

| Family | Operator | Stratification |
|---|---|---|
| **Typography** | `font_weight`     | Tailwind step distance (Easy 3–5, Medium 2, Hard 1) |
|                | `font_size`       | step distance |
|                | `letter_spacing`  | em-offset (Easy ±0.20em, Medium ±0.12em, Hard ±0.06em) |
|                | `line_height`     | em-offset |
|                | `text`            | substitution / deletion magnitude |
| **Color**      | `color`           | step distance on Tailwind palette |
|                | `opacity`         | offset magnitude |
|                | `gradient`        | step distance |
| **Layout**     | `position`        | translate magnitude |
|                | `spacing`         | margin / padding offset |
|                | `justify`         | discrete value swap |
| **Shape**      | `border`          | width / style / color |
|                | `rounded`         | border-radius step distance |

Each operator has two mutation mechanisms — a Tailwind class swap and an inline `!important` style override — both fully reproducible from the structured mutation record.

## Domain & language distribution

- **Domains**: 15 categories (e-commerce, SaaS/tool, news/media, education, government, healthcare, finance, travel, food/restaurant, real estate, portfolio, corporate, social/community, entertainment, other)
- **Languages**: natural distribution from the source crawl — predominantly English (~60%), CJK (~15%), other (~25%); language was not used as a sampling axis
- **URL uniqueness**: every pair uses a distinct source page; no URL appears twice across the 4,400 instances

## Source pipeline

```
3M+ rendered web pages (proprietary crawl)
    -> automatic filtering (HTML length, blank/solid pages, iframe/video/canvas, PII)
~2M candidates
    -> quality-based selection (qwen_similarity >= 0.75, NSFW/PII/viewport/length filters)
56,816 candidates                              # pass rate at this stage: 62.6%
    -> top-4,400 by qwen_similarity            # final similarity range [0.896, 0.979]
4,400-page test set (frozen)

Selection rate: 0.17% (stricter than Design2Code 0.4%, SWE-bench 2.5%)
```

For mutation generation:
1. Each clean page goes through grouped mode (one candidate per difficulty tier per operator) → 23,104 raw mutation candidates
2. **Grounding gate** rejects no-effect mutations (CSS shadowed) and reflow contamination (mutation cascades beyond target). Predicates: inside-bbox pixel change non-zero; outside-bbox unchanged; selector resolves in rendered DOM
3. Stratified sampling to 100 pairs per (operator × tier) cell

## What's distributed

- Pre-rendered screenshot pairs (PNG, before/after)
- Structured mutation record (operator, target element selector, before/after value) for has-diff items
- Polished English natural-language description (display only — judge consumes the structured record)
- Per-item metadata: id, split, domain, complexity tier, mutation operator, family

What is **not** distributed: the original third-party HTML/CSS/JS source.

## Known limitations

- All mutations are programmatic — does not cover human-introduced design changes that programmatic operators can't express (e.g., wholesale redesigns, content rewrites)
- Single mutation per pair; multi-mutation interactions are out of scope for v1
- Single viewport size; cross-viewport diffs are out of scope
- The no-diff split tolerates minor browser-rendering noise; this is intentional — a perfectly nitpicky model can score above 0% hallucination on this split

## Intended uses

- Evaluating VLMs on web-UI visual change detection
- Studying VLM failure modes by mutation operator and difficulty tier
- Reference distribution for training-data curation targeting visual diff capability

## Out-of-scope uses

- Production UI regression testing without further validation
- Commercial use without separate licensing
