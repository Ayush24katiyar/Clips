"use client";

import type { QualityMode } from "@/lib/api";
import { cn } from "@/lib/utils";

const options: { value: QualityMode; label: string; hint: string }[] = [
  { value: "visually_lossless", label: "Visually lossless", hint: "CRF 17 · recommended" },
  { value: "balanced", label: "Balanced", hint: "CRF 21 · smaller files" },
  { value: "bit_exact", label: "Bit-exact archive", hint: "stream copy · no captions" },
  { value: "true_lossless", label: "True lossless", hint: "MKV master · huge" },
];

export function QualitySelector({
  value,
  onChange,
}: {
  value: QualityMode;
  onChange: (value: QualityMode) => void;
}) {
  return (
    <fieldset className="space-y-2">
      <legend className="mb-2 text-sm font-medium">Quality mode</legend>
      <div className="grid gap-2 sm:grid-cols-2">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={cn(
              "rounded-lg border p-3 text-left transition",
              value === option.value
                ? "border-violet-500 bg-violet-500/10"
                : "border-white/10 bg-white/5 hover:border-white/25",
            )}
          >
            <div className="text-sm font-medium">{option.label}</div>
            <div className="mt-1 text-xs text-zinc-500">{option.hint}</div>
          </button>
        ))}
      </div>
    </fieldset>
  );
}
