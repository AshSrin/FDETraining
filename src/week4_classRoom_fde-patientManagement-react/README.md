# Patient Management (React)

A React + TypeScript + Vite front end for the patient risk API built in the earlier mini projects. It loads all encounters from the backend and shows them in a table with 40 rows per page.

## Prerequisites

- Node.js 20+
- The FastAPI backend running on `http://127.0.0.1:8001` (see [week3_miniProject_with_HTML](../week3_miniProject_with_HTML) and the [root README](../../README.md#running-the-backend-week-3-version))

## Getting started

```bash
npm install
npm run dev        # http://localhost:5173
```

| Script | What it does |
|--------|--------------|
| `npm run dev` | Start the Vite dev server with hot reload |
| `npm run build` | Type-check (`tsc -b`) and build into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |

## How it works

`App.tsx` fetches `GET /encounters` once on mount, stores the result in state, and passes the current 40-row slice to `Pagination`.

```
src/
├── App.tsx                  # Fetches encounters and tracks the current page
├── types.tsx                # encounterInterface (encounter_id, patient_nbr, risk_level, risk_score, age)
└── components/
    ├── Header.tsx
    ├── Pagination.tsx       # Page controls + table for the current slice
    ├── PatientTable.tsx
    ├── PatientRow.tsx
    └── SearchScreen.tsx     # Search form (patient number, risk level, risk score) – not wired up yet
```

## Notes and next steps

- The API URL is hard-coded in `App.tsx`. Moving it to a Vite env variable (`import.meta.env.VITE_API_BASE`) would make it configurable.
- `SearchScreen` renders the form but does not filter results yet.
- The backend must allow CORS from the dev server origin. The week 3 API already allows all origins.
