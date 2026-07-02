#!/usr/bin/env python3
import argparse
import math
import random
import time
from pathlib import Path

import numpy as np
import torch

from llm.checkpoint import load_checkpoint, save_checkpoint
from llm.config import ModelConfig
from llm.dataset import BinaryTokenDataset
from llm.model import GPT


def choose_device(requested: str) -> str:
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@torch.no_grad()
def estimate_loss(model: GPT, train_data: BinaryTokenDataset, val_data: BinaryTokenDataset, batch_size: int, eval_iters: int, device: str) -> dict[str, float]:
    model.eval()
    losses: dict[str, list[float]] = {"train": [], "val": []}
    for split, dataset in (("train", train_data), ("val", val_data)):
        for _ in range(eval_iters):
            x, y = dataset.get_batch(batch_size, device)
            _, loss = model(x, y)
            assert loss is not None
            losses[split].append(float(loss.item()))
    model.train()
    return {split: float(np.mean(values)) for split, values in losses.items()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a tiny GPT-style byte-level LLM.")
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--out-dir", default="out")
    parser.add_argument("--resume", default="")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument("--max-steps", type=int, default=2000)
    parser.add_argument("--eval-interval", type=int, default=100)
    parser.add_argument("--eval-iters", type=int, default=20)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=0.1)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--n-layer", type=int, default=4)
    parser.add_argument("--n-head", type=int, default=4)
    parser.add_argument("--n-embd", type=int, default=128)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--device", default="auto")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = choose_device(args.device)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    train_data = BinaryTokenDataset(Path(args.data_dir) / "train.bin", args.block_size)
    val_data = BinaryTokenDataset(Path(args.data_dir) / "val.bin", args.block_size)

    if args.resume:
        checkpoint = load_checkpoint(args.resume, map_location=device)
        config = checkpoint["model_config"]
        model = GPT(config).to(device)
        model.load_state_dict(checkpoint["model_state"])
        optimizer = model.configure_optimizer(args.learning_rate, args.weight_decay)
        if checkpoint["optimizer_state"] is not None:
            optimizer.load_state_dict(checkpoint["optimizer_state"])
        start_step = int(checkpoint["step"]) + 1
        best_val_loss = checkpoint["best_val_loss"]
    else:
        config = ModelConfig(
            vocab_size=256,
            block_size=args.block_size,
            n_layer=args.n_layer,
            n_head=args.n_head,
            n_embd=args.n_embd,
            dropout=args.dropout,
        )
        model = GPT(config).to(device)
        optimizer = model.configure_optimizer(args.learning_rate, args.weight_decay)
        start_step = 0
        best_val_loss = math.inf

    print(f"device={device} parameters={sum(p.numel() for p in model.parameters()):,}")
    t0 = time.time()
    for step in range(start_step, args.max_steps):
        if step == 0 or step % args.eval_interval == 0:
            metrics = estimate_loss(model, train_data, val_data, args.batch_size, args.eval_iters, device)
            print(f"step {step}: train loss {metrics['train']:.4f}, val loss {metrics['val']:.4f}")
            save_checkpoint(out_dir / "last.pt", model=model, optimizer=optimizer, step=step, best_val_loss=best_val_loss)
            if metrics["val"] < best_val_loss:
                best_val_loss = metrics["val"]
                save_checkpoint(out_dir / "best.pt", model=model, optimizer=optimizer, step=step, best_val_loss=best_val_loss)

        x, y = train_data.get_batch(args.batch_size, device)
        _, loss = model(x, y)
        assert loss is not None
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        if args.grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
        optimizer.step()

        if (step + 1) % 10 == 0:
            dt = time.time() - t0
            print(f"step {step + 1}: loss {loss.item():.4f}, {dt:.1f}s elapsed")

    save_checkpoint(out_dir / "last.pt", model=model, optimizer=optimizer, step=args.max_steps - 1, best_val_loss=best_val_loss)
    print(f"saved checkpoint to {out_dir / 'last.pt'}")


if __name__ == "__main__":
    main()
