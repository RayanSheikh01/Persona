import type { ChatDone } from "./types";

const API_KEY = process.env.NEXT_PUBLIC_PERSONA_API_KEY ?? "";

export type ChatHandlers = {
  onMemoriesUsed?: (memoryIds: string[]) => void;
  onToken?: (token: string) => void;
  onDone?: (done: ChatDone) => void;
  onError?: (err: unknown) => void;
};

export async function streamChat(
  conversationId: string,
  message: string,
  handlers: ChatHandlers,
  signal?: AbortSignal,
): Promise<void> {
  let res: Response;
  try {
    res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Persona-Key": API_KEY,
      },
      body: JSON.stringify({ conversation_id: conversationId, message }),
      signal,
    });
  } catch (err) {
    handlers.onError?.(err);
    return;
  }

  if (!res.ok || !res.body) {
    handlers.onError?.(
      new Error(`chat failed (${res.status}): ${await res.text().catch(() => "")}`),
    );
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let sep = buffer.indexOf("\n\n");
      while (sep !== -1) {
        const raw = buffer.slice(0, sep);
        buffer = buffer.slice(sep + 2);
        dispatch(raw, handlers);
        sep = buffer.indexOf("\n\n");
      }
    }
    if (buffer.trim()) dispatch(buffer, handlers);
  } catch (err) {
    handlers.onError?.(err);
  } finally {
    reader.releaseLock();
  }
}

function dispatch(block: string, handlers: ChatHandlers): void {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }
  if (dataLines.length === 0) return;
  const raw = dataLines.join("\n");

  let payload: unknown;
  try {
    payload = JSON.parse(raw);
  } catch {
    payload = raw;
  }

  switch (event) {
    case "retrieved":
    case "memories_used":
      if (Array.isArray(payload)) {
        handlers.onMemoriesUsed?.(payload as string[]);
      }
      break;
    case "token":
      if (typeof payload === "string") handlers.onToken?.(payload);
      break;
    case "done":
      handlers.onDone?.(payload as ChatDone);
      break;
    case "error":
      handlers.onError?.(payload);
      break;
  }
}
