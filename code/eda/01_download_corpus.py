"""Step 1: download the ConvoKit r/tennis corpus (and fan subreddits if they exist).

Run on EC2:
    python code/eda/01_download_corpus.py

Files land in ~/data/convokit/<corpus-name>/ (utterances.jsonl, conversations.json, ...).
"""
from pathlib import Path

from convokit import download

DATA_DIR = Path.home() / "data" / "convokit"

# Main corpus first; the fan subreddits are optional and may not exist in ConvoKit.
CORPORA = [
    "subreddit-tennis",
    "subreddit-rogerfederer",
    "subreddit-RafaelNadal",
    "subreddit-novakdjokovic",
]


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in CORPORA:
        try:
            path = download(name, data_dir=str(DATA_DIR))
            files = sorted(p.name for p in Path(path).iterdir())
            print(f"OK    {name} -> {path}  {files}")
        except Exception as e:  # missing corpora raise various errors
            print(f"SKIP  {name}: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
