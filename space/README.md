# DiffSpot HuggingFace Space

Source for the public Space at <TBD>.

## What it does

- Browse a random or curated DiffSpot item, see image_a / image_b side-by-side
- View the GT mutation list and natural-language description
- Run any of the included baselines against the item and see the judge's verdict
- Filter by split (easy/medium/hard/no_diff), domain, and mutation type

## Local dev

```bash
cd space
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:7860>.

## Deploy

Push this directory as the root of a HuggingFace Space (Gradio or Streamlit). The Space pulls the dataset from the official HF repo at runtime.
