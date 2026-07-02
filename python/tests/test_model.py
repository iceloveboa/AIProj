import torch

from llm.config import ModelConfig
from llm.model import CausalSelfAttention, GPT


def test_causal_attention_does_not_use_future_tokens():
    torch.manual_seed(0)
    config = ModelConfig(vocab_size=16, block_size=4, n_layer=1, n_head=2, n_embd=8, dropout=0.0)
    attention = CausalSelfAttention(config)
    attention.eval()

    x = torch.randn(1, 4, config.n_embd)
    changed_future = x.clone()
    changed_future[:, 3, :] += 1000.0

    with torch.no_grad():
        original = attention(x)
        modified = attention(changed_future)

    assert torch.allclose(original[:, :3, :], modified[:, :3, :], atol=1e-5)


def test_gpt_forward_returns_logits_and_loss():
    torch.manual_seed(0)
    config = ModelConfig(vocab_size=32, block_size=8, n_layer=2, n_head=4, n_embd=16, dropout=0.0)
    model = GPT(config)
    idx = torch.randint(0, config.vocab_size, (2, config.block_size))
    targets = torch.randint(0, config.vocab_size, (2, config.block_size))

    logits, loss = model(idx, targets)

    assert logits.shape == (2, config.block_size, config.vocab_size)
    assert loss is not None
    assert loss.ndim == 0
