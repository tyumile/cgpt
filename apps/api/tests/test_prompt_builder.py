from types import SimpleNamespace

from app.modules.prompt_builder.main import SYSTEM_PROMPT, build_prompt


def test_prompt_contains_system_rules_and_workspace() -> None:
    messages = [SimpleNamespace(role="user", content="Привет"), SimpleNamespace(role="assistant", content="Здравствуйте")]
    prompt = build_prompt(messages=messages, workspace_path="/tmp/ws")

    assert SYSTEM_PROMPT in prompt
    assert "Current workspace path: /tmp/ws" in prompt
    assert "USER: Привет" in prompt
    assert "ASSISTANT: Здравствуйте" in prompt


def test_prompt_trims_to_last_30() -> None:
    messages = [SimpleNamespace(role="user", content=f"m{i}") for i in range(35)]
    prompt = build_prompt(messages=messages, workspace_path="/tmp/ws")

    assert "USER: m0" not in prompt
    assert "USER: m5" in prompt
    assert "USER: m34" in prompt
