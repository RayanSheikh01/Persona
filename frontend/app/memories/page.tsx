"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, Search } from "lucide-react";
import MemoryCard from "persona/components/Memories/MemoryCard";
import TypeFilter from "persona/components/Memories/TypeFilter";
import { api } from "persona/lib/api";
import type { Memory, MemoryType } from "persona/lib/types";

export default function MemoriesPage() {
  const [type, setType] = useState<MemoryType | null>(null);
  const [q, setQ] = useState("");
  const [includeSuperseded, setIncludeSuperseded] = useState(false);
  const [items, setItems] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    const timer = window.setTimeout(() => {
      api
        .listMemories({
          type: type ?? undefined,
          q: q.trim() || undefined,
          include_superseded: includeSuperseded,
          limit: 100,
        })
        .then((res) => {
          if (!cancelled) setItems(res.items);
        })
        .catch((err) => {
          if (!cancelled) {
            console.error(err);
            setItems([]);
          }
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }, q ? 250 : 0);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [type, q, includeSuperseded]);

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <Link
              href="/"
              className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-200"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              back to chat
            </Link>
            <h1 className="mt-2 font-mono text-2xl tracking-tight">memories</h1>
            <p className="mt-1 text-sm text-zinc-400">
              everything persona has remembered, grouped by type
            </p>
          </div>
        </header>

        <div className="mb-6 flex flex-col gap-4">
          <TypeFilter value={type} onChange={setType} />

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
              <input
                type="text"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="semantic search…"
                className="w-full rounded-md border border-zinc-800 bg-zinc-900 py-2 pl-9 pr-3 text-sm placeholder:text-zinc-500 focus:border-zinc-600 focus:outline-none"
              />
            </div>
            <label className="inline-flex items-center gap-2 text-xs text-zinc-400">
              <input
                type="checkbox"
                checked={includeSuperseded}
                onChange={(e) => setIncludeSuperseded(e.target.checked)}
                className="h-3.5 w-3.5 rounded border-zinc-700 bg-zinc-900"
              />
              include superseded
            </label>
          </div>
        </div>

        {loading ? (
          <p className="py-12 text-center text-sm text-zinc-500">loading…</p>
        ) : items.length === 0 ? (
          <p className="py-12 text-center text-sm text-zinc-500">
            no memories match
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
            {items.map((m) => (
              <MemoryCard key={m.id} memory={m} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
