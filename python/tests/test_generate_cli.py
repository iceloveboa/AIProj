from generate import run_repl


class EchoModel:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return f"generated:{prompt}"


def test_run_repl_generates_for_each_input_line(capsys, monkeypatch):
    model = EchoModel()
    inputs = iter(["hello", "attention"])

    def fake_input(_: str) -> str:
        try:
            return next(inputs)
        except StopIteration as exc:
            raise EOFError from exc

    monkeypatch.setattr("builtins.input", fake_input)

    run_repl(model.generate_text)

    captured = capsys.readouterr()
    assert model.prompts == ["hello", "attention"]
    assert "generated:hello" in captured.out
    assert "generated:attention" in captured.out


def test_run_repl_exits_when_user_enters_exit(capsys, monkeypatch):
    model = EchoModel()
    inputs = iter(["hello", "exit", "should not run"])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    run_repl(model.generate_text)

    captured = capsys.readouterr()
    assert model.prompts == ["hello"]
    assert "generated:hello" in captured.out
    assert "should not run" not in captured.out
