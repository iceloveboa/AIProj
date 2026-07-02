# RedPajama C4 Data Source Update

## Goal

Change the default training corpus from `enwik9` to a different public dataset while keeping the raw text target at about 1 GB.

## Design

The downloader now defaults to RedPajama C4, using the public URL list from `togethercomputer/RedPajama-Data-1T`. It streams JSONL shards, extracts only the `text` field from each record, writes `data/raw/redpajama_c4_1gb.txt`, and stops after 1,000,000,000 bytes. This keeps disk and network usage bounded while using a broader web-text style corpus than Wikipedia-only `enwik9`.

The old `enwik9` downloader remains available through `--dataset enwik9` for fallback or comparison runs.

## Verification

Tests cover JSONL text extraction and byte-limit behavior without network access. A small live check downloads 10 KB from RedPajama C4 with `--insecure` for the local self-signed certificate environment.
