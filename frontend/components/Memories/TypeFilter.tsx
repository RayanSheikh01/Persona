"use client";

import { MEMORY_TYPES, type MemoryType } from "persona/lib/types";
import { cn } from "persona/lib/utils";

type Props = {
  value: MemoryType | null;
  onChange: (type: MemoryType | null) => void;
};

const BASE = "rounded-full border px-3 py-1 font-mono text-xs uppercase tracking-wider transition-colors";

export default function TypeFilter({ value, onChange }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        onClick={() => onChange(null)}
        className={cn(
          BASE,
          value === null
            ? "border-zinc-200 bg-zinc-100 text-zinc-900"
            : "border-zinc-800 bg-zinc-900 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200",
        )}
      >
        all
      </button>
      {MEMORY_TYPES.map((t) => {
        const active = value === t;
        return (
          <button
            key={t}
            type="button"
            onClick={() => onChange(t)}
            className={cn(
              BASE,
              active
                ? "border-zinc-200 bg-zinc-100 text-zinc-900"
                : "border-zinc-800 bg-zinc-900 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200",
            )}
          >
            {t}
          </button>
        );
      })}
    </div>
  );
}
