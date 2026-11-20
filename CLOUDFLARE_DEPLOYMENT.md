# Cloudflare deployment

## Current migration status

This branch adds a Cloudflare Python Worker foundation, D1 schema, health route,
and a Telegram webhook for the safe base commands `/start`, `/menu`, and
`/help`.

The existing `osintfinl.py` is intentionally left unchanged as a legacy
reference. It is **not** imported by the Worker: it starts a local Flask thread,
contains a Telegram polling loop, uses local SQLite/filesystem state, and has
private-personal-data lookup integrations that are not part of this migration.
The remaining legitimate bot features need to be ported and tested in separate
small steps before this branch can replace the legacy bot.

## Prerequisites

- A Cloudflare account with Workers and D1 enabled.
- Python 3.12+ and Node.js installed locally.
- `uv` installed.

## 1. Create the D1 database

From the repository root:

```bash
npx wrangler d1 create osint-db
```

Copy the returned database ID into `wrangler.jsonc`, replacing
`REPLACE_WITH_D1_DATABASE_ID`.

Apply the migration locally and remotely:

```bash
npx wrangler d1 migrations apply osint-db --local
npx wrangler d1 migrations apply osint-db --remote
```

## 2. Install the Python Worker tooling

```bash
uv sync
```

Run locally:

```bash
uv run pywrangler dev
```

The local server should expose `/` and `/health`. The webhook will return
401 until a local `TELEGRAM_WEBHOOK_SECRET` is configured in `.dev.vars`.

Example `.dev.vars` (never commit this file):

```dotenv
BOT_TOKEN=replace-with-your-telegram-bot-token
TELEGRAM_WEBHOOK_SECRET=replace-with-a-long-random-secret
```

## 3. Configure production secrets

```bash
uv run pywrangler secret put BOT_TOKEN
uv run pywrangler secret put TELEGRAM_WEBHOOK_SECRET
```

Enter the values when prompted. Never paste tokens into source files, commits,
screenshots, or public issue reports.

## 4. Deploy

```bash
uv run pywrangler deploy
```

Save the deployed Worker URL, for example
`https://osint-cloudflare.<your-subdomain>.workers.dev`.

## 5. Register the Telegram webhook

Use the deployed URL and the same secret value configured above. Telegram's
`setWebhook` API accepts a `secret_token` parameter; the Worker checks the
matching `X-Telegram-Bot-Api-Secret-Token` header.

From a trusted local terminal, enter the values interactively so they are not
written into the command history:

```bash
read -rsp "Telegram bot token: " BOT_TOKEN; echo
read -rsp "Webhook secret: " WEBHOOK_SECRET; echo
read -rp "Worker URL (https://...workers.dev): " WORKER_URL
curl -fsS "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  --data-urlencode "url=${WORKER_URL%/}/telegram/webhook" \
  --data-urlencode "secret_token=${WEBHOOK_SECRET}"
unset BOT_TOKEN WEBHOOK_SECRET
```

Do not publish your bot token or webhook secret.

## 6. Smoke tests

- Open `/` and confirm JSON reports `status: ok`.
- Open `/health` and confirm D1 reports `connected`.
- Send `/start`, `/menu`, and `/help` to the Telegram bot.
- Confirm an invalid webhook secret receives HTTP 401.
- Confirm unknown commands receive a safe "not migrated" response.

## Important

This is a migration foundation, not a completed feature-for-feature port. Do
not switch the production bot over until every required legitimate feature has
a Cloudflare implementation and passing tests. Cloudflare Workers are
request-driven: do not add `bot.polling()`, `app.run()`, background threads,
or local SQLite persistence to the Worker.
