import type {
  Conversation,
  MemoriesList,
  Memory,
  MemoryType,
  Message,
  Stats,
} from "./types";

const API_KEY = process.env.NEXT_PUBLIC_PERSONA_API_KEY ?? "";

function headers(extra?: HeadersInit): HeadersInit {
  return {
    "X-Persona-Key": API_KEY,
    ...(extra ?? {}),
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: headers(init?.headers),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`api ${path} failed (${res.status}): ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  createConversation(): Promise<Conversation> {
    return request<Conversation>("/conversations", { method: "POST" });
  },
  listConversations(): Promise<Conversation[]> {
    return request<Conversation[]>("/conversations");
  },
  listMessages(conversationId: string): Promise<Message[]> {
    return request<Message[]>(
      `/conversations/${conversationId}/messages`,
    );
  },
  listMemories(params: {
    type?: MemoryType;
    q?: string;
    limit?: number;
    cursor?: number;
    include_superseded?: boolean;
  } = {}): Promise<MemoriesList> {
    const search = new URLSearchParams();
    if (params.type) search.set("type", params.type);
    if (params.q) search.set("q", params.q);
    if (params.limit != null) search.set("limit", String(params.limit));
    if (params.cursor != null) search.set("cursor", String(params.cursor));
    if (params.include_superseded)
      search.set("include_superseded", "true");
    const qs = search.toString();
    return request<MemoriesList>(`/memories${qs ? `?${qs}` : ""}`);
  },
  getMemory(id: string): Promise<Memory> {
    return request<Memory>(`/memories/${id}`);
  },
  getRetrievals(messageId: string): Promise<Memory[]> {
    return request<Memory[]>(`/messages/${messageId}/retrievals`);
  },
  stats(): Promise<Stats> {
    return request<Stats>("/stats");
  },
};
