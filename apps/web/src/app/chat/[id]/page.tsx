"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import ChatScreen from "@/src/modules/chat/main";
import { deleteChat } from "@/src/modules/api_client/main";
import { authorizeCabinet, clearCabinetSession, loadCabinetSession } from "@/src/modules/cabinet_auth/main";
import { loadInitialMessages, normalizeChatParam, resolveChat } from "@/src/modules/chat_bootstrap/main";
import ChatHistorySidebar from "@/src/modules/chat_history/main";
import { CabinetSession, Message } from "@/src/shared/types";

export default function ChatPage({ params }: { params: { id: string } }) {
  const router = useRouter();

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
        const message = err instanceof Error ? err.message : "Failed to load chat";
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
  }, [params.id, router, session?.token]);

  const onAuthSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const trimmedEmail = email.trim();
    const trimmedName = fullName.trim();

    if (!/^\S+@\S+\.\S+$/.test(trimmedEmail)) {
      setAuthError("Enter a valid email address.");
      return;
    }

    if (trimmedName.length < 2) {
      setAuthError("Enter full name.");
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
    return <main style={{ margin: "0 auto", padding: 20 }}>Loading...</main>;
  }

  if (!session) {
    return (
      <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 20, background: "#f2f2f3" }}>
        <form
          onSubmit={onAuthSubmit}
          style={{
            width: "100%",
            maxWidth: 420,
            background: "#fff",
            border: "1px solid #e2e2e2",
            borderRadius: 12,
            padding: 20,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <h1 style={{ margin: 0 }}>Cabinet access</h1>
          <p style={{ margin: 0, color: "#555" }}>Enter account details to start chatting.</p>

          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
            />
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span>Full name</span>
            <input
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
              style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
            />
          </label>

          {authError ? <p style={{ margin: 0, color: "#b00020" }}>{authError}</p> : null}

          <button
            type="submit"
            disabled={authLoading}
            style={{ padding: "10px 14px", borderRadius: 8, border: "none", background: "#111", color: "#fff", opacity: authLoading ? 0.7 : 1 }}
          >
            {authLoading ? "Authorizing..." : "Continue"}
          </button>
        </form>
      </main>
    );
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#fff" }}>
      <ChatHistorySidebar
        activeChatId={chatId}
        sessionToken={session.token}
        refreshNonce={historyRefreshNonce}
        optimisticPreview={optimisticPreview}
        onCreateChat={() => router.push("/chat/new")}
        onSelectChat={(nextChatId) => router.push(`/chat/${nextChatId}`)}
        onDelete={onDeleteChat}
      />

      <section style={{ flex: 1, minWidth: 0, padding: "0 2%", boxSizing: "border-box" }}>
        {loading ? <main style={{ margin: "0 auto", padding: 20 }}>Загрузка...</main> : null}

        {!loading && error ? (
          <main style={{ margin: "0 auto", padding: 20 }}>
            <p style={{ color: "#b00020" }}>{error}</p>
          </main>
        ) : null}

        {!loading && !error && chatId === null ? (
          <main style={{ margin: "0 auto", padding: 20 }}>
            <p style={{ margin: 0, color: "#444" }}>Чат не выбран. Выберите существующий чат или создайте новый.</p>
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
