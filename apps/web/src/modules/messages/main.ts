import { Message, WsEvent } from "@/src/shared/types";

export type MessageState = {
  messages: Message[];
  streamingText: string;
  error: string | null;
  isThinking: boolean;
};

export function buildInitialState(messages: Message[]): MessageState {
  return {
    messages,
    streamingText: "",
    error: null,
    isThinking: false,
  };
}

export function reduceWsEvent(state: MessageState, event: WsEvent): MessageState {
  if (event.event === "agent_run_started") {
    return { ...state, isThinking: true, error: null };
  }

  if (event.event === "assistant_chunk") {
    return {
      ...state,
      isThinking: true,
      streamingText: event.full_text,
      error: null,
    };
  }

  if (event.event === "assistant_done") {
    const assistant: Message = {
      id: event.output_message_id,
      workspace_id: 0,
      chat_id: 0,
      role: "assistant",
      content: event.full_text,
      status: "done",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    return {
      ...state,
      isThinking: false,
      streamingText: "",
      messages: [...state.messages, assistant],
      error: null,
    };
  }

  return {
    ...state,
    isThinking: false,
    error: event.error,
  };
}
