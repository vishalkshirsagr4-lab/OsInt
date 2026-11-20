# Cloudflare deployment

## Current architecture

- Worker: `osint-cloudflare`
- Telegram webhook: `/telegram/webhook`
- Health endpoint: `/health`
- D1 database binding: `DB`
- D1 database: `osint-db`
- Migration directory: `migrations/`

The Worker supports account balances, daily credits, referrals, redeem codes,
and owner-only code creation. Private-person data lookups and spam/bomber
automation are intentionally not included.

## Required Worker secrets

Create these three secrets under **Cloudflare Dashboard → Workers & Pages →
osint-cloudflare → Settings → Variables and Secrets**. Choose **Secret** for
each value, not plain text.

| Secret name | Value to enter | Purpose |
|---|---|---|
| `BOT_TOKEN` | Current Telegram bot token from BotFather | Sends bot replies and calls Telegram Bot API |
| `TELEGRAM_WEBHOOK_SECRET` | A private random string, 1–256 characters; use letters, numbers, underscores or hyphens | Authenticates incoming Telegram webhook requests |
| `OWNER_ID` | Your Telegram numeric user ID (digits only) | Restricts `/admin` and `/makecode` to the owner |

**Important for this deployment:**
- `OWNER_ID` was already uploaded successfully in the earlier setup. Keep it; do not change it unless your Telegram numeric user ID is wrong.
- The old bot token was revoked. Make sure `BOT_TOKEN` is the newly generated, current token. Re-upload it if you have not done so since revocation.
- Keep the existing `TELEGRAM_WEBHOOK_SECRET` if it is still available and matches the value used when registering the webhook. If you replace it, you must register the webhook again with the same new value.
- Never paste any of these values into chat, source files, GitHub commits, screenshots, or public logs.

## D1 database

The production D1 database is configured in `wrangler.jsonc` with binding
`DB`. The account/economy migration `0002_accounts_economy.sql` has been
applied to the remote database. Do not manually recreate or drop its tables.

## Registering the Telegram webhook

After deploying the Worker, register this exact URL with Telegram:

`https://osint-cloudflare.vishalkshirsagr4.workers.dev/telegram/webhook`

Use Telegram's Bot API `setWebhook` with:
- `url`: the URL above
- `secret_token`: the exact value stored as `TELEGRAM_WEBHOOK_SECRET`

Do not share the token or secret while configuring the webhook.

## Smoke-test checklist

1. Open `https://osint-cloudflare.vishalkshirsagr4.workers.dev/` — service status should be returned.
2. Open `https://osint-cloudflare.vishalkshirsagr4.workers.dev/health` — it should report D1 connected.
3. Send `/start`, `/balance`, `/daily`, and `/refer` to the Telegram bot.
4. Verify a second `/daily` claim on the same UTC date is rejected.
5. Verify a non-owner cannot use `/admin` or `/makecode`.
6. Verify the owner can create a redeem code and a user can redeem it once.
7. Verify an invalid webhook secret is rejected with HTTP 401.

Do not treat the deployment as production-ready until these checks pass.


## Automatic deployment from GitHub Actions

The feature branch now runs Python compilation and unit tests first. If both
pass on a push to `cloudflare-worker-foundation`, GitHub Actions deploys the
tested commit with Pywrangler.

Add these two values under **GitHub repository → Settings → Secrets and
variables → Actions → New repository secret**. These are GitHub Actions
secrets, separate from the three Worker secrets above:

- `CLOUDFLARE_API_TOKEN`: create a Cloudflare API token with the minimum
  permissions needed to deploy Workers and access the configured D1 binding.
- `CLOUDFLARE_ACCOUNT_ID`: your Cloudflare account ID.

Do not add these two names as Worker secrets. Do not put either value in source
code or chat. Once configured, future feature-branch pushes deploy only after
the test job succeeds. The workflow does not deploy `main`.

## Telegram webhook URL

The Telegram webhook must point to:

`https://osint-cloudflare.vishalkshirsagr4.workers.dev/telegram/webhook`

The webhook registration must use the same value as the Worker secret
`TELEGRAM_WEBHOOK_SECRET` as Telegram's `secret_token`. Adding Worker secrets
does not by itself register or change Telegram's webhook. Confirm the webhook
is registered to this exact URL after the first successful deployment.
