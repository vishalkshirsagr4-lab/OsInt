# OsInt

## Cloudflare Worker migration

The `cloudflare-worker-foundation` branch contains the Cloudflare Python Worker,
Telegram webhook handler, and D1-backed account/economy features. The original
`osintfinl.py` is retained for reference and is not imported by the Worker.

### Supported commands

- `/start`, `/menu`, `/help`
- `/balance` — account credits and successful referral count
- `/daily` — one daily credit claim (UTC day)
- `/refer` — personal referral link
- `/redeem CODE` — redeem a valid owner-issued code
- `/admin`, `/makecode CREDITS USES` — owner-only code management

The Worker stores only the Telegram numeric account ID, username, first name,
credit balance, referral metadata, and credit transaction records needed for
these features. It does not store message bodies or lookup queries.

Private-person data lookup integrations and spam/bomber automation are
intentionally excluded. This branch is not a feature-complete port of every
legacy command. Review [CLOUDFLARE_DEPLOYMENT.md](CLOUDFLARE_DEPLOYMENT.md)
for the required Cloudflare secrets and webhook setup.

### Infrastructure

- Worker: `osint-cloudflare`
- Webhook route: `/telegram/webhook`
- Health route: `/health`
- D1 binding: `DB`
- Migrations: `migrations/`

Do not switch production traffic until the Worker runtime and Telegram webhook
have been smoke-tested with the configured secrets.
