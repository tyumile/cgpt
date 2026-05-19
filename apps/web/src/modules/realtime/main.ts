import { WsEvent } from "@/src/shared/types";

const PUBLIC_BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "/gpt";
const WS_BASE =
  process.env.NEXT_PUBLIC_WS_BASE ??
  (typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}${PUBLIC_BASE_PATH}`
    : "ws://localhost:8000");

export type WsConnection = {
  close: () => void;
};

export function connectChatWs(
  chatId: number,
  sessionToken: string | null,
  onEvent: (event: WsEvent) => void,
  onError: (message: string) => void,
): WsConnection {
  let closed = false;
  let attempts = 0;
  let socket: WebSocket | null = null;

  const connect = () => {
    if (closed) {
      return;
    }

    const wsUrl = new URL(`${WS_BASE}/ws/chats/${chatId}`);
    if (sessionToken) {
      wsUrl.searchParams.set("session_token", sessionToken);
    }

    socket = new WebSocket(wsUrl.toString());

    socket.onmessage = (ev) => {
      try {
        const event = JSON.parse(ev.data) as WsEvent;
        onEvent(event);
      } catch {
        onError("Failed to parse websocket event.");
      }
    };

    socket.onerror = () => {
      onError("WebSocket connection error.");
    };

    socket.onclose = () => {
      if (closed) {
        return;
      }
      if (attempts >= 3) {
        onError("WebSocket disconnected after retries.");
        return;
      }
      attempts += 1;
      setTimeout(connect, 1000 * attempts);
    };
  };

  connect();

  return {
    close: () => {
      closed = true;
      if (socket) {
        socket.close();
      }
    },
  };
}
