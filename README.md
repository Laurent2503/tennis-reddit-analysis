# What Makes Tennis Fans Talk?

DSAN 6000 final project. Joins the ConvoKit r/tennis Reddit corpus with Jeff Sackmann's
ATP/WTA match data to study what drives fan attention and sentiment. Processing runs in
Apache Spark on AWS.

Website: https://laurent2503.github.io/tennis-reddit-analysis/

## Layout

- `code/eda`, `code/nlp`, `code/ml` — Spark scripts and notebooks
- `data/` — local data (gitignored; full data lives in S3)
- `website-source/` — Quarto site source; small outputs go in `images/` and `data/`
- `docs/` — rendered site served by GitHub Pages (built with `quarto render`)

## Build the site

```bash
cd website-source && quarto render
```
