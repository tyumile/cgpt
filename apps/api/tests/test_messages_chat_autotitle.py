import asyncio
from types import SimpleNamespace

import pytest

from app.modules.messages import main as messages_main
from app.shared.schemas import MessageCreateRequest


class _FakeResult:
    def __init__(self, *, scalar=None):
        self._scalar = scalar

    def scalar_one_or_none(self):
        return self._scalar


class _FakeSession:
    def __init__(self, *, first_user_message_id):
        self.first_user_message_id = first_user_message_id
        self.execute_calls = 0
        self.commit_calls = 0

    async def execute(self, _statement, _params=None):
        self.execute_calls += 1
        return _FakeResult(scalar=self.first_user_message_id)

    async def commit(self):
        self.commit_calls += 1


def _get_post_endpoint():
    for route in messages_main.router.routes:
        if "POST" in getattr(route, "methods", set()):
            return route.endpoint
    raise AssertionError("POST /api/chats/{chat_id}/messages endpoint not found")


def _setup_common_mocks(monkeypatch: pytest.MonkeyPatch, *, chat_title: str, user_message_id: int):
    chat = SimpleNamespace(id=41, user_id=17, workspace_id=29, title=chat_title)

    async def _fake_resolve(_request, _session):
        return SimpleNamespace(user_id=17)

    async def _fake_get_chat(_session, *, chat_id: int, user_id: int):
        assert chat_id == 41
        assert user_id == 17
        return chat

    async def _fake_create_message(_session, **_kwargs):
        return SimpleNamespace(id=user_message_id)

    async def _fake_create_agent_run(_session, **_kwargs):
        return SimpleNamespace(id=73)

    async def _fake_set_enqueued(_session, _run, *, job_id: str):
        assert job_id == "job-1"

    async def _fake_enqueue_run(_redis, _job):
        return None

    monkeypatch.setattr(messages_main, "resolve_cabinet_session_from_request", _fake_resolve)
    monkeypatch.setattr(messages_main, "_get_owned_chat_or_404", _fake_get_chat)
    monkeypatch.setattr(messages_main, "create_message", _fake_create_message)
    monkeypatch.setattr(messages_main, "create_agent_run", _fake_create_agent_run)
    monkeypatch.setattr(messages_main, "set_enqueued", _fake_set_enqueued)
    monkeypatch.setattr(messages_main, "enqueue_run", _fake_enqueue_run)
    monkeypatch.setattr(messages_main, "get_redis", lambda: object())
    monkeypatch.setattr(messages_main, "build_job", lambda **_kwargs: SimpleNamespace(job_id="job-1"))
    return chat


def test_first_user_message_sets_chat_title(monkeypatch: pytest.MonkeyPatch) -> None:
    chat = _setup_common_mocks(monkeypatch, chat_title=messages_main.DEFAULT_CHAT_TITLE, user_message_id=11)
    post_endpoint = _get_post_endpoint()
    session = _FakeSession(first_user_message_id=11)

    payload = MessageCreateRequest(content="  user:   Привет,   мир \n\n как дела?  ")
    response = asyncio.run(post_endpoint(chat_id=41, payload=payload, request=object(), session=session))

    assert response.message_id == 11
    assert response.agent_run_id == 73
    assert chat.title == "Привет, мир как дела?"
    assert len(chat.title) <= 255
    assert session.commit_calls == 1


def test_second_user_message_does_not_rename_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    chat = _setup_common_mocks(monkeypatch, chat_title=messages_main.DEFAULT_CHAT_TITLE, user_message_id=12)
    post_endpoint = _get_post_endpoint()
    session = _FakeSession(first_user_message_id=11)

    payload = MessageCreateRequest(content="Второе сообщение")
    asyncio.run(post_endpoint(chat_id=41, payload=payload, request=object(), session=session))

    assert chat.title == messages_main.DEFAULT_CHAT_TITLE
    assert session.commit_calls == 0


def test_first_message_noisy_or_empty_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    chat = _setup_common_mocks(monkeypatch, chat_title=messages_main.DEFAULT_CHAT_TITLE, user_message_id=21)
    post_endpoint = _get_post_endpoint()
    session = _FakeSession(first_user_message_id=21)

    payload = MessageCreateRequest(content="  \n\t user:   \r\n  ")
    asyncio.run(post_endpoint(chat_id=41, payload=payload, request=object(), session=session))

    assert chat.title == messages_main.DEFAULT_CHAT_TITLE
    assert session.commit_calls == 1


def test_non_default_title_is_not_overwritten(monkeypatch: pytest.MonkeyPatch) -> None:
    chat = _setup_common_mocks(monkeypatch, chat_title="Ручной заголовок", user_message_id=31)
    post_endpoint = _get_post_endpoint()
    session = _FakeSession(first_user_message_id=31)

    payload = MessageCreateRequest(content="Новый контент")
    asyncio.run(post_endpoint(chat_id=41, payload=payload, request=object(), session=session))

    assert chat.title == "Ручной заголовок"
    assert session.execute_calls == 0
    assert session.commit_calls == 0


def test_legacy_new_chat_title_is_not_backfilled(monkeypatch: pytest.MonkeyPatch) -> None:
    chat = _setup_common_mocks(monkeypatch, chat_title="New chat", user_message_id=41)
    post_endpoint = _get_post_endpoint()
    session = _FakeSession(first_user_message_id=41)

    payload = MessageCreateRequest(content="Первое сообщение для legacy чата")
    asyncio.run(post_endpoint(chat_id=41, payload=payload, request=object(), session=session))

    assert chat.title == "New chat"
    assert session.execute_calls == 0
    assert session.commit_calls == 0
