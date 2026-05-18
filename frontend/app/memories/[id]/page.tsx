"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { api } from "persona/lib/api";
import type { Memory, MemoryType } from "persona/lib/types";

const TYPE_COLORS: Record<MemoryType, string> = {
  profile: "bg-violet-500/15 text-violet-300 border-violet-500/30",
  preference: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  fact: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  goal: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  event: "bg-rose-500/15 text-rose-300 border-rose-500/30",
};

export default function MemoryDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id;
  const [memory, setMemory] = useState<Memory | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!id) return;
    api
      .getMemory(id)
      .then(setMemory)
      .catch(() => setNotFound(true));
  }, [id]);

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-2xl px-6 py-10">
        <Link
          href="/memories"
          className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-200"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          back to memories
        </Link>

        {notFound ? (
          <p className="mt-12 text-center text-sm text-zinc-500">
            memory not found
          </p>
        ) : !memory ? (
          <div className="mt-8 space-y-4">
            <div className="h-6 w-24 animate-pulse rounded bg-zinc-900" />
            <div className="h-24 w-full animate-pulse rounded bg-zinc-900" />
          </div>
        ) : (
          <article className="mt-6 space-y-6">
            <span
              className={`inline-flex items-center rounded border px-2 py-1 font-mono text-xs uppercase tracking-wider ${TYPE_COLORS[memory.type]}`}
            >
              {memory.type}
            </span>

            <p className="whitespace-pre-wrap text-base text-zinc-100">
              {memory.content}
            </p>

            <dl className="grid grid-cols-1 gap-x-6 gap-y-3 border-t border-zinc-800 pt-6 text-sm sm:grid-cols-[max-content_1fr]">
              <dt className="text-zinc-500">importance</dt>
              <dd className="font-mono">
                {"●".repeat(memory.importance)}
                <span className="text-zinc-700">
                  {"○".repeat(5 - memory.importance)}
                </span>{" "}
                <span className="text-zinc-500">({memory.importance}/5)</span>
              </dd>

              <dt className="text-zinc-500">created</dt>
              <dd className="font-mono text-zinc-300">
                {new Date(memory.created_at).toLocaleString()}
              </dd>

              <dt className="text-zinc-500">updated</dt>
              <dd className="font-mono text-zinc-300">
                {new Date(memory.updated_at).toLocaleString()}
              </dd>

              <dt className="text-zinc-500">source conversation</dt>
              <dd>
                <Link
                  href={`/?conversation=${memory.source_conversation_id}`}
                  className="font-mono text-xs text-sky-400 hover:underline"
                >
                  {memory.source_conversation_id}
                </Link>
              </dd>

              <dt className="text-zinc-500">id</dt>
              <dd className="font-mono text-xs text-zinc-400 break-all">
                {memory.id}
              </dd>

              {memory.superseded_by && (
                <>
                  <dt className="text-zinc-500">superseded by</dt>
                  <dd>
                    <Link
                      href={`/memories/${memory.superseded_by}`}
                      className="font-mono text-xs text-sky-400 hover:underline"
                    >
                      {memory.superseded_by}
                    </Link>
                  </dd>
                </>
              )}
            </dl>
          </article>
        )}
      </div>
    </main>
  );
}
