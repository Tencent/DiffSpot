# Dataset License

The DiffSpot dataset (screenshots, mutated HTML pairs, ground-truth diff descriptions, and evaluation metadata) is released under

**Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**
<https://creativecommons.org/licenses/by-nc/4.0/>

## Terms in plain language

- ✅ **Use it for academic research** — train, evaluate, publish results, build derivative benchmarks
- ✅ **Redistribute** — share with collaborators, mirror on internal storage
- ❌ **Do not use it for commercial purposes** without separate permission
- 📌 **Attribute** — cite the DiffSpot paper (see [`README.md`](README.md))

## Source web pages

The screenshots in DiffSpot were rendered from publicly accessible web pages. The dataset distributes only the rendered images and the programmatic mutation diffs — **not** the original HTML / CSS / JS source of any third-party site. Trademarks, logos, and other content visible in screenshots remain the property of their respective owners and are included for the purpose of academic research and benchmarking under fair use / fair dealing principles.

## Takedown policy

If you are the operator of a website whose rendered screenshot appears in this dataset and you would like it removed, please open an issue on the GitHub repository or contact the authors at <TBD@example.com>. We will remove the corresponding entries from the next dataset release.

## Reproducing the dataset

The construction pipeline (URL filtering, mutation operators, rendering, no-diff sampling) is open-sourced in this repository. Re-running the pipeline against your own crawl of public web pages is permitted and unrestricted; only redistribution of the released DiffSpot screenshots is bound by CC BY-NC 4.0.
