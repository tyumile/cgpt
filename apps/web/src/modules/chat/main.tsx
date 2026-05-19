"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { listMessages, postMessage } from "@/src/modules/api_client/main";
import { buildInitialState, reduceWsEvent } from "@/src/modules/messages/main";
import { connectChatWs } from "@/src/modules/realtime/main";
import { Message } from "@/src/shared/types";

type ChatScreenProps = {
  chatId: number;
  initialMessages: Message[];
  sessionToken: string | null;
  onUserMessageSubmitted?: (content: string) => void;
  onUserMessageCreated?: () => void;
  onUserMessageFailed?: () => void;
};

export default function ChatScreen({
  chatId,
  initialMessages,
  sessionToken,
  onUserMessageSubmitted,
  onUserMessageCreated,
  onUserMessageFailed,
}: ChatScreenProps) {
  const [text, setText] = useState("");
  const [state, setState] = useState(() => buildInitialState(initialMessages));

  const recoverAfterWsError = async () => {
    for (let attempt = 0; attempt < 20; attempt += 1) {
      try {
        const latest = await listMessages(chatId, sessionToken ?? undefined);
        const last = latest.length > 0 ? latest[latest.length - 1] : null;
        const hasAssistantReply = last?.role === "assistant";

        setState((prev) => ({
          ...prev,
          messages: latest,
          streamingText: "",
          isThinking: hasAssistantReply ? false : prev.isThinking,
          error: hasAssistantReply ? null : prev.error,
        }));

        if (hasAssistantReply) {
          return;
        }
      } catch {
        // Keep retrying on transient network or upstream errors.
      }

      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
  };

  useEffect(() => {
    setState(buildInitialState(initialMessages));
  }, [initialMessages]);

  useEffect(() => {
    const ws = connectChatWs(
      chatId,
      sessionToken,
      (event) => setState((prev) => reduceWsEvent(prev, event)),
      (message) => {
        setState((prev) => ({ ...prev, error: message }));
        void recoverAfterWsError();
      },
    );

    return () => ws.close();
  }, [chatId, sessionToken]);

  const renderedMessages = useMemo(() => {
    const rows = [...state.messages];
    if (state.streamingText) {
      rows.push({
        id: -1,
        workspace_id: 0,
        chat_id: chatId,
        role: "assistant",
        content: state.streamingText,
        status: "streaming",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
    }
    return rows;
  }, [state.messages, state.streamingText, chatId]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const value = text.trim();
    if (!value) {
      return;
    }

    const optimistic: Message = {
      id: Date.now(),
      workspace_id: 0,
      chat_id: chatId,
      role: "user",
      content: value,
      status: "done",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, optimistic],
      error: null,
      isThinking: true,
    }));
    setText("");
    onUserMessageSubmitted?.(value);

    try {
      await postMessage(chatId, value, sessionToken ?? undefined);
      onUserMessageCreated?.();
    } catch (err) {
      onUserMessageFailed?.();
      setState((prev) => ({
        ...prev,
        isThinking: false,
        error: err instanceof Error ? err.message : "Failed to send message.",
      }));
    }
  };

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 20, width: "100%" }}>
      <h1 style={{ marginTop: 0 }}>SaaS Chat MVP</h1>
      <div style={{ border: "1px solid #ddd", borderRadius: 8, background: "#fff", height: "60vh", overflowY: "auto", padding: 12 }}>
        {renderedMessages.map((message) => (
          <div key={message.id} style={{ marginBottom: 12 }}>
            <strong>{message.role === "user" ? "Вы" : "Ассистент"}:</strong>
            <div style={{ whiteSpace: "pre-wrap" }}>{message.content}</div>
          </div>
        ))}
        {state.isThinking && !state.streamingText ? <div>Агент думает...</div> : null}
      </div>

      {state.error ? <p style={{ color: "#b00020" }}>{state.error}</p> : null}

      <form onSubmit={onSubmit} style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Введите сообщение"
          style={{ flex: 1, padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
        />
        <button type="submit" style={{ padding: "10px 16px", borderRadius: 8, border: "none", background: "#111", color: "#fff" }}>
          Отправить
        </button>
      </form>
    </main>
  );
}
