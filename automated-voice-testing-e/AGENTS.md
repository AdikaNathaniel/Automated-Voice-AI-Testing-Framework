## Operational Guidelines

- For commands that start long-running services (e.g., `npm run dev` or other watchers), never run them directly in the foreground via the shell tool. Instead:
  - Prefer commands with built-in timeouts (`timeout 30s npm run dev -- --host --port 5173`), or
  - Start them in the background with output redirected (e.g., `nohup npm run dev -- --host --port 5173 >/tmp/dev-server.log 2>&1 &`) and mention how to stop/inspect logs in the response.
- When a background process is launched, record the command and PID in the transcript so the user can manage it later, and ensure logs go to a file instead of the terminal.
- If a workflow requires a server, consider using Playwright/Vite `webServer` config or a one-off `npm run build`/`npm run preview` with `timeout` to avoid blocking the chat.
