# Frontend instructions

- Next.js 16 App Router, React 19, TypeScript strict, Tailwind 4, TanStack Query.
- All backend calls live in `src/lib/api.ts`; components must never hardcode URLs.
- Pages go in `src/app`; shared UI in `src/components`.
- Functional components only. No class components. No `any` — define interfaces in `api.ts`.
- Run `npx tsc --noEmit` before finishing. Do not commit `.next/` or `node_modules/`.
- Follow the root `RULES.md`, `NO.md`, `QUALITY.md` and `ARCHITECTURE.md`.
