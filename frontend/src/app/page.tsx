import Link from "next/link";

export default function DashboardPage() {
  return (
    <section className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Clip long videos into sharp shorts</h1>
        <p className="mt-3 max-w-2xl text-zinc-400">
          Paste a YouTube link. ClipForge finds the moments that matter, renders at visually lossless
          quality, and writes captions, thumbnails and metadata.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { title: "Visually lossless", body: "CRF 17 x264, 1080p vertical, no stretched frames." },
          { title: "Groq-powered", body: "Word-level captions and moment scoring for ~5¢ per hour." },
          { title: "Local first", body: "Video never leaves your machine except extracted audio." },
        ].map((card) => (
          <div key={card.title} className="rounded-xl border border-white/10 bg-white/5 p-5">
            <h2 className="font-semibold">{card.title}</h2>
            <p className="mt-2 text-sm text-zinc-400">{card.body}</p>
          </div>
        ))}
      </div>
      <Link
        href="/studio"
        className="inline-block rounded-lg bg-violet-600 px-5 py-3 font-medium hover:bg-violet-500"
      >
        Open Studio →
      </Link>
    </section>
  );
}
