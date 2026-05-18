// chips all | profile | preference | fact | goal | event; active highlighted

"use client";

import { MEMORY_TYPES } from "persona/lib/types";

type Props = {
    type: string | null;
    setType: (type: string | null) => void;
};

export default function TypeFilter({ type, setType }: Props) {
    return (
        <div className="flex items-center space-x-2">
            <span className="text-xs text-zinc-400">filter by type</span>
            <div className="flex items-center space-x-1">
                <button className={`rounded-full px-2 py-0.5 text-xs ${type === null ? "bg-zinc-700 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white"}`} onClick={() => setType(null)}>
                    all
                </button>
                {MEMORY_TYPES.map((t) => (
                    <button key={t} className={`rounded-full px-2 py-0.5 text-xs ${type === t ? "bg-zinc-700 text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white"}`} onClick={() => setType(t)}>
                        {t}
                    </button>
                ))}
            </div>
        </div>
    );
}

