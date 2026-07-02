from llm.tokenizer import ByteTokenizer


def test_byte_tokenizer_round_trips_utf8_text():
    tokenizer = ByteTokenizer()
    text = "Hello, attention. 你好."

    ids = tokenizer.encode(text)
    decoded = tokenizer.decode(ids)

    assert decoded == text
    assert tokenizer.vocab_size == 256
