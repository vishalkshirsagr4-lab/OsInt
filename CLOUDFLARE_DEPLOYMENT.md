# Cloudflare deployment

## Current status

This branch is a Cloudflare Python Worker foundation. It currently supports
only `/start`, `/menu`, and `/help`. The original `osintfinl.py` remains
unchanged and is not imported. Private-personal-data lookup integrations are
intentionally excluded. This is not a feature-complete replacement.

## 1. Get the branch

```bash
git clone -b cloudflare-worker-foundation https://github.com/vishalkshirsagr4-lab/OsInt.git
cd OsInt
```

Or, in an existing clone:

```bash
git switch cloudflare-worker-foundation
git pull
```

## 2. Create D1

```bash
npx wrangler login
npx wrangler d1 create osint-db
```

Copy the database ID printed by Cloudflare into `wrangler.jsonc`, replacing
`REPLACE_WITH_D1_DATABASE_ID`. Keep the binding name `DB`. Then apply:

```bash
npx wrangler d1 migrations apply osint-db --remote
```

## 3. Where to set production secrets

The Worker requires these exact secret names:

- `BOT_TOKEN`: Telegram bot token.
- `TELEGRAM_WEBHOOK_SECRET`: random webhook authentication secret (1–256
  characters; letters, numbers, underscore, and hyphen).

**Easiest method — Cloudflare dashboard:**

1. Open https://dash.cloudflare.com/ and sign in.
2. Go to **Workers & Pages**.
3. Select Worker **osint-cloudflare** (it appears after the first deployment).
4. Open **Settings → Variables and Secrets**.
5. Click **Add**, choose type **Secret**.
6. Add `BOT_TOKEN` and paste its value, then save.
7. Add a second Secret named `TELEGRAM_WEBHOOK_SECRET`, then save.
8. Deploy the changes.

**Termux method — Wrangler prompts you for each value:**

```bash
npx wrangler login
npx wrangler secret put BOT_TOKEN
npx wrangler secret put TELEGRAM_WEBHOOK_SECRET
```

Paste each value only into Wrangler's interactive prompt. Do not put secrets in
`wrangler.jsonc`, source code, GitHub, command arguments, screenshots, or chat.

**For local testing only:**

```bash
cp .dev.vars.example .dev.vars
nano .dev.vars
```

Fill in the two values in `.dev.vars`. This file is ignored by Git and must
never be committed. Local secrets are separate from production secrets.

## 4. Install and test

```bash
uv sync
uv run pywrangler dev
```

Check `http://localhost:8787/` and `http://localhost:8787/health`.
The health route should report D1 connected.

## 5. Deploy

After replacing the D1 ID and configuring both production secrets:

```bash
uv run pywrangler deploy
```

Use the exact workers.dev URL printed by Wrangler.

## 6. Register Telegram webhook

Enter the values interactively so they are not included in command history:

```bash
read -rsp "Telegram bot token: " BOT_TOKEN; echo
read -rsp "Webhook secret: " WEBHOOK_SECRET; echo
read -rp "Worker URL: " WORKER_URL
curl -fsS "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  --data-urlencode "url=${WORKER_URL%/}/telegram/webhook" \
  --data-urlencode "secret_token=${WEBHOOK_SECRET}"
unset BOT_TOKEN WEBHOOK_SECRET
```

The response should contain `"ok":true`. Do not share the token or webhook
secret, or screenshots containing them.

## 7. Smoke tests

- `/` returns service status.
- `/health` reports D1 connected.
- Telegram `/start`, `/menu`, and `/help` reply.
- Wrong webhook secret receives HTTP 401.
- Unknown commands receive a safe not-migrated response.

Do not switch production traffic until all required legitimate features have
been ported and tested. Cloudflare Workers are request-driven; do not add
polling loops, local Flask startup, background threads, or local SQLite.
