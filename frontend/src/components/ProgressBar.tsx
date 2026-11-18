"use client";

export function ProgressBar({ stage, percent }: { stage: string; percent: number }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="capitalize text-zinc-300">{stage || "queued"}</span>
        <span className="text-zinc-500">{percent}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-violet-500 transition-all"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
