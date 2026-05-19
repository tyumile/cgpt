"use client";

import { ChangeEvent, FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { downloadAttachment, listMessages, postMessageWithAttachments } from "@/src/modules/api_client/main";
import { renderAssistantMarkdown } from "@/src/modules/chat/markdown";
import { buildInitialState, reduceWsEvent } from "@/src/modules/messages/main";
import { connectChatWs } from "@/src/modules/realtime/main";
import { Message, UploadedFileAttachment } from "@/src/shared/types";

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
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [state, setState] = useState(() => buildInitialState(initialMessages));
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) {
      return `${bytes} B`;
    }
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const onPickFiles = () => {
    fileInputRef.current?.click();
  };

  const onSelectedFilesChanged = (event: ChangeEvent<HTMLInputElement>) => {
    const next = Array.from(event.target.files ?? []);
    if (next.length === 0) {
      return;
    }
    setSelectedFiles((prev) => [...prev, ...next].slice(0, 10));
    event.target.value = "";
  };

  const onRemoveSelectedFile = (idx: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const onDownloadAttachment = async (attachment: UploadedFileAttachment) => {
    const blob = await downloadAttachment(chatId, attachment.id, sessionToken ?? undefined);
    const href = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    link.download = attachment.original_name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(href);
  };

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
        attachments: [],
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
      attachments: selectedFiles.map((file, idx) => ({
        id: Date.now() + idx,
        original_name: file.name,
        mime_type: file.type || "application/octet-stream",
        size_bytes: file.size,
        created_at: new Date().toISOString(),
        download_path: "",
      })),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, optimistic],
      error: null,
      isThinking: true,
    }));
    setText("");
    setSelectedFiles([]);
    onUserMessageSubmitted?.(value);

    try {
      await postMessageWithAttachments(chatId, value, selectedFiles, sessionToken ?? undefined);
      try {
        const latest = await listMessages(chatId, sessionToken ?? undefined);
        setState((prev) => ({ ...prev, messages: latest, error: null }));
      } catch {
        // Keep optimistic state if background refresh fails.
      }
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
    <main style={{ margin: 0, padding: 20, width: "100%", boxSizing: "border-box", minWidth: 0 }}>
      <h1 style={{ marginTop: 0 }}>SaaS Chat MVP</h1>
      <div style={{ border: "1px solid #ddd", borderRadius: 8, background: "#fff", height: "60vh", overflowY: "auto", padding: 12 }}>
        {renderedMessages.map((message) => (
          <div key={message.id} style={{ marginBottom: 12 }}>
            <strong>{message.role === "user" ? "Вы" : "Ассистент"}:</strong>
            {message.role === "assistant" ? (
              renderAssistantMarkdown(message.content)
            ) : (
              <div style={{ whiteSpace: "pre-wrap", maxWidth: "72ch" }}>{message.content}</div>
            )}
            {message.attachments.length > 0 ? (
              <ul style={{ marginTop: 8, paddingLeft: 18 }}>
                {message.attachments.map((attachment) => (
                  <li key={attachment.id}>
                    {attachment.download_path ? (
                      <button
                        type="button"
                        onClick={() => void onDownloadAttachment(attachment)}
                        style={{ border: "none", background: "none", color: "#0a58ca", cursor: "pointer", padding: 0 }}
                      >
                        {attachment.original_name}
                      </button>
                    ) : (
                      <span>{attachment.original_name}</span>
                    )}
                    <span style={{ color: "#666", marginLeft: 6 }}>({formatFileSize(attachment.size_bytes)})</span>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        ))}
        {state.isThinking && !state.streamingText ? <div>Агент думает...</div> : null}
      </div>

      {state.error ? <p style={{ color: "#b00020" }}>{state.error}</p> : null}

      <form onSubmit={onSubmit} style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={onSelectedFilesChanged}
          style={{ display: "none" }}
        />
        <button type="button" onClick={onPickFiles} style={{ padding: "10px 12px", borderRadius: 8, border: "1px solid #ccc", background: "#fff" }}>
          Скрепка
        </button>
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
      {selectedFiles.length > 0 ? (
        <ul style={{ marginTop: 8, paddingLeft: 18 }}>
          {selectedFiles.map((file, idx) => (
            <li key={`${file.name}-${file.size}-${idx}`}>
              {file.name} <span style={{ color: "#666" }}>({formatFileSize(file.size)})</span>{" "}
              <button
                type="button"
                onClick={() => onRemoveSelectedFile(idx)}
                style={{ border: "none", background: "none", color: "#b00020", cursor: "pointer" }}
              >
                удалить
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </main>
  );
}
