# Mini Attention LLM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a PyTorch mini LLM project with implemented causal attention, 1 GB-ish public text data download, training, checkpointing, and generation.

**Architecture:** Use a decoder-only GPT-style Transformer with byte-level tokenization. Keep scripts small and composable: download raw data, prepare token binaries, train checkpoints, generate from checkpoints.

**Tech Stack:** Python 3.10+, PyTorch, NumPy, pytest.

---

## File Structure

- Create `llm/config.py` for model and train config dataclasses.
- Create `llm/tokenizer.py` for byte-level encode/decode.
- Create `llm/model.py` for causal self-attention and GPT.
- Create `llm/dataset.py` for memmap token batches.
- Create `llm/checkpoint.py` for checkpoint persistence.
- Create `scripts/download_data.py` for `enwik9` download/extract.
- Create `scripts/prepare_data.py` for text to `.bin` arrays.
- Create `train.py` for CLI training.
- Create `generate.py` for CLI generation.
- Create `tests/` for behavior tests and smoke coverage.

### Task 1: Tests

- [ ] Add tests for byte tokenizer round trip.
- [ ] Add tests for causal attention preventing future-token influence.
- [ ] Add tests for GPT forward logits and loss.
- [ ] Add tests for dataset batch shape.
- [ ] Add tests for checkpoint round trip.
- [ ] Run tests and verify they fail because implementation files do not exist yet.

### Task 2: Core Library

- [ ] Implement config dataclasses.
- [ ] Implement byte tokenizer.
- [ ] Implement binary dataset loader.
- [ ] Implement checkpoint save/load helpers.
- [ ] Implement causal self-attention, Transformer block, and GPT model.
- [ ] Run unit tests and verify they pass.

### Task 3: CLIs

- [ ] Implement `scripts/download_data.py`.
- [ ] Implement `scripts/prepare_data.py`.
- [ ] Implement `train.py`.
- [ ] Implement `generate.py`.
- [ ] Add README and requirements.

### Task 4: Verification

- [ ] Run all tests.
- [ ] Create a tiny local sample dataset.
- [ ] Prepare train/validation binaries.
- [ ] Run a tiny smoke training job.
- [ ] Run generation from the trained checkpoint.
- [ ] Attempt to download `enwik9.zip` and extract the 1 GB text dataset.

## Self Review

The plan covers model, data download, preparation, training, checkpointing, generation, and tests from the approved design. There are no unresolved placeholders. Names and paths match the design document.
