# OsInt — Original Python Telegram Bot

This repository deploys the original `osintfinl.py` application. The Cloudflare Worker rewrite is not used as the bot runtime.

## Render deployment

Create a **Web Service** connected to this repository.

- **Branch:** `main` after the deployment pull request is merged
- **Runtime:** Python
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `python osintfinl.py`

The source starts its Flask health server and Telegram polling process. Keep the service as a continuously running Render Web Service.

## Required Render environment variables

Add these in **Render → your Web Service → Environment**. Use your own values; never commit real credentials.

| Variable | Purpose |
|---|---|
| `BOT_TOKEN` | Telegram bot token (use a newly rotated token) |
| `OWNER_ID` | Numeric Telegram owner user ID |
| `DB_CHANNEL` | Telegram database channel ID |
| `LOGS_CHANNEL` | Telegram logs channel ID |
| `GH_TOKEN` | GitHub token used by the existing database restore/backup code |
| `GH_REPO` | Repository in `owner/repository` format for database backup |
| `GH_DB_PATH` | Database backup filename/path in that repository; defaults to `database.db` |

Render automatically supplies its own `RENDER_*` environment variables. Do not manually copy those.

## Environment template

`.env.example` lists the required variable names and safe placeholders. It is a template only. The application does not load a local `.env` file, so configure the values in Render's Environment page. For local development, export the variables in your shell before starting Python.

## Database notes

The existing source restores and backs up its SQLite database through the configured GitHub repository. Keep the existing repository and database path values. Do not create a replacement database or upload a real database file to this repository.

Before first deployment, confirm that the GitHub token can access the configured backup repository and that the expected database file already exists there. Check Render logs for restore/backup messages after startup.

## Credential safety

A Telegram token was embedded as a fallback in the public source. That fallback has been removed from the deployment branch. **Revoke/rotate the exposed token in BotFather before deploying**, then set the new token only in Render Environment.

Never commit `.env`, tokens, API keys, or database files. GitHub Actions secrets and Cloudflare Worker secrets are separate from Render environment variables; they are not automatically available to this Render service.

## Health check

The Flask server is started by the original source on port `10000`. If configuring a Render health check path, use `/health` and verify it returns a successful response on the deployed service.
