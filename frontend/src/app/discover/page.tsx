"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { StreamerCard } from "@/components/streamer/StreamerCard";
import { api } from "@/lib/api";

const REGIONS = ["US", "GB", "IN", "JP", "BR", "KR", "DE"];

export default function DiscoverPage() {
  const [region, setRegion] = useState("US");
  const queryClient = useQueryClient();
  const streamers = useQuery({
    queryKey: ["streamers", region],
    queryFn: () => api.listStreamers(region),
  });
  const refresh = useMutation({
    mutationFn: () => api.refreshStreamers(region),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["streamers"] }),
  });

  return (
    <section className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Discover creators</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Popular YouTube creators by country and top Twitch streamers.
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={region}
            onChange={(event) => setRegion(event.target.value)}
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm"
          >
            {REGIONS.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => refresh.mutate()}
            disabled={refresh.isPending}
            className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium hover:bg-violet-500 disabled:opacity-40"
          >
            {refresh.isPending ? "Refreshing…" : "Refresh"}
          </button>
        </div>
      </div>

      {streamers.data && streamers.data.length > 0 ? (
        <div className="grid gap-3 md:grid-cols-2">
          {streamers.data.map((streamer) => (
            <StreamerCard key={streamer.id} streamer={streamer} />
          ))}
        </div>
      ) : (
        <p className="text-sm text-zinc-500">
          No data yet. Add YouTube/Twitch keys to <code>.env</code> and click Refresh.
        </p>
      )}
    </section>
  );
}
