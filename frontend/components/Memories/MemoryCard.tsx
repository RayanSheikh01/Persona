
"use client";

import Link from "next/link";
import type { Memory } from "persona/lib/types";

type Props = {
  memory: Memory;
};

export default function MemoryCard({ memory }: Props) {
    return (
        <Link           href={`/memories/${memory.id}`}
            className="block rounded-md border border-zinc-800 bg-zinc-900/50 p-3 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
        >
            <span className={`inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider ${TYPE_COLORS[memory.type]}`}>
                {memory.type}
            </span>
            <p className="mt-2 line-clamp-3 text-xs text-zinc-300">
                {memory.content}
            </p>
        </Link>
    );
}
