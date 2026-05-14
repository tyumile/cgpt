import { createChat, getChat, listChats, listMessages } from "@/src/modules/api_client/main";
import { Chat, Message } from "@/src/shared/types";

export async function resolveChat(chatParam: string): Promise<Chat> {
  if (chatParam === "new") {
    const chats = await listChats();
    if (chats.length > 0) {
      return chats[0];
    }
    return createChat("New chat");
  }

  const chatId = Number(chatParam);
  if (!Number.isFinite(chatId)) {
    return createChat("New chat");
  }

  return getChat(chatId);
}

export async function loadInitialMessages(chatId: number): Promise<Message[]> {
  return listMessages(chatId);
}

export function normalizeChatParam(chatParam: string): number | null {
  const parsed = Number(chatParam);
  if (!Number.isFinite(parsed)) {
    return null;
  }
  return parsed;
}
