# Mini Attention LLM Design

## Goal

Build a practical, small Python LLM project that implements causal self-attention, can download about 1 GB of public text data, can train a tiny GPT-style model, and can run generation from a trained checkpoint.

## Architecture

The project uses PyTorch and a compact GPT-style decoder-only Transformer. The core model is implemented locally: token embeddings, positional embeddings, stacked Transformer blocks, masked multi-head causal self-attention, feed-forward layers, layer normalization, and an autoregressive language-modeling head.

Data preparation is split from training. A downloader fetches the public `enwik9` archive, whose extracted text is about 1 GB. A preparation script converts raw text into byte-level token IDs and writes memory-mappable train/validation arrays. Training consumes those arrays and writes checkpoints. Generation loads a checkpoint and samples tokens autoregressively.

## Components

- `llm/config.py`: dataclass configuration for model and training defaults.
- `llm/model.py`: GPT model, Transformer block, and causal self-attention.
- `llm/tokenizer.py`: byte-level tokenizer with a stable 256-token vocabulary.
- `llm/dataset.py`: binary token dataset and random batch sampling.
- `llm/checkpoint.py`: checkpoint save/load helpers.
- `scripts/download_data.py`: resumable public text download and extraction.
- `scripts/prepare_data.py`: raw text to binary train/validation token files.
- `train.py`: train loop with checkpointing, resume support, and device selection.
- `generate.py`: checkpoint loading and text generation CLI.

## Data

The default dataset is `enwik9` from Matt Mahoney's Large Text Compression Benchmark:

- Download URL: `https://mattmahoney.net/dc/enwik9.zip`
- Compressed size: roughly 300 MB
- Extracted size: 1,000,000,000 bytes

This gives the requested 1 GB-ish training corpus while keeping the network transfer smaller than a raw 1 GB download.

## Error Handling

Scripts create directories as needed, skip work when expected outputs already exist, and raise clear errors for missing inputs. Training validates that the dataset exists before starting. Generation validates checkpoint compatibility by restoring both model config and state dict.

## Testing

Focused tests cover byte tokenizer round trips, causal attention masking, model forward/loss shape, dataset batch sampling, and checkpoint round trip behavior. A tiny smoke training command verifies the project can train and generate without needing the full 1 GB dataset.

## Limitations

This is a small educational/practical LLM baseline, not a production-scale model. The default byte tokenizer is simple and robust, but a BPE tokenizer would train more efficiently. Full training over 1 GB on CPU will be slow; the project supports CPU, Apple MPS, and CUDA so it can scale with available hardware.
