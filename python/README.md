# Mini Attention LLM

A small PyTorch GPT-style language model project with local causal self-attention, byte-level tokenization, training, checkpointing, and generation.

## Setup

Use Python 3.10-3.12 for PyTorch compatibility.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Download About 1 GB Of Text

The default downloader now streams public RedPajama C4 JSONL shards and writes the first 1,000,000,000 bytes of text into `data/raw/redpajama_c4_1gb.txt`.

```bash
python scripts/download_data.py
python scripts/prepare_data.py --raw-path data/raw/redpajama_c4_1gb.txt
```

If Python reports a corporate/self-signed certificate error in this environment, run:

```bash
python scripts/download_data.py --insecure
```

The older Wikipedia-only source is still available as a fallback:

```bash
python scripts/download_data.py --dataset enwik9 --url http://mattmahoney.net/dc/enwik9.zip
python scripts/prepare_data.py --raw-path data/raw/enwik9
```

## Train

Tiny smoke training:

```bash
python train.py --batch-size 4 --block-size 64 --n-layer 2 --n-head 2 --n-embd 64 --max-steps 20 --eval-interval 10 --eval-iters 2
```

Longer training:

```bash
python train.py --batch-size 32 --block-size 256 --n-layer 6 --n-head 8 --n-embd 256 --max-steps 10000
```

Checkpoints are written to `out/last.pt` and `out/best.pt`.

## Generate

```bash
python generate.py --checkpoint out/best.pt --prompt "The history of attention is " --max-new-tokens 300
```

Or start interactive prompt mode by omitting `--prompt`:

```bash
python generate.py --checkpoint out/best.pt --max-new-tokens 300
```

In interactive mode, enter `exit` to quit.

## Tests

```bash
python -m pytest -q
```
