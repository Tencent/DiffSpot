#!/usr/bin/env python3
"""Generate the static GitHub Pages leaderboard at docs/index.html.

Single source of truth: leaderboard/leaderboard.json. To refresh the public
leaderboard page, edit leaderboard.json and re-run this script (then commit
docs/index.html). The page is fully self-contained (data + logo inlined), so
GitHub Pages can serve docs/ with no build step.
"""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEADERBOARD_JSON = ROOT / "leaderboard" / "leaderboard.json"
LOGO = ROOT / "assets" / "diffspot-logo.png"
OUT = ROOT / "docs" / "index.html"

HF_URL = "https://huggingface.co/datasets/tencent/DiffSpot"
GH_URL = "https://github.com/Tencent/DiffSpot"
ARXIV_URL = "https://arxiv.org/abs/2605.29615"

NUMCOLS = [
    ("easy_recall", "Easy"),
    ("med_recall", "Med"),
    ("hard_recall", "Hard"),
    ("diff_overall_recall", "Diff"),
    ("no_diff_specificity", "No-Diff"),
    ("overall_accuracy", "Overall"),
]


def main() -> int:
    data = json.loads(LEADERBOARD_JSON.read_text())
    entries = data["entries"]
    judge = data.get("judge", {})
    trivial = (
        data.get("trivial_baselines", {}).get("always_no_diff", {}).get("overall_accuracy")
    )

    # column maxima (for bold) and best open-weight (for underline marker)
    colmax = {k: max(float(e[k]) for e in entries) for k, _ in NUMCOLS}
    open_entries = [e for e in entries if e.get("family") == "open-weight"]
    open_best = {
        "diff_overall_recall": max((float(e["diff_overall_recall"]) for e in open_entries), default=None),
        "overall_accuracy": max((float(e["overall_accuracy"]) for e in open_entries), default=None),
    }

    # default order: Overall desc
    rows = sorted(entries, key=lambda e: float(e["overall_accuracy"]), reverse=True)

    logo_b64 = base64.b64encode(LOGO.read_bytes()).decode("ascii")

    def cell(e, key):
        v = float(e[key])
        s = f"{v:.1f}"
        cls = []
        if v == colmax[key]:
            cls.append("max")
        elif key in open_best and open_best[key] is not None and v == open_best[key]:
            cls.append("openbest")
        cls_attr = f' class="{" ".join(cls)}"' if cls else ""
        return f'<td data-v="{v}"{cls_attr}>{s}</td>'

    tbody = []
    for rank, e in enumerate(rows, 1):
        fam = e.get("family", "")
        fam_label = "Open" if fam == "open-weight" else "Proprietary"
        fam_cls = "open" if fam == "open-weight" else "prop"
        name = html.escape(e["display_name"])
        params = html.escape(str(e.get("params") or "—"))
        tds = "".join(cell(e, k) for k, _ in NUMCOLS)
        tbody.append(
            f'<tr data-fam="{fam}">'
            f'<td class="rank" data-v="{rank}">{rank}</td>'
            f'<td class="model">{name}</td>'
            f'<td><span class="pill {fam_cls}">{fam_label}</span></td>'
            f'<td class="params">{params}</td>'
            f"{tds}</tr>"
        )
    tbody_html = "\n".join(tbody)

    # header cells: Rank, Model, Type, Params, then numeric cols
    num_th = "".join(
        f'<th class="num{" overallcol" if k=="overall_accuracy" else ""}" data-key="{k}">{label}'
        f'<span class="arr"></span></th>'
        for k, label in NUMCOLS
    )
    judge_line = (
        f'Scored by an LLM-as-Judge ({html.escape(judge.get("model","gpt-oss-120b"))}, '
        f'reasoning_effort={html.escape(judge.get("reasoning_effort","high"))}). '
        f"<b>Diff</b> = recall on the 3,900 has-diff pairs; <b>No-Diff</b> = specificity on the 500 "
        f"control pairs; <b>Overall</b> = per-case accuracy over all 4,400 pairs."
    )
    trivial_line = (
        f"Trivial always-no-diff baseline: {trivial:.1f}% Overall." if trivial else ""
    )
    arxiv_badge = (
        f'<a class="badge arxiv" href="{ARXIV_URL or "#"}">arXiv</a>' if True else ""
    )

    page = TEMPLATE.format(
        logo_b64=logo_b64,
        hf=HF_URL,
        gh=GH_URL,
        arxiv_badge=arxiv_badge,
        num_th=num_th,
        tbody=tbody_html,
        judge_line=judge_line,
        trivial_line=trivial_line,
        n_models=len(entries),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    # ensure GitHub Pages serves files as-is (no Jekyll)
    (OUT.parent / ".nojekyll").write_text("")
    print(f"wrote {OUT} ({len(rows)} models)")
    return 0


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>DiffSpot Leaderboard</title>
<meta name="description" content="DiffSpot: Can VLMs Spot Fine-Grained Visual Differences in Web Interfaces? Public leaderboard."/>
<style>
  :root {{
    --ink:#141414; --muted:#6b7280; --line:#e6e8eb; --weblue:#e8f2fa;
    --open:#e7f5ee; --open-tx:#1a7f4b; --prop:#eef0fb; --prop-tx:#4a4fb0;
  }}
  * {{ box-sizing:border-box; }}
  body {{
    margin:0; background:#fff; color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
    line-height:1.5; -webkit-font-smoothing:antialiased;
  }}
  .wrap {{ max-width:1000px; margin:0 auto; padding:48px 20px 80px; }}
  header {{ text-align:center; }}
  header img {{ height:62px; width:auto; }}
  h1 {{ font-size:20px; font-weight:600; margin:18px 0 4px; }}
  .sub {{ color:var(--muted); font-size:15px; margin:0 0 18px; }}
  .badges {{ display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin-bottom:8px; }}
  .badge {{ text-decoration:none; font-size:13px; font-weight:600; padding:6px 12px; border-radius:6px;
            border:1px solid var(--line); color:var(--ink); background:#fafbfc; }}
  .badge:hover {{ background:#f0f2f4; }}
  .badge.arxiv {{ background:#b31b1b; color:#fff; border-color:#b31b1b; }}
  hr {{ border:none; border-top:1px solid var(--line); margin:28px 0; }}
  .note {{ font-size:13.5px; color:var(--muted); margin:14px 2px 4px; }}
  .tablecard {{ overflow-x:auto; border:1px solid var(--line); border-radius:10px; }}
  table {{ border-collapse:collapse; width:100%; font-size:14px; }}
  thead th {{ position:sticky; top:0; background:#fff; border-bottom:2px solid var(--ink);
              padding:11px 10px; text-align:right; white-space:nowrap; cursor:pointer; user-select:none; }}
  thead th.model, thead th.type, thead th.rankh {{ text-align:left; }}
  thead th.overallcol {{ background:var(--weblue); }}
  th .arr {{ display:inline-block; width:10px; color:var(--muted); }}
  th.sorted-asc .arr::after {{ content:"\\2191"; }}
  th.sorted-desc .arr::after {{ content:"\\2193"; }}
  tbody td {{ padding:10px 10px; text-align:right; border-bottom:1px solid var(--line); white-space:nowrap; }}
  tbody td.model {{ text-align:left; font-weight:600; }}
  tbody td.rank {{ text-align:left; color:var(--muted); width:34px; }}
  tbody td.params {{ text-align:left; color:var(--muted); font-variant-numeric:tabular-nums; }}
  tbody td.num, tbody td[data-v] {{ font-variant-numeric:tabular-nums; }}
  tbody tr:hover {{ background:#fafbfc; }}
  td.overallcol, th.overallcol {{ }}
  tbody td.max {{ font-weight:700; }}
  tbody td.openbest {{ text-decoration:underline; text-underline-offset:3px; }}
  /* shade the Overall column body cells */
  tbody td:last-child {{ background:var(--weblue); font-weight:700; }}
  .pill {{ display:inline-block; font-size:11.5px; font-weight:600; padding:2px 9px; border-radius:999px; }}
  .pill.open {{ background:var(--open); color:var(--open-tx); }}
  .pill.prop {{ background:var(--prop); color:var(--prop-tx); }}
  .legend {{ font-size:12.5px; color:var(--muted); margin-top:12px; }}
  .legend b {{ color:var(--ink); }}
  .submit {{ margin-top:26px; padding:14px 16px; background:#fafbfc; border:1px solid var(--line);
             border-radius:10px; font-size:14px; }}
  footer {{ margin-top:34px; text-align:center; color:var(--muted); font-size:12.5px; }}
  a {{ color:#2563eb; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <img src="data:image/png;base64,{logo_b64}" alt="DiffSpot"/>
    <h1>Can VLMs Spot Fine-Grained Visual Differences in Web Interfaces?</h1>
    <p class="sub">WeChat AI &middot; {n_models}-model public leaderboard</p>
    <div class="badges">
      <a class="badge" href="{hf}">🤗 Dataset</a>
      <a class="badge" href="{gh}">GitHub</a>
      {arxiv_badge}
    </div>
  </header>

  <hr/>

  <p class="note">{judge_line}</p>

  <div class="tablecard">
    <table id="lb">
      <thead>
        <tr>
          <th class="rankh">#</th>
          <th class="model" data-key="display_name">Model<span class="arr"></span></th>
          <th class="type">Type</th>
          <th class="rankh" data-key="params">Params</th>
          {num_th}
        </tr>
      </thead>
      <tbody>
{tbody}
      </tbody>
    </table>
  </div>

  <p class="legend"><b>Bold</b> = column best &nbsp;|&nbsp; <u>underline</u> = best open-weight &nbsp;|&nbsp; {trivial_line} Click any column header to sort.</p>

  <div class="submit">
    <b>Submit your model.</b> Run it on the dataset and either self-evaluate or send us your raw
    predictions — see the <a href="{gh}/blob/main/docs/submission.md">submission guide</a>.
  </div>

  <footer>
    Built from <code>leaderboard/leaderboard.json</code> &middot; DiffSpot is released under the MIT License (© 2026 Tencent).
  </footer>
</div>

<script>
(function () {{
  var table = document.getElementById("lb");
  var tbody = table.tBodies[0];
  var ths = table.tHead.rows[0].cells;
  var sortState = {{ key: "overall_accuracy", dir: -1 }};  // default Overall desc

  function reRank() {{
    Array.prototype.forEach.call(tbody.rows, function (tr, i) {{
      tr.cells[0].textContent = i + 1;
    }});
  }}

  function sortBy(key, dir) {{
    var rows = Array.prototype.slice.call(tbody.rows);
    rows.sort(function (a, b) {{
      var av, bv;
      if (key === "display_name") {{ av = a.cells[1].textContent.toLowerCase(); bv = b.cells[1].textContent.toLowerCase();
        return av < bv ? -dir : av > bv ? dir : 0; }}
      if (key === "params") {{ av = a.cells[3].textContent; bv = b.cells[3].textContent;
        return av < bv ? -dir : av > bv ? dir : 0; }}
      av = parseFloat(a.querySelector('td[data-col="'+key+'"]').dataset.v);
      bv = parseFloat(b.querySelector('td[data-col="'+key+'"]').dataset.v);
      return (av - bv) * dir;
    }});
    rows.forEach(function (r) {{ tbody.appendChild(r); }});
    reRank();
    Array.prototype.forEach.call(ths, function (th) {{ th.classList.remove("sorted-asc","sorted-desc"); }});
    var active = table.querySelector('th[data-key="'+key+'"]');
    if (active) active.classList.add(dir === 1 ? "sorted-asc" : "sorted-desc");
  }}

  // tag numeric cells with their column key so JS can read them
  var numKeys = ["easy_recall","med_recall","hard_recall","diff_overall_recall","no_diff_specificity","overall_accuracy"];
  Array.prototype.forEach.call(tbody.rows, function (tr) {{
    var numCells = Array.prototype.slice.call(tr.cells, 4);  // after rank/model/type/params
    numCells.forEach(function (td, i) {{ td.dataset.col = numKeys[i]; }});
  }});

  Array.prototype.forEach.call(ths, function (th) {{
    var key = th.dataset.key;
    if (!key) return;
    th.addEventListener("click", function () {{
      var dir = (sortState.key === key) ? -sortState.dir : (key === "display_name" || key === "params" ? 1 : -1);
      sortState = {{ key: key, dir: dir }};
      sortBy(key, dir);
    }});
  }});

  sortBy(sortState.key, sortState.dir);
}})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    raise SystemExit(main())
