# Run the Project Manually

## Start the backend

Open PowerShell and run:

```powershell
cd "C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro"
.\.venv\Scripts\python.exe .\app.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

Keep this terminal open.

## Start the frontend

Open a second PowerShell window and run:

```powershell
cd "C:\Users\shash\OneDrive\Desktop\Projects\Final_pro\Final_pro\frontend"
npm install
npm run dev
```

Open the frontend URL shown by Vite, normally:

```text
http://127.0.0.1:5173
```

## Startup order

1. Start the backend in the first terminal.
2. Start the frontend in the second terminal.
3. Open `http://127.0.0.1:5173` in your browser.

To stop either server, press `Ctrl+C` in its terminal.
