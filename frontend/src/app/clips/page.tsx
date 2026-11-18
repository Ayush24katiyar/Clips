"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ClipCard } from "@/components/ClipCard";
import { api } from "@/lib/api";

export default function ClipsPage() {
  const jobs = useQuery({ queryKey: ["jobs"], queryFn: api.listJobs, refetchInterval: 5000 });
  const latest = jobs.data?.[0];

  const clips = useQuery({
    queryKey: ["clips", latest?.id],
    queryFn: () => api.listClips(latest?.id ?? ""),
    enabled: Boolean(latest?.id),
  });

  return (
    <section className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Clip library</h1>
        <Link href="/studio" className="text-sm text-violet-400 hover:underline">
          New job →
        </Link>
      </div>
      {!latest && <p className="text-zinc-500">No jobs yet. Start one in the Studio.</p>}
      {clips.data && clips.data.length > 0 && (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-5">
          {clips.data.map((clip) => (
            <ClipCard key={clip.id} clip={clip} />
          ))}
        </div>
      )}
    </section>
  );
}
