"use client";

import type { Streamer } from "@/lib/api";

export function StreamerCard({ streamer }: { streamer: Streamer }) {
  return (
    <article className="flex items-center gap-4 rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-violet-500/20 text-lg font-bold text-violet-300">
        {streamer.name.charAt(0).toUpperCase()}
      </div>
      <div className="min-w-0 flex-1">
        <h3 className="truncate text-sm font-semibold">{streamer.name}</h3>
        <p className="truncate text-xs text-zinc-500">
          {streamer.platform} · {streamer.category ?? "General"} · {streamer.country ?? "global"}
        </p>
      </div>
      <a
        href={streamer.channel_url}
        target="_blank"
        rel="noreferrer"
        className="shrink-0 rounded bg-white/10 px-3 py-1.5 text-xs hover:bg-white/20"
      >
        Visit
      </a>
    </article>
  );
}
