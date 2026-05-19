export type Chat = {
  id: number;
  workspace_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  preview_first_message?: string | null;
};

export type Message = {
  id: number;
  workspace_id: number;
  chat_id: number;
  role: "user" | "assistant" | "system";
  content: string;
  status: "created" | "streaming" | "done" | "failed";
  created_at: string;
  updated_at: string;
};

export type CabinetSession = {
  token: string;
  email: string;
  full_name: string;
  expires_at: number;
};

export type ChatHistoryItem = {
  chat: Chat;
  preview: string | null;
};

export type MessagePostResponse = {
  message_id: number;
  agent_run_id: number;
};

export type WsEvent =
  | { event: "agent_run_started"; agent_run_id: number }
  | { event: "assistant_chunk"; agent_run_id: number; chunk: string; full_text: string }
  | { event: "assistant_done"; agent_run_id: number; output_message_id: number; full_text: string }
  | { event: "assistant_error"; agent_run_id: number; error: string };
