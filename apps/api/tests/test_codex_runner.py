from app.modules.codex_runner.main import build_output_file_path


def test_output_file_path_is_unique_per_run() -> None:
    first = build_output_file_path(workspace_path="/tmp/workspace", run_id=10)
    second = build_output_file_path(workspace_path="/tmp/workspace", run_id=11)

    assert first != second
    assert first.name == ".codex_last_message_10.txt"
    assert second.name == ".codex_last_message_11.txt"
