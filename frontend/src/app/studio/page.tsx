"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { QualitySelector } from "@/components/QualitySelector";
import { api, type CreateJobPayload, type QualityMode } from "@/lib/api";

export default function StudioPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [payload, setPayload] = useState<CreateJobPayload>({
    url: "",
    quality_mode: "visually_lossless",
    ratio: "9:16",
    reframe: "crop",
    source_max_seconds: 1800,
    clip_count: 7,
    burn_captions: true,
    generate_thumbnail: true,
    webm: false,
  });

  const mutation = useMutation({
    mutationFn: () => api.createJob(payload),
    onSuccess: (job) => {
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      router.push(`/jobs/${job.id}`);
    },
  });

  return (
    <section className="mx-auto max-w-2xl space-y-8">
      <h1 className="text-2xl font-bold">New clipping job</h1>

      <div className="space-y-3">
        <label className="text-sm font-medium" htmlFor="url">
          YouTube / Twitch URL
        </label>
        <input
          id="url"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          value={payload.url}
          onChange={(event) => setPayload({ ...payload, url: event.target.value })}
          className="w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-violet-500"
        />
      </div>

      <QualitySelector
        value={payload.quality_mode}
        onChange={(quality_mode: QualityMode) => setPayload({ ...payload, quality_mode })}
      />

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="text-sm font-medium" htmlFor="ratio">Aspect ratio</label>
          <select
            id="ratio"
            value={payload.ratio}
            onChange={(event) => setPayload({ ...payload, ratio: event.target.value })}
            className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3"
          >
            <option value="9:16">9:16 — Shorts / Reels</option>
            <option value="1:1">1:1 — Feed</option>
            <option value="16:9">16:9 — Widescreen</option>
          </select>
        </div>
        <div>
          <label className="text-sm font-medium" htmlFor="count">Clips</label>
          <input
            id="count"
            type="number"
            min={1}
            max={20}
            value={payload.clip_count}
            onChange={(event) => setPayload({ ...payload, clip_count: Number(event.target.value) })}
            className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3"
          />
        </div>
        <div>
          <label className="text-sm font-medium" htmlFor="reframe">Reframe</label>
          <select
            id="reframe"
            value={payload.reframe}
            onChange={(event) =>
              setPayload({ ...payload, reframe: event.target.value as "crop" | "letterbox" })
            }
            className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3"
          >
            <option value="crop">Crop — face / center</option>
            <option value="letterbox">Letterbox — full frame (gaming)</option>
          </select>
        </div>
        <div>
          <label className="text-sm font-medium" htmlFor="maxseconds">
            Max source seconds (0 = full)
          </label>
          <input
            id="maxseconds"
            type="number"
            min={0}
            max={86400}
            value={payload.source_max_seconds}
            onChange={(event) =>
              setPayload({ ...payload, source_max_seconds: Number(event.target.value) })
            }
            className="mt-2 w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-5 text-sm text-zinc-400">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={payload.burn_captions}
            onChange={(event) => setPayload({ ...payload, burn_captions: event.target.checked })}
          />
          Burn captions
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={payload.generate_thumbnail}
            onChange={(event) =>
              setPayload({ ...payload, generate_thumbnail: event.target.checked })
            }
          />
          Thumbnail
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={payload.webm}
            onChange={(event) => setPayload({ ...payload, webm: event.target.checked })}
          />
          WebM copy
        </label>
      </div>

      <button
        type="button"
        disabled={!payload.url || mutation.isPending}
        onClick={() => mutation.mutate()}
        className="rounded-lg bg-violet-600 px-6 py-3 font-medium hover:bg-violet-500 disabled:opacity-40"
      >
        {mutation.isPending ? "Queuing…" : "Create clips"}
      </button>
      {mutation.isError && <p className="text-sm text-red-400">{mutation.error.message}</p>}
    </section>
  );
}
