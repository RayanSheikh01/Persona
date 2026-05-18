export type MemoryType = "profile" | "preference" | "fact" | "goal" | "event";

export const MEMORY_TYPES: MemoryType[] = [
  "profile",
  "preference",
  "fact",
  "goal",
  "event",
];

export type Memory = {
  id: string;
  type: MemoryType;
  content: string;
  importance: number;
  created_at: string;
  updated_at: string;
  source_message_id: string;
  source_conversation_id: string;
  superseded_by: string | null;
  related_ids: string[];
};

export type Conversation = {
  id: string;
  title: string | null;
  created_at: string;
  last_message_at: string | null;
};

export type Role = "user" | "assistant";

export type Message = {
  id: string;
  conversation_id: string;
  role: Role;
  content: string;
  created_at: string;
};

export type MemoriesList = {
  items: Memory[];
  next_cursor: number | null;
};

export type Stats = {
  totals: {
    memories: number;
    messages: number;
    conversations: number;
  };
  by_type: Record<MemoryType, number>;
  last_activity: string | null;
};

export type ChatDone = {
  user_message_id: string;
  assistant_message_id: string;
  new_memory_ids: string[];
  retrieved_memory_ids?: string[];
};
