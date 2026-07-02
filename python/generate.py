#!/usr/bin/env python3
import argparse
from collections.abc import Callable

import torch

from llm.checkpoint import load_checkpoint
from llm.model import GPT
from llm.tokenizer import ByteTokenizer
from train import choose_device


def generate_text(
    model: GPT,
    tokenizer: ByteTokenizer,
    prompt: str,
    device: str,
    max_new_tokens: int,
    temperature: float,
    top_k: int | None,
) -> str:
    idx = torch.tensor([tokenizer.encode(prompt)], dtype=torch.long, device=device)
    output = model.generate(idx, max_new_tokens, temperature=temperature, top_k=top_k)
    return tokenizer.decode(output[0].tolist())


def run_repl(generate_once: Callable[[str], str]) -> None:
    while True:
        try:
            prompt = input("prompt> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if prompt.strip() == "exit":
            break
        if not prompt:
            continue
        print(generate_once(prompt))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate text from a trained checkpoint.")
    parser.add_argument("--checkpoint", default="out/best.pt")
    parser.add_argument("--prompt")
    parser.add_argument("--max-new-tokens", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    device = choose_device(args.device)
    checkpoint = load_checkpoint(args.checkpoint, map_location=device)
    model = GPT(checkpoint["model_config"]).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    tokenizer = ByteTokenizer()
    generate_once = lambda prompt: generate_text(
        model,
        tokenizer,
        prompt,
        device,
        args.max_new_tokens,
        args.temperature,
        args.top_k,
    )
    if args.prompt is None:
        run_repl(generate_once)
    else:
        print(generate_once(args.prompt))


if __name__ == "__main__":
    main()
