import json

from scripts.download_data import write_jsonl_text_corpus


def test_write_jsonl_text_corpus_extracts_text_until_byte_limit(tmp_path):
    shard = tmp_path / "sample.jsonl"
    shard.write_text(
        "\n".join(
            [
                json.dumps({"text": "first document", "meta": {"source": "test"}}),
                json.dumps({"text": "second document"}),
                json.dumps({"not_text": "ignored"}),
            ]
        ),
        encoding="utf-8",
    )
    target = tmp_path / "raw.txt"

    written = write_jsonl_text_corpus([shard.as_uri()], target, target_bytes=20)

    data = target.read_bytes()
    assert written == 20
    assert len(data) == 20
    assert data.startswith(b"first document\n")
    assert b"meta" not in data
