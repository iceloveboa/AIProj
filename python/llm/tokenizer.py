from collections.abc import Iterable


class ByteTokenizer:
    """UTF-8 byte-level tokenizer with a fixed 256-token vocabulary."""

    vocab_size = 256

    def encode(self, text: str) -> list[int]:
        return list(text.encode("utf-8"))

    def encode_bytes(self, data: bytes) -> list[int]:
        return list(data)

    def decode(self, ids: Iterable[int]) -> str:
        return bytes(int(token) % 256 for token in ids).decode("utf-8", errors="replace")

    def decode_bytes(self, ids: Iterable[int]) -> bytes:
        return bytes(int(token) % 256 for token in ids)
