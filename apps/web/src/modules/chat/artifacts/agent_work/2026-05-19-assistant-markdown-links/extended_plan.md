# Extended Plan

## 1. Same bug class search
- Check if any other renderer in `chat` module bypasses markdown path for assistant messages.
- Confirm streaming placeholder (`state.streamingText`) uses the same assistant render path.

## 2. Adjacent surfaces to inspect
- `ChatPage` container for no unintended clipping/overflow after markdown blocks.
- `chat_history` preview remains plain text and stable.

## 3. Compatibility checks
- Ensure unchanged `Message` type and API payload contracts.
- Confirm no dependency additions required outside module scope.

## 4. Persisted state checks
- None required; stored messages remain raw text.

## 5. Additional protections
- No `dangerouslySetInnerHTML`.
- Restrict URL protocols to `http/https` for generated anchors.
- Fallback to plain text for malformed markdown link constructs.
- Ensure bare URL autolink strips trailing punctuation from href resolution.

## 6. Additional tests
- Assistant: markdown link + bare URL + inline/fenced code.
- Assistant: URL followed by punctuation remains clickable without punctuation in href.
- User: markdown characters remain plain text.
- Streaming: incomplete markdown fragments do not throw runtime errors.

## 7. Non-goals
- Full CommonMark/GFM parity.
- Syntax highlighting.
- Markdown rendering in chat history preview.

## 8. Final implementation boundary
Only files under `apps/web/src/modules/chat/` plus required task-log files (`apps/web/src/modules/chat/commit.md`, `/srv/projects/aicom/cgpt/commits.md`).
