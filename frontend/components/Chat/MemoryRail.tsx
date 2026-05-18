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

type Props = {
  memories: Memory[];
};

export default function MemoryRail({ memories }: Props) {
  return (
    <aside className="flex h-screen flex-col border-l border-zinc-800 bg-zinc-950">
      <div className="border-b border-zinc-800 px-4 py-3">
        <h2 className="font-mono text-xs uppercase tracking-wider text-zinc-400">
          memories used
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-3">
        {memories.length === 0 ? (
          <p className="px-2 py-2 text-xs text-zinc-500">
            none yet — memories surfaced for the current turn appear here
          </p>
        ) : (
          <ul className="space-y-2">
            {memories.map((m) => (
              <li key={m.id}>
                <Link
                  href={`/memories/${m.id}`}
                  className="block rounded-md border border-zinc-800 bg-zinc-900/50 p-3 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
                >
                  <span
                    className={`inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider ${TYPE_COLORS[m.type]}`}
                  >
                    {m.type}
                  </span>
                  <p className="mt-2 line-clamp-3 text-xs text-zinc-300">
                    {m.content}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
