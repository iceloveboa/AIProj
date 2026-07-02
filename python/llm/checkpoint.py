from pathlib import Path
from typing import Any

import torch

from llm.config import ModelConfig


def save_checkpoint(
    path: str | Path,
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None,
    step: int,
    best_val_loss: float | None,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    config = getattr(model, "config", None)
    if not isinstance(config, ModelConfig):
        raise TypeError("model must expose a ModelConfig as model.config")
    torch.save(
        {
            "model_config": config.to_dict(),
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict() if optimizer is not None else None,
            "step": step,
            "best_val_loss": best_val_loss,
        },
        path,
    )


def load_checkpoint(path: str | Path, map_location: str | torch.device = "cpu") -> dict[str, Any]:
    data = torch.load(Path(path), map_location=map_location, weights_only=False)
    data["model_config"] = ModelConfig.from_dict(data["model_config"])
    return data
