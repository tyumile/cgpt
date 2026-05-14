"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import ChatScreen from "@/src/modules/chat/main";
import { loadInitialMessages, normalizeChatParam, resolveChat } from "@/src/modules/chat_bootstrap/main";
import { Message } from "@/src/shared/types";

export default function ChatPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [chatId, setChatId] = useState<number | null>(normalizeChatParam(params.id));
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const bootstrap = async () => {
      try {
        setLoading(true);
        setError(null);
        const chat = await resolveChat(params.id);
        if (!active) {
          return;
        }
        if (params.id === "new") {
          router.replace(`/chat/${chat.id}`);
          return;
        }
        const history = await loadInitialMessages(chat.id);
        if (!active) {
          return;
        }
        setChatId(chat.id);
        setMessages(history);
      } catch (err) {
        if (!active) {
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load chat");
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
  }, [params.id, router]);

  if (loading || chatId === null) {
    return <main style={{ maxWidth: 900, margin: "0 auto", padding: 20 }}>Загрузка...</main>;
  }

  if (error) {
    return (
      <main style={{ maxWidth: 900, margin: "0 auto", padding: 20 }}>
        <p style={{ color: "#b00020" }}>{error}</p>
      </main>
    );
  }

  return <ChatScreen chatId={chatId} initialMessages={messages} />;
}
