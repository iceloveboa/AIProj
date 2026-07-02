#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np


def write_uint16_tokens(raw_path: Path, train_path: Path, val_path: Path, val_fraction: float, chunk_size: int) -> None:
    if not raw_path.exists():
        raise FileNotFoundError(f"raw data not found: {raw_path}")
    if not 0.0 < val_fraction < 1.0:
        raise ValueError("val_fraction must be between 0 and 1")

    total = raw_path.stat().st_size
    train_cutoff = int(total * (1.0 - val_fraction))
    train_path.parent.mkdir(parents=True, exist_ok=True)
    val_path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with raw_path.open("rb") as source, train_path.open("wb") as train, val_path.open("wb") as val:
        while True:
            chunk = source.read(chunk_size)
            if not chunk:
                break
            chunk_start = written
            chunk_end = written + len(chunk)
            if chunk_end <= train_cutoff:
                np.frombuffer(chunk, dtype=np.uint8).astype(np.uint16).tofile(train)
            elif chunk_start >= train_cutoff:
                np.frombuffer(chunk, dtype=np.uint8).astype(np.uint16).tofile(val)
            else:
                split = train_cutoff - chunk_start
                np.frombuffer(chunk[:split], dtype=np.uint8).astype(np.uint16).tofile(train)
                np.frombuffer(chunk[split:], dtype=np.uint8).astype(np.uint16).tofile(val)
            written = chunk_end
            print(f"\rprocessed {written / 1024 / 1024:.1f} MiB / {total / 1024 / 1024:.1f} MiB", end="")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert raw bytes into uint16 token binaries.")
    parser.add_argument("--raw-path", default="data/raw/redpajama_c4_1gb.txt")
    parser.add_argument("--out-dir", default="data/processed")
    parser.add_argument("--val-fraction", type=float, default=0.01)
    parser.add_argument("--chunk-size", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    raw_path = Path(args.raw_path)
    out_dir = Path(args.out_dir)
    train_path = out_dir / "train.bin"
    val_path = out_dir / "val.bin"
    if not args.force and train_path.exists() and val_path.exists():
        print(f"prepared files already exist: {train_path}, {val_path}")
        return
    write_uint16_tokens(raw_path, train_path, val_path, args.val_fraction, args.chunk_size)
    print(f"wrote {train_path} and {val_path}")


if __name__ == "__main__":
    main()
