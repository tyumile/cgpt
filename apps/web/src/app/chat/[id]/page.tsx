"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import ChatScreen from "@/src/modules/chat/main";
import { deleteChat } from "@/src/modules/api_client/main";
import { authorizeCabinet, clearCabinetSession, loadCabinetSession } from "@/src/modules/cabinet_auth/main";
import { loadInitialMessages, normalizeChatParam, resolveChat } from "@/src/modules/chat_bootstrap/main";
import ChatHistorySidebar from "@/src/modules/chat_history/main";
import { CabinetSession, Message } from "@/src/shared/types";

type Copy = {
  loading: string;
  authTitle: string;
  authSubtitle: string;
  email: string;
  fullName: string;
  authButton: string;
  authButtonLoading: string;
  invalidEmail: string;
  invalidName: string;
  emptyChatHint: string;
  genericLoadError: string;
};

const COPY_RU: Copy = {
  loading: "Загрузка...",
  authTitle: "Доступ к кабинету",
  authSubtitle: "Введите данные аккаунта, чтобы начать диалог.",
  email: "Email",
  fullName: "Полное имя",
  authButton: "Продолжить",
  authButtonLoading: "Авторизация...",
  invalidEmail: "Введите корректный email.",
  invalidName: "Введите полное имя.",
  emptyChatHint: "Чат не выбран. Выберите существующий чат или создайте новый.",
  genericLoadError: "Не удалось загрузить чат",
};

const COPY_EN: Copy = {
  loading: "Loading...",
  authTitle: "Cabinet access",
  authSubtitle: "Enter account details to start chatting.",
  email: "Email",
  fullName: "Full name",
  authButton: "Continue",
  authButtonLoading: "Authorizing...",
  invalidEmail: "Enter a valid email address.",
  invalidName: "Enter full name.",
  emptyChatHint: "No chat selected. Choose an existing chat or create a new one.",
  genericLoadError: "Failed to load chat",
};

function getUiCopy(): Copy {
  if (typeof navigator === "undefined") {
    return COPY_RU;
  }
  return navigator.language.toLowerCase().startsWith("ru") ? COPY_RU : COPY_EN;
}

export default function ChatPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const copy = useMemo(getUiCopy, []);

  const [session, setSession] = useState<CabinetSession | null>(null);
  const [sessionChecked, setSessionChecked] = useState(false);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);

  const [chatId, setChatId] = useState<number | null>(normalizeChatParam(params.id));
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(params.id !== "empty");
  const [error, setError] = useState<string | null>(null);
  const [historyRefreshNonce, setHistoryRefreshNonce] = useState(0);
  const [optimisticPreview, setOptimisticPreview] = useState<{ chatId: number; content: string } | null>(null);

  useEffect(() => {
    setSession(loadCabinetSession());
    setSessionChecked(true);
  }, []);

  useEffect(() => {
    let active = true;

    const bootstrap = async () => {
      if (!session?.token) {
        if (active) {
          setLoading(false);
        }
        return;
      }

      if (params.id === "empty") {
        if (!active) {
          return;
        }
        setLoading(false);
        setError(null);
        setChatId(null);
        setMessages([]);
        setOptimisticPreview(null);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const chat = await resolveChat(params.id, session.token);
        if (!active) {
          return;
        }
        if (chat === null) {
          setLoading(false);
          setError(null);
          setChatId(null);
          setMessages([]);
          setOptimisticPreview(null);
          return;
        }

        if (params.id === "new") {
          setHistoryRefreshNonce((prev) => prev + 1);
          router.replace(`/chat/${chat.id}`);
          return;
        }

        const history = await loadInitialMessages(chat.id, session.token);
        if (!active) {
          return;
        }

        setChatId(chat.id);
        setMessages(history);
        setOptimisticPreview(null);
      } catch (err) {
        if (!active) {
          return;
        }
        const message = err instanceof Error ? err.message : copy.genericLoadError;
        if (message.includes("cabinet session") || message.includes("401")) {
          clearCabinetSession();
          setSession(null);
        }
        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    void bootstrap();

    return () => {
      active = false;
    };
  }, [copy.genericLoadError, params.id, router, session?.token]);

  const onAuthSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const trimmedEmail = email.trim();
    const trimmedName = fullName.trim();

    if (!/^\S+@\S+\.\S+$/.test(trimmedEmail)) {
      setAuthError(copy.invalidEmail);
      return;
    }

    if (trimmedName.length < 2) {
      setAuthError(copy.invalidName);
      return;
    }

    setAuthError(null);
    setAuthLoading(true);
    try {
      const nextSession = await authorizeCabinet(trimmedEmail, trimmedName);
      setSession(nextSession);
      setHistoryRefreshNonce((prev) => prev + 1);
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Authorization failed.");
    } finally {
      setAuthLoading(false);
    }
  };

  const onDeleteChat = async (targetChatId: number) => {
    if (!session?.token) {
      throw new Error("Cabinet session is missing");
    }

    await deleteChat(targetChatId, session.token);
    setHistoryRefreshNonce((prev) => prev + 1);

    if (targetChatId === chatId) {
      setChatId(null);
      setMessages([]);
      setOptimisticPreview(null);
      setLoading(false);
      setError(null);
      router.push("/chat/empty");
    }
  };

  if (!sessionChecked) {
    return <main className="cg-center-state">{copy.loading}</main>;
  }

  if (!session) {
    return (
      <main className="cg-auth-wrap">
        <form onSubmit={onAuthSubmit} className="cg-auth-card">
          <h1 className="cg-auth-title">{copy.authTitle}</h1>
          <p className="cg-auth-subtitle">{copy.authSubtitle}</p>

          <label className="cg-field">
            <span>{copy.email}</span>
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required className="cg-input" />
          </label>

          <label className="cg-field">
            <span>{copy.fullName}</span>
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} required className="cg-input" />
          </label>

          {authError ? <p className="cg-error">{authError}</p> : null}

          <button type="submit" disabled={authLoading} className="cg-btn cg-btn--primary">
            {authLoading ? copy.authButtonLoading : copy.authButton}
          </button>
        </form>
      </main>
    );
  }

  return (
    <div className="cg-shell">
      <ChatHistorySidebar
        activeChatId={chatId}
        sessionToken={session.token}
        refreshNonce={historyRefreshNonce}
        optimisticPreview={optimisticPreview}
        onCreateChat={() => router.push("/chat/new")}
        onSelectChat={(nextChatId) => router.push(`/chat/${nextChatId}`)}
        onDelete={onDeleteChat}
      />

      <section className="cg-main">
        {loading ? <main className="cg-center-state">{copy.loading}</main> : null}

        {!loading && error ? (
          <main className="cg-center-state cg-center-state--error">
            <p>{error}</p>
          </main>
        ) : null}

        {!loading && !error && chatId === null ? (
          <main className="cg-center-state">
            <p>{copy.emptyChatHint}</p>
          </main>
        ) : null}

        {!loading && !error && chatId !== null ? (
          <ChatScreen
            chatId={chatId}
            initialMessages={messages}
            sessionToken={session.token}
            onUserMessageSubmitted={(content) => setOptimisticPreview({ chatId, content })}
            onUserMessageCreated={() => {
              setHistoryRefreshNonce((prev) => prev + 1);
            }}
            onUserMessageFailed={() => {
              // Keep optimistic preview to avoid sidebar rollback on transient gateway failures.
            }}
          />
        ) : null}
      </section>
    </div>
  );
}
