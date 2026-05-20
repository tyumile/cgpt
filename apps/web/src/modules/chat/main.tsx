"use client";

import { ChangeEvent, FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";

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

type Copy = {
  you: string;
  assistant: string;
  thinking: string;
  attach: string;
  send: string;
  remove: string;
  placeholder: string;
  sendFailed: string;
};

const COPY_RU: Copy = {
  you: "Вы",
  assistant: "Ассистент",
  thinking: "Ассистент думает...",
  attach: "Файл",
  send: "Отправить",
  remove: "Удалить",
  placeholder: "Напишите сообщение",
  sendFailed: "Не удалось отправить сообщение.",
};

const COPY_EN: Copy = {
  you: "You",
  assistant: "Assistant",
  thinking: "Assistant is thinking...",
  attach: "Attach",
  send: "Send",
  remove: "Remove",
  placeholder: "Message",
  sendFailed: "Failed to send message.",
};

function getUiCopy(): Copy {
  if (typeof navigator === "undefined") {
    return COPY_RU;
  }
  return navigator.language.toLowerCase().startsWith("ru") ? COPY_RU : COPY_EN;
}

export default function ChatScreen({
  chatId,
  initialMessages,
  sessionToken,
  onUserMessageSubmitted,
  onUserMessageCreated,
  onUserMessageFailed,
}: ChatScreenProps) {
  const copy = useMemo(getUiCopy, []);

  const [text, setText] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [state, setState] = useState(() => buildInitialState(initialMessages));
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) {
      return;
    }
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [state.messages, state.streamingText, state.isThinking]);

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

  const sendMessage = async () => {
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
        error: err instanceof Error ? err.message : copy.sendFailed,
      }));
    }
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    await sendMessage();
  };

  const onComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage();
    }
  };

  return (
    <main className="cg-thread-wrap">
      <div className="cg-thread-scroll" ref={scrollRef}>
        <div className="cg-thread-inner">
          {renderedMessages.map((message) => (
            <div key={message.id} className={`cg-msg ${message.role === "user" ? "cg-msg--user" : "cg-msg--assistant"}`}>
              <div className="cg-msg-bubble">
                <p className="cg-msg-head">{message.role === "user" ? copy.you : copy.assistant}</p>
                {message.role === "assistant" ? (
                  renderAssistantMarkdown(message.content)
                ) : (
                  <div className="cg-msg-plain">{message.content}</div>
                )}

                {message.attachments.length > 0 ? (
                  <ul className="cg-list">
                    {message.attachments.map((attachment) => (
                      <li key={attachment.id}>
                        {attachment.download_path ? (
                          <button type="button" onClick={() => void onDownloadAttachment(attachment)} className="cg-link-btn">
                            {attachment.original_name}
                          </button>
                        ) : (
                          <span>{attachment.original_name}</span>
                        )}
                        <span className="cg-file-size"> ({formatFileSize(attachment.size_bytes)})</span>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            </div>
          ))}

          {state.isThinking && !state.streamingText ? <div className="cg-thinking">{copy.thinking}</div> : null}
          {state.error ? <p className="cg-error">{state.error}</p> : null}
        </div>
      </div>

      <div className="cg-composer-wrap">
        <div className="cg-composer-inner">
          <input ref={fileInputRef} type="file" multiple onChange={onSelectedFilesChanged} style={{ display: "none" }} />

          {selectedFiles.length > 0 ? (
            <ul className="cg-file-chips">
              {selectedFiles.map((file, idx) => (
                <li key={`${file.name}-${file.size}-${idx}`} className="cg-file-chip">
                  <span>{file.name}</span>
                  <span className="cg-file-size">{formatFileSize(file.size)}</span>
                  <button type="button" onClick={() => onRemoveSelectedFile(idx)} className="cg-link-btn">
                    {copy.remove}
                  </button>
                </li>
              ))}
            </ul>
          ) : null}

          <form onSubmit={onSubmit} className="cg-form">
            <button type="button" onClick={onPickFiles} className="cg-btn cg-btn--ghost" aria-label={copy.attach}>
              +
            </button>

            <textarea
              value={text}
              onChange={(event) => setText(event.target.value)}
              onKeyDown={onComposerKeyDown}
              placeholder={copy.placeholder}
              className="cg-textarea"
              rows={1}
            />

            <button type="submit" className="cg-btn cg-btn--primary" disabled={!text.trim()}>
              {copy.send}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
