import numpy as np
import torch

from llm.checkpoint import load_checkpoint, save_checkpoint
from llm.config import ModelConfig
from llm.dataset import BinaryTokenDataset
from llm.model import GPT


def test_binary_token_dataset_returns_shifted_batches(tmp_path):
    path = tmp_path / "train.bin"
    np.arange(128, dtype=np.uint16).tofile(path)
    dataset = BinaryTokenDataset(path, block_size=8)

    x, y = dataset.get_batch(batch_size=4, device="cpu")

    assert x.shape == (4, 8)
    assert y.shape == (4, 8)
    assert torch.equal(y[:, :-1], x[:, 1:])


def test_checkpoint_round_trip_restores_model_config_and_state(tmp_path):
    config = ModelConfig(vocab_size=32, block_size=8, n_layer=1, n_head=4, n_embd=16, dropout=0.0)
    model = GPT(config)
    checkpoint_path = tmp_path / "ckpt.pt"

    save_checkpoint(checkpoint_path, model=model, optimizer=None, step=7, best_val_loss=1.25)
    loaded = load_checkpoint(checkpoint_path, map_location="cpu")

    assert loaded["step"] == 7
    assert loaded["best_val_loss"] == 1.25
    assert loaded["model_config"].vocab_size == config.vocab_size
    restored = GPT(loaded["model_config"])
    restored.load_state_dict(loaded["model_state"])
