# Frontend — ResumeVerify (Prototype)

This folder contains a single-file dashboard prototype (`index_simple.html`) and a React app (`src/`) used during development.

Quick options to run the prototype UI locally

1) Serve the single-file prototype (fast, no build required):

```bash
cd frontend
python -m http.server 5500
# Open http://127.0.0.1:5500/index_simple.html in your browser
```

2) Run the React/Vite dev server (if you want the React app):

```bash
cd frontend
# install new dependencies (Chart.js, Web3) then run dev
npm install
npm run dev
# Open http://localhost:5173 (or the port shown by Vite)
```

Notes
- The prototype uses Chart.js (CDN) and a MetaMask/web3 snippet for demo purposes.
- The single-file prototype will attempt to call the backend at `http://127.0.0.1:8000` for uploads. If the backend is unreachable it falls back to a simulated verification UI.
- The React app (`src/App.tsx`) already contains a fully functional upload component that posts to `/resumes/upload` and polls `/resumes/{id}` for results. Use the Vite dev server to run it.

Backend quick start (example)

```bash
# from project root
cd backend
# create and activate python venv, install requirements, then run
# python -m venv .venv
# .venv\Scripts\activate
# pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

If you want, I can:
- Convert the prototype UI into React + Tailwind components and wire them into `src/`.
- Add Chart.js as a dependency and render the charts inside the React app.
- Add Web3 integration and transaction UI in the React app.

Tell me which of the above you'd like me to implement next.
