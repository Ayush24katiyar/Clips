"use client";

import type { Clip } from "@/lib/api";

export function ClipCard({ clip }: { clip: Clip }) {
  return (
    <article className="overflow-hidden rounded-xl border border-white/10 bg-white/5">
      <div className="aspect-9/16 bg-black">
        {clip.thumbnail_path ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={clip.thumbnail_path}
            alt={clip.title}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-xs text-zinc-600">
            No thumbnail
          </div>
        )}
      </div>
      <div className="space-y-2 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-sm font-semibold leading-snug">{clip.title || "Untitled clip"}</h3>
          <span className="shrink-0 rounded bg-violet-500/15 px-2 py-1 text-xs text-violet-300">
            {clip.score.toFixed(0)}
          </span>
        </div>
        <p className="line-clamp-2 text-xs text-zinc-500">{clip.description}</p>
        <p className="text-xs text-zinc-600">
          {clip.start.toFixed(1)}s – {clip.end.toFixed(1)}s
        </p>
        <a
          href={clip.file_path}
          className="inline-block rounded bg-white/10 px-3 py-1.5 text-xs hover:bg-white/20"
        >
          Download MP4
        </a>
      </div>
    </article>
  );
}
