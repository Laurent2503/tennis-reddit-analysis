"""Step 2: convert a ConvoKit corpus to parquet with Spark, plus a 1% dev sample.

Run on EC2 (after step 1):
    python code/eda/02_convert_to_parquet.py subreddit-tennis

Writes locally to ~/data/parquet/<corpus>/ :
    comments/        every utterance (posts and comments), partitioned by year
    threads/         one row per thread (title, num_comments, ...) from conversations.json
    comments_sample/ 1% random sample of comments for development
Then upload with:
    aws s3 sync ~/data/parquet s3://$BUCKET/parquet

Sized for a 2-core / 8 GB instance.
"""
import json
import sys
from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

CORPUS = sys.argv[1] if len(sys.argv) > 1 else "subreddit-tennis"
SRC = Path.home() / "data" / "convokit" / CORPUS
OUT = Path.home() / "data" / "parquet" / CORPUS
SAMPLE_FRACTION = 0.01


def build_spark():
    return (
        SparkSession.builder.appName(f"convert-{CORPUS}")
        .master("local[2]")
        .config("spark.driver.memory", "5g")
        .config("spark.sql.shuffle.partitions", "16")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def convert_comments(spark):
    raw = spark.read.json(str(SRC / "utterances.jsonl"))
    cols = raw.columns
    # ConvoKit 2+ uses "speaker"; older corpora use "user".
    author = F.col("speaker") if "speaker" in cols else F.col("user")

    meta_cols = []
    if "meta" in cols:
        meta_fields = raw.schema["meta"].dataType.fieldNames()
        meta_cols = [F.col(f"meta.{f}").alias(f) for f in meta_fields]

    ts = F.col("timestamp").cast("long")
    df = raw.select(
        F.col("id"),
        F.col("root").alias("thread_id"),
        F.col("reply_to"),
        author.alias("author"),
        ts.alias("timestamp"),
        F.to_timestamp(F.from_unixtime(ts)).alias("created_utc"),
        F.col("text"),
        *meta_cols,
    ).withColumn("is_post", F.col("id") == F.col("thread_id"))
    df = (
        df.withColumn("date", F.to_date("created_utc"))
        .withColumn("year", F.year("created_utc"))
        .withColumn("month", F.month("created_utc"))
    )

    df.write.mode("overwrite").partitionBy("year").parquet(str(OUT / "comments"))

    comments = spark.read.parquet(str(OUT / "comments"))
    comments.sample(fraction=SAMPLE_FRACTION, seed=42).coalesce(2).write.mode(
        "overwrite"
    ).parquet(str(OUT / "comments_sample"))
    return comments


def convert_threads():
    """conversations.json is one JSON object keyed by thread id, so read it with pandas."""
    with open(SRC / "conversations.json") as f:
        convos = json.load(f)
    rows = []
    for thread_id, value in convos.items():
        meta = value.get("meta", value) if isinstance(value, dict) else {}
        row = {k: v for k, v in meta.items() if k != "vectors"}
        row["thread_id"] = thread_id
        rows.append(row)
    threads = pd.DataFrame(rows)
    # Nested fields (e.g. gildings dicts) don't round-trip cleanly; store them as JSON text.
    for col in threads.columns:
        if threads[col].map(lambda v: isinstance(v, (dict, list))).any():
            threads[col] = threads[col].map(
                lambda v: json.dumps(v) if isinstance(v, (dict, list)) else v
            )
    (OUT / "threads").mkdir(parents=True, exist_ok=True)
    threads.to_parquet(OUT / "threads" / "threads.parquet", index=False)
    return threads


def main():
    if not SRC.exists():
        sys.exit(f"{SRC} not found - run 01_download_corpus.py first")

    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    comments = convert_comments(spark)
    threads = convert_threads()

    print("\n=== Summary:", CORPUS, "===")
    print("columns:", comments.columns)
    comments.groupBy("year").agg(
        F.count("*").alias("utterances"),
        F.sum(F.col("is_post").cast("int")).alias("posts"),
        F.countDistinct("author").alias("authors"),
    ).orderBy("year").show(30)
    print("total utterances:", comments.count())
    print("threads:", len(threads), "| thread columns:", list(threads.columns))
    print(f"\nWritten to {OUT}")
    spark.stop()


if __name__ == "__main__":
    main()
