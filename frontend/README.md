# Frontend (React)

This is a minimal React frontend for the Career Guidance Platform.

## Quick Start

```bash
# from project root
npm create vite@latest frontend -- --template react
cd frontend
npm install

# install extra deps if needed
npm install axios

# run dev server
npm run dev
# app will be at http://localhost:5173
```

## Configure API base URL

Create `src/config.ts`:

```ts
export const API_BASE = 'http://127.0.0.1:5000';
```

Update the components to import `API_BASE` for calling backend.