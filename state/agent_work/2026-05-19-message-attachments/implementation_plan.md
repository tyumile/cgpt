# Implementation Plan
1. Root cause
- File schema exists, but no upload/download/runtime integration in API and UI.

2. Strategy
- Keep single Stage-1 message endpoint and switch it to multipart contract.
- Reuse existing table uploaded_files and add ORM/service helpers.
- Store files under user/chat scoped workspace path to satisfy agent access + retention constraints.

3. File-by-file changes
- API schemas/models/messages/messages_store/chats/agent_exec/prompt_builder.
- Web shared types/api client/chat component.
- Tests for message endpoint and prompt/chats delete expectations.

4. Layer coverage
- Input/validation: multipart parse + limits + blocked executable types + text required.
- Logic/persistence: create message + persist files + create run.
- Contract/UI: attachments returned and rendered, download route added.
- Runtime: prompt gains attachment paths and user upload root.

5. Test plan
- Update/add unit tests for changed endpoint signature and prompt builder.
- Run full api pytest + web build.

6. Risks
- Multipart compatibility regressions for existing clients.
- Filesystem cleanup races on delete.

7. Done when
- Upload/send/download works in code path and checks pass with tests/build.
