"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "persona/lib/api";
import { streamChat } from "persona/lib/sse";
import type { Conversation, Memory, Message } from "persona/lib/types";
import ConversationList from "./ConversationList";
import MemoryRail from "./MemoryRail";
import MessageStream from "./MessageStream";

export default function ChatLayout() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [pending, setPending] = useState<string>("");
  const [streaming, setStreaming] = useState(false);
  const [memoriesUsed, setMemoriesUsed] = useState<Memory[]>([]);

  useEffect(() => {
    api.listConversations().then(setConversations).catch(console.error);
  }, []);

  useEffect(() => {
    if (!activeId) {
      setMessages([]);
      return;
    }
    api.listMessages(activeId).then(setMessages).catch(console.error);
    setMemoriesUsed([]);
  }, [activeId]);

  const newChat = useCallback(async () => {
    const conv = await api.createConversation();
    setConversations((prev) => [conv, ...prev]);
    setActiveId(conv.id);
    setMessages([]);
    setMemoriesUsed([]);
  }, []);

  const send = useCallback(
    async (text: string) => {
      if (streaming) return;
      let conversationId = activeId;
      if (!conversationId) {
        const conv = await api.createConversation();
        setConversations((prev) => [conv, ...prev]);
        setActiveId(conv.id);
        conversationId = conv.id;
      }

      const optimistic: Message = {
        id: `temp-${Date.now()}`,
        conversation_id: conversationId,
        role: "user",
        content: text,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, optimistic]);
      setPending("");
      setStreaming(true);
      setMemoriesUsed([]);

      await streamChat(conversationId, text, {
        onMemoriesUsed: async (ids) => {
          if (ids.length === 0) return;
          try {
            const mems = await Promise.all(ids.map((id) => api.getMemory(id)));
            setMemoriesUsed(mems);
          } catch (err) {
            console.error(err);
          }
        },
        onToken: (token) => {
          setPending((prev) => prev + token);
        },
        onDone: async () => {
          try {
            const [msgs, convs] = await Promise.all([
              api.listMessages(conversationId!),
              api.listConversations(),
            ]);
            setMessages(msgs);
            setConversations(convs);
          } catch (err) {
            console.error(err);
          } finally {
            setPending("");
            setStreaming(false);
          }
        },
        onError: (err) => {
          console.error(err);
          setPending("");
          setStreaming(false);
        },
      });
    },
    [activeId, streaming],
  );

  return (
    <div className="grid h-screen grid-cols-[260px_1fr_320px] bg-zinc-950 text-zinc-100">
      <ConversationList
        conversations={conversations}
        activeId={activeId}
        onSelect={setActiveId}
        onNewChat={newChat}
      />
      <MessageStream
        messages={messages}
        pending={pending}
        streaming={streaming}
        onSend={send}
      />
      <MemoryRail memories={memoriesUsed} />
    </div>
  );
}
