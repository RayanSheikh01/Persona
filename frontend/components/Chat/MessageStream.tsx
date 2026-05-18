"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import { Send } from "lucide-react";
import { Button } from "persona/components/ui/button";
import type { Message } from "persona/lib/types";
import { cn } from "persona/lib/utils";

type Props = {
  messages: Message[];
  pending: string;
  streaming: boolean;
  onSend: (text: string) => void;
};

export default function MessageStream({
  messages,
  pending,
  streaming,
  onSend,
}: Props) {
  const endRef = useRef<HTMLDivElement>(null);
  const [draft, setDraft] = useState("");

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, pending]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text || streaming) return;
    onSend(text);
    setDraft("");
  };

  const isEmpty = messages.length === 0 && !pending;

  return (
    <section className="flex h-screen flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto flex max-w-2xl flex-col gap-6 px-6 py-8">
          {isEmpty ? (
            <p className="mt-24 text-center text-sm text-zinc-500">
              start a new conversation
            </p>
          ) : (
            messages.map((m) => <Bubble key={m.id} role={m.role} content={m.content} />)
          )}
          {streaming && (
            <Bubble
              role="assistant"
              content={pending || "…"}
              isStreaming={!pending}
            />
          )}
          <div ref={endRef} />
        </div>
      </div>

      <form
        onSubmit={handleSubmit}
        className="border-t border-zinc-800 bg-zinc-950 px-6 py-4"
      >
        <div className="mx-auto flex max-w-2xl items-end gap-2">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e as unknown as FormEvent<HTMLFormElement>);
              }
            }}
            placeholder="message persona…"
            rows={1}
            className="flex-1 resize-none rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm placeholder:text-zinc-500 focus:border-zinc-600 focus:outline-none"
          />
          <Button type="submit" size="sm" disabled={streaming || !draft.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </section>
  );
}

function Bubble({
  role,
  content,
  isStreaming = false,
}: {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}) {
  const isUser = role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-2.5",
          isUser
            ? "bg-zinc-100 text-zinc-900"
            : "bg-zinc-900 text-zinc-100",
        )}
      >
        <div
          className={cn(
            "prose prose-sm max-w-none break-words [&_p]:my-1 [&_pre]:my-2",
            isUser ? "text-black [&_*]:text-black" : "prose-invert",
          )}
        >
          {isStreaming ? (
            <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-zinc-500" />
          ) : (
            <ReactMarkdown>{content}</ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  );
}
