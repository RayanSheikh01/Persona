"use client";

import Link from "next/link";
import { Plus, BookOpen } from "lucide-react";
import { Button } from "persona/components/ui/button";
import type { Conversation } from "persona/lib/types";
import { cn } from "persona/lib/utils";

type Props = {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
};

function formatTimestamp(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

export default function ConversationList({
  conversations,
  activeId,
  onSelect,
  onNewChat,
}: Props) {
  return (
    <aside className="flex h-screen flex-col border-r border-zinc-800 bg-zinc-950">
      <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
        <span className="font-mono text-sm tracking-tight">persona</span>
        <Link
          href="/memories"
          className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-100"
        >
          <BookOpen className="h-3.5 w-3.5" />
          memories
        </Link>
      </div>

      <div className="px-3 py-3">
        <Button
          size="sm"
          variant="secondary"
          className="w-full justify-start gap-2"
          onClick={onNewChat}
        >
          <Plus className="h-4 w-4" />
          new chat
        </Button>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 pb-3">
        {conversations.length === 0 ? (
          <p className="px-2 py-4 text-xs text-zinc-500">no conversations yet</p>
        ) : (
          <ul className="space-y-1">
            {conversations.map((c) => {
              const isActive = c.id === activeId;
              return (
                <li key={c.id}>
                  <button
                    type="button"
                    onClick={() => onSelect(c.id)}
                    className={cn(
                      "flex w-full flex-col items-start gap-0.5 rounded-md px-3 py-2 text-left text-sm transition-colors",
                      isActive
                        ? "bg-zinc-800 text-zinc-100"
                        : "text-zinc-300 hover:bg-zinc-900",
                    )}
                  >
                    <span className="line-clamp-1 w-full">
                      {c.title ?? "untitled"}
                    </span>
                    <span className="text-[11px] text-zinc-500">
                      {formatTimestamp(c.last_message_at)}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </nav>
    </aside>
  );
}
