import { createChat, getChat, listMessages } from "@/src/modules/api_client/main";
import { Chat, Message } from "@/src/shared/types";

export async function resolveChat(chatParam: string, sessionToken?: string): Promise<Chat | null> {
  if (chatParam === "empty") {
    return null;
  }

  if (chatParam === "new") {
    return createChat("Новый чат", sessionToken);
  }

  const chatId = Number(chatParam);
  if (!Number.isFinite(chatId)) {
    return createChat("Новый чат", sessionToken);
  }

  return getChat(chatId, sessionToken);
}

export async function loadInitialMessages(chatId: number, sessionToken?: string): Promise<Message[]> {
  return listMessages(chatId, sessionToken);
}

export function normalizeChatParam(chatParam: string): number | null {
  const parsed = Number(chatParam);
  if (!Number.isFinite(parsed)) {
    return null;
  }
  return parsed;
}
