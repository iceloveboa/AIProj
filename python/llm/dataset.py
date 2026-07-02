from pathlib import Path

import numpy as np
import torch


class BinaryTokenDataset:
    def __init__(self, path: str | Path, block_size: int) -> None:
        self.path = Path(path)
        self.block_size = block_size
        if not self.path.exists():
            raise FileNotFoundError(f"token dataset not found: {self.path}")
        self.tokens = np.memmap(self.path, dtype=np.uint16, mode="r")
        if len(self.tokens) <= self.block_size + 1:
            raise ValueError(
                f"dataset {self.path} has {len(self.tokens)} tokens, "
                f"need more than block_size + 1 ({self.block_size + 1})"
            )

    def __len__(self) -> int:
        return int(len(self.tokens))

    def get_batch(self, batch_size: int, device: str | torch.device) -> tuple[torch.Tensor, torch.Tensor]:
        ix = torch.randint(len(self.tokens) - self.block_size - 1, (batch_size,))
        x = torch.stack(
            [torch.from_numpy(np.asarray(self.tokens[i : i + self.block_size], dtype=np.int64)) for i in ix]
        )
        y = torch.stack(
            [torch.from_numpy(np.asarray(self.tokens[i + 1 : i + 1 + self.block_size], dtype=np.int64)) for i in ix]
        )
        return x.to(device), y.to(device)
