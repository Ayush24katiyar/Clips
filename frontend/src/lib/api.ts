export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type QualityMode = "visually_lossless" | "bit_exact" | "true_lossless" | "balanced";

export interface CreateJobPayload {
  url: string;
  quality_mode: QualityMode;
  ratio: string;
  clip_count: number;
  burn_captions: boolean;
  generate_thumbnail: boolean;
  webm: boolean;
}

export interface Job {
  id: string;
  status: string;
  stage: string;
  progress: number;
  error: string | null;
  source_id: string;
  quality_mode: string;
  created_at: string;
}

export interface Clip {
  id: string;
  start: number;
  end: number;
  score: number;
  title: string;
  description: string;
  file_path: string;
  webm_path: string | null;
  thumbnail_path?: string;
}

export interface Streamer {
  id: string;
  platform: string;
  name: string;
  country: string | null;
  category: string | null;
  channel_url: string;
  avatar_url: string | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json() as Promise<T>;
}

export const api = {
  createJob: (payload: CreateJobPayload) =>
    request<Job>("/jobs", { method: "POST", body: JSON.stringify(payload) }),
  listJobs: () => request<Job[]>("/jobs"),
  getJob: (id: string) => request<Job>(`/jobs/${id}`),
  listClips: (jobId: string) => request<Clip[]>(`/clips/job/${jobId}`),
  listStreamers: (country?: string, category?: string) => {
    const params = new URLSearchParams();
    if (country) params.set("country", country);
    if (category) params.set("category", category);
    return request<Streamer[]>(`/discover?${params.toString()}`);
  },
  refreshStreamers: (region = "US") =>
    request<Streamer[]>(`/discover/refresh?region=${region}`, { method: "POST" }),
  mediaUrl: (path: string) => `${API_URL}/media/${path.replace(/^\//, "")}`,
};
