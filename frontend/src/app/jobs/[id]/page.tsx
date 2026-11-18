"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { ClipCard } from "@/components/ClipCard";
import { ProgressBar } from "@/components/ProgressBar";
import { API_URL, api, type Clip, type Job } from "@/lib/api";

export default function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const [id, setId] = useState("");
  const [live, setLive] = useState({ stage: "", percent: 0 });

  useEffect(() => {
    void params.then((value) => setId(value.id));
  }, [params]);

  const jobQuery = useQuery({
    queryKey: ["job", id],
    queryFn: () => api.getJob(id),
    enabled: Boolean(id),
    refetchInterval: 3000,
    refetchIntervalInBackground: true,
  });

  const clipsQuery = useQuery({
    queryKey: ["clips", id],
    queryFn: () => api.listClips(id),
    enabled: Boolean(id),
    refetchInterval: 5000,
    refetchIntervalInBackground: true,
  });

  useEffect(() => {
    if (!id) return;
    const source = new EventSource(`${API_URL}/jobs/${id}/events`);
    source.onmessage = (event) => {
      const data = JSON.parse(event.data as string) as { stage: string; percent: number };
      setLive({ stage: data.stage, percent: data.percent });
    };
    return () => source.close();
  }, [id]);

  const job: Job | undefined = jobQuery.data;
  const clips: Clip[] = clipsQuery.data ?? [];

  return (
    <section className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Job {id || "…"}</h1>
        <p className="mt-1 text-sm text-zinc-500">
          {job?.status ?? "loading"} · {job?.quality_mode ?? "—"}
        </p>
      </div>

      <ProgressBar
        stage={live.stage || job?.stage || "queued"}
        percent={live.percent || job?.progress || 0}
      />

      {job?.status === "failed" && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          <strong>Job failed:</strong> {job.error || "Unknown error"}
        </div>
      )}
      {job?.status === "succeeded" && (
        <p className="text-sm text-emerald-400">Done — {clips.length} clips ready.</p>
      )}

      {clips.length > 0 && (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-5">
          {clips.map((clip) => (
            <ClipCard key={clip.id} clip={clip} />
          ))}
        </div>
      )}
    </section>
  );
}
