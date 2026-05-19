import { getCabinetSessionToken } from "@/src/modules/cabinet_auth/main";
import { Chat, Message, MessagePostResponse } from "@/src/shared/types";

const PUBLIC_BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "/gpt";
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? PUBLIC_BASE_PATH;

type RequestOptions = RequestInit & {
  sessionToken?: string | null;
  responseType?: "json" | "blob" | "none";
};

async function request<T>(path: string, init?: RequestOptions): Promise<T> {
  const { sessionToken, responseType = "json", ...requestInit } = init ?? {};
  const token = sessionToken ?? getCabinetSessionToken();
  const isFormData = typeof FormData !== "undefined" && requestInit.body instanceof FormData;
  const response = await fetch(`${API_BASE}${path}`, {
    ...requestInit,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
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

  if (responseType === "blob") {
    return (await response.blob()) as T;
  }

  if (responseType === "none") {
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
  const form = new FormData();
  form.append("content", content);
  return request<MessagePostResponse>(`/api/chats/${chatId}/messages`, {
    method: "POST",
    body: form,
    sessionToken,
  });
}

export async function postMessageWithAttachments(
  chatId: number,
  content: string,
  files: File[],
  sessionToken?: string,
): Promise<MessagePostResponse> {
  const form = new FormData();
  form.append("content", content);
  for (const file of files) {
    form.append("files", file, file.name);
  }
  return request<MessagePostResponse>(`/api/chats/${chatId}/messages`, {
    method: "POST",
    body: form,
    sessionToken,
  });
}

export async function downloadAttachment(chatId: number, fileId: number, sessionToken?: string): Promise<Blob> {
  return request<Blob>(`/api/chats/${chatId}/messages/files/${fileId}`, {
    method: "GET",
    responseType: "blob",
    sessionToken,
  });
}
