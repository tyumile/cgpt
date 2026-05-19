import { getCabinetSessionToken } from "@/src/modules/cabinet_auth/main";
import { Chat, Message, MessagePostResponse } from "@/src/shared/types";

const PUBLIC_BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "/gpt";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? PUBLIC_BASE_PATH;

type RequestOptions = RequestInit & {
  sessionToken?: string | null;
};

async function request<T>(path: string, init?: RequestOptions): Promise<T> {
  const { sessionToken, ...requestInit } = init ?? {};
  const token = sessionToken ?? getCabinetSessionToken();
  const response = await fetch(`${API_BASE}${path}`, {
    ...requestInit,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { "X-Cabinet-Session": token } : {}),
      ...(requestInit.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  if (response.status === 204 || response.status === 205) {
    return undefined as T;
  }

  const text = await response.text();
  if (!text) {
    return undefined as T;
  }

  return JSON.parse(text) as T;
}

export async function listChats(sessionToken?: string): Promise<Chat[]> {
  return request<Chat[]>("/api/chats", { sessionToken });
}

export async function createChat(title?: string, sessionToken?: string): Promise<Chat> {
  return request<Chat>("/api/chats", {
    method: "POST",
    body: JSON.stringify({ title }),
    sessionToken,
  });
}

export async function getChat(chatId: number, sessionToken?: string): Promise<Chat> {
  return request<Chat>(`/api/chats/${chatId}`, { sessionToken });
}

export async function deleteChat(chatId: number, sessionToken?: string): Promise<void> {
  return request<void>(`/api/chats/${chatId}`, {
    method: "DELETE",
    sessionToken,
  });
}

export async function listMessages(chatId: number, sessionToken?: string): Promise<Message[]> {
  return request<Message[]>(`/api/chats/${chatId}/messages`, { sessionToken });
}

export async function postMessage(chatId: number, content: string, sessionToken?: string): Promise<MessagePostResponse> {
  return request<MessagePostResponse>(`/api/chats/${chatId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
    sessionToken,
  });
}
