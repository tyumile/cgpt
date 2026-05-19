import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.modules.chats import main as chats_main


class _FakeResult:
    def __init__(self, *, scalar=None, mappings_rows=None):
        self._scalar = scalar
        self._mappings_rows = mappings_rows or []

    def scalar_one_or_none(self):
        return self._scalar

    def mappings(self):
        class _Rows:
            def __init__(self, rows):
                self._rows = rows

            def all(self):
                return self._rows

        return _Rows(self._mappings_rows)


class _FakeSession:
    def __init__(self, results):
        self._results = list(results)
        self.executions = []
        self.begin_enter_calls = 0
        self.begin_exit_calls = 0

    async def execute(self, statement, params=None):
        self.executions.append({"statement": statement, "params": params})
        if self._results:
            return self._results.pop(0)
        return _FakeResult()

    def begin(self):
        return _FakeSessionBegin(self)


class _FakeSessionBegin:
    def __init__(self, session: _FakeSession):
        self._session = session

    async def __aenter__(self):
        self._session.begin_enter_calls += 1
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        self._session.begin_exit_calls += 1
        return False


def _get_delete_endpoint():
    for route in chats_main.router.routes:
        if "DELETE" in getattr(route, "methods", set()) and route.path.endswith("/{chat_id}"):
            return route.endpoint
    raise AssertionError("DELETE /api/chats/{chat_id} endpoint not found")


def _statement_sql(statement) -> str:
    return str(statement.compile()).lower()


def _statement_param_values(statement, params=None) -> list[object]:
    compiled = statement.compile()
    values = []
    for value in compiled.params.values():
        if isinstance(value, (list, tuple, set)):
            values.extend(value)
        else:
            values.append(value)
    if params:
        for value in params.values():
            if isinstance(value, (list, tuple, set)):
                values.extend(value)
            else:
                values.append(value)
    return values


def test_delete_chat_returns_404_when_chat_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_resolve(_request, _session):
        return SimpleNamespace(user_id=17)

    async def _fake_workspace(_session):
        return SimpleNamespace(id=29, root_path="/tmp/workspace")

    monkeypatch.setattr(chats_main, "resolve_cabinet_session_from_request", _fake_resolve)
    monkeypatch.setattr(chats_main, "get_current_workspace", _fake_workspace)

    delete_endpoint = _get_delete_endpoint()
    session = _FakeSession(results=[_FakeResult(scalar=None)])

    with pytest.raises(HTTPException) as exc:
        asyncio.run(delete_endpoint(chat_id=41, request=object(), session=session))

    assert exc.value.status_code == 404
    assert session.begin_enter_calls == 1
    assert session.begin_exit_calls == 1
    assert len(session.executions) == 1

    select_values = _statement_param_values(session.executions[0]["statement"])
    assert 41 in select_values
    assert 17 in select_values
    assert 29 in select_values


def test_delete_chat_deletes_uploaded_files_runs_messages_and_chat_by_chat_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_resolve(_request, _session):
        return SimpleNamespace(user_id=17)

    async def _fake_workspace(_session):
        return SimpleNamespace(id=29, root_path="/tmp/workspace")

    monkeypatch.setattr(chats_main, "resolve_cabinet_session_from_request", _fake_resolve)
    monkeypatch.setattr(chats_main, "get_current_workspace", _fake_workspace)

    chat_id = 42
    delete_endpoint = _get_delete_endpoint()
    session = _FakeSession(results=[_FakeResult(scalar=SimpleNamespace(id=chat_id, user_id=17))])

    asyncio.run(delete_endpoint(chat_id=chat_id, request=object(), session=session))

    sql_by_index = [_statement_sql(execution["statement"]) for execution in session.executions]
    upload_idx = next(i for i, sql in enumerate(sql_by_index) if "delete from uploaded_files" in sql)
    runs_idx = next(i for i, sql in enumerate(sql_by_index) if "delete from agent_runs" in sql)
    messages_idx = next(i for i, sql in enumerate(sql_by_index) if "delete from messages" in sql)
    chats_idx = next(i for i, sql in enumerate(sql_by_index) if "delete from chats" in sql)

    assert upload_idx < runs_idx < messages_idx < chats_idx

    for idx in (upload_idx, runs_idx, messages_idx, chats_idx):
        execution = session.executions[idx]
        assert chat_id in _statement_param_values(execution["statement"], execution["params"])

    assert session.begin_enter_calls == 1
    assert session.begin_exit_calls == 1


def test_delete_chat_marks_queued_and_running_runs_failed_with_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_resolve(_request, _session):
        return SimpleNamespace(user_id=17)

    async def _fake_workspace(_session):
        return SimpleNamespace(id=29, root_path="/tmp/workspace")

    monkeypatch.setattr(chats_main, "resolve_cabinet_session_from_request", _fake_resolve)
    monkeypatch.setattr(chats_main, "get_current_workspace", _fake_workspace)

    chat_id = 43
    delete_endpoint = _get_delete_endpoint()
    session = _FakeSession(results=[_FakeResult(scalar=SimpleNamespace(id=chat_id, user_id=17))])

    asyncio.run(delete_endpoint(chat_id=chat_id, request=object(), session=session))

    update_statement = next(
        execution["statement"]
        for execution in session.executions
        if _statement_sql(execution["statement"]).startswith("update agent_runs")
    )
    values = _statement_param_values(update_statement)

    assert "queued" in values
    assert "running" in values
    assert "failed" in values
    assert any(isinstance(value, str) and "delete" in value.lower() for value in values)
