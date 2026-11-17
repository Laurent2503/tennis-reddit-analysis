#!/usr/bin/env bash
# Step 3: download Jeff Sackmann's ATP/WTA match + ranking CSVs and upload them to S3.
#
# Run on EC2:
#     BUCKET=your-bucket-name bash code/eda/03_get_match_data.sh
set -euo pipefail

: "${BUCKET:?Set BUCKET, e.g. BUCKET=my-bucket bash code/eda/03_get_match_data.sh}"
SRC="$HOME/data/sackmann"
OUT="$HOME/data/matches"
mkdir -p "$SRC" "$OUT"

# Jeff Sackmann's original tennis_atp / tennis_wta repos are no longer public on GitHub
# (checked Nov 2026). These are public forks of them; the data is still Sackmann's
# (CC BY-NC-SA 4.0) and should be credited to him. Override with ATP_REPO / WTA_REPO.
ATP_REPO="${ATP_REPO:-https://github.com/Kadantte/tennis_atp.git}"
WTA_REPO="${WTA_REPO:-https://github.com/VictorSquidWei/tennis_wta.git}"

for tour in atp wta; do
  if [ ! -d "$SRC/tennis_$tour" ]; then
    repo=$([ "$tour" = atp ] && echo "$ATP_REPO" || echo "$WTA_REPO")
    git clone --depth 1 "$repo" "$SRC/tennis_$tour"
  fi
  # Tour-level singles matches 2010-2018 and the 2010s weekly rankings.
  for year in $(seq 2010 2018); do
    cp "$SRC/tennis_$tour/${tour}_matches_${year}.csv" "$OUT/"
  done
  cp "$SRC/tennis_$tour/${tour}_rankings_10s.csv" "$OUT/"
  cp "$SRC/tennis_$tour/${tour}_players.csv" "$OUT/"
done

ls -lh "$OUT"
aws s3 sync "$OUT" "s3://$BUCKET/raw/matches/"
echo "Uploaded to s3://$BUCKET/raw/matches/"
