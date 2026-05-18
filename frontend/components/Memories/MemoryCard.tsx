"use client";

import Link from "next/link";
import type { Memory, MemoryType } from "persona/lib/types";

const TYPE_COLORS: Record<MemoryType, string> = {
  profile: "bg-violet-500/15 text-violet-300 border-violet-500/30",
  preference: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  fact: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  goal: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  event: "bg-rose-500/15 text-rose-300 border-rose-500/30",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function ImportanceDots({ value }: { value: number }) {
  const filled = Math.max(0, Math.min(5, value));
  return (
    <span className="font-mono text-xs tracking-tighter text-zinc-400">
      {"●".repeat(filled)}
      <span className="text-zinc-700">{"○".repeat(5 - filled)}</span>
    </span>
  );
}

type Props = {
  memory: Memory;
};

export default function MemoryCard({ memory }: Props) {
  return (
    <Link
      href={`/memories/${memory.id}`}
      className="flex flex-col gap-3 rounded-lg border border-zinc-800 bg-zinc-900/40 p-4 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
    >
      <div className="flex items-center justify-between gap-2">
        <span
          className={`inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider ${TYPE_COLORS[memory.type]}`}
        >
          {memory.type}
        </span>
        <ImportanceDots value={memory.importance} />
      </div>
      <p className="line-clamp-4 text-sm text-zinc-200">{memory.content}</p>
      <span className="text-[11px] text-zinc-500">
        {formatDate(memory.created_at)}
      </span>
    </Link>
  );
}
