# Module Commit Log
2026-05-19 | 05:48 UTC | Chat full-width + mobile sidebar controls | Full-width chat pane, readable text cap, mobile sidebar toggle/close behavior, build PASS; production verification blocked by remote Next chunk 400.
2026-05-19 | 06:06 UTC | Production chunk-400 runtime recovery | Restarted cgpt-web to align runtime with current .next artifacts; production desktop/mobile verification PASS.
2026-05-19 | 06:45 UTC | Recover gray production screen after chunk drift | Restarted cgpt-web; runtime chunk hash synchronized; visual production check PASS (no 4xx/no blank screen).
2026-05-19 | 10:07 UTC | Chat delete UI + layout overlap fix | Added per-chat delete with confirm and active-chat empty-state redirect; fixed sidebar/content overlap via border-box; production recheck PASS.
2026-05-19 | 10:28 UTC | Auto-title from first message + title ellipsis in sidebar | New chat bootstrap default switched to "Новый чат" and sidebar title constrained to one-line ellipsis; build PASS, production scenario PASS.
2026-05-20 | 10:45 UTC | Chat UI redesign to ChatGPT-like light interface | Refactored chat page, sidebar, thread, and composer to class-based ChatGPT-style UI with minimal animations and RU/EN copy; web build PASS, lint blocked by interactive Next ESLint setup.
