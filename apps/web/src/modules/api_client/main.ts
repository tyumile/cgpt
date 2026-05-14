import { Chat, Message, MessagePostResponse } from "@/src/shared/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function listChats(): Promise<Chat[]> {
  return request<Chat[]>("/api/chats");
}

export async function createChat(title?: string): Promise<Chat> {
  return request<Chat>("/api/chats", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function getChat(chatId: number): Promise<Chat> {
  return request<Chat>(`/api/chats/${chatId}`);
}

export async function listMessages(chatId: number): Promise<Message[]> {
  return request<Message[]>(`/api/chats/${chatId}/messages`);
}

export async function postMessage(chatId: number, content: string): Promise<MessagePostResponse> {
  return request<MessagePostResponse>(`/api/chats/${chatId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}
